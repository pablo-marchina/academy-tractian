from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import duckdb


RUN_EXECUTION_SCHEMA_VERSION = "run-execution-store-v1"
ExecutionKind = Literal["runtime", "action"]
ExecutionState = Literal[
    "accepted",
    "running",
    "completed",
    "failed",
    "interrupted",
    "uncertain",
]
_NONTERMINAL_STATES = frozenset({"accepted", "running"})


@dataclass(frozen=True, slots=True)
class DurableExecution:
    run_id: str
    execution_kind: ExecutionKind
    state: ExecutionState
    related_action_id: str | None
    transition_count: int


class DuckDBRunExecutionStore:
    """Durable single-node execution state for restart-safe product status.

    This is the baseline operational adapter, not a claim that DuckDB is the final
    multi-user operational database. Its contract is intentionally small so PostgreSQL can
    be benchmarked and promoted without changing the product API or execution semantics.

    On process restart, an unfinished ordinary runtime is marked ``interrupted`` because the
    private request payload is intentionally not retained for blind replay. An unfinished
    consequential-action execution is marked ``uncertain`` because repeating it could create
    a duplicate side effect.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("DuckDBRunExecutionStore requires a persistent path")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.path)

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_execution_meta (
                    key VARCHAR PRIMARY KEY,
                    value VARCHAR NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_executions (
                    run_id VARCHAR PRIMARY KEY,
                    execution_kind VARCHAR NOT NULL,
                    state VARCHAR NOT NULL,
                    related_action_id VARCHAR,
                    transition_count INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO run_execution_meta(key, value)
                VALUES ('schema_version', ?)
                """,
                [RUN_EXECUTION_SCHEMA_VERSION],
            )
        finally:
            connection.close()

    def ready(self) -> bool:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT value FROM run_execution_meta WHERE key = 'schema_version'"
            ).fetchone()
            return bool(row and row[0] == RUN_EXECUTION_SCHEMA_VERSION)
        finally:
            connection.close()

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

        connection = self._connect()
        try:
            existing = connection.execute(
                """
                SELECT execution_kind, state, related_action_id
                FROM run_executions WHERE run_id = ?
                """,
                [run_id],
            ).fetchone()
            if existing is not None:
                if (
                    str(existing[0]) == execution_kind
                    and str(existing[1]) == "accepted"
                    and existing[2] == related_action_id
                ):
                    return
                raise RuntimeError("run_execution_conflict")
            connection.execute(
                """
                INSERT INTO run_executions(
                    run_id, execution_kind, state, related_action_id, transition_count
                ) VALUES (?, ?, 'accepted', ?, 1)
                """,
                [run_id, execution_kind, related_action_id],
            )
        finally:
            connection.close()

    def transition(
        self,
        *,
        run_id: str,
        expected_states: frozenset[str],
        new_state: ExecutionState,
    ) -> bool:
        if not expected_states:
            raise ValueError("expected_states must be non-empty")
        connection = self._connect()
        try:
            connection.execute("BEGIN TRANSACTION")
            row = connection.execute(
                "SELECT state FROM run_executions WHERE run_id = ?",
                [run_id],
            ).fetchone()
            if row is None or str(row[0]) not in expected_states:
                connection.execute("ROLLBACK")
                return False
            connection.execute(
                """
                UPDATE run_executions
                SET state = ?,
                    transition_count = transition_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE run_id = ?
                """,
                [new_state, run_id],
            )
            connection.execute("COMMIT")
            return True
        except Exception:
            try:
                connection.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            connection.close()

    def get(self, run_id: str) -> DurableExecution | None:
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT run_id, execution_kind, state, related_action_id, transition_count
                FROM run_executions WHERE run_id = ?
                """,
                [run_id],
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return DurableExecution(
            run_id=str(row[0]),
            execution_kind=str(row[1]),  # type: ignore[arg-type]
            state=str(row[2]),  # type: ignore[arg-type]
            related_action_id=None if row[3] is None else str(row[3]),
            transition_count=int(row[4]),
        )

    def reconcile_orphaned(self) -> tuple[DurableExecution, ...]:
        """Fail-safe all nonterminal records left by a previous product process."""

        connection = self._connect()
        try:
            connection.execute("BEGIN TRANSACTION")
            rows = connection.execute(
                """
                SELECT run_id, execution_kind, state, related_action_id, transition_count
                FROM run_executions
                WHERE state IN ('accepted', 'running')
                ORDER BY run_id
                """
            ).fetchall()
            recovered: list[DurableExecution] = []
            for row in rows:
                kind = str(row[1])
                new_state: ExecutionState = "uncertain" if kind == "action" else "interrupted"
                connection.execute(
                    """
                    UPDATE run_executions
                    SET state = ?,
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE run_id = ? AND state IN ('accepted', 'running')
                    """,
                    [new_state, str(row[0])],
                )
                recovered.append(
                    DurableExecution(
                        run_id=str(row[0]),
                        execution_kind=kind,  # type: ignore[arg-type]
                        state=new_state,
                        related_action_id=None if row[3] is None else str(row[3]),
                        transition_count=int(row[4]) + 1,
                    )
                )
            connection.execute("COMMIT")
            return tuple(recovered)
        except Exception:
            try:
                connection.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            connection.close()

    def counts(self) -> dict[str, int]:
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT state, COUNT(*) FROM run_executions GROUP BY state"
            ).fetchall()
        finally:
            connection.close()
        counts = {
            state: 0
            for state in (
                "accepted",
                "running",
                "completed",
                "failed",
                "interrupted",
                "uncertain",
            )
        }
        for state, count in rows:
            counts[str(state)] = int(count)
        return counts
