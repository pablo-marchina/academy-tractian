from __future__ import annotations

import json
import logging
from threading import Lock
from time import perf_counter
from typing import Any, Protocol

from research.e2.controller import AgentController
from research.e2.models import RunTrace, ToolKind
from research.e2.runner import HarnessRunner, ToolExecution

from .observability import SafeEvidenceRef, SafeEvent, SafeRun, project_trace
from .observability_contract import ObservabilityStoreContract
from .production_telemetry import ProductionTelemetry


_LOGGER = logging.getLogger(__name__)


def _canonical_read_signature(tool_name: str, arguments: dict[str, Any]) -> str | None:
    try:
        return json.dumps(
            {"tool_name": tool_name, "arguments": arguments},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        # Invalid/non-JSON arguments remain owned by the frozen B1 validator in HarnessRunner.
        return None


class SafeObservabilityEventSink(Protocol):
    """Sink boundary receives safe projections only, never raw RunTrace material."""

    def publish(
        self,
        *,
        run: SafeRun,
        event: SafeEvent,
        evidence: SafeEvidenceRef | None,
    ) -> None: ...


class ObservabilityEventSink:
    """Storage-engine-neutral publisher for the sanitized durable observability projection."""

    def __init__(
        self,
        store: ObservabilityStoreContract,
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
                duration_ms=(perf_counter() - started) * 1000.0,
            )


# Backwards-compatible symbol for historical tests/research imports. New production composition
# must use the engine-neutral name above; the implementation has no DuckDB-specific behavior.
DuckDBObservabilityEventSink = ObservabilityEventSink


class FailIsolatedObservabilityPublisher:
    """Project the latest canonical event and publish it without affecting runtime semantics."""

    def __init__(self, sink: SafeObservabilityEventSink) -> None:
        self.sink = sink
        self.telemetry = (
            sink.telemetry if isinstance(sink, ObservabilityEventSink) else None
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

    def publish_trace_state(
        self,
        trace: RunTrace,
        *,
        canonical_append_perf: float | None = None,
    ) -> None:
        """Publish the newest safe event after the accepted canonical append.

        `canonical_append_perf` is captured immediately after the frozen runner/controller append
        returns. It is monotonic process-local instrumentation only and never enters RunTrace.
        """

        started = perf_counter()
        safe_run_id: str | None = None
        event_type: str | None = None
        sequence: int | None = None
        try:
            run, events, evidence = project_trace(trace)
            safe_run_id = run.run_id
            if not events:
                return
            event = events[-1]
            event_type = event.event_type
            sequence = event.sequence
            evidence_item = next(
                (item for item in evidence if item.sequence == event.sequence),
                None,
            )
            self.sink.publish(run=run, event=event, evidence=evidence_item)
        except Exception as exc:
            sqlstate = getattr(exc, "sqlstate", None)
            safe_sqlstate = (
                sqlstate.upper()
                if isinstance(sqlstate, str)
                and len(sqlstate) == 5
                and sqlstate.isalnum()
                else None
            )
            _LOGGER.error(
                "observability_publish_failed",
                extra={
                    "academy_event": "observability_publish_failed",
                    "failure_type": type(exc).__name__,
                    "sqlstate": safe_sqlstate,
                    "safe_run_id": safe_run_id,
                    "event_type": event_type,
                    "sequence": sequence,
                },
            )
            with self._lock:
                self._failure_count += 1
            if self.telemetry is not None:
                self.telemetry.record_publish_overhead(
                    duration_ms=(perf_counter() - started) * 1000.0,
                    failed=True,
                )
            return

        completed = perf_counter()
        with self._lock:
            self._published_count += 1
            self._last_event_id = event.event_id
        if self.telemetry is not None:
            self.telemetry.record_publish_overhead(
                duration_ms=(completed - started) * 1000.0,
                failed=False,
            )
            if canonical_append_perf is not None:
                self.telemetry.record_event_to_persistence(
                    duration_ms=(completed - canonical_append_perf) * 1000.0,
                )


class ObservableHarnessRunner(HarnessRunner):
    """Production wrapper with safe observability and exact successful-READ loop containment."""

    def __init__(
        self,
        *,
        observability_publisher: FailIsolatedObservabilityPublisher,
        **kwargs: Any,
    ) -> None:
        self.observability_publisher = observability_publisher
        self._successful_read_signatures: set[str] = set()
        super().__init__(**kwargs)
        canonical_append_perf = perf_counter()
        self.observability_publisher.publish_trace_state(
            self.trace,
            canonical_append_perf=canonical_append_perf,
        )

    def _emit(self, event_type: str, **kwargs: Any) -> None:
        super()._emit(event_type, **kwargs)
        canonical_append_perf = perf_counter()
        self.observability_publisher.publish_trace_state(
            self.trace,
            canonical_append_perf=canonical_append_perf,
        )

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        evidence_id: str | None = None,
    ) -> ToolExecution:
        if tool_name not in self.registry:
            raise KeyError(tool_name)
        tool = self.registry[tool_name]
        signature = (
            _canonical_read_signature(tool_name, arguments)
            if tool.kind is ToolKind.READ
            else None
        )
        if signature is not None and signature in self._successful_read_signatures:
            # Match the frozen HarnessRunner trace contract: a proposal is visible before the
            # production wrapper contains the duplicate. No transport or action policy is touched.
            self._emit("tool_proposal", tool_name=tool.name, arguments=dict(arguments))
            return self._block(
                tool=tool,
                code="DUPLICATE_SUCCESSFUL_READ",
                reason="an identical read already completed successfully in this run",
                stage="B1",
            )

        result = super().execute_tool(
            tool_name,
            arguments,
            evidence_id=evidence_id,
        )
        if (
            signature is not None
            and result.executed
            and result.response is not None
            and 200 <= result.response.status_code < 300
        ):
            self._successful_read_signatures.add(signature)
        return result


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
        super()._emit(event_type, **kwargs)
        canonical_append_perf = perf_counter()
        self.observability_publisher.publish_trace_state(
            self.runner.trace,
            canonical_append_perf=canonical_append_perf,
        )
