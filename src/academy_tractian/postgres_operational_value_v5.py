from __future__ import annotations

from typing import Literal

from .operational_value_pilot import OperationalPilotCompletion
from .postgres_operational_value import (
    PostgresOperationalPilotStore,
    _ASSIGNMENT_PAIR_FK,
    _TASK_PAIR_CONSTRAINT,
)


_OPERATIONAL_VALUE_COLLECTION_SCHEMA_VERSION = "operational-value-collection-v5"
_ASSIGNMENT_STATE_CONSTRAINT = "operational_pilot_assignment_state_shape_v5"
HumanTerminationStatus = Literal["INTERRUPTED", "WITHDRAWN"]


class PostgresOperationalPilotStoreV5(PostgresOperationalPilotStore):
    """Promoted pilot store with explicit human termination semantics.

    The v4 store remains the proven reservation/RLS/anti-crossover substrate. This promotion adds
    only the stronger terminal-state invariant and the two human-controlled invalid terminal
    transitions required by the participant UI. It uses the same PostgreSQL tables and pools.
    """

    def initialize_schema(self) -> None:
        super().initialize_schema()
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                # v4 already proves the ACTIVE/VALID shapes. v5 additionally guarantees that an
                # invalid trial can never carry a duration or an operational conclusion. Adding
                # the constraint validates existing rows and fails closed on incompatible history.
                connection.execute(
                    f"""
                    DO $migration$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1
                            FROM pg_constraint c
                            JOIN pg_class t ON t.oid = c.conrelid
                            JOIN pg_namespace n ON n.oid = t.relnamespace
                            WHERE n.nspname = '{schema}'
                              AND t.relname = 'operational_pilot_assignments'
                              AND c.conname = '{_ASSIGNMENT_STATE_CONSTRAINT}'
                        ) THEN
                            ALTER TABLE "{schema}".operational_pilot_assignments
                            ADD CONSTRAINT {_ASSIGNMENT_STATE_CONSTRAINT} CHECK (
                                (
                                    state = 'ACTIVE'
                                    AND finished_at IS NULL
                                    AND elapsed_seconds IS NULL
                                    AND terminal_decision IS NULL
                                    AND conclusion_summary IS NULL
                                    AND invalid_reason IS NULL
                                )
                                OR (
                                    state = 'VALID'
                                    AND finished_at IS NOT NULL
                                    AND elapsed_seconds IS NOT NULL
                                    AND elapsed_seconds > 0
                                    AND terminal_decision IS NOT NULL
                                    AND length(btrim(terminal_decision)) > 0
                                    AND conclusion_summary IS NOT NULL
                                    AND length(btrim(conclusion_summary)) > 0
                                    AND invalid_reason IS NULL
                                )
                                OR (
                                    state IN ('INTERRUPTED','TECHNICAL_FAILURE','WITHDRAWN')
                                    AND finished_at IS NOT NULL
                                    AND elapsed_seconds IS NULL
                                    AND terminal_decision IS NULL
                                    AND conclusion_summary IS NULL
                                    AND invalid_reason IS NOT NULL
                                    AND length(btrim(invalid_reason)) > 0
                                )
                            );
                        END IF;
                    END
                    $migration$
                    """
                )
                connection.execute(
                    f"""
                    INSERT INTO "{schema}".operational_meta(key, value)
                    VALUES ('operational_value_collection_schema_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (_OPERATIONAL_VALUE_COLLECTION_SCHEMA_VERSION,),
                )

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                version = connection.execute(
                    f"""
                    SELECT value FROM "{self.schema}".operational_meta
                    WHERE key = 'operational_value_collection_schema_version'
                    """
                ).fetchone()
                constraints = connection.execute(
                    """
                    SELECT c.conname, c.convalidated
                    FROM pg_constraint c
                    JOIN pg_class t ON t.oid = c.conrelid
                    JOIN pg_namespace n ON n.oid = t.relnamespace
                    WHERE n.nspname = %s
                      AND (
                          (t.relname = 'operational_pilot_tasks' AND c.conname = %s)
                          OR
                          (t.relname = 'operational_pilot_assignments' AND c.conname IN (%s, %s))
                      )
                    """,
                    (
                        self.schema,
                        _TASK_PAIR_CONSTRAINT,
                        _ASSIGNMENT_PAIR_FK,
                        _ASSIGNMENT_STATE_CONSTRAINT,
                    ),
                ).fetchall()
            validated = {str(row[0]) for row in constraints if bool(row[1])}
            required = {
                _TASK_PAIR_CONSTRAINT,
                _ASSIGNMENT_PAIR_FK,
                _ASSIGNMENT_STATE_CONSTRAINT,
            }
            return (
                version is not None
                and str(version[0]) == _OPERATIONAL_VALUE_COLLECTION_SCHEMA_VERSION
                and required.issubset(validated)
            )
        except Exception:
            return False

    def terminate_active(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        terminal_status: HumanTerminationStatus,
    ) -> OperationalPilotCompletion:
        if terminal_status == "INTERRUPTED":
            invalid_reason = "operator_interrupted"
        elif terminal_status == "WITHDRAWN":
            invalid_reason = "operator_withdrew"
        else:
            raise ValueError("unsupported_operational_pilot_human_termination_status")

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE "{self.schema}".operational_pilot_assignments
                    SET state = %s,
                        finished_at = CURRENT_TIMESTAMP,
                        elapsed_seconds = NULL,
                        terminal_decision = NULL,
                        conclusion_summary = NULL,
                        invalid_reason = %s
                    WHERE assignment_id = %s
                      AND organization_id = %s
                      AND user_id = %s
                      AND state = 'ACTIVE'
                    RETURNING packet_id, task_id, operator_ref_sha256
                    """,
                    (
                        terminal_status,
                        invalid_reason,
                        assignment_id,
                        organization_id,
                        user_id,
                    ),
                ).fetchone()
        if row is None:
            raise KeyError(assignment_id)
        return OperationalPilotCompletion(
            packet_id=str(row[0]),
            task_id=str(row[1]),
            operator_ref_sha256=str(row[2]),
            status=terminal_status,
            invalid_reason=invalid_reason,
        )
