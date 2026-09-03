from __future__ import annotations

import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from academy_tractian.operational_value_analysis import (
    OperationalValueAnalysisProtocol,
    analyze_operational_value,
)
from academy_tractian.operational_value_pilot import (
    OperationalPilotSource,
    build_operational_pilot_packet,
)
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.postgres_operational_value_analysis import (
    PostgresOperationalValueAnalysisStore,
)
from academy_tractian.postgres_operational_value_v5 import PostgresOperationalPilotStoreV5


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_value_analysis_{suffix}"
        self.role = f"academy_value_analysis_scoped_{suffix}"
        self.password = "scoped-test-password"
        with connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(self.role),
                    sql.Literal(self.password),
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


def _split_manifest() -> dict[str, object]:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {"group_id": "asset_A", "scenarios": ["VALUE-01"]},
                    {"group_id": "asset_B", "scenarios": ["VALUE-02"]},
                ]
            },
            "VALIDATION": {
                "groups": [{"group_id": "asset_V", "scenarios": ["VALUE-V"]}]
            },
            "LOCKED_TEST": {
                "groups": [{"group_id": "asset_L", "scenarios": ["VALUE-L"]}]
            },
        },
    }


def _packet():
    sources = (
        OperationalPilotSource(
            scenario_id="VALUE-01",
            case_id="VALUE-TICKET-01",
            ticket_request="Investigate ticket one.",
            agent_terminal_decision="ORIENT",
            agent_terminal_message="Evidence supports orientation.",
            safe_evidence_context=("Evidence A",),
            agent_runtime_seconds=2.0,
        ),
        OperationalPilotSource(
            scenario_id="VALUE-02",
            case_id="VALUE-TICKET-02",
            ticket_request="Investigate ticket two.",
            agent_terminal_decision="ORIENT",
            agent_terminal_message="Evidence supports orientation.",
            safe_evidence_context=("Evidence B",),
            agent_runtime_seconds=2.0,
        ),
    )
    return build_operational_pilot_packet(
        sources=sources,
        frozen_split_payload=_split_manifest(),
        protocol_id="postgres-value-analysis-test-v1",
        deterministic_shuffle_seed=71,
        minimum_distinct_groups=2,
    )


def _database(fixture: _PgFixture) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize=True,
    )


def _protocol() -> OperationalValueAnalysisProtocol:
    return OperationalValueAnalysisProtocol(
        status="FROZEN",
        protocol_id="postgres-value-analysis-v1",
        minimum_complete_pairs=2,
        confidence_level=0.95,
        bootstrap_iterations=3000,
        bootstrap_seed=31,
    )


def test_postgres_freeze_refuses_active_trial_then_yields_stable_closed_snapshot(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        pilot_store = PostgresOperationalPilotStoreV5(database, initialize=True)
        analysis_store = PostgresOperationalValueAnalysisStore(database)
        packet, manifest = _packet()
        pilot_store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)

        pre = analysis_store.snapshot(organization_id="org-a", packet_id=packet.packet_id)
        assert pre.collection_closed is False
        assert len(pre.task_slots) == 4
        assert pre.valid_measurements == ()

        active = pilot_store.assign_next(
            organization_id="org-a",
            user_id="interrupted-user",
            operator_ref_sha256="1" * 64,
            host_session_id="ovhost_" + "2" * 24,
        )
        assert active is not None
        with pytest.raises(RuntimeError, match="close_blocked_active_assignments"):
            analysis_store.close_packet(organization_id="org-a", packet_id=packet.packet_id)
        still_open = analysis_store.snapshot(organization_id="org-a", packet_id=packet.packet_id)
        assert still_open.collection_closed is False
        assert still_open.active_assignment_count == 1

        pilot_store.terminate_active(
            assignment_id=active.assignment_id,
            organization_id="org-a",
            user_id="interrupted-user",
            terminal_status="INTERRUPTED",
        )

        completed_task_ids: set[str] = set()
        for index in range(10):
            assigned = pilot_store.assign_next(
                organization_id="org-a",
                user_id=f"valid-user-{index}",
                operator_ref_sha256=f"{index + 10:064x}",
                host_session_id="ovhost_" + f"{index + 20:024x}",
            )
            if assigned is None:
                break
            elapsed = 120.0 if assigned.task.condition == "MANUAL" else 60.0
            pilot_store.complete_valid(
                assignment_id=assigned.assignment_id,
                organization_id="org-a",
                user_id=f"valid-user-{index}",
                elapsed_seconds=elapsed,
                terminal_decision="ORIENT",
                conclusion_summary="Recorded valid operational conclusion.",
            )
            completed_task_ids.add(assigned.task.task_id)
        assert len(completed_task_ids) == 4

        open_complete = analysis_store.snapshot(
            organization_id="org-a",
            packet_id=packet.packet_id,
        )
        assert open_complete.collection_closed is False
        assert open_complete.invalid_trial_count == 1
        assert len(open_complete.valid_measurements) == 4

        assert analysis_store.close_packet(
            organization_id="org-a",
            packet_id=packet.packet_id,
        ) == 4
        closed = analysis_store.snapshot(organization_id="org-a", packet_id=packet.packet_id)
        closed_again = analysis_store.snapshot(organization_id="org-a", packet_id=packet.packet_id)
        assert closed.collection_closed is True
        assert closed.active_assignment_count == 0
        assert closed.snapshot_sha256 == closed_again.snapshot_sha256
        assert analysis_store.close_packet(
            organization_id="org-a",
            packet_id=packet.packet_id,
        ) == 0

        no_more = pilot_store.assign_next(
            organization_id="org-a",
            user_id="late-user",
            operator_ref_sha256="9" * 64,
            host_session_id="ovhost_" + "8" * 24,
        )
        assert no_more is None

        result = analyze_operational_value(snapshot=closed, protocol=_protocol())
        assert result.status == "POSITIVE_TIME_SIGNAL"
        assert result.complete_pair_count == 2
        assert result.incomplete_pair_count == 0
        assert result.engineer_minutes_saved_per_ticket == pytest.approx(1.0)
        assert result.business_claim_ready is False
    finally:
        database.close()


def test_postgres_analysis_unknown_packet_fails_closed(postgres_fixture: _PgFixture) -> None:
    database = _database(postgres_fixture)
    try:
        PostgresOperationalPilotStoreV5(database, initialize=True)
        analysis_store = PostgresOperationalValueAnalysisStore(database)
        missing = "ovpkt_" + "f" * 24
        with pytest.raises(KeyError):
            analysis_store.snapshot(organization_id="org-a", packet_id=missing)
        with pytest.raises(KeyError):
            analysis_store.close_packet(organization_id="org-a", packet_id=missing)
    finally:
        database.close()
