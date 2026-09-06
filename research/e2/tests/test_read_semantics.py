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


def test_trace_evaluator_classifies_existing_raw_runner_trace_without_mutation() -> None:
    transport = StaticTransport(
        TransportResponse(200, {}, {"mode": "conflict", "data": {"sources": 2}})
    )
    runner = make_runner(transport=transport)
    runner.execute_tool("get_data_quality", {"asset_id": "asset_a"}, evidence_id="dq")
    before = runner.trace.model_dump(mode="json")

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate(list(runner.trace.events))

    assert runner.trace.model_dump(mode="json") == before
    assert report.schema_version == READ_SEMANTICS_VERSION
    assert report.passed
    assert report.read_result_count == 1
    assert report.assessed_result_count == 1
    assert report.contract_issue_count == 0
    assert report.mode_counts["conflict"] == 1
    entry = report.entries[0]
    assert entry.tool_name == "get_data_quality"
    assert entry.response_mode is ResponseMode.CONFLICT
    assert entry.source == "structured_mode"
    assert entry.status_code == 200
    assert entry.issue_code is None


def test_trace_evaluator_fails_acceptance_on_missing_mode_but_preserves_safe_classification() -> None:
    raw_body = {"message": "complete according to prose only"}
    runner = make_runner(transport=StaticTransport(TransportResponse(200, {}, raw_body)))
    runner.execute_tool("get_asset", {"asset_id": "asset_a"}, evidence_id="asset")

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate(list(runner.trace.events))
    observation = next(event for event in runner.trace.events if event.event_type == "observation")

    assert not report.passed
    assert report.contract_issue_count == 1
    assert report.entries[0].response_mode is ResponseMode.INCONCLUSIVE
    assert report.entries[0].source == "fail_closed"
    assert report.entries[0].issue_code == "MISSING_MODE"
    assert observation.result == raw_body


def test_live_and_replay_yield_identical_semantic_reports() -> None:
    replay = ReplayStore()
    live = make_runner(
        transport=StaticTransport(TransportResponse(200, {}, {"mode": "partial", "data": [1]})),
        replay=replay,
        mode="live",
    )
    live.execute_tool("get_rms", {"asset_id": "asset_a"})

    replay_runner = make_runner(
        transport=ExplodingTransport(),
        replay=replay,
        mode="replay",
    )
    replay_runner.execute_tool("get_rms", {"asset_id": "asset_a"})

    evaluator = ReadSemanticsTraceEvaluator(REGISTRY)
    live_report = evaluator.evaluate(list(live.trace.events))
    replay_report = evaluator.evaluate(list(replay_runner.trace.events))

    assert live_report.entries == replay_report.entries
    assert replay_report.passed
    assert replay_report.mode_counts["partial"] == 1


def test_existing_uninstrumented_tool_result_is_still_in_evaluator_denominator() -> None:
    legacy_read = TraceEvent(
        sequence=0,
        event_type="tool_result",
        tool_name="get_asset",
        result={"status_code": 200, "headers": {}, "body": {"mode": "complete"}},
        metadata={"status_code": 200},
    )

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate([legacy_read])

    assert report.passed
    assert report.read_result_count == 1
    assert report.assessed_result_count == 1
    assert report.mode_counts["complete"] == 1


def test_trace_evaluator_rejects_status_code_mismatch_fail_closed() -> None:
    tampered = TraceEvent(
        sequence=0,
        event_type="tool_result",
        tool_name="get_asset",
        result={"status_code": 200, "headers": {}, "body": {"mode": "complete"}},
        metadata={"status_code": 503},
    )

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate([tampered])

    assert not report.passed
    assert report.contract_issue_count == 1
    assert report.entries[0].response_mode is ResponseMode.INCONCLUSIVE
    assert report.entries[0].issue_code == "STATUS_CODE_MISMATCH"


def test_trace_evaluator_does_not_trust_forged_read_kind_for_action() -> None:
    forged_action = TraceEvent(
        sequence=0,
        event_type="tool_result",
        tool_name="reprocess_analysis",
        result={"status_code": 200, "headers": {}, "body": {"mode": "complete"}},
        metadata={"status_code": 200, "kind": "read"},
    )

    report = ReadSemanticsTraceEvaluator(REGISTRY).evaluate([forged_action])

    assert report.passed
    assert report.read_result_count == 0
    assert report.assessed_result_count == 0


def test_controller_provider_facing_observation_schema_is_unchanged_in_v1() -> None:
    # The provider already receives the raw structured body. Adding a new observation field would
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
