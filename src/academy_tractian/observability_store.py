from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any

import duckdb

from research.e2.models import RunTrace

from .evaluation import ProductionEvaluationReport
from .observability import (
    SafeEvaluation,
    SafeEvidenceRef,
    SafeEvent,
    SafeRun,
    project_evaluation,
    project_trace,
)


OBSERVABILITY_SCHEMA_VERSION = "observability-store-v1"


class _SerializedDuckDBConnection:
    """Own one DuckDB file handle at a time for the browser-safe read model.

    DuckDB remains the analytical/evaluation store, but the product frontend performs many
    small concurrent REST/SSE reads while realtime publication writes safe events. DuckDB 1.5
    can otherwise race while repeatedly attaching the same file from multiple Python threads
    (`Unique file handle conflict`). Holding this process-local lock for the lifetime of each
    short store operation removes that file-handle race without changing persisted semantics.

    Mutable multi-user operational state is not routed through this lock; it lives in the
    PostgreSQL production stores selected by OPS-STORE-001.
    """

    def __init__(self, *, path: str, lock: RLock) -> None:
        self._lock = lock
        self._closed = False
        self._lock.acquire()
        try:
            self._connection = duckdb.connect(path)
        except Exception:
            self._lock.release()
            raise

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._connection.close()
        finally:
            self._lock.release()


class ObservabilityStore:
    """DuckDB-backed persistence for browser-safe observability projections only.

    Raw RunTrace objects may enter this class through `persist_trace()`, but only their
    allow-listed projections are persisted. The database is therefore a safe read model,
    not a second raw-trace store.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError(
                "ObservabilityStore requires a persistent DuckDB path; ':memory:' is unsupported"
            )
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._database_lock = RLock()
        self._initialize()

    def _connect(self) -> _SerializedDuckDBConnection:
        return _SerializedDuckDBConnection(path=self.path, lock=self._database_lock)

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS observability_meta (
                    key VARCHAR PRIMARY KEY,
                    value VARCHAR NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id VARCHAR PRIMARY KEY,
                    scenario_id VARCHAR NOT NULL,
                    config_hash VARCHAR NOT NULL,
                    event_count INTEGER NOT NULL,
                    model_calls INTEGER NOT NULL,
                    tool_proposals INTEGER NOT NULL,
                    tool_calls INTEGER NOT NULL,
                    policy_blocks INTEGER NOT NULL,
                    errors INTEGER NOT NULL,
                    terminal_decision VARCHAR,
                    terminal_response_mode VARCHAR,
                    terminal_reason_code VARCHAR,
                    terminal_message VARCHAR,
                    completed BOOLEAN NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id VARCHAR PRIMARY KEY,
                    run_id VARCHAR NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type VARCHAR NOT NULL,
                    origin VARCHAR NOT NULL,
                    timestamp VARCHAR,
                    tool_name VARCHAR,
                    decision_kind VARCHAR,
                    provider_id VARCHAR,
                    model_id VARCHAR,
                    route_id VARCHAR,
                    live_call BOOLEAN,
                    outcome VARCHAR,
                    failure_code VARCHAR,
                    latency_ms INTEGER,
                    turn_index INTEGER,
                    tool_call_count INTEGER,
                    argument_names VARCHAR,
                    method VARCHAR,
                    path_template VARCHAR,
                    tool_kind VARCHAR,
                    status_code INTEGER,
                    policy_stage VARCHAR,
                    policy_allowed BOOLEAN,
                    policy_contained BOOLEAN,
                    policy_violation VARCHAR,
                    evidence_id VARCHAR,
                    reason_code VARCHAR,
                    response_mode VARCHAR,
                    message VARCHAR
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id VARCHAR NOT NULL,
                    run_id VARCHAR NOT NULL,
                    sequence INTEGER NOT NULL,
                    tool_name VARCHAR,
                    status_code INTEGER,
                    PRIMARY KEY (run_id, sequence, evidence_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluations (
                    run_id VARCHAR NOT NULL,
                    check_name VARCHAR NOT NULL,
                    passed BOOLEAN NOT NULL,
                    blocking BOOLEAN NOT NULL,
                    blocking_pass BOOLEAN NOT NULL,
                    PRIMARY KEY (run_id, check_name)
                )
                """
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO observability_meta(key, value)
                VALUES ('schema_version', ?)
                """,
                [OBSERVABILITY_SCHEMA_VERSION],
            )
        finally:
            connection.close()

    def ready(self) -> bool:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT value FROM observability_meta WHERE key = 'schema_version'"
            ).fetchone()
            return bool(row and row[0] == OBSERVABILITY_SCHEMA_VERSION)
        finally:
            connection.close()

    @staticmethod
    def _run_values(run: SafeRun) -> list[Any]:
        return [
            run.run_id,
            run.scenario_id,
            run.config_hash,
            run.event_count,
            run.model_calls,
            run.tool_proposals,
            run.tool_calls,
            run.policy_blocks,
            run.errors,
            run.terminal_decision,
            run.terminal_response_mode,
            run.terminal_reason_code,
            run.terminal_message,
            run.completed,
        ]

    @staticmethod
    def _event_values(event: SafeEvent) -> list[Any]:
        return [
            event.event_id,
            event.run_id,
            event.sequence,
            event.event_type,
            event.origin,
            event.timestamp,
            event.tool_name,
            event.decision_kind,
            event.provider_id,
            event.model_id,
            event.route_id,
            event.live_call,
            event.outcome,
            event.failure_code,
            event.latency_ms,
            event.turn_index,
            event.tool_call_count,
            ",".join(event.argument_names),
            event.method,
            event.path_template,
            event.tool_kind,
            event.status_code,
            event.policy_stage,
            event.policy_allowed,
            event.policy_contained,
            event.policy_violation,
            event.evidence_id,
            event.reason_code,
            event.response_mode,
            event.message,
        ]

    def persist_trace(
        self,
        trace: RunTrace,
        *,
        evaluation: ProductionEvaluationReport | None = None,
    ) -> str:
        run, events, evidence = project_trace(trace)
        safe_evaluation = None if evaluation is None else project_evaluation(evaluation)
        return self.persist_projection(
            run,
            events,
            evidence,
            evaluation=safe_evaluation,
        )

    def persist_projection(
        self,
        run: SafeRun,
        events: tuple[SafeEvent, ...],
        evidence: tuple[SafeEvidenceRef, ...],
        *,
        evaluation: SafeEvaluation | None = None,
    ) -> str:
        if any(event.run_id != run.run_id for event in events):
            raise ValueError("event run_id does not match SafeRun")
        if any(item.run_id != run.run_id for item in evidence):
            raise ValueError("evidence run_id does not match SafeRun")
        if evaluation is not None and evaluation.run_id != run.run_id:
            raise ValueError("evaluation run_id does not match SafeRun")

        connection = self._connect()
        try:
            connection.execute("BEGIN TRANSACTION")
            connection.execute("DELETE FROM evaluations WHERE run_id = ?", [run.run_id])
            connection.execute("DELETE FROM evidence WHERE run_id = ?", [run.run_id])
            connection.execute("DELETE FROM events WHERE run_id = ?", [run.run_id])
            connection.execute("DELETE FROM runs WHERE run_id = ?", [run.run_id])
            connection.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                self._run_values(run),
            )
            for event in events:
                connection.execute(
                    """
                    INSERT INTO events VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    self._event_values(event),
                )
            for item in evidence:
                connection.execute(
                    "INSERT INTO evidence VALUES (?, ?, ?, ?, ?)",
                    [
                        item.evidence_id,
                        item.run_id,
                        item.sequence,
                        item.tool_name,
                        item.status_code,
                    ],
                )
            if evaluation is not None:
                for check in evaluation.checks:
                    connection.execute(
                        "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?)",
                        [
                            evaluation.run_id,
                            check.name,
                            check.passed,
                            check.blocking,
                            evaluation.blocking_pass,
                        ],
                    )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()
        return run.run_id

    def persist_live_update(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None = None,
    ) -> bool:
        """Persist one genuine safe event plus the current safe run summary.

        `event_id` and evidence primary keys make duplicate transport/publication idempotent.
        Returning False means the event already existed; the run summary is still refreshed.
        """

        if event.run_id != run.run_id:
            raise ValueError("event run_id does not match SafeRun")
        if evidence is not None and evidence.run_id != run.run_id:
            raise ValueError("evidence run_id does not match SafeRun")
        if evidence is not None and evidence.sequence != event.sequence:
            raise ValueError("evidence sequence does not match SafeEvent")

        connection = self._connect()
        try:
            connection.execute("BEGIN TRANSACTION")
            existed = connection.execute(
                "SELECT 1 FROM events WHERE event_id = ?",
                [event.event_id],
            ).fetchone() is not None

            connection.execute(
                "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                self._run_values(run),
            )
            connection.execute(
                """
                INSERT OR REPLACE INTO events VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                self._event_values(event),
            )
            if evidence is not None:
                connection.execute(
                    "INSERT OR REPLACE INTO evidence VALUES (?, ?, ?, ?, ?)",
                    [
                        evidence.evidence_id,
                        evidence.run_id,
                        evidence.sequence,
                        evidence.tool_name,
                        evidence.status_code,
                    ],
                )
            connection.execute("COMMIT")
            return not existed
        except Exception:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    @staticmethod
    def _rows(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

    def overview(self) -> dict[str, Any]:
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(CASE WHEN completed THEN 1 ELSE 0 END), 0) AS completed_runs,
                    COALESCE(SUM(model_calls), 0) AS model_calls,
                    COALESCE(SUM(tool_calls), 0) AS tool_calls,
                    COALESCE(SUM(policy_blocks), 0) AS policy_blocks,
                    COALESCE(SUM(errors), 0) AS errors
                FROM runs
                """
            ).fetchone()
            assert row is not None
            return {
                "schema_version": OBSERVABILITY_SCHEMA_VERSION,
                "total_runs": int(row[0]),
                "completed_runs": int(row[1]),
                "model_calls": int(row[2]),
                "tool_calls": int(row[3]),
                "policy_blocks": int(row[4]),
                "errors": int(row[5]),
            }
        finally:
            connection.close()

    def list_runs(self, *, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be within [1, 1000]")
        connection = self._connect()
        try:
            return self._rows(
                connection.execute(
                    "SELECT * FROM runs ORDER BY run_id DESC LIMIT ?",
                    [limit],
                )
            )
        finally:
            connection.close()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            rows = self._rows(
                connection.execute("SELECT * FROM runs WHERE run_id = ?", [run_id])
            )
            return rows[0] if rows else None
        finally:
            connection.close()

    def get_events(self, run_id: str) -> list[dict[str, Any]]:
        connection = self._connect()
        try:
            return self._rows(
                connection.execute(
                    "SELECT * FROM events WHERE run_id = ? ORDER BY sequence",
                    [run_id],
                )
            )
        finally:
            connection.close()

    def get_events_after(
        self,
        run_id: str,
        *,
        after_sequence: int = -1,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        if after_sequence < -1:
            raise ValueError("after_sequence must be >= -1")
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be within [1, 1000]")
        connection = self._connect()
        try:
            return self._rows(
                connection.execute(
                    """
                    SELECT * FROM events
                    WHERE run_id = ? AND sequence > ?
                    ORDER BY sequence
                    LIMIT ?
                    """,
                    [run_id, after_sequence, limit],
                )
            )
        finally:
            connection.close()

    def get_evidence(self, run_id: str) -> list[dict[str, Any]]:
        connection = self._connect()
        try:
            return self._rows(
                connection.execute(
                    "SELECT * FROM evidence WHERE run_id = ? ORDER BY sequence",
                    [run_id],
                )
            )
        finally:
            connection.close()

    def get_evaluation(self, run_id: str) -> list[dict[str, Any]]:
        connection = self._connect()
        try:
            return self._rows(
                connection.execute(
                    "SELECT * FROM evaluations WHERE run_id = ? ORDER BY check_name",
                    [run_id],
                )
            )
        finally:
            connection.close()
