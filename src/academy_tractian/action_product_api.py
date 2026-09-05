from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .action_evaluation import ProductionActionEvaluator
from .action_execution_lease import (
    ActionExecutionLeaseContext,
    ActionExecutionLeaseLost,
    ActionExecutionLeaseStore,
    ActionExecutionLeaseSupervisor,
    LeaseContextGuardedCustody,
    LeaseContextGuardedLedger,
    LeaseContextGuardedObservabilitySink,
    LeaseContextGuardedTransport,
)
from .action_recovery import reconcile_orphaned_actions
from .observability_contract import ObservabilityStoreContract
from .product_api import (
    AuthenticatedRuntimeContext,
    RuntimeContextProvider,
    create_product_app,
    require_runtime_permission,
    trusted_runtime_context,
)
from .product_storage_contracts import RunAccessStore, RunExecutionStore, RuntimeHandoffStore
from .production_actions_v2 import (
    ActionAuthorizationResolver,
    ActionProposalRealtimeProductionRuntime,
    DuckDBActionIdempotencyLedger,
    PendingActionCustody,
    PendingActionSafe,
    ProductionActionExecutor,
)
from .realtime_observability import DuckDBObservabilityEventSink
from .realtime_wakeup import RealtimeWakeup
from .target_action_authorization import (
    TargetAwareActionProposalRealtimeProductionRuntime,
    TargetAwareProductionActionExecutor,
    target_resolver_from_legacy,
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ActionConfirmation(_FrozenModel):
    confirm: Literal[True]


class ActionExecutionAccepted(_FrozenModel):
    action_id: str
    status: Literal["accepted"] = "accepted"
    execution_run_id: str
    stream_path: str
    run_path: str
    execution_path: str


def _derived_test_db_path(db_path: str | Path, infix: str) -> Path:
    path = Path(db_path)
    if path.suffix:
        return path.with_name(f"{path.stem}.{infix}{path.suffix}")
    return path.with_name(f"{path.name}.{infix}.duckdb")


def create_action_capable_product_app(
    *,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    context_provider: RuntimeContextProvider,
    authorization_resolver: ActionAuthorizationResolver,
    observability_store: ObservabilityStoreContract | None = None,
    db_path: str | Path | None = None,
    action_custody_path: str | Path | None = None,
    action_ledger_path: str | Path | None = None,
    custody_store: Any | None = None,
    action_ledger: Any | None = None,
    action_execution_lease_store: ActionExecutionLeaseStore | None = None,
    access_db_path: str | Path | None = None,
    execution_db_path: str | Path | None = None,
    run_access_store: RunAccessStore | None = None,
    execution_store: RunExecutionStore | None = None,
    runtime_handoff_store: RuntimeHandoffStore | None = None,
    operational_close: Callable[[], None] | None = None,
    max_workers: int = 4,
    provider_calls_enabled: bool = True,
    actions_enabled: bool = False,
    heartbeat_interval_ms: int = 1000,
    realtime_wakeup: RealtimeWakeup | None = None,
    realtime_fallback_poll_ms: int = 1000,
    runtime_handoff_lease_seconds: float = 15.0,
    runtime_handoff_scan_ms: int = 500,
    action_execution_lease_seconds: float = 15.0,
    action_execution_lease_scan_ms: int = 500,
    allow_local_test_storage: bool = False,
) -> FastAPI:
    """Create the action-capable product while failing closed on local storage.

    Production callers inject all durable stores. File-backed stores are retained only for
    isolated compatibility tests and require ``allow_local_test_storage=True``. The strict base
    product factory never receives a path and cannot infer a local persistence topology.

    ``runtime_handoff_store`` applies only to read-only investigation runtimes. Consequential
    action executions use a separate non-transferable lease when supplied. A healthy action lease
    prevents another replica's startup/reconciler from declaring the attempt orphaned; an expired
    lease converges to UNCERTAIN and is never permission to replay the external side effect.

    A resolver object may expose ``resolve_target(user_id, tool, arguments)``. When present, the
    product lazily resolves the exact action target at proposal time and resolves it again before
    confirmation is accepted. Legacy user-only resolvers retain their existing behavior.
    """

    if custody_store is not None and action_custody_path is not None:
        raise ValueError("provide custody_store or action_custody_path, not both")
    if action_ledger is not None and action_ledger_path is not None:
        raise ValueError("provide action_ledger or action_ledger_path, not both")
    if run_access_store is not None and access_db_path is not None:
        raise ValueError("provide run_access_store or access_db_path, not both")
    if execution_store is not None and execution_db_path is not None:
        raise ValueError("provide execution_store or execution_db_path, not both")
    if observability_store is not None and db_path is not None:
        raise ValueError("provide observability_store or db_path, not both")
    if not 3.0 <= action_execution_lease_seconds <= 3600.0:
        raise ValueError("action_execution_lease_seconds must be within [3, 3600]")
    if not 100 <= action_execution_lease_scan_ms <= 10000:
        raise ValueError("action_execution_lease_scan_ms must be within [100, 10000]")

    if allow_local_test_storage:
        if db_path is None and observability_store is None:
            raise ValueError("db_path is required for local test observability storage")
        if observability_store is None:
            from .observability_store import ObservabilityStore

            observability_store = ObservabilityStore(db_path)  # type: ignore[arg-type,assignment]
        if run_access_store is None:
            from .run_access import DuckDBRunAccessStore

            run_access_store = DuckDBRunAccessStore(
                access_db_path
                if access_db_path is not None
                else _derived_test_db_path(db_path, "access")  # type: ignore[arg-type]
            )
        if execution_store is None:
            from .run_execution_store import DuckDBRunExecutionStore

            execution_store = DuckDBRunExecutionStore(
                execution_db_path
                if execution_db_path is not None
                else _derived_test_db_path(db_path, "execution")  # type: ignore[arg-type]
            )
    else:
        local_path_supplied = any(
            value is not None
            for value in (
                db_path,
                action_custody_path,
                action_ledger_path,
                access_db_path,
                execution_db_path,
            )
        )
        if local_path_supplied:
            raise ValueError(
                "production action storage must be explicitly injected; "
                "local file-backed fallbacks are test-only"
            )

    if observability_store is None:
        raise ValueError("observability store is required for production")
    if custody_store is None and action_custody_path is None:
        raise ValueError("action custody store is required for production")
    if action_ledger is None and action_ledger_path is None:
        raise ValueError("action idempotency ledger is required for production")
    if run_access_store is None:
        raise ValueError("run access store is required for production")
    if execution_store is None:
        raise ValueError("run execution store is required for production")

    custody = custody_store or PendingActionCustody(action_custody_path)  # type: ignore[arg-type]
    ledger = action_ledger or DuckDBActionIdempotencyLedger(action_ledger_path)  # type: ignore[arg-type]
    target_authorization_resolver = target_resolver_from_legacy(authorization_resolver)
    lease_context = ActionExecutionLeaseContext()
    lease_supervisor = (
        ActionExecutionLeaseSupervisor(
            store=action_execution_lease_store,
            instance_id=f"action-{uuid4().hex}",
            lease_seconds=action_execution_lease_seconds,
            scan_interval_seconds=action_execution_lease_scan_ms / 1000.0,
        )
        if action_execution_lease_store is not None
        else None
    )
    action_recovery = reconcile_orphaned_actions(
        custody=custody,
        ledger=ledger,
        lease_store=action_execution_lease_store,
    )
    action_recovered_executions = tuple(
        item
        for run_id in action_recovery.execution_runs_marked_uncertain
        if (item := execution_store.get(run_id)) is not None
    )

    def runtime_factory(sink):
        if target_authorization_resolver is not None:
            return TargetAwareActionProposalRealtimeProductionRuntime(
                decision_source=decision_source_factory(),
                transport=transport_factory(),
                observability_sink=sink,
                target_authorization_resolver=target_authorization_resolver,
                custody=custody,
            )
        return ActionProposalRealtimeProductionRuntime(
            decision_source=decision_source_factory(),
            transport=transport_factory(),
            observability_sink=sink,
            authorization_resolver=authorization_resolver,
            custody=custody,
        )

    original_operational_close = operational_close

    def close_operational_dependencies() -> None:
        if lease_supervisor is not None:
            lease_supervisor.close()
        if original_operational_close is not None:
            original_operational_close()

    app = create_product_app(
        observability_store=observability_store,
        runtime_factory=runtime_factory,
        context_provider=context_provider,
        run_access_store=run_access_store,
        execution_store=execution_store,
        runtime_handoff_store=runtime_handoff_store,
        operational_close=close_operational_dependencies,
        max_workers=max_workers,
        provider_calls_enabled=provider_calls_enabled,
        heartbeat_interval_ms=heartbeat_interval_ms,
        realtime_wakeup=realtime_wakeup,
        realtime_fallback_poll_ms=realtime_fallback_poll_ms,
        runtime_handoff_lease_seconds=runtime_handoff_lease_seconds,
        runtime_handoff_scan_ms=runtime_handoff_scan_ms,
    )
    app.state.recovered_executions = tuple(app.state.recovered_executions) + action_recovered_executions
    controls = app.state.production_controls
    controls.set_actions_enabled(actions_enabled)
    store = app.state.observability_store
    telemetry = app.state.production_telemetry
    active_run_access_store: RunAccessStore = app.state.run_access_store
    active_execution_store: RunExecutionStore = app.state.run_execution_store
    access_policy = app.state.product_access_policy
    sink = DuckDBObservabilityEventSink(store, telemetry=telemetry)

    executor_custody = (
        LeaseContextGuardedCustody(custody, lease_context)
        if lease_supervisor is not None
        else custody
    )
    executor_ledger = (
        LeaseContextGuardedLedger(ledger, lease_context)
        if lease_supervisor is not None
        else ledger
    )
    executor_sink = (
        LeaseContextGuardedObservabilitySink(sink, lease_context)
        if lease_supervisor is not None
        else sink
    )

    def action_transport_factory() -> RequestTransport:
        transport = transport_factory()
        if lease_supervisor is None:
            return transport
        return LeaseContextGuardedTransport(transport, lease_context)  # type: ignore[return-value]

    if target_authorization_resolver is not None:
        executor = TargetAwareProductionActionExecutor(
            custody=executor_custody,
            ledger=executor_ledger,
            target_authorization_resolver=target_authorization_resolver,
            transport_factory=action_transport_factory,
            observability_sink=executor_sink,
            actions_enabled=actions_enabled,
        )
    else:
        executor = ProductionActionExecutor(
            custody=executor_custody,
            ledger=executor_ledger,
            authorization_resolver=authorization_resolver,
            transport_factory=action_transport_factory,
            observability_sink=executor_sink,
            actions_enabled=actions_enabled,
        )
    if lease_supervisor is not None:
        lease_supervisor.start()

    app.state.pending_action_custody = custody
    app.state.action_idempotency_ledger = ledger
    app.state.production_action_executor = executor
    app.state.action_recovery_report = action_recovery
    app.state.action_execution_lease_store = action_execution_lease_store
    app.state.action_execution_lease_supervisor = lease_supervisor
    app.state.action_execution_lease_backend = (
        "non_transferable_shared_lease"
        if action_execution_lease_store is not None
        else "legacy_no_lease"
    )
    app.state.action_authorization_backend = (
        "exact_target_v1" if target_authorization_resolver is not None else "legacy_user_snapshot"
    )
    app.state.local_test_storage_enabled = allow_local_test_storage

    def trusted_context(request: Request) -> AuthenticatedRuntimeContext:
        return trusted_runtime_context(context_provider, request)

    def authorize_action(
        action_id: str,
        request: Request,
        permission: str,
    ) -> tuple[AuthenticatedRuntimeContext, PendingActionSafe]:
        context = trusted_context(request)
        require_runtime_permission(context, permission)
        try:
            safe = custody.get_safe(action_id)
            ownership = active_run_access_store.get_scoped(
                run_id=safe.origin_run_id,
                organization_id=context.organization_id,
            )
            if ownership is None or ownership.user_id != context.user_id:
                raise PermissionError("action_origin_ownership_mismatch")
            custody.get_private_for_requester(
                action_id=action_id,
                requester_user_id=context.user_id,
            )
            return context, safe
        except (KeyError, PermissionError) as exc:
            raise HTTPException(status_code=404, detail="action_not_found") from exc

    @app.get("/api/runs/{run_id}/actions")
    def run_actions(run_id: str, request: Request) -> dict[str, object]:
        access_policy.authorize_run(request, run_id)
        if store.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="run_not_found")
        items = [item.model_dump(mode="json") for item in custody.list_safe_for_origin(run_id)]
        return {"items": items, "count": len(items)}

    @app.get("/api/actions/{action_id}", response_model=PendingActionSafe)
    def action_detail(action_id: str, request: Request) -> PendingActionSafe:
        _, safe = authorize_action(action_id, request, "actions:read:self")
        return safe

    def converge_worker_failure(execution_run_id: str, action_id: str) -> None:
        try:
            current = active_execution_store.get(execution_run_id)
            if current is not None and current.state in {"accepted", "running"}:
                active_execution_store.transition(
                    run_id=execution_run_id,
                    expected_states=frozenset({current.state}),
                    new_state="failed",
                )
                app.state.run_execution_registry.observe(execution_run_id, "failed")
            executor_custody.transition(
                action_id=action_id,
                expected_states=frozenset({"EXECUTING"}),
                new_state="UNCERTAIN",
            )
        except ActionExecutionLeaseLost:
            return

    def execute_confirmed_action(execution_run_id: str, action_id: str, prepared, claim) -> None:
        registry = app.state.run_execution_registry
        if lease_supervisor is None or claim is None:
            try:
                registry.running(execution_run_id)
            except Exception:
                custody.transition(
                    action_id=action_id,
                    expected_states=frozenset({"EXECUTING"}),
                    new_state="UNCERTAIN",
                )
                return
            try:
                trace = prepared.execute()
                report = ProductionActionEvaluator().evaluate(trace)
                store.persist_trace(trace, evaluation=report)
            except Exception:
                registry.failed(execution_run_id)
                custody.transition(
                    action_id=action_id,
                    expected_states=frozenset({"EXECUTING"}),
                    new_state="UNCERTAIN",
                )
                return
            registry.completed(execution_run_id)
            return

        guard = lease_supervisor.guard(claim)
        with lease_context.activate(guard):
            try:
                guard.assert_active()
                registry.running(execution_run_id)
                guard.assert_active()
                trace = prepared.execute()
                guard.assert_active()
                report = ProductionActionEvaluator().evaluate(trace)
                guard.assert_active()
                store.persist_trace(trace, evaluation=report)
                guard.assert_active()
                registry.completed(execution_run_id)
            except ActionExecutionLeaseLost:
                return
            except Exception:
                converge_worker_failure(execution_run_id, action_id)
                return
        lease_supervisor.release_terminal(claim)

    @app.post(
        "/api/actions/{action_id}/confirm",
        response_model=ActionExecutionAccepted,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def confirm_action(
        action_id: str,
        payload: ActionConfirmation,
        request: Request,
    ) -> ActionExecutionAccepted:
        del payload
        context, _ = authorize_action(action_id, request, "actions:confirm:self")
        if not controls.actions_enabled():
            raise HTTPException(status_code=503, detail="action_kill_switch_engaged")

        if target_authorization_resolver is None:
            principal = authorization_resolver(user_id=context.user_id)
            if principal.user_id != context.user_id:
                raise HTTPException(status_code=403, detail="action_authorization_context_mismatch")

        executor.set_actions_enabled(controls.actions_enabled())
        try:
            execution_run_id, prepared = executor.prepare_confirmed(
                action_id=action_id,
                identity_id=context.identity_id,
                requester_user_id=context.user_id,
            )
        except (KeyError, PermissionError) as exc:
            raise HTTPException(status_code=404, detail="action_not_found") from exc
        except RuntimeError as exc:
            code = str(exc)
            if code.startswith("action_not_confirmable") or code == "action_confirmation_race_lost":
                raise HTTPException(status_code=409, detail=code) from exc
            raise HTTPException(status_code=422, detail=code) from exc

        registry = app.state.run_execution_registry
        try:
            active_run_access_store.claim(
                run_id=execution_run_id,
                organization_id=context.organization_id,
                user_id=context.user_id,
            )
            registry.accepted(
                execution_run_id,
                execution_kind="action",
                related_action_id=action_id,
            )
        except Exception as exc:
            custody.transition(
                action_id=action_id,
                expected_states=frozenset({"EXECUTING"}),
                new_state="UNCERTAIN",
            )
            raise HTTPException(
                status_code=503,
                detail="action_execution_operational_state_persist_failed",
            ) from exc

        claim = None
        if lease_supervisor is not None:
            try:
                claim = lease_supervisor.acquire(
                    action_id=action_id,
                    execution_run_id=execution_run_id,
                )
            except ActionExecutionLeaseLost as exc:
                active_execution_store.transition(
                    run_id=execution_run_id,
                    expected_states=frozenset({"accepted"}),
                    new_state="uncertain",
                )
                registry.observe(execution_run_id, "uncertain")
                custody.transition(
                    action_id=action_id,
                    expected_states=frozenset({"EXECUTING"}),
                    new_state="UNCERTAIN",
                )
                raise HTTPException(
                    status_code=503,
                    detail="action_execution_lease_acquire_failed",
                ) from exc

        try:
            future = app.state.product_executor.submit(
                execute_confirmed_action,
                execution_run_id,
                action_id,
                prepared,
                claim,
            )
        except Exception as exc:
            registry.failed(execution_run_id)
            custody.transition(
                action_id=action_id,
                expected_states=frozenset({"EXECUTING"}),
                new_state="UNCERTAIN",
            )
            if lease_supervisor is not None and claim is not None:
                lease_supervisor.release_terminal(claim)
            raise HTTPException(status_code=503, detail="action_dispatch_failed") from exc
        registry.bind_future(execution_run_id, future)
        if lease_supervisor is not None and claim is not None:
            lease_supervisor.bind_future(claim, future)

        return ActionExecutionAccepted(
            action_id=action_id,
            execution_run_id=execution_run_id,
            stream_path=f"/api/stream?run_id={execution_run_id}",
            run_path=f"/api/runs/{execution_run_id}",
            execution_path=f"/api/runs/{execution_run_id}/execution",
        )

    return app
