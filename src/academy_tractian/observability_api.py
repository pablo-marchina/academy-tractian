from __future__ import annotations

import asyncio
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
from time import perf_counter
from typing import Any, AsyncContextManager, Callable

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from .architecture_manifest import ProviderSelectionState, architecture_manifest
from .observability_store import OBSERVABILITY_SCHEMA_VERSION, ObservabilityStore
from .operational_read_model import AnalyticsQuery, OperationalReadModel
from .production_telemetry import CloseReason, ProductionTelemetry


def _package_version() -> str:
    try:
        return version("academy-tractian")
    except PackageNotFoundError:
        return "0+unknown"


def _safe_config_hash() -> str:
    return sha256(
        f"academy-tractian-observability:{OBSERVABILITY_SCHEMA_VERSION}".encode("utf-8")
    ).hexdigest()


def _last_sequence(run_id: str, last_event_id: str | None) -> int:
    if last_event_id is None or last_event_id == "":
        return -1
    prefix, separator, sequence = last_event_id.rpartition(":")
    if separator != ":" or prefix != run_id:
        raise ValueError("Last-Event-ID does not belong to requested run")
    try:
        parsed = int(sequence)
    except ValueError as exc:
        raise ValueError("Last-Event-ID sequence is not an integer") from exc
    if parsed < -1:
        raise ValueError("Last-Event-ID sequence must be >= -1")
    return parsed


def _sse_record(event: dict[str, object]) -> str:
    payload = json.dumps(event, sort_keys=True, separators=(",", ":"), default=str)
    return f"id: {event['event_id']}\nevent: trace_event\ndata: {payload}\n\n"


def _safe_route_template(request: Request) -> str:
    route = request.scope.get("route")
    template = getattr(route, "path", None)
    if isinstance(template, str) and template:
        return template
    path = request.url.path
    if path.startswith("/api/runs/"):
        suffix = path.split("/", 4)
        tail = "" if len(suffix) < 5 else f"/{suffix[4]}"
        return f"/api/runs/{{run_id}}{tail}"
    if path in {
        "/api/runs", "/api/stream", "/api/query", "/api/query/schema", "/api/overview",
        "/api/production/health", "/api/tools/metrics", "/api/policies/metrics",
        "/api/evaluations/metrics", "/api/providers/experiments", "/api/architecture",
        "/health", "/ready", "/version",
    }:
        return path
    return "unclassified"


def _api_kind(method: str, route_template: str) -> str:
    if method == "POST" and route_template == "/api/query":
        return "analytics_query"
    if route_template == "/api/query/schema":
        return "analytics_schema"
    if method == "POST" and route_template == "/api/runs":
        return "runtime_submit"
    if route_template == "/api/stream":
        return "sse_handshake"
    if route_template.startswith("/api/runs/") or route_template == "/api/runs":
        return "run_read"
    if route_template in {
        "/api/overview", "/api/tools/metrics", "/api/policies/metrics", "/api/evaluations/metrics",
        "/api/providers/experiments", "/api/architecture", "/api/production/health",
    }:
        return "analytics_read"
    if route_template in {"/health", "/ready", "/version"}:
        return "control_read"
    return "other"


def _augment_health_with_quantitative_telemetry(
    health: dict[str, Any],
    live_operability: dict[str, Any] | None,
) -> dict[str, Any]:
    if live_operability is None:
        return health
    telemetry = live_operability.get("telemetry")
    if not isinstance(telemetry, dict):
        return health

    measured = health.setdefault("measured", {})
    if not isinstance(measured, dict):
        return health

    for key in ("runtime_requests", "api", "resources"):
        value = telemetry.get(key)
        if isinstance(value, dict):
            measured[key] = value

    sse = telemetry.get("sse")
    if isinstance(sse, dict):
        measured["sse"] = sse

    closed_gaps = {
        "runtime_request_latency_by_outcome_ms": "runtime_requests" in measured,
        "api_read_query_latency_ms": "api" in measured,
        "cpu_memory_pressure": "resources" in measured,
        "reconnect_event_loss_rate": isinstance(sse, dict) and "detected_gap_rate" in sse,
        "logical_duplicate_delivery_rate": isinstance(sse, dict) and "logical_duplicate_rate" in sse,
    }
    gaps = health.get("not_measured_yet")
    if isinstance(gaps, list):
        health["not_measured_yet"] = [
            item for item in gaps if not closed_gaps.get(str(item), False)
        ]
    health["schema_version"] = "production-health-v3"
    health["quantitative_measurement_contract"] = {
        "thresholds_preregistered": False,
        "interpretation": "measured_distributions_only; targets require provider-free baseline and EDD preregistration",
    }
    return health


def create_observability_app(
    *,
    db_path: str | Path = "./var/observability.duckdb",
    lifespan: Callable[[FastAPI], AsyncContextManager[None]] | None = None,
    provider_selection_state: ProviderSelectionState = "NO_SELECTION",
    production_telemetry: ProductionTelemetry | None = None,
    live_operability_supplier: Callable[[], dict[str, Any]] | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Academy × TRACTIAN Observability API",
        version=_package_version(),
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )
    store = ObservabilityStore(db_path)
    analytics = OperationalReadModel(store)
    app.state.observability_store = store
    app.state.operational_read_model = analytics

    if production_telemetry is not None:
        @app.middleware("http")
        async def measured_api_request(request: Request, call_next):
            started = perf_counter()
            status_code = 500
            try:
                response = await call_next(request)
                status_code = int(response.status_code)
                return response
            finally:
                route_template = _safe_route_template(request)
                production_telemetry.record_api_request(
                    method=request.method,
                    route_template=route_template,
                    kind=_api_kind(request.method, route_template),
                    status_code=status_code,
                    duration_ms=(perf_counter() - started) * 1000.0,
                )

    def require_run(run_id: str) -> dict[str, object]:
        item = store.get_run(run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run_not_found")
        return item

    def validate_scope(run_id: str | None) -> None:
        if run_id is not None:
            require_run(run_id)

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "service": "observability-api", "version": _package_version()}

    @app.get("/ready")
    def ready() -> dict[str, object]:
        if not store.ready():
            raise HTTPException(status_code=503, detail="observability_store_not_ready")
        return {"status": "ready", "store_schema_version": OBSERVABILITY_SCHEMA_VERSION}

    @app.get("/version")
    def version_info() -> dict[str, object]:
        return {
            "service": "observability-api",
            "package_version": _package_version(),
            "store_schema_version": OBSERVABILITY_SCHEMA_VERSION,
            "config_hash": _safe_config_hash(),
        }

    @app.get("/api/architecture")
    def architecture() -> dict[str, object]:
        return architecture_manifest(provider_selection_state=provider_selection_state).model_dump(mode="json")

    @app.get("/api/overview")
    def overview() -> dict[str, object]:
        return store.overview()

    @app.get("/api/production/health")
    def production_health() -> dict[str, object]:
        live_operability = None if live_operability_supplier is None else live_operability_supplier()
        payload = analytics.production_health(
            provider_selection_state=provider_selection_state,
            live_operability=live_operability,
        )
        return _augment_health_with_quantitative_telemetry(payload, live_operability)

    @app.get("/api/tools/metrics")
    def tools_metrics(run_id: str | None = Query(default=None, min_length=1, max_length=128)) -> dict[str, object]:
        validate_scope(run_id)
        return analytics.tools_metrics(run_id=run_id)

    @app.get("/api/policies/metrics")
    def policies_metrics(run_id: str | None = Query(default=None, min_length=1, max_length=128)) -> dict[str, object]:
        validate_scope(run_id)
        return analytics.policies_metrics(run_id=run_id)

    @app.get("/api/evaluations/metrics")
    def evaluation_metrics(run_id: str | None = Query(default=None, min_length=1, max_length=128)) -> dict[str, object]:
        validate_scope(run_id)
        return analytics.evaluation_metrics(run_id=run_id)

    @app.get("/api/providers/experiments")
    def provider_experiments() -> dict[str, object]:
        return analytics.provider_experiments()

    @app.get("/api/query/schema")
    def query_schema() -> dict[str, object]:
        return analytics.query_schema()

    @app.post("/api/query")
    def dynamic_query(spec: AnalyticsQuery) -> dict[str, object]:
        validate_scope(spec.run_id)
        try:
            return analytics.query(spec)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/runs")
    def runs(limit: int = Query(default=100, ge=1, le=1000)) -> dict[str, object]:
        items = store.list_runs(limit=limit)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, object]:
        return require_run(run_id)

    @app.get("/api/runs/{run_id}/events")
    def run_events(run_id: str) -> dict[str, object]:
        require_run(run_id)
        items = store.get_events(run_id)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}/evidence")
    def run_evidence(run_id: str) -> dict[str, object]:
        require_run(run_id)
        items = store.get_evidence(run_id)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}/evaluation")
    def run_evaluation(run_id: str) -> dict[str, object]:
        require_run(run_id)
        items = store.get_evaluation(run_id)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}/lineage")
    def run_lineage(run_id: str) -> dict[str, object]:
        require_run(run_id)
        try:
            return analytics.lineage(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="run_not_found") from exc

    @app.get("/api/stream")
    async def stream(
        request: Request,
        run_id: str = Query(min_length=1),
        follow: bool = Query(default=True),
        poll_ms: int = Query(default=200, ge=50, le=5000),
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        require_run(run_id)
        try:
            after_sequence = _last_sequence(run_id, last_event_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        connection_id = None
        if production_telemetry is not None:
            connection_id = production_telemetry.sse_open(
                reconnect=bool(last_event_id),
                after_sequence=after_sequence,
            )

        async def event_stream():
            nonlocal after_sequence
            close_reason: CloseReason = "client_disconnect"
            try:
                while True:
                    items = store.get_events_after(run_id, after_sequence=after_sequence, limit=1000)
                    for item in items:
                        sequence = int(item["sequence"])
                        after_sequence = sequence
                        if production_telemetry is not None and connection_id is not None:
                            production_telemetry.sse_event(
                                connection_id=connection_id,
                                event_id=str(item["event_id"]),
                                sequence=sequence,
                            )
                        yield _sse_record(item)

                    current = store.get_run(run_id)
                    if current is None:
                        close_reason = "run_missing"
                        return
                    if bool(current["completed"]) and after_sequence >= int(current["event_count"]) - 1:
                        close_reason = "completed"
                        return
                    if not follow:
                        close_reason = "single_replay"
                        return
                    if await request.is_disconnected():
                        close_reason = "client_disconnect"
                        return

                    if production_telemetry is not None and connection_id is not None:
                        production_telemetry.sse_keepalive(connection_id=connection_id)
                    yield ": keepalive\n\n"
                    await asyncio.sleep(poll_ms / 1000.0)
            finally:
                if production_telemetry is not None and connection_id is not None:
                    production_telemetry.sse_close(connection_id=connection_id, reason=close_reason)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app
