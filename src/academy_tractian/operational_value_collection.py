from __future__ import annotations

from hashlib import sha256
from threading import Lock
from time import perf_counter
from typing import Callable, Literal, Protocol
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from research.e2.models import Decision

from .operational_value_pilot import OperationalPilotCompletion, OperationalPilotTask, PilotTrialStatus
from .product_api import (
    AuthenticatedRuntimeContext,
    RuntimeContextProvider,
    require_runtime_permission,
    trusted_runtime_context,
)


OPERATIONAL_VALUE_PARTICIPATE_PERMISSION = "operational-value:participate"
HumanPilotTerminationStatus = Literal["INTERRUPTED", "WITHDRAWN"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PilotAssignmentRecord(_FrozenModel):
    """Server-side assignment record. Pair identity is never serialized by the API."""

    assignment_id: str = Field(pattern=r"^ova_[0-9a-f]{24}$")
    organization_id: str = Field(min_length=1)
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    task: OperationalPilotTask
    pair_id: str = Field(pattern=r"^ovpair_[0-9a-f]{24}$")
    user_id: str = Field(min_length=1)
    operator_ref_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    host_session_id: str = Field(pattern=r"^ovhost_[0-9a-f]{24}$")


class PilotAssignmentSafe(_FrozenModel):
    """Only material needed by the operator. No pair/split/group/operator identity leaks."""

    assignment_id: str = Field(pattern=r"^ova_[0-9a-f]{24}$")
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    task: OperationalPilotTask


class PilotCompletionSubmission(_FrozenModel):
    terminal_decision: Decision
    conclusion_summary: str = Field(min_length=1, max_length=10000)


class PilotTerminationSubmission(_FrozenModel):
    status: HumanPilotTerminationStatus


class PilotCompletionAccepted(_FrozenModel):
    """Participant-safe acknowledgement; measured duration remains evaluator/private state."""

    assignment_id: str = Field(pattern=r"^ova_[0-9a-f]{24}$")
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    status: PilotTrialStatus


class OperationalPilotCollectionStore(Protocol):
    def reconcile_active_host_session(self, host_session_id: str) -> tuple[str, ...]: ...

    def get_active_for_user(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> PilotAssignmentRecord | None: ...

    def assign_next(
        self,
        *,
        organization_id: str,
        user_id: str,
        operator_ref_sha256: str,
        host_session_id: str,
    ) -> PilotAssignmentRecord | None: ...

    def fail_active(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        reason: str,
    ) -> bool: ...

    def complete_valid(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        elapsed_seconds: float,
        terminal_decision: str,
        conclusion_summary: str,
    ) -> OperationalPilotCompletion: ...

    def terminate_active(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        terminal_status: HumanPilotTerminationStatus,
    ) -> OperationalPilotCompletion: ...


class HostMonotonicPilotTimerRegistry:
    """Process-local monotonic timers with explicit session-loss invalidation semantics.

    A persisted assignment is not enough to reconstruct a monotonic interval after process loss.
    The store therefore persists ``host_session_id`` and the API invalidates an ACTIVE assignment
    if it no longer belongs to this registry session instead of fabricating elapsed time.
    """

    def __init__(self, *, clock: Callable[[], float] = perf_counter) -> None:
        self.clock = clock
        self.host_session_id = f"ovhost_{uuid4().hex[:24]}"
        self._lock = Lock()
        self._starts: dict[str, float] = {}
        # Keep process-session memory of assignments that were actually timed. This closes a
        # subtle concurrency gap: two requests may converge on one DB assignment before either
        # starts the timer, while a timer that existed and later disappeared must never be
        # silently recreated with a shorter interval.
        self._seen: set[str] = set()

    def ensure_started(self, assignment_id: str) -> bool:
        """Start once, converge concurrent retries, and fail if a known timer was lost."""

        with self._lock:
            if assignment_id in self._starts:
                return False
            if assignment_id in self._seen:
                raise RuntimeError("operational_pilot_timer_session_lost")
            self._starts[assignment_id] = self.clock()
            self._seen.add(assignment_id)
            return True

    def has(self, assignment_id: str) -> bool:
        with self._lock:
            return assignment_id in self._starts

    def finish(self, assignment_id: str) -> float | None:
        with self._lock:
            started = self._starts.pop(assignment_id, None)
        if started is None:
            return None
        elapsed = self.clock() - started
        if elapsed <= 0.0:
            raise RuntimeError("operational_pilot_nonpositive_elapsed_time")
        return elapsed

    def discard(self, assignment_id: str) -> None:
        # Intentionally preserve ``_seen`` so a lost authoritative timer cannot be restarted in
        # the same host session with a fabricated shorter duration.
        with self._lock:
            self._starts.pop(assignment_id, None)


def pilot_operator_ref_sha256(
    *,
    packet_id: str,
    organization_id: str,
    user_id: str,
) -> str:
    """Study-scoped pseudonym; prevents cross-packet correlation and caller spoofing."""

    material = "\0".join(
        (
            "operational-value-operator-v1",
            packet_id,
            organization_id,
            user_id,
        )
    )
    return sha256(material.encode("utf-8")).hexdigest()


def _safe_assignment(record: PilotAssignmentRecord) -> PilotAssignmentSafe:
    return PilotAssignmentSafe(
        assignment_id=record.assignment_id,
        packet_id=record.packet_id,
        task=record.task,
    )


def attach_operational_value_collection_api(
    app: FastAPI,
    *,
    context_provider: RuntimeContextProvider,
    store: OperationalPilotCollectionStore,
    timer_registry: HostMonotonicPilotTimerRegistry | None = None,
) -> HostMonotonicPilotTimerRegistry:
    """Attach the human-effort pilot to the existing authenticated product API."""

    timers = timer_registry or HostMonotonicPilotTimerRegistry()
    recovery_lock = Lock()
    recovery_complete = False
    app.state.operational_value_collection_store = store
    app.state.operational_value_timer_registry = timers
    app.state.operational_value_recovered_assignments = ()

    def context(request: Request) -> AuthenticatedRuntimeContext:
        trusted = trusted_runtime_context(context_provider, request)
        require_runtime_permission(trusted, OPERATIONAL_VALUE_PARTICIPATE_PERMISSION)
        return trusted

    def ensure_host_session_reconciled() -> None:
        """Reconcile lazily on the first authorized pilot request, never at app construction.

        Constructing/importing a FastAPI application is not evidence that a new collector session
        has actually entered service. Delaying the mutation prevents a dry-run or validation-only
        app construction from invalidating an active human measurement.
        """

        nonlocal recovery_complete
        if recovery_complete:
            return
        with recovery_lock:
            if recovery_complete:
                return
            try:
                recovered = store.reconcile_active_host_session(timers.host_session_id)
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="operational_pilot_recovery_unavailable",
                ) from exc
            app.state.operational_value_recovered_assignments = recovered
            recovery_complete = True

    def fail_lost_timer(record: PilotAssignmentRecord) -> None:
        timers.discard(record.assignment_id)
        if not store.fail_active(
            assignment_id=record.assignment_id,
            organization_id=record.organization_id,
            user_id=record.user_id,
            reason="host_timer_session_lost",
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="operational_pilot_assignment_state_conflict",
            )

    def active_assignment(
        *,
        assignment_id: str,
        trusted: AuthenticatedRuntimeContext,
    ) -> PilotAssignmentRecord:
        active = store.get_active_for_user(
            organization_id=trusted.organization_id,
            user_id=trusted.user_id,
        )
        if active is None or active.assignment_id != assignment_id:
            raise HTTPException(status_code=404, detail="operational_pilot_assignment_not_found")
        if active.host_session_id != timers.host_session_id or not timers.has(assignment_id):
            fail_lost_timer(active)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="operational_pilot_timer_session_lost",
            )
        return active

    @app.post(
        "/api/operational-value/tasks/next",
        response_model=PilotAssignmentSafe,
    )
    def next_operational_value_task(request: Request) -> PilotAssignmentSafe:
        trusted = context(request)
        ensure_host_session_reconciled()

        # Every request goes through the store allocator. PostgreSQL serializes one trusted
        # principal with an advisory transaction lock and returns the existing ACTIVE assignment
        # when a concurrent/retry request converges on it. Avoiding a separate pre-read closes the
        # DB-commit -> in-memory-timer race.
        principal_marker = sha256(
            "\0".join(
                (
                    "operational-value-principal-v1",
                    trusted.organization_id,
                    trusted.user_id,
                )
            ).encode("utf-8")
        ).hexdigest()
        assigned = store.assign_next(
            organization_id=trusted.organization_id,
            user_id=trusted.user_id,
            operator_ref_sha256=principal_marker,
            host_session_id=timers.host_session_id,
        )
        if assigned is None:
            raise HTTPException(status_code=404, detail="operational_pilot_no_task_available")
        if assigned.host_session_id != timers.host_session_id:
            fail_lost_timer(assigned)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="operational_pilot_timer_session_lost",
            )

        try:
            # The first converged request starts the interval; later concurrent requests return the
            # same task without resetting it. A timer that was previously started and disappeared
            # in this host session raises instead of being reconstructed.
            timers.ensure_started(assigned.assignment_id)
        except RuntimeError as exc:
            if str(exc) != "operational_pilot_timer_session_lost":
                raise
            fail_lost_timer(assigned)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="operational_pilot_timer_session_lost",
            ) from exc
        return _safe_assignment(assigned)

    @app.post(
        "/api/operational-value/assignments/{assignment_id}/complete",
        response_model=PilotCompletionAccepted,
    )
    def complete_operational_value_task(
        assignment_id: str,
        payload: PilotCompletionSubmission,
        request: Request,
    ) -> PilotCompletionAccepted:
        trusted = context(request)
        ensure_host_session_reconciled()
        active_assignment(assignment_id=assignment_id, trusted=trusted)
        elapsed = timers.finish(assignment_id)
        if elapsed is None:
            # ``active_assignment`` already proved the timer existed. Reaching this branch means
            # the authoritative timer disappeared between the two locked registry operations.
            active = store.get_active_for_user(
                organization_id=trusted.organization_id,
                user_id=trusted.user_id,
            )
            if active is not None and active.assignment_id == assignment_id:
                fail_lost_timer(active)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="operational_pilot_timer_session_lost",
            )
        try:
            completion = store.complete_valid(
                assignment_id=assignment_id,
                organization_id=trusted.organization_id,
                user_id=trusted.user_id,
                elapsed_seconds=elapsed,
                terminal_decision=payload.terminal_decision.value,
                conclusion_summary=payload.conclusion_summary,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="operational_pilot_assignment_not_found") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return PilotCompletionAccepted(
            assignment_id=assignment_id,
            packet_id=completion.packet_id,
            task_id=completion.task_id,
            status=completion.status,
        )

    @app.post(
        "/api/operational-value/assignments/{assignment_id}/terminate",
        response_model=PilotCompletionAccepted,
    )
    def terminate_operational_value_task(
        assignment_id: str,
        payload: PilotTerminationSubmission,
        request: Request,
    ) -> PilotCompletionAccepted:
        trusted = context(request)
        ensure_host_session_reconciled()
        active_assignment(assignment_id=assignment_id, trusted=trusted)
        try:
            # Persist the human terminal state first. If PostgreSQL fails, keep the authoritative
            # timer alive so the operator can recover instead of silently discarding a valid trial.
            completion = store.terminate_active(
                assignment_id=assignment_id,
                organization_id=trusted.organization_id,
                user_id=trusted.user_id,
                terminal_status=payload.status,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="operational_pilot_assignment_not_found") from exc
        timers.discard(assignment_id)
        return PilotCompletionAccepted(
            assignment_id=assignment_id,
            packet_id=completion.packet_id,
            task_id=completion.task_id,
            status=completion.status,
        )

    return timers
