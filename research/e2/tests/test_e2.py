from datetime import datetime, timezone

import pytest

from research.e2.binding import bind_request
from research.e2.models import (
    AgentCase,
    BoundContext,
    ConclusionOracle,
    DecisionOracle,
    EnvironmentSpec,
    EvaluationSpec,
    ExecutionBinding,
    EvidenceOracle,
    Provenance,
    Scenario,
    ScenarioInput,
    PolicyOracle,
    RunTrace,
    TraceEvent,
    TrajectoryOracle,
    ToolSpec,
)
from research.e2.provenance import ArtifactRef, build_run_manifest
from research.e2.replay import ReplayStore
from research.e2.trace import append_event, validate_trace


def scenario() -> Scenario:
    return Scenario(
        scenario_id="CEN-01",
        title="test",
        ticket_ids=["TKT-INV-04"],
        split_group_id="asset_G501",
        provenance=Provenance(review_status="APPROVED", benchmark_authoritative=True),
        input=ScenarioInput(cases=[AgentCase(id="case", ticket_id="TKT-INV-04", company_id="comp", user_id="usr_pedro", asset_id="asset_G501", message="x")]),
        bound_context=BoundContext(user_ids=["usr_pedro"], company_ids=["comp"], asset_ids=["asset_G501"]),
        environment=EnvironmentSpec(),
        decision_oracle=DecisionOracle(),
        policy_oracle=PolicyOracle(),
        evidence_oracle=EvidenceOracle(),
        conclusion_oracle=ConclusionOracle(source_resolution_text="x"),
        trajectory_oracle=TrajectoryOracle(),
        evaluation=EvaluationSpec(p1_success_source="x"),
    )


def test_models_forbid_unknown_fields():
    with pytest.raises(Exception):
        ToolSpec(name="x", operation_id="x", method="GET", path_template="/x", unknown=True)  # type: ignore[arg-type]


def test_identity_and_seed_are_runner_bound():
    request = bind_request(method="GET", path="/assets/{assetId}", arguments={"query": {}}, binding=ExecutionBinding(identity_id="run", user_id="usr_pedro", seed="CEN-01"))
    assert request.headers["x-user-id"] == "usr_pedro"
    assert request.query["seed"] == "CEN-01"
    with pytest.raises(ValueError):
        bind_request(method="GET", path="/assets/{assetId}", arguments={"user_id": "usr_bad"}, binding=ExecutionBinding(identity_id="run", user_id="usr_pedro"))


def test_trace_invariants():
    trace = RunTrace(run_id="r1", scenario_id="CEN-01", config_hash="a" * 64, identity_binding_id="u", seed_ref="s")
    trace = append_event(trace, TraceEvent(sequence=0, event_type="run_started", timestamp=datetime.now(timezone.utc)))
    trace = append_event(trace, TraceEvent(sequence=1, event_type="run_finished"))
    assert validate_trace(trace) == []


def test_replay_is_deterministic():
    store = ReplayStore()
    request = {"method": "GET", "path": "/x", "query": {"seed": "a"}}
    store.record(request, {"mode": "partial"})
    assert store.replay(request) == {"mode": "partial"}
    with pytest.raises(ValueError):
        store.record(request, {"mode": "complete"})


def test_run_manifest_is_order_stable():
    a = build_run_manifest(config={"b": 2, "a": 1}, artifacts=[ArtifactRef("z", "2"), ArtifactRef("a", "1")], scenario_id="CEN-01", run_id="r")
    b = build_run_manifest(config={"a": 1, "b": 2}, artifacts=[ArtifactRef("a", "1"), ArtifactRef("z", "2")], scenario_id="CEN-01", run_id="r")
    assert a == b


def test_registry_is_complete():
    from research.e2.tool_registry import TOOLS, validate_registry
    validate_registry()
    assert len(TOOLS) == 18
    assert sum(t.kind.value == "action" for t in TOOLS) == 5


def test_trace_requires_single_terminal_event():
    trace = RunTrace(run_id="r", scenario_id="CEN-01", config_hash="a" * 64, identity_binding_id="u", seed_ref="s", events=[TraceEvent(sequence=0, event_type="run_started")])
    assert "trace must contain exactly one terminal event" in validate_trace(trace)


def test_scenario_enforces_runner_control_flags():
    assert scenario().bound_context.identity_model_controlled is False
    assert scenario().bound_context.seed_model_controlled is False
