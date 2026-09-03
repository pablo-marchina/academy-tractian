from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from psycopg import connect, sql
from psycopg.errors import CheckViolation, ForeignKeyViolation

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.operational_value_collection import OPERATIONAL_VALUE_PARTICIPATE_PERMISSION
from academy_tractian.operational_value_pilot import (
    OperationalPilotSource,
    build_operational_pilot_packet,
)
from academy_tractian.postgres_product_api import create_postgres_action_capable_product_app
from academy_tractian.product_api import (
    DEFAULT_RUNTIME_PERMISSIONS,
    AuthenticatedRuntimeContext,
)
from academy_tractian.production_actions_v2 import ProductionActionPrincipal


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Provider-free product path is available.",
            },
        )


class RecordingTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        return TransportResponse(status_code=200, headers={}, body={})


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-1",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="analysis-1", company_id="company-1"),
        ),
    )


def _context(request: Request) -> AuthenticatedRuntimeContext:
    user = request.headers.get("x-test-user", "user-a")
    permissions = set(DEFAULT_RUNTIME_PERMISSIONS)
    if request.headers.get("x-no-pilot-permission") != "1":
        permissions.add(OPERATIONAL_VALUE_PARTICIPATE_PERMISSION)
    return AuthenticatedRuntimeContext(
        organization_id=request.headers.get("x-test-organization", "org-a"),
        identity_id=f"identity-{user}",
        user_id=user,
        permissions=frozenset(permissions),
    )


def _headers(user: str, org: str = "org-a") -> dict[str, str]:
    return {"x-test-user": user, "x-test-organization": org}


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_pilot_{suffix}"
        self.role = f"academy_pilot_scoped_{suffix}"
        self.password = "scoped-test-password"
        with connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(self.role),
                    sql.Literal(self.password),
                )
            )

        from urllib.parse import urlsplit, urlunsplit

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
                    {"group_id": "asset_G501", "scenarios": ["CEN-01"]},
                    {"group_id": "asset_C710", "scenarios": ["CEN-02"]},
                ]
            },
            "VALIDATION": {
                "groups": [{"group_id": "asset_B204", "scenarios": ["CEN-07"]}]
            },
            "LOCKED_TEST": {
                "groups": [{"group_id": "asset_V301", "scenarios": ["CEN-08"]}]
            },
        },
    }


def _packet():
    sources = [
        OperationalPilotSource(
            scenario_id="CEN-01",
            case_id="TKT-01",
            ticket_request="Investigate why asset G501 has no reliable diagnostic conclusion.",
            agent_terminal_decision="ESCALATE_HUMAN",
            agent_terminal_message="Evidence is incomplete and specialist review is required.",
            safe_evidence_context=("Recent measurements are incomplete.",),
            agent_runtime_seconds=4.0,
        ),
        OperationalPilotSource(
            scenario_id="CEN-02",
            case_id="TKT-02",
            ticket_request="Investigate why the latest analysis for asset C710 is still pending.",
            agent_terminal_decision="FINAL",
            agent_terminal_message="The analysis is still processing; wait before corrective action.",
            safe_evidence_context=("Analysis state is pending.",),
            agent_runtime_seconds=3.0,
        ),
    ]
    return build_operational_pilot_packet(
        sources=sources,
        frozen_split_payload=_split_manifest(),
        protocol_id="engineer-effort-dev-pilot-v1",
        deterministic_shuffle_seed=19,
        minimum_distinct_groups=2,
    )


def _app(tmp_path: Path, fixture: _PgFixture, *, initialize_schema: bool):
    return create_postgres_action_capable_product_app(
        db_path=tmp_path / "pilot-observability.duckdb",
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize_schema=initialize_schema,
        decision_source_factory=FinalSource,
        transport_factory=RecordingTransport,
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=False,
        heartbeat_interval_ms=250,
    )


def test_postgres_store_serializes_same_principal_assignment(
    tmp_path: Path,
    postgres_fixture: _PgFixture,
) -> None:
    packet, manifest = _packet()
    app = _app(tmp_path, postgres_fixture, initialize_schema=True)
    store = app.state.operational_value_collection_store
    store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)
    host_session_id = app.state.operational_value_timer_registry.host_session_id

    def assign():
        return store.assign_next(
            organization_id="org-a",
            user_id="same-user",
            operator_ref_sha256="f" * 64,
            host_session_id=host_session_id,
        )

    with TestClient(app):
        with ThreadPoolExecutor(max_workers=2) as executor:
            assignments = tuple(executor.map(lambda _: assign(), range(2)))

        assert all(assignment is not None for assignment in assignments)
        assert assignments[0] is not None and assignments[1] is not None
        assert assignments[0].assignment_id == assignments[1].assignment_id
        assert assignments[0].task.task_id == assignments[1].task.task_id


def test_postgres_rejects_structurally_invalid_valid_measurement(
    tmp_path: Path,
    postgres_fixture: _PgFixture,
) -> None:
    packet, manifest = _packet()
    app = _app(tmp_path, postgres_fixture, initialize_schema=True)
    store = app.state.operational_value_collection_store
    store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)
    task = packet.tasks[0]
    entry = next(item for item in manifest.entries if item.task_id == task.task_id)
    schema = postgres_fixture.schema

    with TestClient(app):
        with pytest.raises(CheckViolation):
            with app.state.postgres_operational_database.internal_pool.connection() as connection:
                with connection.transaction():
                    connection.execute(
                        f"""
                        INSERT INTO "{schema}".operational_pilot_assignments(
                            assignment_id, organization_id, packet_id, task_id, pair_id,
                            user_id, operator_ref_sha256, host_session_id, state,
                            finished_at, elapsed_seconds, terminal_decision, conclusion_summary
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, 'VALID',
                            CURRENT_TIMESTAMP, NULL, %s, %s
                        )
                        """,
                        (
                            "ova_" + "1" * 24,
                            "org-a",
                            packet.packet_id,
                            task.task_id,
                            entry.pair_id,
                            "constraint-user",
                            "2" * 64,
                            "ovhost_" + "3" * 24,
                            "FINAL",
                            "This row must fail because a valid measurement has no elapsed time.",
                        ),
                    )


def test_postgres_rejects_assignment_with_noncanonical_pair_binding(
    tmp_path: Path,
    postgres_fixture: _PgFixture,
) -> None:
    packet, manifest = _packet()
    app = _app(tmp_path, postgres_fixture, initialize_schema=True)
    store = app.state.operational_value_collection_store
    store.register_packet(organization_id="org-a", packet=packet, manifest=manifest)
    task = packet.tasks[0]
    schema = postgres_fixture.schema

    with TestClient(app):
        with pytest.raises(ForeignKeyViolation):
            with app.state.postgres_operational_database.internal_pool.connection() as connection:
                with connection.transaction():
                    connection.execute(
                        f"""
                        INSERT INTO "{schema}".operational_pilot_assignments(
                            assignment_id, organization_id, packet_id, task_id, pair_id,
                            user_id, operator_ref_sha256, host_session_id, state
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
                        """,
                        (
                            "ova_" + "4" * 24,
                            "org-a",
                            packet.packet_id,
                            task.task_id,
                            "ovpair_" + "5" * 24,
                            "pair-integrity-user",
                            "6" * 64,
                            "ovhost_" + "7" * 24,
                        ),
                    )


def test_postgres_collection_is_authenticated_server_timed_and_pair_safe(
    tmp_path: Path,
    postgres_fixture: _PgFixture,
) -> None:
    packet, manifest = _packet()
    app = _app(tmp_path, postgres_fixture, initialize_schema=True)
    app.state.operational_value_collection_store.register_packet(
        organization_id="org-a",
        packet=packet,
        manifest=manifest,
    )
    pair_by_task = {entry.task_id: entry.pair_id for entry in manifest.entries}

    with TestClient(app) as client:
        denied = client.post(
            "/api/operational-value/tasks/next",
            headers={**_headers("user-denied"), "x-no-pilot-permission": "1"},
        )
        assert denied.status_code == 403

        first_a = client.post(
            "/api/operational-value/tasks/next",
            headers=_headers("user-a"),
        )
        assert first_a.status_code == 200
        first_payload = first_a.json()
        first_task_a = first_payload["task"]["task_id"]
        first_assignment_a = first_payload["assignment_id"]

        first_b = client.post(
            "/api/operational-value/tasks/next",
            headers=_headers("user-b"),
        )
        assert first_b.status_code == 200
        assert first_b.json()["task"]["task_id"] != first_task_a

        assert (
            client.post(
                f"/api/operational-value/assignments/{first_assignment_a}/complete",
                headers=_headers("user-b"),
                json={"terminal_decision": "FINAL", "conclusion_summary": "Wrong owner."},
            ).status_code
            == 404
        )
        assert (
            client.post(
                f"/api/operational-value/assignments/{first_assignment_a}/complete",
                headers=_headers("user-a", "org-b"),
                json={"terminal_decision": "FINAL", "conclusion_summary": "Wrong tenant."},
            ).status_code
            == 404
        )
        assert (
            client.post(
                "/api/operational-value/tasks/next",
                headers=_headers("other-user", "org-b"),
            ).status_code
            == 404
        )

        completed_a = client.post(
            f"/api/operational-value/assignments/{first_assignment_a}/complete",
            headers=_headers("user-a"),
            json={
                "terminal_decision": "FINAL",
                "conclusion_summary": "The operational conclusion is recorded from the evidence.",
            },
        )
        assert completed_a.status_code == 200
        assert completed_a.json()["elapsed_seconds"] > 0.0

        duplicate = client.post(
            f"/api/operational-value/assignments/{first_assignment_a}/complete",
            headers=_headers("user-a"),
            json={
                "terminal_decision": "FINAL",
                "conclusion_summary": "Duplicate submission must not be recorded.",
            },
        )
        assert duplicate.status_code == 404

        second_a = client.post(
            "/api/operational-value/tasks/next",
            headers=_headers("user-a"),
        )
        assert second_a.status_code == 200
        second_task_a = second_a.json()["task"]["task_id"]
        assert pair_by_task[second_task_a] != pair_by_task[first_task_a]

        completions = app.state.operational_value_collection_store.list_completions(
            organization_id="org-a",
            packet_id=packet.packet_id,
        )
        valid_for_first = [row for row in completions if row.task_id == first_task_a]
        assert len(valid_for_first) == 1
        assert valid_for_first[0].status == "VALID"
        assert valid_for_first[0].operator_ref_sha256 not in {"user-a", "identity-user-a"}


def test_postgres_collection_restart_invalidates_orphaned_monotonic_timer(
    tmp_path: Path,
    postgres_fixture: _PgFixture,
) -> None:
    packet, manifest = _packet()
    pair_by_task = {entry.task_id: entry.pair_id for entry in manifest.entries}
    first = _app(tmp_path, postgres_fixture, initialize_schema=True)
    first.state.operational_value_collection_store.register_packet(
        organization_id="org-a",
        packet=packet,
        manifest=manifest,
    )

    with TestClient(first) as client:
        assigned = client.post(
            "/api/operational-value/tasks/next",
            headers=_headers("restart-user"),
        )
        assert assigned.status_code == 200
        orphaned_assignment = assigned.json()["assignment_id"]
        orphaned_task = assigned.json()["task"]["task_id"]

    second = _app(tmp_path, postgres_fixture, initialize_schema=False)
    # Merely constructing/importing the replacement app is not enough to invalidate a human trial.
    assert second.state.operational_value_recovered_assignments == ()
    with TestClient(second) as client:
        stale_completion = client.post(
            f"/api/operational-value/assignments/{orphaned_assignment}/complete",
            headers=_headers("restart-user"),
            json={
                "terminal_decision": "FINAL",
                "conclusion_summary": "A restarted timer must fail closed.",
            },
        )
        assert stale_completion.status_code == 404
        assert orphaned_assignment in second.state.operational_value_recovered_assignments

        recovered = second.state.operational_value_collection_store.list_completions(
            organization_id="org-a",
            packet_id=packet.packet_id,
        )
        failed = [row for row in recovered if row.task_id == orphaned_task]
        assert len(failed) == 1
        assert failed[0].status == "TECHNICAL_FAILURE"
        assert failed[0].elapsed_seconds is None
        assert failed[0].invalid_reason == "host_timer_session_lost"

        same_user_replacement = client.post(
            "/api/operational-value/tasks/next",
            headers=_headers("restart-user"),
        )
        assert same_user_replacement.status_code == 200
        assert (
            pair_by_task[same_user_replacement.json()["task"]["task_id"]]
            != pair_by_task[orphaned_task]
        )

        replacement = client.post(
            "/api/operational-value/tasks/next",
            headers=_headers("replacement-user"),
        )
        assert replacement.status_code == 200
