from __future__ import annotations

import json

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.observability_store import ObservabilityStore
from academy_tractian.realtime_observability import DuckDBObservabilityEventSink
from academy_tractian.runtime import ProductionRequest, ProductionRuntime


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body={"asset_id": "asset-1", "status": "ok"},
        )


class ScriptedDecisionSource:
    def __init__(self, *decisions: ControllerDecision) -> None:
        self.decisions = list(decisions)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        if not self.decisions:
            raise AssertionError("script exhausted")
        return self.decisions.pop(0)


def _source() -> ScriptedDecisionSource:
    return ScriptedDecisionSource(
        ControllerDecision(
            kind=ControllerDecisionKind.TOOL,
            proposal=ToolProposal(
                tool_name="get_asset",
                arguments={"asset_id": "asset-1"},
                evidence_id="EV-live-asset",
            ),
        ),
        ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Asset evidence was inspected.",
            },
        ),
    )


def _request() -> ProductionRequest:
    return ProductionRequest(
        request_id="realtime-equivalence-1",
        identity_id="private-identity",
        user_id="private-user",
        user_request="Inspect asset-1.",
        seed="private-seed",
    )


def test_observable_runtime_preserves_exact_canonical_trace(tmp_path) -> None:
    baseline_transport = FakeTransport()
    baseline = ProductionRuntime(
        decision_source=_source(),
        transport=baseline_transport,
    ).run(_request())

    store = ObservabilityStore(tmp_path / "live.duckdb")
    observed_transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=_source(),
        transport=observed_transport,
        observability_sink=DuckDBObservabilityEventSink(store),
    )
    observed = runtime.run(_request())

    assert observed.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert observed_transport.calls == baseline_transport.calls
    assert runtime.observability_publisher is not None
    assert runtime.observability_publisher.failure_count == 0
    assert runtime.observability_publisher.published_count == len(observed.events)

    safe_run_id = runtime.observability_publisher.last_event_id.rsplit(":", 1)[0]
    persisted_run = store.get_run(safe_run_id)
    persisted_events = store.get_events(safe_run_id)
    assert persisted_run is not None
    assert persisted_run["completed"] is True
    assert len(persisted_events) == len(observed.events)
    assert [row["sequence"] for row in persisted_events] == list(range(len(observed.events)))

    serialized = json.dumps(
        {"run": persisted_run, "events": persisted_events},
        sort_keys=True,
        default=str,
    )
    assert "private-identity" not in serialized
    assert "private-user" not in serialized
    assert "private-seed" not in serialized


class ExplodingSink:
    def publish(self, *, run, event, evidence) -> None:
        raise RuntimeError("observability backend unavailable")


def test_sink_failure_cannot_change_runtime_trace_or_tool_execution() -> None:
    baseline_transport = FakeTransport()
    baseline = ProductionRuntime(
        decision_source=_source(),
        transport=baseline_transport,
    ).run(_request())

    observed_transport = FakeTransport()
    runtime = ProductionRuntime(
        decision_source=_source(),
        transport=observed_transport,
        observability_sink=ExplodingSink(),
    )
    observed = runtime.run(_request())

    assert observed.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert observed_transport.calls == baseline_transport.calls
    assert runtime.observability_publisher is not None
    assert runtime.observability_publisher.published_count == 0
    assert runtime.observability_publisher.failure_count == len(observed.events)


class InspectingSink:
    def __init__(self, store: ObservabilityStore) -> None:
        self.delegate = DuckDBObservabilityEventSink(store)
        self.store = store
        self.snapshots: list[tuple[str, bool, int]] = []

    def publish(self, *, run, event, evidence) -> None:
        self.delegate.publish(run=run, event=event, evidence=evidence)
        persisted = self.store.get_run(run.run_id)
        assert persisted is not None
        self.snapshots.append(
            (event.event_type, bool(persisted["completed"]), len(self.store.get_events(run.run_id)))
        )


def test_events_are_persisted_during_execution_not_only_after_finish(tmp_path) -> None:
    store = ObservabilityStore(tmp_path / "incremental.duckdb")
    sink = InspectingSink(store)
    runtime = ProductionRuntime(
        decision_source=_source(),
        transport=FakeTransport(),
        observability_sink=sink,
    )
    trace = runtime.run(_request())

    assert sink.snapshots[0] == ("run_started", False, 1)
    tool_call_snapshot = next(item for item in sink.snapshots if item[0] == "tool_call")
    assert tool_call_snapshot[1] is False
    assert tool_call_snapshot[2] < len(trace.events)
    assert sink.snapshots[-1] == ("run_finished", True, len(trace.events))
