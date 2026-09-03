from __future__ import annotations

import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from threading import Lock
from time import perf_counter
from typing import Any, Literal, Protocol
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from .evaluation import ProductionEvaluator
from .observability import safe_run_id
from .observability_api import ObservabilityAccessPolicy, create_observability_app
from .production_controls import ProductionControlState
from .production_telemetry import ProductionTelemetry
from .realtime_observability import DuckDBObservabilityEventSink, SafeObservabilityEventSink
from .realtime_runtime import PreparedRealtimeRun, RealtimeProductionRuntime
from .run_access import DuckDBRunAccessStore
from .run_execution_store import DuckDBRunExecutionStore, ExecutionKind
from .runtime import ProductionRequest


DEFAULT_RUNTIME_PERMISSIONS = frozenset(
    {
        "runs:create",
        "runs:read:self",
        "actions:read:self",
        "actions:confirm:self",
    }
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuthenticatedRuntimeContext(_FrozenModel):
    """Trusted server-side execution context; never accepted from the run payload."""

    organization_id: str = Field(default="default-organization", min_length=1)
    identity_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    role: str = Field(default="operator", min_length=1, max_length=64)
    permissions: frozenset[str] = Field(default_factory=lambda: DEFAULT_RUNTIME_PERMISSIONS)
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
    def __call__(self, sink: SafeObservabilityEventSink) -> RealtimeProductionRuntime: ...


def trusted_runtime_context(
    context_provider: RuntimeContextProvider,
    request: Request,
) -> AuthenticatedRuntimeContext:
    try:
        context = context_provider(request)
        if not isinstance(context, AuthenticatedRuntimeContext):
            raise TypeError("runtime context provider returned an invalid type")
        return context
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="trusted_runtime_context_unavailable",
        ) from exc


def require_runtime_permission(
    context: AuthenticatedRuntimeContext,
    permission: str,
) -> None:
    if permission not in context.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="insufficient_permission",
        )


class ProductObservabilityAccessPolicy(ObservabilityAccessPolicy):
    """Fail-closed run authorization over trusted identity plus persistent ownership."""

    def __init__(
        self,
        *,
        context_provider: RuntimeContextProvider,
        run_access_store: DuckDBRunAccessStore,
    ) -> None:
        self.context_provider = context_provider
        self.run_access_store = run_access_store

    def context(self, request: Request) -> AuthenticatedRuntimeContext:
        return trusted_runtime_context(self.context_provider, request)

    def authorize_run(self, request: Request, run_id: str) -> None:
        context = self.context(request)
        if "runs:read:any" in context.permissions:
            return

        ownership = self.run_access_store.get(run_id)
        if ownership is None or ownership.organization_id != context.organization_id:
            raise HTTPException(status_code=404, detail="run_not_found")

        if "runs:read:org" in context.permissions:
            return
        if (
            "runs:read:self" in context.permissions
            and ownership.user_id == context.user_id
        ):
            return
        raise HTTPException(status_code=404, detail="run_not_found")

    def authorize_global(self, request: Request, capability: str) -> None:
        context = self.context(request)
        if capability not in context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="insufficient_permission",
            )

    def filter_runs(
        self,
        request: Request,
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        context = self.context(request)
        if "runs:read:any" in context.permissions:
            return items

        ownerships = self.run_access_store.get_many(
            str(item["run_id"]) for item in items
        )
        visible: list[dict[str, Any]] = []
        for item in items:
            ownership = ownerships.get(str(item["run_id"]))
            if ownership is None or ownership.organization_id != context.organization_id:
                continue
            if "runs:read:org" in context.permissions:
                visible.append(item)
                continue
            if (
                "runs:read:self" in context.permissions
                and ownership.user_id == context.user_id
            ):
                visible.append(item)
        return visible


class RunExecutionRegistry:
    """Local Future handles plus durable single-node execution state and pressure metrics."""

    def __init__(
        self,
        *,
        max_workers: int,
        state_store: DuckDBRunExecutionStore,
    ) -> None:
        self.max_workers = max_workers
        self.state_store = state_store
        self._lock = Lock()
        self._status: dict[str, str] = {}
        self._futures: dict[str, Future[object]] = {}
        self._last_transition_perf: float | None = None
        self._transition_count = 0

    def _local_transition(self, run_id: str, state: str) -> None:
        with self._lock:
            self._status[run_id] = state
            self._last_transition_perf = perf_counter()
            self._transition_count += 1

    def accepted(
        self,
        run_id: str,
        *,
        execution_kind: ExecutionKind = "runtime",
        related_action_id: str | None = None,
    ) -> None:
        self.state_store.create_accepted(
            run_id=run_id,
            execution_kind=execution_kind,
            related_action_id=related_action_id,
        )
        self._local_transition(run_id, "accepted")

    def running(self, run_id: str) -> None:
        if not self.state_store.transition(
            run_id=run_id,
            expected_states=frozenset({"accepted"}),
            new_state="running",
        ):
            raise RuntimeError("run_execution_running_transition_failed")
        self._local_transition(run_id, "running")

    def completed(self, run_id: str) -> None:
        if not self.state_store.transition(
            run_id=run_id,
            expected_states=frozenset({"running"}),
            new_state="completed",
        ):
            raise RuntimeError("run_execution_completed_transition_failed")
        self._local_transition(run_id, "completed")

    def failed(self, run_id: str) -> None:
        if not self.state_store.transition(
            run_id=run_id,
            expected_states=frozenset({"accepted", "running"}),
            new_state="failed",
        ):
            current = self.state_store.get(run_id)
            if current is None or current.state != "failed":
                raise RuntimeError("run_execution_failed_transition_failed")
        self._local_transition(run_id, "failed")

    def bind_future(self, run_id: str, future: Future[object]) -> None:
        with self._lock:
            self._futures[run_id] = future

    def status(self, run_id: str) -> str | None:
        item = self.state_store.get(run_id)
        return None if item is None else item.state

    def future(self, run_id: str) -> Future[object] | None:
        with self._lock:
            return self._futures.get(run_id)

    def snapshot(self) -> dict[str, Any]:
        now = perf_counter()
        with self._lock:
            counts = {
                state: sum(value == state for value in self._status.values())
                for state in ("accepted", "running", "completed", "failed")
            }
            active = counts["running"]
            queued = counts["accepted"]
            return {
                "schema_version": "run-execution-operability-v2",
                **counts,
                "active_runs": active,
                "queued_runs": queued,
                "inflight_runs": active + queued,
                "max_workers": self.max_workers,
                "executor_utilization": active / self.max_workers,
                "transition_count": self._transition_count,
                "last_transition_age_ms": None
                if self._last_transition_perf is None
                else max(0.0, (now - self._last_transition_perf) * 1000.0),
                "durable_state_counts": self.state_store.counts(),
            }


def _derived_db_path(db_path: str | Path, infix: str) -> Path:
    path = Path(db_path)
    if path.suffix:
        return path.with_name(f"{path.stem}.{infix}{path.suffix}")
    return path.with_name(f"{path.name}.{infix}.duckdb")


def create_product_app(
    *,
    db_path: str | Path,
    runtime_factory: RealtimeRuntimeFactory,
    context_provider: RuntimeContextProvider,
    access_db_path: str | Path | None = None,
    execution_db_path: str | Path | None = None,
    max_workers: int = 4,
    provider_calls_enabled: bool = True,
    heartbeat_interval_ms: int = 1000,
) -> FastAPI:
    """Create the production product API over the safe observability/control plane.

    `runtime_factory` is provider-neutral and is expected to create a fresh decision-source
    runtime per request. The provider kill switch gates construction before any provider-owned
    client can be reached. Consequential actions remain disabled by ProductionRuntimeConfig v1.

    Product run reads are scoped by trusted identity and persistent ownership. Execution state
    is persisted separately from local Future handles. At startup, unfinished ordinary runs are
    marked interrupted and unfinished action runs are marked uncertain; neither is replayed.
    The operational adapters remain replaceable for the planned DuckDB-vs-PostgreSQL benchmark.
    """

    if not 1 <= max_workers <= 64:
        raise ValueError("max_workers must be within [1, 64]")
    if not 250 <= heartbeat_interval_ms <= 10000:
        raise ValueError("heartbeat_interval_ms must be within [250, 10000]")

    created_perf = perf_counter()
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="academy-tractian-run")
    telemetry = ProductionTelemetry(heartbeat_stale_after_ms=max(1000, heartbeat_interval_ms * 3))
    controls = ProductionControlState(provider_calls_enabled=provider_calls_enabled)
    run_access_store = DuckDBRunAccessStore(
        _derived_db_path(db_path, "access") if access_db_path is None else access_db_path
    )
    execution_store = DuckDBRunExecutionStore(
        _derived_db_path(db_path, "execution")
        if execution_db_path is None
        else execution_db_path
    )
    recovered_executions = execution_store.reconcile_orphaned()
    registry = RunExecutionRegistry(max_workers=max_workers, state_store=execution_store)
    access_policy = ProductObservabilityAccessPolicy(
        context_provider=context_provider,
        run_access_store=run_access_store,
    )

    def live_operability_snapshot() -> dict[str, Any]:
        return {
            "telemetry": telemetry.snapshot(),
            "execution": registry.snapshot(),
            "controls": controls.snapshot(),
            "access": {
                "schema_version": "product-access-operability-v1",
                "ready": run_access_store.ready(),
            },
            "recovery": {
                "schema_version": "product-recovery-operability-v1",
                "execution_store_ready": execution_store.ready(),
                "orphaned_executions_reconciled": len(recovered_executions),
                "interrupted_runtime_runs": sum(
                    item.state == "interrupted" for item in recovered_executions
                ),
                "uncertain_action_runs": sum(
                    item.state == "uncertain" for item in recovered_executions
                ),
            },
        }

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        telemetry.mark_started(startup_readiness_ms=(perf_counter() - created_perf) * 1000.0)

        async def heartbeat_loop() -> None:
            while True:
                telemetry.heartbeat()
                await asyncio.sleep(heartbeat_interval_ms / 1000.0)

        heartbeat_task = asyncio.create_task(heartbeat_loop())
        try:
            yield
        finally:
            heartbeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await heartbeat_task
            telemetry.mark_stopped()
            executor.shutdown(wait=True, cancel_futures=False)

    try:
        app = create_observability_app(
            db_path=db_path,
            lifespan=lifespan,
            production_telemetry=telemetry,
            live_operability_supplier=live_operability_snapshot,
            access_policy=access_policy,
        )
    except Exception:
        executor.shutdown(wait=False, cancel_futures=True)
        raise

    store = app.state.observability_store
    sink = DuckDBObservabilityEventSink(store, telemetry=telemetry)
    app.state.product_executor = executor
    app.state.run_execution_registry = registry
    app.state.run_execution_store = execution_store
    app.state.recovered_executions = recovered_executions
    app.state.production_telemetry = telemetry
    app.state.production_controls = controls
    app.state.run_access_store = run_access_store
    app.state.product_access_policy = access_policy

    def execute_prepared(run_id: str, prepared: PreparedRealtimeRun) -> None:
        registry.running(run_id)
        telemetry.runtime_execution_started(run_id=run_id)
        try:
            trace = prepared.execute()
            report = ProductionEvaluator().evaluate(trace)
            store.persist_trace(trace, evaluation=report)
            safe_run = store.get_run(run_id)
            telemetry.runtime_request_finished(
                run_id=run_id,
                outcome="completed",
                terminal_decision=None if safe_run is None else safe_run.get("terminal_decision"),
                response_mode=None if safe_run is None else safe_run.get("terminal_response_mode"),
            )
        except Exception:
            registry.failed(run_id)
            telemetry.runtime_request_finished(
                run_id=run_id,
                outcome="failed",
                terminal_decision=None,
                response_mode=None,
            )
            return
        registry.completed(run_id)

    @app.post(
        "/api/runs",
        response_model=RunAccepted,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def submit_run(payload: RunSubmission, request: Request) -> RunAccepted:
        context = trusted_runtime_context(context_provider, request)
        require_runtime_permission(context, "runs:create")

        if not controls.provider_calls_enabled():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="provider_kill_switch_engaged",
            )

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
            if runtime.config.actions_enabled is not False:
                raise RuntimeError("production_action_switch_contract_drift")
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

        try:
            run_access_store.claim(
                run_id=run_id,
                organization_id=context.organization_id,
                user_id=context.user_id,
            )
            registry.accepted(run_id)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="run_operational_state_persist_failed",
            ) from exc

        telemetry.runtime_request_started(run_id=run_id)
        try:
            future = executor.submit(execute_prepared, run_id, prepared)
        except Exception as exc:
            registry.failed(run_id)
            telemetry.runtime_request_finished(
                run_id=run_id,
                outcome="failed",
                terminal_decision=None,
                response_mode=None,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="run_dispatch_failed",
            ) from exc
        registry.bind_future(run_id, future)

        return RunAccepted(
            run_id=run_id,
            stream_path=f"/api/stream?run_id={run_id}",
            run_path=f"/api/runs/{run_id}",
            execution_path=f"/api/runs/{run_id}/execution",
        )

    @app.get("/api/runs/{run_id}/execution")
    def execution_status(run_id: str, request: Request) -> dict[str, str]:
        access_policy.authorize_run(request, run_id)
        execution_state = registry.status(run_id)
        if execution_state is None:
            raise HTTPException(status_code=404, detail="run_execution_not_found")
        return {"run_id": run_id, "status": execution_state}

    return app
