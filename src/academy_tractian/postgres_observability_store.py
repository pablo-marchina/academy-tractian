from __future__ import annotations

from typing import Any

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
from .postgres_operational import PostgresOperationalDatabase


# Safe-projection contract version. Storage technology is evidenced independently.
OBSERVABILITY_SCHEMA_VERSION = "observability-store-v1"


class PostgresObservabilityStore:
    """Shared PostgreSQL persistence for browser-safe observability projections only.

    The store receives the already-qualified production PostgreSQL substrate instead of a DSN
    or filesystem path. The parent application owns pool lifecycle and all replicas therefore
    read and write the same durable safe projection.

    Raw ``RunTrace`` objects may enter through ``persist_trace``. Only the allow-listed
    projection produced by ``project_trace`` / ``project_evaluation`` is persisted.
    """

    def __init__(
        self,
        database: PostgresOperationalDatabase,
        *,
        initialize: bool = False,
    ) -> None:
        self.database = database
        self.schema = database.schema
        if initialize:
            self.initialize_schema()

    def _table(self, name: str) -> str:
        return f'"{self.schema}".observability_{name}'

    def initialize_schema(self) -> None:
        meta = self._table("meta")
        runs = self._table("runs")
        events = self._table("events")
        evidence = self._table("evidence")
        evaluations = self._table("evaluations")

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"')
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {meta} (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {runs} (
                        run_id TEXT PRIMARY KEY,
                        scenario_id TEXT NOT NULL,
                        config_hash TEXT NOT NULL,
                        event_count INTEGER NOT NULL,
                        model_calls INTEGER NOT NULL,
                        tool_proposals INTEGER NOT NULL,
                        tool_calls INTEGER NOT NULL,
                        policy_blocks INTEGER NOT NULL,
                        errors INTEGER NOT NULL,
                        terminal_decision TEXT,
                        terminal_response_mode TEXT,
                        terminal_reason_code TEXT,
                        terminal_message TEXT,
                        completed BOOLEAN NOT NULL
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {events} (
                        event_id TEXT PRIMARY KEY,
                        run_id TEXT NOT NULL,
                        sequence INTEGER NOT NULL,
                        event_type TEXT NOT NULL,
                        origin TEXT NOT NULL,
                        timestamp TEXT,
                        tool_name TEXT,
                        decision_kind TEXT,
                        provider_id TEXT,
                        model_id TEXT,
                        route_id TEXT,
                        live_call BOOLEAN,
                        outcome TEXT,
                        failure_code TEXT,
                        latency_ms INTEGER,
                        turn_index INTEGER,
                        tool_call_count INTEGER,
                        argument_names TEXT,
                        method TEXT,
                        path_template TEXT,
                        tool_kind TEXT,
                        status_code INTEGER,
                        policy_stage TEXT,
                        policy_allowed BOOLEAN,
                        policy_contained BOOLEAN,
                        policy_violation TEXT,
                        evidence_id TEXT,
                        reason_code TEXT,
                        response_mode TEXT,
                        message TEXT,
                        UNIQUE (run_id, sequence)
                    )
                    """
                )
                connection.execute(
                    f"CREATE INDEX IF NOT EXISTS observability_events_run_sequence_idx "
                    f"ON {events} (run_id, sequence)"
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {evidence} (
                        evidence_id TEXT NOT NULL,
                        run_id TEXT NOT NULL,
                        sequence INTEGER NOT NULL,
                        tool_name TEXT,
                        status_code INTEGER,
                        PRIMARY KEY (run_id, sequence, evidence_id)
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {evaluations} (
                        run_id TEXT NOT NULL,
                        check_name TEXT NOT NULL,
                        passed BOOLEAN NOT NULL,
                        blocking BOOLEAN NOT NULL,
                        blocking_pass BOOLEAN NOT NULL,
                        PRIMARY KEY (run_id, check_name)
                    )
                    """
                )
                connection.execute(
                    f"""
                    INSERT INTO {meta}(key, value)
                    VALUES ('schema_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (OBSERVABILITY_SCHEMA_VERSION,),
                )

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                row = connection.execute(
                    f"SELECT value FROM {self._table('meta')} WHERE key = 'schema_version'"
                ).fetchone()
                return bool(row and str(row[0]) == OBSERVABILITY_SCHEMA_VERSION)
        except Exception:
            return False

    @staticmethod
    def _run_values(run: SafeRun) -> tuple[Any, ...]:
        return (
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
        )

    @staticmethod
    def _event_values(event: SafeEvent) -> tuple[Any, ...]:
        return (
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
        )

    def persist_trace(
        self,
        trace: RunTrace,
        *,
        evaluation: ProductionEvaluationReport | None = None,
    ) -> str:
        run, events, evidence = project_trace(trace)
        safe_evaluation = None if evaluation is None else project_evaluation(evaluation)
        return self.persist_projection(run, events, evidence, evaluation=safe_evaluation)

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

        runs = self._table("runs")
        events_table = self._table("events")
        evidence_table = self._table("evidence")
        evaluations = self._table("evaluations")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f"DELETE FROM {evaluations} WHERE run_id = %s", (run.run_id,))
                connection.execute(f"DELETE FROM {evidence_table} WHERE run_id = %s", (run.run_id,))
                connection.execute(f"DELETE FROM {events_table} WHERE run_id = %s", (run.run_id,))
                connection.execute(f"DELETE FROM {runs} WHERE run_id = %s", (run.run_id,))
                connection.execute(
                    f"""
                    INSERT INTO {runs} VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    self._run_values(run),
                )
                for event in events:
                    connection.execute(
                        f"""
                        INSERT INTO {events_table} VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        self._event_values(event),
                    )
                for item in evidence:
                    connection.execute(
                        f"INSERT INTO {evidence_table} VALUES (%s, %s, %s, %s, %s)",
                        (
                            item.evidence_id,
                            item.run_id,
                            item.sequence,
                            item.tool_name,
                            item.status_code,
                        ),
                    )
                if evaluation is not None:
                    for check in evaluation.checks:
                        connection.execute(
                            f"INSERT INTO {evaluations} VALUES (%s, %s, %s, %s, %s)",
                            (
                                evaluation.run_id,
                                check.name,
                                check.passed,
                                check.blocking,
                                evaluation.blocking_pass,
                            ),
                        )
        return run.run_id

    def persist_live_update(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None = None,
    ) -> bool:
        if event.run_id != run.run_id:
            raise ValueError("event run_id does not match SafeRun")
        if evidence is not None and evidence.run_id != run.run_id:
            raise ValueError("evidence run_id does not match SafeRun")
        if evidence is not None and evidence.sequence != event.sequence:
            raise ValueError("evidence sequence does not match SafeEvent")

        runs = self._table("runs")
        events = self._table("events")
        evidence_table = self._table("evidence")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                existed = connection.execute(
                    f"SELECT 1 FROM {events} WHERE event_id = %s",
                    (event.event_id,),
                ).fetchone() is not None
                connection.execute(
                    f"""
                    INSERT INTO {runs} VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (run_id) DO UPDATE SET
                        scenario_id = EXCLUDED.scenario_id,
                        config_hash = EXCLUDED.config_hash,
                        event_count = EXCLUDED.event_count,
                        model_calls = EXCLUDED.model_calls,
                        tool_proposals = EXCLUDED.tool_proposals,
                        tool_calls = EXCLUDED.tool_calls,
                        policy_blocks = EXCLUDED.policy_blocks,
                        errors = EXCLUDED.errors,
                        terminal_decision = EXCLUDED.terminal_decision,
                        terminal_response_mode = EXCLUDED.terminal_response_mode,
                        terminal_reason_code = EXCLUDED.terminal_reason_code,
                        terminal_message = EXCLUDED.terminal_message,
                        completed = EXCLUDED.completed
                    """,
                    self._run_values(run),
                )
                connection.execute(
                    f"""
                    INSERT INTO {events} VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (event_id) DO UPDATE SET
                        run_id = EXCLUDED.run_id,
                        sequence = EXCLUDED.sequence,
                        event_type = EXCLUDED.event_type,
                        origin = EXCLUDED.origin,
                        timestamp = EXCLUDED.timestamp,
                        tool_name = EXCLUDED.tool_name,
                        decision_kind = EXCLUDED.decision_kind,
                        provider_id = EXCLUDED.provider_id,
                        model_id = EXCLUDED.model_id,
                        route_id = EXCLUDED.route_id,
                        live_call = EXCLUDED.live_call,
                        outcome = EXCLUDED.outcome,
                        failure_code = EXCLUDED.failure_code,
                        latency_ms = EXCLUDED.latency_ms,
                        turn_index = EXCLUDED.turn_index,
                        tool_call_count = EXCLUDED.tool_call_count,
                        argument_names = EXCLUDED.argument_names,
                        method = EXCLUDED.method,
                        path_template = EXCLUDED.path_template,
                        tool_kind = EXCLUDED.tool_kind,
                        status_code = EXCLUDED.status_code,
                        policy_stage = EXCLUDED.policy_stage,
                        policy_allowed = EXCLUDED.policy_allowed,
                        policy_contained = EXCLUDED.policy_contained,
                        policy_violation = EXCLUDED.policy_violation,
                        evidence_id = EXCLUDED.evidence_id,
                        reason_code = EXCLUDED.reason_code,
                        response_mode = EXCLUDED.response_mode,
                        message = EXCLUDED.message
                    """,
                    self._event_values(event),
                )
                if evidence is not None:
                    connection.execute(
                        f"""
                        INSERT INTO {evidence_table} VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (run_id, sequence, evidence_id) DO UPDATE SET
                            tool_name = EXCLUDED.tool_name,
                            status_code = EXCLUDED.status_code
                        """,
                        (
                            evidence.evidence_id,
                            evidence.run_id,
                            evidence.sequence,
                            evidence.tool_name,
                            evidence.status_code,
                        ),
                    )
        return not existed

    @staticmethod
    def _rows(cursor: Any) -> list[dict[str, Any]]:
        columns = [
            description.name if hasattr(description, "name") else description[0]
            for description in cursor.description
        ]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

    def overview(self) -> dict[str, Any]:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(CASE WHEN completed THEN 1 ELSE 0 END), 0) AS completed_runs,
                    COALESCE(SUM(model_calls), 0) AS model_calls,
                    COALESCE(SUM(tool_calls), 0) AS tool_calls,
                    COALESCE(SUM(policy_blocks), 0) AS policy_blocks,
                    COALESCE(SUM(errors), 0) AS errors
                FROM {self._table('runs')}
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

    def list_runs(self, *, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be within [1, 1000]")
        with self.database.internal_pool.connection() as connection:
            return self._rows(
                connection.execute(
                    f"SELECT * FROM {self._table('runs')} ORDER BY run_id DESC LIMIT %s",
                    (limit,),
                )
            )

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.database.internal_pool.connection() as connection:
            rows = self._rows(
                connection.execute(
                    f"SELECT * FROM {self._table('runs')} WHERE run_id = %s",
                    (run_id,),
                )
            )
            return rows[0] if rows else None

    def get_events(self, run_id: str) -> list[dict[str, Any]]:
        with self.database.internal_pool.connection() as connection:
            return self._rows(
                connection.execute(
                    f"SELECT * FROM {self._table('events')} WHERE run_id = %s ORDER BY sequence",
                    (run_id,),
                )
            )

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
        with self.database.internal_pool.connection() as connection:
            return self._rows(
                connection.execute(
                    f"""
                    SELECT * FROM {self._table('events')}
                    WHERE run_id = %s AND sequence > %s
                    ORDER BY sequence
                    LIMIT %s
                    """,
                    (run_id, after_sequence, limit),
                )
            )

    def get_evidence(self, run_id: str) -> list[dict[str, Any]]:
        with self.database.internal_pool.connection() as connection:
            return self._rows(
                connection.execute(
                    f"SELECT * FROM {self._table('evidence')} WHERE run_id = %s ORDER BY sequence",
                    (run_id,),
                )
            )

    def get_evaluation(self, run_id: str) -> list[dict[str, Any]]:
        with self.database.internal_pool.connection() as connection:
            return self._rows(
                connection.execute(
                    f"SELECT * FROM {self._table('evaluations')} WHERE run_id = %s ORDER BY check_name",
                    (run_id,),
                )
            )
