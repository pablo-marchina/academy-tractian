from __future__ import annotations

from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Event, Lock, Thread, local
from time import perf_counter
from typing import Any, Iterator, Protocol


ACTION_EXECUTION_LEASE_SCHEMA_VERSION = "action-execution-lease-v1"


@dataclass(frozen=True, slots=True)
class ActionExecutionLeaseClaim:
    """One non-transferable ownership token for a consequential action attempt.

    Unlike read-only runtime handoff, an expired action lease is never reclaimable for another
    transport attempt. Expiry means the external side effect may have happened and the action must
    converge to UNCERTAIN until a human or an external idempotency source resolves it.
    """

    action_id: str
    execution_run_id: str
    owner_instance_id: str
    generation: int


@dataclass(frozen=True, slots=True)
class ActionExecutionRecoveryReport:
    actions_marked_uncertain: tuple[str, ...]
    execution_runs_marked_uncertain: tuple[str, ...]
    ledger_entries_marked_uncertain: tuple[str, ...]


class ActionExecutionLeaseStore(Protocol):
    def ready(self) -> bool: ...

    def acquire(
        self,
        *,
        action_id: str,
        execution_run_id: str,
        owner_instance_id: str,
        lease_seconds: float,
    ) -> ActionExecutionLeaseClaim | None: ...

    def renew(
        self,
        *,
        claim: ActionExecutionLeaseClaim,
        lease_seconds: float,
    ) -> bool: ...

    def is_current_owner(self, claim: ActionExecutionLeaseClaim) -> bool: ...

    def release_terminal(self, claim: ActionExecutionLeaseClaim) -> bool: ...

    def reconcile_expired(self) -> ActionExecutionRecoveryReport: ...

    def snapshot(self) -> dict[str, Any]: ...


class ActionExecutionLeaseLost(RuntimeError):
    pass


class ActionExecutionLeaseGuard:
    """Fail-closed guard used immediately before side effects and terminal writes."""

    def __init__(self, store: ActionExecutionLeaseStore, claim: ActionExecutionLeaseClaim) -> None:
        self.store = store
        self.claim = claim

    def assert_active(self) -> None:
        try:
            active = self.store.is_current_owner(self.claim)
        except Exception as exc:
            raise ActionExecutionLeaseLost("action_execution_lease_backend_unavailable") from exc
        if not active:
            raise ActionExecutionLeaseLost("action_execution_lease_not_current")


class ActionExecutionLeaseContext:
    """Thread-local guard context for the action worker only.

    Confirmation/setup happens before a lease exists and therefore sees no active guard. Once the
    worker starts, the exact claim is installed for that thread so transport, custody, ledger and
    safe-observability adapters can fence every sensitive operation without changing the frozen
    action engine's public interfaces.
    """

    def __init__(self) -> None:
        self._local = local()

    def current(self) -> ActionExecutionLeaseGuard | None:
        value = getattr(self._local, "guard", None)
        return value if isinstance(value, ActionExecutionLeaseGuard) else None

    def assert_if_active(self) -> None:
        guard = self.current()
        if guard is not None:
            guard.assert_active()

    @contextmanager
    def activate(self, guard: ActionExecutionLeaseGuard) -> Iterator[None]:
        previous = getattr(self._local, "guard", None)
        self._local.guard = guard
        try:
            yield
        finally:
            if previous is None:
                try:
                    delattr(self._local, "guard")
                except AttributeError:
                    pass
            else:
                self._local.guard = previous


class LeaseContextGuardedTransport:
    """Assert the action lease at the last boundary before an external request."""

    def __init__(self, delegate: Any, context: ActionExecutionLeaseContext) -> None:
        self.delegate = delegate
        self.context = context

    def request(self, request: Any) -> Any:
        self.context.assert_if_active()
        return self.delegate.request(request)


class LeaseContextGuardedObservabilitySink:
    """Fence browser-safe action projection when a worker has lost ownership."""

    def __init__(self, delegate: Any, context: ActionExecutionLeaseContext) -> None:
        self.delegate = delegate
        self.context = context
        # FailIsolatedObservabilityPublisher detects telemetry on storage-backed sinks.
        self.telemetry = getattr(delegate, "telemetry", None)

    def publish(self, *, run: Any, event: Any, evidence: Any) -> None:
        self.context.assert_if_active()
        self.delegate.publish(run=run, event=event, evidence=evidence)


class LeaseContextGuardedCustody:
    """Delegate custody reads; fence worker-time state transitions."""

    def __init__(self, delegate: Any, context: ActionExecutionLeaseContext) -> None:
        self.delegate = delegate
        self.context = context

    def __getattr__(self, name: str) -> Any:
        return getattr(self.delegate, name)

    def transition(self, **kwargs: Any) -> bool:
        self.context.assert_if_active()
        return bool(self.delegate.transition(**kwargs))


class LeaseContextGuardedLedger:
    """Fence idempotency claims and terminal ledger writes for the active worker."""

    def __init__(self, delegate: Any, context: ActionExecutionLeaseContext) -> None:
        self.delegate = delegate
        self.context = context

    def __getattr__(self, name: str) -> Any:
        return getattr(self.delegate, name)

    def claim(self, **kwargs: Any) -> bool:
        self.context.assert_if_active()
        return bool(self.delegate.claim(**kwargs))

    def mark(self, **kwargs: Any) -> None:
        self.context.assert_if_active()
        self.delegate.mark(**kwargs)


@dataclass(slots=True)
class _ActiveActionLease:
    claim: ActionExecutionLeaseClaim
    future: Future[object]
    last_renew_perf: float


class ActionExecutionLeaseSupervisor:
    """Replica-local renewer over non-transferable consequential-action leases.

    This supervisor never dequeues work and never creates a replacement action attempt. It only
    maintains leases for action Futures already started by this replica and periodically asks the
    shared store to converge expired/missing ownership to UNCERTAIN. One daemon thread per product
    replica owns maintenance; it is closed before the shared PostgreSQL pool.

    Backend readiness is checked before every maintenance tick. Losing the durable fencing backend
    stops this supervisor instead of continuing an unbounded error loop; worker guards separately
    fail closed when ownership cannot be verified. Another healthy replica can perform later
    reconciliation when the shared store returns.
    """

    def __init__(
        self,
        *,
        store: ActionExecutionLeaseStore,
        instance_id: str,
        lease_seconds: float = 15.0,
        scan_interval_seconds: float = 0.5,
    ) -> None:
        if not store.ready():
            raise ValueError("action execution lease store must be ready")
        if not instance_id or len(instance_id) > 128:
            raise ValueError("instance_id must be within [1, 128] characters")
        if not 3.0 <= lease_seconds <= 3600.0:
            raise ValueError("lease_seconds must be within [3, 3600]")
        if not 0.1 <= scan_interval_seconds <= 10.0:
            raise ValueError("scan_interval_seconds must be within [0.1, 10]")
        self.store = store
        self.instance_id = instance_id
        self.lease_seconds = float(lease_seconds)
        self.scan_interval_seconds = float(scan_interval_seconds)
        self._renew_every_seconds = max(1.0, self.lease_seconds / 3.0)
        self._lock = Lock()
        self._active: dict[str, _ActiveActionLease] = {}
        self._stop = Event()
        self._thread: Thread | None = None
        self._acquired = 0
        self._acquire_failures = 0
        self._renewals = 0
        self._renewal_failures = 0
        self._terminal_releases = 0
        self._terminal_release_failures = 0
        self._reconcile_ticks = 0
        self._reconcile_failures = 0
        self._reconciled_uncertain = 0
        self._backend_unavailable_stops = 0

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = Thread(
                target=self._run,
                name=f"action-lease-{self.instance_id[:24]}",
                daemon=True,
            )
            self._thread.start()

    def _run(self) -> None:
        while not self._stop.wait(self.scan_interval_seconds):
            try:
                ready = self.store.ready()
            except Exception:
                ready = False
            if not ready:
                with self._lock:
                    self._backend_unavailable_stops += 1
                self._stop.set()
                return
            self.tick()

    def close(self) -> None:
        self._stop.set()
        with self._lock:
            thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=max(1.0, self.scan_interval_seconds * 4.0))

    def acquire(self, *, action_id: str, execution_run_id: str) -> ActionExecutionLeaseClaim:
        claim = self.store.acquire(
            action_id=action_id,
            execution_run_id=execution_run_id,
            owner_instance_id=self.instance_id,
            lease_seconds=self.lease_seconds,
        )
        with self._lock:
            if claim is None:
                self._acquire_failures += 1
                raise ActionExecutionLeaseLost("action_execution_lease_acquire_failed")
            self._acquired += 1
        return claim

    def guard(self, claim: ActionExecutionLeaseClaim) -> ActionExecutionLeaseGuard:
        return ActionExecutionLeaseGuard(self.store, claim)

    def bind_future(self, claim: ActionExecutionLeaseClaim, future: Future[object]) -> None:
        with self._lock:
            self._active[claim.action_id] = _ActiveActionLease(
                claim=claim,
                future=future,
                last_renew_perf=perf_counter(),
            )

    def release_terminal(self, claim: ActionExecutionLeaseClaim) -> bool:
        released = self.store.release_terminal(claim)
        with self._lock:
            self._active.pop(claim.action_id, None)
            if released:
                self._terminal_releases += 1
            else:
                self._terminal_release_failures += 1
        return released

    def tick(self) -> None:
        """Renew healthy local attempts first, then reconcile globally expired ownership."""

        now = perf_counter()
        with self._lock:
            active_items = list(self._active.items())
        for action_id, active in active_items:
            if active.future.done():
                with self._lock:
                    self._active.pop(action_id, None)
                continue
            if now - active.last_renew_perf < self._renew_every_seconds:
                continue
            try:
                renewed = self.store.renew(
                    claim=active.claim,
                    lease_seconds=self.lease_seconds,
                )
            except Exception:
                renewed = False
            with self._lock:
                current = self._active.get(action_id)
                if current is not None:
                    current.last_renew_perf = now
                if renewed:
                    self._renewals += 1
                else:
                    self._renewal_failures += 1

        try:
            report = self.store.reconcile_expired()
        except Exception:
            with self._lock:
                self._reconcile_ticks += 1
                self._reconcile_failures += 1
            return
        with self._lock:
            self._reconcile_ticks += 1
            self._reconciled_uncertain += len(report.actions_marked_uncertain)
            for action_id in report.actions_marked_uncertain:
                self._active.pop(action_id, None)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            local = {
                "schema_version": "action-execution-lease-supervisor-v1",
                "instance_id": self.instance_id,
                "lease_seconds": self.lease_seconds,
                "scan_interval_seconds": self.scan_interval_seconds,
                "maintenance_running": self._thread is not None and self._thread.is_alive(),
                "active_local_leases": len(self._active),
                "acquired": self._acquired,
                "acquire_failures": self._acquire_failures,
                "renewals": self._renewals,
                "renewal_failures": self._renewal_failures,
                "terminal_releases": self._terminal_releases,
                "terminal_release_failures": self._terminal_release_failures,
                "reconcile_ticks": self._reconcile_ticks,
                "reconcile_failures": self._reconcile_failures,
                "reconciled_uncertain": self._reconciled_uncertain,
                "backend_unavailable_stops": self._backend_unavailable_stops,
                "automatic_replay_enabled": False,
            }
        try:
            local["store"] = self.store.snapshot()
        except Exception:
            local["store"] = {"ready": False, "automatic_replay_enabled": False}
        return local
