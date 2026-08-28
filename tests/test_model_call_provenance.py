from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from academy_tractian.decision_source import (
    ProviderCallIdentity,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    ProviderModelCallRecord,
)
from academy_tractian.evaluation import ProductionEvaluationPolicy, ProductionEvaluator
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry
from research.e2.controller import ControllerDecision, ControllerDecisionKind, DecisionSourceAuditRecord, ToolProposal
from research.e2.models import BoundRequest, TraceEvent
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
        raise RuntimeError("provider-private-secret-text")


class FixedClock:
    def __init__(self, *values: int) -> None:
        self.values = list(values)

    def __call__(self) -> int:
        if not self.values:
            raise AssertionError("clock exhausted")
        return self.values.pop(0)


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(status_code=200, headers={}, body={"asset_id": "asset-1", "status": "ok"})


class MaliciousAuditSource:
    def decide(self, context):
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={"decision": "ORIENT", "response_mode": "complete", "message": "safe"},
        )

    def drain_audit_records(self):
        return (
            {
                "call_id": "0" * 64,
                "metadata": {"prompt": "sensitive-prompt-must-never-enter-trace"},
            },
        )


def _json(kind: str, **kwargs: Any) -> str:
    return json.dumps(
        {"schema_version": "provider-decision-payload-v1", "kind": kind, **kwargs},
        sort_keys=True,
    )


def _request(request_id: str = "provenance-1") -> ProductionRequest:
    return ProductionRequest(
        request_id=request_id,
        identity_id="identity-1",
        user_id="user-1",
        user_request="Inspect asset asset-1.",
        seed="runner-seed",
    )


def _identity() -> ProviderCallIdentity:
    return ProviderCallIdentity(
        provider_id="fake-provider",
        model_id="fake-model-v1",
        route_id="provider-free-contract-test",
        live_call=False,
    )


def _traced_policy() -> ProductionEvaluationPolicy:
    return ProductionEvaluationPolicy(
        provider_free=False,
        require_model_call_provenance=True,
    )


def _resequence(events: list[TraceEvent]) -> list[TraceEvent]:
    return [event.model_copy(update={"sequence": index}) for index, event in enumerate(events)]


def _model_calls(trace):
    return [event for event in trace.events if event.event_type == "model_call"]


def _final(trace):
    event = next(event for event in trace.events if event.event_type == "final_response")
    assert isinstance(event.result, dict)
    return event.result


def test_non_audited_provider_source_preserves_existing_trace_shape_and_provider_free_evaluation() -> None:
    raw = _json("ABSTAIN", message="No safe path", reason_code="NO_SAFE_PATH")
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=ScriptedProviderClient(raw),
            registry=canonical_tool_registry(),
        ),
        transport=FakeTransport(),
    )

    trace = runtime.run(_request())

    assert [event.event_type for event in trace.events] == [
        "run_started",
        "decision",
        "final_response",
        "run_finished",
    ]
    assert _model_calls(trace) == []
    assert ProductionEvaluator().evaluate(trace).passed is True


def test_audited_success_emits_one_self_verifying_model_call_before_decision() -> None:
    raw = _json("ABSTAIN", message="No safe path", reason_code="NO_SAFE_PATH")
    client = ScriptedProviderClient(raw)
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=client,
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(1_000_000_000, 1_007_000_000),
        ),
        transport=FakeTransport(),
    )

    trace = runtime.run(_request())
    calls = _model_calls(trace)

    assert len(client.calls) == 1
    assert len(calls) == 1
    call_event = calls[0]
    decision_event = next(event for event in trace.events if event.event_type == "decision")
    assert call_event.sequence < decision_event.sequence
    assert call_event.tool_name is None
    assert call_event.arguments is None
    assert call_event.result is None

    record = ProviderModelCallRecord.from_trace_event(
        call_id=call_event.call_id,
        metadata=call_event.metadata,
    )
    assert record.provider_id == "fake-provider"
    assert record.model_id == "fake-model-v1"
    assert record.route_id == "provider-free-contract-test"
    assert record.live_call is False
    assert record.outcome == "success"
    assert record.decision_kind is ControllerDecisionKind.ABSTAIN
    assert record.turn_index == 0
    assert record.tool_call_count == 0
    assert record.latency_ms == 7
    assert record.adapter_client_invocations == 1
    assert record.adapter_retry_count == 0
    assert record.adapter_fallback_used is False
    assert record.raw_request_recorded is False
    assert record.raw_response_recorded is False
    assert record.exception_text_recorded is False
    assert record.response_sha256 == sha256(raw.encode("utf-8")).hexdigest()

    serialized_event = json.dumps(call_event.model_dump(mode="json"), sort_keys=True)
    assert raw not in serialized_event
    assert "user-1" not in serialized_event
    assert "runner-seed" not in serialized_event


def test_call_id_is_deterministic_for_same_canonical_non_secret_inputs() -> None:
    raw = _json("ABSTAIN", message="No safe path", reason_code="NO_SAFE_PATH")
    call_ids: list[str] = []

    for request_id in ("deterministic-a", "deterministic-b"):
        runtime = ProductionRuntime(
            decision_source=ProviderDecisionSource(
                client=ScriptedProviderClient(raw),
                registry=canonical_tool_registry(),
                call_identity=_identity(),
                clock_ns=FixedClock(10, 20),
            ),
            transport=FakeTransport(),
        )
        trace = runtime.run(_request(request_id))
        call_ids.append(_model_calls(trace)[0].call_id or "")

    assert call_ids[0] == call_ids[1]
    assert len(call_ids[0]) == 64


def test_two_successful_provider_turns_each_emit_model_call_before_matching_decision() -> None:
    client = ScriptedProviderClient(
        _json("TOOL", tool_name="get_asset", arguments={"asset_id": "asset-1"}),
        _json(
            "FINAL",
            final={"decision": "ORIENT", "response_mode": "complete", "message": "Done."},
        ),
    )
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=client,
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 1_000_000, 2_000_000, 4_000_000),
        ),
        transport=FakeTransport(),
    )

    trace = runtime.run(_request("two-turns"))
    model_calls = _model_calls(trace)
    decisions = [event for event in trace.events if event.event_type == "decision"]

    assert len(model_calls) == 2
    assert len(decisions) == 2
    for model_call, decision in zip(model_calls, decisions):
        assert model_call.sequence < decision.sequence
        record = ProviderModelCallRecord.from_trace_event(
            call_id=model_call.call_id,
            metadata=model_call.metadata,
        )
        assert isinstance(decision.result, dict)
        assert decision.result["kind"] == record.decision_kind.value
        assert decision.result["turn_index"] == record.turn_index
        assert decision.result["tool_call_count"] == record.tool_call_count


def test_provider_failure_is_recorded_before_safe_abstention_without_exception_text() -> None:
    client = ExplodingProviderClient()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=client,
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 9_000_000),
        ),
        transport=FakeTransport(),
    )

    trace = runtime.run(_request("client-failure"))
    calls = _model_calls(trace)

    assert len(client.calls) == 1
    assert len(calls) == 1
    record = ProviderModelCallRecord.from_trace_event(
        call_id=calls[0].call_id,
        metadata=calls[0].metadata,
    )
    assert record.outcome == "failure"
    assert record.failure_code == "CLIENT_FAILURE"
    assert record.response_sha256 is None
    assert _final(trace)["reason_code"] == "DECISION_SOURCE_FAILURE"
    assert calls[0].sequence < next(
        event.sequence for event in trace.events if event.event_type == "state_change"
    )
    serialized = trace.model_dump_json()
    assert "provider-private-secret-text" not in serialized


def test_malformed_provider_output_records_sanitized_failure_before_decision_source_failure() -> None:
    raw = "not-json-sensitive-body"
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=ScriptedProviderClient(raw),
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 3_000_000),
        ),
        transport=FakeTransport(),
    )

    trace = runtime.run(_request("bad-json"))
    calls = _model_calls(trace)
    record = ProviderModelCallRecord.from_trace_event(
        call_id=calls[0].call_id,
        metadata=calls[0].metadata,
    )

    assert record.failure_code == "RESPONSE_JSON_INVALID"
    assert record.response_sha256 == sha256(raw.encode("utf-8")).hexdigest()
    assert _final(trace)["reason_code"] == "DECISION_SOURCE_FAILURE"
    assert raw not in trace.model_dump_json()


def test_default_provider_free_evaluator_rejects_audited_model_calls() -> None:
    raw = _json("ABSTAIN")
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=ScriptedProviderClient(raw),
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 1),
        ),
        transport=FakeTransport(),
    )

    report = ProductionEvaluator().evaluate(runtime.run(_request("provider-free-reject")))

    assert report.passed is False
    assert report.by_name()["provider_free_trace"].passed is False
    assert report.by_name()["model_call_provenance"].passed is False


def test_explicit_traced_provider_evaluator_accepts_valid_provider_free_fake_provenance() -> None:
    raw = _json("ABSTAIN", message="No safe path")
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=ScriptedProviderClient(raw),
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 5_000_000),
        ),
        transport=FakeTransport(),
    )

    report = ProductionEvaluator(policy=_traced_policy()).evaluate(
        runtime.run(_request("traced-provider-valid"))
    )
    provenance = report.by_name()["model_call_provenance"]

    assert report.passed is True
    assert provenance.passed is True
    assert provenance.details["model_call_count"] == 1
    assert provenance.details["calls"][0]["live_call"] is False
    assert "request_sha256" not in provenance.details["calls"][0]
    assert "response_sha256" not in provenance.details["calls"][0]


def test_traced_provider_evaluator_rejects_tampered_call_id() -> None:
    raw = _json("ABSTAIN")
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=ScriptedProviderClient(raw),
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 1),
        ),
        transport=FakeTransport(),
    )
    trace = runtime.run(_request("tampered-call-id"))
    events = list(trace.events)
    index = next(i for i, event in enumerate(events) if event.event_type == "model_call")
    events[index] = events[index].model_copy(update={"call_id": "0" * 64})
    tampered = trace.model_copy(update={"events": events})

    report = ProductionEvaluator(policy=_traced_policy()).evaluate(tampered)
    issues = report.by_name()["model_call_provenance"].details["issues"]

    assert report.passed is False
    assert any(issue["code"] == "INVALID_MODEL_CALL_RECORD" for issue in issues)


def test_traced_provider_evaluator_rejects_duplicate_call_id_and_invalid_metadata() -> None:
    raw = _json("ABSTAIN")
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=ScriptedProviderClient(raw),
            registry=canonical_tool_registry(),
            call_identity=_identity(),
            clock_ns=FixedClock(0, 1),
        ),
        transport=FakeTransport(),
    )
    trace = runtime.run(_request("duplicate-call"))
    original = next(event for event in trace.events if event.event_type == "model_call")
    injected = original.model_copy(
        update={
            "sequence": 0,
            "metadata": {**original.metadata, "raw_response": "sensitive"},
        }
    )
    decision_index = next(i for i, event in enumerate(trace.events) if event.event_type == "decision")
    events = [*trace.events[:decision_index], injected, *trace.events[decision_index:]]
    tampered = trace.model_copy(update={"events": _resequence(events)})

    report = ProductionEvaluator(policy=_traced_policy()).evaluate(tampered)
    issues = report.by_name()["model_call_provenance"].details["issues"]

    assert report.passed is False
    assert any(issue["code"] == "INVALID_MODEL_CALL_RECORD" for issue in issues)


def test_malicious_audit_metadata_is_rejected_before_it_can_enter_trace() -> None:
    runtime = ProductionRuntime(
        decision_source=MaliciousAuditSource(),
        transport=FakeTransport(),
    )

    trace = runtime.run(_request("malicious-audit"))

    assert _model_calls(trace) == []
    assert _final(trace)["reason_code"] == "DECISION_SOURCE_AUDIT_FAILURE"
    assert "sensitive-prompt-must-never-enter-trace" not in trace.model_dump_json()


def test_audit_record_rejects_nested_metadata_before_trace_insertion() -> None:
    try:
        DecisionSourceAuditRecord(
            call_id="0" * 64,
            metadata={"provider_id": {"nested": "forbidden"}},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("nested audit metadata must be rejected")
