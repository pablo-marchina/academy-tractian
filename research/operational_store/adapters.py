from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Literal, Protocol

import duckdb

from academy_tractian.run_access import DuckDBRunAccessStore
from academy_tractian.run_execution_store import DuckDBRunExecutionStore


ExecutionKind = Literal["runtime", "action"]
ExecutionState = Literal[
    "accepted",
    "running",
    "completed",
    "failed",
    "interrupted",
    "uncertain",
]


@dataclass(frozen=True, slots=True)
class ScopedOwner:
    run_id: str
    organization_id: str
    user_id: str


class OperationalStoreCandidate(Protocol):
    name: str

    def reset(self) -> None: ...

    def close(self) -> None: ...

    def destroy(self) -> None: ...

    def reconnect(self) -> None: ...

    def claim_run(self, *, run_id: str, organization_id: str, user_id: str) -> bool: ...

    def scoped_owner(self, *, run_id: str, organization_id: str) -> ScopedOwner | None: ...

    def create_execution(
        self,
        *,
        run_id: str,
        organization_id: str,
        execution_kind: ExecutionKind = "runtime",
        related_action_id: str | None = None,
    ) -> None: ...

    def transition_execution(
        self,
        *,
        run_id: str,
        organization_id: str,
        expected_states: frozenset[str],
        new_state: ExecutionState,
    ) -> bool: ...

    def execution_state(self, *, run_id: str, organization_id: str) -> str | None: ...

    def reconcile_orphaned(self) -> dict[str, int]: ...

    def prefix_counts(self, prefix: str) -> dict[str, int]: ...

    def direct_cross_tenant_probe(
        self,
        *,
        run_id: str,
        organization_id: str,
    ) -> int | None: ...

    def metadata(self) -> dict[str, str]: ...


class DuckDBOperationalCandidate:
    """Benchmark adapter over the current production operational stores."""

    name = "duckdb"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.access_path = self.root / "run-access.duckdb"
        self.execution_path = self.root / "run-execution.duckdb"
        self._open()

    def _open(self) -> None:
        self.access = DuckDBRunAccessStore(self.access_path)
        self.execution = DuckDBRunExecutionStore(self.execution_path)

    def reset(self) -> None:
        self.close()
        for path in (self.access_path, self.execution_path):
            path.unlink(missing_ok=True)
            Path(f"{path}.wal").unlink(missing_ok=True)
        self._open()

    def close(self) -> None:
        # Production stores are connection-per-operation and retain no open handles.
        return None

    def destroy(self) -> None:
        self.close()
        for path in (self.access_path, self.execution_path):
            path.unlink(missing_ok=True)
            Path(f"{path}.wal").unlink(missing_ok=True)

    def reconnect(self) -> None:
        self._open()

    def claim_run(self, *, run_id: str, organization_id: str, user_id: str) -> bool:
        return self.access.claim(
            run_id=run_id,
            organization_id=organization_id,
            user_id=user_id,
        )

    def scoped_owner(self, *, run_id: str, organization_id: str) -> ScopedOwner | None:
        owner = self.access.get(run_id)
        if owner is None or owner.organization_id != organization_id:
            return None
        return ScopedOwner(
            run_id=owner.run_id,
            organization_id=owner.organization_id,
            user_id=owner.user_id,
        )

    def _require_scope(self, *, run_id: str, organization_id: str) -> None:
        if self.scoped_owner(run_id=run_id, organization_id=organization_id) is None:
            raise PermissionError("run_outside_organization_scope")

    def create_execution(
        self,
        *,
        run_id: str,
        organization_id: str,
        execution_kind: ExecutionKind = "runtime",
        related_action_id: str | None = None,
    ) -> None:
        self._require_scope(run_id=run_id, organization_id=organization_id)
        self.execution.create_accepted(
            run_id=run_id,
            execution_kind=execution_kind,
            related_action_id=related_action_id,
        )

    def transition_execution(
        self,
        *,
        run_id: str,
        organization_id: str,
        expected_states: frozenset[str],
        new_state: ExecutionState,
    ) -> bool:
        self._require_scope(run_id=run_id, organization_id=organization_id)
        return self.execution.transition(
            run_id=run_id,
            expected_states=expected_states,
            new_state=new_state,
        )

    def execution_state(self, *, run_id: str, organization_id: str) -> str | None:
        self._require_scope(run_id=run_id, organization_id=organization_id)
        item = self.execution.get(run_id)
        return None if item is None else item.state

    def reconcile_orphaned(self) -> dict[str, int]:
        recovered = self.execution.reconcile_orphaned()
        return {
            "interrupted": sum(item.state == "interrupted" for item in recovered),
            "uncertain": sum(item.state == "uncertain" for item in recovered),
        }

    def prefix_counts(self, prefix: str) -> dict[str, int]:
        access_connection = duckdb.connect(str(self.access_path))
        try:
            ownership = int(
                access_connection.execute(
                    "SELECT COUNT(*) FROM run_ownership WHERE run_id LIKE ?",
                    [f"{prefix}%"],
                ).fetchone()[0]
            )
        finally:
            access_connection.close()

        execution_connection = duckdb.connect(str(self.execution_path))
        try:
            rows = execution_connection.execute(
                """
                SELECT state, COUNT(*)
                FROM run_executions
                WHERE run_id LIKE ?
                GROUP BY state
                """,
                [f"{prefix}%"],
            ).fetchall()
        finally:
            execution_connection.close()
        counts = {"ownership": ownership, "execution_total": 0}
        for state, count in rows:
            value = int(count)
            counts[str(state)] = value
            counts["execution_total"] += value
        return counts

    def direct_cross_tenant_probe(
        self,
        *,
        run_id: str,
        organization_id: str,
    ) -> int | None:
        # DuckDB baseline has application-layer scoping, not a DB-native RLS claim.
        del run_id, organization_id
        return None

    def metadata(self) -> dict[str, str]:
        return {
            "candidate": self.name,
            "duckdb_version": duckdb.__version__,
            "scope_enforcement": "application_adapter",
            "connection_model": "connection_per_operation",
        }


class PostgreSQLOperationalCandidate:
    """Experimental PostgreSQL adapter with non-superuser RLS enforcement.

    This class deliberately lives under ``research``. It is not a production implementation
    and must not be imported by the product runtime unless OPS-STORE-001 promotes it.
    """

    name = "postgresql"
    app_role = "academy_benchmark_app"
    app_password = "academy-benchmark-local-only"

    def __init__(
        self,
        *,
        admin_dsn: str,
        schema: str,
        pool_max_size: int = 32,
    ) -> None:
        if not admin_dsn:
            raise ValueError("admin_dsn is required")
        if not schema.replace("_", "").isalnum() or not schema[0].isalpha():
            raise ValueError("schema must be a simple SQL identifier")
        self.admin_dsn = admin_dsn
        self.schema = schema
        self.pool_max_size = max(1, pool_max_size)
        self._pool: Any | None = None
        self._bootstrap_role()
        self.reset()

    @staticmethod
    def _imports():
        try:
            import psycopg
            from psycopg import sql
            from psycopg.conninfo import conninfo_to_dict, make_conninfo
            from psycopg_pool import ConnectionPool
        except ImportError as exc:  # pragma: no cover - exercised by dependency preflight
            raise RuntimeError(
                "Install .[operational-store-benchmark] to run PostgreSQL candidate"
            ) from exc
        return psycopg, sql, conninfo_to_dict, make_conninfo, ConnectionPool

    def _admin_connect(self, *, autocommit: bool = True):
        psycopg, _, _, _, _ = self._imports()
        return psycopg.connect(self.admin_dsn, autocommit=autocommit)

    def _app_dsn(self) -> str:
        _, _, conninfo_to_dict, make_conninfo, _ = self._imports()
        params = conninfo_to_dict(self.admin_dsn)
        params["user"] = self.app_role
        params["password"] = self.app_password
        return make_conninfo(**params)

    def _bootstrap_role(self) -> None:
        _, sql, _, _, _ = self._imports()
        with self._admin_connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s",
                (self.app_role,),
            ).fetchone()
            if exists is None:
                connection.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(self.app_role),
                        sql.Literal(self.app_password),
                    )
                )
            else:
                connection.execute(
                    sql.SQL(
                        "ALTER ROLE {} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD {}"
                    ).format(
                        sql.Identifier(self.app_role),
                        sql.Literal(self.app_password),
                    )
                )

    def _open_pool(self) -> None:
        _, _, _, _, ConnectionPool = self._imports()
        self._pool = ConnectionPool(
            conninfo=self._app_dsn(),
            min_size=1,
            max_size=self.pool_max_size,
            open=True,
            timeout=30.0,
        )
        self._pool.wait(timeout=30.0)

    def _close_pool(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool = None

    def reset(self) -> None:
        self._close_pool()
        _, sql, _, _, _ = self._imports()
        schema = sql.Identifier(self.schema)
        role = sql.Identifier(self.app_role)
        ownership = sql.SQL("{}.run_ownership").format(schema)
        executions = sql.SQL("{}.run_executions").format(schema)
        with self._admin_connect() as connection:
            connection.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(schema))
            connection.execute(sql.SQL("CREATE SCHEMA {}").format(schema))
            connection.execute(
                sql.SQL(
                    """
                    CREATE TABLE {} (
                        run_id TEXT PRIMARY KEY,
                        organization_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ).format(ownership)
            )
            connection.execute(
                sql.SQL(
                    """
                    CREATE TABLE {} (
                        run_id TEXT PRIMARY KEY REFERENCES {}(run_id),
                        organization_id TEXT NOT NULL,
                        execution_kind TEXT NOT NULL CHECK (execution_kind IN ('runtime', 'action')),
                        state TEXT NOT NULL CHECK (
                            state IN ('accepted', 'running', 'completed', 'failed', 'interrupted', 'uncertain')
                        ),
                        related_action_id TEXT,
                        transition_count INTEGER NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CHECK (
                            (execution_kind = 'runtime' AND related_action_id IS NULL)
                            OR (execution_kind = 'action' AND related_action_id IS NOT NULL)
                        )
                    )
                    """
                ).format(executions, ownership)
            )
            for table in (ownership, executions):
                connection.execute(sql.SQL("ALTER TABLE {} ENABLE ROW LEVEL SECURITY").format(table))
            connection.execute(
                sql.SQL(
                    """
                    CREATE POLICY run_ownership_org_scope ON {}
                    FOR ALL TO {}
                    USING (organization_id = current_setting('academy.organization_id', true))
                    WITH CHECK (organization_id = current_setting('academy.organization_id', true))
                    """
                ).format(ownership, role)
            )
            connection.execute(
                sql.SQL(
                    """
                    CREATE POLICY run_executions_org_scope ON {}
                    FOR ALL TO {}
                    USING (organization_id = current_setting('academy.organization_id', true))
                    WITH CHECK (organization_id = current_setting('academy.organization_id', true))
                    """
                ).format(executions, role)
            )
            connection.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(schema, role))
            connection.execute(
                sql.SQL("GRANT SELECT, INSERT, UPDATE ON TABLE {}, {} TO {}").format(
                    ownership,
                    executions,
                    role,
                )
            )
        self._open_pool()

    def close(self) -> None:
        self._close_pool()

    def destroy(self) -> None:
        self._close_pool()
        _, sql, _, _, _ = self._imports()
        with self._admin_connect() as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema))
            )

    def reconnect(self) -> None:
        self._close_pool()
        self._open_pool()

    @contextmanager
    def _tenant_connection(self, organization_id: str) -> Iterator[Any]:
        if self._pool is None:
            raise RuntimeError("postgres_pool_closed")
        with self._pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT set_config('academy.organization_id', %s, true)",
                    (organization_id,),
                )
                yield connection

    def _table(self, name: str):
        _, sql, _, _, _ = self._imports()
        return sql.SQL("{}.{}").format(sql.Identifier(self.schema), sql.Identifier(name))

    def claim_run(self, *, run_id: str, organization_id: str, user_id: str) -> bool:
        _, sql, _, _, _ = self._imports()
        table = self._table("run_ownership")
        with self._tenant_connection(organization_id) as connection:
            inserted = connection.execute(
                sql.SQL(
                    """
                    INSERT INTO {}(run_id, organization_id, user_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (run_id) DO NOTHING
                    RETURNING run_id
                    """
                ).format(table),
                (run_id, organization_id, user_id),
            ).fetchone()
            if inserted is not None:
                return True
            existing = connection.execute(
                sql.SQL(
                    "SELECT organization_id, user_id FROM {} WHERE run_id = %s"
                ).format(table),
                (run_id,),
            ).fetchone()
            if existing == (organization_id, user_id):
                return False
            raise RuntimeError("run_ownership_conflict")

    def scoped_owner(self, *, run_id: str, organization_id: str) -> ScopedOwner | None:
        _, sql, _, _, _ = self._imports()
        table = self._table("run_ownership")
        with self._tenant_connection(organization_id) as connection:
            row = connection.execute(
                sql.SQL(
                    "SELECT run_id, organization_id, user_id FROM {} WHERE run_id = %s"
                ).format(table),
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return ScopedOwner(run_id=str(row[0]), organization_id=str(row[1]), user_id=str(row[2]))

    def create_execution(
        self,
        *,
        run_id: str,
        organization_id: str,
        execution_kind: ExecutionKind = "runtime",
        related_action_id: str | None = None,
    ) -> None:
        if execution_kind == "runtime" and related_action_id is not None:
            raise ValueError("runtime execution cannot carry related_action_id")
        if execution_kind == "action" and not related_action_id:
            raise ValueError("action execution requires related_action_id")
        _, sql, _, _, _ = self._imports()
        table = self._table("run_executions")
        with self._tenant_connection(organization_id) as connection:
            inserted = connection.execute(
                sql.SQL(
                    """
                    INSERT INTO {}(
                        run_id, organization_id, execution_kind, state,
                        related_action_id, transition_count
                    ) VALUES (%s, %s, %s, 'accepted', %s, 1)
                    ON CONFLICT (run_id) DO NOTHING
                    RETURNING run_id
                    """
                ).format(table),
                (run_id, organization_id, execution_kind, related_action_id),
            ).fetchone()
            if inserted is None:
                existing = connection.execute(
                    sql.SQL(
                        """
                        SELECT execution_kind, state, related_action_id
                        FROM {} WHERE run_id = %s
                        """
                    ).format(table),
                    (run_id,),
                ).fetchone()
                if existing == (execution_kind, "accepted", related_action_id):
                    return
                raise RuntimeError("run_execution_conflict")

    def transition_execution(
        self,
        *,
        run_id: str,
        organization_id: str,
        expected_states: frozenset[str],
        new_state: ExecutionState,
    ) -> bool:
        if not expected_states:
            raise ValueError("expected_states must be non-empty")
        _, sql, _, _, _ = self._imports()
        table = self._table("run_executions")
        with self._tenant_connection(organization_id) as connection:
            row = connection.execute(
                sql.SQL(
                    """
                    UPDATE {}
                    SET state = %s,
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE run_id = %s AND state = ANY(%s)
                    RETURNING run_id
                    """
                ).format(table),
                (new_state, run_id, list(expected_states)),
            ).fetchone()
            return row is not None

    def execution_state(self, *, run_id: str, organization_id: str) -> str | None:
        _, sql, _, _, _ = self._imports()
        table = self._table("run_executions")
        with self._tenant_connection(organization_id) as connection:
            row = connection.execute(
                sql.SQL("SELECT state FROM {} WHERE run_id = %s").format(table),
                (run_id,),
            ).fetchone()
        return None if row is None else str(row[0])

    def reconcile_orphaned(self) -> dict[str, int]:
        _, sql, _, _, _ = self._imports()
        table = self._table("run_executions")
        with self._admin_connect(autocommit=False) as connection:
            runtime_rows = connection.execute(
                sql.SQL(
                    """
                    UPDATE {}
                    SET state = 'interrupted',
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE execution_kind = 'runtime' AND state IN ('accepted', 'running')
                    RETURNING run_id
                    """
                ).format(table)
            ).fetchall()
            action_rows = connection.execute(
                sql.SQL(
                    """
                    UPDATE {}
                    SET state = 'uncertain',
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE execution_kind = 'action' AND state IN ('accepted', 'running')
                    RETURNING run_id
                    """
                ).format(table)
            ).fetchall()
            connection.commit()
        return {"interrupted": len(runtime_rows), "uncertain": len(action_rows)}

    def prefix_counts(self, prefix: str) -> dict[str, int]:
        _, sql, _, _, _ = self._imports()
        ownership = self._table("run_ownership")
        executions = self._table("run_executions")
        with self._admin_connect() as connection:
            ownership_count = int(
                connection.execute(
                    sql.SQL("SELECT COUNT(*) FROM {} WHERE run_id LIKE %s").format(ownership),
                    (f"{prefix}%",),
                ).fetchone()[0]
            )
            rows = connection.execute(
                sql.SQL(
                    """
                    SELECT state, COUNT(*)
                    FROM {}
                    WHERE run_id LIKE %s
                    GROUP BY state
                    """
                ).format(executions),
                (f"{prefix}%",),
            ).fetchall()
        counts = {"ownership": ownership_count, "execution_total": 0}
        for state, count in rows:
            value = int(count)
            counts[str(state)] = value
            counts["execution_total"] += value
        return counts

    def direct_cross_tenant_probe(
        self,
        *,
        run_id: str,
        organization_id: str,
    ) -> int | None:
        _, sql, _, _, _ = self._imports()
        table = self._table("run_ownership")
        with self._tenant_connection(organization_id) as connection:
            return int(
                connection.execute(
                    sql.SQL("SELECT COUNT(*) FROM {} WHERE run_id = %s").format(table),
                    (run_id,),
                ).fetchone()[0]
            )

    def metadata(self) -> dict[str, str]:
        psycopg, _, _, _, _ = self._imports()
        with self._admin_connect() as connection:
            server_version = str(connection.execute("SHOW server_version").fetchone()[0])
        return {
            "candidate": self.name,
            "psycopg_version": psycopg.__version__,
            "postgresql_server_version": server_version,
            "scope_enforcement": "postgresql_row_level_security",
            "connection_model": "psycopg_pool",
        }
