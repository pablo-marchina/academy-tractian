from __future__ import annotations

from threading import Lock
from time import perf_counter
from typing import Any, Protocol

from research.e2.controller import AgentController
from research.e2.models import RunTrace
from research.e2.runner import HarnessRunner

from .observability import SafeEvidenceRef, SafeEvent, SafeRun, project_trace
from .observability_store import ObservabilityStore
from .production_telemetry import ProductionTelemetry


class SafeObservabilityEventSink(Protocol):
    """Sink boundary receives safe projections only, never raw RunTrace material."""

    def publish(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None,
    ) -> None: ...


class DuckDBObservabilityEventSink:
    def __init__(
        self,
        store: ObservabilityStore,
        *,
        telemetry: ProductionTelemetry | None = None,
    ) -> None:
        self.store = store
        self.telemetry = telemetry

    def publish(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None,
    ) -> None:
        started = perf_counter()
        self.store.persist_live_update(run=run, event=event, evidence=evidence)
        if self.telemetry is not None:
            self.telemetry.record_persistence(
                event_id=event.event_id,
                event_timestamp=event.timestamp,
                duration_ms=(perf_counter() - started) * 1000.0,
            )


class FailIsolatedObservabilityPublisher:
    """Project the latest canonical event and publish it without affecting runtime semantics."""

    def __init__(self, sink: SafeObservabilityEventSink) -> None:
        self.sink = sink
        self.telemetry = (
            sink.telemetry if isinstance(sink, DuckDBObservabilityEventSink) else None
        )
        self._lock = Lock()
        self._published_count = 0
        self._failure_count = 0
        self._last_event_id: str | None = None

    @property
    def published_count(self) -> int:
        with self._lock:
            return self._published_count

    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    @property
    def last_event_id(self) -> str | None:
        with self._lock:
            return self._last_event_id

    def publish_trace_state(self, trace: RunTrace) -> None:
        """Publish the newest safe event.

        Projection happens before the sink boundary. Any projection/persistence failure is
        intentionally contained so observability cannot make the production agent unavailable.
        """

        started = perf_counter()
        try:
            run, events, evidence = project_trace(trace)
            if not events:
                return
            event = events[-1]
            evidence_item = next(
                (item for item in evidence if item.sequence == event.sequence),
                None,
            )
            self.sink.publish(run=run, event=event, evidence=evidence_item)
        except Exception:
            with self._lock:
                self._failure_count += 1
            if self.telemetry is not None:
                self.telemetry.record_publish_overhead(
                    duration_ms=(perf_counter() - started) * 1000.0,
                    failed=True,
                )
            return

        with self._lock:
            self._published_count += 1
            self._last_event_id = event.event_id
        if self.telemetry is not None:
            self.telemetry.record_publish_overhead(
                duration_ms=(perf_counter() - started) * 1000.0,
                failed=False,
            )


class ObservableHarnessRunner(HarnessRunner):
    """Production opt-in wrapper preserving HarnessRunner's execution ownership."""

    def __init__(
        self,
        *,
        observability_publisher: FailIsolatedObservabilityPublisher,
        **kwargs: Any,
    ) -> None:
        self.observability_publisher = observability_publisher
        super().__init__(**kwargs)
        # HarnessRunner constructs run_started directly rather than through _emit().
        self.observability_publisher.publish_trace_state(self.trace)

    def _emit(self, event_type: str, **kwargs: Any) -> None:
        super()._emit(event_type, **kwargs)
        self.observability_publisher.publish_trace_state(self.trace)


class ObservableAgentController(AgentController):
    """Controller wrapper that publishes controller-owned events after canonical append."""

    def __init__(
        self,
        *,
        observability_publisher: FailIsolatedObservabilityPublisher,
        **kwargs: Any,
    ) -> None:
        self.observability_publisher = observability_publisher
        super().__init__(**kwargs)

    def _emit(self, event_type: str, **kwargs: Any) -> None:
        # ADR-004 semantics stay owned by the accepted controller implementation.
        super()._emit(event_type, **kwargs)
        self.observability_publisher.publish_trace_state(self.runner.trace)
