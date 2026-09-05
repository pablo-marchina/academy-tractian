from __future__ import annotations

from threading import Event

from fastapi.testclient import TestClient

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.observability_store import ObservabilityStore
from academy_tractian.product_api import AuthenticatedRuntimeContext, create_product_app
from academy_tractian.realtime_runtime import RealtimeProductionRuntime
from academy_tractian.run_access import DuckDBRunAccessStore
from academy_tractian.run_execution_store import DuckDBRunExecutionStore


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


class ToolThenFinalSource:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        self.calls += 1
        if self.calls == 1:
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-1"},
                    evidence_id="EV-operability-asset",
                ),
            )
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Measured operability path completed.",
            },
        )


class BlockingFinalSource:
    def __init__(self, *, entered: Event, release: Event) -> None:
        self.entered = entered
        self.release = release

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        self.entered.set()
        if not self.release.wait(timeout=10):
            raise RuntimeError("release timeout")
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Released.",
            },
        )


class FailingSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        raise RuntimeError("provider-free synthetic execution failure")


def _context(_request) -> AuthenticatedRuntimeContext:
    return AuthenticatedRuntimeContext(identity_id="identity", user_id="user")


def _component(health: dict, name: str) -> dict:
    return next(item for item in health["components"] if item["component"] == name)


def _explicit_local_test_stores(tmp_path, prefix: str):
    return {
        "observability_store": ObservabilityStore(tmp_path / f"{prefix}.observability.duckdb"),
        "run_access_store": DuckDBRunAccessStore(tmp_path / f"{prefix}.access.duckdb"),
        "execution_store": DuckDBRunExecutionStore(tmp_path / f"{prefix}.execution.duckdb"),
    }


def test_health_reports_real_quantitative_runtime_api_sse_resource_and_adapter_metrics(tmp_path) -> None:
    transports: list[FakeTransport] = []

    def runtime_factory(sink) -> RealtimeProductionRuntime:
        transport = FakeTransport()
        transports.append(transport)
        return RealtimeProductionRuntime(
            decision_source=ToolThenFinalSource(),
            transport=transport,
            observability_sink=sink,
        )

    app = create_product_app(
        **_explicit_local_test_stores(tmp_path, "operability"),
        runtime_factory=runtime_factory,
        context_provider=_context,
        max_workers=2,
        heartbeat_interval_ms=250,
    )

    with TestClient(app) as client:
        accepted = client.post(
            "/api/runs",
            json={"user_request": "Inspect asset-1."},
        ).json()
        run_id = accepted["run_id"]
        future = app.state.run_execution_registry.future(run_id)
        assert future is not None
        future.result(timeout=10)

        replay = client.get(f"{accepted['stream_path']}&follow=false")
        assert replay.status_code == 200
        assert "event: trace_event" in replay.text

        reconnect = client.get(
            f"{accepted['stream_path']}&follow=false",
            headers={"Last-Event-ID": f"{run_id}:0"},
        )
        assert reconnect.status_code == 200
        assert f"id: {run_id}:0" not in reconnect.text
        assert "event: trace_event" in reconnect.text

        assert client.get("/api/query/schema").status_code == 200
        query = client.post(
            "/api/query",
            json={
                "dataset": "runs",
                "run_id": run_id,
                "dimensions": [],
                "measure": "count",
                "filters": [],
                "chart_type": "table",
                "limit": 20,
            },
        )
        assert query.status_code == 200

        health = client.get("/api/production/health").json()
        assert health["schema_version"] == "production-health-v3"
        assert health["overall_status"] == "ready"
        assert health["quantitative_measurement_contract"]["thresholds_preregistered"] is False
        assert _component(health, "runtime")["status"] == "ready"
        assert _component(health, "sse_clients")["status"] == "instrumented"
        assert _component(health, "provider_kill_switch")["status"] == "disengaged"
        assert _component(health, "action_kill_switch")["status"] == "engaged"
        assert _component(health, "executor_pressure")["status"] == "measured"
        assert _component(health, "tractian_api_adapter")["status"] == "observed"

        measured = health["measured"]
        assert measured["startup_readiness_ms"] is not None
        assert measured["runtime_heartbeat"]["age_ms"] is not None
        assert measured["executor_pressure"]["max_workers"] == 2
        assert measured["executor_pressure"]["active_runs"] == 0
        assert measured["controls"]["provider_kill_switch"]["engaged"] is False
        assert measured["controls"]["action_kill_switch"]["engaged"] is True

        runtime_requests = measured["runtime_requests"]
        assert runtime_requests["sample_count"] >= 1
        assert runtime_requests["request_latency"]["p50_ms"] is not None
        assert runtime_requests["request_latency"]["p95_ms"] is not None
        assert runtime_requests["execution_latency"]["p95_ms"] is not None
        assert runtime_requests["by_outcome"]["completed"]["count"] >= 1
        assert runtime_requests["by_terminal_decision"]["ORIENT"]["count"] >= 1
        assert runtime_requests["by_response_mode"]["complete"]["count"] >= 1

        api = measured["api"]
        assert api["sample_count"] > 0
        assert api["request_latency"]["p95_ms"] is not None
        assert api["by_kind"]["runtime_submit"]["count"] >= 1
        assert api["by_kind"]["analytics_query"]["count"] >= 1
        assert api["by_kind"]["analytics_schema"]["count"] >= 1

        resources = measured["resources"]
        assert resources["process_cpu_time_ms"] >= 0
        assert resources["threshold_interpretation"] == "not_preregistered"
        assert resources["rss_current_source"] in {"proc_self_statm", "unavailable"}
        assert resources["rss_max_source"] in {"resource_getrusage", "unavailable"}

        observability = measured["observability"]
        assert observability["publish_overhead"]["count"] > 0
        assert observability["persistence_duration"]["count"] > 0
        assert observability["runtime_event_to_persistence"]["count"] > 0
        assert observability["publisher_failures"] == 0

        sse = measured["sse"]
        assert sse["active_clients"] == 0
        assert sse["connections_opened"] >= 2
        assert sse["connections_closed"] >= 2
        assert sse["reconnects"] >= 1
        assert sse["events_delivered"] > 0
        assert sse["persistence_to_delivery"]["count"] > 0
        assert sse["reconnect_recovery"]["count"] >= 1
        assert sse["reconnect_first_event_checks"] >= 1
        assert sse["reconnect_sequential_recovery_rate"] == 1.0
        assert sse["detected_gap_events"] == 0
        assert sse["detected_gap_rate"] == 0.0
        assert sse["logical_duplicate_events"] == 0
        assert sse["logical_duplicate_rate"] == 0.0

        for closed_gap in (
            "runtime_request_latency_by_outcome_ms",
            "api_read_query_latency_ms",
            "cpu_memory_pressure",
            "reconnect_event_loss_rate",
            "logical_duplicate_delivery_rate",
        ):
            assert closed_gap not in health["not_measured_yet"]

        adapter = measured["tractian_adapter_operability"]
        assert adapter["observations"] >= 1
        assert adapter["http_2xx"] >= 1
        assert adapter["external_probe_performed"] is False
        assert len(transports) == 1
        assert len(transports[0].calls) == 1


def test_decision_source_failure_is_completed_safe_abstention_slice_without_private_material(tmp_path) -> None:
    def runtime_factory(sink) -> RealtimeProductionRuntime:
        return RealtimeProductionRuntime(
            decision_source=FailingSource(),
            transport=FakeTransport(),
            observability_sink=sink,
        )

    app = create_product_app(
        **_explicit_local_test_stores(tmp_path, "handled-failure"),
        runtime_factory=runtime_factory,
        context_provider=_context,
        heartbeat_interval_ms=250,
    )

    with TestClient(app) as client:
        accepted = client.post("/api/runs", json={"user_request": "Fail safely."}).json()
        future = app.state.run_execution_registry.future(accepted["run_id"])
        assert future is not None
        future.result(timeout=10)
        assert app.state.run_execution_registry.status(accepted["run_id"]) == "completed"

        run = client.get(accepted["run_path"]).json()
        assert run["terminal_decision"] == "ABSTAIN"
        assert run["terminal_response_mode"] == "unavailable"

        health = client.get("/api/production/health").json()
        runtime_requests = health["measured"]["runtime_requests"]
        assert runtime_requests["by_outcome"]["completed"]["count"] == 1
        assert runtime_requests["by_terminal_decision"]["ABSTAIN"]["count"] == 1
        assert runtime_requests["by_response_mode"]["unavailable"]["count"] == 1
        serialized = str(runtime_requests).lower()
        assert "identity" not in serialized
        assert "user" not in serialized
        assert "seed" not in serialized
        assert "fail safely" not in serialized


def test_provider_kill_switch_blocks_before_runtime_factory(tmp_path) -> None:
    factory_calls = 0

    def runtime_factory(_sink) -> RealtimeProductionRuntime:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("runtime factory must not run while provider switch is engaged")

    app = create_product_app(
        **_explicit_local_test_stores(tmp_path, "kill-switch"),
        runtime_factory=runtime_factory,
        context_provider=_context,
        provider_calls_enabled=False,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            json={"user_request": "Do not reach provider construction."},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "provider_kill_switch_engaged"
        assert factory_calls == 0

        health = client.get("/api/production/health").json()
        assert _component(health, "provider_kill_switch")["status"] == "engaged"
        assert health["measured"]["controls"]["provider_kill_switch"]["provider_calls_enabled"] is False


def test_executor_pressure_reports_one_running_and_one_queued_with_single_worker(tmp_path) -> None:
    release = Event()
    entered_events: list[Event] = []

    def runtime_factory(sink) -> RealtimeProductionRuntime:
        entered = Event()
        entered_events.append(entered)
        return RealtimeProductionRuntime(
            decision_source=BlockingFinalSource(entered=entered, release=release),
            transport=FakeTransport(),
            observability_sink=sink,
        )

    app = create_product_app(
        **_explicit_local_test_stores(tmp_path, "pressure"),
        runtime_factory=runtime_factory,
        context_provider=_context,
        max_workers=1,
        heartbeat_interval_ms=250,
    )

    with TestClient(app) as client:
        first = client.post("/api/runs", json={"user_request": "First."}).json()
        assert entered_events[0].wait(timeout=5)

        second = client.post("/api/runs", json={"user_request": "Second."}).json()
        health = client.get("/api/production/health").json()
        pressure = health["measured"]["executor_pressure"]
        assert pressure["active_runs"] == 1
        assert pressure["queued_runs"] == 1
        assert pressure["inflight_runs"] == 2
        assert pressure["max_workers"] == 1
        assert pressure["executor_utilization"] == 1.0

        release.set()
        first_future = app.state.run_execution_registry.future(first["run_id"])
        second_future = app.state.run_execution_registry.future(second["run_id"])
        assert first_future is not None
        assert second_future is not None
        first_future.result(timeout=10)
        second_future.result(timeout=10)

        after = client.get("/api/production/health").json()["measured"]["executor_pressure"]
        assert after["active_runs"] == 0
        assert after["queued_runs"] == 0
        assert after["completed"] == 2
