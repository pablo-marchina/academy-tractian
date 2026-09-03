from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from psycopg import connect, sql

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.action_recovery import reconcile_orphaned_actions
from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.observability import safe_run_id
from academy_tractian.postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from academy_tractian.postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
)
from academy_tractian.postgres_product_api import create_postgres_action_capable_product_app
from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.production_actions_v2 import ProductionActionPrincipal
from academy_tractian.runtime import canonical_tool_registry


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


ACTION_ARGS = {
    "analysis_id": "analysis-1",
    "body": {
        "justification": "Evidence reviewed and the operator must confirm this exact reprocessing action before execution."
    },
}


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "PostgreSQL-backed product run completed.",
            },
        )


class ActionThenFinalSource:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        self.calls += 1
        if self.calls == 1:
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="reprocess_analysis",
                    arguments=ACTION_ARGS,
                    evidence_id="EV-postgres-action",
                ),
            )
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "partial",
                "message": "The consequential action is pending explicit operator confirmation.",
            },
        )


class RecordingTransport:
    def __init__(self, calls: list[BoundRequest]) -> None:
        self.calls = calls

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=202,
            headers={"content-type": "application/json"},
            body={"accepted": True},
        )


def _context(request: Request) -> AuthenticatedRuntimeContext:
    user = request.headers.get("x-test-user", "user-a")
    org = request.headers.get("x-test-organization", "org-a")
    return AuthenticatedRuntimeContext(
        organization_id=org,
        identity_id=f"identity-{user}",
        user_id=user,
    )


def _headers(user: str, org: str = "org-a") -> dict[str, str]:
    return {"x-test-user": user, "x-test-organization": org}


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-1",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="analysis-1", company_id="company-1"),
        ),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_prod_{suffix}"
        self.role = f"academy_scoped_{suffix}"
        self.password = "scoped-test-password"
        with connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(self.role),
                    sql.Literal(self.password),
                )
            )
        # CI DSN is intentionally simple and local. Replace only credentials, preserving host/db.
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
            connection.execute(
                sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role))
            )


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _wait(app, run_id: str) -> None:
    future = app.state.run_execution_registry.future(run_id)
    assert future is not None
    future.result(timeout=15)


def test_postgres_product_multiuser_rls_and_restart(tmp_path: Path, postgres_fixture) -> None:
    calls: list[BoundRequest] = []
    db_path = tmp_path / "observability.duckdb"

    first = create_postgres_action_capable_product_app(
        db_path=db_path,
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=True,
        decision_source_factory=FinalSource,
        transport_factory=lambda: RecordingTransport(calls),
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=False,
        heartbeat_interval_ms=250,
    )
    with TestClient(first) as client:
        run_a_response = client.post(
            "/api/runs",
            headers=_headers("user-a", "org-a"),
            json={"user_request": "Investigate ticket A."},
        )
        run_b_response = client.post(
            "/api/runs",
            headers=_headers("user-b", "org-b"),
            json={"user_request": "Investigate ticket B."},
        )
        assert run_a_response.status_code == 202
        assert run_b_response.status_code == 202
        run_a = run_a_response.json()["run_id"]
        run_b = run_b_response.json()["run_id"]
        _wait(first, run_a)
        _wait(first, run_b)

        assert first.state.operational_backend == "postgresql"
        assert first.state.postgres_operational_database.ready() is True
        assert client.get(f"/api/runs/{run_a}", headers=_headers("user-a", "org-a")).status_code == 200
        assert client.get(f"/api/runs/{run_b}", headers=_headers("user-b", "org-b")).status_code == 200
        assert client.get(f"/api/runs/{run_a}", headers=_headers("user-b", "org-b")).status_code == 404
        assert client.get(f"/api/runs/{run_a}", headers=_headers("user-a", "org-b")).status_code == 404
        assert (
            client.get(
                f"/api/stream?run_id={run_a}&follow=false",
                headers=_headers("user-b", "org-b"),
            ).status_code
            == 404
        )
        assert first.state.run_access_store.get_scoped(run_id=run_a, organization_id="org-b") is None
        assert calls == []

    second = create_postgres_action_capable_product_app(
        db_path=db_path,
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=False,
        decision_source_factory=FinalSource,
        transport_factory=lambda: RecordingTransport(calls),
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=False,
        heartbeat_interval_ms=250,
    )
    with TestClient(second) as client:
        assert client.get(f"/api/runs/{run_a}", headers=_headers("user-a", "org-a")).status_code == 200
        execution = client.get(
            f"/api/runs/{run_a}/execution", headers=_headers("user-a", "org-a")
        )
        assert execution.status_code == 200
        assert execution.json()["status"] == "completed"
        assert client.get(f"/api/runs/{run_a}", headers=_headers("user-b", "org-b")).status_code == 404


def test_postgres_action_custody_confirmation_and_tenant_scope(tmp_path: Path, postgres_fixture) -> None:
    calls: list[BoundRequest] = []
    app = create_postgres_action_capable_product_app(
        db_path=tmp_path / "action-observability.duckdb",
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=True,
        decision_source_factory=ActionThenFinalSource,
        transport_factory=lambda: RecordingTransport(calls),
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=True,
        heartbeat_interval_ms=250,
    )
    with TestClient(app) as client:
        accepted = client.post(
            "/api/runs",
            headers=_headers("user-a", "org-a"),
            json={"user_request": "Reprocess analysis-1 only after confirmation."},
        )
        assert accepted.status_code == 202
        origin_run = accepted.json()["run_id"]
        _wait(app, origin_run)

        actions = client.get(
            f"/api/runs/{origin_run}/actions", headers=_headers("user-a", "org-a")
        )
        assert actions.status_code == 200
        pending = actions.json()["items"][0]
        action_id = pending["action_id"]
        assert pending["state"] == "PENDING_CONFIRMATION"
        assert calls == []

        assert client.get(f"/api/actions/{action_id}", headers=_headers("user-b", "org-a")).status_code == 404
        assert client.get(f"/api/actions/{action_id}", headers=_headers("user-a", "org-b")).status_code == 404

        confirmation = client.post(
            f"/api/actions/{action_id}/confirm",
            headers=_headers("user-a", "org-a"),
            json={"confirm": True},
        )
        assert confirmation.status_code == 202
        action_run = confirmation.json()["execution_run_id"]
        _wait(app, action_run)
        assert len(calls) == 1
        assert calls[0].method == "POST"
        assert calls[0].path.endswith("/analyses/analysis-1/reprocess")
        assert client.get(f"/api/actions/{action_id}", headers=_headers("user-a", "org-a")).json()["state"] == "ACCEPTED"

        duplicate = client.post(
            f"/api/actions/{action_id}/confirm",
            headers=_headers("user-a", "org-a"),
            json={"confirm": True},
        )
        assert duplicate.status_code == 409
        assert len(calls) == 1

        # Browser-safe surfaces never serialize private custody material.
        serialized = client.get(
            f"/api/runs/{origin_run}/actions", headers=_headers("user-a", "org-a")
        ).text.lower()
        assert "operator must confirm this exact" not in serialized
        assert "idem-" not in serialized


def test_postgres_orphaned_action_recovery_never_replays(postgres_fixture) -> None:
    database = PostgresOperationalDatabase(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize=True,
    )
    try:
        access = PostgresRunAccessStore(database)
        access.claim(
            run_id=safe_run_id("origin-run"),
            organization_id="org-a",
            user_id="user-a",
        )
        custody = PostgresPendingActionCustody(database, initialize=True)
        ledger = PostgresActionIdempotencyLedger(database, initialize=True)
        tool = canonical_tool_registry()["reprocess_analysis"]
        pending = custody.create_or_get(
            origin_raw_run_id="origin-run",
            requester_user_id="user-a",
            tool=tool,
            arguments=ACTION_ARGS,
        )
        private = custody.get_private_for_requester(
            action_id=pending.action_id,
            requester_user_id="user-a",
        )
        assert custody.transition(
            action_id=pending.action_id,
            expected_states=frozenset({"PENDING_CONFIRMATION"}),
            new_state="EXECUTING",
            execution_run_id="safe-action-run",
        )
        key_sha = sha256(private.idempotency_key.encode("utf-8")).hexdigest()
        assert ledger.claim(
            key_sha256=key_sha,
            action_fingerprint=pending.action_fingerprint,
            action_id=pending.action_id,
        )

        report = reconcile_orphaned_actions(custody=custody, ledger=ledger)
        assert report.executing_actions_marked_uncertain == (pending.action_id,)
        assert report.claimed_ledger_entries_marked_uncertain == (pending.action_id,)
        assert custody.get_safe(pending.action_id).state == "UNCERTAIN"
        assert ledger.get(key_sha)["state"] == "UNCERTAIN"  # type: ignore[index]

        second = reconcile_orphaned_actions(custody=custody, ledger=ledger)
        assert second.executing_actions_marked_uncertain == ()
        assert second.claimed_ledger_entries_marked_uncertain == ()
        assert custody.get_safe(pending.action_id).state == "UNCERTAIN"
    finally:
        database.close()