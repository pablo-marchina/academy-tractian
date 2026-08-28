from __future__ import annotations

import ast
import inspect

import pytest

import academy_tractian.action_safety as action_safety_module
from academy_tractian.action_safety import (
    ACTION_SAFETY_POLICY_VERSION,
    PRODUCTION_RUNTIME_CONTROLLED_ACTION_FIELDS,
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ProductionActionSafetyPolicy,
    ResourceCompanyBinding,
    action_fingerprint,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry
from research.e2.controller import ControllerDecision, ControllerDecisionKind, ControllerContext, ToolProposal
from research.e2.models import BoundRequest, ToolKind, ToolSpec
from research.e2.transport import TransportResponse


ACTION_CASES = (
    ("update_asset_config", {"asset_id": "asset-1", "body": {"justification": "Evidence reviewed and requester approved this exact configuration update.", "changes": {"criticality": "high"}}}),
    ("reprocess_analysis", {"analysis_id": "analysis-1", "body": {"justification": "Evidence reviewed and requester approved this exact reprocessing action."}}),
    ("request_specialist_analysis", {"analysis_id": "analysis-1", "body": {"justification": "Evidence reviewed and requester approved this exact specialist request."}}),
    ("request_retraining", {"model_id": "model-1", "body": {"justification": "Evidence reviewed and requester approved this exact retraining request."}}),
    ("escalate_case", {"case_id": "case-1", "body": {"justification": "Evidence reviewed and requester approved this exact escalation request."}}),
)


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(status_code=202, headers={}, body={"accepted": True})


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
    execution_enabled: bool = True,
    permissions: bool = True,
    scope_company: str | None = "company-1",
    confirmed: bool = True,
    idempotency: bool = True,
    consumed: bool = False,
) -> ProductionActionAuthorizationContext:
    fingerprint = action_fingerprint(tool, arguments)
    key = f"idem-{tool.name}-1"
    bindings = (
        ()
        if scope_company is None
        else (
            ResourceCompanyBinding(
                resource_id=_resource_id(arguments),
                company_id=scope_company,
            ),
        )
    )
    idempotency_bindings = (
        (ActionIdempotencyBinding(action_fingerprint=fingerprint, idempotency_key=key),)
        if idempotency
        else ()
    )
    return ProductionActionAuthorizationContext(
        execution_enabled=execution_enabled,
        user_permissions=(frozenset(tool.required_permissions) if permissions else frozenset()),
        user_company_id="company-1",
        resource_company_bindings=bindings,
        confirmed_action_fingerprints=(frozenset({fingerprint}) if confirmed else frozenset()),
        idempotency_bindings=idempotency_bindings,
        consumed_idempotency_keys=(frozenset({key}) if consumed else frozenset()),
    )


def _decision(tool_name: str, arguments: dict, **context_kwargs):
    tool = canonical_tool_registry()[tool_name]
    policy = ProductionActionSafetyPolicy(
        context=_context(tool, arguments, **context_kwargs)
    )
    return policy.evaluate(tool, arguments)


@pytest.mark.parametrize(("tool_name", "arguments"), ACTION_CASES)
def test_all_five_actions_can_pass_only_in_fully_satisfied_hypothetical_context(
    tool_name: str,
    arguments: dict,
) -> None:
    decision = _decision(tool_name, arguments)
    assert decision.allowed is True
    assert decision.code == "ALLOWED"
    assert decision.failed_codes == ()
    assert all(check.passed for check in decision.checks)


def test_missing_permission_is_distinct() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, permissions=False)
    assert decision.allowed is False
    assert decision.code == "PERMISSION_DENIED"


def test_global_action_switch_is_distinct_even_with_every_other_gate_satisfied() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, execution_enabled=False)
    assert decision.allowed is False
    assert decision.code == "ACTIONS_DISABLED"


def test_unknown_resource_scope_fails_closed() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, scope_company=None)
    assert decision.code == "RESOURCE_SCOPE_UNKNOWN"


def test_cross_company_resource_scope_is_denied() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, scope_company="company-2")
    assert decision.code == "RESOURCE_SCOPE_DENIED"


def test_requester_confirmation_is_bound_to_exact_action_fingerprint() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, confirmed=False)
    assert decision.code == "CONFIRMATION_REQUIRED"


def test_idempotency_key_is_required_outside_model_arguments() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, idempotency=False)
    assert decision.code == "IDEMPOTENCY_KEY_REQUIRED"


def test_consumed_idempotency_key_is_a_duplicate_action() -> None:
    tool_name, arguments = ACTION_CASES[1]
    decision = _decision(tool_name, arguments, consumed=True)
    assert decision.code == "DUPLICATE_ACTION"


def test_invalid_justification_is_independently_denied() -> None:
    tool_name, original = ACTION_CASES[1]
    arguments = {**original, "body": {"justification": "too short"}}
    decision = _decision(tool_name, arguments)
    assert decision.code == "INVALID_JUSTIFICATION"


def test_runtime_owned_authorization_fields_cannot_be_smuggled_as_tool_arguments() -> None:
    tool_name, original = ACTION_CASES[1]
    arguments = {**original, "idempotency_key": "model-controlled-key"}
    decision = _decision(tool_name, arguments)
    assert "idempotency_key" in PRODUCTION_RUNTIME_CONTROLLED_ACTION_FIELDS
    assert decision.code == "RUNTIME_CONTEXT_FIELD_PROPOSED"
    assert "ARGUMENT_INVALID" in decision.failed_codes


def test_decision_hash_is_stable_and_does_not_serialize_raw_idempotency_key() -> None:
    tool_name, arguments = ACTION_CASES[1]
    first = _decision(tool_name, arguments)
    second = _decision(tool_name, arguments)
    assert first.decision_sha256 == second.decision_sha256
    assert first.action_fingerprint == second.action_fingerprint
    serialized = first.model_dump_json()
    assert f"idem-{tool_name}-1" not in serialized
    assert first.idempotency_key_sha256 is not None


def test_canonical_registry_action_metadata_is_complete_for_policy() -> None:
    actions = [tool for tool in canonical_tool_registry().values() if tool.kind is ToolKind.ACTION]
    assert len(actions) == 5
    assert all(tool.required_permissions for tool in actions)
    assert all(tool.target_scope == "resource" for tool in actions)
    assert all(tool.justification_required for tool in actions)
    assert all((tool.minimum_justification_length or 0) >= 20 for tool in actions)
    assert all(tool.identity_binding == "runner" for tool in actions)
    assert all(tool.seed_supported is False for tool in actions)


def test_real_production_runtime_still_executes_zero_actions_and_uses_new_policy() -> None:
    tool_name, arguments = ACTION_CASES[1]
    transport = FakeTransport()
    source = ScriptedDecisionSource(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(tool_name=tool_name, arguments=arguments),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={"decision": "ORIENT", "response_mode": "complete", "message": "Action remained blocked."},
        ),
    )
    runtime = ProductionRuntime(decision_source=source, transport=transport)
    trace = runtime.run(
        ProductionRequest(
            request_id="req-action-1",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Reprocess the analysis if safe.",
        )
    )

    assert transport.calls == []
    b2 = [
        event
        for event in trace.events
        if event.event_type == "policy_check"
        and event.metadata.get("stage") == "B2"
        and event.tool_name == tool_name
    ]
    assert len(b2) == 1
    assert b2[0].metadata["allowed"] is False
    assert b2[0].metadata["contained"] is True
    assert b2[0].metadata["violation"] == "PERMISSION_DENIED"
    assert str(b2[0].metadata["reason"]).startswith(ACTION_SAFETY_POLICY_VERSION)

    decision_context = source.contexts[0].model_dump(mode="json")
    for field in (
        "execution_enabled",
        "user_permissions",
        "user_company_id",
        "resource_company_bindings",
        "confirmed_action_fingerprints",
        "idempotency_bindings",
        "consumed_idempotency_keys",
    ):
        assert field not in decision_context


def test_action_safety_surface_imports_no_provider_or_private_evaluator_stack() -> None:
    source = inspect.getsource(action_safety_module)
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

    forbidden_roots = {"anthropic", "cerebras", "groq", "langchain", "langgraph", "openai", "pydantic_ai"}
    assert imported_roots.isdisjoint(forbidden_roots)
    assert "research.e2.evaluators" not in imported_modules
    assert "research.e2.evaluation_suite" not in imported_modules
    assert "Scenario" not in source
