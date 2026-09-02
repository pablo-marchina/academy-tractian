from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
from typing import Literal, Protocol
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from .evaluation import ProductionEvaluator
from .observability import safe_run_id
from .observability_api import create_observability_app
from .realtime_observability import (
    DuckDBObservabilityEventSink,
    SafeObservabilityEventSink,
)
from .realtime_runtime import PreparedRealtimeRun, RealtimeProductionRuntime
from .runtime import ProductionRequest


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuthenticatedRuntimeContext(_FrozenModel):
    """Trusted server-side execution context; never accepted from the run payload."""

    identity_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    seed: str | None = None


class RunSubmission(_FrozenModel):
    user_request: str = Field(min_length=1, max_length=20000)


class RunAccepted(_FrozenModel):
    run_id: str
    status: Literal["accepted"] = "accepted"
    stream_path: str
    run_path: str
    execution_path: str


class RuntimeContextProvider(Protocol):
    def __call__(self, request: Request) -> AuthenticatedRuntimeContext: ...


class RealtimeRuntimeFactory(Protocol):
    def __call__(
        self, sink: SafeObservabilityEventSink
    ) -> RealtimeProductionRuntime: ...


class RunExecutionRegistry:
    """Safe process-local execution status; exception internals are never exposed."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._status: dict[str, str] = {}
        self._futures: dict[str, Future[object]] = {}

    def accepted(self, run_id: str) -> None:
        with self._lock:
            self._status[run_id] = "accepted"

    def running(self, run_id: str) -> None:
        with self._lock:
            self._status[run_id] = "running"

    def completed(self, run_id: str) -> None:
        with self._lock:
            self._status[run_id] = "completed"

    def failed(self, run_id: str) -> None:
        with self._lock:
            self._status[run_id] = "failed"

    def bind_future(self, run_id: str, future: Future[object]) -> None:
        with self._lock:
            self._futures[run_id] = future

    def status(self, run_id: str) -> str | None:
        with self._lock:
            return self._status.get(run_id)

    def future(self, run_id: str) -> Future[object] | None:
        with self._lock:
            return self._futures.get(run_id)


def create_product_app(
    *,
    db_path: str | Path,
    runtime_factory: RealtimeRuntimeFactory,
    context_provider: RuntimeContextProvider,
    max_workers: int = 4,
) -> FastAPI:
    """Create the production product API over the safe observability/control plane.

    `runtime_factory` is provider-neutral and is expected to create a fresh decision-source
    runtime per request. This avoids sharing stateful model/controller clients across runs and
    keeps provider selection outside the web API contract.
    """

    if not 1 <= max_workers <= 64:
        raise ValueError("max_workers must be within [1, 64]")

    executor = ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="academy-tractian-run",
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            # Graceful product shutdown waits for already accepted work and forbids silently
            # abandoning a claimed one-shot run at process teardown.
            executor.shutdown(wait=True, cancel_futures=False)

    try:
        app = create_observability_app(db_path=db_path, lifespan=lifespan)
    except Exception:
        executor.shutdown(wait=False, cancel_futures=True)
        raise

    store = app.state.observability_store
    sink = DuckDBObservabilityEventSink(store)
    registry = RunExecutionRegistry()
    app.state.product_executor = executor
    app.state.run_execution_registry = registry

    def execute_prepared(run_id: str, prepared: PreparedRealtimeRun) -> None:
        registry.running(run_id)
        try:
            trace = prepared.execute()
            # Evaluator enters only after the runtime has produced a terminal trace.
            report = ProductionEvaluator().evaluate(trace)
            # Re-persisting the completed safe projection is idempotent and attaches the
            # post-runtime safe evaluation without exposing evaluator-private material.
            store.persist_trace(trace, evaluation=report)
        except Exception:
            registry.failed(run_id)
            return
        registry.completed(run_id)

    @app.post(
        "/api/runs",
        response_model=RunAccepted,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def submit_run(payload: RunSubmission, request: Request) -> RunAccepted:
        try:
            context = context_provider(request)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="trusted_runtime_context_unavailable",
            ) from exc

        raw_request_id = uuid4().hex
        production_request = ProductionRequest(
            request_id=raw_request_id,
            identity_id=context.identity_id,
            user_id=context.user_id,
            user_request=payload.user_request,
            seed=context.seed,
        )

        try:
            runtime = runtime_factory(sink)
            prepared = runtime.prepare(production_request)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="run_prepare_failed",
            ) from exc

        run_id = safe_run_id(raw_request_id)
        if store.get_run(run_id) is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="run_start_not_persisted",
            )

        registry.accepted(run_id)
        future = executor.submit(execute_prepared, run_id, prepared)
        registry.bind_future(run_id, future)

        return RunAccepted(
            run_id=run_id,
            stream_path=f"/api/stream?run_id={run_id}",
            run_path=f"/api/runs/{run_id}",
            execution_path=f"/api/runs/{run_id}/execution",
        )

    @app.get("/api/runs/{run_id}/execution")
    def execution_status(run_id: str) -> dict[str, str]:
        execution_state = registry.status(run_id)
        if execution_state is None:
            raise HTTPException(status_code=404, detail="run_execution_not_found")
        return {"run_id": run_id, "status": execution_state}

    return app
