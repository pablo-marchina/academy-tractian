#!/usr/bin/env python3
from __future__ import annotations

"""P12-C4 bootstrap-only statistical gate.

Consumes the exact frozen 144-row deterministic C4 scoring artifact and performs
only the preregistered group-cluster percentile bootstrap. It does not load any
private oracle, call any provider/model/network service, execute LOGO, compute
modality/failure slices, perform semantic evaluation, or authorize a survivor.
"""

import argparse
import hashlib
import json
import math
import os
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

EXPECTED_INPUT_SHA256 = "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c"
EXPECTED_INPUT_SCHEMA = "p12-c4-deterministic-private-scoring-rows-v1"
EXPECTED_INPUT_STATUS = "PASS_144_OF_144_DETERMINISTIC_SCORES"
EXPECTED_EXPERIMENT_ID = "P12-C4-PROSPECTIVE-EXPOSED-POOL"
EXPECTED_PARTITION = "EXPOSED_POOL"
EXPECTED_ARMS = ["A00", "A10", "A01", "A11"]
EXPECTED_PARENTS = 36
EXPECTED_ROWS = 144
EXPECTED_GROUPS = 7
BOOTSTRAP_N = 20_000
BOOTSTRAP_SEED = 20260822
CONFIDENCE_LEVEL = 0.95
RESAMPLING_UNIT = "asset_story_group"

PROVENANCE_PINS = {
    "deterministic_scoring_freeze_path": "research/results/p12-c4-deterministic-scoring-freeze-2026-08-27.json",
    "deterministic_scoring_freeze_git_blob_sha": "9db9c14c38da0edc83dd69147fb5b884926fcbe9",
    "factorial_preregistration_path": "research/experiments/p12-c2-exposed-pool-factorial-evidence-safety-preregistration-v1.json",
    "factorial_preregistration_git_blob_sha": "0d0637a954ef544824bc69df88e47d7c790f0714",
    "historical_factorial_scorer_path": "scripts/research/p12_c2_factorial_score.py",
    "historical_factorial_scorer_git_blob_sha": "dc20be4896ff023989ee6deb012ad440c39ec531",
    "historical_factorial_scorer_sha256": "f3500751448c3b52bf361f4d565ba940c8e9e62e8ab197bb1206fdb7d89a7d22",
}

PROVIDER_CREDENTIAL_ENVS = (
    "NVIDIA_API_KEY",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "CEREBRAS_API_KEY",
    "OPENROUTER_API_KEY",
)

METRIC_SPECS = {
    "evidence_correctness": ("evidence_correct", "higher"),
    "mean_expected_read_recall": ("evidence_recall", "higher"),
    "mean_extra_public_read_count": ("extra_public_read_count", "lower"),
    "task_or_reference_quality": ("reference_quality", "higher"),
    "decision_correctness": ("decision_correct", "higher"),
    "action_correctness": ("action_correct", "higher"),
    "escalation_correctness": ("escalation_correct", "higher"),
    "premature_action_rate": ("premature_action", "lower"),
    "unsupported_action_or_escalation_rate": ("unsupported_action_or_escalation", "lower"),
    "schema_valid_rate": ("schema_valid", "higher"),
}

PRIMARY_COMPARISONS = {
    "A10_minus_A00": {
        "lhs": "A10",
        "rhs": "A00",
        "metrics": [
            "evidence_correctness",
            "mean_expected_read_recall",
            "mean_extra_public_read_count",
            "task_or_reference_quality",
        ],
    },
    "A01_minus_A00": {
        "lhs": "A01",
        "rhs": "A00",
        "metrics": [
            "unsupported_action_or_escalation_rate",
            "confirmed_p12_hard_safety_violation_rate",
            "decision_correctness",
            "action_correctness",
            "escalation_correctness",
        ],
    },
    "A11_minus_A00": {
        "lhs": "A11",
        "rhs": "A00",
        "metrics": [
            "evidence_correctness",
            "mean_expected_read_recall",
            "mean_extra_public_read_count",
            "task_or_reference_quality",
            "decision_correctness",
            "action_correctness",
            "escalation_correctness",
            "unsupported_action_or_escalation_rate",
            "confirmed_p12_hard_safety_violation_rate",
        ],
    },
}

INTERACTION_METRICS = [
    "mean_expected_read_recall",
    "mean_extra_public_read_count",
    "action_correctness",
    "unsupported_action_or_escalation_rate",
]

REPORT_METRICS = [
    "evidence_correctness",
    "mean_expected_read_recall",
    "mean_extra_public_read_count",
    "task_or_reference_quality",
    "decision_correctness",
    "action_correctness",
    "escalation_correctness",
    "premature_action_rate",
    "unsupported_action_or_escalation_rate",
    "locked_test_or_gold_leakage_rate",
    "confirmed_p12_hard_safety_violation_rate",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else float("nan")


def qtile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_values[lo]
    w = pos - lo
    return sorted_values[lo] * (1 - w) + sorted_values[hi] * w


def as_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raise AssertionError(f"metric value is not numeric: {value!r}")


def verify_environment() -> None:
    present = sorted(name for name in PROVIDER_CREDENTIAL_ENVS if os.getenv(name))
    if present:
        raise AssertionError(f"provider credential(s) present in bootstrap environment: {present}")


def verify_input(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    actual_hash = sha256_bytes(path)
    if actual_hash != EXPECTED_INPUT_SHA256:
        raise AssertionError(f"deterministic input SHA-256 mismatch: {actual_hash}")

    payload = load_json(path)
    if not isinstance(payload, dict):
        raise AssertionError("deterministic input must be a JSON object")
    if payload.get("schema_version") != EXPECTED_INPUT_SCHEMA:
        raise AssertionError("deterministic input schema changed")
    if payload.get("status") != EXPECTED_INPUT_STATUS:
        raise AssertionError("deterministic input status changed")
    if payload.get("experiment_id") != EXPECTED_EXPERIMENT_ID:
        raise AssertionError("experiment id changed")
    if payload.get("partition") != EXPECTED_PARTITION:
        raise AssertionError("bootstrap may consume EXPOSED_POOL only")
    if payload.get("participating_arms") != EXPECTED_ARMS:
        raise AssertionError("factorial arm set/order changed")
    if int(payload.get("common_parent_count") or 0) != EXPECTED_PARENTS:
        raise AssertionError("common-parent count changed")
    if int(payload.get("fixed_factorial_outputs_scored") or 0) != EXPECTED_ROWS:
        raise AssertionError("fixed-output score count changed")
    if int(payload.get("scoreable_outputs") or 0) != EXPECTED_ROWS:
        raise AssertionError("not all deterministic outputs are scoreable")

    boundaries = payload.get("execution_boundaries") or {}
    for key in (
        "provider_calls",
        "model_calls",
        "network_io",
        "candidate_private_oracle_accesses",
        "fresh_blind_accesses",
        "legacy_locked_test_accesses",
    ):
        if int(boundaries.get(key) or 0) != 0:
            raise AssertionError(f"frozen deterministic boundary changed: {key}")
    for key in (
        "bootstrap_executed",
        "logo_executed",
        "slice_analysis_executed",
        "semantic_stage_executed",
        "independent_validation_executed",
    ):
        if boundaries.get(key) is not False:
            raise AssertionError(f"frozen deterministic artifact already marks later stage executed: {key}")

    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROWS:
        raise AssertionError("expected exactly 144 deterministic rows")

    per_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    arms: dict[str, list[dict[str, Any]]] = defaultdict(list)
    groups: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("deterministic row is not an object")
        if row.get("score", {}).get("scoreable") is not True:
            raise AssertionError("unscoreable deterministic row found")
        arm = str(row.get("arm"))
        if arm not in EXPECTED_ARMS:
            raise AssertionError(f"unexpected arm: {arm}")
        parent = str(row.get("parent_id"))
        group = str(row.get("group_id"))
        if not parent or not group:
            raise AssertionError("missing parent/group binding")
        per_parent[parent].append(row)
        arms[arm].append(row)
        groups.add(group)

    expected_parent_ids = [f"P{i:02d}" for i in range(1, EXPECTED_PARENTS + 1)]
    if sorted(per_parent) != expected_parent_ids:
        raise AssertionError("parent coverage is not exactly P01..P36")
    for parent, parent_rows in per_parent.items():
        if len(parent_rows) != 4 or {str(r["arm"]) for r in parent_rows} != set(EXPECTED_ARMS):
            raise AssertionError(f"incomplete factorial geometry for {parent}")
        for key in (
            "ordinal",
            "group_id",
            "scenario_id",
            "ticket_id",
            "modality",
            "seed",
            "repeat_index",
            "request_sha256",
            "common_parent_row_sha256",
            "common_parent_output_sha256",
        ):
            if len({str(r.get(key)) for r in parent_rows}) != 1:
                raise AssertionError(f"common-parent binding changed across arms for {parent}: {key}")
    if any(len(arms[arm]) != EXPECTED_PARENTS for arm in EXPECTED_ARMS):
        raise AssertionError("each arm must contain exactly 36 rows")
    if len(groups) != EXPECTED_GROUPS:
        raise AssertionError(f"expected 7 independent groups, got {len(groups)}")

    return payload, rows, sorted(groups)


def nested_group_metrics(rows: list[dict[str, Any]], metric: str) -> dict[str, float]:
    score_key, _ = METRIC_SPECS[metric]
    ticket_values: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        ticket_values[(str(row["group_id"]), str(row["scenario_id"]), str(row["ticket_id"]))].append(
            as_float(row["score"][score_key])
        )
    ticket_means = {key: mean(vals) for key, vals in ticket_values.items()}
    scenario_values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for (group, scenario, _ticket), value in ticket_means.items():
        scenario_values[(group, scenario)].append(value)
    scenario_means = {key: mean(vals) for key, vals in scenario_values.items()}
    group_values: dict[str, list[float]] = defaultdict(list)
    for (group, _scenario), value in scenario_means.items():
        group_values[group].append(value)
    return {group: mean(vals) for group, vals in sorted(group_values.items())}


def full_metrics(rows: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    group_by_metric: dict[str, dict[str, float]] = {}
    full: dict[str, float] = {}
    for metric in METRIC_SPECS:
        gm = nested_group_metrics(rows, metric)
        group_by_metric[metric] = gm
        full[metric] = mean(gm.values())

    leakage_group: dict[str, float] = {}
    hard_group: dict[str, float] = {}
    hard_count = 0
    for group in sorted({str(r["group_id"]) for r in rows}):
        group_rows = [r for r in rows if str(r["group_id"]) == group]
        leakage: list[float] = []
        hard: list[float] = []
        for row in group_rows:
            score = row["score"]
            leak = not (bool(score["no_locked_test_claim"]) and bool(score["no_gold_claim"]))
            violation = bool(score["premature_action"]) or bool(score["unsupported_action_or_escalation"]) or leak
            leakage.append(1.0 if leak else 0.0)
            hard.append(1.0 if violation else 0.0)
            hard_count += int(violation)
        leakage_group[group] = mean(leakage)
        hard_group[group] = mean(hard)

    group_by_metric["locked_test_or_gold_leakage_rate"] = leakage_group
    group_by_metric["confirmed_p12_hard_safety_violation_rate"] = hard_group
    full["locked_test_or_gold_leakage_rate"] = mean(leakage_group.values())
    full["confirmed_p12_hard_safety_violation_rate"] = mean(hard_group.values())
    full["confirmed_p12_hard_safety_violations"] = float(hard_count)
    return full, group_by_metric


def bootstrap_group_effect(group_effect: dict[str, float], groups: list[str]) -> dict[str, Any]:
    # Historical C2 semantics: a fresh Random(seed) is created for every metric.
    rng = random.Random(BOOTSTRAP_SEED)
    draws: list[float] = []
    for _ in range(BOOTSTRAP_N):
        sampled = [rng.choice(groups) for _ in groups]
        draws.append(mean(group_effect[group] for group in sampled))
    draws.sort()
    alpha = (1.0 - CONFIDENCE_LEVEL) / 2.0
    return {
        "point_estimate": round(mean(group_effect[group] for group in groups), 6),
        "ci95_low": round(qtile(draws, alpha), 6),
        "ci95_high": round(qtile(draws, 1.0 - alpha), 6),
        "bootstrap_resamples": BOOTSTRAP_N,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def contrast_effects(
    arm_groups: dict[str, dict[str, dict[str, float]]], groups: list[str]
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, spec in PRIMARY_COMPARISONS.items():
        lhs = str(spec["lhs"])
        rhs = str(spec["rhs"])
        out[name] = {}
        for metric in spec["metrics"]:
            effect = {group: arm_groups[lhs][metric][group] - arm_groups[rhs][metric][group] for group in groups}
            out[name][metric] = {
                **bootstrap_group_effect(effect, groups),
                "lhs": lhs,
                "rhs": rhs,
                "direction": METRIC_SPECS.get(metric, (None, "lower"))[1],
                "per_group_effect": {group: round(effect[group], 6) for group in groups},
            }
    return out


def factorial_effects(
    arm_groups: dict[str, dict[str, dict[str, float]]], groups: list[str]
) -> dict[str, Any]:
    metrics = sorted(set(REPORT_METRICS) | set(INTERACTION_METRICS))
    result: dict[str, Any] = {"evidence_main_effect": {}, "safety_main_effect": {}, "interaction": {}}
    for metric in metrics:
        evidence = {
            group: 0.5 * (
                (arm_groups["A10"][metric][group] - arm_groups["A00"][metric][group])
                + (arm_groups["A11"][metric][group] - arm_groups["A01"][metric][group])
            )
            for group in groups
        }
        safety = {
            group: 0.5 * (
                (arm_groups["A01"][metric][group] - arm_groups["A00"][metric][group])
                + (arm_groups["A11"][metric][group] - arm_groups["A10"][metric][group])
            )
            for group in groups
        }
        interaction = {
            group: (arm_groups["A11"][metric][group] - arm_groups["A10"][metric][group])
            - (arm_groups["A01"][metric][group] - arm_groups["A00"][metric][group])
            for group in groups
        }
        result["evidence_main_effect"][metric] = bootstrap_group_effect(evidence, groups)
        result["safety_main_effect"][metric] = bootstrap_group_effect(safety, groups)
        if metric in INTERACTION_METRICS:
            result["interaction"][metric] = bootstrap_group_effect(interaction, groups)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score-rows", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    verify_environment()
    _payload, rows, groups = verify_input(args.score_rows)

    by_arm = {arm: [row for row in rows if row["arm"] == arm] for arm in EXPECTED_ARMS}
    arm_metrics: dict[str, dict[str, float]] = {}
    arm_groups: dict[str, dict[str, dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        metrics, group_metrics = full_metrics(by_arm[arm])
        arm_metrics[arm] = metrics
        arm_groups[arm] = group_metrics
        for metric_groups in group_metrics.values():
            if sorted(metric_groups) != groups:
                raise AssertionError(f"group coverage mismatch in arm {arm}")

    primary_contrasts = contrast_effects(arm_groups, groups)
    factorial = factorial_effects(arm_groups, groups)

    result = {
        "schema_version": "p12-c4-bootstrap-20000-result-v1",
        "status": "PASS_C4_BOOTSTRAP_20000_COMPLETE",
        "experiment_id": EXPECTED_EXPERIMENT_ID,
        "partition": EXPECTED_PARTITION,
        "input": {
            "deterministic_score_rows_sha256": EXPECTED_INPUT_SHA256,
            "deterministic_score_rows": EXPECTED_ROWS,
            "common_parents": EXPECTED_PARENTS,
            "participating_arms": EXPECTED_ARMS,
            "independent_groups": EXPECTED_GROUPS,
        },
        "provenance_pins": PROVENANCE_PINS,
        "aggregation": {
            "hierarchy": "asset_story_group -> scenario -> ticket -> repeated_run",
            "group_weighting": "EQUAL_WEIGHT_PER_INDEPENDENT_GROUP",
            "within_group_scenario_weighting": "EQUAL_WEIGHT_PER_SCENARIO",
            "within_scenario_ticket_weighting": "EQUAL_WEIGHT_PER_TICKET",
            "within_ticket_run_weighting": "EQUAL_WEIGHT_PER_VALID_RUN",
            "hard_safety_and_leakage_group_rates": "historical C2 direct mean over rows within group",
        },
        "bootstrap": {
            "method": "GROUP_CLUSTER_PERCENTILE_BOOTSTRAP",
            "resampling_unit": RESAMPLING_UNIT,
            "resamples": BOOTSTRAP_N,
            "seed": BOOTSTRAP_SEED,
            "confidence_level": CONFIDENCE_LEVEL,
            "rng_semantics": "fresh random.Random(seed) per comparison metric, matching historical frozen C2 scorer",
        },
        "arm_aggregate_metrics": {
            arm: {metric: round(value, 6) for metric, value in metrics.items()}
            for arm, metrics in arm_metrics.items()
        },
        "primary_contrasts": primary_contrasts,
        "factorial_main_effects_and_interaction": factorial,
        "execution_boundaries": {
            "private_oracle_loaded": False,
            "provider_credentials_present": False,
            "provider_calls": 0,
            "model_calls": 0,
            "network_io": 0,
            "scores_recomputed": False,
            "candidate_regeneration": False,
            "logo_executed": False,
            "slice_analysis_executed": False,
            "semantic_stage_executed": False,
            "fresh_blind_accesses": 0,
            "legacy_locked_test_accesses": 0,
        },
        "claim_boundary": {
            "automatic_preferred_state": False,
            "survivor_decision_executed": False,
            "semantic_eligibility_decision_executed": False,
            "architecture_frozen": False,
            "production_readiness_claim": False,
        },
        "next_required_transition": "FREEZE_AND_INDEPENDENTLY_VALIDATE_BOOTSTRAP_RESULT",
        "next_gate_authorized_by_this_runner": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "input_sha256": EXPECTED_INPUT_SHA256,
        "independent_groups": EXPECTED_GROUPS,
        "bootstrap_resamples": BOOTSTRAP_N,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "logo_executed": False,
        "slice_analysis_executed": False,
        "semantic_stage_executed": False,
        "next_gate_authorized": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
