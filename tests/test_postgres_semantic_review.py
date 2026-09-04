from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.postgres_semantic_review import PostgresSemanticReviewStore
from academy_tractian.semantic_evaluation import semantic_rubric_v1
from academy_tractian.semantic_human_calibration import (
    SemanticAnnotationManifest,
    SemanticAnnotationManifestEntry,
    SemanticReviewerPacket,
    SemanticReviewerTask,
    resolve_human_semantic_labels,
)


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_sem_review_{suffix}"
        self.role = f"academy_sem_review_scoped_{suffix}"
        self.password = "scoped-test-password"
        with connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(self.role), sql.Literal(self.password)
                )
            )
        parsed = urlsplit(admin_dsn)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 5432
        database = parsed.path or "/postgres"
        self.scoped_dsn = urlunsplit(
            (
                parsed.scheme or "postgresql",
                f"{self.role}:{self.password}@{host}:{port}",
                database,
                "",
                "",
            )
        )

    def cleanup(self) -> None:
        with connect(self.admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema))
            )
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role)))


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _database(fixture: _PgFixture) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize=True,
    )


def _packet_manifest(seed: str = "1") -> tuple[SemanticReviewerPacket, SemanticAnnotationManifest]:
    rubric = semantic_rubric_v1()
    task_id = "sem_" + seed * 24
    packet_id = "sempkt_" + seed * 24
    output_hash = ("2" if seed != "2" else "3") * 64
    context_hash = ("4" if seed != "2" else "5") * 64
    task = SemanticReviewerTask(
        task_id=task_id,
        scenario_id=f"VAL-{seed}",
        output_sha256=output_hash,
        context_sha256=context_hash,
        response_mode="complete",
        dimension="operational_usefulness",
        terminal_decision="ORIENT",
        terminal_message="The sanitized evidence supports the stated operational next step.",
        safe_evidence_context=("Sanitized evidence only.",),
        criterion_description="Judge operational usefulness.",
        score_0_anchor="Incorrect or unusable.",
        score_1_anchor="Partially useful.",
        score_2_anchor="Correct and actionable.",
    )
    packet = SemanticReviewerPacket(
        packet_id=packet_id,
        purpose="HELD_OUT_CALIBRATION",
        rubric_id=rubric.rubric_id,
        rubric_sha256=rubric.rubric_sha256,
        deterministic_shuffle_seed=1,
        source_count=1,
        task_count=1,
        tasks=(task,),
    )
    manifest = SemanticAnnotationManifest(
        packet_id=packet_id,
        purpose="HELD_OUT_CALIBRATION",
        source_split="VALIDATION",
        frozen_split_schema_version="benchmark-split-v1",
        frozen_split_sha256="6" * 64,
        group_ids=(f"validation-group-{seed}",),
        entries=(
            SemanticAnnotationManifestEntry(
                task_id=task_id,
                scenario_id=task.scenario_id,
                group_id=f"validation-group-{seed}",
                source_split="VALIDATION",
                output_sha256=output_hash,
                context_sha256=context_hash,
                response_mode=task.response_mode,
                dimension=task.dimension,
            ),
        ),
    )
    return packet, manifest


def _marker(user: str) -> str:
    return (user.encode("utf-8").hex() + "0" * 64)[:64]


def test_two_independent_reviews_then_distinct_blind_adjudication_export_cleanly(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        store = PostgresSemanticReviewStore(database, initialize=True)
        assert store.ready() is True
        packet, manifest = _packet_manifest()
        store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)
        store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)

        first = store.assign_next(
            organization_id="org-a", user_id="reviewer-a", principal_ref_sha256=_marker("a")
        )
        assert first is not None and first.phase == "REVIEW" and first.reviewer_slot == "A"
        retry = store.assign_next(
            organization_id="org-a", user_id="reviewer-a", principal_ref_sha256=_marker("a")
        )
        assert retry is not None and retry.assignment_id == first.assignment_id
        store.complete(
            assignment_id=first.assignment_id,
            organization_id="org-a",
            user_id="reviewer-a",
            score=2,
            reason_codes=("NO_MATERIAL_DEFECT",),
        )
        assert store.assign_next(
            organization_id="org-a", user_id="reviewer-a", principal_ref_sha256=_marker("a")
        ) is None

        second = store.assign_next(
            organization_id="org-a", user_id="reviewer-b", principal_ref_sha256=_marker("b")
        )
        assert second is not None and second.phase == "REVIEW" and second.reviewer_slot == "B"
        store.complete(
            assignment_id=second.assignment_id,
            organization_id="org-a",
            user_id="reviewer-b",
            score=1,
            reason_codes=("MISSING_NEXT_STEP",),
        )
        # Prior reviewers can never adjudicate their own disagreement.
        assert store.assign_next(
            organization_id="org-a", user_id="reviewer-b", principal_ref_sha256=_marker("b")
        ) is None

        adjudication = store.assign_next(
            organization_id="org-a", user_id="reviewer-c", principal_ref_sha256=_marker("c")
        )
        assert adjudication is not None
        assert adjudication.phase == "ADJUDICATION"
        assert adjudication.reviewer_slot is None
        store.complete(
            assignment_id=adjudication.assignment_id,
            organization_id="org-a",
            user_id="reviewer-c",
            score=1,
            reason_codes=("MISSING_NEXT_STEP",),
        )

        labels, adjudications = store.export_resolution_inputs(
            organization_id="org-a", packet_id=packet.packet_id
        )
        assert [label.reviewer_slot for label in labels] == ["A", "B"]
        assert len({label.reviewer_ref_sha256 for label in labels}) == 2
        assert len(adjudications) == 1
        assert adjudications[0].adjudicator_ref_sha256 not in {
            label.reviewer_ref_sha256 for label in labels
        }

        report = resolve_human_semantic_labels(
            packet=packet,
            manifest=manifest,
            labels=labels,
            adjudications=adjudications,
        )
        assert report.calibration_ready is True
        assert report.agreed_count == 0
        assert report.adjudicated_count == 1
        assert report.human_references[0].score == 1
    finally:
        database.close()


def test_withdrawal_contains_no_label_and_exposure_prevents_same_user_reassignment(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        store = PostgresSemanticReviewStore(database, initialize=True)
        packet, manifest = _packet_manifest("2")
        store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)
        assigned = store.assign_next(
            organization_id="org-a", user_id="reviewer-a", principal_ref_sha256=_marker("a")
        )
        assert assigned is not None
        store.withdraw(
            assignment_id=assigned.assignment_id,
            organization_id="org-a",
            user_id="reviewer-a",
        )
        assert store.assign_next(
            organization_id="org-a", user_id="reviewer-a", principal_ref_sha256=_marker("a")
        ) is None
        replacement = store.assign_next(
            organization_id="org-a", user_id="reviewer-b", principal_ref_sha256=_marker("b")
        )
        assert replacement is not None and replacement.reviewer_slot == "A"
        labels, adjudications = store.export_resolution_inputs(
            organization_id="org-a", packet_id=packet.packet_id
        )
        assert labels == ()
        assert adjudications == ()
        with database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT state, score, reason_codes
                FROM "{database.schema}".semantic_review_assignments
                WHERE assignment_id = %s
                """,
                (assigned.assignment_id,),
            ).fetchone()
        assert row == ("WITHDRAWN", None, None)
    finally:
        database.close()


def test_same_principal_concurrent_assignment_converges_and_tenant_isolation_holds(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        store = PostgresSemanticReviewStore(database, initialize=True)
        packet, manifest = _packet_manifest()
        store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)

        def assign():
            return store.assign_next(
                organization_id="org-a",
                user_id="reviewer-a",
                principal_ref_sha256=_marker("a"),
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: assign(), range(2)))
        assert all(result is not None for result in results)
        assert len({result.assignment_id for result in results if result is not None}) == 1
        assert store.assign_next(
            organization_id="org-b",
            user_id="reviewer-a",
            principal_ref_sha256=_marker("a"),
        ) is None
        with database.scoped_connection("org-b") as connection:
            count = connection.execute(
                f'SELECT count(*) FROM "{database.schema}".semantic_review_tasks'
            ).fetchone()
        assert count is not None and int(count[0]) == 0
    finally:
        database.close()
