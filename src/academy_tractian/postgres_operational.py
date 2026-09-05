from __future__ import annotations

from contextlib import contextmanager
import re
from typing import Iterable, Iterator

from .product_storage_contracts import (
    RUN_ACCESS_SCHEMA_VERSION,
    RUN_EXECUTION_SCHEMA_VERSION,
    DurableExecution,
    ExecutionKind,
    ExecutionState,
    RunOwnership,
)


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_OPERATIONAL_SCHEMA_VERSION = "postgres-operational-v1"
_EXECUTION_STATES = (
    "accepted",
    "running",
    "completed",
    "failed",
    "interrupted",
    "uncertain",
)


def _identifier(value: str, *, label: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def _psycopg():
    try:
        import psycopg
        from psycopg_pool import ConnectionPool
    except ImportError as exc:  # pragma: no cover - packaging/runtime guard
        raise RuntimeError(
            "PostgreSQL operational state requires psycopg[binary,pool]"
        ) from exc
    return psycopg, ConnectionPool


class PostgresOperationalDatabase:
    """Shared PostgreSQL operational substrate with a real RLS read channel.

    ``internal_dsn`` is a trusted service/migration connection used for server-owned state
    changes. ``scoped_dsn`` must identify a distinct, non-superuser, non-BYPASSRLS,
    non-table-owner role. Product authorization reads run through that role with a transaction-
    local ``academy.organization_id`` setting, so tenant isolation is enforced by PostgreSQL in
    addition to application policy.
    """

    def __init__(
        self,
        *,
        internal_dsn: str,
        scoped_dsn: str,
        schema: str = "academy_operational",
        min_size: int = 1,
        max_size: int = 16,
        initialize: bool = False,
    ) -> None:
        if not internal_dsn or not scoped_dsn:
            raise ValueError("internal_dsn and scoped_dsn are required")
        if not 1 <= min_size <= max_size <= 64:
            raise ValueError("invalid PostgreSQL pool bounds")
        self.schema = _identifier(schema, label="schema")
        _, ConnectionPool = _psycopg()
        self.internal_pool = ConnectionPool(
            conninfo=internal_dsn,
            min_size=min_size,
            max_size=max_size,
            open=True,
        )
        self.scoped_pool = ConnectionPool(
            conninfo=scoped_dsn,
            min_size=min_size,
            max_size=max_size,
            open=True,
        )
        if initialize:
            self.initialize_schema()
        self._verify_scoped_role()

    def close(self) -> None:
        self.scoped_pool.close()
        self.internal_pool.close()

    def initialize_schema(self) -> None:
        """Create the v1 schema using trusted migration credentials.

        Serving deployments should normally run this during migration/bootstrap and then avoid
        retaining elevated DDL credentials. CI may initialize in-process for reproducibility.
        """

        schema = self.schema
        with self.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema}".operational_meta (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema}".run_ownership (
                        run_id TEXT PRIMARY KEY,
                        organization_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema}".run_executions (
                        run_id TEXT PRIMARY KEY REFERENCES "{schema}".run_ownership(run_id)
                            ON DELETE RESTRICT,
                        execution_kind TEXT NOT NULL CHECK (execution_kind IN ('runtime','action')),
                        state TEXT NOT NULL CHECK (
                            state IN ('accepted','running','completed','failed','interrupted','uncertain')
                        ),
                        related_action_id TEXT,
                        transition_count INTEGER NOT NULL CHECK (transition_count >= 1),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CHECK (
                            (execution_kind = 'runtime' AND related_action_id IS NULL)
                            OR (execution_kind = 'action' AND related_action_id IS NOT NULL)
                        )
                    )
                    """
                )
                connection.execute(
                    f'ALTER TABLE "{schema}".run_ownership ENABLE ROW LEVEL SECURITY'
                )
                connection.execute(
                    f'DROP POLICY IF EXISTS tenant_select ON "{schema}".run_ownership'
                )
                connection.execute(
                    f"""
                    CREATE POLICY tenant_select ON "{schema}".run_ownership
                    FOR SELECT
                    USING (
                        organization_id = current_setting('academy.organization_id', true)
                    )
                    """
                )
                metadata = {
                    "schema_version": _OPERATIONAL_SCHEMA_VERSION,
                    "run_access_schema_version": RUN_ACCESS_SCHEMA_VERSION,
                    "run_execution_schema_version": RUN_EXECUTION_SCHEMA_VERSION,
                }
                for key, value in metadata.items():
                    connection.execute(
                        f"""
                        INSERT INTO "{schema}".operational_meta(key, value)
                        VALUES (%s, %s)
                        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                        """,
                        (key, value),
                    )

        with self.scoped_pool.connection() as scoped_connection:
            scoped_role = str(scoped_connection.execute("SELECT current_user").fetchone()[0])
        role = _identifier(scoped_role, label="scoped role")
        with self.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"')
                connection.execute(f'GRANT SELECT ON "{schema}".run_ownership TO "{role}"')

    def _verify_scoped_role(self) -> None:
        """Fail closed if scoped reads could bypass the tenant policy."""

        schema = self.schema
        with self.scoped_pool.connection() as connection:
            row = connection.execute(
                """
                SELECT current_user, r.rolsuper, r.rolbypassrls
                FROM pg_roles AS r
                WHERE r.rolname = current_user
                """
            ).fetchone()
            if row is None:
                raise RuntimeError("postgres_scoped_role_unknown")
            role = str(row[0])
            if bool(row[1]) or bool(row[2]):
                raise RuntimeError("postgres_scoped_role_can_bypass_rls")
        with self.internal_pool.connection() as connection:
            owner = connection.execute(
                """
                SELECT pg_get_userbyid(c.relowner)
                FROM pg_class AS c
                JOIN pg_namespace AS n ON n.oid = c.relnamespace
                WHERE n.nspname = %s AND c.relname = 'run_ownership'
                """,
                (schema,),
            ).fetchone()
        if owner is None:
            raise RuntimeError("postgres_operational_schema_missing")
        if str(owner[0]) == role:
            raise RuntimeError("postgres_scoped_role_owns_rls_table")

    def ready(self) -> bool:
        schema = self.schema
        try:
            with self.internal_pool.connection() as connection:
                row = connection.execute(
                    f"""
                    SELECT value FROM "{schema}".operational_meta
                    WHERE key = 'schema_version'
                    """,
                ).fetchone()
                if row is None or str(row[0]) != _OPERATIONAL_SCHEMA_VERSION:
                    return False
            with self.scoped_connection("readiness-probe") as connection:
                connection.execute(
                    f'SELECT run_id FROM "{schema}".run_ownership LIMIT 1'
                ).fetchall()
            return True
        except Exception:
            return False

    @contextmanager
    def scoped_connection(self, organization_id: str) -> Iterator[object]:
        if not organization_id:
            raise ValueError("organization_id must be non-empty")
        with self.scoped_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT set_config('academy.organization_id', %s, true)",
                    (organization_id,),
                )
                yield connection


class PostgresRunAccessStore:
    def __init__(self, database: PostgresOperationalDatabase) -> None:
        self.database = database
        self.schema = database.schema

    def ready(self) -> bool:
        return self.database.ready()

    def claim(self, *, run_id: str, organization_id: str, user_id: str) -> bool:
        if not run_id or not organization_id or not user_id:
            raise ValueError("run ownership fields must be non-empty")
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                inserted = connection.execute(
                    f"""
                    INSERT INTO "{schema}".run_ownership(run_id, organization_id, user_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (run_id) DO NOTHING
                    RETURNING run_id
                    """,
                    (run_id, organization_id, user_id),
                ).fetchone()
                if inserted is not None:
                    return True
                existing = connection.execute(
                    f"""
                    SELECT organization_id, user_id
                    FROM "{schema}".run_ownership
                    WHERE run_id = %s
                    """,
                    (run_id,),
                ).fetchone()
                if existing != (organization_id, user_id):
                    raise RuntimeError("run_ownership_conflict")
                return False

    @staticmethod
    def _ownership(row: object | None) -> RunOwnership | None:
        if row is None:
            return None
        values = tuple(row)  # type: ignore[arg-type]
        return RunOwnership(
            run_id=str(values[0]),
            organization_id=str(values[1]),
            user_id=str(values[2]),
        )

    def get(self, run_id: str) -> RunOwnership | None:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT run_id, organization_id, user_id
                FROM "{self.schema}".run_ownership
                WHERE run_id = %s
                """,
                (run_id,),
            ).fetchone()
        return self._ownership(row)

    def get_many(self, run_ids: Iterable[str]) -> dict[str, RunOwnership]:
        unique = tuple(dict.fromkeys(run_id for run_id in run_ids if run_id))
        if not unique:
            return {}
        if len(unique) > 1000:
            raise ValueError("get_many supports at most 1000 run ids")
        with self.database.internal_pool.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT run_id, organization_id, user_id
                FROM "{self.schema}".run_ownership
                WHERE run_id = ANY(%s)
                """,
                (list(unique),),
            ).fetchall()
        result: dict[str, RunOwnership] = {}
        for row in rows:
            item = self._ownership(row)
            assert item is not None
            result[item.run_id] = item
        return result

    def get_scoped(self, *, run_id: str, organization_id: str) -> RunOwnership | None:
        with self.database.scoped_connection(organization_id) as connection:
            row = connection.execute(
                f"""
                SELECT run_id, organization_id, user_id
                FROM "{self.schema}".run_ownership
                WHERE run_id = %s
                """,
                (run_id,),
            ).fetchone()
        return self._ownership(row)

    def get_many_scoped(
        self,
        *,
        run_ids: Iterable[str],
        organization_id: str,
    ) -> dict[str, RunOwnership]:
        unique = tuple(dict.fromkeys(run_id for run_id in run_ids if run_id))
        if not unique:
            return {}
        if len(unique) > 1000:
            raise ValueError("get_many_scoped supports at most 1000 run ids")
        with self.database.scoped_connection(organization_id) as connection:
            rows = connection.execute(
                f"""
                SELECT run_id, organization_id, user_id
                FROM "{self.schema}".run_ownership
                WHERE run_id = ANY(%s)
                """,
                (list(unique),),
            ).fetchall()
        result: dict[str, RunOwnership] = {}
        for row in rows:
            item = self._ownership(row)
            assert item is not None
            result[item.run_id] = item
        return result


class PostgresRunExecutionStore:
    def __init__(self, database: PostgresOperationalDatabase) -> None:
        self.database = database
        self.schema = database.schema

    def ready(self) -> bool:
        return self.database.ready()

    def create_accepted(
        self,
        *,
        run_id: str,
        execution_kind: ExecutionKind = "runtime",
        related_action_id: str | None = None,
    ) -> None:
        if not run_id:
            raise ValueError("run_id must be non-empty")
        if execution_kind == "runtime" and related_action_id is not None:
            raise ValueError("runtime execution cannot carry related_action_id")
        if execution_kind == "action" and not related_action_id:
            raise ValueError("action execution requires related_action_id")
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                inserted = connection.execute(
                    f"""
                    INSERT INTO "{schema}".run_executions(
                        run_id, execution_kind, state, related_action_id, transition_count
                    ) VALUES (%s, %s, 'accepted', %s, 1)
                    ON CONFLICT (run_id) DO NOTHING
                    RETURNING run_id
                    """,
                    (run_id, execution_kind, related_action_id),
                ).fetchone()
                if inserted is not None:
                    return
                existing = connection.execute(
                    f"""
                    SELECT execution_kind, state, related_action_id
                    FROM "{schema}".run_executions
                    WHERE run_id = %s
                    """,
                    (run_id,),
                ).fetchone()
                if existing == (execution_kind, "accepted", related_action_id):
                    return
                raise RuntimeError("run_execution_conflict")

    def transition(
        self,
        *,
        run_id: str,
        expected_states: frozenset[str],
        new_state: ExecutionState,
    ) -> bool:
        if not expected_states:
            raise ValueError("expected_states must be non-empty")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE "{self.schema}".run_executions
                    SET state = %s,
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE run_id = %s AND state = ANY(%s)
                    RETURNING run_id
                    """,
                    (new_state, run_id, list(expected_states)),
                ).fetchone()
                return row is not None

    @staticmethod
    def _execution(row: object | None) -> DurableExecution | None:
        if row is None:
            return None
        values = tuple(row)  # type: ignore[arg-type]
        return DurableExecution(
            run_id=str(values[0]),
            execution_kind=str(values[1]),  # type: ignore[arg-type]
            state=str(values[2]),  # type: ignore[arg-type]
            related_action_id=None if values[3] is None else str(values[3]),
            transition_count=int(values[4]),
        )

    def get(self, run_id: str) -> DurableExecution | None:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT run_id, execution_kind, state, related_action_id, transition_count
                FROM "{self.schema}".run_executions
                WHERE run_id = %s
                """,
                (run_id,),
            ).fetchone()
        return self._execution(row)

    def reconcile_orphaned(self) -> tuple[DurableExecution, ...]:
        schema = self.schema
        recovered: list[DurableExecution] = []
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                rows = connection.execute(
                    f"""
                    SELECT run_id, execution_kind, state, related_action_id, transition_count
                    FROM "{schema}".run_executions
                    WHERE state IN ('accepted','running')
                    ORDER BY run_id
                    FOR UPDATE
                    """
                ).fetchall()
                for row in rows:
                    current = self._execution(row)
                    assert current is not None
                    new_state: ExecutionState = (
                        "uncertain" if current.execution_kind == "action" else "interrupted"
                    )
                    updated = connection.execute(
                        f"""
                        UPDATE "{schema}".run_executions
                        SET state = %s,
                            transition_count = transition_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE run_id = %s AND state IN ('accepted','running')
                        RETURNING run_id, execution_kind, state, related_action_id,
                                  transition_count
                        """,
                        (new_state, current.run_id),
                    ).fetchone()
                    item = self._execution(updated)
                    if item is not None:
                        recovered.append(item)
        return tuple(recovered)

    def counts(self) -> dict[str, int]:
        with self.database.internal_pool.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT state, COUNT(*)
                FROM "{self.schema}".run_executions
                GROUP BY state
                """
            ).fetchall()
        counts = {state: 0 for state in _EXECUTION_STATES}
        for state, count in rows:
            counts[str(state)] = int(count)
        return counts
