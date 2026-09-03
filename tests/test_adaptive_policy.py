from __future__ import annotations

from hashlib import sha256
import json

from academy_tractian.adaptive_policy import (
    AdaptiveSoftBudgetPolicyConfig,
    AdaptiveStoppingDecisionSource,
    RepeatedNonprogressSoftStopPolicy,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime
from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ControllerObservation,
    DecisionSourceAuditRecord,
    ToolProposal,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


class AuditedSource(ScriptedDecisionSource):
    def __init__(self, *decisions: ControllerDecision) -> None:
        super().__init__(*decisions)
        self.record = DecisionSourceAuditRecord(
            call_id="a" * 64,
            metadata={"outcome": "success", "turn_index": 0, "tool_call_count": 0},
        )

    def drain_audit_records(self) -> tuple[DecisionSourceAuditRecord, ...]:
        record, self.record = self.record, None  # type: ignore[assignment]
        return () if record is None else (record,)


class AlwaysFailingPolicy(RepeatedNonprogressSoftStopPolicy):
    def evaluate(self, *, context, proposed_decision):
        raise RuntimeError("private-policy-error-detail")


class FailingTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=503,
            headers={"content-type": "application/json"},
            body={"status": "unavailable"},
        )


def _tool() -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.TOOL,
        proposal=ToolProposal(
            tool_name="get_asset",
            arguments={"asset_id": "asset-1"},
            evidence_id="asset-context",
        ),
    )


def _final() -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={
            "decision": "ORIENT",
            "response_mode": "complete",
            "message": "Evidence inspected.",
        },
    )


def _context(*statuses: str, tool_call_count: int | None = None) -> ControllerContext:
    observations = tuple(
        ControllerObservation(
            tool_name=f"tool-{index}",
            status=status,  # type: ignore[arg-type]
            executed=status != "blocked",
            status_code=503 if status == "failure" else (200 if status == "success" else None),
            blocked_code="PERMISSION_DENIED" if status == "blocked" else None,
            body={"opaque": f"body-{index}"},
        )
        for index, status in enumerate(statuses)
    )
    return ControllerContext(
        user_request="Inspect the asset.",
        turn_index=len(statuses),
        tool_call_count=len(statuses) if tool_call_count is None else tool_call_count,
        observations=observations,
    )


def test_policy_config_hash_is_stable_and_changes_with_threshold() -> None:
    first = RepeatedNonprogressSoftStopPolicy()
    same = RepeatedNonprogressSoftStopPolicy()
    changed = RepeatedNonprogressSoftStopPolicy(
        AdaptiveSoftBudgetPolicyConfig(consecutive_nonprogress_limit=3)
    )

    assert first.config_sha256 == same.config_sha256
    assert len(first.config_sha256) == 64
    assert first.config_sha256 != changed.config_sha256


def test_terminal_decision_is_never_rewritten() -> None:
    terminal = _final()
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(terminal),
    )

    result = wrapped.decide(_context("failure", "blocked"))

    assert result == terminal
    record = wrapped.drain_policy_records()[0]
    assert record.proposed_kind is ControllerDecisionKind.FINAL
    assert record.outcome == "CONTINUE"


def test_tool_proposal_passes_through_before_nonprogress_threshold() -> None:
    proposal = _tool()
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(proposal),
    )

    result = wrapped.decide(_context("failure"))

    assert result == proposal
    record = wrapped.drain_policy_records()[0]
    assert record.consecutive_nonprogress == 1
    assert record.outcome == "CONTINUE"


def test_repeated_nonprogress_can_only_replace_tool_with_safe_abstain() -> None:
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(_tool()),
    )

    result = wrapped.decide(_context("failure", "blocked"))

    assert result.kind is ControllerDecisionKind.ABSTAIN
    assert result.proposal is None
    assert result.reason_code == "ADAPTIVE_SOFT_STOP_REPEATED_NONPROGRESS"
    record = wrapped.drain_policy_records()[0]
    assert record.outcome == "SAFE_ABSTAIN"
    assert record.reason_code == "REPEATED_NONPROGRESS"
    assert record.consecutive_nonprogress == 2


def test_success_resets_nonprogress_streak() -> None:
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(_tool()),
    )

    result = wrapped.decide(_context("failure", "blocked", "success"))

    assert result.kind is ControllerDecisionKind.TOOL
    record = wrapped.drain_policy_records()[0]
    assert record.consecutive_nonprogress == 0
    assert record.outcome == "CONTINUE"


def test_policy_failure_falls_back_to_exact_baseline_decision_without_error_leak() -> None:
    proposal = _tool()
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(proposal),
        policy=AlwaysFailingPolicy(),
    )

    result = wrapped.decide(_context("failure", "failure"))
    records = wrapped.drain_policy_records()

    assert result == proposal
    assert records[0].outcome == "BASELINE_FALLBACK"
    serialized = json.dumps(records[0].model_dump(mode="json"), sort_keys=True)
    assert "private-policy-error-detail" not in serialized


def test_wrapper_preserves_underlying_model_call_audit_channel() -> None:
    wrapped = AdaptiveStoppingDecisionSource(
        source=AuditedSource(_final()),
    )

    wrapped.decide(_context())
    records = wrapped.drain_audit_records()

    assert len(records) == 1
    assert records[0].call_id == "a" * 64
    assert wrapped.drain_audit_records() == ()


def test_policy_record_contains_no_observation_body_or_private_binding() -> None:
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(_tool()),
    )
    wrapped.decide(_context("failure", "blocked"))

    serialized = json.dumps(
        wrapped.drain_policy_records()[0].model_dump(mode="json"),
        sort_keys=True,
    ).lower()
    for forbidden in (
        "body-0",
        "body-1",
        "identity_id",
        "user_id",
        "seed",
        "authorization",
        "chain_of_thought",
    ):
        assert forbidden not in serialized


def test_real_controller_executes_no_third_tool_after_two_nonprogress_results() -> None:
    transport = FailingTransport()
    wrapped = AdaptiveStoppingDecisionSource(
        source=ScriptedDecisionSource(_tool(), _tool(), _tool(), _final()),
    )
    runtime = ProductionRuntime(
        decision_source=wrapped,
        transport=transport,
    )

    trace = runtime.run(
        ProductionRequest(
            request_id="adaptive-candidate-1",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect asset-1 and stop safely if evidence cannot progress.",
            seed=None,
        )
    )

    assert len(transport.calls) == 2
    final_event = next(event for event in trace.events if event.event_type == "final_response")
    assert final_event.result["decision"] == "ABSTAIN"
    assert final_event.result["reason_code"] == "ADAPTIVE_SOFT_STOP_REPEATED_NONPROGRESS"
    assert not any(
        event.event_type == "tool_call" and event.sequence > final_event.sequence
        for event in trace.events
    )


def test_policy_config_does_not_contain_hard_cap_or_authorization_controls() -> None:
    fields = set(AdaptiveSoftBudgetPolicyConfig.model_fields)
    assert fields == {
        "schema_version",
        "policy_id",
        "minimum_tool_calls_before_stop",
        "consecutive_nonprogress_limit",
    }
    assert "max_turns" not in fields
    assert "max_tool_calls" not in fields
    assert "permissions" not in fields
    assert "actions_enabled" not in fields
