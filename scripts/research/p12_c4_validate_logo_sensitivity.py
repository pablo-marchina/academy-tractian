#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

EXPECTED_SCORE_SHA256 = "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c"
EXPECTED_BOOTSTRAP_SHA256 = "08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526"
EXPECTED_HISTORICAL_SCORER_SHA256 = "f3500751448c3b52bf361f4d565ba940c8e9e62e8ab197bb1206fdb7d89a7d22"
EXPECTED_ARMS = ["A00", "A10", "A01", "A11"]
EXPECTED_ROWS = 144
EXPECTED_PARENTS = 36
EXPECTED_GROUPS = 7


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--bootstrap-result", type=Path, required=True)
    ap.add_argument("--logo-result", type=Path, required=True)
    ap.add_argument("--historical-scorer", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    mismatches: list[str] = []
    if sha256(args.scores) != EXPECTED_SCORE_SHA256:
        mismatches.append("score_sha256")
    if sha256(args.bootstrap_result) != EXPECTED_BOOTSTRAP_SHA256:
        mismatches.append("bootstrap_sha256")
    if sha256(args.historical_scorer) != EXPECTED_HISTORICAL_SCORER_SHA256:
        mismatches.append("historical_scorer_sha256")

    spec = importlib.util.spec_from_file_location("frozen_c2", args.historical_scorer)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen historical scorer")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    scores = load(args.scores)
    result = load(args.logo_result)
    rows = scores.get("rows") or []
    if len(rows) != EXPECTED_ROWS:
        mismatches.append("row_count")
    by_arm = {arm: [r for r in rows if r.get("arm") == arm] for arm in EXPECTED_ARMS}
    if any(len(v) != EXPECTED_PARENTS for v in by_arm.values()):
        mismatches.append("arm_geometry")

    arm_groups = {}
    for arm in EXPECTED_ARMS:
        _metrics, groups = mod.full_metrics(by_arm[arm])
        arm_groups[arm] = groups
    group_ids = sorted(arm_groups["A00"]["evidence_correctness"])
    if len(group_ids) != EXPECTED_GROUPS:
        mismatches.append("group_count")

    expected_logo = mod.logo_effects(arm_groups, group_ids)
    if result.get("leave_one_group_out_primary_contrasts") != expected_logo:
        mismatches.append("logo_effects")
    if (result.get("input") or {}).get("group_ids") != group_ids:
        mismatches.append("group_ids")
    protocol = result.get("protocol") or {}
    if protocol.get("retained_groups_per_estimate") != 6 or protocol.get("estimates_per_primary_comparison") != 7:
        mismatches.append("logo_geometry")

    boundaries = result.get("execution_boundaries") or {}
    for key in ("provider_calls", "model_calls", "network_io", "fresh_blind_accesses", "legacy_locked_test_accesses"):
        if int(boundaries.get(key) or 0) != 0:
            mismatches.append(f"boundary_{key}")
    for key in ("private_oracle_loaded", "scores_recomputed_or_changed", "candidate_regeneration", "slice_analysis_executed", "semantic_stage_executed", "survivor_decision_executed"):
        if boundaries.get(key) is not False:
            mismatches.append(f"boundary_{key}")

    validation = {
        "schema_version": "p12-c4-logo-sensitivity-validation-v1",
        "status": "PASS_INDEPENDENT_LOGO_RECOMPUTATION" if not mismatches else "FAIL_LOGO_RECOMPUTATION_MISMATCH",
        "deterministic_score_rows_sha256": EXPECTED_SCORE_SHA256,
        "bootstrap_result_sha256": EXPECTED_BOOTSTRAP_SHA256,
        "logo_result_sha256": sha256(args.logo_result),
        "historical_factorial_scorer_sha256": EXPECTED_HISTORICAL_SCORER_SHA256,
        "rows_reused_without_rescoring": EXPECTED_ROWS,
        "arms": EXPECTED_ARMS,
        "rows_per_arm": EXPECTED_PARENTS,
        "independent_groups": EXPECTED_GROUPS,
        "omitted_group_estimates_per_comparison": 7,
        "retained_groups_per_estimate": 6,
        "historical_logo_effects_exact_match": "logo_effects" not in mismatches,
        "mismatch_sections": mismatches,
        "provider_calls": 0,
        "private_oracle_loaded": False,
        "slice_analysis_executed": False,
        "semantic_stage_executed": False,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "survivor_decision_executed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "mismatch_sections": mismatches, "logo_result_sha256": validation["logo_result_sha256"]}, indent=2))
    return 0 if not mismatches else 2


if __name__ == "__main__":
    raise SystemExit(main())
