#!/usr/bin/env python3
from __future__ import annotations

"""Independent C4 BOOTSTRAP_20000 validation against frozen C2 helpers.

This validator does not import the new bootstrap runner. It recomputes the
bootstrap quantities through the exact frozen historical C2 statistical helper
implementation and compares the resulting sections at the JSON object level.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

EXPECTED_INPUT_SHA256 = "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c"
EXPECTED_HISTORICAL_SCORER_SHA256 = "f3500751448c3b52bf361f4d565ba940c8e9e62e8ab197bb1206fdb7d89a7d22"
EXPECTED_RESULT_STATUS = "PASS_C4_BOOTSTRAP_20000_COMPLETE"
EXPECTED_ARMS = ["A00", "A10", "A01", "A11"]
EXPECTED_ROWS = 144
EXPECTED_PARENTS = 36
EXPECTED_GROUPS = 7
EXPECTED_BOOTSTRAP_N = 20000
EXPECTED_SEED = 20260822

PROVIDER_CREDENTIAL_ENVS = (
    "NVIDIA_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "CEREBRAS_API_KEY", "OPENROUTER_API_KEY",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_historical_scorer(path: Path):
    if sha256(path) != EXPECTED_HISTORICAL_SCORER_SHA256:
        raise AssertionError("historical C2 scorer bytes changed")
    root = path.resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location("p12_c4_bootstrap_historical_reference", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import historical C2 scorer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score-rows", type=Path, required=True)
    parser.add_argument("--bootstrap-result", type=Path, required=True)
    parser.add_argument("--historical-scorer", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    present = sorted(name for name in PROVIDER_CREDENTIAL_ENVS if os.getenv(name))
    if present:
        raise AssertionError(f"provider credentials present during validation: {present}")
    if sha256(args.score_rows) != EXPECTED_INPUT_SHA256:
        raise AssertionError("frozen deterministic score-row input hash mismatch")

    score_payload = load_json(args.score_rows)
    result = load_json(args.bootstrap_result)
    rows = score_payload.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROWS:
        raise AssertionError("expected 144 deterministic rows")
    if result.get("status") != EXPECTED_RESULT_STATUS:
        raise AssertionError("bootstrap result status mismatch")
    if result.get("input", {}).get("deterministic_score_rows_sha256") != EXPECTED_INPUT_SHA256:
        raise AssertionError("bootstrap result points to wrong deterministic input")
    if int(result.get("bootstrap", {}).get("resamples") or 0) != EXPECTED_BOOTSTRAP_N:
        raise AssertionError("bootstrap resample count changed")
    if int(result.get("bootstrap", {}).get("seed") or 0) != EXPECTED_SEED:
        raise AssertionError("bootstrap seed changed")
    if result.get("bootstrap", {}).get("resampling_unit") != "asset_story_group":
        raise AssertionError("bootstrap resampling unit changed")

    historical = load_historical_scorer(args.historical_scorer)
    if historical.BOOTSTRAP_N != EXPECTED_BOOTSTRAP_N or historical.BOOTSTRAP_SEED != EXPECTED_SEED:
        raise AssertionError("historical C2 bootstrap constants changed")
    if historical.EXPECTED_ARMS != EXPECTED_ARMS:
        raise AssertionError("historical factorial arm set changed")

    by_arm = {arm: [row for row in rows if row.get("arm") == arm] for arm in EXPECTED_ARMS}
    if any(len(by_arm[arm]) != EXPECTED_PARENTS for arm in EXPECTED_ARMS):
        raise AssertionError("expected 36 rows per arm")

    arm_metrics: dict[str, dict[str, float]] = {}
    arm_groups: dict[str, dict[str, dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        metrics, group_metrics = historical.full_metrics(by_arm[arm])
        arm_metrics[arm] = metrics
        arm_groups[arm] = group_metrics

    groups = sorted(arm_groups["A00"]["evidence_correctness"])
    if len(groups) != EXPECTED_GROUPS:
        raise AssertionError("expected exactly 7 independent groups")
    for arm in EXPECTED_ARMS[1:]:
        if sorted(arm_groups[arm]["evidence_correctness"]) != groups:
            raise AssertionError("group coverage mismatch between arms")

    expected_arm_metrics = {
        arm: {metric: round(value, 6) for metric, value in values.items()}
        for arm, values in arm_metrics.items()
    }
    expected_contrasts = historical.contrast_effects(arm_groups, groups)
    expected_factorial = historical.factorial_effects(arm_groups, groups)

    mismatches: list[str] = []
    if result.get("arm_aggregate_metrics") != expected_arm_metrics:
        mismatches.append("arm_aggregate_metrics")
    if result.get("primary_contrasts") != expected_contrasts:
        mismatches.append("primary_contrasts")
    if result.get("factorial_main_effects_and_interaction") != expected_factorial:
        mismatches.append("factorial_main_effects_and_interaction")

    boundaries = result.get("execution_boundaries") or {}
    required_false = (
        "private_oracle_loaded", "provider_credentials_present", "scores_recomputed",
        "candidate_regeneration", "logo_executed", "slice_analysis_executed",
        "semantic_stage_executed",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        mismatches.append("execution_boundaries_false")
    required_zero = (
        "provider_calls", "model_calls", "network_io", "fresh_blind_accesses",
        "legacy_locked_test_accesses",
    )
    if any(int(boundaries.get(key) or 0) != 0 for key in required_zero):
        mismatches.append("execution_boundaries_zero")

    claim = result.get("claim_boundary") or {}
    if any(claim.get(key) is not False for key in (
        "automatic_preferred_state", "survivor_decision_executed",
        "semantic_eligibility_decision_executed", "architecture_frozen",
        "production_readiness_claim",
    )):
        mismatches.append("claim_boundary")

    validation = {
        "schema_version": "p12-c4-bootstrap-20000-validation-v1",
        "status": "PASS_INDEPENDENT_BOOTSTRAP_RECOMPUTATION" if not mismatches else "FAIL_BOOTSTRAP_RECOMPUTATION_MISMATCH",
        "deterministic_score_rows_sha256": EXPECTED_INPUT_SHA256,
        "bootstrap_result_sha256": sha256(args.bootstrap_result),
        "historical_factorial_scorer_sha256": EXPECTED_HISTORICAL_SCORER_SHA256,
        "rows_reused_without_rescoring": EXPECTED_ROWS,
        "arms": EXPECTED_ARMS,
        "rows_per_arm": EXPECTED_PARENTS,
        "independent_groups": EXPECTED_GROUPS,
        "bootstrap_resamples_verified": EXPECTED_BOOTSTRAP_N,
        "bootstrap_seed_verified": EXPECTED_SEED,
        "historical_arm_metrics_exact_match": "arm_aggregate_metrics" not in mismatches,
        "historical_primary_contrasts_exact_match": "primary_contrasts" not in mismatches,
        "historical_factorial_effects_exact_match": "factorial_main_effects_and_interaction" not in mismatches,
        "mismatch_sections": mismatches,
        "provider_calls": 0,
        "private_oracle_loaded": False,
        "logo_executed": False,
        "slice_analysis_executed": False,
        "semantic_stage_executed": False,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": validation["status"],
        "mismatch_sections": mismatches,
        "bootstrap_result_sha256": validation["bootstrap_result_sha256"],
    }, indent=2))
    return 0 if not mismatches else 2


if __name__ == "__main__":
    raise SystemExit(main())
