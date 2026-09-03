from __future__ import annotations

import asyncio
import json
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from .analytics import AnalyticsReadModel
from .architecture import architecture_manifest
from .observability_store import ObservabilityStore
from .operational_read_model import OperationalReadModel
from .production_operability import ProductionTelemetry


CloseReason = Literal["completed", "client_disconnect", "run_missing", "single_replay"]


def _last_sequence(run_id: str, last_event_id: str | None) -> int:
    if last_event_id is None:
        return -1
    prefix = f"{run_id}:"
    if not last_event_id.startswith(prefix):
        raise ValueError("Last-Event-ID does not belong to requested run")
    try:
        sequence = int(last_event_id[len(prefix) :])
    except ValueError as exc:
        raise ValueError("Last-Event-ID sequence must be an integer") from exc
    if sequence < 0:
        raise ValueError("Last-Event-ID sequence must be non-negative")
    return sequence


def _sse_record(event: dict[str, object]) -> str:
    payload = json.dumps(event, sort_keys=True, separators=(",", ":"), default=str)
    return f"id: {event['event_id']}\nevent: trace_event\ndata: {payload}\n\n"


def _sse_stream_state_record(*, run_id: str, state: str, after_sequence: int) -> str:
    payload = json.dumps(
        {"run_id": run_id, "state": state, "after_sequence": after_sequence},
        sort_keys=True,
        separators=(",", ":"),
    )
    # Transport-control state deliberately carries no SSE id so the browser's Last-Event-ID
    # remains the last persisted trace event and reconnect resumes from the canonical cursor.
    return f"event: stream_state\ndata: {payload}\n\n"


def create_observability_app(
    *,
    db_path,
    store: ObservabilityStore | None = None,
    analytics: AnalyticsReadModel | None = None,
    operational_read_model: OperationalReadModel | None = None,
    production_telemetry: ProductionTelemetry | None = None,
    access_policy=None,
) -> FastAPI:
    store = store or ObservabilityStore(db_path)
    analytics = analytics or AnalyticsReadModel(db_path)
    operational_read_model = operational_read_model or OperationalReadModel(db_path)

    app = FastAPI(title="Academy × TRACTIAN Observability API")
    app.state.observability_store = store
    app.state.analytics = analytics
    app.state.operational_read_model = operational_read_model
    app.state.production_telemetry = production_telemetry
    app.state.observability_access_policy = access_policy

    def authorize_run(request: Request, run_id: str) -> None:
        if access_policy is not None:
            access_policy.authorize_run(request, run_id)

    def require_run(run_id: str) -> dict[str, object]:
        item = store.get_run(run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run_not_found")
        return item

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "version": "observability-api-v1"}

    @app.get("/ready")
    def ready() -> dict[str, object]:
        ready_status = operational_read_model.ready()
        if not ready_status:
            raise HTTPException(status_code=503, detail="read_model_not_ready")
        return {"status": "ready"}

    @app.get("/version")
    def version() -> dict[str, object]:
        return {"version": "observability-api-v1"}

    @app.get("/api/architecture")
    def architecture() -> dict[str, object]:
        return architecture_manifest().model_dump(mode="json")

    @app.get("/api/overview")
    def overview(request: Request) -> dict[str, object]:
        run_ids = None
        if access_policy is not None:
            run_ids = access_policy.visible_run_ids(request)
        return operational_read_model.overview(run_ids=run_ids)

    @app.get("/api/production/health")
    def production_health() -> dict[str, object]:
        if production_telemetry is None:
            return {
                "overall_status": "not_instrumented",
                "components": [],
                "measured": {},
                "not_measured_yet": ["production_telemetry"],
            }
        return production_telemetry.snapshot()

    @app.get("/api/tools/metrics")
    def tools_metrics(request: Request, run_id: str | None = None) -> dict[str, object]:
        if run_id is not None:
            authorize_run(request, run_id)
        elif access_policy is not None:
            access_policy.authorize_global_analytics(request)
        return operational_read_model.tools_metrics(run_id=run_id)

    @app.get("/api/policies/metrics")
    def policies_metrics(request: Request, run_id: str | None = None) -> dict[str, object]:
        if run_id is not None:
            authorize_run(request, run_id)
        elif access_policy is not None:
            access_policy.authorize_global_analytics(request)
        return operational_read_model.policies_metrics(run_id=run_id)

    @app.get("/api/evaluations/metrics")
    def evaluation_metrics(request: Request, run_id: str | None = None) -> dict[str, object]:
        if run_id is not None:
            authorize_run(request, run_id)
        elif access_policy is not None:
            access_policy.authorize_global_analytics(request)
        return operational_read_model.evaluation_metrics(run_id=run_id)

    @app.get("/api/providers/experiments")
    def provider_experiments(request: Request) -> dict[str, object]:
        if access_policy is not None:
            access_policy.authorize_global_analytics(request)
        return operational_read_model.provider_experiments()

    @app.get("/api/query/schema")
    def query_schema(request: Request) -> dict[str, object]:
        if access_policy is not None:
            access_policy.authorize_global_analytics(request)
        return analytics.schema()

    @app.post("/api/query")
    def query(request: Request, spec: dict[str, object]) -> dict[str, object]:
        if access_policy is not None:
            run_id = spec.get("run_id")
            if isinstance(run_id, str) and run_id:
                authorize_run(request, run_id)
            else:
                access_policy.authorize_global_analytics(request)
        try:
            return analytics.query(spec)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/runs")
    def runs(
        request: Request,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict[str, object]:
        fetch_limit = 1000 if access_policy is not None else limit
        items = store.list_runs(limit=fetch_limit)
        if access_policy is not None:
            items = access_policy.filter_runs(request, items)[:limit]
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str, request: Request) -> dict[str, object]:
        authorize_run(request, run_id)
        return require_run(run_id)

    @app.get("/api/runs/{run_id}/events")
    def run_events(run_id: str, request: Request) -> dict[str, object]:
        authorize_run(request, run_id)
        require_run(run_id)
        items = store.get_events(run_id)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}/evidence")
    def run_evidence(run_id: str, request: Request) -> dict[str, object]:
        authorize_run(request, run_id)
        require_run(run_id)
        items = store.get_evidence(run_id)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}/evaluation")
    def run_evaluation(run_id: str, request: Request) -> dict[str, object]:
        authorize_run(request, run_id)
        require_run(run_id)
        items = store.get_evaluation(run_id)
        return {"items": items, "count": len(items)}

    @app.get("/api/runs/{run_id}/lineage")
    def run_lineage(run_id: str, request: Request) -> dict[str, object]:
        authorize_run(request, run_id)
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
        authorize_run(request, run_id)
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
            reconnect_catchup_pending = bool(last_event_id) and follow
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

                    if reconnect_catchup_pending:
                        yield _sse_stream_state_record(
                            run_id=run_id,
                            state="caught_up",
                            after_sequence=after_sequence,
                        )
                        reconnect_catchup_pending = False

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
