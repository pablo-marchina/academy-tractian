from __future__ import annotations

from research.e2.action_gate import EvidenceAwareActionGate
from research.e2.evaluation_suite import default_suite
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
    TrajectoryOracle,
)
from research.e2.policy import ResourcePolicy
from research.e2.replay import ReplayStore
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import TOOLS
from research.e2.transport import TransportResponse


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, request):
        self.calls.append(request)
        if request.method == "POST":
            return TransportResponse(200, {}, {"accepted": True, "action_id": "act_volatile"})
        return TransportResponse(200, {}, {"mode": "complete", "data": {"ok": True}})


class ExplodingTransport:
    def request(self, request):
        raise AssertionError("replay mode must not call live transport")


def scenario() -> Scenario:
    return Scenario(
        scenario_id="CEN-01",
        title="integrated fixture",
        ticket_ids=["TKT-X"],
        split_group_id="asset_a",
        provenance=Provenance(review_status="APPROVED", benchmark_authoritative=True),
        input=ScenarioInput(cases=[AgentCase(id="case", ticket_id="TKT-X", company_id="comp_a", user_id="usr_a", asset_id="asset_a", message="x")]),
        bound_context=BoundContext(user_ids=["usr_a"], company_ids=["comp_a"], asset_ids=["asset_a"]),
        environment=EnvironmentSpec(),
        decision_oracle=DecisionOracle(required=[Decision.ACT_REPROCESS]),
        policy_oracle=PolicyOracle(required_permissions=[Permission.ACTION_LOW]),
        evidence_oracle=EvidenceOracle(required_groups=[EvidenceGroup(group_id="g", requirements=[EvidenceRequirement(source="analysis", predicate="available", required_before_action=True)])]),
        action_oracle=ActionOracle(execution_expectation="required", success_semantics="accepted_event", post_action_read_semantics="diagnostic_only", required_action="reprocess_analysis", target_resource="an_1", required_permission=Permission.ACTION_LOW),
        conclusion_oracle=ConclusionOracle(required_facts=["resolved"], source_resolution_text="fixture"),
        trajectory_oracle=TrajectoryOracle(),
        evaluation=EvaluationSpec(p1_success_source="fixture"),
    )


def test_integrated_live_then_replay_trace_is_transport_independent():
    registry = {tool.name: tool for tool in TOOLS}
    replay = ReplayStore()
    transport = FakeTransport()
    binding = ExecutionBinding(identity_id="binding", user_id="usr_a", seed="CEN-01")

    live = HarnessRunner(run_id="live", scenario_id="CEN-01", config_hash="a" * 64, registry=registry, binding=binding, transport=transport, replay=replay)
    result = live.execute_tool("get_asset", {"asset_id": "asset_a"}, evidence_id="asset")
    assert result.executed and result.response.status_code == 200
    live_trace = live.finish({"decision": "INVESTIGATE", "facts": []})
    assert len(transport.calls) == 1

    replay_runner = HarnessRunner(run_id="replay", scenario_id="CEN-01", config_hash="a" * 64, registry=registry, binding=binding, transport=ExplodingTransport(), replay=replay, execution_mode="replay")
    replay_result = replay_runner.execute_tool("get_asset", {"asset_id": "asset_a"}, evidence_id="asset")
    assert replay_result.response.body == result.response.body
    replay_trace = replay_runner.finish({"decision": "INVESTIGATE", "facts": []})
    assert [e.event_type for e in live_trace.events] == [e.event_type for e in replay_trace.events]


def test_integrated_b3_blocks_action_before_transport_then_allows_after_evidence():
    s = scenario()
    registry = {tool.name: tool for tool in TOOLS}
    transport = FakeTransport()
    binding = ExecutionBinding(identity_id="binding", user_id="usr_a", seed="CEN-01")
    policy = ResourcePolicy(user_permissions={Permission.ACTION_LOW}, user_company_id="comp_a", resource_company_lookup={"an_1": "comp_a", "asset_a": "comp_a"})
    gate = EvidenceAwareActionGate(policy)
    runner = HarnessRunner(run_id="r", scenario_id=s.scenario_id, config_hash="b" * 64, registry=registry, binding=binding, transport=transport, strict_arguments=True, resource_policy=policy, action_gate=gate, scenario=s)

    blocked = runner.execute_tool("reprocess_analysis", {"analysis_id": "an_1", "body": {"justification": "justification sufficiently long"}})
    assert not blocked.executed and blocked.blocked_code == "EVIDENCE_INSUFFICIENT"
    assert transport.calls == []

    runner.execute_tool("get_analysis", {"analysis_id": "an_1"}, evidence_id="analysis")
    allowed = runner.execute_tool("reprocess_analysis", {"analysis_id": "an_1", "body": {"justification": "justification sufficiently long"}})
    assert allowed.executed and allowed.response.body["accepted"] is True

    final = {"decision": "ACT_REPROCESS", "facts": ["resolved"], "claims": []}
    trace = runner.finish(final)
    bundle = default_suite(registry).evaluate(scenario=s, trace=list(trace.events), final=final)
    assert bundle.by_name()["action"].passed
    assert bundle.by_name()["arguments"].passed
    assert bundle.by_name()["conclusion"].passed
