from __future__ import annotations

from collections import OrderedDict, defaultdict
import os
from statistics import mean
import sys
from threading import Lock
from time import perf_counter, process_time
from typing import Any, Literal
from uuid import uuid4

try:
    import resource as _resource
except ImportError:  # pragma: no cover - Windows fallback is part of the product contract.
    _resource = None


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


def _resource_snapshot() -> dict[str, Any]:
    cpu_count = os.cpu_count()
    try:
        load_1m, load_5m, load_15m = os.getloadavg()
    except (AttributeError, OSError):
        load_1m = load_5m = load_15m = None

    rss_current_bytes: int | None = None
    rss_current_source = "unavailable"
    statm_path = "/proc/self/statm"
    if os.path.exists(statm_path):
        try:
            resident_pages = int(open(statm_path, "r", encoding="utf-8").read().split()[1])
            rss_current_bytes = resident_pages * int(os.sysconf("SC_PAGE_SIZE"))
            rss_current_source = "proc_self_statm"
        except (OSError, ValueError, IndexError):
            rss_current_bytes = None

    rss_max_bytes: int | None = None
    rss_max_source = "unavailable"
    if _resource is not None:
        try:
            raw = int(_resource.getrusage(_resource.RUSAGE_SELF).ru_maxrss)
            # Linux reports KiB; macOS/BSD report bytes.
            rss_max_bytes = raw if sys.platform == "darwin" else raw * 1024
            rss_max_source = "resource_getrusage"
        except (OSError, ValueError):
            rss_max_bytes = None

    return {
        "process_cpu_time_ms": process_time() * 1000.0,
        "cpu_count": cpu_count,
        "system_load_1m": load_1m,
        "system_load_5m": load_5m,
        "system_load_15m": load_15m,
        "system_load_1m_per_cpu": None if load_1m is None or not cpu_count else load_1m / cpu_count,
        "rss_current_bytes": rss_current_bytes,
        "rss_current_source": rss_current_source,
        "rss_max_bytes": rss_max_bytes,
        "rss_max_source": rss_max_source,
        "threshold_interpretation": "not_preregistered",
    }


class ProductionTelemetry:
    """Bounded process-local metrics for real production control-plane operations.

    This object never receives prompts, response bodies, credentials, identity values or raw
    RunTrace material. Correlation uses safe run/event ids only. Metrics expose observations and
    distributions without inventing health thresholds; promotion targets remain preregistered by
    EDD after a provider-free baseline exists.
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

        self._runtime_started: OrderedDict[str, tuple[float, float | None]] = OrderedDict()
        self._runtime_request_samples: list[dict[str, Any]] = []
        self._runtime_execution_ms: list[float] = []

        self._api_samples: list[dict[str, Any]] = []

        self._connections: dict[str, dict[str, Any]] = {}
        self._sse_connections_opened = 0
        self._sse_connections_closed = 0
        self._sse_reconnects = 0
        self._sse_events_delivered = 0
        self._sse_keepalives = 0
        self._sse_disconnects = 0
        self._sse_completed = 0
        self._reconnect_recovery_ms: list[float] = []
        self._reconnect_first_event_checks = 0
        self._reconnect_sequential_recoveries = 0
        self._detected_gap_events = 0
        self._logical_duplicate_events = 0

    def _append(self, target: list[Any], value: Any) -> None:
        target.append(value)
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

    def runtime_request_started(self, *, run_id: str) -> None:
        with self._lock:
            self._runtime_started[run_id] = (perf_counter(), None)
            self._runtime_started.move_to_end(run_id)
            while len(self._runtime_started) > self.sample_limit:
                self._runtime_started.popitem(last=False)

    def runtime_execution_started(self, *, run_id: str) -> None:
        now = perf_counter()
        with self._lock:
            started = self._runtime_started.get(run_id)
            if started is not None:
                self._runtime_started[run_id] = (started[0], now)

    def runtime_request_finished(
        self,
        *,
        run_id: str,
        outcome: Literal["completed", "failed"],
        terminal_decision: str | None,
        response_mode: str | None,
    ) -> None:
        now = perf_counter()
        with self._lock:
            started = self._runtime_started.pop(run_id, None)
            if started is None:
                return
            accepted_perf, execution_perf = started
            request_ms = max(0.0, (now - accepted_perf) * 1000.0)
            execution_ms = None if execution_perf is None else max(0.0, (now - execution_perf) * 1000.0)
            self._append(
                self._runtime_request_samples,
                {
                    "outcome": outcome,
                    "terminal_decision": terminal_decision,
                    "response_mode": response_mode,
                    "request_ms": request_ms,
                    "execution_ms": execution_ms,
                },
            )
            if execution_ms is not None:
                self._append(self._runtime_execution_ms, execution_ms)

    def record_api_request(
        self,
        *,
        method: str,
        route_template: str,
        kind: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        with self._lock:
            self._append(
                self._api_samples,
                {
                    "method": method,
                    "route_template": route_template,
                    "kind": kind,
                    "status_code": int(status_code),
                    "duration_ms": max(0.0, float(duration_ms)),
                },
            )

    def record_publish_overhead(self, *, duration_ms: float, failed: bool) -> None:
        with self._lock:
            self._append(self._publish_overhead_ms, max(0.0, float(duration_ms)))
            if failed:
                self._publisher_failures += 1

    def record_persistence(self, *, event_id: str, duration_ms: float) -> None:
        persisted_perf = perf_counter()
        with self._lock:
            self._append(self._persistence_duration_ms, max(0.0, float(duration_ms)))
            self._persisted_perf[event_id] = persisted_perf
            self._persisted_perf.move_to_end(event_id)
            while len(self._persisted_perf) > self.sample_limit:
                self._persisted_perf.popitem(last=False)

    def record_event_to_persistence(self, *, duration_ms: float) -> None:
        with self._lock:
            self._append(self._event_to_persistence_ms, max(0.0, float(duration_ms)))

    def sse_open(self, *, reconnect: bool, after_sequence: int) -> str:
        connection_id = uuid4().hex
        with self._lock:
            self._connections[connection_id] = {
                "opened_perf": perf_counter(),
                "reconnect": reconnect,
                "first_event_delivered": False,
                "last_sequence": after_sequence,
            }
            self._sse_connections_opened += 1
            if reconnect:
                self._sse_reconnects += 1
        return connection_id

    def sse_event(self, *, connection_id: str, event_id: str, sequence: int) -> None:
        now = perf_counter()
        with self._lock:
            state = self._connections.get(connection_id)
            if state is not None:
                last_sequence = int(state["last_sequence"])
                if sequence <= last_sequence:
                    self._logical_duplicate_events += 1
                elif sequence > last_sequence + 1:
                    self._detected_gap_events += sequence - last_sequence - 1

                if bool(state["reconnect"]) and not bool(state["first_event_delivered"]):
                    self._reconnect_first_event_checks += 1
                    if sequence == last_sequence + 1:
                        self._reconnect_sequential_recoveries += 1
                    self._append(
                        self._reconnect_recovery_ms,
                        (now - float(state["opened_perf"])) * 1000.0,
                    )
                state["first_event_delivered"] = True
                state["last_sequence"] = sequence

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

    @staticmethod
    def _group_runtime_samples(samples: list[dict[str, Any]], key: str) -> dict[str, Any]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for sample in samples:
            value = sample.get(key)
            group = "none" if value is None else str(value)
            grouped[group].append(float(sample["request_ms"]))
        return {group: _summary(values) for group, values in sorted(grouped.items())}

    @staticmethod
    def _group_api_samples(samples: list[dict[str, Any]], key: str) -> dict[str, Any]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for sample in samples:
            grouped[str(sample[key])].append(float(sample["duration_ms"]))
        return {group: _summary(values) for group, values in sorted(grouped.items())}

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

            runtime_samples = list(self._runtime_request_samples)
            api_samples = list(self._api_samples)
            reconnect_rate = (
                0.0
                if self._reconnect_first_event_checks == 0
                else self._reconnect_sequential_recoveries / self._reconnect_first_event_checks
            )
            total_sequence_checks = self._sse_events_delivered
            duplicate_rate = 0.0 if total_sequence_checks == 0 else self._logical_duplicate_events / total_sequence_checks
            gap_rate = 0.0 if total_sequence_checks == 0 else self._detected_gap_events / total_sequence_checks

            return {
                "schema_version": "production-telemetry-v2",
                "uptime_ms": max(0.0, (now - self._created_perf) * 1000.0),
                "startup_readiness_ms": self._startup_readiness_ms,
                "runtime_heartbeat": {
                    "status": heartbeat_status,
                    "age_ms": heartbeat_age_ms,
                    "stale_after_ms": self.heartbeat_stale_after_ms,
                },
                "runtime_requests": {
                    "accepted_inflight": len(self._runtime_started),
                    "request_latency": _summary([float(item["request_ms"]) for item in runtime_samples]),
                    "execution_latency": _summary(list(self._runtime_execution_ms)),
                    "by_outcome": self._group_runtime_samples(runtime_samples, "outcome"),
                    "by_terminal_decision": self._group_runtime_samples(runtime_samples, "terminal_decision"),
                    "by_response_mode": self._group_runtime_samples(runtime_samples, "response_mode"),
                    "sample_count": len(runtime_samples),
                },
                "api": {
                    "request_latency": _summary([float(item["duration_ms"]) for item in api_samples]),
                    "by_kind": self._group_api_samples(api_samples, "kind"),
                    "by_route": self._group_api_samples(api_samples, "route_template"),
                    "status_codes": dict(
                        sorted(
                            {
                                str(code): sum(int(item["status_code"]) == code for item in api_samples)
                                for code in {int(item["status_code"]) for item in api_samples}
                            }.items()
                        )
                    ),
                    "sample_count": len(api_samples),
                },
                "resources": _resource_snapshot(),
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
                    "reconnect_first_event_checks": self._reconnect_first_event_checks,
                    "reconnect_sequential_recoveries": self._reconnect_sequential_recoveries,
                    "reconnect_sequential_recovery_rate": reconnect_rate,
                    "detected_gap_events": self._detected_gap_events,
                    "detected_gap_rate": gap_rate,
                    "logical_duplicate_events": self._logical_duplicate_events,
                    "logical_duplicate_rate": duplicate_rate,
                },
            }
