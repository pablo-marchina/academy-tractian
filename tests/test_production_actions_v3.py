from __future__ import annotations

from academy_tractian.production_actions_v3 import ActionProposalRealtimeProductionRuntimeV3
from academy_tractian.production_actions_v2 import PendingActionCustody, ProductionActionPrincipal
from research.e2.controller import ControllerDecision, ControllerDecisionKind, ToolProposal
from research.e2.transport import TransportResponse


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, request):
        self.calls.append(request)
        return TransportResponse(200, {}, {"ok": True})


class Sink:
    def publish(self, *, run, event, evidence):
        pass


class ScriptedSource:
    def __init__(self):
        self.decisions = [
            ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a"})),
            ControllerDecision(kind=ControllerDecisionKind.TOOL, proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "asset_a"})),
            ControllerDecision(kind=ControllerDecisionKind.FINAL, final={"decision": "ORIENT", "response_mode": "partial", "message": "done"}),
        ]

    def decide(self, context):
        return self.decisions.pop(0)


def _principal(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-a",
        permissions=frozenset(),
        resource_company_bindings=(),
    )


def test_v3_contains_exact_duplicate_read_before_transport(tmp_path):
    transport = FakeTransport()
    runtime = ActionProposalRealtimeProductionRuntimeV3(
        decision_source=ScriptedSource(),
        transport=transport,
        observability_sink=Sink(),
        authorization_resolver=_principal,
        custody=PendingActionCustody(tmp_path / "custody.duckdb"),
    )

    from academy_tractian.runtime import ProductionRequest

    trace = runtime.run(
        ProductionRequest(
            request_id="run-v3",
            identity_id="identity-a",
            user_id="user-a",
            user_request="inspect asset",
        )
    )

    assert len(transport.calls) == 1
    assert sum(event.event_type == "tool_call" for event in trace.events) == 1
    assert any(
        event.event_type == "policy_check"
        and event.metadata.get("violation") == "DUPLICATE_SUCCESSFUL_READ"
        for event in trace.events
    )
