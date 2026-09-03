from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .action_evaluation import ProductionActionEvaluator
from .action_recovery import reconcile_orphaned_actions
from .product_api import (
    AuthenticatedRuntimeContext,
    RuntimeContextProvider,
    create_product_app,
    require_runtime_permission,
    trusted_runtime_context,
)
from .production_actions_v2 import (
    ActionAuthorizationResolver,
    ActionProposalRealtimeProductionRuntime,
    DuckDBActionIdempotencyLedger,
    PendingActionCustody,
    PendingActionSafe,
    ProductionActionExecutor,
)
from .realtime_observability import DuckDBObservabilityEventSink
from .run_access import RunAccessStore
from .run_execution_store import RunExecutionStore


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


def create_action_capable_product_app(
    *,
    db_path: str | Path,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    context_provider: RuntimeContextProvider,
    authorization_resolver: ActionAuthorizationResolver,
    action_custody_path: str | Path | None = None,
    action_ledger_path: str | Path | None = None,
    custody_store: Any | None = None,
    action_ledger: Any | None = None,
    access_db_path: str | Path | None = None,
    execution_db_path: str | Path | None = None,
    run_access_store: RunAccessStore | None = None,
    execution_store: RunExecutionStore | None = None,
    operational_close: Callable[[], None] | None = None,
    max_workers: int = 4,
    provider_calls_enabled: bool = True,
    actions_enabled: bool = False,
    heartbeat_interval_ms: int = 1000,
) -> FastAPI:
    if custody_store is not None and action_custody_path is not None:
        raise ValueError("provide custody_store or action_custody_path, not both")
    if action_ledger is not None and action_ledger_path is not None:
        raise ValueError("provide action_ledger or action_ledger_path, not both")
    if custody_store is None and action_custody_path is None:
        raise ValueError("action custody store or path is required")
    if action_ledger is None and action_ledger_path is None:
        raise ValueError("action idempotency ledger or path is required")

    custody = custody_store or PendingActionCustody(action_custody_path)  # type: ignore[arg-type]
    ledger = action_ledger or DuckDBActionIdempotencyLedger(action_ledger_path)  # type: ignore[arg-type]
    action_recovery = reconcile_orphaned_actions(custody=custody, ledger=ledger)

    def runtime_factory(sink):
        return ActionProposalRealtimeProductionRuntime(
            decision_source=decision_source_factory(),
            transport=transport_factory(),
            observability_sink=sink,
            authorization_resolver=authorization_resolver,
            custody=custody,
        )

    app = create_product_app(
        db_path=db_path,
        runtime_factory=runtime_factory,
        context_provider=context_provider,
        access_db_path=access_db_path,
        execution_db_path=execution_db_path,
        run_access_store=run_access_store,
        execution_store=execution_store,
        operational_close=operational_close,
        max_workers=max_workers,
        provider_calls_enabled=provider_calls_enabled,
        heartbeat_interval_ms=heartbeat_interval_ms,
    )
    controls = app.state.production_controls
    controls.set_actions_enabled(actions_enabled)
    store = app.state.observability_store
    telemetry = app.state.production_telemetry
    active_run_access_store: RunAccessStore = app.state.run_access_store
    access_policy = app.state.product_access_policy
    sink = DuckDBObservabilityEventSink(store, telemetry=telemetry)
    executor = ProductionActionExecutor(
        custody=custody,
        ledger=ledger,
        authorization_resolver=authorization_resolver,
        transport_factory=transport_factory,
        observability_sink=sink,
        actions_enabled=actions_enabled,
    )
    app.state.pending_action_custody = custody
    app.state.action_idempotency_ledger = ledger
    app.state.production_action_executor = executor
    app.state.action_recovery_report = action_recovery

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

    def execute_confirmed_action(execution_run_id: str, action_id: str, prepared) -> None:
        registry = app.state.run_execution_registry
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

        try:
            future = app.state.product_executor.submit(
                execute_confirmed_action,
                execution_run_id,
                action_id,
                prepared,
            )
        except Exception as exc:
            registry.failed(execution_run_id)
            custody.transition(
                action_id=action_id,
                expected_states=frozenset({"EXECUTING"}),
                new_state="UNCERTAIN",
            )
            raise HTTPException(status_code=503, detail="action_dispatch_failed") from exc
        registry.bind_future(execution_run_id, future)

        return ActionExecutionAccepted(
            action_id=action_id,
            execution_run_id=execution_run_id,
            stream_path=f"/api/stream?run_id={execution_run_id}",
            run_path=f"/api/runs/{execution_run_id}",
            execution_path=f"/api/runs/{execution_run_id}/execution",
        )

    return app
