from __future__ import annotations

from threading import Barrier, Thread

import pytest

from research.e2.controller import ControllerDecision, ControllerDecisionKind, ControllerContext, ToolProposal
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.action_safety import ResourceCompanyBinding, action_fingerprint
from academy_tractian.observability_store import ObservabilityStore
from academy_tractian.production_actions_v2 import (
    ActionProposalRealtimeProductionRuntime,
    DuckDBActionIdempotencyLedger,
    PendingActionCustody,
    ProductionActionExecutor,
    ProductionActionPrincipal,
)
from academy_tractian.realtime_observability import DuckDBObservabilityEventSink
from academy_tractian.runtime import ProductionRequest, canonical_tool_registry


ACTION_ARGS = {
    "analysis_id": "analysis-1",
    "body": {
        "justification": "Evidence reviewed and operator confirmation is required before this exact reprocessing action."
    },
}


class ScriptedSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


class FakeTransport:
    def __init__(self, *, accepted: bool = True, explode: bool = False) -> None:
        self.accepted = accepted
        self.explode = explode
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        if self.explode:
            raise RuntimeError("ambiguous transport failure")
        return TransportResponse(
            status_code=202,
            headers={"content-type": "application/json"},
            body={"accepted": self.accepted},
        )


def _principal(*, permissions: frozenset[Permission] | None = None, company: str = "company-1") -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id="user-1",
        user_company_id="company-1",
        permissions=permissions if permissions is not None else frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="analysis-1", company_id=company),
        ),
    )


def _resolver(principal: ProductionActionPrincipal):
    def resolve(*, user_id: str) -> ProductionActionPrincipal:
        assert user_id == principal.user_id
        return principal
    return resolve


def _proposal_runtime(tmp_path, *, principal: ProductionActionPrincipal, transport: FakeTransport, custody: PendingActionCustody):
    store = ObservabilityStore(tmp_path / "observability.duckdb")
    sink = DuckDBObservabilityEventSink(store)
    source = ScriptedSource(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="reprocess_analysis",
                arguments=ACTION_ARGS,
                evidence_id="EV-action-proposal",
            ),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "partial",
                "message": "Action requires explicit operator confirmation.",
            },
        ),
    )
    return ActionProposalRealtimeProductionRuntime(
        decision_source=source,
        transport=transport,
        observability_sink=sink,
        authorization_resolver=_resolver(principal),
        custody=custody,
    ), store


def _request() -> ProductionRequest:
    return ProductionRequest(
        request_id="req-action-v2-1",
        identity_id="identity-1",
        user_id="user-1",
        user_request="Reprocess analysis-1 if authorized.",
    )


def test_valid_action_proposal_is_custodied_but_never_executes_transport(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "private-actions.duckdb")
    transport = FakeTransport()
    runtime, store = _proposal_runtime(
        tmp_path,
        principal=_principal(),
        transport=transport,
        custody=custody,
    )

    trace = runtime.run(_request())
    assert transport.calls == []
    safe_run_id = store.list_runs(limit=10)[0]["run_id"]
    pending = custody.list_safe_for_origin(str(safe_run_id))
    assert len(pending) == 1
    item = pending[0]
    assert item.state == "PENDING_CONFIRMATION"
    assert item.tool_name == "reprocess_analysis"
    assert item.impact == "low"
    assert item.required_permissions == ("action_low",)
    assert item.confirmation_required is True
    assert ACTION_ARGS["body"]["justification"] not in item.model_dump_json()

    b2 = [event for event in trace.events if event.event_type == "policy_check"]
    assert len(b2) == 1
    assert b2[0].metadata["allowed"] is False
    assert b2[0].metadata["violation"] == "CONFIRMATION_REQUIRED"


def test_permission_or_scope_failure_creates_no_pending_action(tmp_path) -> None:
    for suffix, principal, expected in (
        ("permission", _principal(permissions=frozenset()), "PERMISSION_DENIED"),
        ("scope", _principal(company="company-2"), "RESOURCE_SCOPE_DENIED"),
    ):
        custody = PendingActionCustody(tmp_path / f"private-{suffix}.duckdb")
        runtime, store = _proposal_runtime(
            tmp_path / suffix,
            principal=principal,
            transport=FakeTransport(),
            custody=custody,
        )
        trace = runtime.run(_request().model_copy(update={"request_id": f"req-{suffix}"}))
        safe_id = store.list_runs(limit=10)[0]["run_id"]
        assert custody.list_safe_for_origin(str(safe_id)) == []
        checks = [event for event in trace.events if event.event_type == "policy_check"]
        assert checks[0].metadata["violation"] == expected


def test_operator_confirmation_executes_exact_custodied_action_once(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "private-actions.duckdb")
    proposal_transport = FakeTransport()
    proposal_runtime, store = _proposal_runtime(
        tmp_path,
        principal=_principal(),
        transport=proposal_transport,
        custody=custody,
    )
    proposal_runtime.run(_request())
    origin_run_id = str(store.list_runs(limit=10)[0]["run_id"])
    pending = custody.list_safe_for_origin(origin_run_id)[0]

    ledger = DuckDBActionIdempotencyLedger(tmp_path / "action-ledger.duckdb")
    action_transport = FakeTransport(accepted=True)
    executor = ProductionActionExecutor(
        custody=custody,
        ledger=ledger,
        authorization_resolver=_resolver(_principal()),
        transport_factory=lambda: action_transport,
        observability_sink=DuckDBObservabilityEventSink(store),
        actions_enabled=True,
    )

    execution_run_id, prepared = executor.prepare_confirmed(
        action_id=pending.action_id,
        identity_id="identity-1",
        requester_user_id="user-1",
    )
    trace = prepared.execute()
    assert execution_run_id == custody.get_safe(pending.action_id).execution_run_id
    assert len(action_transport.calls) == 1
    assert action_transport.calls[0].path.endswith("/analyses/analysis-1/reprocess")
    assert custody.get_safe(pending.action_id).state == "ACCEPTED"
    final = [event for event in trace.events if event.event_type == "final_response"][-1]
    assert final.result["reason_code"] == "ACTION_ACCEPTED"

    fingerprint = action_fingerprint(canonical_tool_registry()["reprocess_analysis"], ACTION_ARGS)
    private = custody.get_private_for_requester(action_id=pending.action_id, requester_user_id="user-1")
    key_hash = __import__("hashlib").sha256(private.idempotency_key.encode("utf-8")).hexdigest()
    ledger_row = ledger.get(key_hash)
    assert ledger_row is not None
    assert ledger_row["action_fingerprint"] == fingerprint
    assert ledger_row["state"] == "ACCEPTED"

    with pytest.raises(RuntimeError, match="action_not_confirmable"):
        executor.prepare_confirmed(
            action_id=pending.action_id,
            identity_id="identity-1",
            requester_user_id="user-1",
        )
    assert len(action_transport.calls) == 1


def test_action_kill_switch_does_not_consume_pending_action(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "private-actions.duckdb")
    proposal_runtime, store = _proposal_runtime(
        tmp_path,
        principal=_principal(),
        transport=FakeTransport(),
        custody=custody,
    )
    proposal_runtime.run(_request())
    pending = custody.list_safe_for_origin(str(store.list_runs(limit=10)[0]["run_id"]))[0]
    executor = ProductionActionExecutor(
        custody=custody,
        ledger=DuckDBActionIdempotencyLedger(tmp_path / "ledger.duckdb"),
        authorization_resolver=_resolver(_principal()),
        transport_factory=lambda: FakeTransport(),
        observability_sink=DuckDBObservabilityEventSink(store),
        actions_enabled=False,
    )

    with pytest.raises(RuntimeError, match="action_kill_switch_engaged"):
        executor.prepare_confirmed(
            action_id=pending.action_id,
            identity_id="identity-1",
            requester_user_id="user-1",
        )
    assert custody.get_safe(pending.action_id).state == "PENDING_CONFIRMATION"


def test_ambiguous_transport_failure_keeps_persistent_claim_and_forbids_retry(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "private-actions.duckdb")
    proposal_runtime, store = _proposal_runtime(
        tmp_path,
        principal=_principal(),
        transport=FakeTransport(),
        custody=custody,
    )
    proposal_runtime.run(_request())
    pending = custody.list_safe_for_origin(str(store.list_runs(limit=10)[0]["run_id"]))[0]
    ledger_path = tmp_path / "ledger.duckdb"
    ledger = DuckDBActionIdempotencyLedger(ledger_path)
    exploding = FakeTransport(explode=True)
    executor = ProductionActionExecutor(
        custody=custody,
        ledger=ledger,
        authorization_resolver=_resolver(_principal()),
        transport_factory=lambda: exploding,
        observability_sink=DuckDBObservabilityEventSink(store),
        actions_enabled=True,
    )
    _, prepared = executor.prepare_confirmed(
        action_id=pending.action_id,
        identity_id="identity-1",
        requester_user_id="user-1",
    )
    trace = prepared.execute()
    assert len(exploding.calls) == 1
    assert custody.get_safe(pending.action_id).state == "UNCERTAIN"
    assert [event for event in trace.events if event.event_type == "final_response"][-1].result["reason_code"] == "ACTION_EXECUTION_UNCERTAIN"

    private = custody.get_private_for_requester(action_id=pending.action_id, requester_user_id="user-1")
    key_hash = __import__("hashlib").sha256(private.idempotency_key.encode("utf-8")).hexdigest()
    restarted_ledger = DuckDBActionIdempotencyLedger(ledger_path)
    assert restarted_ledger.get(key_hash)["state"] == "UNCERTAIN"  # type: ignore[index]
    assert restarted_ledger.claim(
        key_sha256=key_hash,
        action_fingerprint=pending.action_fingerprint,
        action_id=pending.action_id,
    ) is False


def test_wrong_requester_cannot_confirm_pending_action(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "private-actions.duckdb")
    proposal_runtime, store = _proposal_runtime(
        tmp_path,
        principal=_principal(),
        transport=FakeTransport(),
        custody=custody,
    )
    proposal_runtime.run(_request())
    pending = custody.list_safe_for_origin(str(store.list_runs(limit=10)[0]["run_id"]))[0]
    executor = ProductionActionExecutor(
        custody=custody,
        ledger=DuckDBActionIdempotencyLedger(tmp_path / "ledger.duckdb"),
        authorization_resolver=_resolver(_principal()),
        transport_factory=lambda: FakeTransport(),
        observability_sink=DuckDBObservabilityEventSink(store),
        actions_enabled=True,
    )
    with pytest.raises(PermissionError, match="action_requester_mismatch"):
        executor.prepare_confirmed(
            action_id=pending.action_id,
            identity_id="identity-other",
            requester_user_id="user-other",
        )


def test_persistent_ledger_allows_exactly_one_concurrent_claim(tmp_path) -> None:
    ledger = DuckDBActionIdempotencyLedger(tmp_path / "ledger.duckdb")
    barrier = Barrier(3)
    outcomes: list[bool] = []

    def claim() -> None:
        barrier.wait()
        outcomes.append(
            ledger.claim(
                key_sha256="a" * 64,
                action_fingerprint="b" * 64,
                action_id="act-concurrent",
            )
        )

    threads = [Thread(target=claim), Thread(target=claim)]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join(timeout=5)
    assert sorted(outcomes) == [False, True]
