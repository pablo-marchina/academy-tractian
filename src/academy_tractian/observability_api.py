from __future__ import annotations

from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

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

    return app
