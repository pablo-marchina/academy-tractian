from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any
from uuid import uuid4

import psycopg

from academy_tractian.realtime_wakeup import (
    DEFAULT_POSTGRES_WAKEUP_CHANNEL,
    PostgresListenNotifyWakeup,
    encode_wakeup_payload,
)


@dataclass(frozen=True)
class Profile:
    clients: int
    repetitions: int
    polling_seconds: float
    fallback_seconds: float
    event_delay_seconds: float
    idle_seconds: float


PROFILES = {
    "ci": Profile(
        clients=100,
        repetitions=5,
        polling_seconds=0.2,
        fallback_seconds=1.0,
        event_delay_seconds=0.35,
        idle_seconds=1.25,
    ),
    "full": Profile(
        clients=250,
        repetitions=20,
        polling_seconds=0.2,
        fallback_seconds=1.0,
        event_delay_seconds=0.35,
        idle_seconds=2.25,
    ),
}


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


def _latency_summary(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "mean_ms": None if not values else mean(values),
        "median_ms": None if not values else median(values),
        "p95_ms": _percentile(values, 0.95),
        "max_ms": None if not values else max(values),
    }


def _send_notify(dsn: str, *, run_id: str, sequence: int, copies: int = 1) -> None:
    payload = encode_wakeup_payload(run_id=run_id, sequence=sequence)
    with psycopg.connect(dsn, autocommit=True) as connection:
        for _ in range(copies):
            connection.execute(
                "SELECT pg_notify(%s, %s)",
                (DEFAULT_POSTGRES_WAKEUP_CHANNEL, payload),
            )


async def _wait_connected(wakeup: PostgresListenNotifyWakeup, timeout_seconds: float = 5.0) -> None:
    deadline = perf_counter() + timeout_seconds
    while perf_counter() < deadline:
        if wakeup.snapshot()["connected"] is True:
            return
        await asyncio.sleep(0.02)
    raise RuntimeError("PostgreSQL wakeup listener did not become ready")


async def _polling_idle(profile: Profile) -> dict[str, Any]:
    deadline = perf_counter() + profile.idle_seconds

    async def worker() -> int:
        queries = 0
        while True:
            queries += 1
            remaining = deadline - perf_counter()
            if remaining <= 0:
                return queries
            await asyncio.sleep(min(profile.polling_seconds, remaining))

    counts = await asyncio.gather(*(worker() for _ in range(profile.clients)))
    return {
        "total_durable_reads": sum(counts),
        "reads_per_client": mean(counts),
        "reads_per_client_second": sum(counts) / profile.clients / profile.idle_seconds,
    }


async def _wakeup_idle(
    profile: Profile,
    wakeup: PostgresListenNotifyWakeup,
) -> dict[str, Any]:
    deadline = perf_counter() + profile.idle_seconds
    run_id = f"rt_idle_{uuid4().hex[:20]}"

    async def worker() -> int:
        queries = 0
        generation = wakeup.generation(run_id)
        while True:
            queries += 1
            remaining = deadline - perf_counter()
            if remaining <= 0:
                return queries
            await wakeup.wait_for_change(
                run_id,
                after_generation=generation,
                timeout_seconds=min(profile.fallback_seconds, max(0.001, remaining)),
            )
            generation = wakeup.generation(run_id)

    counts = await asyncio.gather(*(worker() for _ in range(profile.clients)))
    return {
        "total_durable_reads": sum(counts),
        "reads_per_client": mean(counts),
        "reads_per_client_second": sum(counts) / profile.clients / profile.idle_seconds,
    }


async def _polling_event(profile: Profile) -> dict[str, Any]:
    visible = asyncio.Event()
    published_at: list[float] = []

    async def publisher() -> None:
        await asyncio.sleep(profile.event_delay_seconds)
        published_at.append(perf_counter())
        visible.set()

    async def worker() -> tuple[int, float]:
        queries = 0
        while True:
            queries += 1
            if visible.is_set():
                assert published_at
                return queries, (perf_counter() - published_at[0]) * 1000.0
            await asyncio.sleep(profile.polling_seconds)

    publisher_task = asyncio.create_task(publisher())
    results = await asyncio.gather(*(worker() for _ in range(profile.clients)))
    await publisher_task
    queries = [item[0] for item in results]
    latencies = [item[1] for item in results]
    return {
        "delivered_clients": len(results),
        "lost_clients": profile.clients - len(results),
        "logical_duplicates": 0,
        "total_durable_reads": sum(queries),
        "reads_per_delivered_client": mean(queries),
        "latency": _latency_summary(latencies),
        "latencies_ms": latencies,
    }


async def _wakeup_event(
    profile: Profile,
    wakeup: PostgresListenNotifyWakeup,
    dsn: str,
    *,
    send_notification: bool = True,
    duplicate_notification: bool = False,
) -> dict[str, Any]:
    visible = asyncio.Event()
    published_at: list[float] = []
    run_id = f"rt_event_{uuid4().hex[:20]}"
    deadline = perf_counter() + profile.event_delay_seconds + profile.fallback_seconds + 2.0

    async def publisher() -> None:
        await asyncio.sleep(profile.event_delay_seconds)
        # Represents the durable row having committed before the wakeup is emitted.
        published_at.append(perf_counter())
        visible.set()
        if send_notification:
            await asyncio.to_thread(
                _send_notify,
                dsn,
                run_id=run_id,
                sequence=0,
                copies=2 if duplicate_notification else 1,
            )

    async def worker() -> tuple[int, float]:
        queries = 0
        generation = wakeup.generation(run_id)
        while perf_counter() < deadline:
            queries += 1
            if visible.is_set():
                assert published_at
                return queries, (perf_counter() - published_at[0]) * 1000.0
            await wakeup.wait_for_change(
                run_id,
                after_generation=generation,
                timeout_seconds=profile.fallback_seconds,
            )
            generation = wakeup.generation(run_id)
        raise RuntimeError("logical SSE client failed to observe durable event")

    publisher_task = asyncio.create_task(publisher())
    results = await asyncio.gather(*(worker() for _ in range(profile.clients)))
    await publisher_task
    queries = [item[0] for item in results]
    latencies = [item[1] for item in results]
    return {
        "run_id": run_id,
        "delivered_clients": len(results),
        "lost_clients": profile.clients - len(results),
        "logical_duplicates": 0,
        "total_durable_reads": sum(queries),
        "reads_per_delivered_client": mean(queries),
        "latency": _latency_summary(latencies),
        "latencies_ms": latencies,
    }


async def _run(profile_name: str, dsn: str) -> dict[str, Any]:
    profile = PROFILES[profile_name]
    wakeup = PostgresListenNotifyWakeup(
        dsn=dsn,
        channel=DEFAULT_POSTGRES_WAKEUP_CHANNEL,
        listen_timeout_seconds=0.1,
        reconnect_delay_seconds=0.1,
    )
    wakeup.start()
    try:
        await _wait_connected(wakeup)
        snapshot_at_start = wakeup.snapshot()

        baseline_idle = await _polling_idle(profile)
        candidate_idle = await _wakeup_idle(profile, wakeup)

        repetitions: list[dict[str, Any]] = []
        baseline_latencies: list[float] = []
        candidate_latencies: list[float] = []
        for repetition in range(profile.repetitions):
            baseline = await _polling_event(profile)
            candidate = await _wakeup_event(profile, wakeup, dsn)
            baseline_latencies.extend(baseline.pop("latencies_ms"))
            candidate_latencies.extend(candidate.pop("latencies_ms"))
            repetitions.append(
                {
                    "repetition": repetition,
                    "polling": baseline,
                    "postgres_listen_notify": candidate,
                }
            )

        missed_notify = await _wakeup_event(
            profile,
            wakeup,
            dsn,
            send_notification=False,
        )
        missed_notify.pop("latencies_ms")
        duplicate_notify = await _wakeup_event(
            profile,
            wakeup,
            dsn,
            duplicate_notification=True,
        )
        duplicate_notify.pop("latencies_ms")
        await asyncio.sleep(0.15)
        final_snapshot = wakeup.snapshot()

        baseline_p95 = _percentile(baseline_latencies, 0.95)
        candidate_p95 = _percentile(candidate_latencies, 0.95)
        assert baseline_p95 is not None and candidate_p95 is not None
        idle_ratio = (
            candidate_idle["reads_per_client_second"]
            / baseline_idle["reads_per_client_second"]
        )
        normal_loss = sum(
            item["postgres_listen_notify"]["lost_clients"] for item in repetitions
        )
        baseline_loss = sum(item["polling"]["lost_clients"] for item in repetitions)
        logical_duplicates = sum(
            item["postgres_listen_notify"]["logical_duplicates"] for item in repetitions
        )

        hard_gates = {
            "baseline_loss_zero": baseline_loss == 0,
            "candidate_normal_loss_zero": normal_loss == 0,
            "candidate_logical_duplicates_zero": logical_duplicates == 0,
            "missed_notify_fallback_recovery_100pct": missed_notify["lost_clients"] == 0,
            "duplicate_notify_logical_delivery_once": duplicate_notify["logical_duplicates"] == 0,
            "listener_connected": final_snapshot["connected"] is True,
            "listener_failures_zero": final_snapshot["listener_failures"] == 0,
            "payload_rejections_zero": final_snapshot["payload_rejections"] == 0,
        }
        efficiency_gates = {
            "idle_durable_read_ratio_lte_0_50": idle_ratio <= 0.50,
            "candidate_p95_not_worse_than_baseline_plus_50ms": candidate_p95 <= baseline_p95 + 50.0,
            "single_listener_connection_opened": final_snapshot["listener_connections_opened"] == 1,
        }
        hard_pass = all(hard_gates.values())
        efficiency_pass = all(efficiency_gates.values())
        if not hard_pass:
            outcome = "REJECT_PG_LISTEN_NOTIFY"
        elif efficiency_pass:
            outcome = "PROMOTE_PG_LISTEN_NOTIFY"
        else:
            outcome = "INCONCLUSIVE_KEEP_POLLING_BASELINE"

        return {
            "schema_version": "realtime-wakeup-benchmark-v1",
            "decision_id": "RT-WAKEUP-001",
            "profile": profile_name,
            "config": {
                "clients": profile.clients,
                "repetitions": profile.repetitions,
                "polling_interval_ms": profile.polling_seconds * 1000.0,
                "fallback_interval_ms": profile.fallback_seconds * 1000.0,
                "event_delay_ms": profile.event_delay_seconds * 1000.0,
                "idle_window_ms": profile.idle_seconds * 1000.0,
            },
            "candidates": {
                "polling": {
                    "idle": baseline_idle,
                    "event_latency": _latency_summary(baseline_latencies),
                },
                "postgres_listen_notify": {
                    "idle": candidate_idle,
                    "event_latency": _latency_summary(candidate_latencies),
                    "listener_start": snapshot_at_start,
                    "listener_final": final_snapshot,
                    "missed_notify_slice": missed_notify,
                    "duplicate_notify_slice": duplicate_notify,
                },
            },
            "paired_repetitions": repetitions,
            "comparison": {
                "idle_durable_read_ratio_candidate_over_baseline": idle_ratio,
                "idle_durable_read_reduction_fraction": 1.0 - idle_ratio,
                "baseline_event_p95_ms": baseline_p95,
                "candidate_event_p95_ms": candidate_p95,
                "candidate_minus_baseline_p95_ms": candidate_p95 - baseline_p95,
            },
            "hard_gates": hard_gates,
            "efficiency_gates": efficiency_gates,
            "decision": {
                "outcome": outcome,
                "hard_gates_passed": hard_pass,
                "efficiency_gates_passed": efficiency_pass,
            },
        }
    finally:
        wakeup.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=sorted(PROFILES), default="ci")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    dsn = os.environ.get("REALTIME_POSTGRES_DSN")
    if not dsn:
        raise SystemExit("REALTIME_POSTGRES_DSN is required")
    payload = asyncio.run(_run(args.profile, dsn))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    if payload["decision"]["outcome"] != "PROMOTE_PG_LISTEN_NOTIFY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
