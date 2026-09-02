from __future__ import annotations

from collections import OrderedDict
from statistics import mean
from threading import Lock
from time import perf_counter
from typing import Any, Literal
from uuid import uuid4


CloseReason = Literal["completed", "client_disconnect", "single_replay", "run_missing"]


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = percentile * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    fraction = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction


def _summary(values: list[float]) -> dict[str, int | float | None]:
    return {
        "count": len(values),
        "avg_ms": None if not values else mean(values),
        "p50_ms": _percentile(values, 0.50),
        "p95_ms": _percentile(values, 0.95),
        "max_ms": None if not values else max(values),
    }


class ProductionTelemetry:
    """Bounded process-local metrics for real production control-plane operations.

    This object never receives prompts, response bodies, credentials, identity values or raw
    RunTrace material. Event correlation is restricted to already-safe event ids. Runtime-event
    persistence latency is measured from the first monotonic instant immediately after the
    accepted canonical append returns until safe persistence completes; no wall-clock timestamp
    is inferred when TraceEvent.timestamp is absent.
    """

    def __init__(self, *, sample_limit: int = 4096, heartbeat_stale_after_ms: int = 3000) -> None:
        if not 64 <= sample_limit <= 65536:
            raise ValueError("sample_limit must be within [64, 65536]")
        if not 500 <= heartbeat_stale_after_ms <= 60000:
            raise ValueError("heartbeat_stale_after_ms must be within [500, 60000]")
        self.sample_limit = sample_limit
        self.heartbeat_stale_after_ms = heartbeat_stale_after_ms
        self._lock = Lock()
        self._created_perf = perf_counter()
        self._heartbeat_perf: float | None = None
        self._heartbeat_running = False
        self._startup_readiness_ms: float | None = None

        self._persisted_perf: OrderedDict[str, float] = OrderedDict()
        self._publish_overhead_ms: list[float] = []
        self._persistence_duration_ms: list[float] = []
        self._event_to_persistence_ms: list[float] = []
        self._persistence_to_sse_ms: list[float] = []
        self._publisher_failures = 0

        self._connections: dict[str, tuple[float, bool, bool]] = {}
        self._sse_connections_opened = 0
        self._sse_connections_closed = 0
        self._sse_reconnects = 0
        self._sse_events_delivered = 0
        self._sse_keepalives = 0
        self._sse_disconnects = 0
        self._sse_completed = 0
        self._reconnect_recovery_ms: list[float] = []

    def _append(self, target: list[float], value: float) -> None:
        target.append(max(0.0, float(value)))
        overflow = len(target) - self.sample_limit
        if overflow > 0:
            del target[:overflow]

    def mark_started(self, *, startup_readiness_ms: float) -> None:
        now = perf_counter()
        with self._lock:
            self._startup_readiness_ms = max(0.0, startup_readiness_ms)
            self._heartbeat_perf = now
            self._heartbeat_running = True

    def heartbeat(self) -> None:
        with self._lock:
            if self._heartbeat_running:
                self._heartbeat_perf = perf_counter()

    def mark_stopped(self) -> None:
        with self._lock:
            self._heartbeat_running = False

    def record_publish_overhead(self, *, duration_ms: float, failed: bool) -> None:
        with self._lock:
            self._append(self._publish_overhead_ms, duration_ms)
            if failed:
                self._publisher_failures += 1

    def record_persistence(
        self,
        *,
        event_id: str,
        duration_ms: float,
    ) -> None:
        persisted_perf = perf_counter()
        with self._lock:
            self._append(self._persistence_duration_ms, duration_ms)
            self._persisted_perf[event_id] = persisted_perf
            self._persisted_perf.move_to_end(event_id)
            while len(self._persisted_perf) > self.sample_limit:
                self._persisted_perf.popitem(last=False)

    def record_event_to_persistence(self, *, duration_ms: float) -> None:
        with self._lock:
            self._append(self._event_to_persistence_ms, duration_ms)

    def sse_open(self, *, reconnect: bool) -> str:
        connection_id = uuid4().hex
        with self._lock:
            self._connections[connection_id] = (perf_counter(), reconnect, False)
            self._sse_connections_opened += 1
            if reconnect:
                self._sse_reconnects += 1
        return connection_id

    def sse_event(self, *, connection_id: str, event_id: str) -> None:
        now = perf_counter()
        with self._lock:
            state = self._connections.get(connection_id)
            if state is not None:
                opened_perf, reconnect, first_event_delivered = state
                if reconnect and not first_event_delivered:
                    self._append(self._reconnect_recovery_ms, (now - opened_perf) * 1000.0)
                self._connections[connection_id] = (opened_perf, reconnect, True)
            persisted_perf = self._persisted_perf.get(event_id)
            if persisted_perf is not None:
                self._append(self._persistence_to_sse_ms, (now - persisted_perf) * 1000.0)
            self._sse_events_delivered += 1

    def sse_keepalive(self, *, connection_id: str) -> None:
        with self._lock:
            if connection_id in self._connections:
                self._sse_keepalives += 1

    def sse_close(self, *, connection_id: str, reason: CloseReason) -> None:
        with self._lock:
            existed = self._connections.pop(connection_id, None) is not None
            if not existed:
                return
            self._sse_connections_closed += 1
            if reason == "client_disconnect":
                self._sse_disconnects += 1
            elif reason == "completed":
                self._sse_completed += 1

    def snapshot(self) -> dict[str, Any]:
        now = perf_counter()
        with self._lock:
            heartbeat_age_ms = None
            if self._heartbeat_perf is not None:
                heartbeat_age_ms = max(0.0, (now - self._heartbeat_perf) * 1000.0)
            heartbeat_status = "stopped"
            if self._heartbeat_running:
                heartbeat_status = (
                    "ready"
                    if heartbeat_age_ms is not None and heartbeat_age_ms <= self.heartbeat_stale_after_ms
                    else "stale"
                )
            return {
                "schema_version": "production-telemetry-v1",
                "uptime_ms": max(0.0, (now - self._created_perf) * 1000.0),
                "startup_readiness_ms": self._startup_readiness_ms,
                "runtime_heartbeat": {
                    "status": heartbeat_status,
                    "age_ms": heartbeat_age_ms,
                    "stale_after_ms": self.heartbeat_stale_after_ms,
                },
                "observability": {
                    "publish_overhead": _summary(list(self._publish_overhead_ms)),
                    "persistence_duration": _summary(list(self._persistence_duration_ms)),
                    "runtime_event_to_persistence": _summary(list(self._event_to_persistence_ms)),
                    "runtime_event_to_persistence_boundary": "post_canonical_append_to_successful_safe_persistence",
                    "publisher_failures": self._publisher_failures,
                },
                "sse": {
                    "active_clients": len(self._connections),
                    "connections_opened": self._sse_connections_opened,
                    "connections_closed": self._sse_connections_closed,
                    "reconnects": self._sse_reconnects,
                    "events_delivered": self._sse_events_delivered,
                    "keepalives": self._sse_keepalives,
                    "client_disconnects": self._sse_disconnects,
                    "completed_streams": self._sse_completed,
                    "persistence_to_delivery": _summary(list(self._persistence_to_sse_ms)),
                    "reconnect_recovery": _summary(list(self._reconnect_recovery_ms)),
                },
            }
