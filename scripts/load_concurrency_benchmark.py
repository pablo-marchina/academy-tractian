from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
from threading import Event, Lock, Thread
from time import monotonic, perf_counter, sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from academy_tractian.load_concurrency_benchmark import (
    LoadBenchmarkProtocol,
    LoadPressureObservation,
    LoadRequestObservation,
    analyze_load_benchmark,
)


TOKEN_ENV = "ACADEMY_LOAD_BENCHMARK_BEARER_TOKEN"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a preregistered aggregate-only load benchmark against a serving product API."
    )
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def _validate_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base URL must be an absolute http(s) URL")
    if parsed.query or parsed.fragment:
        raise ValueError("base URL cannot contain query or fragment")
    return value.rstrip("/")


def _http_json(
    *,
    base_url: str,
    token: str,
    method: str,
    path: str,
    body: dict[str, object] | None = None,
    timeout_seconds: float = 10.0,
) -> tuple[int, dict[str, object], float]:
    encoded = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if body is not None:
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{base_url}{path}",
        data=encoded,
        headers=headers,
        method=method,
    )
    started = perf_counter()
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            status = int(response.status)
            raw = response.read()
    except HTTPError as exc:
        status = int(exc.code)
        raw = exc.read()
    elapsed_ms = (perf_counter() - started) * 1000.0
    if not raw:
        return status, {}, elapsed_ms
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("load benchmark endpoint returned non-JSON payload") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("load benchmark endpoint returned non-object JSON")
    return status, payload, elapsed_ms


def _pressure_from_health(
    payload: dict[str, object],
    *,
    level: int,
    elapsed_ms: float,
) -> LoadPressureObservation:
    measured = payload.get("measured")
    if not isinstance(measured, dict):
        raise RuntimeError("production health is missing measured telemetry")
    execution = measured.get("executor_pressure")
    resources = measured.get("resources")
    observability = measured.get("observability")
    if not isinstance(execution, dict) or not isinstance(resources, dict):
        raise RuntimeError("production health is missing executor/resource telemetry")
    persistence_p95 = None
    if isinstance(observability, dict):
        persistence = observability.get("persistence_duration")
        if isinstance(persistence, dict) and persistence.get("p95_ms") is not None:
            persistence_p95 = float(persistence["p95_ms"])
    return LoadPressureObservation(
        concurrency_level=level,
        elapsed_ms=elapsed_ms,
        active_runs=int(execution["active_runs"]),
        queued_runs=int(execution["queued_runs"]),
        inflight_runs=int(execution["inflight_runs"]),
        max_workers=int(execution["max_workers"]),
        executor_utilization=float(execution["executor_utilization"]),
        process_cpu_time_ms=None
        if resources.get("process_cpu_time_ms") is None
        else float(resources["process_cpu_time_ms"]),
        rss_current_bytes=None
        if resources.get("rss_current_bytes") is None
        else int(resources["rss_current_bytes"]),
        rss_max_bytes=None
        if resources.get("rss_max_bytes") is None
        else int(resources["rss_max_bytes"]),
        persistence_p95_ms=persistence_p95,
    )


def _run_one(
    *,
    base_url: str,
    token: str,
    protocol: LoadBenchmarkProtocol,
    level: int,
    request_index: int,
) -> LoadRequestObservation:
    started = perf_counter()
    try:
        status, payload, submit_ms = _http_json(
            base_url=base_url,
            token=token,
            method="POST",
            path="/api/runs",
            body={"user_request": f"Provider-free load benchmark request {level}-{request_index}."},
            timeout_seconds=min(30.0, protocol.completion_timeout_seconds),
        )
    except (OSError, URLError, RuntimeError):
        return LoadRequestObservation(
            concurrency_level=level,
            request_index=request_index,
            submit_status_code=599,
            submit_latency_ms=(perf_counter() - started) * 1000.0,
            terminal_state="submit_rejected",
        )

    if status != 202 or not isinstance(payload.get("run_id"), str):
        return LoadRequestObservation(
            concurrency_level=level,
            request_index=request_index,
            submit_status_code=status,
            submit_latency_ms=submit_ms,
            terminal_state="submit_rejected",
        )

    run_id = str(payload["run_id"])
    deadline = monotonic() + protocol.completion_timeout_seconds
    while monotonic() < deadline:
        try:
            execution_status, execution, _ = _http_json(
                base_url=base_url,
                token=token,
                method="GET",
                path=f"/api/runs/{run_id}/execution",
                timeout_seconds=min(10.0, protocol.completion_timeout_seconds),
            )
        except (OSError, URLError, RuntimeError):
            sleep(0.05)
            continue
        if execution_status == 200:
            terminal = execution.get("status")
            if terminal in {"completed", "failed", "interrupted", "uncertain"}:
                return LoadRequestObservation(
                    concurrency_level=level,
                    request_index=request_index,
                    submit_status_code=202,
                    submit_latency_ms=submit_ms,
                    end_to_end_latency_ms=(perf_counter() - started) * 1000.0,
                    terminal_state=terminal,
                )
        sleep(0.05)

    return LoadRequestObservation(
        concurrency_level=level,
        request_index=request_index,
        submit_status_code=202,
        submit_latency_ms=submit_ms,
        end_to_end_latency_ms=(perf_counter() - started) * 1000.0,
        terminal_state="timeout",
    )


def main() -> int:
    args = _parser().parse_args()
    base_url = _validate_base_url(args.base_url)
    token = os.environ.get(TOKEN_ENV, "")
    if not token:
        raise RuntimeError(f"{TOKEN_ENV} is required")
    protocol = LoadBenchmarkProtocol.model_validate_json(args.protocol.read_text(encoding="utf-8"))

    # Warmups exercise the same endpoint but are never mixed into the measured aggregate.
    for index in range(protocol.warmup_requests):
        _run_one(
            base_url=base_url,
            token=token,
            protocol=protocol,
            level=1,
            request_index=index,
        )

    request_observations: list[LoadRequestObservation] = []
    pressure_observations: list[LoadPressureObservation] = []
    wall_durations: dict[int, float] = {}
    pressure_lock = Lock()

    for level in protocol.concurrency_levels:
        level_started = perf_counter()
        stop_monitor = Event()

        def monitor() -> None:
            while not stop_monitor.is_set():
                try:
                    status, health, _ = _http_json(
                        base_url=base_url,
                        token=token,
                        method="GET",
                        path="/api/production/health",
                        timeout_seconds=5.0,
                    )
                    if status == 200:
                        sample = _pressure_from_health(
                            health,
                            level=level,
                            elapsed_ms=(perf_counter() - level_started) * 1000.0,
                        )
                        with pressure_lock:
                            pressure_observations.append(sample)
                except (OSError, URLError, RuntimeError, KeyError, TypeError, ValueError):
                    pass
                stop_monitor.wait(protocol.pressure_poll_interval_ms / 1000.0)

        monitor_thread = Thread(target=monitor, name=f"load-pressure-{level}", daemon=True)
        monitor_thread.start()
        with ThreadPoolExecutor(max_workers=level) as executor:
            level_observations = tuple(
                executor.map(
                    lambda index: _run_one(
                        base_url=base_url,
                        token=token,
                        protocol=protocol,
                        level=level,
                        request_index=index,
                    ),
                    range(protocol.requests_per_level),
                )
            )
        wall_durations[level] = perf_counter() - level_started
        request_observations.extend(level_observations)
        stop_monitor.set()
        monitor_thread.join(timeout=5)

        # Require one final pressure sample even if the polling interval exceeded a very short run.
        status, health, _ = _http_json(
            base_url=base_url,
            token=token,
            method="GET",
            path="/api/production/health",
            timeout_seconds=5.0,
        )
        if status != 200:
            raise RuntimeError("production health unavailable after load level")
        pressure_observations.append(
            _pressure_from_health(
                health,
                level=level,
                elapsed_ms=(perf_counter() - level_started) * 1000.0,
            )
        )

    report = analyze_load_benchmark(
        protocol,
        requests=tuple(request_observations),
        pressure=tuple(pressure_observations),
        wall_duration_seconds=wall_durations,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
