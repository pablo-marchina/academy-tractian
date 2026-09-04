from __future__ import annotations

import json
from uuid import uuid4

from .postgres_operational import PostgresOperationalDatabase, _identifier
from .semantic_human_calibration import (
    HumanLabelReason,
    SemanticAnnotationManifest,
    SemanticHumanAdjudication,
    SemanticReviewerLabel,
    SemanticReviewerPacket,
    SemanticReviewerTask,
    resolve_human_semantic_labels,
)
from .semantic_review_collection import (
    SemanticReviewAssignmentRecord,
    semantic_reviewer_ref_sha256,
)


_SEMANTIC_REVIEW_SCHEMA_VERSION = "semantic-review-collection-v1"
_TASK_BINDING_CONSTRAINT = "semantic_review_task_packet_binding_v1"
_ASSIGNMENT_TASK_FK = "semantic_review_assignment_task_fkey_v1"
_ASSIGNMENT_SHAPE_CONSTRAINT = "semantic_review_assignment_shape_v1"


class PostgresSemanticReviewStore:
    """Persistent blind two-reviewer + third-adjudicator semantic-label custody."""

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
                    CREATE TABLE IF NOT EXISTS "{schema}".semantic_review_tasks (
                        organization_id TEXT NOT NULL,
                        packet_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        purpose TEXT NOT NULL CHECK (purpose = 'HELD_OUT_CALIBRATION'),
                        source_split TEXT NOT NULL CHECK (source_split = 'VALIDATION'),
                        group_id TEXT NOT NULL,
                        rubric_sha256 TEXT NOT NULL CHECK (length(rubric_sha256) = 64),
                        frozen_split_sha256 TEXT NOT NULL CHECK (length(frozen_split_sha256) = 64),
                        display_order INTEGER NOT NULL CHECK (display_order >= 0),
                        task_payload JSONB NOT NULL,
                        active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (organization_id, task_id),
                        UNIQUE (organization_id, packet_id, display_order),
                        CONSTRAINT {_TASK_BINDING_CONSTRAINT}
                            UNIQUE (organization_id, packet_id, task_id)
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema}".semantic_review_assignments (
                        assignment_id TEXT PRIMARY KEY,
                        organization_id TEXT NOT NULL,
                        packet_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        phase TEXT NOT NULL CHECK (phase IN ('REVIEW','ADJUDICATION')),
                        reviewer_slot TEXT CHECK (reviewer_slot IN ('A','B')),
                        user_id TEXT NOT NULL,
                        reviewer_ref_sha256 TEXT NOT NULL CHECK (length(reviewer_ref_sha256) = 64),
                        state TEXT NOT NULL CHECK (state IN ('ACTIVE','COMPLETED','WITHDRAWN')),
                        score INTEGER CHECK (score IN (0,1,2)),
                        reason_codes JSONB,
                        started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        finished_at TIMESTAMPTZ,
                        CONSTRAINT {_ASSIGNMENT_TASK_FK}
                            FOREIGN KEY (organization_id, packet_id, task_id)
                            REFERENCES "{schema}".semantic_review_tasks(
                                organization_id, packet_id, task_id
                            ) ON DELETE RESTRICT,
                        CONSTRAINT {_ASSIGNMENT_SHAPE_CONSTRAINT} CHECK (
                            (
                                phase = 'REVIEW' AND reviewer_slot IN ('A','B')
                                OR phase = 'ADJUDICATION' AND reviewer_slot IS NULL
                            )
                            AND (
                                state = 'ACTIVE'
                                AND finished_at IS NULL
                                AND score IS NULL
                                AND reason_codes IS NULL
                                OR state = 'COMPLETED'
                                AND finished_at IS NOT NULL
                                AND score IS NOT NULL
                                AND reason_codes IS NOT NULL
                                OR state = 'WITHDRAWN'
                                AND finished_at IS NOT NULL
                                AND score IS NULL
                                AND reason_codes IS NULL
                            )
                        )
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS semantic_review_one_active_per_user_v1
                    ON "{schema}".semantic_review_assignments(organization_id, user_id)
                    WHERE state = 'ACTIVE'
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS semantic_review_one_active_slot_v1
                    ON "{schema}".semantic_review_assignments(organization_id, task_id, reviewer_slot)
                    WHERE phase = 'REVIEW' AND state = 'ACTIVE'
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS semantic_review_one_completed_slot_v1
                    ON "{schema}".semantic_review_assignments(organization_id, task_id, reviewer_slot)
                    WHERE phase = 'REVIEW' AND state = 'COMPLETED'
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS semantic_review_one_active_adjudication_v1
                    ON "{schema}".semantic_review_assignments(organization_id, task_id)
                    WHERE phase = 'ADJUDICATION' AND state = 'ACTIVE'
                    """
                )
                connection.execute(
                    f"""
                    CREATE UNIQUE INDEX IF NOT EXISTS semantic_review_one_completed_adjudication_v1
                    ON "{schema}".semantic_review_assignments(organization_id, task_id)
                    WHERE phase = 'ADJUDICATION' AND state = 'COMPLETED'
                    """
                )
                connection.execute(
                    f'ALTER TABLE "{schema}".semantic_review_tasks ENABLE ROW LEVEL SECURITY'
                )
                connection.execute(
                    f'ALTER TABLE "{schema}".semantic_review_assignments ENABLE ROW LEVEL SECURITY'
                )
                for table in ("semantic_review_tasks", "semantic_review_assignments"):
                    connection.execute(f'DROP POLICY IF EXISTS tenant_select ON "{schema}".{table}')
                    connection.execute(
                        f"""
                        CREATE POLICY tenant_select ON "{schema}".{table}
                        FOR SELECT
                        USING (organization_id = current_setting('academy.organization_id', true))
                        """
                    )
                connection.execute(
                    f"""
                    INSERT INTO "{schema}".operational_meta(key, value)
                    VALUES ('semantic_review_collection_schema_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (_SEMANTIC_REVIEW_SCHEMA_VERSION,),
                )

        with self.database.scoped_pool.connection() as scoped_connection:
            scoped_role = str(scoped_connection.execute("SELECT current_user").fetchone()[0])
        role = _identifier(scoped_role, label="scoped role")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"')
                for table in ("semantic_review_tasks", "semantic_review_assignments"):
                    connection.execute(f'GRANT SELECT ON "{schema}".{table} TO "{role}"')

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                version = connection.execute(
                    f"""
                    SELECT value FROM "{self.schema}".operational_meta
                    WHERE key = 'semantic_review_collection_schema_version'
                    """
                ).fetchone()
                constraints = connection.execute(
                    """
                    SELECT c.conname, c.convalidated
                    FROM pg_constraint c
                    JOIN pg_class t ON t.oid = c.conrelid
                    JOIN pg_namespace n ON n.oid = t.relnamespace
                    WHERE n.nspname = %s
                      AND c.conname IN (%s, %s, %s)
                    """,
                    (
                        self.schema,
                        _TASK_BINDING_CONSTRAINT,
                        _ASSIGNMENT_TASK_FK,
                        _ASSIGNMENT_SHAPE_CONSTRAINT,
                    ),
                ).fetchall()
            validated = {str(row[0]) for row in constraints if bool(row[1])}
            return (
                version is not None
                and str(version[0]) == _SEMANTIC_REVIEW_SCHEMA_VERSION
                and {
                    _TASK_BINDING_CONSTRAINT,
                    _ASSIGNMENT_TASK_FK,
                    _ASSIGNMENT_SHAPE_CONSTRAINT,
                }.issubset(validated)
            )
        except Exception:
            return False

    def register_packet(
        self,
        *,
        organization_id: str,
        packet: SemanticReviewerPacket,
        manifest: SemanticAnnotationManifest,
    ) -> None:
        if not organization_id:
            raise ValueError("organization_id must be non-empty")
        packet = SemanticReviewerPacket.model_validate(packet.model_dump(mode="json"))
        manifest = SemanticAnnotationManifest.model_validate(manifest.model_dump(mode="json"))
        if packet.purpose != "HELD_OUT_CALIBRATION" or manifest.purpose != "HELD_OUT_CALIBRATION":
            raise ValueError("semantic_review_store_requires_held_out_calibration")
        if manifest.source_split != "VALIDATION":
            raise ValueError("semantic_review_store_requires_validation_split")
        # Reuse the canonical resolver's packet/manifest binding checks without fabricating labels.
        resolve_human_semantic_labels(packet=packet, manifest=manifest, labels=())
        private_entries = {entry.task_id: entry for entry in manifest.entries}

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                for display_order, task in enumerate(packet.tasks):
                    entry = private_entries[task.task_id]
                    payload = json.dumps(
                        task.model_dump(mode="json"),
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    inserted = connection.execute(
                        f"""
                        INSERT INTO "{self.schema}".semantic_review_tasks(
                            organization_id, packet_id, task_id, purpose, source_split,
                            group_id, rubric_sha256, frozen_split_sha256,
                            display_order, task_payload, active
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,TRUE)
                        ON CONFLICT (organization_id, task_id) DO NOTHING
                        RETURNING task_id
                        """,
                        (
                            organization_id,
                            packet.packet_id,
                            task.task_id,
                            packet.purpose,
                            manifest.source_split,
                            entry.group_id,
                            packet.rubric_sha256,
                            manifest.frozen_split_sha256,
                            display_order,
                            payload,
                        ),
                    ).fetchone()
                    if inserted is not None:
                        continue
                    existing = connection.execute(
                        f"""
                        SELECT packet_id, purpose, source_split, group_id, rubric_sha256,
                               frozen_split_sha256, display_order, task_payload
                        FROM "{self.schema}".semantic_review_tasks
                        WHERE organization_id = %s AND task_id = %s
                        """,
                        (organization_id, task.task_id),
                    ).fetchone()
                    if existing is None or (
                        str(existing[0]) != packet.packet_id
                        or str(existing[1]) != packet.purpose
                        or str(existing[2]) != manifest.source_split
                        or str(existing[3]) != entry.group_id
                        or str(existing[4]) != packet.rubric_sha256
                        or str(existing[5]) != manifest.frozen_split_sha256
                        or int(existing[6]) != display_order
                        or existing[7] != task.model_dump(mode="json")
                    ):
                        raise RuntimeError("semantic_review_registration_conflict")

    @staticmethod
    def _record(row: object | None) -> SemanticReviewAssignmentRecord | None:
        if row is None:
            return None
        values = tuple(row)  # type: ignore[arg-type]
        task_payload = values[7]
        if isinstance(task_payload, str):
            task_payload = json.loads(task_payload)
        return SemanticReviewAssignmentRecord(
            assignment_id=str(values[0]),
            organization_id=str(values[1]),
            packet_id=str(values[2]),
            task=SemanticReviewerTask.model_validate(task_payload),
            phase=str(values[4]),  # type: ignore[arg-type]
            reviewer_slot=None if values[5] is None else str(values[5]),  # type: ignore[arg-type]
            user_id=str(values[6]),
            reviewer_ref_sha256=str(values[8]),
        )

    def get_active_for_user(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> SemanticReviewAssignmentRecord | None:
        with self.database.scoped_connection(organization_id) as connection:
            row = connection.execute(
                f"""
                SELECT a.assignment_id, a.organization_id, a.packet_id, a.task_id,
                       a.phase, a.reviewer_slot, a.user_id, t.task_payload,
                       a.reviewer_ref_sha256
                FROM "{self.schema}".semantic_review_assignments AS a
                JOIN "{self.schema}".semantic_review_tasks AS t
                  ON t.organization_id = a.organization_id AND t.task_id = a.task_id
                WHERE a.organization_id = %s AND a.user_id = %s AND a.state = 'ACTIVE'
                """,
                (organization_id, user_id),
            ).fetchone()
        return self._record(row)

    def _select_review_task(self, connection, *, organization_id: str, user_id: str):
        return connection.execute(
            f"""
            SELECT t.packet_id, t.task_id, t.task_payload
            FROM "{self.schema}".semantic_review_tasks AS t
            WHERE t.organization_id = %s
              AND t.active = TRUE
              AND NOT EXISTS (
                  SELECT 1 FROM "{self.schema}".semantic_review_assignments exposure
                  WHERE exposure.organization_id = t.organization_id
                    AND exposure.task_id = t.task_id
                    AND exposure.user_id = %s
              )
              AND (
                  NOT EXISTS (
                      SELECT 1 FROM "{self.schema}".semantic_review_assignments a
                      WHERE a.organization_id = t.organization_id AND a.task_id = t.task_id
                        AND a.phase = 'REVIEW' AND a.reviewer_slot = 'A'
                        AND a.state IN ('ACTIVE','COMPLETED')
                  )
                  OR NOT EXISTS (
                      SELECT 1 FROM "{self.schema}".semantic_review_assignments b
                      WHERE b.organization_id = t.organization_id AND b.task_id = t.task_id
                        AND b.phase = 'REVIEW' AND b.reviewer_slot = 'B'
                        AND b.state IN ('ACTIVE','COMPLETED')
                  )
              )
            ORDER BY t.created_at, t.packet_id, t.display_order
            FOR UPDATE OF t SKIP LOCKED
            LIMIT 1
            """,
            (organization_id, user_id),
        ).fetchone()

    def _select_adjudication_task(self, connection, *, organization_id: str, user_id: str):
        return connection.execute(
            f"""
            SELECT t.packet_id, t.task_id, t.task_payload
            FROM "{self.schema}".semantic_review_tasks AS t
            JOIN "{self.schema}".semantic_review_assignments a
              ON a.organization_id = t.organization_id AND a.task_id = t.task_id
             AND a.phase = 'REVIEW' AND a.reviewer_slot = 'A' AND a.state = 'COMPLETED'
            JOIN "{self.schema}".semantic_review_assignments b
              ON b.organization_id = t.organization_id AND b.task_id = t.task_id
             AND b.phase = 'REVIEW' AND b.reviewer_slot = 'B' AND b.state = 'COMPLETED'
            WHERE t.organization_id = %s
              AND t.active = TRUE
              AND a.score <> b.score
              AND NOT EXISTS (
                  SELECT 1 FROM "{self.schema}".semantic_review_assignments exposure
                  WHERE exposure.organization_id = t.organization_id
                    AND exposure.task_id = t.task_id
                    AND exposure.user_id = %s
              )
              AND NOT EXISTS (
                  SELECT 1 FROM "{self.schema}".semantic_review_assignments adjudication
                  WHERE adjudication.organization_id = t.organization_id
                    AND adjudication.task_id = t.task_id
                    AND adjudication.phase = 'ADJUDICATION'
                    AND adjudication.state IN ('ACTIVE','COMPLETED')
              )
            ORDER BY t.created_at, t.packet_id, t.display_order
            FOR UPDATE OF t SKIP LOCKED
            LIMIT 1
            """,
            (organization_id, user_id),
        ).fetchone()

    def assign_next(
        self,
        *,
        organization_id: str,
        user_id: str,
        principal_ref_sha256: str,
    ) -> SemanticReviewAssignmentRecord | None:
        if not organization_id or not user_id or not principal_ref_sha256:
            raise ValueError("semantic_review_assignment_principal_fields_must_be_nonempty")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                lock_key = json.dumps(
                    ["semantic-review-principal-v1", organization_id, user_id],
                    ensure_ascii=True,
                    separators=(",", ":"),
                )
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (lock_key,),
                )
                existing = connection.execute(
                    f"""
                    SELECT a.assignment_id, a.organization_id, a.packet_id, a.task_id,
                           a.phase, a.reviewer_slot, a.user_id, t.task_payload,
                           a.reviewer_ref_sha256
                    FROM "{self.schema}".semantic_review_assignments a
                    JOIN "{self.schema}".semantic_review_tasks t
                      ON t.organization_id = a.organization_id AND t.task_id = a.task_id
                    WHERE a.organization_id = %s AND a.user_id = %s AND a.state = 'ACTIVE'
                    FOR UPDATE OF a
                    """,
                    (organization_id, user_id),
                ).fetchone()
                if existing is not None:
                    return self._record(existing)

                task = self._select_review_task(
                    connection,
                    organization_id=organization_id,
                    user_id=user_id,
                )
                phase = "REVIEW"
                slot: str | None = None
                if task is not None:
                    slots = {
                        str(row[0])
                        for row in connection.execute(
                            f"""
                            SELECT reviewer_slot
                            FROM "{self.schema}".semantic_review_assignments
                            WHERE organization_id = %s AND task_id = %s
                              AND phase = 'REVIEW' AND state IN ('ACTIVE','COMPLETED')
                            """,
                            (organization_id, str(task[1])),
                        ).fetchall()
                    }
                    slot = "A" if "A" not in slots else "B" if "B" not in slots else None
                    if slot is None:
                        raise RuntimeError("semantic_review_slot_allocation_conflict")
                else:
                    task = self._select_adjudication_task(
                        connection,
                        organization_id=organization_id,
                        user_id=user_id,
                    )
                    phase = "ADJUDICATION"
                if task is None:
                    return None

                packet_id = str(task[0])
                task_id = str(task[1])
                task_payload = task[2]
                if isinstance(task_payload, str):
                    task_payload = json.loads(task_payload)
                assignment_id = f"semassign_{uuid4().hex[:24]}"
                reviewer_ref = semantic_reviewer_ref_sha256(
                    packet_id=packet_id,
                    organization_id=organization_id,
                    principal_ref_sha256=principal_ref_sha256,
                )
                connection.execute(
                    f"""
                    INSERT INTO "{self.schema}".semantic_review_assignments(
                        assignment_id, organization_id, packet_id, task_id, phase,
                        reviewer_slot, user_id, reviewer_ref_sha256, state
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE')
                    """,
                    (
                        assignment_id,
                        organization_id,
                        packet_id,
                        task_id,
                        phase,
                        slot,
                        user_id,
                        reviewer_ref,
                    ),
                )
                return SemanticReviewAssignmentRecord(
                    assignment_id=assignment_id,
                    organization_id=organization_id,
                    packet_id=packet_id,
                    task=SemanticReviewerTask.model_validate(task_payload),
                    phase=phase,  # type: ignore[arg-type]
                    reviewer_slot=slot,  # type: ignore[arg-type]
                    user_id=user_id,
                    reviewer_ref_sha256=reviewer_ref,
                )

    def complete(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        score: int,
        reason_codes: tuple[HumanLabelReason, ...],
    ) -> SemanticReviewAssignmentRecord:
        if score not in (0, 1, 2):
            raise ValueError("semantic_review_score_out_of_range")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    SELECT a.assignment_id, a.organization_id, a.packet_id, a.task_id,
                           a.phase, a.reviewer_slot, a.user_id, t.task_payload,
                           a.reviewer_ref_sha256, a.state
                    FROM "{self.schema}".semantic_review_assignments a
                    JOIN "{self.schema}".semantic_review_tasks t
                      ON t.organization_id = a.organization_id AND t.task_id = a.task_id
                    WHERE a.assignment_id = %s AND a.organization_id = %s AND a.user_id = %s
                    FOR UPDATE OF a
                    """,
                    (assignment_id, organization_id, user_id),
                ).fetchone()
                if row is None:
                    raise KeyError(assignment_id)
                if str(row[9]) != "ACTIVE":
                    raise RuntimeError("semantic_review_assignment_not_active")
                record = self._record(row[:9])
                if record is None:  # pragma: no cover - row was just proven present
                    raise RuntimeError("semantic_review_assignment_decode_failed")
                # Constructing the canonical label validates score/reason semantics for REVIEW.
                if record.phase == "REVIEW":
                    SemanticReviewerLabel(
                        packet_id=record.packet_id,
                        task_id=record.task.task_id,
                        rubric_sha256=record.task.output_sha256[:0] + self._task_rubric_hash(
                            connection, organization_id, record.task.task_id
                        ),
                        reviewer_slot=record.reviewer_slot,  # type: ignore[arg-type]
                        reviewer_ref_sha256=record.reviewer_ref_sha256,
                        score=score,  # type: ignore[arg-type]
                        reason_codes=reason_codes,
                    )
                reason_payload = json.dumps(list(reason_codes), separators=(",", ":"))
                connection.execute(
                    f"""
                    UPDATE "{self.schema}".semantic_review_assignments
                    SET state = 'COMPLETED', score = %s, reason_codes = %s::jsonb,
                        finished_at = CURRENT_TIMESTAMP
                    WHERE assignment_id = %s
                    """,
                    (score, reason_payload, assignment_id),
                )
                return record

    def _task_rubric_hash(self, connection, organization_id: str, task_id: str) -> str:
        row = connection.execute(
            f"""
            SELECT rubric_sha256 FROM "{self.schema}".semantic_review_tasks
            WHERE organization_id = %s AND task_id = %s
            """,
            (organization_id, task_id),
        ).fetchone()
        if row is None:
            raise RuntimeError("semantic_review_task_binding_missing")
        return str(row[0])

    def withdraw(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
    ) -> SemanticReviewAssignmentRecord:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    SELECT a.assignment_id, a.organization_id, a.packet_id, a.task_id,
                           a.phase, a.reviewer_slot, a.user_id, t.task_payload,
                           a.reviewer_ref_sha256, a.state
                    FROM "{self.schema}".semantic_review_assignments a
                    JOIN "{self.schema}".semantic_review_tasks t
                      ON t.organization_id = a.organization_id AND t.task_id = a.task_id
                    WHERE a.assignment_id = %s AND a.organization_id = %s AND a.user_id = %s
                    FOR UPDATE OF a
                    """,
                    (assignment_id, organization_id, user_id),
                ).fetchone()
                if row is None:
                    raise KeyError(assignment_id)
                if str(row[9]) != "ACTIVE":
                    raise RuntimeError("semantic_review_assignment_not_active")
                record = self._record(row[:9])
                if record is None:  # pragma: no cover
                    raise RuntimeError("semantic_review_assignment_decode_failed")
                connection.execute(
                    f"""
                    UPDATE "{self.schema}".semantic_review_assignments
                    SET state = 'WITHDRAWN', finished_at = CURRENT_TIMESTAMP
                    WHERE assignment_id = %s
                    """,
                    (assignment_id,),
                )
                return record

    def export_resolution_inputs(
        self,
        *,
        organization_id: str,
        packet_id: str,
    ) -> tuple[tuple[SemanticReviewerLabel, ...], tuple[SemanticHumanAdjudication, ...]]:
        """Trusted evaluator export. Raw user IDs and withdrawn/incomplete rows never leave custody."""

        with self.database.internal_pool.connection() as connection:
            packet_meta = connection.execute(
                f"""
                SELECT DISTINCT rubric_sha256
                FROM "{self.schema}".semantic_review_tasks
                WHERE organization_id = %s AND packet_id = %s
                """,
                (organization_id, packet_id),
            ).fetchall()
            if not packet_meta:
                raise KeyError(packet_id)
            rubric_hashes = {str(row[0]) for row in packet_meta}
            if len(rubric_hashes) != 1:
                raise RuntimeError("semantic_review_packet_rubric_corruption")
            rubric_hash = next(iter(rubric_hashes))
            rows = connection.execute(
                f"""
                SELECT task_id, phase, reviewer_slot, reviewer_ref_sha256, score, reason_codes
                FROM "{self.schema}".semantic_review_assignments
                WHERE organization_id = %s AND packet_id = %s AND state = 'COMPLETED'
                ORDER BY task_id, phase, reviewer_slot NULLS LAST
                """,
                (organization_id, packet_id),
            ).fetchall()

        labels: list[SemanticReviewerLabel] = []
        adjudications: list[SemanticHumanAdjudication] = []
        for row in rows:
            task_id = str(row[0])
            phase = str(row[1])
            reviewer_ref = str(row[3])
            score = int(row[4])
            reasons_raw = row[5]
            if isinstance(reasons_raw, str):
                reasons_raw = json.loads(reasons_raw)
            reasons = tuple(str(item) for item in (reasons_raw or ()))
            if phase == "REVIEW":
                labels.append(
                    SemanticReviewerLabel(
                        packet_id=packet_id,
                        task_id=task_id,
                        rubric_sha256=rubric_hash,
                        reviewer_slot=str(row[2]),  # type: ignore[arg-type]
                        reviewer_ref_sha256=reviewer_ref,
                        score=score,  # type: ignore[arg-type]
                        reason_codes=reasons,  # type: ignore[arg-type]
                    )
                )
            elif phase == "ADJUDICATION":
                adjudications.append(
                    SemanticHumanAdjudication(
                        packet_id=packet_id,
                        task_id=task_id,
                        rubric_sha256=rubric_hash,
                        adjudicator_ref_sha256=reviewer_ref,
                        score=score,  # type: ignore[arg-type]
                    )
                )
            else:
                raise RuntimeError("semantic_review_assignment_phase_corruption")
        return tuple(labels), tuple(adjudications)
