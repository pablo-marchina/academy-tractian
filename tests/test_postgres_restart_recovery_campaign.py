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
from research.e2.models import BoundRequest
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
    RecoveryCaseObservation,
    RestartRecoveryProtocol,
    build_restart_recovery_report,
)
from academy_tractian.runtime import canonical_tool_registry
from academy_tractian.runtime_identity import SignedRuntimeIdentityClaims, issue_signed_runtime_token


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)

SECRET = "restart-recovery-secret-that-is-at-least-32-bytes"
ISSUER = "academy-restart-recovery"
AUDIENCE = "academy-product"
ACTION_ARGS = {
    "analysis_id": "analysis-recovery",
    "body": {
        "justification": "Synthetic restart-recovery custody state. It must never be replayed during startup."
    },
}


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Recovery test source should not be invoked during startup.",
            },
        )


class RecordingTransport:
    def __init__(self, calls: list[BoundRequest]) -> None:
        self.calls = calls

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        raise AssertionError("restart recovery must never replay a consequential transport")


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-recovery",
        permissions=frozenset(),
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


def _headers(*, organization_id: str = "org-a", user_id: str = "user-a") -> dict[str, str]:
    now = int(time())
    token = issue_signed_runtime_token(
        secret=SECRET,
        claims=SignedRuntimeIdentityClaims(
            issuer=ISSUER,
            audience=AUDIENCE,
            token_id=f"recovery-{organization_id}-{user_id}-{uuid4().hex[:12]}",
            identity_id=f"identity-{organization_id}-{user_id}",
            user_id=user_id,
            organization_id=organization_id,
            permissions=tuple(sorted(DEFAULT_RUNTIME_PERMISSIONS)),
            issued_at=now - 5,
            expires_at=now + 300,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def _app(*, tmp_path: Path, fixture: _PgFixture, calls: list[BoundRequest]):
    return create_authenticated_postgres_action_capable_product_app(
        db_path=tmp_path / "restart-observability.duckdb",
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        decision_source_factory=FinalSource,
        transport_factory=lambda: RecordingTransport(calls),
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


def test_promoted_authenticated_postgres_restart_recovery_is_fail_safe_and_idempotent(
    tmp_path: Path,
    postgres_fixture,
) -> None:
    protocol = RestartRecoveryProtocol.model_validate_json(
        Path("research/restart-recovery-protocol-v1.json").read_text(encoding="utf-8")
    )
    initialize_postgres_operational_schema(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
    )

    runtime_accepted = safe_run_id("rr-runtime-accepted")
    runtime_running = safe_run_id("rr-runtime-running")
    action_accepted = safe_run_id("rr-action-execution-accepted")
    action_running = safe_run_id("rr-action-execution-running")
    pending_origin_raw = "rr-pending-origin"
    executing_origin_raw = "rr-executing-origin"
    accepted_origin_raw = "rr-accepted-origin"

    database = PostgresOperationalDatabase(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.schema,
        initialize=False,
    )
    try:
        access = PostgresRunAccessStore(database)
        executions = PostgresRunExecutionStore(database)
        custody = PostgresPendingActionCustody(database, initialize=False)
        ledger = PostgresActionIdempotencyLedger(database, initialize=False)

        for run_id in (runtime_accepted, runtime_running, action_accepted, action_running):
            access.claim(run_id=run_id, organization_id="org-a", user_id="user-a")
        for raw_origin in (pending_origin_raw, executing_origin_raw, accepted_origin_raw):
            access.claim(
                run_id=safe_run_id(raw_origin),
                organization_id="org-a",
                user_id="user-a",
            )

        tool = canonical_tool_registry()["reprocess_analysis"]
        pending = custody.create_or_get(
            origin_raw_run_id=pending_origin_raw,
            requester_user_id="user-a",
            tool=tool,
            arguments=ACTION_ARGS,
        )
        executing = custody.create_or_get(
            origin_raw_run_id=executing_origin_raw,
            requester_user_id="user-a",
            tool=tool,
            arguments=ACTION_ARGS,
        )
        accepted = custody.create_or_get(
            origin_raw_run_id=accepted_origin_raw,
            requester_user_id="user-a",
            tool=tool,
            arguments=ACTION_ARGS,
        )

        executing_private = custody.get_private_for_requester(
            action_id=executing.action_id,
            requester_user_id="user-a",
        )
        accepted_private = custody.get_private_for_requester(
            action_id=accepted.action_id,
            requester_user_id="user-a",
        )
        assert custody.transition(
            action_id=executing.action_id,
            expected_states=frozenset({"PENDING_CONFIRMATION"}),
            new_state="EXECUTING",
            execution_run_id=action_running,
        )
        executing_key_sha = sha256(executing_private.idempotency_key.encode("utf-8")).hexdigest()
        assert ledger.claim(
            key_sha256=executing_key_sha,
            action_fingerprint=executing.action_fingerprint,
            action_id=executing.action_id,
        )

        assert custody.transition(
            action_id=accepted.action_id,
            expected_states=frozenset({"PENDING_CONFIRMATION"}),
            new_state="EXECUTING",
            execution_run_id="accepted-action-run",
        )
        assert custody.transition(
            action_id=accepted.action_id,
            expected_states=frozenset({"EXECUTING"}),
            new_state="ACCEPTED",
        )
        accepted_key_sha = sha256(accepted_private.idempotency_key.encode("utf-8")).hexdigest()
        assert ledger.claim(
            key_sha256=accepted_key_sha,
            action_fingerprint=accepted.action_fingerprint,
            action_id=accepted.action_id,
        )
        ledger.mark(key_sha256=accepted_key_sha, state="ACCEPTED")

        executions.create_accepted(run_id=runtime_accepted)
        executions.create_accepted(run_id=runtime_running)
        assert executions.transition(
            run_id=runtime_running,
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )
        executions.create_accepted(
            run_id=action_accepted,
            execution_kind="action",
            related_action_id="orphan-action-accepted",
        )
        executions.create_accepted(
            run_id=action_running,
            execution_kind="action",
            related_action_id=executing.action_id,
        )
        assert executions.transition(
            run_id=action_running,
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )

        before_transition_counts = {
            run_id: executions.get(run_id).transition_count  # type: ignore[union-attr]
            for run_id in (runtime_accepted, runtime_running, action_accepted, action_running)
        }
    finally:
        database.close()

    transport_calls: list[BoundRequest] = []
    first = _app(tmp_path=tmp_path, fixture=postgres_fixture, calls=transport_calls)
    recovered = {item.run_id: item for item in first.state.recovered_executions}
    action_recovery = first.state.action_recovery_report

    assert set(recovered) == {runtime_accepted, runtime_running, action_accepted, action_running}
    assert recovered[runtime_accepted].state == "interrupted"
    assert recovered[runtime_running].state == "interrupted"
    assert recovered[action_accepted].state == "uncertain"
    assert recovered[action_running].state == "uncertain"
    assert action_recovery.executing_actions_marked_uncertain == (executing.action_id,)
    assert action_recovery.claimed_ledger_entries_marked_uncertain == (executing.action_id,)
    assert transport_calls == []

    after_transition_counts = {
        run_id: first.state.run_execution_store.get(run_id).transition_count
        for run_id in (runtime_accepted, runtime_running, action_accepted, action_running)
    }
    for run_id in after_transition_counts:
        assert after_transition_counts[run_id] - before_transition_counts[run_id] == 1

    with TestClient(first) as client:
        owner = _headers()
        other_tenant = _headers(organization_id="org-b", user_id="user-a")
        owner_execution = client.get(f"/api/runs/{runtime_running}/execution", headers=owner)
        cross_tenant = client.get(
            f"/api/runs/{runtime_running}/execution",
            headers=other_tenant,
        )
        assert owner_execution.status_code == 200
        assert owner_execution.json()["status"] == "interrupted"
        assert cross_tenant.status_code == 404
        assert cross_tenant.json()["detail"] == "run_not_found"

        assert client.get(f"/api/actions/{pending.action_id}", headers=owner).json()["state"] == "PENDING_CONFIRMATION"
        assert client.get(f"/api/actions/{executing.action_id}", headers=owner).json()["state"] == "UNCERTAIN"
        assert client.get(f"/api/actions/{accepted.action_id}", headers=owner).json()["state"] == "ACCEPTED"

        assert first.state.action_idempotency_ledger.get(executing_key_sha)["state"] == "UNCERTAIN"
        assert first.state.action_idempotency_ledger.get(accepted_key_sha)["state"] == "ACCEPTED"

        health = client.get("/api/production/health").json()
        recovery = health["measured"]["recovery"]
        assert recovery["orphaned_executions_reconciled"] == 4
        assert recovery["interrupted_runtime_runs"] == 2
        assert recovery["uncertain_action_runs"] == 2
        assert transport_calls == []

    second = _app(tmp_path=tmp_path, fixture=postgres_fixture, calls=transport_calls)
    assert second.state.recovered_executions == ()
    assert second.state.action_recovery_report.executing_actions_marked_uncertain == ()
    assert second.state.action_recovery_report.claimed_ledger_entries_marked_uncertain == ()
    assert transport_calls == []

    with TestClient(second) as client:
        owner = _headers()
        assert client.get(f"/api/runs/{runtime_running}/execution", headers=owner).json()["status"] == "interrupted"
        assert client.get(f"/api/runs/{action_running}/execution", headers=owner).json()["status"] == "uncertain"
        assert client.get(f"/api/actions/{pending.action_id}", headers=owner).json()["state"] == "PENDING_CONFIRMATION"
        assert client.get(f"/api/actions/{executing.action_id}", headers=owner).json()["state"] == "UNCERTAIN"
        assert client.get(f"/api/actions/{accepted.action_id}", headers=owner).json()["state"] == "ACCEPTED"

        second_counts = {
            run_id: second.state.run_execution_store.get(run_id).transition_count
            for run_id in (runtime_accepted, runtime_running, action_accepted, action_running)
        }
        assert second_counts == after_transition_counts

        cases = (
            RecoveryCaseObservation(
                case_id="RR-01",
                expected_state="interrupted",
                observed_state=second.state.run_execution_store.get(runtime_accepted).state,
                transition_count_delta=after_transition_counts[runtime_accepted] - before_transition_counts[runtime_accepted],
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-02",
                expected_state="interrupted",
                observed_state=second.state.run_execution_store.get(runtime_running).state,
                transition_count_delta=after_transition_counts[runtime_running] - before_transition_counts[runtime_running],
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-03",
                expected_state="uncertain",
                observed_state=second.state.run_execution_store.get(action_accepted).state,
                transition_count_delta=after_transition_counts[action_accepted] - before_transition_counts[action_accepted],
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-04",
                expected_state="uncertain",
                observed_state=second.state.run_execution_store.get(action_running).state,
                transition_count_delta=after_transition_counts[action_running] - before_transition_counts[action_running],
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-05",
                expected_state="UNCERTAIN",
                observed_state=second.state.pending_action_custody.get_safe(executing.action_id).state,
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-06",
                expected_state="UNCERTAIN",
                observed_state=second.state.action_idempotency_ledger.get(executing_key_sha)["state"],
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-07",
                expected_state="PENDING_CONFIRMATION",
                observed_state=second.state.pending_action_custody.get_safe(pending.action_id).state,
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-08",
                expected_state="ACCEPTED/ACCEPTED",
                observed_state=(
                    second.state.pending_action_custody.get_safe(accepted.action_id).state
                    + "/"
                    + second.state.action_idempotency_ledger.get(accepted_key_sha)["state"]
                ),
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-09",
                expected_state="owner_visible_cross_tenant_hidden",
                observed_state="owner_visible_cross_tenant_hidden",
                expectation_met=True,
            ),
            RecoveryCaseObservation(
                case_id="RR-10",
                expected_state="no_additional_transitions",
                observed_state="no_additional_transitions",
                expectation_met=True,
            ),
        )

        report = build_restart_recovery_report(
            protocol,
            cases=cases,
            startup_recovered_execution_count=4,
            startup_interrupted_runtime_count=2,
            startup_uncertain_action_execution_count=2,
            startup_uncertain_custody_count=1,
            startup_uncertain_claim_count=1,
            second_startup_recovered_execution_count=0,
            second_startup_recovered_custody_count=0,
            second_startup_recovered_claim_count=0,
            transport_replay_count=len(transport_calls),
            automatic_retry_count=0,
            real_customer_mutations=0,
            authenticated_tenant_isolation_preserved=True,
            second_restart_idempotent=True,
        )
        assert report.expectations_passed == 10
        assert report.promoted_topology_recovery_contract_ready is True
        assert report.transport_replay_count == 0

        serialized = report.model_dump_json()
        for private_fragment in (
            runtime_accepted,
            runtime_running,
            action_accepted,
            action_running,
            pending.action_id,
            executing.action_id,
            accepted.action_id,
            "org-a",
            "org-b",
            "user-a",
            "identity-",
            "Synthetic restart-recovery",
        ):
            assert private_fragment not in serialized

        output_path = os.environ.get("RESTART_RECOVERY_OUTPUT")
        if output_path:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
