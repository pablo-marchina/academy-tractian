#!/usr/bin/env python3
"""Provider-free BIG-B2 benchmark-design geometry analysis.

Reads only frozen PUBLIC split metadata. It never loads evaluator gold, expected
paths, fixed model outputs, VALIDATION feedback, or LOCKED_TEST semantic labels.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


def wilson(k: int, n: int, z: float = 1.959963984540054) -> list[float]:
    p = k / n
    den = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / den
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / den
    return [center - half, center + half]


def canonical_partition(parts: Iterable[Iterable[str]]) -> tuple[tuple[str, ...], ...]:
    return tuple(sorted(tuple(sorted(part)) for part in parts))


def balanced_two_fold(groups: list[str]) -> list[tuple[tuple[str, ...], ...]]:
    # With seven groups, enumerate unique 3/4 partitions.
    universe = set(groups)
    seen: set[tuple[tuple[str, ...], ...]] = set()
    for left in itertools.combinations(groups, 3):
        right = universe - set(left)
        seen.add(canonical_partition([left, right]))
    return sorted(seen)


def balanced_three_fold(groups: list[str]) -> list[tuple[tuple[str, ...], ...]]:
    # With seven groups, enumerate unique 3/2/2 partitions.
    universe = set(groups)
    seen: set[tuple[tuple[str, ...], ...]] = set()
    for first in itertools.combinations(groups, 3):
        remaining = universe - set(first)
        for second in itertools.combinations(sorted(remaining), 2):
            third = remaining - set(second)
            seen.add(canonical_partition([first, second, third]))
    return sorted(seen)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-manifest",
        default="research/frozen/benchmark-split-v1.json",
        help="Frozen public benchmark split manifest",
    )
    parser.add_argument("--out", help="Optional JSON output path")
    args = parser.parse_args()

    manifest = json.loads(Path(args.split_manifest).read_text(encoding="utf-8"))
    split = manifest["splits"]
    exposed_rows = split["DEV"]["groups"] + split["VALIDATION"]["groups"]
    locked_rows = split["LOCKED_TEST"]["groups"]

    by_group = {row["group_id"]: row for row in exposed_rows}
    groups = sorted(by_group)
    contextualize = {
        gid for gid, row in by_group.items() if "contextualize" in row["modalities"]
    }

    def scenario_count(fold: Iterable[str]) -> int:
        return sum(len(by_group[g]["scenarios"]) for g in fold)

    two = balanced_two_fold(groups)
    two_ctx_both = 0
    two_scenario_imbalances: list[int] = []
    for part in two:
        ctx_test = [bool(set(fold) & contextualize) for fold in part]
        # In a two-fold design the complementary fold is the train fold.
        if all(ctx_test):
            two_ctx_both += 1
        counts = [scenario_count(fold) for fold in part]
        two_scenario_imbalances.append(max(counts) - min(counts))

    three = balanced_three_fold(groups)
    three_train_ctx_all = 0
    three_test_ctx_all = 0
    best_three_imbalance = None
    best_three_counts: list[int] | None = None
    for part in three:
        folds = [set(fold) for fold in part]
        train_ctx = [bool((set(groups) - fold) & contextualize) for fold in folds]
        test_ctx = [bool(fold & contextualize) for fold in folds]
        if all(train_ctx):
            three_train_ctx_all += 1
        if all(test_ctx):
            three_test_ctx_all += 1
        counts = [scenario_count(fold) for fold in folds]
        imbalance = max(counts) - min(counts)
        if best_three_imbalance is None or imbalance < best_three_imbalance:
            best_three_imbalance = imbalance
            best_three_counts = sorted(counts)

    logo_test_ctx = sum(1 for g in groups if g in contextualize)
    logo_train_ctx = sum(1 for g in groups if contextualize - {g})

    leave_two = list(itertools.combinations(groups, 2))
    l2_test_ctx = sum(1 for pair in leave_two if set(pair) & contextualize)
    l2_train_ctx = sum(1 for pair in leave_two if contextualize - set(pair))

    locked_contextualize = [
        row["group_id"] for row in locked_rows if "contextualize" in row["modalities"]
    ]

    output = {
        "schema_version": "big-b2-public-benchmark-geometry-v1",
        "source": args.split_manifest,
        "privacy_boundary": "PUBLIC_SPLIT_METADATA_ONLY",
        "exposed_pool": {
            "groups": len(exposed_rows),
            "scenarios": sum(len(r["scenarios"]) for r in exposed_rows),
            "tickets": sum(len(r["tickets"]) for r in exposed_rows),
            "contextualize_groups": sorted(contextualize),
            "contextualize_group_count": len(contextualize),
        },
        "balanced_2fold": {
            "unique_partitions": len(two),
            "partitions_with_contextualize_in_both_test_folds": two_ctx_both,
            "fraction_with_contextualize_in_both_test_folds": two_ctx_both / len(two),
            "minimum_scenario_count_imbalance": min(two_scenario_imbalances),
        },
        "balanced_3fold": {
            "unique_partitions": len(three),
            "partitions_with_contextualize_in_every_training_fold": three_train_ctx_all,
            "fraction_with_contextualize_in_every_training_fold": three_train_ctx_all / len(three),
            "partitions_with_contextualize_in_every_test_fold": three_test_ctx_all,
            "minimum_scenario_count_imbalance": best_three_imbalance,
            "best_test_scenario_counts": best_three_counts,
        },
        "leave_one_group_out": {
            "folds": len(groups),
            "training_folds_with_contextualize": logo_train_ctx,
            "test_folds_with_contextualize": logo_test_ctx,
        },
        "leave_two_groups_out": {
            "folds": len(leave_two),
            "training_folds_with_contextualize": l2_train_ctx,
            "test_folds_with_contextualize": l2_test_ctx,
        },
        "legacy_locked_test": {
            "groups": len(locked_rows),
            "scenarios": sum(len(r["scenarios"]) for r in locked_rows),
            "tickets": sum(len(r["tickets"]) for r in locked_rows),
            "contextualize_groups": locked_contextualize,
            "contextualize_group_count": len(locked_contextualize),
        },
        "illustrative_group_pass_wilson_95": {
            str(n): {
                "all_pass": wilson(n, n),
                "near_half": wilson(round(n / 2), n),
            }
            for n in (2, 3, 5, 7)
        },
        "warnings": [
            "Wilson intervals are illustrative only; group outcomes need not be IID Bernoulli.",
            "Cross-validation over historically exposed groups does not restore blind independence.",
            "Naive standard deviation across overlapping CV folds must not be treated as an unbiased uncertainty estimator.",
        ],
    }

    rendered = json.dumps(output, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
