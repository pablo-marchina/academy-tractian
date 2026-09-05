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

from academy_tractian.observability import safe_run_id
from academy_tractian.postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
    PostgresRunExecutionStore,
)
from academy_tractian.postgres_product_api import (
    create_postgres_action_capable_product_app,
    initialize_postgres_operational_schema,
)
from academy_tractian.postgres_runtime_handoff import PostgresRuntimeHandoffStore
from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.product_storage_contracts import RuntimeExecutionEnvelope
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
                "reason_code": "HORIZONTAL_HANDOFF_RECOVERED",
                "message": "Read-only runtime recovered on another replica.",
            },
        )


class NoopTransport:
    calls = 0

    def request(self, _request: BoundRequest) -> TransportResponse:
        type(self).calls += 1
        raise AssertionError("no tool call expected in horizontal handoff proof")


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
        resource_company_bindings=(),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_handoff_{suffix}"
        self.role = f"academy_handoff_scoped_{suffix}"
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
        initialize_postgres_operational_schema(
            internal_dsn=fixture.admin_dsn,
            scoped_dsn=fixture.scoped_dsn,
            schema=fixture.schema,
        )
        yield fixture
    finally:
        fixture.cleanup()


def _database(fixture: _PgFixture) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize=False,
    )


def _seed_runtime(
    database: PostgresOperationalDatabase,
    *,
    raw_request_id: str,
    user_request: str = "Recover this read-only investigation.",
) -> tuple[str, PostgresRunExecutionStore, PostgresRuntimeHandoffStore]:
    run_id = safe_run_id(raw_request_id)
    access = PostgresRunAccessStore(database)
    executions = PostgresRunExecutionStore(database)
    handoff = PostgresRuntimeHandoffStore(database)
    assert access.claim(run_id=run_id, organization_id="org-a", user_id="user-a")
    executions.create_accepted(run_id=run_id)
    handoff.enqueue(
        RuntimeExecutionEnvelope(
            run_id=run_id,
            request_id=raw_request_id,
            identity_id="identity-user-a",
            user_id="user-a",
            user_request=user_request,
        )
    )
    return run_id, executions, handoff


def _expire_lease(database: PostgresOperationalDatabase, run_id: str) -> None:
    with database.internal_pool.connection() as connection:
        with connection.transaction():
            connection.execute(
                f"""
                UPDATE "{database.schema}".runtime_work_items
                SET lease_expires_at = CURRENT_TIMESTAMP - INTERVAL '1 second'
                WHERE run_id = %s
                """,
                (run_id,),
            )


def test_runtime_handoff_lease_takeover_is_generation_fenced(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        run_id, executions, handoff = _seed_runtime(
            database,
            raw_request_id="handoff-generation-proof",
        )

        claim_a = handoff.claim_specific(
            run_id=run_id,
            owner_instance_id="replica-a",
            lease_seconds=30,
        )
        assert claim_a is not None
        assert claim_a.claim_generation == 1
        assert claim_a.previous_state == "accepted"
        assert handoff.is_current_owner(
            run_id=run_id,
            owner_instance_id="replica-a",
            claim_generation=1,
        )
        assert handoff.claim_specific(
            run_id=run_id,
            owner_instance_id="replica-b",
            lease_seconds=30,
        ) is None

        _expire_lease(database, run_id)
        assert not handoff.is_current_owner(
            run_id=run_id,
            owner_instance_id="replica-a",
            claim_generation=1,
        )
        assert not handoff.renew(
            run_id=run_id,
            owner_instance_id="replica-a",
            claim_generation=1,
            lease_seconds=30,
        )

        claim_b = handoff.claim_specific(
            run_id=run_id,
            owner_instance_id="replica-b",
            lease_seconds=30,
        )
        assert claim_b is not None
        assert claim_b.claim_generation == 2
        assert claim_b.previous_state == "running"
        assert claim_b.recovery_count == 1

        # The stale generation cannot win a terminal write after takeover.
        assert not handoff.complete(
            run_id=run_id,
            owner_instance_id="replica-a",
            claim_generation=1,
        )
        assert handoff.complete(
            run_id=run_id,
            owner_instance_id="replica-b",
            claim_generation=2,
        )
        assert executions.get(run_id).state == "completed"  # type: ignore[union-attr]
        snapshot = handoff.snapshot()
        assert snapshot["queued_or_running"] == 0
        assert snapshot["active_leases"] == 0
    finally:
        database.close()


def test_new_replica_does_not_interrupt_healthy_leased_runtime(postgres_fixture) -> None:
    seed_database = _database(postgres_fixture)
    run_id, executions, handoff = _seed_runtime(
        seed_database,
        raw_request_id="healthy-owner-proof",
    )
    claim = handoff.claim_specific(
        run_id=run_id,
        owner_instance_id="healthy-replica-a",
        lease_seconds=60,
    )
    assert claim is not None
    assert executions.get(run_id).state == "running"  # type: ignore[union-attr]
    seed_database.close()

    app = create_postgres_action_capable_product_app(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=False,
        decision_source_factory=FinalSource,
        transport_factory=NoopTransport,
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=False,
        runtime_handoff_lease_seconds=5,
        runtime_handoff_scan_ms=100,
    )
    with TestClient(app):
        # Constructor/startup reconciliation must not reinterpret another replica's live lease
        # as an orphan. The local supervisor also cannot claim it while the lease is current.
        assert app.state.run_execution_store.get(run_id).state == "running"
        assert not any(item.run_id == run_id for item in app.state.recovered_executions)
        sleep(0.25)
        assert app.state.run_execution_store.get(run_id).state == "running"
        snapshot = app.state.runtime_handoff_supervisor.snapshot()
        assert snapshot["recovery_claims_started"] == 0


def test_second_replica_recovers_expired_runtime_to_completion(postgres_fixture) -> None:
    NoopTransport.calls = 0
    seed_database = _database(postgres_fixture)
    raw_request_id = "dead-owner-horizontal-recovery"
    run_id, executions, handoff = _seed_runtime(
        seed_database,
        raw_request_id=raw_request_id,
    )
    dead_claim = handoff.claim_specific(
        run_id=run_id,
        owner_instance_id="dead-replica-a",
        lease_seconds=30,
    )
    assert dead_claim is not None
    assert executions.get(run_id).state == "running"  # type: ignore[union-attr]
    _expire_lease(seed_database, run_id)
    seed_database.close()

    app = create_postgres_action_capable_product_app(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize_schema=False,
        decision_source_factory=FinalSource,
        transport_factory=NoopTransport,
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=False,
        runtime_handoff_lease_seconds=5,
        runtime_handoff_scan_ms=100,
    )

    with TestClient(app) as client:
        deadline = monotonic() + 10
        state = None
        while monotonic() < deadline:
            state = app.state.run_execution_store.get(run_id).state
            if state == "completed":
                break
            sleep(0.05)
        assert state == "completed"

        run = client.get(
            f"/api/runs/{run_id}",
            headers={"x-test-user": "user-a", "x-test-organization": "org-a"},
        )
        assert run.status_code == 200
        assert run.json()["terminal_reason_code"] == "HORIZONTAL_HANDOFF_RECOVERED"
        assert run.json()["completed"] is True

        supervisor = app.state.runtime_handoff_supervisor.snapshot()
        assert supervisor["recovery_claims_started"] >= 1
        assert supervisor["fenced_terminal_writes"] == 0
        assert supervisor["queue"]["queued_or_running"] == 0
        assert app.state.runtime_handoff_backend == "postgresql_skip_locked_lease"
        assert app.state.local_test_storage_enabled is False
        assert NoopTransport.calls == 0
