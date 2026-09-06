from __future__ import annotations

import pytest

from research.e2.controller import ControllerObservation
from research.e2.models import ExecutionBinding, ResponseMode, TraceEvent
from research.e2.read_semantics import (
    READ_SEMANTICS_VERSION,
    ReadSemanticsTraceEvaluator,
    classify_read_response,
)
from research.e2.replay import ReplayStore
from research.e2.runner import HarnessRunner
from research.e2.tool_registry import TOOLS, get_tool
from research.e2.transport import TransportResponse


REGISTRY = {tool.name: tool for tool in TOOLS}


@pytest.mark.parametrize("mode", list(ResponseMode))
def test_structured_read_modes_are_preserved_exactly(mode: ResponseMode) -> None:
    assessment = classify_read_response(
        tool=get_tool("get_asset"),
        response=TransportResponse(200, {}, {"mode": mode.value, "data": {"ok": True}}),
    )

    assert assessment.response_mode is mode
    assert assessment.source == "structured_mode"
    assert assessment.issue_code is None


def test_non_2xx_status_takes_precedence_over_body_claim() -> None:
    assessment = classify_read_response(
        tool=get_tool("get_rms"),
        response=TransportResponse(503, {}, {"mode": "complete", "message": "stale body"}),
    )

    assert assessment.response_mode is ResponseMode.UNAVAILABLE
    assert assessment.source == "http_status"
    assert assessment.issue_code is None


@pytest.mark.parametrize(
    ("body", "issue_code"),
    [
        ("complete", "NON_OBJECT_BODY"),
        ({"data": {"ok": True}}, "MISSING_MODE"),
        ({"mode": "mystery", "message": "this prose says complete"}, "INVALID_MODE"),
        ({"mode": 1}, "INVALID_MODE"),
    ],
)
def test_successful_http_without_valid_structured_mode_fails_closed(
    body,
    issue_code: str,
) -> None:
    assessment = classify_read_response(
        tool=get_tool("get_analysis"),
        response=TransportResponse(200, {}, body),
    )

    assert assessment.response_mode is ResponseMode.INCONCLUSIVE
    assert assessment.source == "fail_closed"
    assert assessment.issue_code == issue_code


def test_classifier_rejects_action_acknowledgements() -> None:
    with pytest.raises(ValueError, match="only accepts read tools"):
        classify_read_response(
            tool=get_tool("reprocess_analysis"),
            response=TransportResponse(200, {}, {"accepted": True}),
        )


class StaticTransport:
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls = []

    def request(self, request):
        self.calls.append(request)
        return self.response


class ExplodingTransport:
    def request(self, request):
        raise AssertionError("replay must not call live transport")


def make_runner(*, transport, replay: ReplayStore | None = None, mode: str = "live") -> HarnessRunner:
    return HarnessRunner(
        run_id=f"read-semantics-{mode}",
        scenario_id="CEN-01",
        config_hash="d" * 64,
        registry=REGISTRY,
        binding=ExecutionBinding(
            identity_id="read-semantics-binding",
            user_id="usr-read-semantics",
            seed="CEN-01",
        ),
        transport=transport,
        replay=replay,
        execution_mode=mode,
        strict_arguments=True,
    )


def test_runner_preserves_semantic_state_in_execution_result_and_trace() -> None:
    transport = StaticTransport(
        TransportResponse(200, {}, {"mode": "conflict", "data": {"sources": 2}})
    )
    runner = make_runner(transport=transport)

    execution = runner.execute_tool("get_data_quality", {"asset_id": "asset_a"}, evidence_id="dq")

    assert execution.read_semantics is not None
    assert execution.read_semantics.response_mode is ResponseMode.CONFLICT

    tool_result = next(event for event in runner.trace.events if event.event_type == "tool_result")
    observation = next(event for event in runner.trace.events if event.event_type == "observation")
    for event in (tool_result, observation):
        assert event.metadata["kind"] == "read"
        assert event.metadata["read_semantics_version"] == READ_SEMANTICS_VERSION
        assert event.metadata["response_mode"] == "conflict"
        assert event.metadata["response_mode_source"] == "structured_mode"
        assert "response_mode_issue_code" not in event.metadata

    assert tool_result.result["response_mode"] == "conflict"
    assert observation.result == {"mode": "conflict", "data": {"sources": 2}}


def test_runner_records_fail_closed_issue_without_rewriting_raw_body() -> None:
    raw_body = {"message": "complete according to prose only"}
    runner = make_runner(transport=StaticTransport(TransportResponse(200, {}, raw_body)))

    execution = runner.execute_tool("get_asset", {"asset_id": "asset_a"}, evidence_id="asset")

    assert execution.read_semantics is not None
    assert execution.read_semantics.response_mode is ResponseMode.INCONCLUSIVE
    observation = next(event for event in runner.trace.events if event.event_type == "observation")
    assert observation.result == raw_body
    assert observation.metadata["response_mode"] == "inconclusive"
    assert observation.metadata["response_mode_source"] == "fail_closed"
    assert observation.metadata["response_mode_issue_code"] == "MISSING_MODE"


def test_live_and_replay_recompute_identical_read_semantics() -> None:
    replay = ReplayStore()
    live = make_runner(
        transport=StaticTransport(TransportResponse(200, {}, {"mode": "partial", "data": [1]})),
        replay=replay,
        mode="live",
    )
    live_execution = live.execute_tool("get_rms", {"asset_id": "asset_a"})

    replay_runner = make_runner(
        transport=ExplodingTransport(),
        replay=replay,
        mode="replay",
    )
    replay_execution = replay_runner.execute_tool("get_rms", {"asset_id": "asset_a"})

    assert live_execution.read_semantics == replay_execution.read_semantics
    assert replay_execution.read_semantics is not None
    assert replay_execution.read_semantics.response_mode is ResponseMode.PARTIAL


def test_trace_evaluator_measures_coverage_and_contract_issues() -> None:
    runner = make_runner(
        transport=StaticTransport(TransportResponse(200, {}, {"mode": "inconclusive"}))
    )
    runner.execute_tool("get_model", {"model_id": "model_a"})

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate(list(runner.trace.events))

    assert report.passed
    assert report.read_result_count == 1
    assert report.covered_result_count == 1
    assert report.contract_issue_count == 0
    assert report.mode_counts["inconclusive"] == 1


def test_trace_evaluator_rejects_uninstrumented_read_result() -> None:
    legacy_read = TraceEvent(
        sequence=0,
        event_type="tool_result",
        tool_name="get_asset",
        result={"status_code": 200, "body": {"mode": "complete"}},
        metadata={"status_code": 200},
    )

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate([legacy_read])

    assert not report.passed
    assert report.read_result_count == 1
    assert report.covered_result_count == 0
    assert report.contract_issue_count == 0


def test_trace_evaluator_does_not_trust_forged_read_kind_for_action() -> None:
    forged_action = TraceEvent(
        sequence=0,
        event_type="tool_result",
        tool_name="reprocess_analysis",
        result={"status_code": 200, "body": {"accepted": True}},
        metadata={
            "kind": "read",
            "read_semantics_version": READ_SEMANTICS_VERSION,
            "response_mode": "complete",
            "response_mode_source": "structured_mode",
        },
    )

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate([forged_action])

    assert report.passed
    assert report.read_result_count == 0
    assert report.covered_result_count == 0


def test_controller_provider_facing_observation_schema_is_unchanged_in_v1() -> None:
    # Semantic read state is trace/evaluator-owned in this gate. Exposing it to the model would
    # change provider-decision-request-v1 hashes and requires an explicit versioned protocol step.
    assert "response_mode" not in ControllerObservation.model_fields
    assert set(ControllerObservation.model_fields) == {
        "tool_name",
        "status",
        "executed",
        "blocked_code",
        "status_code",
        "body",
        "error_code",
    }
