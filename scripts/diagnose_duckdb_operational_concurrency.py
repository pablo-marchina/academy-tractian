from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import platform
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Callable

from academy_tractian.run_access import DuckDBRunAccessStore
from academy_tractian.run_execution_store import DuckDBRunExecutionStore


def signature(exc: Exception) -> str:
    message = " ".join(str(exc).split())
    if len(message) > 300:
        message = message[:297] + "..."
    return f"{type(exc).__name__}: {message or '<empty>'}"


def exercise(
    *,
    access: DuckDBRunAccessStore,
    execution: DuckDBRunExecutionStore,
    concurrency: int,
    operations_per_worker: int,
) -> dict[str, object]:
    errors: Counter[str] = Counter()
    stages: Counter[str] = Counter()
    successes = 0

    def invoke(stage: str, call: Callable[[], object]) -> object:
        try:
            return call()
        except Exception as exc:
            stages[stage] += 1
            errors[signature(exc)] += 1
            raise

    def worker(worker_index: int) -> int:
        local_success = 0
        org = f"org-{worker_index % 3}"
        user = f"user-{worker_index}"
        for operation_index in range(operations_per_worker):
            run_id = f"diag-c{concurrency}-w{worker_index}-o{operation_index}"
            try:
                invoke(
                    "access.claim",
                    lambda: access.claim(
                        run_id=run_id,
                        organization_id=org,
                        user_id=user,
                    ),
                )
                invoke(
                    "execution.create_accepted",
                    lambda: execution.create_accepted(run_id=run_id),
                )
                started = invoke(
                    "execution.accepted_to_running",
                    lambda: execution.transition(
                        run_id=run_id,
                        expected_states=frozenset({"accepted"}),
                        new_state="running",
                    ),
                )
                if started is not True:
                    raise RuntimeError("accepted_to_running_returned_false")
                owner = invoke("access.get", lambda: access.get(run_id))
                if owner is None or owner.organization_id != org or owner.user_id != user:
                    raise RuntimeError("ownership_mismatch")
                completed = invoke(
                    "execution.running_to_completed",
                    lambda: execution.transition(
                        run_id=run_id,
                        expected_states=frozenset({"running"}),
                        new_state="completed",
                    ),
                )
                if completed is not True:
                    raise RuntimeError("running_to_completed_returned_false")
                item = invoke("execution.get", lambda: execution.get(run_id))
                if item is None or item.state != "completed":
                    raise RuntimeError("terminal_state_mismatch")
                local_success += 1
            except Exception:
                continue
        return local_success

    started = perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for value in pool.map(worker, range(concurrency)):
            successes += value
    wall = perf_counter() - started
    attempts = concurrency * operations_per_worker
    return {
        "concurrency": concurrency,
        "operations_per_worker": operations_per_worker,
        "attempts": attempts,
        "successes": successes,
        "errors": attempts - successes,
        "error_rate": round((attempts - successes) / attempts, 8),
        "wall_seconds": round(wall, 6),
        "success_throughput_per_second": round(successes / wall, 6) if wall else 0.0,
        "error_stages": dict(stages.most_common()),
        "error_signatures": dict(errors.most_common(20)),
    }


def run(*, root: Path, operations_per_worker: int) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=True)
    access = DuckDBRunAccessStore(root / "run-access.duckdb")
    execution = DuckDBRunExecutionStore(root / "run-execution.duckdb")
    results = [
        exercise(
            access=access,
            execution=execution,
            concurrency=concurrency,
            operations_per_worker=operations_per_worker,
        )
        for concurrency in (1, 5, 10, 25)
    ]
    return {
        "schema_version": "duckdb-operational-concurrency-diagnostic-v1",
        "production_store_classes": [
            "academy_tractian.run_access.DuckDBRunAccessStore",
            "academy_tractian.run_execution_store.DuckDBRunExecutionStore",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operations-per-worker", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("artifacts/duckdb-operational-diagnostic.json"))
    parser.add_argument("--work-root", type=Path)
    args = parser.parse_args()

    if args.work_root is None:
        temp = TemporaryDirectory(prefix="academy-duckdb-diagnostic-")
        root = Path(temp.name)
    else:
        temp = None
        root = args.work_root
    try:
        result = run(root=root, operations_per_worker=args.operations_per_worker)
    finally:
        if temp is not None:
            temp.cleanup()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
