#!/usr/bin/env python3
"""Prove P12-C4 common-parent seeds do not reuse repository-visible P12-C1/C2/C3 seeds.

Provider-free by construction: this script reads only versioned JSON artifacts.
It intentionally scans the full predecessor P12 artifact surface rather than one
hand-picked manifest so a seed copied into an execution/result/frozen artifact is
still detected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SEED_MAP = Path("research/frozen/p12-c4-fresh-seed-map-v1.json")
PREDECESSOR_ROOTS = (Path("research/experiments"), Path("research/frozen"), Path("research/results"))
PREDECESSOR_PREFIXES = ("p12-c1-", "p12-c2-", "p12-c3-")
DERIVATION_NAMESPACE = "academy-tractian:P12-C4:common-parent-seed:v1"


class CheckFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def predecessor_files() -> list[Path]:
    paths: list[Path] = []
    for root in PREDECESSOR_ROOTS:
        if not root.exists():
            continue
        for path in root.glob("p12-c[123]-*.json"):
            if path.is_file() and path.name.startswith(PREDECESSOR_PREFIXES):
                paths.append(path)
    paths = sorted(set(paths))
    require(paths, "no P12-C1/C2/C3 predecessor JSON artifacts found")
    return paths


def ints_below(value: Any) -> Iterable[int]:
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from ints_below(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from ints_below(nested)


def collect_seed_values(value: Any, *, inherited_seed_context: bool = False) -> set[int]:
    """Collect integers under keys whose names carry seed semantics.

    Once a seed-bearing key is encountered, integer descendants are included so
    structures such as ``seeds: [{...}]`` are covered. This is intentionally
    conservative; extra non-seed integers can only create false-positive blocks,
    never allow reuse.
    """
    found: set[int] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            seed_context = inherited_seed_context or ("seed" in str(key).lower())
            if seed_context:
                found.update(ints_below(nested))
            else:
                found.update(collect_seed_values(nested, inherited_seed_context=False))
    elif isinstance(value, list):
        for nested in value:
            found.update(collect_seed_values(nested, inherited_seed_context=inherited_seed_context))
    elif inherited_seed_context and isinstance(value, int) and not isinstance(value, bool):
        found.add(value)
    return found


def expected_seed(ordinal: int) -> int:
    payload = f"{DERIVATION_NAMESPACE}:{ordinal:02d}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big") & 0x7FFFFFFF


def validate_seed_map(seed_map: dict[str, Any]) -> list[int]:
    require(seed_map.get("schema_version") == "p12-c4-fresh-seed-map-v1", "seed-map schema mismatch")
    require(seed_map.get("experiment_id") == "P12-C4-PROSPECTIVE-EXPOSED-POOL", "experiment id mismatch")
    require(seed_map.get("status") == "FROZEN_PROVIDER_FREE_SEED_PLAN", "seed map must remain provider-free and frozen")
    derivation = seed_map.get("derivation", {})
    require(derivation.get("namespace") == DERIVATION_NAMESPACE, "seed namespace mismatch")
    require(derivation.get("algorithm") == "sha256_namespace_first_u32_mask_31bit", "seed derivation algorithm mismatch")
    require(derivation.get("selection_after_outcome_access") is False, "seed selection must be prospective")
    require(derivation.get("benchmark_inputs_used") is False, "benchmark inputs cannot inform seed selection")
    require(derivation.get("provider_outputs_used") is False, "provider outputs cannot inform seed selection")

    rows = seed_map.get("common_parents")
    require(isinstance(rows, list) and len(rows) == 36, "exactly 36 common-parent seed rows are required")
    seeds: list[int] = []
    for ordinal, row in enumerate(rows, start=1):
        require(isinstance(row, dict), f"row {ordinal} must be an object")
        require(row.get("ordinal") == ordinal, f"row {ordinal} ordinal mismatch")
        require(row.get("parent_id") == f"P{ordinal:02d}", f"row {ordinal} parent id mismatch")
        seed = row.get("seed")
        require(isinstance(seed, int) and not isinstance(seed, bool) and 0 <= seed <= 0x7FFFFFFF, f"row {ordinal} seed invalid")
        require(seed == expected_seed(ordinal), f"row {ordinal} does not match frozen deterministic derivation")
        seeds.append(seed)
    require(len(set(seeds)) == 36, "P12-C4 contains duplicate seeds")

    invariants = seed_map.get("invariants", {})
    require(invariants.get("common_parent_count") == 36, "seed-map common-parent invariant mismatch")
    require(invariants.get("all_seeds_unique_within_c4") is True, "within-C4 uniqueness invariant missing")
    require(invariants.get("no_seed_reuse_from_p12_c1_c2_c3_required") is True, "predecessor isolation invariant missing")
    require(invariants.get("partial_parent_reuse_forbidden") is True, "partial-parent reuse must remain forbidden")
    require(invariants.get("arm_specific_seed_variation_forbidden") is True, "arm-specific seed variation must remain forbidden")
    require(invariants.get("same_common_parent_seed_for_all_four_arms") is True, "paired-parent seed invariant missing")

    authorization = seed_map.get("authorization", {})
    require(authorization == {"provider_calls": False, "exposed_pool_generation": False, "private_scoring": False}, "seed map must not authorize live work")
    return seeds


def run(seed_map_path: Path) -> dict[str, Any]:
    seed_map = load_json(seed_map_path)
    require(isinstance(seed_map, dict), "seed map must contain an object")
    c4_seeds = set(validate_seed_map(seed_map))

    scanned: list[str] = []
    predecessor_seed_values: set[int] = set()
    per_file_counts: dict[str, int] = {}
    for path in predecessor_files():
        value = load_json(path)
        seeds = collect_seed_values(value)
        scanned.append(path.as_posix())
        per_file_counts[path.as_posix()] = len(seeds)
        predecessor_seed_values.update(seeds)

    collisions = sorted(c4_seeds & predecessor_seed_values)
    require(not collisions, f"P12-C4 reuses predecessor seed values: {collisions}")

    return {
        "schema_version": "p12-c4-seed-isolation-self-check-v1",
        "status": "PASS",
        "provider_calls": 0,
        "credentials_read": 0,
        "benchmark_outcomes_read": 0,
        "c4_seed_count": len(c4_seeds),
        "c4_seed_unique_count": len(c4_seeds),
        "predecessor_artifact_count": len(scanned),
        "predecessor_seed_value_count": len(predecessor_seed_values),
        "seed_collisions": [],
        "derivation_recomputed": True,
        "scanned_predecessor_artifacts": scanned,
        "seed_value_counts_by_artifact": per_file_counts,
        "live_generation_authorized": False,
        "next_gate": "VERIFY_ACCOUNT_LIMITS_AND_PREREGISTER_SYNTHETIC_LIVE_COMPATIBILITY_PROBE"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-map", type=Path, default=DEFAULT_SEED_MAP)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run(args.seed_map)
        code = 0
    except (CheckFailure, json.JSONDecodeError, OSError, KeyError) as exc:
        result = {
            "schema_version": "p12-c4-seed-isolation-self-check-v1",
            "status": "FAIL",
            "provider_calls": 0,
            "credentials_read": 0,
            "benchmark_outcomes_read": 0,
            "error": str(exc)
        }
        code = 1
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
