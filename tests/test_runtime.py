from __future__ import annotations

import ast
import inspect

import pytest
from pydantic import ValidationError

import academy_tractian.runtime as runtime_module
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, ProductionRuntimeConfig, canonical_tool_registry
from research.e2.controller import ControllerDecision, ControllerDecisionKind, ControllerContext, ToolProposal
from research.e2.models import BoundRequest, ToolKind
from research.e2.transport import TransportResponse


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(status_code=200, headers={"content-type": "application/json"}, body={"asset_id": "asset-1", "status": "ok"})


class ExplodingTransport:
    def request(self, request: BoundRequest) -> TransportResponse:
        raise RuntimeError("backend-internal-detail")


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)
        self.contexts: list[ControllerContext] = []

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.contexts.append(context)
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


def _request(*, seed: str | None = "seed-7") -> ProductionRequest:
    return ProductionRequest(request_id="req-1", identity_id="identity-1", user_id="user-1", user_request="Check asset asset-1 and summarize the evidence.", seed=seed)


def _final(message: str = "Asset evidence was inspected.") -> ControllerDecision:
    return ControllerDecision(kind=ControllerDecisionKind.FINAL, final={"decision": "ORIENT", "response_mode": "complete", "message": message})


def _event_types(trace) -> list[str]:
    return [event.event_type for event in trace.events]


def test_read_tool_routes_once_through_e2_and_keeps_binding_outside_decision_context() -> None:
    transport = FakeTransport()
    source = ScriptedDecisionSource(
        ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset-1"}, evidence_id="asset-context")),
        _final(),
    )
    runtime = ProductionRuntime(decision_source=source, transport=transport)
    trace = runtime.run(_request())

    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.method == "GET"
    assert call.path == "/assets/asset-1"
    assert call.headers["x-user-id"] == "user-1"
    assert call.query["seed"] == "seed-7"

    dumped_context = source.contexts[0].model_dump(mode="json")
    assert set(dumped_context) == {"user_request", "turn_index", "tool_call_count", "observations"}
    assert "user_id" not in dumped_context
    assert "identity_id" not in dumped_context
    assert "seed" not in dumped_context
    assert trace.identity_binding_id == "identity-1"
    assert trace.seed_ref == "runner-bound"
    assert trace.scenario_id == "prod:req-1"
    assert {"tool_proposal", "tool_call", "tool_result", "observation"} <= set(_event_types(trace))
    assert _event_types(trace)[-1] == "run_finished"


ACTION_CASES = (
    ("update_asset_config", {"asset_id": "asset-1", "body": {"justification": "Evidence reviewed; production actions are not enabled.", "changes": {"criticality": "high"}}}),
    ("reprocess_analysis", {"analysis_id": "analysis-1", "body": {"justification": "Evidence reviewed; production actions are not enabled."}}),
    ("request_specialist_analysis", {"analysis_id": "analysis-1", "body": {"justification": "Evidence reviewed; production actions are not enabled."}}),
    ("request_retraining", {"model_id": "model-1", "body": {"justification": "Evidence reviewed; production actions are not enabled."}}),
    ("escalate_case", {"case_id": "case-1", "body": {"justification": "Evidence reviewed; production actions are not enabled."}}),
)


@pytest.mark.parametrize(("tool_name", "arguments"), ACTION_CASES)
def test_every_canonical_action_is_denied_before_transport(tool_name: str, arguments: dict) -> None:
    transport = FakeTransport()
    source = ScriptedDecisionSource(
        ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name=tool_name, arguments=arguments)),
        _final("Action was not executed."),
    )
    runtime = ProductionRuntime(decision_source=source, transport=transport)
    trace = runtime.run(_request(seed=None))

    assert transport.calls == []
    policy_events = [event for event in trace.events if event.event_type == "policy_check" and event.tool_name == tool_name]
    assert len(policy_events) == 1
    event = policy_events[0]
    assert event.metadata["allowed"] is False
    assert event.metadata["contained"] is True
    assert event.metadata["stage"] == "B2"
    assert event.metadata["violation"] == "PERMISSION_DENIED"
    observations = [event for event in trace.events if event.event_type == "observation" and event.tool_name == tool_name and event.metadata.get("controller_generated") is True]
    assert len(observations) == 1
    assert observations[0].result["executed"] is False
    assert observations[0].result["blocked_code"] == "PERMISSION_DENIED"


@pytest.mark.parametrize("decision", (_final(), ControllerDecision(kind=ControllerDecisionKind.CLARIFY, message="Which asset should be inspected?"), ControllerDecision(kind=ControllerDecisionKind.ESCALATE, message="Human review is required."), ControllerDecision(kind=ControllerDecisionKind.ABSTAIN, message="Evidence is unavailable.")))
def test_terminal_decisions_execute_zero_tools(decision: ControllerDecision) -> None:
    transport = FakeTransport()
    runtime = ProductionRuntime(decision_source=ScriptedDecisionSource(decision), transport=transport)
    trace = runtime.run(_request(seed=None))
    assert transport.calls == []
    assert "final_response" in _event_types(trace)
    assert _event_types(trace)[-1] == "run_finished"


def test_strict_argument_validation_blocks_invalid_read_before_transport() -> None:
    transport = FakeTransport()
    source = ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={})), _final("Invalid proposal was contained."))
    trace = ProductionRuntime(decision_source=source, transport=transport).run(_request(seed=None))
    assert transport.calls == []
    policy_events = [event for event in trace.events if event.event_type == "policy_check" and event.metadata.get("stage") == "B1"]
    assert len(policy_events) == 1
    assert policy_events[0].metadata["violation"] == "ARGUMENT_INVALID"


def test_transport_failure_safe_abstains_without_internal_detail_leakage() -> None:
    source = ScriptedDecisionSource(ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset-1"})))
    trace = ProductionRuntime(decision_source=source, transport=ExplodingTransport()).run(_request(seed=None))
    payload = trace.model_dump_json()
    assert "backend-internal-detail" not in payload
    final_event = next(event for event in trace.events if event.event_type == "final_response")
    assert final_event.result["decision"] == "ABSTAIN"
    assert final_event.result["reason_code"] == "TOOL_BOUNDARY_FAILURE"


def test_runtime_config_cannot_enable_actions() -> None:
    with pytest.raises(ValidationError):
        ProductionRuntimeConfig(actions_enabled=True)  # type: ignore[arg-type]


def test_canonical_registry_keeps_18_operations_and_five_actions() -> None:
    registry = canonical_tool_registry()
    assert len(registry) == 18
    assert sum(tool.kind is ToolKind.ACTION for tool in registry.values()) == 5


def test_config_hash_is_stable_and_changes_with_runtime_limits() -> None:
    transport = FakeTransport()
    runtime_a = ProductionRuntime(decision_source=ScriptedDecisionSource(_final()), transport=transport, config=ProductionRuntimeConfig(max_turns=8))
    runtime_a_again = ProductionRuntime(decision_source=ScriptedDecisionSource(_final()), transport=transport, config=ProductionRuntimeConfig(max_turns=8))
    runtime_b = ProductionRuntime(decision_source=ScriptedDecisionSource(_final()), transport=transport, config=ProductionRuntimeConfig(max_turns=9))
    assert runtime_a.config_hash == runtime_a_again.config_hash
    assert runtime_a.config_hash != runtime_b.config_hash


def test_production_runtime_imports_no_provider_or_orchestration_sdk() -> None:
    tree = ast.parse(inspect.getsource(runtime_module))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    forbidden = {"anthropic", "cerebras", "groq", "langchain", "langgraph", "openai", "pydantic_ai"}
    assert imported_roots.isdisjoint(forbidden)
