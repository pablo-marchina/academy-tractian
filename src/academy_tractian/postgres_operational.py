from __future__ import annotations

from contextlib import contextmanager
import re
from typing import Iterable, Iterator

from .run_access import RUN_ACCESS_SCHEMA_VERSION, RunOwnership
from .run_execution_store import (
    RUN_EXECUTION_SCHEMA_VERSION,
    DurableExecution,
    ExecutionKind,
    ExecutionState,
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
    except ImportError as exc:  # pragma: no cover - exercised by production packaging tests
        raise RuntimeError(
            "PostgreSQL operational state requires psycopg[binary,pool]"
        ) from exc
    return psycopg, ConnectionPool


class PostgresOperationalDatabase:
    """Shared PostgreSQL operational substrate.

    ``internal_dsn`` is used only by trusted server-side state transitions. ``scoped_dsn``
    must resolve to a non-BYPASSRLS role and is used for tenant-scoped ownership reads.
    Keeping those channels separate makes RLS a real defense-in-depth boundary rather than
    a policy executed through a privileged role that silently bypasses it.
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
        """Create/upgrade the v1 schema using the trusted migration connection.

        Production deployments should run this with migration credentials before dropping
        those credentials from the serving process. The method remains callable for local CI.
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
                    f'ALTER TABLE "{schema}".run_ownership FORCE ROW LEVEL SECURITY'
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

        # Grant only what the scoped role needs. It must never mutate operational state.
        with self.scoped_pool.connection() as scoped_connection:
            scoped_role = str(
                scoped_connection.execute("SELECT current_user").fetchone()[0]
            )
        role = _identifier(scoped_role, label="scoped role")
        with self.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"')
                connection.execute(
                    f'GRANT SELECT ON "{schema}".run_ownership TO "{role}"'
                )

    def _verify_scoped_role(self) -> None:
        """Fail closed if the scoped connection can bypass the RLS contract."""

        with self.scoped_pool.connection() as connection:
            row = connection.execute(
                """
                SELECT r.rolsuper, r.rolbypassrls
                FROM pg_roles AS r
                WHERE r.rolname = current_user
                """
            ).fetchone()
            if row is None or bool(row[0]) or bool(row[1]):
                raise RuntimeError("postgres_scoped_role_can_bypass_rls")

    def ready(self) -> bool:
        schema = self.schema
        try:
            with self.internal_pool.connection() as connection:
                row = connection.execute(
                    f"""
                    SELECT value FROM "{schema}".operational_meta
                    WHERE key = 'schema_version'
                    """
                ).fetchone()
                if row is None or str(row[0]) != _OPERATIONAL_SCHEMA_VERSION:
                    return False
            with self.scoped_pool.connection() as connection:
                connection.execute("BEGIN")
                try:
                    connection.execute(
                        "SELECT set_config('academy.organization_id', %s, true)",
                        ("readiness-probe",),
                    )
                    connection.execute(
                        f'SELECT run_id FROM "{schema}".run_ownership LIMIT 1'
                    ).fetchall()
                finally:
                    connection.execute("ROLLBACK")
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
        return {
            item.run_id: item
            for row in rows
            if (item := self._ownership(row)) is not None
        }

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
        return {
            item.run_id: item
            for row in rows
            if (item := self._ownership(row)) is not None
        }


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
