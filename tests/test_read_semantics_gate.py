from __future__ import annotations

import pytest

from academy_tractian.read_semantics_gate import (
    PRODUCTION_READ_SEMANTICS_GATE_VERSION,
    ProductionReadSemanticsGate,
    ProductionReadSemanticsGateError,
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


class StaticTransport:
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return self.response


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)
        self.contexts: list[ControllerContext] = []

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.contexts.append(context)
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


def _request(request_id: str) -> ProductionRequest:
    return ProductionRequest(
        request_id=request_id,
        identity_id="read-semantics-identity",
        user_id="read-semantics-user",
        user_request="Inspect asset asset-1.",
        seed="read-semantics-seed",
    )


def _final(response_mode: str = "complete") -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={
            "decision": "ORIENT",
            "response_mode": response_mode,
            "message": "Inspection finished.",
        },
    )


def _read_runtime(response: TransportResponse) -> ProductionRuntime:
    return ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-1"},
                    evidence_id="asset-context",
                ),
            ),
            _final(),
        ),
        transport=StaticTransport(response),
    )


def test_complete_structured_read_passes_sanitized_production_gate() -> None:
    trace = _read_runtime(
        TransportResponse(
            200,
            {"content-type": "application/json"},
            {"mode": "complete", "data": {"asset_id": "asset-1"}},
        )
    ).run(_request("read-complete"))

    report = ProductionReadSemanticsGate().require(trace)

    assert report.schema_version == PRODUCTION_READ_SEMANTICS_GATE_VERSION
    assert report.passed
    assert report.read_result_count == 1
    assert report.assessed_result_count == 1
    assert report.contract_issue_count == 0
    assert report.mode_counts["complete"] == 1
    assert report.entries[0].response_mode == "complete"
    assert report.entries[0].source == "structured_mode"
    assert report.raw_response_recorded is False
    assert report.trace_mutated is False
    assert "asset_id" not in report.model_dump_json()


def test_partial_and_conflict_remain_distinct_valid_read_states() -> None:
    gate = ProductionReadSemanticsGate()

    partial = _read_runtime(
        TransportResponse(200, {}, {"mode": "partial", "data": {"coverage": 0.4}})
    ).run(_request("read-partial"))
    conflict = _read_runtime(
        TransportResponse(200, {}, {"mode": "conflict", "data": {"sources": 2}})
    ).run(_request("read-conflict"))

    partial_report = gate.require(partial)
    conflict_report = gate.require(conflict)

    assert partial_report.entries[0].response_mode == "partial"
    assert conflict_report.entries[0].response_mode == "conflict"
    assert partial_report.mode_counts["partial"] == 1
    assert conflict_report.mode_counts["conflict"] == 1


def test_non_2xx_is_valid_unavailable_state_not_a_contract_drift() -> None:
    trace = _read_runtime(
        TransportResponse(503, {}, {"mode": "complete", "message": "upstream unavailable"})
    ).run(_request("read-unavailable"))

    report = ProductionReadSemanticsGate().require(trace)

    assert report.passed
    assert report.entries[0].response_mode == "unavailable"
    assert report.entries[0].source == "http_status"
    assert report.entries[0].issue_code is None
    assert report.mode_counts["unavailable"] == 1


def test_missing_structured_mode_fails_acceptance_without_leaking_raw_body() -> None:
    secret_marker = "TOP-SECRET-READ-BODY"
    trace = _read_runtime(
        TransportResponse(200, {}, {"message": secret_marker, "data": {"value": 7}})
    ).run(_request("read-missing-mode"))

    report = ProductionReadSemanticsGate().evaluate(trace)

    assert not report.passed
    assert report.contract_issue_count == 1
    assert report.entries[0].response_mode == "inconclusive"
    assert report.entries[0].source == "fail_closed"
    assert report.entries[0].issue_code == "MISSING_MODE"
    assert secret_marker not in report.model_dump_json()

    with pytest.raises(ProductionReadSemanticsGateError) as captured:
        ProductionReadSemanticsGate().require(trace)
    assert secret_marker not in str(captured.value)
    assert "contract_issues=1" in str(captured.value)


def test_terminal_only_trace_is_vacuously_valid_for_semantic_contract() -> None:
    runtime = ProductionRuntime(
        decision_source=ScriptedDecisionSource(_final()),
        transport=StaticTransport(TransportResponse(500, {}, {})),
    )
    trace = runtime.run(_request("read-none"))

    report = ProductionReadSemanticsGate().require(trace)

    assert report.passed
    assert report.read_result_count == 0
    assert report.assessed_result_count == 0
    assert report.contract_issue_count == 0
