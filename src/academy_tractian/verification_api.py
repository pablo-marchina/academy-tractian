from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .verification import verify_persisted_run


def install_verification_api(app: FastAPI) -> None:
    """Expose run assurance without widening the browser trust boundary."""

    store = getattr(app.state, "observability_store", None)
    access_policy = getattr(app.state, "product_access_policy", None)
    if store is None or access_policy is None:
        raise RuntimeError("verification_api_requires_product_observability_and_access_policy")

    @app.get("/api/runs/{run_id}/verification")
    def run_verification(run_id: str, request: Request) -> dict[str, Any]:
        access_policy.authorize_run(request, run_id)
        run = store.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="run_not_found")
        report = verify_persisted_run(
            run=run,
            events=store.get_events(run_id),
            evaluation=store.get_evaluation(run_id),
        )
        return report.model_dump(mode="json")
