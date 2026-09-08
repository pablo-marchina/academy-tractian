from __future__ import annotations

from research.e2.controller import (
    AgentController,
    ControllerDecision,
    ControllerDecisionKind,
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
        return TransportResponse(200, {}, {"ok": True})


class ScriptedDecisionSource:
    def __init__(self, decisions: list[ControllerDecision]) -> None:
        self.decisions = list(decisions)
        self.contexts = []

    def decide(self, context):
        self.contexts.append(context)
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


def make_runner(transport: FakeTransport) -> HarnessRunner:
    return HarnessRunner(
        run_id="duplicate-read-test",
        scenario_id="DUP-01",
        config_hash="d" * 64,
        registry={tool.name: tool for tool in TOOLS},
        binding=ExecutionBinding(identity_id="binding-1", user_id="usr-bound", seed=None),
        transport=transport,
        strict_arguments=True,
    )


def _tool(asset_id: str) -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.TOOL,
        proposal=ToolProposal(
            tool_name="get_asset",
            arguments={"asset_id": asset_id},
            evidence_id=f"asset-{asset_id}",
        ),
    )


def _final() -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={"decision": "ORIENT", "response_mode": "partial", "message": "done"},
    )


def test_exact_successful_read_is_blocked_before_second_transport_call():
    transport = FakeTransport()
    source = ScriptedDecisionSource([_tool("asset_a"), _tool("asset_a"), _final()])

    trace = AgentController(runner=make_runner(transport), decision_source=source).run("inspect asset")

    assert len(transport.calls) == 1
    assert source.contexts[1].tool_call_count == 1
    assert source.contexts[2].tool_call_count == 1
    assert source.contexts[2].observations[-1].status == "blocked"
    assert source.contexts[2].observations[-1].blocked_code == "DUPLICATE_SUCCESSFUL_READ"
    duplicate_blocks = [
        event
        for event in trace.events
        if event.event_type == "policy_check"
        and event.metadata.get("violation") == "DUPLICATE_SUCCESSFUL_READ"
    ]
    assert len(duplicate_blocks) == 1
    assert sum(event.event_type == "tool_call" for event in trace.events) == 1


def test_same_read_tool_with_different_resource_arguments_remains_allowed():
    transport = FakeTransport()
    source = ScriptedDecisionSource([_tool("asset_a"), _tool("asset_b"), _final()])

    trace = AgentController(runner=make_runner(transport), decision_source=source).run("compare assets")

    assert len(transport.calls) == 2
    assert sum(event.event_type == "tool_call" for event in trace.events) == 2
    assert not any(
        event.event_type == "policy_check"
        and event.metadata.get("violation") == "DUPLICATE_SUCCESSFUL_READ"
        for event in trace.events
    )
