from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
from time import time
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from psycopg import connect, sql

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from academy_tractian.observability import safe_run_id
from academy_tractian.postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from academy_tractian.postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
    PostgresRunExecutionStore,
)
from academy_tractian.postgres_product_api import initialize_postgres_operational_schema
from academy_tractian.product_api import DEFAULT_RUNTIME_PERMISSIONS
from academy_tractian.production_actions_v2 import ProductionActionPrincipal
from academy_tractian.restart_recovery_campaign import (
    RestartRecoveryObservation,
    verify_restart_recovery,
)
from academy_tractian.runtime import canonical_tool_registry
from academy_tractian.runtime_identity import SignedRuntimeIdentityClaims, issue_signed_runtime_token


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)

SECRET = "restart-recovery-runtime-secret-that-is-at-least-32-bytes"
ISSUER = "academy-restart-recovery"
AUDIENCE = "academy-product"
ACTION_ARGS = {
    "analysis_id": "analysis-recovery",
    "body": {"justification": "Synthetic provider-free restart recovery evidence only."},
}


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Fresh provider-free run after recovery completed.",
            },
        )


class CountingTransport:
    requests: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.requests.append(request)
        return TransportResponse(status_code=200, headers={}, body={"status": "unexpected"})


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-recovery",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_recovery_{suffix}"
        self.role = f"academy_recovery_scoped_{suffix}"
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


def _headers(*, user_id: str, organization_id: str) -> dict[str, str]:
    now = int(time())
    token = issue_signed_runtime_token(
        secret=SECRET,
        claims=SignedRuntimeIdentityClaims(
            issuer=ISSUER,
            audience=AUDIENCE,
            token_id=f"recovery-{uuid4().hex}",
            identity_id=f"identity-{organization_id}-{user_id}",
            user_id=user_id,
            organization_id=organization_id,
            permissions=tuple(sorted(DEFAULT_RUNTIME_PERMISSIONS)),
            issued_at=now - 5,
            expires_at=now + 300,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def _build_app(*, fixture: _PgFixture):
    return create_authenticated_postgres_action_capable_product_app(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        decision_source_factory=FinalSource,
        transport_factory=CountingTransport,
        authorization_resolver=_resolver,
        runtime_identity_secret=SECRET,
        runtime_identity_issuer=ISSUER,
        runtime_identity_audience=AUDIENCE,
        schema=fixture.schema,
        initialize_schema=False,
        max_workers=2,
        provider_calls_enabled=True,
        actions_enabled=False,
        heartbeat_interval_ms=250,
    )


def test_promoted_postgres_restart_recovery_is_fail_safe_and_idempotent(
    postgres_fixture,
) -> None:
    CountingTransport.requests.clear()
    initialize_postgres_operational_schema(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
    )

    seed_db = PostgresOperationalDatabase(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize=False,
    )
    access = PostgresRunAccessStore(seed_db)
    executions = PostgresRunExecutionStore(seed_db)
    custody = PostgresPendingActionCustody(seed_db, initialize=False)
    ledger = PostgresActionIdempotencyLedger(seed_db, initialize=False)

    runtime_accepted = "run-recovery-runtime-accepted"
    runtime_running = "run-recovery-runtime-running"
    runtime_completed = "run-recovery-runtime-completed"
    runtime_failed = "run-recovery-runtime-failed"
    action_execution_run = "run-recovery-action-execution"
    for run_id in (
        runtime_accepted,
        runtime_running,
        runtime_completed,
        runtime_failed,
        action_execution_run,
    ):
        assert access.claim(run_id=run_id, organization_id="org-a", user_id="user-a")

    executions.create_accepted(run_id=runtime_accepted)
    executions.create_accepted(run_id=runtime_running)
    assert executions.transition(
        run_id=runtime_running,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )

    executions.create_accepted(run_id=runtime_completed)
    assert executions.transition(
        run_id=runtime_completed,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )
    assert executions.transition(
        run_id=runtime_completed,
        expected_states=frozenset({"running"}),
        new_state="completed",
    )

    executions.create_accepted(run_id=runtime_failed)
    assert executions.transition(
        run_id=runtime_failed,
        expected_states=frozenset({"accepted"}),
        new_state="failed",
    )

    action_tool = canonical_tool_registry()["reprocess_analysis"]
    executing_origin_raw = "raw-recovery-action-origin"
    executing_origin_safe = safe_run_id(executing_origin_raw)
    assert access.claim(
        run_id=executing_origin_safe,
        organization_id="org-a",
        user_id="user-a",
    )
    executing_action = custody.create_or_get(
        origin_raw_run_id=executing_origin_raw,
        requester_user_id="user-a",
        tool=action_tool,
        arguments=ACTION_ARGS,
    )
    executing_private = custody.get_private_for_requester(
        action_id=executing_action.action_id,
        requester_user_id="user-a",
    )
    assert custody.transition(
        action_id=executing_action.action_id,
        expected_states=frozenset({"PENDING_CONFIRMATION"}),
        new_state="EXECUTING",
        execution_run_id=action_execution_run,
    )
    key_sha256 = sha256(executing_private.idempotency_key.encode("utf-8")).hexdigest()
    assert ledger.claim(
        key_sha256=key_sha256,
        action_fingerprint=executing_action.action_fingerprint,
        action_id=executing_action.action_id,
    )
    executions.create_accepted(
        run_id=action_execution_run,
        execution_kind="action",
        related_action_id=executing_action.action_id,
    )
    assert executions.transition(
        run_id=action_execution_run,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )

    pending_origin_raw = "raw-recovery-pending-origin"
    pending_origin_safe = safe_run_id(pending_origin_raw)
    assert access.claim(
        run_id=pending_origin_safe,
        organization_id="org-a",
        user_id="user-a",
    )
    pending_action = custody.create_or_get(
        origin_raw_run_id=pending_origin_raw,
        requester_user_id="user-a",
        tool=action_tool,
        arguments={
            "analysis_id": "analysis-pending",
            "body": {"justification": "Must remain pending across restart."},
        },
    )
    seed_db.close()

    first = _build_app(fixture=postgres_fixture)
    assert first.state.local_test_storage_enabled is False
    recovered = tuple(first.state.recovered_executions)
    first_action_recovery = first.state.action_recovery_report
    first_db = first.state.postgres_operational_database
    first_executions = PostgresRunExecutionStore(first_db)
    first_custody = first.state.pending_action_custody
    first_ledger = first.state.action_idempotency_ledger

    first_runtime_interrupted = sum(
        item.execution_kind == "runtime" and item.state == "interrupted" for item in recovered
    )
    first_action_execution_uncertain = sum(
        item.execution_kind == "action" and item.state == "uncertain" for item in recovered
    )

    assert first_executions.get(runtime_accepted).state == "interrupted"  # type: ignore[union-attr]
    assert first_executions.get(runtime_running).state == "interrupted"  # type: ignore[union-attr]
    assert first_executions.get(action_execution_run).state == "uncertain"  # type: ignore[union-attr]
    assert first_custody.get_safe(executing_action.action_id).state == "UNCERTAIN"
    assert first_ledger.get(key_sha256)["state"] == "UNCERTAIN"  # type: ignore[index]

    pending_preserved = first_custody.get_safe(pending_action.action_id).state == "PENDING_CONFIRMATION"
    completed_preserved = first_executions.get(runtime_completed).state == "completed"  # type: ignore[union-attr]
    failed_preserved = first_executions.get(runtime_failed).state == "failed"  # type: ignore[union-attr]
    assert pending_preserved
    assert completed_preserved
    assert failed_preserved

    with TestClient(first) as client:
        accepted = client.post(
            "/api/runs",
            headers=_headers(user_id="user-a", organization_id="org-a"),
            json={"user_request": "Run after restart recovery."},
        )
        assert accepted.status_code == 202
        fresh_run_id = accepted.json()["run_id"]
        future = first.state.run_execution_registry.future(fresh_run_id)
        assert future is not None
        future.result(timeout=10)
        fresh_completed = first.state.run_execution_registry.status(fresh_run_id) == "completed"

        wrong_tenant = client.get(
            f"/api/runs/{fresh_run_id}",
            headers=_headers(user_id="user-b", organization_id="org-b"),
        )
        cross_tenant_blocked = (
            wrong_tenant.status_code == 404
            and wrong_tenant.json()["detail"] == "run_not_found"
        )

    first_transport_calls = len(CountingTransport.requests)

    second = _build_app(fixture=postgres_fixture)
    assert second.state.local_test_storage_enabled is False
    second_recovered = tuple(second.state.recovered_executions)
    second_action_recovery = second.state.action_recovery_report
    second_custody = second.state.pending_action_custody
    second_executions = PostgresRunExecutionStore(second.state.postgres_operational_database)

    with TestClient(second):
        assert second_custody.get_safe(executing_action.action_id).state == "UNCERTAIN"
        assert second_custody.get_safe(pending_action.action_id).state == "PENDING_CONFIRMATION"
        assert second_executions.get(runtime_completed).state == "completed"  # type: ignore[union-attr]
        assert second_executions.get(runtime_failed).state == "failed"  # type: ignore[union-attr]
        assert second_executions.get(fresh_run_id).state == "completed"  # type: ignore[union-attr]

    report = verify_restart_recovery(
        RestartRecoveryObservation(
            first_restart_runtime_interrupted=first_runtime_interrupted,
            first_restart_action_execution_uncertain=first_action_execution_uncertain,
            first_restart_action_custody_uncertain=len(
                first_action_recovery.executing_actions_marked_uncertain
            ),
            first_restart_ledger_uncertain=len(
                first_action_recovery.claimed_ledger_entries_marked_uncertain
            ),
            pending_confirmation_preserved=pending_preserved,
            completed_runtime_preserved=completed_preserved,
            failed_runtime_preserved=failed_preserved,
            fresh_runtime_completed_after_recovery=fresh_completed,
            cross_tenant_visibility_blocked=cross_tenant_blocked,
            first_restart_provider_calls=0,
            first_restart_action_transport_calls=first_transport_calls,
            second_restart_new_runtime_recoveries=len(second_recovered),
            second_restart_new_action_custody_recoveries=len(
                second_action_recovery.executing_actions_marked_uncertain
            ),
            second_restart_new_ledger_recoveries=len(
                second_action_recovery.claimed_ledger_entries_marked_uncertain
            ),
            second_restart_provider_calls=0,
            second_restart_action_transport_calls=len(CountingTransport.requests) - first_transport_calls,
        )
    )

    assert report.status == "VERIFIED"
    assert report.production_availability_claim_ready is False
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0

    output = os.environ.get("ACADEMY_RESTART_RECOVERY_EVIDENCE_OUTPUT")
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
