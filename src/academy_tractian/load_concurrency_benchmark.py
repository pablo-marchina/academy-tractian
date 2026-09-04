from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite
from statistics import mean
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


TerminalState = Literal[
    "completed",
    "failed",
    "interrupted",
    "uncertain",
    "submit_rejected",
    "timeout",
]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _percentile(values: tuple[float, ...], percentile: float) -> float | None:
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


class LoadBenchmarkProtocol(_FrozenModel):
    """Preregistered provider-free load protocol.

    The protocol is intentionally descriptive. It freezes the workload shape before outcomes are
    observed but does not contain a post-hoc pass/fail threshold or a production-capacity claim.
    """

    schema_version: Literal["load-concurrency-protocol-v1"] = "load-concurrency-protocol-v1"
    status: Literal["FROZEN"] = "FROZEN"
    protocol_id: str = Field(min_length=8, max_length=128)
    concurrency_levels: tuple[int, ...] = Field(min_length=1, max_length=16)
    requests_per_level: int = Field(ge=1, le=10000)
    warmup_requests: int = Field(default=0, ge=0, le=1000)
    completion_timeout_seconds: float = Field(default=30.0, ge=1.0, le=600.0)
    pressure_poll_interval_ms: int = Field(default=25, ge=5, le=5000)

    @model_validator(mode="after")
    def validate_levels(self) -> "LoadBenchmarkProtocol":
        if any(level < 1 or level > 256 for level in self.concurrency_levels):
            raise ValueError("concurrency levels must be within [1, 256]")
        if tuple(sorted(set(self.concurrency_levels))) != self.concurrency_levels:
            raise ValueError("concurrency levels must be unique and strictly increasing")
        if not isfinite(self.completion_timeout_seconds):
            raise ValueError("completion timeout must be finite")
        return self

    def sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class LoadRequestObservation(_FrozenModel):
    """Ephemeral request measurement with no run, user, tenant, prompt or credential identifiers."""

    concurrency_level: int = Field(ge=1)
    request_index: int = Field(ge=0)
    submit_status_code: int = Field(ge=100, le=599)
    submit_latency_ms: float = Field(ge=0)
    end_to_end_latency_ms: float | None = Field(default=None, ge=0)
    terminal_state: TerminalState

    @model_validator(mode="after")
    def validate_shape(self) -> "LoadRequestObservation":
        numeric = [self.submit_latency_ms]
        if self.end_to_end_latency_ms is not None:
            numeric.append(self.end_to_end_latency_ms)
        if not all(isfinite(value) for value in numeric):
            raise ValueError("load request latency must be finite")
        if self.terminal_state in {"completed", "failed", "interrupted", "uncertain"}:
            if self.submit_status_code != 202 or self.end_to_end_latency_ms is None:
                raise ValueError("accepted terminal request requires 202 and end-to-end latency")
        if self.terminal_state == "submit_rejected":
            if self.submit_status_code == 202 or self.end_to_end_latency_ms is not None:
                raise ValueError("submit rejection cannot look accepted or carry completion latency")
        if self.terminal_state == "timeout":
            if self.submit_status_code != 202 or self.end_to_end_latency_ms is None:
                raise ValueError("timeout requires accepted submission and observed elapsed latency")
        return self


class LoadPressureObservation(_FrozenModel):
    """Safe process/executor sample captured while a load level is running."""

    concurrency_level: int = Field(ge=1)
    elapsed_ms: float = Field(ge=0)
    active_runs: int = Field(ge=0)
    queued_runs: int = Field(ge=0)
    inflight_runs: int = Field(ge=0)
    max_workers: int = Field(ge=1)
    executor_utilization: float = Field(ge=0)
    process_cpu_time_ms: float | None = Field(default=None, ge=0)
    rss_current_bytes: int | None = Field(default=None, ge=0)
    rss_max_bytes: int | None = Field(default=None, ge=0)
    persistence_p95_ms: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_pressure(self) -> "LoadPressureObservation":
        if self.inflight_runs != self.active_runs + self.queued_runs:
            raise ValueError("inflight_runs must equal active_runs + queued_runs")
        if self.executor_utilization > 1.0:
            raise ValueError("executor utilization must be within [0, 1]")
        finite_values = [self.elapsed_ms, self.executor_utilization]
        for value in (self.process_cpu_time_ms, self.persistence_p95_ms):
            if value is not None:
                finite_values.append(value)
        if not all(isfinite(value) for value in finite_values):
            raise ValueError("pressure measurements must be finite")
        return self


class LatencySummary(_FrozenModel):
    count: int = Field(ge=0)
    avg_ms: float | None = Field(default=None, ge=0)
    p50_ms: float | None = Field(default=None, ge=0)
    p95_ms: float | None = Field(default=None, ge=0)
    p99_ms: float | None = Field(default=None, ge=0)
    max_ms: float | None = Field(default=None, ge=0)


class LoadLevelResult(_FrozenModel):
    concurrency_level: int = Field(ge=1)
    request_count: int = Field(ge=1)
    accepted_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    interrupted_count: int = Field(ge=0)
    uncertain_count: int = Field(ge=0)
    submit_rejected_count: int = Field(ge=0)
    timeout_count: int = Field(ge=0)
    error_rate: float = Field(ge=0, le=1)
    wall_duration_seconds: float = Field(gt=0)
    completed_throughput_rps: float = Field(ge=0)
    submit_latency: LatencySummary
    end_to_end_latency: LatencySummary
    pressure_sample_count: int = Field(ge=1)
    peak_active_runs: int = Field(ge=0)
    peak_queued_runs: int = Field(ge=0)
    peak_inflight_runs: int = Field(ge=0)
    peak_executor_utilization: float = Field(ge=0, le=1)
    cpu_time_delta_ms: float | None = Field(default=None, ge=0)
    rss_start_bytes: int | None = Field(default=None, ge=0)
    rss_end_bytes: int | None = Field(default=None, ge=0)
    rss_peak_bytes: int | None = Field(default=None, ge=0)
    persistence_p95_ms_max_observed: float | None = Field(default=None, ge=0)


class LoadBenchmarkReport(_FrozenModel):
    schema_version: Literal["load-concurrency-report-v1"] = "load-concurrency-report-v1"
    status: Literal["MEASURED"] = "MEASURED"
    thresholds_preregistered: Literal[False] = False
    interpretation: Literal["descriptive_only"] = "descriptive_only"
    production_capacity_claim_ready: Literal[False] = False
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    total_requests: int = Field(ge=1)
    levels: tuple[LoadLevelResult, ...] = Field(min_length=1)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_hash(self) -> "LoadBenchmarkReport":
        payload = self.model_dump(mode="json", exclude={"evidence_sha256"})
        if _canonical_sha256(payload) != self.evidence_sha256:
            raise ValueError("load benchmark evidence hash mismatch")
        return self


def _latency_summary(values: tuple[float, ...]) -> LatencySummary:
    return LatencySummary(
        count=len(values),
        avg_ms=None if not values else mean(values),
        p50_ms=_percentile(values, 0.50),
        p95_ms=_percentile(values, 0.95),
        p99_ms=_percentile(values, 0.99),
        max_ms=None if not values else max(values),
    )


def analyze_load_benchmark(
    protocol: LoadBenchmarkProtocol,
    *,
    requests: tuple[LoadRequestObservation, ...],
    pressure: tuple[LoadPressureObservation, ...],
    wall_duration_seconds: dict[int, float],
) -> LoadBenchmarkReport:
    """Aggregate one preregistered load campaign without inventing capacity thresholds."""

    allowed_levels = set(protocol.concurrency_levels)
    if set(wall_duration_seconds) != allowed_levels:
        raise ValueError("wall duration levels do not match frozen protocol")
    if any(not isfinite(value) or value <= 0 for value in wall_duration_seconds.values()):
        raise ValueError("wall duration must be finite and positive")

    by_level_requests: dict[int, list[LoadRequestObservation]] = {
        level: [] for level in protocol.concurrency_levels
    }
    for observation in requests:
        if observation.concurrency_level not in allowed_levels:
            raise ValueError("request observation contains unexpected concurrency level")
        by_level_requests[observation.concurrency_level].append(observation)

    by_level_pressure: dict[int, list[LoadPressureObservation]] = {
        level: [] for level in protocol.concurrency_levels
    }
    for observation in pressure:
        if observation.concurrency_level not in allowed_levels:
            raise ValueError("pressure observation contains unexpected concurrency level")
        by_level_pressure[observation.concurrency_level].append(observation)

    levels: list[LoadLevelResult] = []
    for level in protocol.concurrency_levels:
        observations = sorted(by_level_requests[level], key=lambda item: item.request_index)
        expected_indices = list(range(protocol.requests_per_level))
        if [item.request_index for item in observations] != expected_indices:
            raise ValueError("request observations must contain every preregistered index exactly once")

        pressure_samples = sorted(by_level_pressure[level], key=lambda item: item.elapsed_ms)
        if not pressure_samples:
            raise ValueError("each concurrency level requires at least one pressure sample")
        if any(sample.max_workers != pressure_samples[0].max_workers for sample in pressure_samples):
            raise ValueError("max_workers changed within one load level")

        accepted = sum(item.submit_status_code == 202 for item in observations)
        counts = {
            state: sum(item.terminal_state == state for item in observations)
            for state in (
                "completed",
                "failed",
                "interrupted",
                "uncertain",
                "submit_rejected",
                "timeout",
            )
        }
        error_count = len(observations) - counts["completed"]
        submit_latencies = tuple(item.submit_latency_ms for item in observations)
        end_to_end_latencies = tuple(
            item.end_to_end_latency_ms
            for item in observations
            if item.end_to_end_latency_ms is not None
        )
        duration = wall_duration_seconds[level]

        cpu_values = tuple(
            sample.process_cpu_time_ms
            for sample in pressure_samples
            if sample.process_cpu_time_ms is not None
        )
        rss_values = tuple(
            sample.rss_current_bytes
            for sample in pressure_samples
            if sample.rss_current_bytes is not None
        )
        persistence_values = tuple(
            sample.persistence_p95_ms
            for sample in pressure_samples
            if sample.persistence_p95_ms is not None
        )

        levels.append(
            LoadLevelResult(
                concurrency_level=level,
                request_count=len(observations),
                accepted_count=accepted,
                completed_count=counts["completed"],
                failed_count=counts["failed"],
                interrupted_count=counts["interrupted"],
                uncertain_count=counts["uncertain"],
                submit_rejected_count=counts["submit_rejected"],
                timeout_count=counts["timeout"],
                error_rate=error_count / len(observations),
                wall_duration_seconds=duration,
                completed_throughput_rps=counts["completed"] / duration,
                submit_latency=_latency_summary(submit_latencies),
                end_to_end_latency=_latency_summary(end_to_end_latencies),
                pressure_sample_count=len(pressure_samples),
                peak_active_runs=max(sample.active_runs for sample in pressure_samples),
                peak_queued_runs=max(sample.queued_runs for sample in pressure_samples),
                peak_inflight_runs=max(sample.inflight_runs for sample in pressure_samples),
                peak_executor_utilization=max(
                    sample.executor_utilization for sample in pressure_samples
                ),
                cpu_time_delta_ms=None
                if len(cpu_values) < 2
                else max(0.0, cpu_values[-1] - cpu_values[0]),
                rss_start_bytes=None if not rss_values else rss_values[0],
                rss_end_bytes=None if not rss_values else rss_values[-1],
                rss_peak_bytes=None if not rss_values else max(rss_values),
                persistence_p95_ms_max_observed=None
                if not persistence_values
                else max(persistence_values),
            )
        )

    payload = {
        "schema_version": "load-concurrency-report-v1",
        "status": "MEASURED",
        "thresholds_preregistered": False,
        "interpretation": "descriptive_only",
        "production_capacity_claim_ready": False,
        "protocol_sha256": protocol.sha256(),
        "total_requests": len(requests),
        "levels": [item.model_dump(mode="json") for item in levels],
    }
    return LoadBenchmarkReport(
        **payload,
        evidence_sha256=_canonical_sha256(payload),
    )
