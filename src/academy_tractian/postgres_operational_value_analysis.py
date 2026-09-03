from __future__ import annotations

from .operational_value_analysis import (
    OperationalValueCollectionSnapshot,
    OperationalValueTaskSlot,
    OperationalValueValidMeasurement,
    build_operational_value_snapshot,
)
from .postgres_operational import PostgresOperationalDatabase


_INVALID_STATES = ("INTERRUPTED", "TECHNICAL_FAILURE", "WITHDRAWN")


class PostgresOperationalValueAnalysisStore:
    """Trusted freeze/snapshot boundary for human-effort analysis.

    This store is intentionally not attached to the participant FastAPI surface. It reads private
    pair/operator/timing material with the internal PostgreSQL connection only after the collection
    protocol explicitly closes a packet. Closing is irreversible through this API and refuses to
    race an active human measurement.
    """

    def __init__(self, database: PostgresOperationalDatabase) -> None:
        self.database = database
        self.schema = database.schema

    def close_packet(self, *, organization_id: str, packet_id: str) -> int:
        if not organization_id or not packet_id:
            raise ValueError("organization_id and packet_id are required")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                tasks = connection.execute(
                    f"""
                    SELECT task_id
                    FROM "{self.schema}".operational_pilot_tasks
                    WHERE organization_id = %s AND packet_id = %s
                    ORDER BY task_id
                    FOR UPDATE
                    """,
                    (organization_id, packet_id),
                ).fetchall()
                if not tasks:
                    raise KeyError(packet_id)

                active = connection.execute(
                    f"""
                    SELECT assignment_id
                    FROM "{self.schema}".operational_pilot_assignments
                    WHERE organization_id = %s AND packet_id = %s AND state = 'ACTIVE'
                    ORDER BY assignment_id
                    FOR UPDATE
                    """,
                    (organization_id, packet_id),
                ).fetchall()
                if active:
                    raise RuntimeError("operational_value_close_blocked_active_assignments")

                closed = connection.execute(
                    f"""
                    UPDATE "{self.schema}".operational_pilot_tasks
                    SET active = FALSE
                    WHERE organization_id = %s AND packet_id = %s AND active = TRUE
                    RETURNING task_id
                    """,
                    (organization_id, packet_id),
                ).fetchall()
        return len(closed)

    def snapshot(
        self,
        *,
        organization_id: str,
        packet_id: str,
    ) -> OperationalValueCollectionSnapshot:
        if not organization_id or not packet_id:
            raise ValueError("organization_id and packet_id are required")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                task_rows = connection.execute(
                    f"""
                    SELECT task_id, pair_id, condition, active
                    FROM "{self.schema}".operational_pilot_tasks
                    WHERE organization_id = %s AND packet_id = %s
                    ORDER BY pair_id, condition, task_id
                    """,
                    (organization_id, packet_id),
                ).fetchall()
                if not task_rows:
                    raise KeyError(packet_id)

                assignment_rows = connection.execute(
                    f"""
                    SELECT task_id, pair_id, operator_ref_sha256, state,
                           elapsed_seconds, terminal_decision
                    FROM "{self.schema}".operational_pilot_assignments
                    WHERE organization_id = %s AND packet_id = %s
                    ORDER BY pair_id, task_id, started_at, assignment_id
                    """,
                    (organization_id, packet_id),
                ).fetchall()

        task_slots = tuple(
            OperationalValueTaskSlot(
                task_id=str(row[0]),
                pair_id=str(row[1]),
                condition=str(row[2]),  # type: ignore[arg-type]
            )
            for row in task_rows
        )
        slot_by_task = {slot.task_id: slot for slot in task_slots}
        active_assignment_count = 0
        invalid_trial_count = 0
        valid_measurements: list[OperationalValueValidMeasurement] = []
        for row in assignment_rows:
            task_id = str(row[0])
            pair_id = str(row[1])
            operator_ref = str(row[2])
            state = str(row[3])
            elapsed = row[4]
            terminal_decision = row[5]
            if state == "ACTIVE":
                active_assignment_count += 1
                continue
            if state in _INVALID_STATES:
                invalid_trial_count += 1
                continue
            if state != "VALID":
                raise RuntimeError("operational_value_unknown_assignment_state")
            slot = slot_by_task.get(task_id)
            if slot is None or slot.pair_id != pair_id:
                raise RuntimeError("operational_value_assignment_task_binding_mismatch")
            if elapsed is None or terminal_decision is None:
                raise RuntimeError("operational_value_valid_measurement_incomplete")
            valid_measurements.append(
                OperationalValueValidMeasurement(
                    task_id=task_id,
                    pair_id=pair_id,
                    condition=slot.condition,
                    operator_ref_sha256=operator_ref,
                    elapsed_seconds=float(elapsed),
                    terminal_decision=str(terminal_decision),  # type: ignore[arg-type]
                )
            )

        collection_closed = all(not bool(row[3]) for row in task_rows)
        return build_operational_value_snapshot(
            organization_id=organization_id,
            packet_id=packet_id,
            collection_closed=collection_closed,
            active_assignment_count=active_assignment_count,
            invalid_trial_count=invalid_trial_count,
            task_slots=task_slots,
            valid_measurements=tuple(valid_measurements),
        )
