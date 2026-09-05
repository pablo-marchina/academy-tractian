from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
from time import perf_counter
from typing import Any, Callable

from .evaluation import ProductionEvaluator
from .observability import SafeEvidenceRef, SafeEvent, SafeRun
from .observability_contract import ObservabilityStoreContract
from .production_telemetry import ProductionTelemetry
from .product_storage_contracts import RuntimeHandoffClaim, RuntimeHandoffStore
from .realtime_observability import ObservabilityEventSink, SafeObservabilityEventSink
from .realtime_runtime import RealtimeProductionRuntime
from .runtime import ProductionRequest


@dataclass(slots=True)
class _ActiveClaim:
    claim: RuntimeHandoffClaim
    future: Future[object]
    last_renew_perf: float


class ClaimBoundObservabilityEventSink(ObservabilityEventSink):
    """Observability/tool guard bound to one non-expired runtime claim generation."""

    def __init__(
        self,
        *,
        delegate: SafeObservabilityEventSink,
        handoff_store: RuntimeHandoffStore,
        claim: RuntimeHandoffClaim,
    ) -> None:
        store = getattr(delegate, "store", None)
        if store is None:
            raise TypeError("horizontal runtime requires a storage-backed observability sink")
        super().__init__(store, telemetry=getattr(delegate, "telemetry", None))
        self.handoff_store = handoff_store
        self.claim = claim

    def assert_active(self) -> None:
        if not self.handoff_store.is_current_owner(
            run_id=self.claim.envelope.run_id,
            owner_instance_id=self.claim.owner_instance_id,
            claim_generation=self.claim.claim_generation,
        ):
            raise RuntimeError("runtime_handoff_claim_not_current")

    def publish(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None,
    ) -> None:
        self.assert_active()
        super().publish(run=run, event=event, evidence=evidence)


class HorizontalRuntimeSupervisor:
    """Replica-local worker supervisor over a durable shared runtime handoff queue.

    The executor remains process-local compute capacity; ownership does not. PostgreSQL decides
    which replica owns each read-only runtime and a lease/generation token allows another replica
    to take over after process loss. Consequential action execution is intentionally outside this
    supervisor and retains its separate no-blind-replay safety contract.
    """

    def __init__(
        self,
        *,
        instance_id: str,
        max_workers: int,
        executor: ThreadPoolExecutor,
        handoff_store: RuntimeHandoffStore,
        runtime_factory: Callable[[SafeObservabilityEventSink], RealtimeProductionRuntime],
        observability_sink: SafeObservabilityEventSink,
        observability_store: ObservabilityStoreContract,
        telemetry: ProductionTelemetry,
        bind_future: Callable[[str, Future[object]], None],
        observe_state: Callable[[str, str], None],
        execution_enabled: Callable[[], bool],
        lease_seconds: float = 15.0,
    ) -> None:
        if not instance_id or len(instance_id) > 128:
            raise ValueError("instance_id must be within [1, 128] characters")
        if not 1 <= max_workers <= 64:
            raise ValueError("max_workers must be within [1, 64]")
        if not 3.0 <= lease_seconds <= 3600.0:
            raise ValueError("lease_seconds must be within [3, 3600]")
        if not handoff_store.ready():
            raise ValueError("runtime_handoff_store must be ready")

        self.instance_id = instance_id
        self.max_workers = max_workers
        self.executor = executor
        self.handoff_store = handoff_store
        self.runtime_factory = runtime_factory
        self.observability_sink = observability_sink
        self.observability_store = observability_store
        self.telemetry = telemetry
        self.bind_future = bind_future
        self.observe_state = observe_state
        self.execution_enabled = execution_enabled
        self.lease_seconds = lease_seconds
        self._renew_every_seconds = max(1.0, lease_seconds / 3.0)
        self._lock = Lock()
        # Capacity observation + durable claim + local submit form one replica-local reservation.
        # Without this lock concurrent HTTP request threads can all observe the same free slot,
        # over-claim PostgreSQL work and silently queue more "running" tasks than max_workers.
        self._dispatch_lock = Lock()
        self._active: dict[str, _ActiveClaim] = {}
        self._claims_started = 0
        self._recovery_claims_started = 0
        self._lease_renewals = 0
        self._lease_renewal_failures = 0
        self._fenced_terminal_writes = 0
        self._dispatch_ticks = 0
        self._execution_failures = 0

    def _active_count(self) -> int:
        with self._lock:
            return sum(not item.future.done() for item in self._active.values())

    def _submit_claim(self, claim: RuntimeHandoffClaim) -> Future[object]:
        future = self.executor.submit(self._execute_claim, claim)
        now = perf_counter()
        with self._lock:
            self._active[claim.envelope.run_id] = _ActiveClaim(
                claim=claim,
                future=future,
                last_renew_perf=now,
            )
            self._claims_started += 1
            if claim.previous_state == "running":
                self._recovery_claims_started += 1
        self.observe_state(claim.envelope.run_id, "running")
        self.bind_future(claim.envelope.run_id, future)
        return future

    def dispatch_specific(self, run_id: str) -> Future[object] | None:
        if not self.execution_enabled():
            return None
        with self._dispatch_lock:
            with self._lock:
                existing = self._active.get(run_id)
                if existing is not None and not existing.future.done():
                    return existing.future
            if self._active_count() >= self.max_workers:
                return None
            claim = self.handoff_store.claim_specific(
                run_id=run_id,
                owner_instance_id=self.instance_id,
                lease_seconds=self.lease_seconds,
            )
            if claim is None:
                return None
            return self._submit_claim(claim)

    def _cleanup_and_renew(self) -> None:
        now = perf_counter()
        with self._lock:
            items = list(self._active.items())
        for run_id, active in items:
            if active.future.done():
                with self._lock:
                    self._active.pop(run_id, None)
                continue
            if now - active.last_renew_perf < self._renew_every_seconds:
                continue
            renewed = self.handoff_store.renew(
                run_id=run_id,
                owner_instance_id=self.instance_id,
                claim_generation=active.claim.claim_generation,
                lease_seconds=self.lease_seconds,
            )
            with self._lock:
                current = self._active.get(run_id)
                if current is not None:
                    current.last_renew_perf = now
                if renewed:
                    self._lease_renewals += 1
                else:
                    self._lease_renewal_failures += 1

    def tick(self) -> None:
        """Renew local leases and fill free worker capacity from the shared queue."""

        with self._lock:
            self._dispatch_ticks += 1
        self._cleanup_and_renew()
        if not self.execution_enabled():
            return
        with self._dispatch_lock:
            capacity = self.max_workers - self._active_count()
            if capacity <= 0:
                return
            claims = self.handoff_store.claim_available(
                owner_instance_id=self.instance_id,
                lease_seconds=self.lease_seconds,
                limit=capacity,
            )
            for claim in claims:
                self._submit_claim(claim)

    def _execute_claim(self, claim: RuntimeHandoffClaim) -> None:
        run_id = claim.envelope.run_id
        self.telemetry.runtime_execution_started(run_id=run_id)
        guarded_sink = ClaimBoundObservabilityEventSink(
            delegate=self.observability_sink,
            handoff_store=self.handoff_store,
            claim=claim,
        )
        try:
            guarded_sink.assert_active()
            runtime = self.runtime_factory(guarded_sink)
            if runtime.config.actions_enabled is not False:
                raise RuntimeError("production_action_switch_contract_drift")
            prepared = runtime.prepare(
                ProductionRequest(
                    request_id=claim.envelope.request_id,
                    identity_id=claim.envelope.identity_id,
                    user_id=claim.envelope.user_id,
                    user_request=claim.envelope.user_request,
                    seed=claim.envelope.seed,
                )
            )
            guarded_sink.assert_active()
            trace = prepared.execute()
            guarded_sink.assert_active()
            report = ProductionEvaluator().evaluate(trace)
            guarded_sink.assert_active()
            self.observability_store.persist_trace(trace, evaluation=report)
        except Exception:
            with self._lock:
                self._execution_failures += 1
            finalized = self.handoff_store.fail(
                run_id=run_id,
                owner_instance_id=self.instance_id,
                claim_generation=claim.claim_generation,
            )
            if finalized:
                self.observe_state(run_id, "failed")
                self.telemetry.runtime_request_finished(
                    run_id=run_id,
                    outcome="failed",
                    terminal_decision=None,
                    response_mode=None,
                )
            else:
                with self._lock:
                    self._fenced_terminal_writes += 1
            return

        finalized = self.handoff_store.complete(
            run_id=run_id,
            owner_instance_id=self.instance_id,
            claim_generation=claim.claim_generation,
        )
        if not finalized:
            with self._lock:
                self._fenced_terminal_writes += 1
            return
        self.observe_state(run_id, "completed")
        safe_run = self.observability_store.get_run(run_id)
        self.telemetry.runtime_request_finished(
            run_id=run_id,
            outcome="completed",
            terminal_decision=None if safe_run is None else safe_run.get("terminal_decision"),
            response_mode=None if safe_run is None else safe_run.get("terminal_response_mode"),
        )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            local = {
                "schema_version": "horizontal-runtime-supervisor-v1",
                "instance_id": self.instance_id,
                "max_workers": self.max_workers,
                "active_claims": sum(not item.future.done() for item in self._active.values()),
                "claims_started": self._claims_started,
                "recovery_claims_started": self._recovery_claims_started,
                "lease_renewals": self._lease_renewals,
                "lease_renewal_failures": self._lease_renewal_failures,
                "fenced_terminal_writes": self._fenced_terminal_writes,
                "dispatch_ticks": self._dispatch_ticks,
                "execution_failures": self._execution_failures,
                "lease_seconds": self.lease_seconds,
            }
        local["queue"] = self.handoff_store.snapshot()
        return local
