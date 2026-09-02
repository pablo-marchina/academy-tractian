from __future__ import annotations

import asyncio
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from .observability_store import OBSERVABILITY_SCHEMA_VERSION, ObservabilityStore


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


def create_observability_app(
    *,
    db_path: str | Path = "./var/observability.duckdb",
) -> FastAPI:
    app = FastAPI(
        title="Academy × TRACTIAN Observability API",
        version=_package_version(),
        docs_url="/docs",
        redoc_url=None,
    )
    store = ObservabilityStore(db_path)
    app.state.observability_store = store

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "observability-api",
            "version": _package_version(),
        }

    @app.get("/ready")
    def ready() -> dict[str, object]:
        if not store.ready():
            raise HTTPException(status_code=503, detail="observability_store_not_ready")
        return {
            "status": "ready",
            "store_schema_version": OBSERVABILITY_SCHEMA_VERSION,
        }

    @app.get("/version")
    def version_info() -> dict[str, object]:
        return {
            "service": "observability-api",
            "package_version": _package_version(),
            "store_schema_version": OBSERVABILITY_SCHEMA_VERSION,
            "config_hash": _safe_config_hash(),
        }

    @app.get("/api/overview")
    def overview() -> dict[str, object]:
        return store.overview()

    @app.get("/api/runs")
    def runs(
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict[str, object]:
        items = store.list_runs(limit=limit)
        return {"items": items, "count": len(items)}

    def require_run(run_id: str) -> dict[str, object]:
        item = store.get_run(run_id)
        if item is None:
            raise HTTPException(status_code=404, detail="run_not_found")
        return item

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

    @app.get("/api/stream")
    async def stream(
        request: Request,
        run_id: str = Query(min_length=1),
        follow: bool = Query(default=True),
        poll_ms: int = Query(default=200, ge=50, le=5000),
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        run = require_run(run_id)
        try:
            after_sequence = _last_sequence(run_id, last_event_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        async def event_stream():
            nonlocal after_sequence
            while True:
                items = store.get_events_after(
                    run_id,
                    after_sequence=after_sequence,
                    limit=1000,
                )
                for item in items:
                    after_sequence = int(item["sequence"])
                    yield _sse_record(item)

                current = store.get_run(run_id)
                if current is None:
                    return
                if bool(current["completed"]) and after_sequence >= int(current["event_count"]) - 1:
                    return
                if not follow:
                    return
                if await request.is_disconnected():
                    return

                # Comment frame keeps intermediaries/connections alive without fabricating
                # a runtime event or changing any UI state.
                yield ": keepalive\n\n"
                await asyncio.sleep(poll_ms / 1000.0)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return app
