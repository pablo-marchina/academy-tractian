from __future__ import annotations

import pytest

from academy_tractian.mode_acceptance_gate import (
    ProductionAgentModeGate,
    ProductionAgentModeGateError,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime
from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest, Decision, TraceEvent
from research.e2.transport import TransportResponse


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("mode acceptance script exhausted")
        return self.decisions.pop(0)


class StructuredTransport:
    def __init__(
        self,
        *,
        mode: str = "complete",
        status_code: int = 200,
        include_mode: bool = True,
        sensitive_value: str = "raw-upstream-sensitive-marker",
    ) -> None:
        self.mode = mode
        self.status_code = status_code
        self.include_mode = include_mode
        self.sensitive_value = sensitive_value
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        body = {"asset_id": "asset-mode", "private_payload": self.sensitive_value}
        if self.include_mode:
            body["mode"] = self.mode
        return TransportResponse(
            status_code=self.status_code,
            headers={"content-type": "application/json"},
            body=body,
        )


def _request(*, request_id: str = "mode-req-1") -> ProductionRequest:
    return ProductionRequest(
        request_id=request_id,
        identity_id="mode-identity-private",
        user_id="mode-user-private",
        user_request="request-sensitive-marker: inspect asset-mode safely",
        seed="mode-seed-private",
    )


def _final(
    *,
    decision: str,
    response_mode: str,
    message: str = "A bounded terminal response was produced.",
    reason_code: str | None = None,
) -> ControllerDecision:
    payload: dict[str, object] = {
        "decision": decision,
        "response_mode": response_mode,
        "message": message,
    }
    if reason_code is not None:
        payload["reason_code"] = reason_code
    return ControllerDecision(kind=ControllerDecisionKind.FINAL, final=payload)


def _run(
    *decisions: ControllerDecision,
    transport: StructuredTransport | None = None,
    request: ProductionRequest | None = None,
):
    actual_request = request or _request()
    actual_transport = transport or StructuredTransport()
    trace = ProductionRuntime(
        decision_source=ScriptedDecisionSource(*decisions),
        transport=actual_transport,
    ).run(actual_request)
    return actual_request, actual_transport, trace


def _read_then(final: ControllerDecision) -> tuple[ControllerDecision, ControllerDecision]:
    return (
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="get_asset",
                arguments={"asset_id": "asset-mode"},
                evidence_id="mode-evidence",
            ),
        ),
        final,
    )


def test_contextualize_accepts_valid_terminal_without_forcing_a_tool_call() -> None:
    request, transport, trace = _run(
        _final(decision=Decision.ORIENT.value, response_mode="complete")
    )

    report = ProductionAgentModeGate().require(request=request, trace=trace)

    assert transport.calls == []
    assert report.passed is True
    assert report.agent_mode == "CONTEXTUALIZE"
    assert report.applicable_to_required_modes is True
    assert report.read_result_count == 0
    assert report.violations == ()


def test_investigate_requires_and_accepts_a_canonical_read_with_structured_mode() -> None:
    request, transport, trace = _run(
        *_read_then(
            _final(
                decision=Decision.INVESTIGATE.value,
                response_mode="partial",
                message="Investigation remains open after one bounded read.",
            )
        ),
        transport=StructuredTransport(mode="partial"),
    )

    report = ProductionAgentModeGate().require(request=request, trace=trace)

    assert len(transport.calls) == 1
    assert report.agent_mode == "INVESTIGATE"
    assert report.read_result_count == 1
    assert report.read_contract_issue_count == 0
    assert report.read_mode_counts["partial"] == 1


@pytest.mark.parametrize(
    ("decision", "expected_mode", "expected_response_mode"),
    (
        (
            ControllerDecision(
                kind=ControllerDecisionKind.CLARIFY,
                message="Which asset should be inspected?",
                reason_code="MISSING_ASSET",
            ),
            "CLARIFY",
            "partial",
        ),
        (
            ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                message="The evidence is unavailable, so execution stops safely.",
                reason_code="SOURCE_UNAVAILABLE",
            ),
            "ABSTAIN",
            "unavailable",
        ),
    ),
)
def test_controller_generated_clarify_and_abstain_preserve_noncomplete_modes(
    decision: ControllerDecision,
    expected_mode: str,
    expected_response_mode: str,
) -> None:
    request, _, trace = _run(decision)

    report = ProductionAgentModeGate().require(request=request, trace=trace)

    assert report.agent_mode == expected_mode
    assert report.terminal_response_mode == expected_response_mode
    assert report.violations == ()


def test_escalate_requires_exact_sanitized_handoff_binding() -> None:
    request, _, trace = _run(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="get_asset",
                arguments={"asset_id": "asset-mode"},
                evidence_id="conflicting-evidence",
            ),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.ESCALATE,
            message="Human review is required because the source remains conflicting.",
            reason_code="CONFLICT_UNRESOLVED",
        ),
        transport=StructuredTransport(mode="conflict"),
    )

    report = ProductionAgentModeGate().require(request=request, trace=trace)

    assert report.agent_mode == "ESCALATE"
    assert report.terminal_response_mode == "partial"
    assert report.read_mode_counts["conflict"] == 1
    assert report.escalation_handoff_applicable is True
    assert report.escalation_handoff_passed is True
    assert report.escalation_evidence_reference_count == 1


@pytest.mark.parametrize(
    "decision",
    (
        Decision.ACT_REPROCESS,
        Decision.ACT_REQUEST_SPECIALIST,
        Decision.ACT_UPDATE_CONFIG,
        Decision.ACT_REQUEST_RETRAINING,
    ),
)
def test_action_terminals_are_explicitly_deferred_to_later_gate(decision: Decision) -> None:
    request, _, trace = _run(
        _final(decision=decision.value, response_mode="complete")
    )

    report = ProductionAgentModeGate().require(request=request, trace=trace)

    assert report.agent_mode == "EXECUTION_DEFERRED"
    assert report.applicable_to_required_modes is False
    assert report.violations == ()


def test_unknown_terminal_decision_fails_closed() -> None:
    request, _, trace = _run(
        _final(decision="INVENTED_MODE", response_mode="complete")
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert report.passed is False
    assert report.agent_mode == "UNKNOWN"
    assert "TERMINAL_DECISION_UNKNOWN" in report.violations


def test_unknown_terminal_response_mode_fails_closed() -> None:
    request, _, trace = _run(
        _final(decision=Decision.ORIENT.value, response_mode="definitely-complete")
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert report.passed is False
    assert "TERMINAL_RESPONSE_MODE_UNKNOWN" in report.violations


def test_uncertainty_control_terminal_cannot_claim_complete() -> None:
    request, _, trace = _run(
        _final(
            decision=Decision.ASK_CLARIFICATION.value,
            response_mode="complete",
            reason_code="MISSING_CONTEXT",
        )
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert report.passed is False
    assert "CONTROL_TERMINAL_CANNOT_CLAIM_COMPLETE" in report.violations


def test_control_terminal_requires_nonempty_message_and_reason_code() -> None:
    request, _, trace = _run(
        _final(
            decision=Decision.ABSTAIN.value,
            response_mode="unavailable",
            message="   ",
        )
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert report.passed is False
    assert "TERMINAL_MESSAGE_MISSING_OR_EMPTY" in report.violations
    assert "CONTROL_TERMINAL_REASON_CODE_MISSING_OR_EMPTY" in report.violations


def test_investigate_without_canonical_read_fails_closed() -> None:
    request, _, trace = _run(
        _final(decision=Decision.INVESTIGATE.value, response_mode="inconclusive")
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert report.passed is False
    assert report.read_result_count == 0
    assert "INVESTIGATE_REQUIRES_CANONICAL_READ" in report.violations


def test_malformed_read_semantics_blocks_mode_acceptance_without_reclassifying_it() -> None:
    request, _, trace = _run(
        *_read_then(
            _final(decision=Decision.INVESTIGATE.value, response_mode="inconclusive")
        ),
        transport=StructuredTransport(include_mode=False),
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert report.passed is False
    assert report.read_result_count == 1
    assert report.read_contract_issue_count == 1
    assert report.read_mode_counts["inconclusive"] == 1
    assert "READ_SEMANTICS_CONTRACT_FAILED" in report.violations


def test_blocked_action_cannot_be_forged_into_investigation_evidence() -> None:
    request, transport, trace = _run(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="reprocess_analysis",
                arguments={
                    "analysis_id": "analysis-mode",
                    "body": {"justification": "This is intentionally blocked in the read-only runtime."},
                },
            ),
        ),
        _final(decision=Decision.INVESTIGATE.value, response_mode="inconclusive"),
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=trace)

    assert transport.calls == []
    assert report.read_result_count == 0
    assert report.passed is False
    assert "INVESTIGATE_REQUIRES_CANONICAL_READ" in report.violations


def test_report_excludes_raw_upstream_body_request_identity_seed_and_terminal_message() -> None:
    request, _, trace = _run(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="get_asset",
                arguments={"asset_id": "asset-mode"},
                evidence_id="sanitized-evidence",
            ),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.ESCALATE,
            message="Human review is required for this conflicting result.",
            reason_code="CONFLICT_UNRESOLVED",
        ),
        transport=StructuredTransport(
            mode="conflict",
            sensitive_value="raw-upstream-sensitive-marker",
        ),
    )

    report = ProductionAgentModeGate().require(request=request, trace=trace)
    serialized = report.model_dump_json()

    for forbidden in (
        "raw-upstream-sensitive-marker",
        "request-sensitive-marker",
        "mode-identity-private",
        "mode-user-private",
        "mode-seed-private",
        "Human review is required for this conflicting result.",
    ):
        assert forbidden not in serialized
    assert report.raw_response_recorded is False
    assert report.terminal_message_recorded is False
    assert report.trace_mutated is False


def test_unknown_tool_result_in_tampered_trace_fails_closed() -> None:
    request, _, trace = _run(
        _final(decision=Decision.ORIENT.value, response_mode="complete")
    )
    forged = TraceEvent(
        sequence=1,
        event_type="tool_result",
        tool_name="forged_read_tool",
        result={"status_code": 200, "body": {"mode": "complete"}},
    )
    events = [trace.events[0], forged, *trace.events[1:]]
    tampered = trace.model_copy(
        update={
            "events": [event.model_copy(update={"sequence": index}) for index, event in enumerate(events)]
        }
    )

    report = ProductionAgentModeGate().evaluate(request=request, trace=tampered)

    assert report.passed is False
    assert report.unknown_tool_result_count == 1
    assert "UNKNOWN_TOOL_RESULT" in report.violations


def test_invalid_trace_lifecycle_fails_closed() -> None:
    request, _, trace = _run(
        _final(decision=Decision.ORIENT.value, response_mode="complete")
    )
    tampered = trace.model_copy(update={"events": trace.events[:-1]})

    report = ProductionAgentModeGate().evaluate(request=request, trace=tampered)

    assert report.passed is False
    assert report.trace_lifecycle_issue_count > 0
    assert "TRACE_LIFECYCLE_INVALID" in report.violations


def test_require_raises_only_sanitized_gate_codes() -> None:
    request, _, trace = _run(
        _final(decision=Decision.INVESTIGATE.value, response_mode="inconclusive")
    )

    with pytest.raises(ProductionAgentModeGateError) as exc_info:
        ProductionAgentModeGate().require(request=request, trace=trace)

    text = str(exc_info.value)
    assert "INVESTIGATE_REQUIRES_CANONICAL_READ" in text
    assert "request-sensitive-marker" not in text
    assert "mode-identity-private" not in text
    assert "mode-seed-private" not in text
