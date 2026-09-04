from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.load_concurrency_benchmark import (
    LoadBenchmarkProtocol,
    LoadBenchmarkReport,
    LoadPressureObservation,
    LoadRequestObservation,
    analyze_load_benchmark,
)


def _protocol() -> LoadBenchmarkProtocol:
    return LoadBenchmarkProtocol(
        protocol_id="load-contract-001",
        concurrency_levels=(1, 4),
        requests_per_level=4,
        warmup_requests=1,
        completion_timeout_seconds=10,
        pressure_poll_interval_ms=10,
    )


def _requests() -> tuple[LoadRequestObservation, ...]:
    items: list[LoadRequestObservation] = []
    for level in (1, 4):
        for index in range(4):
            state = "completed"
            status = 202
            end_to_end = float(40 + level * 5 + index)
            if level == 4 and index == 3:
                state = "failed"
            items.append(
                LoadRequestObservation(
                    concurrency_level=level,
                    request_index=index,
                    submit_status_code=status,
                    submit_latency_ms=float(2 + index),
                    end_to_end_latency_ms=end_to_end,
                    terminal_state=state,
                )
            )
    return tuple(items)


def _pressure() -> tuple[LoadPressureObservation, ...]:
    return (
        LoadPressureObservation(
            concurrency_level=1,
            elapsed_ms=0,
            active_runs=0,
            queued_runs=0,
            inflight_runs=0,
            max_workers=2,
            executor_utilization=0,
            process_cpu_time_ms=100,
            rss_current_bytes=1000,
            rss_max_bytes=1200,
            persistence_p95_ms=1.0,
        ),
        LoadPressureObservation(
            concurrency_level=1,
            elapsed_ms=20,
            active_runs=1,
            queued_runs=0,
            inflight_runs=1,
            max_workers=2,
            executor_utilization=0.5,
            process_cpu_time_ms=110,
            rss_current_bytes=1100,
            rss_max_bytes=1300,
            persistence_p95_ms=1.4,
        ),
        LoadPressureObservation(
            concurrency_level=4,
            elapsed_ms=0,
            active_runs=2,
            queued_runs=2,
            inflight_runs=4,
            max_workers=2,
            executor_utilization=1.0,
            process_cpu_time_ms=120,
            rss_current_bytes=1200,
            rss_max_bytes=1400,
            persistence_p95_ms=2.0,
        ),
        LoadPressureObservation(
            concurrency_level=4,
            elapsed_ms=30,
            active_runs=2,
            queued_runs=1,
            inflight_runs=3,
            max_workers=2,
            executor_utilization=1.0,
            process_cpu_time_ms=145,
            rss_current_bytes=1500,
            rss_max_bytes=1600,
            persistence_p95_ms=2.8,
        ),
    )


def test_load_report_is_descriptive_hash_bound_and_includes_p99_pressure_and_throughput() -> None:
    protocol = _protocol()
    report = analyze_load_benchmark(
        protocol,
        requests=_requests(),
        pressure=_pressure(),
        wall_duration_seconds={1: 0.4, 4: 0.2},
    )

    assert report.status == "MEASURED"
    assert report.thresholds_preregistered is False
    assert report.interpretation == "descriptive_only"
    assert report.production_capacity_claim_ready is False
    assert report.protocol_sha256 == protocol.sha256()
    assert report.total_requests == 8
    assert len(report.evidence_sha256) == 64

    level_1, level_4 = report.levels
    assert level_1.completed_count == 4
    assert level_1.error_rate == 0
    assert level_1.completed_throughput_rps == 10
    assert level_1.submit_latency.p99_ms is not None
    assert level_1.end_to_end_latency.p99_ms is not None
    assert level_1.peak_executor_utilization == 0.5
    assert level_1.cpu_time_delta_ms == 10

    assert level_4.completed_count == 3
    assert level_4.failed_count == 1
    assert level_4.error_rate == 0.25
    assert level_4.completed_throughput_rps == 15
    assert level_4.peak_active_runs == 2
    assert level_4.peak_queued_runs == 2
    assert level_4.peak_inflight_runs == 4
    assert level_4.peak_executor_utilization == 1.0
    assert level_4.rss_peak_bytes == 1500
    assert level_4.persistence_p95_ms_max_observed == 2.8


def test_load_analysis_fails_closed_on_missing_duplicate_or_unexpected_observations() -> None:
    protocol = _protocol()

    with pytest.raises(ValueError, match="every preregistered index"):
        analyze_load_benchmark(
            protocol,
            requests=_requests()[:-1],
            pressure=_pressure(),
            wall_duration_seconds={1: 0.4, 4: 0.2},
        )

    duplicate = _requests() + (_requests()[-1],)
    with pytest.raises(ValueError, match="every preregistered index"):
        analyze_load_benchmark(
            protocol,
            requests=duplicate,
            pressure=_pressure(),
            wall_duration_seconds={1: 0.4, 4: 0.2},
        )

    unexpected = _requests() + (
        LoadRequestObservation(
            concurrency_level=8,
            request_index=0,
            submit_status_code=202,
            submit_latency_ms=1,
            end_to_end_latency_ms=2,
            terminal_state="completed",
        ),
    )
    with pytest.raises(ValueError, match="unexpected concurrency level"):
        analyze_load_benchmark(
            protocol,
            requests=unexpected,
            pressure=_pressure(),
            wall_duration_seconds={1: 0.4, 4: 0.2},
        )

    with pytest.raises(ValueError, match="at least one pressure sample"):
        analyze_load_benchmark(
            protocol,
            requests=_requests(),
            pressure=tuple(item for item in _pressure() if item.concurrency_level == 1),
            wall_duration_seconds={1: 0.4, 4: 0.2},
        )


def test_load_protocol_and_observation_shapes_reject_posthoc_or_inconsistent_data() -> None:
    with pytest.raises(ValidationError):
        LoadBenchmarkProtocol(
            protocol_id="load-contract-002",
            concurrency_levels=(4, 1),
            requests_per_level=4,
        )

    with pytest.raises(ValidationError):
        LoadRequestObservation(
            concurrency_level=1,
            request_index=0,
            submit_status_code=500,
            submit_latency_ms=1,
            end_to_end_latency_ms=2,
            terminal_state="completed",
        )

    with pytest.raises(ValidationError):
        LoadPressureObservation(
            concurrency_level=4,
            elapsed_ms=1,
            active_runs=2,
            queued_runs=2,
            inflight_runs=5,
            max_workers=2,
            executor_utilization=1,
        )


def test_load_report_rejects_evidence_hash_tampering() -> None:
    report = analyze_load_benchmark(
        _protocol(),
        requests=_requests(),
        pressure=_pressure(),
        wall_duration_seconds={1: 0.4, 4: 0.2},
    )
    payload = report.model_dump(mode="json")
    payload["total_requests"] = 9
    with pytest.raises(ValidationError, match="evidence hash mismatch"):
        LoadBenchmarkReport.model_validate(payload)
