from __future__ import annotations

import json

from academy_tractian.decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from academy_tractian.evaluation import ProductionEvaluationPolicy, ProductionEvaluator
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry
from research.e2.models import BoundRequest, TraceEvent
from research.e2.transport import TransportResponse


class OneShotClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[ProviderDecisionRequest] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request)
        return self.response


class FixedClock:
    def __init__(self) -> None:
        self.values = iter((0, 1_000_000))

    def __call__(self) -> int:
        return next(self.values)


class FakeTransport:
    def request(self, request: BoundRequest) -> TransportResponse:
        return TransportResponse(status_code=200, headers={}, body={})


def _resequence(events: list[TraceEvent]) -> list[TraceEvent]:
    return [event.model_copy(update={"sequence": index}) for index, event in enumerate(events)]


def test_traced_provider_evaluator_rejects_duplicate_valid_model_call_id() -> None:
    raw = json.dumps(
        {
            "schema_version": "provider-decision-payload-v1",
            "kind": "ABSTAIN",
            "message": "No safe path",
        },
        sort_keys=True,
    )
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=OneShotClient(raw),
            registry=canonical_tool_registry(),
            call_identity=ProviderCallIdentity(
                provider_id="fake-provider",
                model_id="fake-model-v1",
                route_id="provider-free-contract-test",
                live_call=False,
            ),
            clock_ns=FixedClock(),
        ),
        transport=FakeTransport(),
    )
    trace = runtime.run(
        ProductionRequest(
            request_id="duplicate-valid-call",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect asset asset-1.",
        )
    )

    model_index = next(i for i, event in enumerate(trace.events) if event.event_type == "model_call")
    original = trace.events[model_index]
    duplicate = original.model_copy(update={"sequence": 0})
    decision_index = next(i for i, event in enumerate(trace.events) if event.event_type == "decision")
    events = [*trace.events[:decision_index], duplicate, *trace.events[decision_index:]]
    tampered = trace.model_copy(update={"events": _resequence(events)})

    report = ProductionEvaluator(
        policy=ProductionEvaluationPolicy(
            provider_free=False,
            require_model_call_provenance=True,
        )
    ).evaluate(tampered)
    issues = report.by_name()["model_call_provenance"].details["issues"]

    assert report.passed is False
    assert any(issue["code"] == "DUPLICATE_MODEL_CALL_ID" for issue in issues)
