from __future__ import annotations

import ast
import inspect

from academy_tractian.evaluation import (
    IntegratedProductionRunner,
    ProductionEvaluator,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime
import academy_tractian.evaluation as evaluation_module
from research.e2.controller import ControllerDecision, ControllerDecisionKind, ControllerContext, ToolProposal
from research.e2.models import BoundRequest, RunTrace, TraceEvent
from research.e2.transport import TransportResponse


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body={"asset_id": "asset-1", "status": "ok", "internal_payload": "not-for-report"},
        )


class ExplodingTransport:
    def request(self, request: BoundRequest) -> TransportResponse:
        raise RuntimeError("transport-private-detail")


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)
        self.contexts: list[ControllerContext] = []

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.contexts.append(context)
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


def _request() -> ProductionRequest:
    return ProductionRequest(
        request_id="eval-req-1",
        identity_id="identity-1",
        user_id="user-1",
        user_request="Inspect asset asset-1.",
        seed="seed-1",
    )


def _final(message: str = "Inspection complete.") -> ControllerDecision:
    return ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={
            "decision": "ORIENT",
            "response_mode": "complete",
            "message": message,
        },
    )


def _read_runtime(transport=None) -> ProductionRuntime:
    return ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-1"},
                    evidence_id="asset-context",
                ),
            ),
            _final(),
        ),
        transport=transport or FakeTransport(),
    )


def _resequence(events: list[TraceEvent]) -> list[TraceEvent]:
    return [event.model_copy(update={"sequence": index}) for index, event in enumerate(events)]


def test_healthy_read_trace_passes_blocking_checks_without_copying_response_body() -> None:
    trace = _read_runtime().run(_request())
    report = ProductionEvaluator().evaluate(trace)

    assert report.passed is True
    assert all(check.passed for check in report.checks if check.blocking)
    assert report.run_id == trace.run_id
    assert report.scenario_id == trace.scenario_id
    assert report.config_hash == trace.config_hash
    serialized = report.model_dump_json()
    assert "not-for-report" not in serialized
    assert "internal_payload" not in serialized


def test_blocked_action_is_contained_and_never_counted_as_executed_action() -> None:
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="update_asset_config",
                    arguments={
                        "asset_id": "asset-1",
                        "body": {
                            "justification": "Evidence reviewed; action remains disabled in this slice.",
                            "changes": {"criticality": "high"},
                        },
                    },
                ),
            ),
            _final("No action was executed."),
        ),
        transport=transport,
    )

    report = ProductionEvaluator().evaluate(runtime.run(_request()))
    checks = report.by_name()

    assert transport.calls == []
    assert report.passed is True
    assert checks["policy_denial_containment"].passed is True
    assert checks["contained_policy_denials"].details["count"] == 1
    assert checks["read_only_action_safety"].passed is True
    assert checks["read_only_action_safety"].details["executed_actions"] == []


def test_invalid_arguments_fail_contract_check_but_preserve_policy_containment() -> None:
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(tool_name="get_asset", arguments={}),
            ),
            _final("Invalid proposal was contained."),
        ),
        transport=transport,
    )

    report = ProductionEvaluator().evaluate(runtime.run(_request()))
    checks = report.by_name()

    assert transport.calls == []
    assert report.passed is False
    assert checks["proposal_contract_validity"].passed is False
    assert checks["policy_denial_containment"].passed is True
    assert checks["contained_policy_denials"].details["count"] == 1


def test_tool_boundary_failure_is_a_valid_contained_failure_trace() -> None:
    runtime = ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-1"},
                ),
            )
        ),
        transport=ExplodingTransport(),
    )

    trace = runtime.run(_request())
    report = ProductionEvaluator().evaluate(trace)
    checks = report.by_name()

    assert report.passed is True
    assert checks["execution_chain_integrity"].passed is True
    assert checks["terminal_consistency"].details["reason_code"] == "TOOL_BOUNDARY_FAILURE"
    assert "transport-private-detail" not in trace.model_dump_json()
    assert "transport-private-detail" not in report.model_dump_json()


def test_terminal_only_paths_are_structurally_valid() -> None:
    decisions = (
        _final(),
        ControllerDecision(
            kind=ControllerDecisionKind.CLARIFY,
            message="Which asset should be inspected?",
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.ESCALATE,
            message="Human review is required.",
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.ABSTAIN,
            message="Evidence is unavailable.",
        ),
    )

    for index, decision in enumerate(decisions):
        runtime = ProductionRuntime(
            decision_source=ScriptedDecisionSource(decision),
            transport=FakeTransport(),
        )
        request = _request().model_copy(update={"request_id": f"terminal-{index}"})
        report = ProductionEvaluator().evaluate(runtime.run(request))
        assert report.passed is True


def test_missing_tool_result_is_detected_when_no_boundary_failure_exists() -> None:
    trace = _read_runtime().run(_request())
    events = [event for event in trace.events if event.event_type != "tool_result"]
    tampered = trace.model_copy(update={"events": _resequence(events)})

    report = ProductionEvaluator().evaluate(tampered)
    issues = report.by_name()["execution_chain_integrity"].details["issues"]

    assert report.passed is False
    assert any(issue["code"] == "MISSING_TOOL_RESULT" for issue in issues)


def test_missing_run_finished_fails_lifecycle() -> None:
    trace = _read_runtime().run(_request())
    tampered = trace.model_copy(update={"events": _resequence(trace.events[:-1])})

    report = ProductionEvaluator().evaluate(tampered)

    assert report.passed is False
    assert report.by_name()["trace_lifecycle"].passed is False


def test_injected_action_tool_call_fails_read_only_safety_even_if_trace_is_well_formed() -> None:
    transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=ScriptedDecisionSource(
            ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="update_asset_config",
                    arguments={
                        "asset_id": "asset-1",
                        "body": {
                            "justification": "Evidence reviewed; action remains disabled in this slice.",
                            "changes": {"criticality": "high"},
                        },
                    },
                ),
            ),
            _final("No action was executed."),
        ),
        transport=transport,
    )
    trace = runtime.run(_request())
    policy_index = next(
        index
        for index, event in enumerate(trace.events)
        if event.event_type == "policy_check" and event.tool_name == "update_asset_config"
    )
    proposal = next(
        event
        for event in trace.events
        if event.event_type == "tool_proposal" and event.tool_name == "update_asset_config"
    )
    injected = [
        TraceEvent(
            sequence=0,
            event_type="tool_call",
            tool_name="update_asset_config",
            arguments=dict(proposal.arguments or {}),
            metadata={
                "method": "PATCH",
                "path": "/assets/{assetId}",
                "resolved_path": "/assets/asset-1",
                "kind": "action",
            },
        ),
        TraceEvent(
            sequence=0,
            event_type="tool_result",
            tool_name="update_asset_config",
            result={"status_code": 202, "headers": {}, "body": {"accepted": True}},
            metadata={"status_code": 202},
        ),
        TraceEvent(
            sequence=0,
            event_type="observation",
            tool_name="update_asset_config",
            result={"accepted": True},
            metadata={"status_code": 202},
        ),
    ]
    events = [*trace.events[: policy_index + 1], *injected, *trace.events[policy_index + 1 :]]
    tampered = trace.model_copy(update={"events": _resequence(events)})

    report = ProductionEvaluator().evaluate(tampered)
    action_check = report.by_name()["read_only_action_safety"]

    assert report.passed is False
    assert action_check.passed is False
    assert action_check.details["executed_actions"][0]["tool_name"] == "update_asset_config"


def test_trace_hash_is_stable_for_same_canonical_trace() -> None:
    trace = _read_runtime().run(_request())
    evaluator = ProductionEvaluator()

    first = evaluator.evaluate(trace)
    second = evaluator.evaluate(trace.model_copy(deep=True))

    assert first.trace_sha256 == second.trace_sha256


class RecordingEvaluator:
    def __init__(self) -> None:
        self.seen: RunTrace | None = None
        self.delegate = ProductionEvaluator()

    def evaluate(self, trace: RunTrace):
        self.seen = trace
        return self.delegate.evaluate(trace)


def test_integrated_runner_evaluates_the_exact_runtime_trace_instance() -> None:
    evaluator = RecordingEvaluator()
    runner = IntegratedProductionRunner(runtime=_read_runtime(), evaluator=evaluator)

    result = runner.run(_request())

    assert evaluator.seen is result.trace
    assert result.evaluation.run_id == result.trace.run_id
    assert result.evaluation.trace_sha256 == ProductionEvaluator().evaluate(result.trace).trace_sha256


def test_production_evaluator_imports_no_private_or_semantic_evaluator_stack() -> None:
    tree = ast.parse(inspect.getsource(evaluation_module))
    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
            imported_names.update(alias.name for alias in node.names)

    forbidden_modules = {
        "research.e2.evaluation_suite",
        "research.e2.evaluator_extensions",
        "research.e2.evaluators",
        "anthropic",
        "cerebras",
        "groq",
        "langchain",
        "langgraph",
        "openai",
        "pydantic_ai",
    }
    assert imported_modules.isdisjoint(forbidden_modules)
    assert "Scenario" not in imported_names
    assert "EvaluationSuite" not in imported_names
