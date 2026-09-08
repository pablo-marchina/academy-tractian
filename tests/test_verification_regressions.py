from __future__ import annotations

from research.e2.models import RunTrace, TraceEvent

from academy_tractian.functional_oracle import (
    EvidenceRequirementSpec,
    RequiredToolGroup,
    ToolResourceRequirement,
    evaluate_evidence_trace,
)
from academy_tractian.verification import verify_persisted_run


def _structural_green() -> list[dict[str, object]]:
    return [
        {"check_name": name, "passed": True, "blocking": True}
        for name in (
            "trace_lifecycle",
            "production_trace_identity",
            "proposal_contract_validity",
            "identity_seed_model_isolation",
            "execution_chain_integrity",
            "policy_denial_containment",
        )
    ]


def test_one_projected_401_is_not_double_counted_as_two_failed_calls() -> None:
    report = verify_persisted_run(
        run={"run_id": "run_recovered", "completed": True, "terminal_reason_code": None},
        events=[
            {"event_type": "tool_result", "tool_name": "get_current_user", "status_code": 401},
            {"event_type": "observation", "tool_name": "get_current_user", "status_code": 401},
            {"event_type": "tool_result", "tool_name": "get_current_user", "status_code": 200},
            {"event_type": "observation", "tool_name": "get_current_user", "status_code": 200},
        ],
        evaluation=_structural_green(),
    )
    availability = report.by_name()["availability"]
    assert availability.status == "VERIFIED"
    assert availability.metrics["auth_failed_calls"] == 1


def test_success_for_same_tool_on_other_asset_cannot_rehabilitate_failed_evidence() -> None:
    events = [
        TraceEvent(sequence=0, event_type="run_started"),
        TraceEvent(sequence=1, event_type="tool_call", call_id="a", tool_name="get_rms", arguments={"asset_id": "asset_A"}),
        TraceEvent(sequence=2, event_type="tool_result", call_id="a", tool_name="get_rms", metadata={"status_code": 500}),
        TraceEvent(sequence=3, event_type="tool_call", call_id="b", tool_name="get_rms", arguments={"asset_id": "asset_B"}),
        TraceEvent(sequence=4, event_type="tool_result", call_id="b", tool_name="get_rms", metadata={"status_code": 200}),
        TraceEvent(sequence=5, event_type="final_response", result={"decision": "ORIENT", "response_mode": "partial", "reason_code": None, "message": "Only B is supported."}),
        TraceEvent(sequence=6, event_type="run_finished"),
    ]
    trace = RunTrace(
        run_id="run_correlation",
        scenario_id="prod:correlation",
        config_hash="a" * 64,
        identity_binding_id="identity",
        seed_ref="none",
        events=events,
    )
    spec = EvidenceRequirementSpec(
        requirement_id="asset-a-condition",
        required_tool_groups=(RequiredToolGroup(group_id="condition", tools=("get_rms",)),),
        required_resources=(ToolResourceRequirement(requirement_id="asset_a", tools=("get_rms",), resource_id="asset_A"),),
    )
    report = evaluate_evidence_trace(trace, spec)
    assert report.status == "FAILED"
    assert "MISSING_EVIDENCE_RESOURCE:asset_a" in report.failures
