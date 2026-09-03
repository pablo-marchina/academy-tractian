from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
from statistics import mean
import tempfile
from time import perf_counter
from typing import Any, Callable

from .adapters import (
    DuckDBOperationalCandidate,
    OperationalStoreCandidate,
    PostgreSQLOperationalCandidate,
)


DECISION_ID = "OPS-STORE-001"
BENCHMARK_SCHEMA_VERSION = "operational-store-benchmark-v1"
DEFAULT_CONCURRENCY = (1, 5, 10, 25)
HARD_GATE_KEYS = (
    "unexpected_operational_errors",
    "conflicting_ownership_takeover",
    "duplicate_logical_ownership_creation",
    "lost_committed_operational_rows",
    "invalid_execution_state_transition_accepted",
    "cross_tenant_rows_scoped_api",
    "terminal_execution_state_corrupted_after_reconnect",
    "orphaned_runtime_replayed_automatically",
    "orphaned_action_replayed_automatically",
    "postgresql_rls_cross_tenant_visibility",
)


@dataclass(slots=True)
class WorkloadSamples:
    lifecycle_ms: list[float] = field(default_factory=list)
    claim_ms: list[float] = field(default_factory=list)
    scoped_read_ms: list[float] = field(default_factory=list)
    transition_ms: list[float] = field(default_factory=list)
    successes: int = 0
    new_claims: int = 0
    errors: int = 0
    error_types: Counter[str] = field(default_factory=Counter)

    def merge(self, other: "WorkloadSamples") -> None:
        self.lifecycle_ms.extend(other.lifecycle_ms)
        self.claim_ms.extend(other.claim_ms)
        self.scoped_read_ms.extend(other.scoped_read_ms)
        self.transition_ms.extend(other.transition_ms)
        self.successes += other.successes
        self.new_claims += other.new_claims
        self.errors += other.errors
        self.error_types.update(other.error_types)


@dataclass(slots=True)
class CandidateAccumulator:
    name: str
    metadata: dict[str, str] = field(default_factory=dict)
    hard_gates: dict[str, int] = field(
        default_factory=lambda: {key: 0 for key in HARD_GATE_KEYS}
    )
    repetitions: list[dict[str, Any]] = field(default_factory=list)
    raw_by_concurrency: dict[int, WorkloadSamples] = field(
        default_factory=lambda: defaultdict(WorkloadSamples)
    )
    total_wall_seconds_by_concurrency: dict[int, float] = field(
        default_factory=lambda: defaultdict(float)
    )
    infrastructure_errors: list[str] = field(default_factory=list)


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(q * len(ordered)) - 1))
    return round(float(ordered[index]), 6)


def _latency_summary(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "p50_ms": _percentile(values, 0.50),
        "p95_ms": _percentile(values, 0.95),
        "p99_ms": _percentile(values, 0.99),
        "mean_ms": None if not values else round(mean(values), 6),
    }


def _sample_summary(samples: WorkloadSamples, wall_seconds: float) -> dict[str, Any]:
    attempts = samples.successes + samples.errors
    return {
        "attempts": attempts,
        "successes": samples.successes,
        "new_claims": samples.new_claims,
        "errors": samples.errors,
        "error_rate": 0.0 if attempts == 0 else round(samples.errors / attempts, 8),
        "error_types": dict(sorted(samples.error_types.items())),
        "wall_seconds": round(wall_seconds, 6),
        "throughput_lifecycles_per_second": (
            0.0 if wall_seconds <= 0 else round(samples.successes / wall_seconds, 6)
        ),
        "lifecycle": _latency_summary(samples.lifecycle_ms),
        "claim": _latency_summary(samples.claim_ms),
        "scoped_read": _latency_summary(samples.scoped_read_ms),
        "transition": _latency_summary(samples.transition_ms),
    }


def _timed(call: Callable[[], Any]) -> tuple[Any, float]:
    started = perf_counter()
    value = call()
    return value, (perf_counter() - started) * 1000.0


def _run_worker(
    *,
    candidate: OperationalStoreCandidate,
    prefix: str,
    worker_index: int,
    operations: int,
) -> WorkloadSamples:
    samples = WorkloadSamples()
    organization_id = f"org-{worker_index % 3}"
    user_id = f"user-{worker_index}"
    for operation_index in range(operations):
        run_id = f"{prefix}-w{worker_index:02d}-o{operation_index:04d}"
        lifecycle_started = perf_counter()
        try:
            claimed, elapsed = _timed(
                lambda: candidate.claim_run(
                    run_id=run_id,
                    organization_id=organization_id,
                    user_id=user_id,
                )
            )
            samples.claim_ms.append(elapsed)
            if claimed:
                samples.new_claims += 1

            candidate.create_execution(
                run_id=run_id,
                organization_id=organization_id,
            )

            transitioned, elapsed = _timed(
                lambda: candidate.transition_execution(
                    run_id=run_id,
                    organization_id=organization_id,
                    expected_states=frozenset({"accepted"}),
                    new_state="running",
                )
            )
            samples.transition_ms.append(elapsed)
            if not transitioned:
                raise RuntimeError("accepted_to_running_transition_rejected")

            owner, elapsed = _timed(
                lambda: candidate.scoped_owner(
                    run_id=run_id,
                    organization_id=organization_id,
                )
            )
            samples.scoped_read_ms.append(elapsed)
            if owner is None or owner.user_id != user_id:
                raise RuntimeError("scoped_owner_mismatch")

            transitioned, elapsed = _timed(
                lambda: candidate.transition_execution(
                    run_id=run_id,
                    organization_id=organization_id,
                    expected_states=frozenset({"running"}),
                    new_state="completed",
                )
            )
            samples.transition_ms.append(elapsed)
            if not transitioned:
                raise RuntimeError("running_to_completed_transition_rejected")

            state = candidate.execution_state(
                run_id=run_id,
                organization_id=organization_id,
            )
            if state != "completed":
                raise RuntimeError("terminal_state_mismatch")

            samples.successes += 1
            samples.lifecycle_ms.append((perf_counter() - lifecycle_started) * 1000.0)
        except Exception as exc:  # benchmark records candidate-visible operational failures
            samples.errors += 1
            samples.error_types[type(exc).__name__] += 1
    return samples


def _run_mixed_workload(
    *,
    candidate: OperationalStoreCandidate,
    prefix: str,
    concurrency: int,
    operations_per_worker: int,
) -> tuple[WorkloadSamples, float]:
    started = perf_counter()
    combined = WorkloadSamples()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(
                _run_worker,
                candidate=candidate,
                prefix=prefix,
                worker_index=worker_index,
                operations=operations_per_worker,
            )
            for worker_index in range(concurrency)
        ]
        for future in futures:
            combined.merge(future.result())
    return combined, perf_counter() - started


def _run_warmup(candidate: OperationalStoreCandidate, *, prefix: str) -> int:
    samples = _run_worker(
        candidate=candidate,
        prefix=prefix,
        worker_index=0,
        operations=3,
    )
    return samples.errors


def _add_gate(accumulator: CandidateAccumulator, gate: str, amount: int | bool) -> None:
    accumulator.hard_gates[gate] += int(amount)


def _run_safety_probes(
    *,
    candidate: OperationalStoreCandidate,
    accumulator: CandidateAccumulator,
    repetition: int,
) -> dict[str, Any]:
    probe_prefix = f"probe-r{repetition:02d}"
    org_a = "probe-org-a"
    org_b = "probe-org-b"
    user_a = "probe-user-a"

    contention_run = f"{probe_prefix}-contended"
    contention_errors = 0
    claim_results: list[bool] = []

    def contend() -> None:
        nonlocal contention_errors
        try:
            claim_results.append(
                candidate.claim_run(
                    run_id=contention_run,
                    organization_id=org_a,
                    user_id=user_a,
                )
            )
        except Exception:
            contention_errors += 1

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(contend) for _ in range(50)]
        for future in futures:
            future.result()

    _add_gate(accumulator, "unexpected_operational_errors", contention_errors)
    _add_gate(
        accumulator,
        "duplicate_logical_ownership_creation",
        max(0, sum(bool(value) for value in claim_results) - 1),
    )

    takeover_failed = 0
    try:
        result = candidate.claim_run(
            run_id=contention_run,
            organization_id=org_a,
            user_id="different-user",
        )
        if result is True or result is False:
            takeover_failed = 1
    except RuntimeError:
        pass
    except Exception:
        _add_gate(accumulator, "unexpected_operational_errors", 1)
        takeover_failed = 1
    owner = candidate.scoped_owner(run_id=contention_run, organization_id=org_a)
    if owner is None or owner.user_id != user_a:
        takeover_failed += 1
    _add_gate(accumulator, "conflicting_ownership_takeover", takeover_failed)

    cross_tenant = candidate.scoped_owner(
        run_id=contention_run,
        organization_id=org_b,
    )
    _add_gate(accumulator, "cross_tenant_rows_scoped_api", cross_tenant is not None)

    rls_probe = candidate.direct_cross_tenant_probe(
        run_id=contention_run,
        organization_id=org_b,
    )
    if candidate.name == "postgresql":
        _add_gate(
            accumulator,
            "postgresql_rls_cross_tenant_visibility",
            0 if rls_probe == 0 else 1,
        )

    transition_run = f"{probe_prefix}-transition"
    candidate.claim_run(run_id=transition_run, organization_id=org_a, user_id=user_a)
    candidate.create_execution(run_id=transition_run, organization_id=org_a)
    invalid_accepted = candidate.transition_execution(
        run_id=transition_run,
        organization_id=org_a,
        expected_states=frozenset({"running"}),
        new_state="completed",
    )
    _add_gate(
        accumulator,
        "invalid_execution_state_transition_accepted",
        invalid_accepted,
    )
    if not candidate.transition_execution(
        run_id=transition_run,
        organization_id=org_a,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    ):
        _add_gate(accumulator, "unexpected_operational_errors", 1)
    if not candidate.transition_execution(
        run_id=transition_run,
        organization_id=org_a,
        expected_states=frozenset({"running"}),
        new_state="completed",
    ):
        _add_gate(accumulator, "unexpected_operational_errors", 1)

    terminal_run = f"{probe_prefix}-terminal"
    candidate.claim_run(run_id=terminal_run, organization_id=org_a, user_id=user_a)
    candidate.create_execution(run_id=terminal_run, organization_id=org_a)
    candidate.transition_execution(
        run_id=terminal_run,
        organization_id=org_a,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )
    candidate.transition_execution(
        run_id=terminal_run,
        organization_id=org_a,
        expected_states=frozenset({"running"}),
        new_state="completed",
    )
    candidate.reconnect()
    owner_after = candidate.scoped_owner(run_id=terminal_run, organization_id=org_a)
    state_after = candidate.execution_state(run_id=terminal_run, organization_id=org_a)
    terminal_corruption = int(
        owner_after is None
        or owner_after.user_id != user_a
        or state_after != "completed"
    )
    _add_gate(
        accumulator,
        "terminal_execution_state_corrupted_after_reconnect",
        terminal_corruption,
    )

    runtime_orphan = f"{probe_prefix}-runtime-orphan"
    candidate.claim_run(run_id=runtime_orphan, organization_id=org_a, user_id=user_a)
    candidate.create_execution(run_id=runtime_orphan, organization_id=org_a)
    candidate.transition_execution(
        run_id=runtime_orphan,
        organization_id=org_a,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )

    action_orphan = f"{probe_prefix}-action-orphan"
    candidate.claim_run(run_id=action_orphan, organization_id=org_a, user_id=user_a)
    candidate.create_execution(
        run_id=action_orphan,
        organization_id=org_a,
        execution_kind="action",
        related_action_id=f"action-{repetition}",
    )
    candidate.transition_execution(
        run_id=action_orphan,
        organization_id=org_a,
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )

    recovery = candidate.reconcile_orphaned()
    runtime_state = candidate.execution_state(run_id=runtime_orphan, organization_id=org_a)
    action_state = candidate.execution_state(run_id=action_orphan, organization_id=org_a)
    _add_gate(
        accumulator,
        "orphaned_runtime_replayed_automatically",
        0 if runtime_state == "interrupted" else 1,
    )
    _add_gate(
        accumulator,
        "orphaned_action_replayed_automatically",
        0 if action_state == "uncertain" else 1,
    )

    return {
        "contention_attempts": 50,
        "contention_new_claims": sum(bool(value) for value in claim_results),
        "contention_errors": contention_errors,
        "cross_tenant_scoped_visible": cross_tenant is not None,
        "direct_rls_visible_rows": rls_probe,
        "invalid_transition_accepted": invalid_accepted,
        "terminal_state_after_reconnect": state_after,
        "recovery": recovery,
        "runtime_orphan_state": runtime_state,
        "action_orphan_state": action_state,
    }


def _run_candidate_repetition(
    *,
    candidate: OperationalStoreCandidate,
    accumulator: CandidateAccumulator,
    repetition: int,
    concurrency_levels: tuple[int, ...],
    operations_per_worker: int,
) -> None:
    candidate.reset()
    if not accumulator.metadata:
        accumulator.metadata = candidate.metadata()

    repetition_result: dict[str, Any] = {
        "repetition": repetition,
        "mixed_workload": {},
    }
    warmup_errors = _run_warmup(candidate, prefix=f"warmup-r{repetition:02d}")
    _add_gate(accumulator, "unexpected_operational_errors", warmup_errors)
    repetition_result["warmup_errors"] = warmup_errors

    for concurrency in concurrency_levels:
        prefix = f"w1-r{repetition:02d}-c{concurrency:02d}"
        samples, wall_seconds = _run_mixed_workload(
            candidate=candidate,
            prefix=prefix,
            concurrency=concurrency,
            operations_per_worker=operations_per_worker,
        )
        counts = candidate.prefix_counts(prefix)
        lost_ownership = max(0, samples.new_claims - counts.get("ownership", 0))
        lost_completed = max(0, samples.successes - counts.get("completed", 0))
        _add_gate(
            accumulator,
            "lost_committed_operational_rows",
            lost_ownership + lost_completed,
        )
        _add_gate(accumulator, "unexpected_operational_errors", samples.errors)

        accumulator.raw_by_concurrency[concurrency].merge(samples)
        accumulator.total_wall_seconds_by_concurrency[concurrency] += wall_seconds
        result = _sample_summary(samples, wall_seconds)
        result["persisted_prefix_counts"] = counts
        result["expected_new_ownership_rows"] = samples.new_claims
        result["expected_completed_rows"] = samples.successes
        repetition_result["mixed_workload"][str(concurrency)] = result

    candidate.reset()
    repetition_result["safety_probes"] = _run_safety_probes(
        candidate=candidate,
        accumulator=accumulator,
        repetition=repetition,
    )
    accumulator.repetitions.append(repetition_result)


def _aggregate_candidate(accumulator: CandidateAccumulator) -> dict[str, Any]:
    aggregate_by_concurrency: dict[str, Any] = {}
    for concurrency, samples in sorted(accumulator.raw_by_concurrency.items()):
        aggregate_by_concurrency[str(concurrency)] = _sample_summary(
            samples,
            accumulator.total_wall_seconds_by_concurrency[concurrency],
        )
    hard_gate_pass = all(value == 0 for value in accumulator.hard_gates.values())
    return {
        "candidate": accumulator.name,
        "metadata": accumulator.metadata,
        "benchmark_valid": not accumulator.infrastructure_errors,
        "eligible_after_hard_gates": hard_gate_pass and not accumulator.infrastructure_errors,
        "hard_gates": dict(accumulator.hard_gates),
        "infrastructure_errors": accumulator.infrastructure_errors,
        "aggregate_by_concurrency": aggregate_by_concurrency,
        "repetitions": accumulator.repetitions,
    }


def _metric(candidate: dict[str, Any], concurrency: int, metric: str) -> float | None:
    row = candidate["aggregate_by_concurrency"].get(str(concurrency))
    if not row:
        return None
    if metric == "p95":
        value = row["lifecycle"]["p95_ms"]
    elif metric == "throughput":
        value = row["throughput_lifecycles_per_second"]
    else:
        raise ValueError(metric)
    return None if value is None else float(value)


def _decision(
    duckdb_result: dict[str, Any] | None,
    postgres_result: dict[str, Any] | None,
    *,
    highest_concurrency: int,
) -> dict[str, Any]:
    if duckdb_result is None or postgres_result is None:
        return {
            "outcome": "INCONCLUSIVE",
            "reason": "both preregistered candidates were not measured",
        }
    if not duckdb_result["benchmark_valid"] or not postgres_result["benchmark_valid"]:
        return {
            "outcome": "INCONCLUSIVE",
            "reason": "benchmark infrastructure invalid for at least one candidate",
        }

    duck_eligible = bool(duckdb_result["eligible_after_hard_gates"])
    pg_eligible = bool(postgres_result["eligible_after_hard_gates"])
    if pg_eligible and not duck_eligible:
        return {
            "outcome": "PROMOTE_POSTGRES_OPERATIONAL",
            "reason": "PostgreSQL passed all hard gates while DuckDB failed at least one",
        }
    if duck_eligible and not pg_eligible:
        return {
            "outcome": "KEEP_DUCKDB_SINGLE_NODE",
            "reason": "DuckDB passed all hard gates while PostgreSQL failed at least one",
        }
    if not duck_eligible and not pg_eligible:
        return {
            "outcome": "INCONCLUSIVE",
            "reason": "neither candidate passed all preregistered hard gates",
        }

    duck_single = _metric(duckdb_result, 1, "p95")
    pg_single = _metric(postgres_result, 1, "p95")
    duck_high_p95 = _metric(duckdb_result, highest_concurrency, "p95")
    pg_high_p95 = _metric(postgres_result, highest_concurrency, "p95")
    duck_high_throughput = _metric(duckdb_result, highest_concurrency, "throughput")
    pg_high_throughput = _metric(postgres_result, highest_concurrency, "throughput")

    required = (
        duck_single,
        pg_single,
        duck_high_p95,
        pg_high_p95,
        duck_high_throughput,
        pg_high_throughput,
    )
    if any(value is None for value in required):
        return {
            "outcome": "INCONCLUSIVE",
            "reason": "insufficient successful samples for preregistered materiality test",
        }

    assert duck_single is not None
    assert pg_single is not None
    assert duck_high_p95 is not None
    assert pg_high_p95 is not None
    assert duck_high_throughput is not None
    assert pg_high_throughput is not None

    if pg_single > 2.0 * duck_single:
        return {
            "outcome": "INCONCLUSIVE",
            "reason": "PostgreSQL violates the preregistered 2x single-user p95 guardrail",
            "ratios": {"postgres_to_duckdb_single_user_p95": pg_single / duck_single},
        }

    lower_p95_condition = (
        pg_high_p95 <= 0.80 * duck_high_p95
        and pg_high_throughput >= 0.90 * duck_high_throughput
    )
    higher_throughput_condition = (
        pg_high_throughput >= 1.25 * duck_high_throughput
        and pg_high_p95 <= 1.10 * duck_high_p95
    )
    if lower_p95_condition or higher_throughput_condition:
        return {
            "outcome": "PROMOTE_POSTGRES_OPERATIONAL",
            "reason": "both candidates passed hard gates and PostgreSQL met a preregistered materiality threshold",
            "materiality": {
                "lower_p95_condition": lower_p95_condition,
                "higher_throughput_condition": higher_throughput_condition,
                "postgres_to_duckdb_high_concurrency_p95": pg_high_p95 / duck_high_p95,
                "postgres_to_duckdb_high_concurrency_throughput": pg_high_throughput / duck_high_throughput,
                "postgres_to_duckdb_single_user_p95": pg_single / duck_single,
            },
        }

    return {
        "outcome": "KEEP_DUCKDB_SINGLE_NODE",
        "reason": "both candidates passed hard gates but PostgreSQL did not meet a preregistered materiality threshold",
        "materiality": {
            "lower_p95_condition": False,
            "higher_throughput_condition": False,
            "postgres_to_duckdb_high_concurrency_p95": pg_high_p95 / duck_high_p95,
            "postgres_to_duckdb_high_concurrency_throughput": pg_high_throughput / duck_high_throughput,
            "postgres_to_duckdb_single_user_p95": pg_single / duck_single,
        },
    }


def run_benchmark(
    *,
    postgres_dsn: str | None,
    concurrency_levels: tuple[int, ...] = DEFAULT_CONCURRENCY,
    repetitions: int = 3,
    operations_per_worker: int = 50,
    work_root: str | Path | None = None,
) -> dict[str, Any]:
    if repetitions < 1:
        raise ValueError("repetitions must be >= 1")
    if operations_per_worker < 1:
        raise ValueError("operations_per_worker must be >= 1")
    if not concurrency_levels or any(level < 1 for level in concurrency_levels):
        raise ValueError("concurrency levels must be positive")

    managed_tmp: tempfile.TemporaryDirectory[str] | None = None
    if work_root is None:
        managed_tmp = tempfile.TemporaryDirectory(prefix="academy-ops-benchmark-")
        root = Path(managed_tmp.name)
    else:
        root = Path(work_root)
        root.mkdir(parents=True, exist_ok=True)

    accumulators = {
        "duckdb": CandidateAccumulator(name="duckdb"),
        "postgresql": CandidateAccumulator(name="postgresql"),
    }

    try:
        for repetition in range(repetitions):
            order = ("duckdb", "postgresql") if repetition % 2 == 0 else ("postgresql", "duckdb")
            for candidate_name in order:
                if candidate_name == "postgresql" and not postgres_dsn:
                    continue
                candidate: OperationalStoreCandidate | None = None
                try:
                    if candidate_name == "duckdb":
                        candidate = DuckDBOperationalCandidate(root / f"duckdb-r{repetition:02d}")
                    else:
                        candidate = PostgreSQLOperationalCandidate(
                            admin_dsn=str(postgres_dsn),
                            schema=f"academy_ops_bench_r{repetition:02d}",
                            pool_max_size=max(concurrency_levels),
                        )
                    _run_candidate_repetition(
                        candidate=candidate,
                        accumulator=accumulators[candidate_name],
                        repetition=repetition,
                        concurrency_levels=concurrency_levels,
                        operations_per_worker=operations_per_worker,
                    )
                except Exception as exc:
                    accumulators[candidate_name].infrastructure_errors.append(type(exc).__name__)
                finally:
                    if candidate is not None:
                        try:
                            candidate.destroy()
                        except Exception as exc:
                            accumulators[candidate_name].infrastructure_errors.append(
                                f"cleanup:{type(exc).__name__}"
                            )

        duckdb_result = _aggregate_candidate(accumulators["duckdb"])
        postgres_result = (
            None
            if not postgres_dsn
            else _aggregate_candidate(accumulators["postgresql"])
        )
        decision = _decision(
            duckdb_result,
            postgres_result,
            highest_concurrency=max(concurrency_levels),
        )
        return {
            "schema_version": BENCHMARK_SCHEMA_VERSION,
            "decision_id": DECISION_ID,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
            },
            "protocol": {
                "concurrency_levels": list(concurrency_levels),
                "repetitions": repetitions,
                "operations_per_worker": operations_per_worker,
                "candidate_order": "alternating_by_repetition",
                "hard_gate_keys": list(HARD_GATE_KEYS),
                "preregistered_document": "docs/OPERATIONAL-STORE-BENCHMARK-2026-09-03.md",
            },
            "candidates": {
                "duckdb": duckdb_result,
                "postgresql": postgres_result,
            },
            "decision": decision,
        }
    finally:
        if managed_tmp is not None:
            managed_tmp.cleanup()


def _parse_levels(value: str) -> tuple[int, ...]:
    levels = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    if not levels:
        raise argparse.ArgumentTypeError("at least one concurrency level is required")
    if any(level < 1 for level in levels):
        raise argparse.ArgumentTypeError("concurrency levels must be >= 1")
    return levels


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OPS-STORE-001 preregistered benchmark")
    parser.add_argument(
        "--postgres-dsn",
        default=os.environ.get("OPERATIONAL_POSTGRES_DSN"),
        help="Admin PostgreSQL DSN. Prefer OPERATIONAL_POSTGRES_DSN to avoid shell history.",
    )
    parser.add_argument("--profile", choices=("ci", "full"), default="ci")
    parser.add_argument("--concurrency", type=_parse_levels, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--operations-per-worker", type=int)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/operational-store-benchmark.json"),
    )
    parser.add_argument("--work-root", type=Path)
    args = parser.parse_args()

    profile_repetitions = 3 if args.profile == "ci" else 5
    profile_operations = 50 if args.profile == "ci" else 200
    repetitions = profile_repetitions if args.repetitions is None else args.repetitions
    operations = profile_operations if args.operations_per_worker is None else args.operations_per_worker

    result = run_benchmark(
        postgres_dsn=args.postgres_dsn,
        concurrency_levels=args.concurrency,
        repetitions=repetitions,
        operations_per_worker=operations,
        work_root=args.work_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "decision_id": result["decision_id"],
        "decision": result["decision"],
        "artifact": str(args.output),
    }, indent=2, sort_keys=True))

    # A losing candidate is a valid experimental outcome. Fail only if the experiment itself
    # cannot produce a valid comparison when PostgreSQL was requested.
    if args.postgres_dsn:
        for candidate in result["candidates"].values():
            if candidate is not None and not candidate["benchmark_valid"]:
                return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
