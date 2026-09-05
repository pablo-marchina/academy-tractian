from __future__ import annotations

from hashlib import sha256
import os
from threading import Event, Lock
from time import monotonic, sleep
from urllib.parse import urlsplit, urlunsplit
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

from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.observability import safe_run_id
from academy_tractian.postgres_action_execution_lease import PostgresActionExecutionLeaseStore
from academy_tractian.postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from academy_tractian.postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
    PostgresRunExecutionStore,
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
    "analysis_id": "analysis-lease-1",
    "body": {"justification": "Exact confirmed action for lease fencing proof."},
}


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
                    evidence_id="EV-action-lease",
                ),
            )
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "partial",
                "message": "The action remains behind explicit confirmation.",
            },
        )


class BlockingTransportState:
    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()
        self._lock = Lock()
        self.calls = 0

    def increment(self) -> None:
        with self._lock:
            self.calls += 1


class BlockingAcceptedTransport:
    def __init__(self, state: BlockingTransportState) -> None:
        self.state = state

    def request(self, _request: BoundRequest) -> TransportResponse:
        self.state.increment()
        self.state.started.set()
        if not self.state.release.wait(timeout=15):
            raise TimeoutError("blocking action transport was not released")
        return TransportResponse(
            status_code=202,
            headers={"content-type": "application/json"},
            body={"accepted": True},
        )


def _context(request: Request) -> AuthenticatedRuntimeContext:
    return AuthenticatedRuntimeContext(
        organization_id=request.headers.get("x-test-organization", "org-a"),
        identity_id="identity-user-a",
        user_id=request.headers.get("x-test-user", "user-a"),
    )


def _headers() -> dict[str, str]:
    return {"x-test-user": "user-a", "x-test-organization": "org-a"}


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-a",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="analysis-lease-1", company_id="company-a"),
        ),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_action_lease_{suffix}"
        self.role = f"academy_action_lease_scoped_{suffix}"
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


def _database(fixture: _PgFixture) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize=True,
    )


def _seed_action(database: PostgresOperationalDatabase):
    origin_raw = "origin-action-lease"
    origin_run = safe_run_id(origin_raw)
    execution_run = safe_run_id("action-execution-lease")
    access = PostgresRunAccessStore(database)
    executions = PostgresRunExecutionStore(database)
    assert access.claim(run_id=origin_run, organization_id="org-a", user_id="user-a")

    custody = PostgresPendingActionCustody(database, initialize=True)
    ledger = PostgresActionIdempotencyLedger(database, initialize=True)
    lease_store = PostgresActionExecutionLeaseStore(
        database,
        initialize=True,
        orphan_grace_seconds=5,
    )
    tool = canonical_tool_registry()["reprocess_analysis"]
    pending = custody.create_or_get(
        origin_raw_run_id=origin_raw,
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
        execution_run_id=execution_run,
    )
    assert access.claim(run_id=execution_run, organization_id="org-a", user_id="user-a")
    executions.create_accepted(
        run_id=execution_run,
        execution_kind="action",
        related_action_id=pending.action_id,
    )
    key_sha = sha256(private.idempotency_key.encode("utf-8")).hexdigest()
    assert ledger.claim(
        key_sha256=key_sha,
        action_fingerprint=pending.action_fingerprint,
        action_id=pending.action_id,
    )
    return pending.action_id, execution_run, custody, ledger, executions, lease_store, key_sha


def _expire(database: PostgresOperationalDatabase, action_id: str) -> None:
    with database.internal_pool.connection() as connection:
        with connection.transaction():
            connection.execute(
                f"""
                UPDATE "{database.schema}".action_execution_leases
                SET lease_expires_at = CURRENT_TIMESTAMP - INTERVAL '1 second'
                WHERE action_id = %s
                """,
                (action_id,),
            )


def _age_lease_less_action(database: PostgresOperationalDatabase, action_id: str) -> None:
    with database.internal_pool.connection() as connection:
        with connection.transaction():
            connection.execute(
                f"""
                UPDATE "{database.schema}".pending_actions
                SET updated_at = CURRENT_TIMESTAMP - INTERVAL '10 seconds'
                WHERE action_id = %s
                """,
                (action_id,),
            )


def _wait_future(app, run_id: str, timeout: float = 15.0) -> None:
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        future = app.state.run_execution_registry.future(run_id)
        if future is not None:
            future.result(timeout=max(0.1, deadline - monotonic()))
            return
        sleep(0.02)
    raise AssertionError(f"future not bound for {run_id}")


def _wait_action_state(app, action_id: str, expected: str, timeout: float = 10.0) -> None:
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        if app.state.pending_action_custody.get_safe(action_id).state == expected:
            return
        sleep(0.05)
    actual = app.state.pending_action_custody.get_safe(action_id).state
    raise AssertionError(f"action state did not reach {expected}; actual={actual}")


def test_healthy_action_lease_is_not_reconciled_or_reclaimed(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, _, executions, leases, _ = _seed_action(database)
        claim = leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-a",
            lease_seconds=30,
        )
        assert claim is not None
        assert leases.is_current_owner(claim) is True
        assert leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-b",
            lease_seconds=30,
        ) is None

        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == ()
        assert custody.get_safe(action_id).state == "EXECUTING"
        assert executions.get(execution_run).state == "accepted"  # type: ignore[union-attr]
        assert leases.snapshot()["automatic_replay_enabled"] is False
    finally:
        database.close()


def test_expired_action_lease_converges_uncertain_and_never_transfers(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, ledger, executions, leases, key_sha = _seed_action(database)
        claim = leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-a",
            lease_seconds=30,
        )
        assert claim is not None
        _expire(database, action_id)

        assert leases.is_current_owner(claim) is False
        assert leases.renew(claim=claim, lease_seconds=30) is False
        assert leases.release_terminal(claim) is False
        assert leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-b",
            lease_seconds=30,
        ) is None

        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == (action_id,)
        assert report.execution_runs_marked_uncertain == (execution_run,)
        assert report.ledger_entries_marked_uncertain == (action_id,)
        assert custody.get_safe(action_id).state == "UNCERTAIN"
        assert ledger.get(key_sha)["state"] == "UNCERTAIN"  # type: ignore[index]
        assert executions.get(execution_run).state == "uncertain"  # type: ignore[union-attr]
        assert leases.snapshot()["total_leases"] == 0
    finally:
        database.close()


def test_recent_executing_action_without_lease_gets_setup_grace(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, ledger, executions, leases, key_sha = _seed_action(database)
        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == ()
        assert custody.get_safe(action_id).state == "EXECUTING"
        assert ledger.get(key_sha)["state"] == "CLAIMED"  # type: ignore[index]
        assert executions.get(execution_run).state == "accepted"  # type: ignore[union-attr]
    finally:
        database.close()


def test_stale_executing_action_without_lease_is_fail_safe_uncertain(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, ledger, executions, leases, key_sha = _seed_action(database)
        _age_lease_less_action(database, action_id)
        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == (action_id,)
        assert custody.get_safe(action_id).state == "UNCERTAIN"
        assert ledger.get(key_sha)["state"] == "UNCERTAIN"  # type: ignore[index]
        assert executions.get(execution_run).state == "uncertain"  # type: ignore[union-attr]
    finally:
        database.close()


def test_multi_replica_action_lease_preserves_one_side_effect_and_fences_late_success(
    postgres_fixture,
) -> None:
    transport_state = BlockingTransportState()
    app_a = create_postgres_action_capable_product_app(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=True,
        decision_source_factory=ActionThenFinalSource,
        transport_factory=lambda: BlockingAcceptedTransport(transport_state),
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=True,
        heartbeat_interval_ms=250,
        action_execution_lease_seconds=3,
        action_execution_lease_scan_ms=100,
        action_execution_orphan_grace_seconds=1,
    )

    with TestClient(app_a) as client_a:
        origin = client_a.post(
            "/api/runs",
            headers=_headers(),
            json={"user_request": "Prepare one reprocess action and require confirmation."},
        )
        assert origin.status_code == 202
        origin_run = origin.json()["run_id"]
        _wait_future(app_a, origin_run)
        actions = client_a.get(f"/api/runs/{origin_run}/actions", headers=_headers()).json()["items"]
        assert len(actions) == 1
        action_id = actions[0]["action_id"]

        confirmation = client_a.post(
            f"/api/actions/{action_id}/confirm",
            headers=_headers(),
            json={"confirm": True},
        )
        assert confirmation.status_code == 202
        execution_run = confirmation.json()["execution_run_id"]
        assert transport_state.started.wait(timeout=10)
        assert transport_state.calls == 1
        assert app_a.state.pending_action_custody.get_safe(action_id).state == "EXECUTING"
        assert app_a.state.action_execution_lease_supervisor.snapshot()["active_local_leases"] == 1

        app_b = create_postgres_action_capable_product_app(
            internal_dsn=postgres_fixture.admin_dsn,
            scoped_dsn=postgres_fixture.scoped_dsn,
            schema=postgres_fixture.schema,
            initialize_schema=False,
            decision_source_factory=ActionThenFinalSource,
            transport_factory=lambda: BlockingAcceptedTransport(transport_state),
            context_provider=_context,
            authorization_resolver=_resolver,
            actions_enabled=True,
            heartbeat_interval_ms=250,
            action_execution_lease_seconds=3,
            action_execution_lease_scan_ms=100,
            action_execution_orphan_grace_seconds=1,
        )
        with TestClient(app_b) as client_b:
            # Replica B startup must not interpret A's healthy in-flight attempt as orphaned.
            assert client_b.get(f"/api/actions/{action_id}", headers=_headers()).json()["state"] == "EXECUTING"
            assert app_b.state.action_recovery_report.executing_actions_marked_uncertain == ()
            duplicate = client_b.post(
                f"/api/actions/{action_id}/confirm",
                headers=_headers(),
                json={"confirm": True},
            )
            assert duplicate.status_code == 409
            assert transport_state.calls == 1

            # Simulate A losing lease maintenance while its already-started HTTP request is still
            # blocked. B may converge the attempt to UNCERTAIN, but may never start a replacement.
            app_a.state.action_execution_lease_supervisor.close()
            database_b = app_b.state.postgres_operational_database
            _expire(database_b, action_id)
            _wait_action_state(app_b, action_id, "UNCERTAIN")
            assert transport_state.calls == 1
            execution = app_b.state.run_execution_store.get(execution_run)
            assert execution is not None and execution.state == "uncertain"

            # The external response arrives late on stale replica A. Lease-aware ledger/custody
            # proxies fence ACCEPTED/NOT_ACCEPTED writes, so the uncertain state is preserved.
            transport_state.release.set()
            _wait_future(app_a, execution_run)
            assert app_b.state.pending_action_custody.get_safe(action_id).state == "UNCERTAIN"
            assert app_b.state.run_execution_store.get(execution_run).state == "uncertain"  # type: ignore[union-attr]
            assert transport_state.calls == 1
            snapshot_b = app_b.state.action_execution_lease_supervisor.snapshot()
            assert snapshot_b["automatic_replay_enabled"] is False
            assert snapshot_b["store"]["total_leases"] == 0
