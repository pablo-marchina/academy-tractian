from __future__ import annotations

import ast
import inspect
from pathlib import Path

import academy_tractian.controlled_action_evaluation as controlled_eval_module
from academy_tractian.action_safety import (
    ActionIdempotencyBinding,
    ProductionActionAuthorizationContext,
    ResourceCompanyBinding,
    action_fingerprint,
)
from academy_tractian.controlled_action_evaluation import (
    ControlledActionEvaluator,
    IntegratedControlledActionRunner,
)
from academy_tractian.controlled_actions import (
    ControlledActionRuntime,
    DurableActionAttemptClaimStore,
    StaticActionAuthorizationSource,
)
from academy_tractian.evaluation import ProductionEvaluator
from academy_tractian.runtime import ProductionRequest, canonical_tool_registry
from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest, RunTrace, TraceEvent
from research.e2.transport import TransportResponse


TOOL_NAME = "reprocess_analysis"
ARGUMENTS = {
    "analysis_id": "analysis-1",
    "body": {
        "justification": "Evidence reviewed and requester approved this exact reprocessing action."
    },
}


class ActionTransport:
    def __init__(self, *, accepted: bool = True) -> None:
        self.accepted = accepted
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=202,
            headers={},
            body={"accepted": self.accepted},
        )


class ScriptedDecisionSource:
    def __init__(self) -> None:
        self.contexts: list[ControllerContext] = []
        self.decisions = [
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name=TOOL_NAME, arguments=ARGUMENTS),
            ),
            ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final={
                    "decision": "EXECUTE",
                    "response_mode": "complete",
                    "message": "The supplied synthetic action was accepted.",
                },
            ),
        ]

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.contexts.append(context)
        return self.decisions.pop(0)


def _runtime(tmp_path: Path, *, accepted: bool = True) -> ControlledActionRuntime:
    tool = canonical_tool_registry()[TOOL_NAME]
    fingerprint = action_fingerprint(tool, ARGUMENTS)
    key = "idem-evaluator-reprocess-1"
    context = ProductionActionAuthorizationContext(
        execution_enabled=True,
        user_permissions=frozenset(tool.required_permissions),
        user_company_id="company-1",
        resource_company_bindings=(
            ResourceCompanyBinding(
                resource_id="analysis-1",
                company_id="company-1",
            ),
        ),
        confirmed_action_fingerprints=frozenset({fingerprint}),
        idempotency_bindings=(
            ActionIdempotencyBinding(
                action_fingerprint=fingerprint,
                idempotency_key=key,
            ),
        ),
    )
    return ControlledActionRuntime(
        decision_source=ScriptedDecisionSource(),
        transport=ActionTransport(accepted=accepted),
        authorization_source=StaticActionAuthorizationSource.from_contexts(
            {fingerprint: context}
        ),
        claim_store=DurableActionAttemptClaimStore(tmp_path / "claims"),
    )


def _request(suffix: str) -> ProductionRequest:
    return ProductionRequest(
        request_id=f"controlled-eval-{suffix}",
        identity_id="identity-1",
        user_id="user-1",
        user_request="Reprocess the analysis under the explicit authorization.",
    )


def _resequence(events: list[TraceEvent]) -> list[TraceEvent]:
    return [event.model_copy(update={"sequence": index}) for index, event in enumerate(events)]


def test_controlled_action_trace_passes_composed_evaluator_while_default_stays_read_only(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path)
    trace = runtime.run(_request("accepted"))

    default_report = ProductionEvaluator().evaluate(trace)
    assert default_report.passed is False
    assert default_report.by_name()["read_only_action_safety"].passed is False

    report = ControlledActionEvaluator().evaluate(trace)
    checks = report.by_name()
    assert report.passed is True
    assert "read_only_action_safety" not in checks
    assert checks["production_trace_identity"].passed is True
    assert checks["controlled_action_execution"].passed is True
    assert checks["controlled_action_execution"].details["action_call_count"] == 1
    assert checks["controlled_action_execution"].details["accepted_action_count"] == 1


def test_integrated_controlled_runner_evaluates_the_exact_runtime_trace(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    runner = IntegratedControlledActionRunner.with_default_evaluator(runtime=runtime)

    result = runner.run(_request("integrated"))

    assert result.evaluation.run_id == result.trace.run_id
    assert result.evaluation.scenario_id == result.trace.scenario_id
    assert result.evaluation.trace_sha256 == ControlledActionEvaluator().evaluate(
        result.trace
    ).trace_sha256
    assert result.evaluation.passed is True


def test_action_without_accepted_true_fails_controlled_action_check(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path, accepted=False)
    trace = runtime.run(_request("not-accepted"))
    report = ControlledActionEvaluator().evaluate(trace)
    check = report.by_name()["controlled_action_execution"]

    assert report.passed is False
    assert check.passed is False
    assert any(issue["code"] == "ACTION_NOT_ACCEPTED" for issue in check.details["issues"])


def test_action_call_without_b2_allow_fails_even_if_transport_result_is_accepted(
    tmp_path: Path,
) -> None:
    trace = _runtime(tmp_path).run(_request("missing-b2"))
    events = [
        event
        for event in trace.events
        if not (
            event.event_type == "policy_check"
            and event.tool_name == TOOL_NAME
            and event.metadata.get("stage") == "B2"
            and event.metadata.get("allowed") is True
        )
    ]
    tampered = trace.model_copy(update={"events": _resequence(events)})

    report = ControlledActionEvaluator().evaluate(tampered)
    check = report.by_name()["controlled_action_execution"]
    assert report.passed is False
    assert any(
        issue["code"] == "ACTION_CALL_WITHOUT_B2_ALLOW"
        for issue in check.details["issues"]
    )


def test_controlled_action_evaluator_does_not_serialize_action_response_body(tmp_path: Path) -> None:
    trace = _runtime(tmp_path).run(_request("sanitized"))
    report = ControlledActionEvaluator().evaluate(trace)
    serialized = report.model_dump_json()

    assert '"accepted":true' not in serialized
    assert "justification" not in serialized
    assert report.by_name()["controlled_action_execution"].details[
        "accepted_action_count"
    ] == 1


def test_controlled_action_evaluator_imports_no_private_or_provider_stack() -> None:
    source = inspect.getsource(controlled_eval_module)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
            imported_roots.add(node.module.split(".")[0])

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
