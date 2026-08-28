from __future__ import annotations

import ast
import inspect
import json
from typing import Any

import pytest

import academy_tractian.decision_source as decision_source_module
from academy_tractian.decision_source import (
    PROVIDER_DECISION_ADAPTER_VERSION,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    build_provider_decision_request,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry
from research.e2.controller import (
    ControllerContext,
    ControllerDecisionKind,
    ControllerObservation,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse


class ScriptedProviderClient:
    def __init__(self, *responses: str) -> None:
        self.responses = list(responses)
        self.calls: list[ProviderDecisionRequest] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request)
        if not self.responses:
            raise AssertionError("provider script exhausted")
        return self.responses.pop(0)


class ExplodingProviderClient:
    def __init__(self) -> None:
        self.calls: list[ProviderDecisionRequest] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request)
        raise RuntimeError("backend secret should never escape")


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(status_code=200, headers={}, body={"asset_id": "asset-1"})


def _json(kind: str, **kwargs: Any) -> str:
    payload = {"schema_version": "provider-decision-payload-v1", "kind": kind, **kwargs}
    return json.dumps(payload, sort_keys=True)


def _final_payload() -> dict[str, Any]:
    return {"decision": "ORIENT", "response_mode": "complete", "message": "Done."}


def _final_result(trace) -> dict[str, Any]:
    events = [event for event in trace.events if event.event_type == "final_response"]
    assert len(events) == 1
    assert isinstance(events[0].result, dict)
    return events[0].result


def test_provider_decision_source_is_structurally_compatible_with_client_protocol() -> None:
    client = ScriptedProviderClient(_json("ABSTAIN"))
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())
    decision = source.decide(ControllerContext(user_request="Inspect state", turn_index=0, tool_call_count=0))
    assert decision.kind is ControllerDecisionKind.ABSTAIN
    assert len(client.calls) == 1


def test_provider_visible_request_is_deterministic_sorted_and_runtime_private_state_free() -> None:
    registry = canonical_tool_registry()
    context = ControllerContext(
        user_request="Inspect the asset state.",
        turn_index=2,
        tool_call_count=1,
        observations=(
            ControllerObservation(
                tool_name="get_asset",
                status="success",
                executed=True,
                status_code=200,
                body={"asset_id": "asset-1", "status": "ok"},
            ),
        ),
    )
    first = build_provider_decision_request(context=context, registry=registry)
    second = build_provider_decision_request(context=context, registry=dict(reversed(list(registry.items()))))

    assert first == second
    assert first.request_sha256 == second.request_sha256
    assert first.adapter_version == PROVIDER_DECISION_ADAPTER_VERSION
    assert len(first.tools) == 18
    assert [tool.name for tool in first.tools] == sorted(registry)
    assert first.observations[0].body == {"asset_id": "asset-1", "status": "ok"}
    assert all(
        "parameter_schema" in parameter.model_dump(mode="json")
        for tool in first.tools
        for parameter in tool.parameters
    )

    serialized = first.model_dump_json()
    for forbidden in (
        '"user_id"',
        '"x-user-id"',
        '"identity_id"',
        '"seed"',
        '"config_hash"',
        '"actions_enabled"',
        '"user_permissions"',
        '"user_company_id"',
        '"confirmed_action_fingerprints"',
        '"idempotency"',
        '"gold"',
        '"oracle"',
    ):
        assert forbidden not in serialized


def test_request_hash_is_verified() -> None:
    request = build_provider_decision_request(
        context=ControllerContext(user_request="Inspect state", turn_index=0, tool_call_count=0),
        registry=canonical_tool_registry(),
    )
    data = request.model_dump(mode="json")
    data["request_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="request_sha256"):
        ProviderDecisionRequest.model_validate(data)


def test_valid_tool_payload_maps_exactly_and_calls_client_once() -> None:
    client = ScriptedProviderClient(
        _json("TOOL", tool_name="get_asset", arguments={"asset_id": "asset-1"}, evidence_id="ev-1")
    )
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())
    decision = source.decide(ControllerContext(user_request="Inspect asset", turn_index=0, tool_call_count=0))

    assert len(client.calls) == 1
    assert decision.kind is ControllerDecisionKind.TOOL
    assert decision.proposal is not None
    assert decision.proposal.tool_name == "get_asset"
    assert decision.proposal.arguments == {"asset_id": "asset-1"}
    assert decision.proposal.evidence_id == "ev-1"


@pytest.mark.parametrize(
    ("raw", "kind", "message", "reason"),
    [
        (_json("FINAL", final=_final_payload()), ControllerDecisionKind.FINAL, None, None),
        (_json("CLARIFY", message="Need asset id", reason_code="MISSING_ASSET"), ControllerDecisionKind.CLARIFY, "Need asset id", "MISSING_ASSET"),
        (_json("ESCALATE", message="Human review", reason_code="RISK"), ControllerDecisionKind.ESCALATE, "Human review", "RISK"),
        (_json("ABSTAIN", message="Cannot proceed", reason_code="NO_SAFE_PATH"), ControllerDecisionKind.ABSTAIN, "Cannot proceed", "NO_SAFE_PATH"),
    ],
)
def test_valid_terminal_payloads_map_to_controller_decisions(raw: str, kind, message, reason) -> None:
    source = ProviderDecisionSource(
        client=ScriptedProviderClient(raw),
        registry=canonical_tool_registry(),
    )
    decision = source.decide(ControllerContext(user_request="Inspect", turn_index=0, tool_call_count=0))
    assert decision.kind is kind
    if kind is ControllerDecisionKind.FINAL:
        assert decision.final == _final_payload()
    else:
        assert decision.message == message
        assert decision.reason_code == reason


@pytest.mark.parametrize(
    "bad_response",
    [
        "not-json",
        "[]",
        '{"schema_version":"provider-decision-payload-v1","kind":"ABSTAIN","kind":"FINAL"}',
        _json("TOOL", tool_name="does_not_exist", arguments={}),
        json.dumps({"schema_version": "provider-decision-payload-v1", "kind": "ABSTAIN", "unexpected": True}),
        _json("FINAL"),
        _json("TOOL", tool_name="get_asset", arguments={"asset_id": "asset-1"}, message="ambiguous"),
    ],
)
def test_malformed_provider_outputs_fail_closed_through_controller(bad_response: str) -> None:
    client = ScriptedProviderClient(bad_response)
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(client=client, registry=canonical_tool_registry()),
        transport=transport,
    )
    trace = runtime.run(
        ProductionRequest(
            request_id="req-bad-provider",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect the asset.",
        )
    )

    assert len(client.calls) == 1
    assert transport.calls == []
    final = _final_result(trace)
    assert final["decision"] == "ABSTAIN"
    assert final["reason_code"] == "DECISION_SOURCE_FAILURE"
    assert "backend" not in json.dumps(final).lower()


def test_provider_client_exception_fails_closed_without_exception_leakage() -> None:
    client = ExplodingProviderClient()
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(client=client, registry=canonical_tool_registry()),
        transport=transport,
    )
    trace = runtime.run(
        ProductionRequest(
            request_id="req-provider-error",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect the asset.",
        )
    )

    assert len(client.calls) == 1
    assert transport.calls == []
    final = _final_result(trace)
    assert final["reason_code"] == "DECISION_SOURCE_FAILURE"
    assert "secret" not in json.dumps(trace.model_dump(mode="json")).lower()


@pytest.mark.parametrize("field", ["user_id", "x-user-id", "seed"])
def test_model_controlled_binding_fields_are_rejected_before_tool_execution(field: str) -> None:
    client = ScriptedProviderClient(
        _json("TOOL", tool_name="get_asset", arguments={"asset_id": "asset-1", field: "attacker-value"})
    )
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(client=client, registry=canonical_tool_registry()),
        transport=transport,
    )
    trace = runtime.run(
        ProductionRequest(
            request_id=f"req-forbidden-{field}",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect the asset.",
            seed="runner-seed",
        )
    )

    assert transport.calls == []
    assert _final_result(trace)["reason_code"] == "DECISION_SOURCE_FAILURE"


def test_known_tool_argument_defect_remains_owned_by_b1_and_is_observable_next_turn() -> None:
    client = ScriptedProviderClient(
        _json("TOOL", tool_name="get_asset", arguments={}),
        _json("FINAL", final=_final_payload()),
    )
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(client=client, registry=canonical_tool_registry()),
        transport=transport,
    )
    trace = runtime.run(
        ProductionRequest(
            request_id="req-b1",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect the asset.",
        )
    )

    assert len(client.calls) == 2
    assert transport.calls == []
    blocked = [
        event
        for event in trace.events
        if event.event_type == "policy_check"
        and event.metadata.get("stage") == "B1"
    ]
    assert len(blocked) == 1
    assert blocked[0].metadata["violation"] == "ARGUMENT_INVALID"
    second_request = client.calls[1]
    assert second_request.observations[-1].status == "blocked"
    assert second_request.observations[-1].blocked_code == "ARGUMENT_INVALID"
    assert _final_result(trace)["decision"] == "ORIENT"


def test_valid_read_tool_flows_through_existing_runner_boundary() -> None:
    client = ScriptedProviderClient(
        _json("TOOL", tool_name="get_asset", arguments={"asset_id": "asset-1"}, evidence_id="ev-asset"),
        _json("FINAL", final=_final_payload()),
    )
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(client=client, registry=canonical_tool_registry()),
        transport=transport,
    )
    trace = runtime.run(
        ProductionRequest(
            request_id="req-valid-provider",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect the asset.",
            seed="seed-123",
        )
    )

    assert len(client.calls) == 2
    assert len(transport.calls) == 1
    assert transport.calls[0].headers["x-user-id"] == "user-1"
    assert transport.calls[0].query["seed"] == "seed-123"
    first_provider_request = client.calls[0].model_dump_json()
    assert "user-1" not in first_provider_request
    assert "seed-123" not in first_provider_request
    assert _final_result(trace)["decision"] == "ORIENT"


def test_provider_adapter_imports_no_provider_or_orchestration_sdk_and_no_private_evaluator_stack() -> None:
    source = inspect.getsource(decision_source_module)
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
            imported_modules.add(node.module)

    forbidden_roots = {
        "anthropic",
        "cerebras",
        "groq",
        "langchain",
        "langgraph",
        "openai",
        "pydantic_ai",
    }
    assert imported_roots.isdisjoint(forbidden_roots)
    assert "research.e2.evaluators" not in imported_modules
    assert "research.e2.evaluation_suite" not in imported_modules
    assert "Scenario" not in source
    assert "FRESH_BLIND" not in source
    assert "LEGACY_LOCKED_TEST" not in source
