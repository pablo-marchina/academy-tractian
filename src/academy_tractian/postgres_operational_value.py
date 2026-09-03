from __future__ import annotations

import json
from uuid import uuid4

from .operational_value_collection import (
    PilotAssignmentRecord,
    pilot_operator_ref_sha256,
)
from .operational_value_pilot import (
    OperationalPilotCompletion,
    OperationalPilotManifest,
    OperationalPilotPacket,
    OperationalPilotTask,
    _verify_packet_manifest_integrity,
)
from .postgres_operational import PostgresOperationalDatabase, _identifier


_OPERATIONAL_VALUE_COLLECTION_SCHEMA_VERSION = "operational-value-collection-v4"
_TASK_PAIR_CONSTRAINT = "operational_pilot_tasks_pair_binding_v4"
_ASSIGNMENT_PAIR_FK = "operational_pilot_assignments_task_pair_fkey_v4"
_ASSIGNMENT_STATE_CONSTRAINT = "operational_pilot_assignment_state_shape_v4"


class PostgresOperationalPilotStore:
    """Private operational store for blinded human-effort collection.

    PostgreSQL owns task reservation, assignment state and completion custody. The operator-facing
    API only receives the safe task payload. Pair identity is retained privately solely to enforce
    the independent-matched anti-crossover invariant.
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

    def initialize_schema(self) -> None:
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema}".operational_pilot_tasks (
                        organization_id TEXT NOT NULL,
                        packet_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        pair_id TEXT NOT NULL,
                        condition TEXT NOT NULL CHECK (condition IN ('MANUAL','ASSISTED')),
                        display_order INTEGER NOT NULL CHECK (display_order >= 0),
                        task_payload JSONB NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (organization_id, task_id),
                        UNIQUE (organization_id, packet_id, display_order),
                        CONSTRAINT {_TASK_PAIR_CONSTRAINT}
                            UNIQUE (organization_id, task_id, packet_id, pair_id)
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema}".operational_pilot_assignments (
                        assignment_id TEXT PRIMARY KEY,
                        organization_id TEXT NOT NULL,
                        packet_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        pair_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        operator_ref_sha256 TEXT NOT NULL,
                        host_session_id TEXT NOT NULL,
                        state TEXT NOT NULL CHECK (
                            state IN ('ACTIVE','VALID','INTERRUPTED','TECHNICAL_FAILURE','WITHDRAWN')
                        ),
                        started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        finished_at TIMESTAMPTZ,
                        elapsed_seconds DOUBLE PRECISION,
                        terminal_decision TEXT,
                        conclusion_summary TEXT,
                        invalid_reason TEXT,
                        CONSTRAINT {_ASSIGNMENT_PAIR_FK}
                            FOREIGN KEY (organization_id, task_id, packet_id, pair_id)
                            REFERENCES "{schema}".operational_pilot_tasks(
                                organization_id, task_id, packet_id, pair_id
                            )
                            ON DELETE RESTRICT,
                        CHECK (elapsed_seconds IS NULL OR elapsed_seconds > 0),
                        CONSTRAINT {_ASSIGNMENT_STATE_CONSTRAINT} CHECK (
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
                                AND invalid_reason IS NOT NULL
                                AND length(btrim(invalid_reason)) > 0
                            )
                        )
                    )
                    """
                )

                # ``CREATE TABLE IF NOT EXISTS`` is not a migration. Explicitly install the v4
                # invariants as named constraints so an older pilot schema cannot merely receive a
                # new metadata version and appear production-ready. Adding a constraint validates
                # all existing rows; incompatible historical data therefore fails closed here.
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
                              AND t.relname = 'operational_pilot_tasks'
                              AND c.conname = '{_TASK_PAIR_CONSTRAINT}'
                        ) THEN
                            ALTER TABLE "{schema}".operational_pilot_tasks
                            ADD CONSTRAINT {_TASK_PAIR_CONSTRAINT}
                            UNIQUE (organization_id, task_id, packet_id, pair_id);
                        END IF;
                    END
                    $migration$
                    """
                )
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
                              AND c.conname = '{_ASSIGNMENT_PAIR_FK}'
                        ) THEN
                            ALTER TABLE "{schema}".operational_pilot_assignments
                            ADD CONSTRAINT {_ASSIGNMENT_PAIR_FK}
                            FOREIGN KEY (organization_id, task_id, packet_id, pair_id)
                            REFERENCES "{schema}".operational_pilot_tasks(
                                organization_id, task_id, packet_id, pair_id
                            )
                            ON DELETE RESTRICT;
                        END IF;
                    END
                    $migration$
                    """
                )
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
                    CREATE UNIQUE INDEX IF NOT EXISTS operational_pilot_one_active_per_task
                    ON "{schema}".operational_pilot_assignments(organization_id, task_id)
                    WHERE state = 'ACTIVE'
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS operational_pilot_one_valid_per_task
                    ON "{schema}".operational_pilot_assignments(organization_id, task_id)
                    WHERE state = 'VALID'
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS operational_pilot_one_active_per_user
                    ON "{schema}".operational_pilot_assignments(organization_id, user_id)
                    WHERE state = 'ACTIVE'
                    """
                )
                connection.execute(
                    f'ALTER TABLE "{schema}".operational_pilot_tasks ENABLE ROW LEVEL SECURITY'
                )
                connection.execute(
                    f'ALTER TABLE "{schema}".operational_pilot_assignments ENABLE ROW LEVEL SECURITY'
                )
                for table in ("operational_pilot_tasks", "operational_pilot_assignments"):
                    connection.execute(
                        f'DROP POLICY IF EXISTS tenant_select ON "{schema}".{table}'
                    )
                    connection.execute(
                        f"""
                        CREATE POLICY tenant_select ON "{schema}".{table}
                        FOR SELECT
                        USING (
                            organization_id = current_setting('academy.organization_id', true)
                        )
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

        with self.database.scoped_pool.connection() as scoped_connection:
            scoped_role = str(scoped_connection.execute("SELECT current_user").fetchone()[0])
        role = _identifier(scoped_role, label="scoped role")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"')
                connection.execute(
                    f'GRANT SELECT ON "{schema}".operational_pilot_tasks TO "{role}"'
                )
                connection.execute(
                    f'GRANT SELECT ON "{schema}".operational_pilot_assignments TO "{role}"'
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

    def register_packet(
        self,
        *,
        organization_id: str,
        packet: OperationalPilotPacket,
        manifest: OperationalPilotManifest,
    ) -> None:
        if not organization_id:
            raise ValueError("organization_id must be non-empty")
        packet = OperationalPilotPacket.model_validate(packet.model_dump(mode="json"))
        manifest = OperationalPilotManifest.model_validate(manifest.model_dump(mode="json"))
        _verify_packet_manifest_integrity(packet, manifest)
        entries = {entry.task_id: entry for entry in manifest.entries}
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                for display_order, task in enumerate(packet.tasks):
                    entry = entries[task.task_id]
                    payload = json.dumps(
                        task.model_dump(mode="json"),
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    inserted = connection.execute(
                        f"""
                        INSERT INTO "{schema}".operational_pilot_tasks(
                            organization_id, packet_id, task_id, pair_id, condition,
                            display_order, task_payload, active
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, TRUE)
                        ON CONFLICT (organization_id, task_id) DO NOTHING
                        RETURNING task_id
                        """,
                        (
                            organization_id,
                            packet.packet_id,
                            task.task_id,
                            entry.pair_id,
                            task.condition,
                            display_order,
                            payload,
                        ),
                    ).fetchone()
                    if inserted is not None:
                        continue
                    existing = connection.execute(
                        f"""
                        SELECT packet_id, pair_id, condition, display_order, task_payload
                        FROM "{schema}".operational_pilot_tasks
                        WHERE organization_id = %s AND task_id = %s
                        """,
                        (organization_id, task.task_id),
                    ).fetchone()
                    expected_payload = task.model_dump(mode="json")
                    if existing is None or (
                        str(existing[0]) != packet.packet_id
                        or str(existing[1]) != entry.pair_id
                        or str(existing[2]) != task.condition
                        or int(existing[3]) != display_order
                        or existing[4] != expected_payload
                    ):
                        raise RuntimeError("operational_pilot_registration_conflict")

    @staticmethod
    def _assignment(row: object | None) -> PilotAssignmentRecord | None:
        if row is None:
            return None
        values = tuple(row)  # type: ignore[arg-type]
        task_payload = values[8]
        if isinstance(task_payload, str):
            task_payload = json.loads(task_payload)
        return PilotAssignmentRecord(
            assignment_id=str(values[0]),
            organization_id=str(values[1]),
            packet_id=str(values[2]),
            task=OperationalPilotTask.model_validate(task_payload),
            pair_id=str(values[4]),
            user_id=str(values[5]),
            operator_ref_sha256=str(values[6]),
            host_session_id=str(values[7]),
        )

    def get_active_for_user(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> PilotAssignmentRecord | None:
        with self.database.scoped_connection(organization_id) as connection:
            row = connection.execute(
                f"""
                SELECT a.assignment_id, a.organization_id, a.packet_id, a.task_id,
                       a.pair_id, a.user_id, a.operator_ref_sha256, a.host_session_id,
                       t.task_payload
                FROM "{self.schema}".operational_pilot_assignments AS a
                JOIN "{self.schema}".operational_pilot_tasks AS t
                  ON t.organization_id = a.organization_id AND t.task_id = a.task_id
                WHERE a.organization_id = %s AND a.user_id = %s AND a.state = 'ACTIVE'
                """,
                (organization_id, user_id),
            ).fetchone()
        return self._assignment(row)

    def reconcile_active_host_session(self, host_session_id: str) -> tuple[str, ...]:
        if not host_session_id:
            raise ValueError("host_session_id must be non-empty")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                rows = connection.execute(
                    f"""
                    UPDATE "{self.schema}".operational_pilot_assignments
                    SET state = 'TECHNICAL_FAILURE', finished_at = CURRENT_TIMESTAMP,
                        invalid_reason = 'host_timer_session_lost'
                    WHERE state = 'ACTIVE' AND host_session_id <> %s
                    RETURNING assignment_id
                    """,
                    (host_session_id,),
                ).fetchall()
        return tuple(sorted(str(row[0]) for row in rows))

    def assign_next(
        self,
        *,
        organization_id: str,
        user_id: str,
        operator_ref_sha256: str,
        host_session_id: str,
    ) -> PilotAssignmentRecord | None:
        # ``operator_ref_sha256`` is a trusted principal marker from the API. Re-scope it to the
        # selected packet below so identities cannot be correlated across studies.
        if not organization_id or not user_id or not host_session_id:
            raise ValueError("assignment principal fields must be non-empty")
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                # Serialize assignment for one trusted principal. JSON gives the lock namespace
                # an unambiguous, NUL-free text representation even if principal fields contain
                # delimiter-like characters. PostgreSQL then hashes that canonical text to bigint.
                advisory_lock_key = json.dumps(
                    ["operational-value-principal-v1", organization_id, user_id],
                    ensure_ascii=True,
                    separators=(",", ":"),
                )
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (advisory_lock_key,),
                )
                existing = connection.execute(
                    f"""
                    SELECT a.assignment_id, a.organization_id, a.packet_id, a.task_id,
                           a.pair_id, a.user_id, a.operator_ref_sha256, a.host_session_id,
                           t.task_payload
                    FROM "{schema}".operational_pilot_assignments AS a
                    JOIN "{schema}".operational_pilot_tasks AS t
                      ON t.organization_id = a.organization_id AND t.task_id = a.task_id
                    WHERE a.organization_id = %s AND a.user_id = %s AND a.state = 'ACTIVE'
                    FOR UPDATE OF a
                    """,
                    (organization_id, user_id),
                ).fetchone()
                if existing is not None:
                    return self._assignment(existing)

                task = connection.execute(
                    f"""
                    SELECT t.packet_id, t.task_id, t.pair_id, t.task_payload
                    FROM "{schema}".operational_pilot_tasks AS t
                    WHERE t.organization_id = %s
                      AND t.active = TRUE
                      AND NOT EXISTS (
                          SELECT 1 FROM "{schema}".operational_pilot_assignments AS completed
                          WHERE completed.organization_id = t.organization_id
                            AND completed.task_id = t.task_id
                            AND completed.state = 'VALID'
                      )
                      AND NOT EXISTS (
                          SELECT 1 FROM "{schema}".operational_pilot_assignments AS active
                          WHERE active.organization_id = t.organization_id
                            AND active.task_id = t.task_id
                            AND active.state = 'ACTIVE'
                      )
                      AND NOT EXISTS (
                          SELECT 1 FROM "{schema}".operational_pilot_assignments AS exposure
                          WHERE exposure.organization_id = t.organization_id
                            AND exposure.user_id = %s
                            AND exposure.pair_id = t.pair_id
                      )
                    ORDER BY t.created_at, t.packet_id, t.display_order
                    FOR UPDATE OF t SKIP LOCKED
                    LIMIT 1
                    """,
                    (organization_id, user_id),
                ).fetchone()
                if task is None:
                    return None

                packet_id = str(task[0])
                task_id = str(task[1])
                pair_id = str(task[2])
                task_payload = task[3]
                if isinstance(task_payload, str):
                    task_payload = json.loads(task_payload)
                assignment_id = f"ova_{uuid4().hex[:24]}"
                # Bind the trusted principal marker to this packet. The helper's user_id input is
                # intentionally the pre-hashed marker so no raw identity is encoded in the digest.
                scoped_operator_ref = pilot_operator_ref_sha256(
                    packet_id=packet_id,
                    organization_id=organization_id,
                    user_id=operator_ref_sha256,
                )
                connection.execute(
                    f"""
                    INSERT INTO "{schema}".operational_pilot_assignments(
                        assignment_id, organization_id, packet_id, task_id, pair_id, user_id,
                        operator_ref_sha256, host_session_id, state
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
                    """,
                    (
                        assignment_id,
                        organization_id,
                        packet_id,
                        task_id,
                        pair_id,
                        user_id,
                        scoped_operator_ref,
                        host_session_id,
                    ),
                )
                return PilotAssignmentRecord(
                    assignment_id=assignment_id,
                    organization_id=organization_id,
                    packet_id=packet_id,
                    task=OperationalPilotTask.model_validate(task_payload),
                    pair_id=pair_id,
                    user_id=user_id,
                    operator_ref_sha256=scoped_operator_ref,
                    host_session_id=host_session_id,
                )

    def fail_active(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        reason: str,
    ) -> bool:
        if not reason:
            raise ValueError("reason must be non-empty")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE "{self.schema}".operational_pilot_assignments
                    SET state = 'TECHNICAL_FAILURE', finished_at = CURRENT_TIMESTAMP,
                        invalid_reason = %s
                    WHERE assignment_id = %s AND organization_id = %s AND user_id = %s
                      AND state = 'ACTIVE'
                    RETURNING assignment_id
                    """,
                    (reason, assignment_id, organization_id, user_id),
                ).fetchone()
        return row is not None

    def complete_valid(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        elapsed_seconds: float,
        terminal_decision: str,
        conclusion_summary: str,
    ) -> OperationalPilotCompletion:
        schema = self.schema
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    SELECT packet_id, task_id, operator_ref_sha256, state
                    FROM "{schema}".operational_pilot_assignments
                    WHERE assignment_id = %s AND organization_id = %s AND user_id = %s
                    FOR UPDATE
                    """,
                    (assignment_id, organization_id, user_id),
                ).fetchone()
                if row is None:
                    raise KeyError(assignment_id)
                if str(row[3]) != "ACTIVE":
                    raise RuntimeError("operational_pilot_assignment_not_active")
                completion = OperationalPilotCompletion(
                    packet_id=str(row[0]),
                    task_id=str(row[1]),
                    operator_ref_sha256=str(row[2]),
                    status="VALID",
                    elapsed_seconds=elapsed_seconds,
                    terminal_decision=terminal_decision,
                    conclusion_summary=conclusion_summary,
                )
                updated = connection.execute(
                    f"""
                    UPDATE "{schema}".operational_pilot_assignments
                    SET state = 'VALID', finished_at = CURRENT_TIMESTAMP,
                        elapsed_seconds = %s, terminal_decision = %s,
                        conclusion_summary = %s, invalid_reason = NULL
                    WHERE assignment_id = %s AND state = 'ACTIVE'
                    RETURNING assignment_id
                    """,
                    (
                        completion.elapsed_seconds,
                        completion.terminal_decision,
                        completion.conclusion_summary,
                        assignment_id,
                    ),
                ).fetchone()
                if updated is None:
                    raise RuntimeError("operational_pilot_assignment_completion_race")
        return completion

    def list_completions(
        self,
        *,
        organization_id: str,
        packet_id: str,
    ) -> tuple[OperationalPilotCompletion, ...]:
        with self.database.scoped_connection(organization_id) as connection:
            rows = connection.execute(
                f"""
                SELECT packet_id, task_id, operator_ref_sha256, state, elapsed_seconds,
                       terminal_decision, conclusion_summary, invalid_reason
                FROM "{self.schema}".operational_pilot_assignments
                WHERE organization_id = %s AND packet_id = %s AND state <> 'ACTIVE'
                ORDER BY task_id, started_at
                """,
                (organization_id, packet_id),
            ).fetchall()
        completions: list[OperationalPilotCompletion] = []
        for row in rows:
            state = str(row[3])
            completions.append(
                OperationalPilotCompletion(
                    packet_id=str(row[0]),
                    task_id=str(row[1]),
                    operator_ref_sha256=str(row[2]),
                    status=state,  # type: ignore[arg-type]
                    elapsed_seconds=(float(row[4]) if row[4] is not None else None),
                    terminal_decision=(str(row[5]) if row[5] is not None else None),
                    conclusion_summary=(str(row[6]) if row[6] is not None else None),
                    invalid_reason=(str(row[7]) if row[7] is not None else None),
                )
            )
        return tuple(completions)
