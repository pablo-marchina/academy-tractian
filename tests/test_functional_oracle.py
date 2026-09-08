from __future__ import annotations

from research.e2.models import ResponseMode, RunTrace, TraceEvent

from academy_tractian.functional_oracle import (
    EvidenceRequirementSpec,
    FunctionalCaseSpec,
    RequiredToolGroup,
    ToolResourceRequirement,
    evaluate_evidence_trace,
    evaluate_functional_trace,
)


def _event(sequence: int, event_type: str, **kwargs):
    return TraceEvent(sequence=sequence, event_type=event_type, **kwargs)


def _trace(events: list[TraceEvent]) -> RunTrace:
    return RunTrace(
        run_id="run_fixture",
        scenario_id="prod:fixture",
        config_hash="a" * 64,
        identity_binding_id="identity_fixture",
        seed_ref="none",
        events=events,
    )


def _successful_bilateral_trace() -> RunTrace:
    return _trace(
        [
            _event(0, "run_started"),
            _event(1, "tool_call", call_id="c1", tool_name="get_current_user", arguments={}),
            _event(2, "tool_result", call_id="c1", tool_name="get_current_user", metadata={"status_code": 200}),
            _event(3, "tool_call", call_id="c2", tool_name="list_assets_by_company", arguments={"company_id": "comp_alpha"}),
            _event(4, "tool_result", call_id="c2", tool_name="list_assets_by_company", metadata={"status_code": 200}),
            _event(5, "tool_call", call_id="c3", tool_name="get_rms", arguments={"asset_id": "asset_A"}),
            _event(6, "tool_result", call_id="c3", tool_name="get_rms", metadata={"status_code": 200}),
            _event(7, "tool_call", call_id="c4", tool_name="get_spectrum", arguments={"asset_id": "asset_B"}),
            _event(8, "tool_result", call_id="c4", tool_name="get_spectrum", metadata={"status_code": 200}),
            _event(
                9,
                "final_response",
                result={"decision": "ORIENT", "response_mode": "complete", "reason_code": None, "message": "A requires attention before B."},
            ),
            _event(10, "run_finished"),
        ]
    )


def _bilateral_functional_spec() -> FunctionalCaseSpec:
    return FunctionalCaseSpec(
        case_id="BILATERAL-01",
        required_tool_groups=(
            RequiredToolGroup(group_id="identity", tools=("get_current_user",)),
            RequiredToolGroup(group_id="fleet", tools=("list_assets_by_company",)),
            RequiredToolGroup(group_id="condition", tools=("get_rms", "get_spectrum", "get_analysis"), minimum_satisfied=1),
        ),
        required_resources=(
            ToolResourceRequirement(requirement_id="asset_a", tools=("get_rms", "get_spectrum", "get_analysis"), resource_id="asset_A"),
            ToolResourceRequirement(requirement_id="asset_b", tools=("get_rms", "get_spectrum", "get_analysis"), resource_id="asset_B"),
        ),
        allowed_response_modes=(ResponseMode.COMPLETE, ResponseMode.PARTIAL),
        minimum_tool_calls=4,
    )


def test_independent_functional_oracle_accepts_multiple_valid_condition_tools() -> None:
    report = evaluate_functional_trace(_successful_bilateral_trace(), _bilateral_functional_spec())
    assert report.status == "VERIFIED"
    assert report.failures == ()
    assert report.tool_calls == 4


def test_independent_functional_oracle_rejects_one_sided_comparison() -> None:
    trace = _successful_bilateral_trace()
    events = [event for event in trace.events if event.call_id != "c4"]
    events = [event.model_copy(update={"sequence": i}) for i, event in enumerate(events)]
    report = evaluate_functional_trace(_trace(events), _bilateral_functional_spec())
    assert report.status == "FAILED"
    assert "MISSING_RESOURCE:asset_b" in report.failures


def test_independent_functional_oracle_rejects_safe_runtime_failure() -> None:
    trace = _trace(
        [
            _event(0, "run_started"),
            _event(
                1,
                "final_response",
                result={
                    "decision": "ABSTAIN",
                    "response_mode": "unavailable",
                    "reason_code": "TOOL_CALL_BUDGET_EXHAUSTED",
                    "message": "Budget exhausted.",
                },
            ),
            _event(2, "run_finished"),
        ]
    )
    report = evaluate_functional_trace(trace, _bilateral_functional_spec())
    assert report.status == "FAILED"
    assert "FORBIDDEN_TERMINAL_REASON:TOOL_CALL_BUDGET_EXHAUSTED" in report.failures


def test_evidence_oracle_requires_successful_condition_evidence_for_each_asset() -> None:
    trace = _successful_bilateral_trace()
    spec = EvidenceRequirementSpec(
        requirement_id="bilateral-condition",
        required_tool_groups=(
            RequiredToolGroup(group_id="condition", tools=("get_rms", "get_spectrum", "get_analysis"), minimum_satisfied=1),
        ),
        required_resources=(
            ToolResourceRequirement(requirement_id="asset_a", tools=("get_rms", "get_spectrum", "get_analysis"), resource_id="asset_A"),
            ToolResourceRequirement(requirement_id="asset_b", tools=("get_rms", "get_spectrum", "get_analysis"), resource_id="asset_B"),
        ),
    )
    report = evaluate_evidence_trace(trace, spec)
    assert report.status == "VERIFIED"


def test_evidence_oracle_does_not_accept_failed_required_tool_as_evidence() -> None:
    trace = _trace(
        [
            _event(0, "run_started"),
            _event(1, "tool_call", call_id="c1", tool_name="get_rms", arguments={"asset_id": "asset_A"}),
            _event(2, "tool_result", call_id="c1", tool_name="get_rms", metadata={"status_code": 500}),
            _event(3, "final_response", result={"decision": "ORIENT", "response_mode": "unavailable", "reason_code": None, "message": "Unavailable"}),
            _event(4, "run_finished"),
        ]
    )
    spec = EvidenceRequirementSpec(
        requirement_id="condition-a",
        required_tool_groups=(RequiredToolGroup(group_id="condition", tools=("get_rms",)),),
        required_resources=(ToolResourceRequirement(requirement_id="asset_a", tools=("get_rms",), resource_id="asset_A"),),
    )
    report = evaluate_evidence_trace(trace, spec)
    assert report.status == "FAILED"
    assert "MISSING_EVIDENCE_GROUP:condition" in report.failures
    assert "MISSING_EVIDENCE_RESOURCE:asset_a" in report.failures
