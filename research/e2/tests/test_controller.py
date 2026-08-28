from __future__ import annotations

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from research.e2.controller import (
    AgentController,
    ControllerDecision,
    ControllerDecisionKind,
    ControllerLimits,
    DecisionSource,
    ToolProposal,
)
from research.e2.models import ExecutionBinding
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import TOOLS
from research.e2.transport import TransportResponse


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, request):
        self.calls.append(request)
        return TransportResponse(200, {}, {"mode": "complete", "data": {"ok": True}})


class ScriptedDecisionSource:
    def __init__(self, decisions: list[ControllerDecision]) -> None:
        self.decisions = list(decisions)
        self.contexts = []

    def decide(self, context):
        self.contexts.append(context)
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


class ExplodingDecisionSource:
    def decide(self, context):
        raise RuntimeError("provider-like failure must be contained")


class ExplodingTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, request):
        self.calls.append(request)
        raise RuntimeError("transport internals must not leak")


def make_runner(transport) -> HarnessRunner:
    return HarnessRunner(
        run_id="controller-test",
        scenario_id="CEN-01",
        config_hash="c" * 64,
        registry={tool.name: tool for tool in TOOLS},
        binding=ExecutionBinding(identity_id="binding-1", user_id="usr-bound", seed="seed-bound"),
        transport=transport,
        strict_arguments=True,
    )


def tool_then_final_source() -> ScriptedDecisionSource:
    return ScriptedDecisionSource(
        [
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset_a"},
                    evidence_id="asset",
                ),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final={"decision": "INVESTIGATE", "facts": ["asset read completed"]},
            ),
        ]
    )


def test_controller_routes_tool_only_through_harness_and_preserves_external_binding():
    transport = FakeTransport()
    runner = make_runner(transport)
    source = tool_then_final_source()

    trace = AgentController(runner=runner, decision_source=source).run("inspect asset")

    assert len(transport.calls) == 1
    request = transport.calls[0]
    assert request.headers["x-user-id"] == "usr-bound"
    assert request.query["seed"] == "seed-bound"
    assert source.contexts[0].tool_call_count == 0
    assert source.contexts[1].tool_call_count == 1
    assert source.contexts[1].observations[0].status == "success"
    assert source.contexts[1].observations[0].body == {"mode": "complete", "data": {"ok": True}}

    event_types = [event.event_type for event in trace.events]
    assert event_types == [
        "run_started",
        "decision",
        "tool_proposal",
        "tool_call",
        "tool_result",
        "observation",
        "decision",
        "final_response",
        "run_finished",
    ]
    assert trace.events[-2].result["controller_decision"] == "FINAL"


def test_tool_proposal_rejects_model_controlled_identity_and_seed():
    for forbidden in ("x-user-id", "user_id", "seed"):
        with pytest.raises((ValidationError, ValueError)):
            ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a", forbidden: "attacker"})


def test_tool_call_budget_fails_closed_before_second_execution():
    transport = FakeTransport()
    runner = make_runner(transport)
    source = ScriptedDecisionSource(
        [
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a"}),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_b"}),
            ),
        ]
    )

    trace = AgentController(
        runner=runner,
        decision_source=source,
        limits=ControllerLimits(max_turns=4, max_tool_calls=1),
    ).run("bounded")

    assert len(transport.calls) == 1
    assert trace.events[-2].result["decision"] == "ABSTAIN"
    assert trace.events[-2].result["reason_code"] == "TOOL_CALL_BUDGET_EXHAUSTED"


def test_blocked_tool_is_returned_as_observation_without_transport_bypass():
    transport = FakeTransport()
    runner = make_runner(transport)
    source = ScriptedDecisionSource(
        [
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name="get_asset", arguments={}),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                message="required arguments unavailable",
                reason_code="MISSING_ARGUMENTS",
            ),
        ]
    )

    trace = AgentController(runner=runner, decision_source=source).run("inspect unknown asset")

    assert transport.calls == []
    assert source.contexts[1].observations[0].status == "blocked"
    assert source.contexts[1].observations[0].blocked_code == "ARGUMENT_INVALID"
    contained_observation = [
        event for event in trace.events if event.event_type == "observation" and event.metadata.get("controller_generated")
    ]
    assert len(contained_observation) == 1


def test_decision_source_failure_returns_safe_abstention_without_tool_execution():
    transport = FakeTransport()
    runner = make_runner(transport)

    trace = AgentController(runner=runner, decision_source=ExplodingDecisionSource()).run("inspect")

    assert transport.calls == []
    assert trace.events[-2].result["decision"] == "ABSTAIN"
    assert trace.events[-2].result["response_mode"] == "unavailable"
    assert trace.events[-2].result["reason_code"] == "DECISION_SOURCE_FAILURE"
    assert "provider-like failure" not in str(trace.model_dump())


@pytest.mark.parametrize(
    ("decision", "expected"),
    [
        (ControllerDecision(kind=ControllerDecisionKind.CLARIFY, message="need asset id"), "ASK_CLARIFICATION"),
        (ControllerDecision(kind=ControllerDecisionKind.ESCALATE, message="operator required"), "ESCALATE_HUMAN"),
        (ControllerDecision(kind=ControllerDecisionKind.ABSTAIN, message="cannot proceed"), "ABSTAIN"),
    ],
)
def test_terminal_non_tool_decisions_never_execute_tools(decision, expected):
    transport = FakeTransport()
    runner = make_runner(transport)
    source = ScriptedDecisionSource([decision])

    trace = AgentController(runner=runner, decision_source=source).run("terminal")

    assert transport.calls == []
    assert trace.events[-2].result["decision"] == expected


def test_controller_source_is_provider_free_and_runtime_framework_free():
    source_path = Path(__file__).parents[1] / "controller.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    forbidden = {
        "openai",
        "anthropic",
        "groq",
        "cerebras",
        "langgraph",
        "langchain",
        "pydantic_ai",
        "agents",
    }
    assert imported_roots.isdisjoint(forbidden)


def test_controller_decision_shape_is_fail_closed():
    with pytest.raises(ValidationError):
        ControllerDecision(kind=ControllerDecisionKind.TOOL)
    with pytest.raises(ValidationError):
        ControllerDecision(kind=ControllerDecisionKind.FINAL)
    with pytest.raises(ValidationError):
        ControllerDecision(
            kind=ControllerDecisionKind.ABSTAIN,
            proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a"}),
        )


def test_turn_budget_fails_closed_after_bounded_tool_turn():
    transport = FakeTransport()
    runner = make_runner(transport)
    source = ScriptedDecisionSource(
        [
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a"}),
            )
        ]
    )

    trace = AgentController(
        runner=runner,
        decision_source=source,
        limits=ControllerLimits(max_turns=1, max_tool_calls=4),
    ).run("bounded turns")

    assert len(transport.calls) == 1
    assert trace.events[-2].result["decision"] == "ABSTAIN"
    assert trace.events[-2].result["reason_code"] == "TURN_BUDGET_EXHAUSTED"


def test_transport_failure_fails_closed_without_leaking_exception_details():
    transport = ExplodingTransport()
    runner = make_runner(transport)
    source = ScriptedDecisionSource(
        [
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a"}),
            )
        ]
    )

    trace = AgentController(runner=runner, decision_source=source).run("inspect")

    assert len(transport.calls) == 1
    assert trace.events[-2].result["decision"] == "ABSTAIN"
    assert trace.events[-2].result["reason_code"] == "TOOL_BOUNDARY_FAILURE"
    assert "transport internals" not in str(trace.model_dump())
    assert [event.event_type for event in trace.events][-3:] == [
        "state_change",
        "final_response",
        "run_finished",
    ]
