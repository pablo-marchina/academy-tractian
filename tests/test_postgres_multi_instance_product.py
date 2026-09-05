from __future__ import annotations

import os
from time import monotonic, sleep
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from psycopg import connect, sql

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.postgres_product_api import create_postgres_action_capable_product_app
from academy_tractian.product_api import AuthenticatedRuntimeContext
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
                "reason_code": "MULTI_INSTANCE_SHARED_STATE",
                "message": "Shared PostgreSQL state is visible from another application instance.",
            },
        )


class NoopTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("no tool call expected in this multi-instance proof")


def _context(request: Request) -> AuthenticatedRuntimeContext:
    return AuthenticatedRuntimeContext(
        organization_id=request.headers.get("x-test-organization", "org-a"),
        identity_id="identity-user-a",
        user_id=request.headers.get("x-test-user", "user-a"),
    )


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-a",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="asset-a", company_id="company-a"),
        ),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_multi_{suffix}"
        self.role = f"academy_multi_scoped_{suffix}"
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


def _app(postgres_fixture: _PgFixture, *, initialize: bool):
    return create_postgres_action_capable_product_app(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=initialize,
        decision_source_factory=FinalSource,
        transport_factory=NoopTransport,
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=False,
        heartbeat_interval_ms=250,
    )


def _headers() -> dict[str, str]:
    return {"x-test-user": "user-a", "x-test-organization": "org-a"}


def _wait_until(predicate, *, timeout_seconds: float = 5.0) -> None:
    deadline = monotonic() + timeout_seconds
    while monotonic() < deadline:
        if predicate():
            return
        sleep(0.02)
    raise AssertionError("condition was not satisfied before timeout")


def test_second_app_instance_reads_execution_trace_and_replays_sse(postgres_fixture) -> None:
    """Prove a request can continue its read/replay path on a different stateless replica."""

    first = _app(postgres_fixture, initialize=True)
    second = _app(postgres_fixture, initialize=False)

    with TestClient(first) as client_a, TestClient(second) as client_b:
        # Both replicas own one dedicated listener. Wait for B to be LISTENing before A writes so
        # this test proves a real cross-replica notification rather than timeout-only catch-up.
        _wait_until(lambda: second.state.realtime_wakeup.snapshot()["connected"] is True)

        accepted = client_a.post(
            "/api/runs",
            headers=_headers(),
            json={"user_request": "Complete the shared-state multi-instance acceptance run."},
        )
        assert accepted.status_code == 202
        run_id = accepted.json()["run_id"]
        future = first.state.run_execution_registry.future(run_id)
        assert future is not None
        future.result(timeout=15)

        _wait_until(lambda: second.state.realtime_wakeup.generation(run_id) >= 0)
        wakeup_snapshot = second.state.realtime_wakeup.snapshot()
        assert wakeup_snapshot["backend"] == "postgresql_listen_notify"
        assert wakeup_snapshot["notifications_received"] >= 1
        assert wakeup_snapshot["valid_notifications"] >= 1
        assert wakeup_snapshot["payload_rejections"] == 0
        assert second.state.realtime_backend == "postgresql_listen_notify"

        # No affinity to instance A: instance B authorizes the same tenant/user against shared
        # ownership state and reads durable execution + safe observability from PostgreSQL.
        run_from_b = client_b.get(f"/api/runs/{run_id}", headers=_headers())
        assert run_from_b.status_code == 200
        assert run_from_b.json()["terminal_reason_code"] == "MULTI_INSTANCE_SHARED_STATE"

        execution_from_b = client_b.get(f"/api/runs/{run_id}/execution", headers=_headers())
        assert execution_from_b.status_code == 200
        assert execution_from_b.json()["status"] == "completed"

        events_response = client_b.get(f"/api/runs/{run_id}/events", headers=_headers())
        assert events_response.status_code == 200
        events = events_response.json()["items"]
        assert len(events) >= 2
        assert [item["sequence"] for item in events] == sorted(item["sequence"] for item in events)

        first_event_id = events[0]["event_id"]
        later_event_ids = [item["event_id"] for item in events[1:]]
        replay = client_b.get(
            f"/api/stream?run_id={run_id}&follow=false&after_sequence=0",
            headers=_headers(),
        )
        assert replay.status_code == 200
        assert first_event_id not in replay.text
        for event_id in later_event_ids:
            assert f"id: {event_id}" in replay.text

        # Last-Event-ID is the native EventSource recovery path and must produce the same
        # no-duplicate continuation when the reconnect lands on replica B.
        native_replay = client_b.get(
            f"/api/stream?run_id={run_id}&follow=false",
            headers={**_headers(), "Last-Event-ID": first_event_id},
        )
        assert native_replay.status_code == 200
        assert first_event_id not in native_replay.text
        for event_id in later_event_ids:
            assert f"id: {event_id}" in native_replay.text

        assert first.state.observability_backend == "postgresql"
        assert second.state.observability_backend == "postgresql"
