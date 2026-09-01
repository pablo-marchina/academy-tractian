from __future__ import annotations

from academy_tractian.escalation_handoff import (
    REVIEWER_INSTRUCTION,
    build_escalation_handoff,
    evaluate_escalation_handoff,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime
from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
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


class RecordingTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body={
                "asset_id": "asset-1",
                "status": "inconclusive",
                "internal_payload": "must-not-enter-handoff",
            },
        )


def _request() -> ProductionRequest:
    return ProductionRequest(
        request_id="handoff-req-1",
        identity_id="identity-private",
        user_id="user-private",
        user_request="Determine whether asset-1 can be safely reprocessed.",
        seed="seed-private",
    )


def _escalate(*, reason: str = "HUMAN_REVIEW_REQUIRED") -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.ESCALATE,
        message="Human review is required because the request remains unresolved.",
        reason_code=reason,
    )


def test_escalation_before_tools_builds_explicit_no_evidence_handoff() -> None:
    request = _request()
    trace = ProductionRuntime(
        decision_source=ScriptedDecisionSource(_escalate()),
        transport=RecordingTransport(),
    ).run(request)

    handoff = build_escalation_handoff(request=request, trace=trace)
    assert handoff is not None
    assert handoff.request_id == request.request_id
    assert handoff.unresolved_request == request.user_request
    assert handoff.reason_code == "HUMAN_REVIEW_REQUIRED"
    assert handoff.evidence_state == "NONE_COLLECTED"
    assert handoff.evidence_references == ()
    assert handoff.reviewer_instruction == REVIEWER_INSTRUCTION

    evaluation = evaluate_escalation_handoff(
        request=request,
        trace=trace,
        handoff=handoff,
    )
    assert evaluation.applicable is True
    assert evaluation.passed is True
    assert evaluation.evidence_reference_count == 0


def test_escalation_after_observation_references_exact_trace_evidence_without_raw_body() -> None:
    request = _request()
    transport = RecordingTransport()
    trace = ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-1"},
                    evidence_id="asset-evidence",
                ),
            ),
            _escalate(reason="SOURCE_UNAVAILABLE"),
        ),
        transport=transport,
    ).run(request)

    assert len(transport.calls) == 1
    handoff = build_escalation_handoff(request=request, trace=trace)
    assert handoff is not None
    assert handoff.evidence_state == "COLLECTED"
    assert len(handoff.evidence_references) == 1
    ref = handoff.evidence_references[0]
    observation = next(event for event in trace.events if event.event_type == "observation")
    assert ref.sequence == observation.sequence
    assert ref.tool_name == "get_asset"
    assert len(ref.result_sha256) == 64

    serialized = handoff.model_dump_json()
    assert "internal_payload" not in serialized
    assert "must-not-enter-handoff" not in serialized
    assert "identity-private" not in serialized
    assert "user-private" not in serialized
    assert "seed-private" not in serialized

    evaluation = evaluate_escalation_handoff(
        request=request,
        trace=trace,
        handoff=handoff,
    )
    assert evaluation.passed is True
    assert evaluation.evidence_reference_count == 1


def test_missing_handoff_fails_for_escalation() -> None:
    request = _request()
    trace = ProductionRuntime(
        decision_source=ScriptedDecisionSource(_escalate()),
        transport=RecordingTransport(),
    ).run(request)

    evaluation = evaluate_escalation_handoff(
        request=request,
        trace=trace,
        handoff=None,
    )
    assert evaluation.applicable is True
    assert evaluation.passed is False
    assert evaluation.violations == ("MISSING_ESCALATION_HANDOFF",)


def test_tampered_handoff_fails_exact_binding() -> None:
    request = _request()
    trace = ProductionRuntime(
        decision_source=ScriptedDecisionSource(_escalate()),
        transport=RecordingTransport(),
    ).run(request)
    handoff = build_escalation_handoff(request=request, trace=trace)
    assert handoff is not None

    other_request = request.model_copy(update={"request_id": "different-request"})
    evaluation = evaluate_escalation_handoff(
        request=other_request,
        trace=trace,
        handoff=handoff,
    )
    assert evaluation.passed is False
    assert "REQUEST_ID_MISMATCH" in evaluation.violations


def test_non_escalation_is_not_applicable_and_emits_no_handoff() -> None:
    request = _request()
    trace = ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final={
                    "decision": "ORIENT",
                    "response_mode": "complete",
                    "message": "No escalation is required.",
                },
            )
        ),
        transport=RecordingTransport(),
    ).run(request)

    handoff = build_escalation_handoff(request=request, trace=trace)
    assert handoff is None
    evaluation = evaluate_escalation_handoff(
        request=request,
        trace=trace,
        handoff=handoff,
    )
    assert evaluation.applicable is False
    assert evaluation.passed is True
