from datetime import datetime, timezone

import pytest

from research.e2.action_gate import EvidenceAwareActionGate
from research.e2.evaluator_extensions import ArgumentEvaluator, ConclusionEvaluator, EscalationHandoffEvaluator
from research.e2.models import (
    ActionOracle,
    AgentCase,
    BoundContext,
    ConclusionOracle,
    Decision,
    DecisionOracle,
    EnvironmentSpec,
    EvaluationSpec,
    ExecutionBinding,
    EvidenceGroup,
    EvidenceOracle,
    EvidenceRequirement,
    Permission,
    PolicyOracle,
    Provenance,
    Scenario,
    ScenarioInput,
    ToolKind,
    ToolParameter,
    ToolSpec,
    TraceEvent,
    TrajectoryOracle,
    RunTrace,
)
from research.e2.policy import ResourcePolicy
from research.e2.tool_registry import get_tool
from research.e2.trace_normalize import normalize_trace
from research.e2.transport import build_b0_request


def make_scenario(*, escalate: bool = False, required_action: str | None = None) -> Scenario:
    return Scenario(
        scenario_id="CEN-01",
        title="fixture",
        ticket_ids=["TKT-INV-04"],
        split_group_id="asset_G501",
        provenance=Provenance(review_status="APPROVED", benchmark_authoritative=True),
        input=ScenarioInput(cases=[AgentCase(id="case", ticket_id="TKT-INV-04", company_id="comp_a", user_id="usr_a", asset_id="asset_a", message="x")]),
        bound_context=BoundContext(user_ids=["usr_a"], company_ids=["comp_a"], asset_ids=["asset_a"]),
        environment=EnvironmentSpec(),
        decision_oracle=DecisionOracle(required=[Decision.ESCALATE_HUMAN] if escalate else [], acceptable=[]),
        policy_oracle=PolicyOracle(required_permissions=[Permission.ACTION_HIGH]),
        evidence_oracle=EvidenceOracle(required_groups=[EvidenceGroup(group_id="g", requirements=[EvidenceRequirement(source="data_quality", predicate="gap", required_before_action=True)])]),
        action_oracle=ActionOracle(execution_expectation="required", success_semantics="accepted_event", post_action_read_semantics="diagnostic_only", required_action=required_action, target_resource="asset_a") if required_action else None,
        conclusion_oracle=ConclusionOracle(required_facts=["fact_a"], forbidden_claims=["claim_bad"], source_resolution_text="fixture"),
        trajectory_oracle=TrajectoryOracle(),
        evaluation=EvaluationSpec(p1_success_source="fixture"),
    )


def test_b0_request_binds_path_query_identity_and_seed():
    tool = get_tool("get_asset")
    request = build_b0_request(tool, {"asset_id": "asset_A/1"}, ExecutionBinding(identity_id="run", user_id="usr_a", seed="CEN-01"))
    assert request.path == "/assets/asset_A%2F1"
    assert request.query == {"seed": "CEN-01"}
    assert request.headers["x-user-id"] == "usr_a"


def test_b0_does_not_send_seed_to_actions():
    tool = get_tool("reprocess_analysis")
    request = build_b0_request(tool, {"analysis_id": "an_1", "body": {"justification": "justification long enough"}}, ExecutionBinding(identity_id="run", user_id="usr_a", seed="CEN-01"))
    assert request.query == {}


def test_b0_rejects_model_controlled_identity_and_unknown_arguments():
    tool = get_tool("get_asset")
    with pytest.raises(ValueError, match="model-controlled"):
        build_b0_request(tool, {"asset_id": "asset_a", "user_id": "usr_bad"}, ExecutionBinding(identity_id="run", user_id="usr_a"))
    with pytest.raises(ValueError, match="unknown arguments"):
        build_b0_request(tool, {"asset_id": "asset_a", "banana": 1}, ExecutionBinding(identity_id="run", user_id="usr_a"))


def test_action_gate_blocks_missing_required_evidence():
    scenario = make_scenario(required_action="reprocess_analysis")
    tool = get_tool("reprocess_analysis")
    policy = ResourcePolicy(user_permissions={Permission.ACTION_LOW}, user_company_id="comp_a", resource_company_lookup={"an_1": "comp_a"})
    gate = EvidenceAwareActionGate(policy)
    decision = gate.check(scenario=scenario, tool=tool, arguments={"analysis_id": "an_1", "body": {"justification": "justification long enough"}}, trace=[])
    assert not decision.allowed and decision.code == "EVIDENCE_INSUFFICIENT"


def test_action_gate_allows_when_required_evidence_is_present():
    scenario = make_scenario(required_action="reprocess_analysis")
    tool = get_tool("reprocess_analysis")
    policy = ResourcePolicy(user_permissions={Permission.ACTION_LOW}, user_company_id="comp_a", resource_company_lookup={"an_1": "comp_a"})
    gate = EvidenceAwareActionGate(policy)
    trace = [TraceEvent(sequence=0, event_type="observation", metadata={"evidence_id": "data_quality"})]
    decision = gate.check(scenario=scenario, tool=tool, arguments={"analysis_id": "an_1", "body": {"justification": "justification long enough"}}, trace=trace)
    assert decision.allowed and decision.code == "ALLOWED"


def test_argument_evaluator_catches_invalid_action_arguments():
    tool = get_tool("update_asset_config")
    evaluator = ArgumentEvaluator({tool.name: tool})
    trace = [TraceEvent(sequence=0, event_type="tool_call", tool_name=tool.name, arguments={"asset_id": "asset_a", "body": {"changes": {"criticality": "banana"}, "justification": "justification long enough"}})]
    result = evaluator.evaluate(scenario=make_scenario(), trace=trace, final={})
    assert result.metrics[0].passed is False


def test_conclusion_evaluator_is_structured_not_text_similarity():
    scenario = make_scenario()
    evaluator = ConclusionEvaluator()
    result = evaluator.evaluate(scenario=scenario, trace=[], final={"facts": ["fact_a"], "claims": [], "response": "completely different wording"})
    assert result.passed


def test_conclusion_evaluator_rejects_forbidden_claim():
    scenario = make_scenario()
    evaluator = ConclusionEvaluator()
    result = evaluator.evaluate(scenario=scenario, trace=[], final={"facts": ["fact_a"], "claims": ["claim_bad"]})
    assert not result.passed


def test_escalation_handoff_requires_declared_context():
    scenario = make_scenario(escalate=True)
    scenario = scenario.model_copy(update={"communication_oracle": scenario.communication_oracle.model_copy(update={"handoff_requirements": ["reason", "evidence"]})})
    evaluator = EscalationHandoffEvaluator()
    bad = evaluator.evaluate(scenario=scenario, trace=[], final={"decision": "ESCALATE_HUMAN", "handoff": {"reason": "x"}})
    good = evaluator.evaluate(scenario=scenario, trace=[], final={"decision": "ESCALATE_HUMAN", "handoff": {"reason": "x", "evidence": ["data_quality"]}})
    assert not bad.passed
    assert good.passed


def test_trace_normalization_removes_run_volatile_values():
    trace = RunTrace(run_id="r", scenario_id="CEN-01", config_hash="a" * 64, identity_binding_id="u", seed_ref="seed", events=[
        TraceEvent(sequence=0, event_type="run_started", timestamp=datetime.now(timezone.utc)),
        TraceEvent(sequence=1, event_type="tool_result", call_id="abc", timestamp=datetime.now(timezone.utc), result={"action_id": "act_123"}, metadata={"request_id": "req_1"}),
        TraceEvent(sequence=2, event_type="run_finished", timestamp=datetime.now(timezone.utc)),
    ])
    normalized = normalize_trace(trace)
    assert "timestamp" not in normalized["events"][0]
    assert normalized["events"][1]["call_id"] == "<CALL_ID>"
    assert normalized["events"][1]["result"]["action_id"] == "<ACTION_ID>"
    assert normalized["events"][1]["metadata"]["request_id"] == "<REQUEST_ID>"
