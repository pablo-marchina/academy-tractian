from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest

import academy_tractian.controlled_actions as controlled_module
from academy_tractian.action_safety import (
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ResourceCompanyBinding,
    action_fingerprint,
)
from academy_tractian.controlled_actions import (
    ControlledActionRuntime,
    DurableActionAttemptClaimStore,
    StaticActionAuthorizationSource,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry
from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest, ToolSpec
from research.e2.transport import TransportResponse


ACTION_CASES = (
    (
        "update_asset_config",
        {
            "asset_id": "asset-1",
            "body": {
                "justification": "Evidence reviewed and requester approved this exact configuration update.",
                "changes": {"criticality": "high"},
            },
        },
    ),
    (
        "reprocess_analysis",
        {
            "analysis_id": "analysis-1",
            "body": {
                "justification": "Evidence reviewed and requester approved this exact reprocessing action."
            },
        },
    ),
    (
        "request_specialist_analysis",
        {
            "analysis_id": "analysis-1",
            "body": {
                "justification": "Evidence reviewed and requester approved this exact specialist request."
            },
        },
    ),
    (
        "request_retraining",
        {
            "model_id": "model-1",
            "body": {
                "justification": "Evidence reviewed and requester approved this exact retraining request."
            },
        },
    ),
    (
        "escalate_case",
        {
            "case_id": "case-1",
            "body": {
                "justification": "Evidence reviewed and requester approved this exact escalation request."
            },
        },
    ),
)


class RecordingTransport:
    def __init__(self, *, explode: bool = False) -> None:
        self.calls: list[BoundRequest] = []
        self.explode = explode

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        if self.explode:
            raise RuntimeError("synthetic transport failure with internal detail")
        return TransportResponse(
            status_code=202,
            headers={},
            body={"accepted": True},
        )


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)
        self.contexts: list[ControllerContext] = []

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.contexts.append(context)
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


def _resource_id(arguments: dict) -> str:
    candidates = [
        value
        for key, value in arguments.items()
        if key.endswith("_id") and isinstance(value, str)
    ]
    assert len(candidates) == 1
    return candidates[0]


def _context(
    tool: ToolSpec,
    arguments: dict,
    *,
    idempotency_key: str,
    execution_enabled: bool = True,
    permissions: bool = True,
    scope_company: str | None = "company-1",
    confirmed: bool = True,
) -> ProductionActionAuthorizationContext:
    fingerprint = action_fingerprint(tool, arguments)
    resource_bindings = (
        ()
        if scope_company is None
        else (
            ResourceCompanyBinding(
                resource_id=_resource_id(arguments),
                company_id=scope_company,
            ),
        )
    )
    return ProductionActionAuthorizationContext(
        execution_enabled=execution_enabled,
        user_permissions=(frozenset(tool.required_permissions) if permissions else frozenset()),
        user_company_id="company-1",
        resource_company_bindings=resource_bindings,
        confirmed_action_fingerprints=(frozenset({fingerprint}) if confirmed else frozenset()),
        idempotency_bindings=(
            ActionIdempotencyBinding(
                action_fingerprint=fingerprint,
                idempotency_key=idempotency_key,
            ),
        ),
    )


def _source_for(
    tool_name: str,
    arguments: dict,
    *,
    idempotency_key: str,
    **context_kwargs,
) -> StaticActionAuthorizationSource:
    tool = canonical_tool_registry()[tool_name]
    fingerprint = action_fingerprint(tool, arguments)
    context = _context(
        tool,
        arguments,
        idempotency_key=idempotency_key,
        **context_kwargs,
    )
    return StaticActionAuthorizationSource.from_contexts({fingerprint: context})


def _tool_then_final(tool_name: str, arguments: dict) -> ScriptedDecisionSource:
    return ScriptedDecisionSource(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(tool_name=tool_name, arguments=arguments),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "EXECUTE",
                "response_mode": "complete",
                "message": "The supplied synthetic action was accepted.",
            },
        ),
    )


def _request(suffix: str) -> ProductionRequest:
    return ProductionRequest(
        request_id=f"controlled-action-{suffix}",
        identity_id="identity-1",
        user_id="user-1",
        user_request="Execute the explicitly authorized action.",
    )


@pytest.mark.parametrize(("tool_name", "arguments"), ACTION_CASES)
def test_all_five_actions_execute_exactly_once_when_fully_authorized(
    tmp_path: Path,
    tool_name: str,
    arguments: dict,
) -> None:
    key = f"idem-{tool_name}-accepted"
    source = _tool_then_final(tool_name, arguments)
    transport = RecordingTransport()
    store = DurableActionAttemptClaimStore(tmp_path / tool_name / "claims")
    runtime = ControlledActionRuntime(
        decision_source=source,
        transport=transport,
        authorization_source=_source_for(
            tool_name,
            arguments,
            idempotency_key=key,
        ),
        claim_store=store,
    )

    trace = runtime.run(_request(tool_name))

    assert len(transport.calls) == 1
    assert transport.calls[0].headers["x-user-id"] == "user-1"
    assert any(
        event.event_type == "tool_result"
        and event.tool_name == tool_name
        and event.result["body"] == {"accepted": True}
        for event in trace.events
    )
    b2 = [
        event
        for event in trace.events
        if event.event_type == "policy_check"
        and event.tool_name == tool_name
        and event.metadata.get("stage") == "B2"
    ]
    assert len(b2) == 1
    assert b2[0].metadata["allowed"] is True

    claim_path = store.claim_path(key)
    assert claim_path.exists()
    payload = json.loads(claim_path.read_text(encoding="utf-8"))
    assert payload["state"] == "claimed"
    assert payload["tool_name"] == tool_name
    assert payload["raw_idempotency_key_recorded"] is False
    assert key not in claim_path.read_text(encoding="utf-8")

    first_context = source.contexts[0].model_dump(mode="json")
    for forbidden in (
        "execution_enabled",
        "user_permissions",
        "user_company_id",
        "resource_company_bindings",
        "confirmed_action_fingerprints",
        "idempotency_bindings",
        "consumed_idempotency_keys",
    ):
        assert forbidden not in first_context


def test_duplicate_is_blocked_across_runtime_instances_before_second_transport(
    tmp_path: Path,
) -> None:
    tool_name, arguments = ACTION_CASES[1]
    key = "idem-reprocess-cross-runtime"
    claim_root = tmp_path / "claims"
    transport = RecordingTransport()

    first = ControlledActionRuntime(
        decision_source=_tool_then_final(tool_name, arguments),
        transport=transport,
        authorization_source=_source_for(tool_name, arguments, idempotency_key=key),
        claim_store=DurableActionAttemptClaimStore(claim_root),
    )
    first.run(_request("first"))
    assert len(transport.calls) == 1

    second_source = _tool_then_final(tool_name, arguments)
    second = ControlledActionRuntime(
        decision_source=second_source,
        transport=transport,
        authorization_source=_source_for(tool_name, arguments, idempotency_key=key),
        claim_store=DurableActionAttemptClaimStore(claim_root),
    )
    trace = second.run(_request("second"))

    assert len(transport.calls) == 1
    duplicate_events = [
        event
        for event in trace.events
        if event.event_type == "policy_check"
        and event.metadata.get("stage") == "B2"
        and event.metadata.get("violation") == "DUPLICATE_ACTION"
    ]
    assert len(duplicate_events) == 1
    assert any(
        event.event_type == "observation"
        and event.result.get("blocked_code") == "DUPLICATE_ACTION"
        for event in trace.events
        if isinstance(event.result, dict)
    )


def test_preclaim_authorization_denial_does_not_consume_idempotency_key(tmp_path: Path) -> None:
    tool_name, arguments = ACTION_CASES[1]
    key = "idem-not-confirmed"
    source = _tool_then_final(tool_name, arguments)
    transport = RecordingTransport()
    store = DurableActionAttemptClaimStore(tmp_path / "claims")
    runtime = ControlledActionRuntime(
        decision_source=source,
        transport=transport,
        authorization_source=_source_for(
            tool_name,
            arguments,
            idempotency_key=key,
            confirmed=False,
        ),
        claim_store=store,
    )

    trace = runtime.run(_request("not-confirmed"))

    assert transport.calls == []
    assert not store.claim_path(key).exists()
    assert any(
        event.event_type == "policy_check"
        and event.metadata.get("violation") == "CONFIRMATION_REQUIRED"
        for event in trace.events
    )


@pytest.mark.parametrize(
    "context_kwargs,expected_code",
    (
        ({"permissions": False}, "PERMISSION_DENIED"),
        ({"scope_company": None}, "RESOURCE_SCOPE_UNKNOWN"),
        ({"scope_company": "company-2"}, "RESOURCE_SCOPE_DENIED"),
        ({"execution_enabled": False}, "ACTIONS_DISABLED"),
    ),
)
def test_adr005_denials_remain_zero_transport_and_zero_claim(
    tmp_path: Path,
    context_kwargs: dict,
    expected_code: str,
) -> None:
    tool_name, arguments = ACTION_CASES[1]
    key = f"idem-denied-{expected_code}"
    transport = RecordingTransport()
    store = DurableActionAttemptClaimStore(tmp_path / expected_code)
    runtime = ControlledActionRuntime(
        decision_source=_tool_then_final(tool_name, arguments),
        transport=transport,
        authorization_source=_source_for(
            tool_name,
            arguments,
            idempotency_key=key,
            **context_kwargs,
        ),
        claim_store=store,
    )

    trace = runtime.run(_request(expected_code.lower()))

    assert transport.calls == []
    assert not store.claim_path(key).exists()
    assert any(
        event.event_type == "policy_check"
        and event.metadata.get("violation") == expected_code
        for event in trace.events
    )


def test_unprovisioned_exact_action_is_contained_without_claim(tmp_path: Path) -> None:
    tool_name, arguments = ACTION_CASES[1]
    transport = RecordingTransport()
    runtime = ControlledActionRuntime(
        decision_source=_tool_then_final(tool_name, arguments),
        transport=transport,
        authorization_source=StaticActionAuthorizationSource.from_contexts({}),
        claim_store=DurableActionAttemptClaimStore(tmp_path / "claims"),
    )

    trace = runtime.run(_request("unprovisioned"))

    assert transport.calls == []
    assert any(
        event.event_type == "policy_check"
        and event.metadata.get("violation") == "AUTHORIZATION_NOT_PROVISIONED"
        for event in trace.events
    )


def test_transport_failure_after_claim_remains_consumed_and_cannot_be_replayed(
    tmp_path: Path,
) -> None:
    tool_name, arguments = ACTION_CASES[1]
    key = "idem-transport-uncertain"
    claim_root = tmp_path / "claims"
    failing_transport = RecordingTransport(explode=True)

    first = ControlledActionRuntime(
        decision_source=_tool_then_final(tool_name, arguments),
        transport=failing_transport,
        authorization_source=_source_for(tool_name, arguments, idempotency_key=key),
        claim_store=DurableActionAttemptClaimStore(claim_root),
    )
    trace = first.run(_request("transport-failure"))

    assert len(failing_transport.calls) == 1
    assert DurableActionAttemptClaimStore(claim_root).claim_path(key).exists()
    final = [event for event in trace.events if event.event_type == "final_response"][-1]
    assert final.result["reason_code"] == "TOOL_BOUNDARY_FAILURE"
    assert "synthetic transport failure" not in json.dumps(trace.model_dump(mode="json"))

    recovery_transport = RecordingTransport()
    second = ControlledActionRuntime(
        decision_source=_tool_then_final(tool_name, arguments),
        transport=recovery_transport,
        authorization_source=_source_for(tool_name, arguments, idempotency_key=key),
        claim_store=DurableActionAttemptClaimStore(claim_root),
    )
    duplicate_trace = second.run(_request("transport-failure-retry"))

    assert recovery_transport.calls == []
    assert any(
        event.event_type == "policy_check"
        and event.metadata.get("violation") == "DUPLICATE_ACTION"
        for event in duplicate_trace.events
    )


def test_raw_idempotency_key_is_not_persisted_or_exposed_by_source_repr(tmp_path: Path) -> None:
    tool_name, arguments = ACTION_CASES[1]
    key = "very-sensitive-runtime-owned-idempotency-key"
    source = _source_for(tool_name, arguments, idempotency_key=key)
    store = DurableActionAttemptClaimStore(tmp_path / "claims")
    runtime = ControlledActionRuntime(
        decision_source=_tool_then_final(tool_name, arguments),
        transport=RecordingTransport(),
        authorization_source=source,
        claim_store=store,
    )
    runtime.run(_request("redaction"))

    assert key not in repr(source)
    claim_text = store.claim_path(key).read_text(encoding="utf-8")
    assert key not in claim_text
    payload = json.loads(claim_text)
    assert payload["idempotency_key_sha256"]
    assert payload["raw_idempotency_key_recorded"] is False


def test_existing_read_only_production_runtime_is_still_action_disabled() -> None:
    tool_name, arguments = ACTION_CASES[1]
    transport = RecordingTransport()
    source = _tool_then_final(tool_name, arguments)
    runtime = ProductionRuntime(decision_source=source, transport=transport)
    trace = runtime.run(_request("read-only-regression"))

    assert transport.calls == []
    assert any(
        event.event_type == "policy_check"
        and event.metadata.get("stage") == "B2"
        and event.metadata.get("allowed") is False
        for event in trace.events
    )


def test_controlled_action_surface_imports_no_provider_or_private_evaluator_stack() -> None:
    source = inspect.getsource(controlled_module)
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
    assert "ProviderDecisionSource" not in source
