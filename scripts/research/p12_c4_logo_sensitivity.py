#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

EXPECTED_SCORE_SHA256 = "b1c877f678b4c29be4bac362adfc7f05b84f73a9444db7f9903361858359719c"
EXPECTED_BOOTSTRAP_SHA256 = "08977c0d419144b885a7d2da6ffb73796ca43d80aa4e330a462d33c058464526"
EXPECTED_SCORE_SCHEMA = "p12-c4-deterministic-private-scoring-rows-v1"
EXPECTED_SCORE_STATUS = "PASS_144_OF_144_DETERMINISTIC_SCORES"
EXPECTED_BOOTSTRAP_SCHEMA = "p12-c4-bootstrap-20000-result-v1"
EXPECTED_BOOTSTRAP_STATUS = "PASS_C4_BOOTSTRAP_20000_COMPLETE"
EXPECTED_EXPERIMENT_ID = "P12-C4-PROSPECTIVE-EXPOSED-POOL"
EXPECTED_PARTITION = "EXPOSED_POOL"
EXPECTED_ARMS = ["A00", "A10", "A01", "A11"]
EXPECTED_ROWS = 144
EXPECTED_PARENTS = 36
EXPECTED_GROUPS = 7

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
        "lhs": "A10", "rhs": "A00",
        "metrics": [
            "evidence_correctness", "mean_expected_read_recall",
            "mean_extra_public_read_count", "task_or_reference_quality",
        ],
    },
    "A01_minus_A00": {
        "lhs": "A01", "rhs": "A00",
        "metrics": [
            "unsupported_action_or_escalation_rate",
            "confirmed_p12_hard_safety_violation_rate",
            "decision_correctness", "action_correctness", "escalation_correctness",
        ],
    },
    "A11_minus_A00": {
        "lhs": "A11", "rhs": "A00",
        "metrics": [
            "evidence_correctness", "mean_expected_read_recall",
            "mean_extra_public_read_count", "task_or_reference_quality",
            "decision_correctness", "action_correctness", "escalation_correctness",
            "unsupported_action_or_escalation_rate",
            "confirmed_p12_hard_safety_violation_rate",
        ],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else float("nan")


def as_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raise AssertionError(f"metric value is not numeric: {value!r}")


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
        leakage = []
        hard = []
        for r in group_rows:
            leak = not (bool(r["score"]["no_locked_test_claim"]) and bool(r["score"]["no_gold_claim"]))
            violation = (
                bool(r["score"]["premature_action"])
                or bool(r["score"]["unsupported_action_or_escalation"])
                or leak
            )
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


def logo_effects(
    arm_groups: dict[str, dict[str, dict[str, float]]], groups: list[str]
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, spec in PRIMARY_COMPARISONS.items():
        lhs, rhs = spec["lhs"], spec["rhs"]
        result[name] = {}
        for omitted in groups:
            retained = [g for g in groups if g != omitted]
            result[name][omitted] = {
                metric: round(mean(
                    arm_groups[lhs][metric][g] - arm_groups[rhs][metric][g]
                    for g in retained
                ), 6)
                for metric in spec["metrics"]
            }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--bootstrap-result", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    for key in ("NVIDIA_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CEREBRAS_API_KEY", "OPENROUTER_API_KEY"):
        if os.getenv(key):
            raise AssertionError(f"provider credential must be absent: {key}")

    if sha256(args.scores) != EXPECTED_SCORE_SHA256:
        raise AssertionError("deterministic score-row SHA-256 mismatch")
    if sha256(args.bootstrap_result) != EXPECTED_BOOTSTRAP_SHA256:
        raise AssertionError("bootstrap result SHA-256 mismatch")

    score_payload = load_json(args.scores)
    bootstrap_payload = load_json(args.bootstrap_result)
    if score_payload.get("schema_version") != EXPECTED_SCORE_SCHEMA or score_payload.get("status") != EXPECTED_SCORE_STATUS:
        raise AssertionError("deterministic score artifact schema/status mismatch")
    if score_payload.get("experiment_id") != EXPECTED_EXPERIMENT_ID or score_payload.get("partition") != EXPECTED_PARTITION:
        raise AssertionError("deterministic score artifact experiment/partition mismatch")
    if bootstrap_payload.get("schema_version") != EXPECTED_BOOTSTRAP_SCHEMA or bootstrap_payload.get("status") != EXPECTED_BOOTSTRAP_STATUS:
        raise AssertionError("bootstrap artifact schema/status mismatch")
    if bootstrap_payload.get("experiment_id") != EXPECTED_EXPERIMENT_ID or bootstrap_payload.get("partition") != EXPECTED_PARTITION:
        raise AssertionError("bootstrap artifact experiment/partition mismatch")
    bi = bootstrap_payload.get("input") or {}
    if bi.get("deterministic_score_rows_sha256") != EXPECTED_SCORE_SHA256:
        raise AssertionError("bootstrap input does not bind exact deterministic score rows")
    if bi.get("participating_arms") != EXPECTED_ARMS or int(bi.get("common_parents") or 0) != EXPECTED_PARENTS:
        raise AssertionError("bootstrap factorial geometry mismatch")
    bb = bootstrap_payload.get("execution_boundaries") or {}
    if bb.get("scores_recomputed") is not False or bb.get("logo_executed") is not False:
        raise AssertionError("bootstrap boundary is incompatible with LOGO handoff")
    if any(int(bb.get(k) or 0) != 0 for k in ("provider_calls", "model_calls", "network_io", "fresh_blind_accesses", "legacy_locked_test_accesses")):
        raise AssertionError("bootstrap boundary contains prohibited accesses")
    if bb.get("private_oracle_loaded") is not False or bb.get("slice_analysis_executed") is not False or bb.get("semantic_stage_executed") is not False:
        raise AssertionError("bootstrap boundary contains prohibited stage/access")

    rows = score_payload.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROWS:
        raise AssertionError("expected exactly 144 deterministic score rows")
    if score_payload.get("participating_arms") != EXPECTED_ARMS:
        raise AssertionError("deterministic score artifact arm ordering changed")
    if int(score_payload.get("common_parent_count") or 0) != EXPECTED_PARENTS:
        raise AssertionError("deterministic score artifact parent count changed")
    if any((r.get("score") or {}).get("scoreable") is not True for r in rows):
        raise AssertionError("all deterministic rows must remain scoreable")

    parent_arms: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        arm = str(r.get("arm"))
        if arm not in EXPECTED_ARMS:
            raise AssertionError("unexpected arm")
        parent_arms[str(r.get("parent_id"))].add(arm)
    if len(parent_arms) != EXPECTED_PARENTS or any(v != set(EXPECTED_ARMS) for v in parent_arms.values()):
        raise AssertionError("36x4 common-parent factorial pairing changed")

    by_arm = {arm: [r for r in rows if r["arm"] == arm] for arm in EXPECTED_ARMS}
    if any(len(v) != EXPECTED_PARENTS for v in by_arm.values()):
        raise AssertionError("each arm must contain 36 deterministic rows")

    arm_metrics: dict[str, dict[str, float]] = {}
    arm_groups: dict[str, dict[str, dict[str, float]]] = {}
    for arm, arm_rows in by_arm.items():
        metrics, group_metrics = full_metrics(arm_rows)
        arm_metrics[arm] = metrics
        arm_groups[arm] = group_metrics

    groups = sorted(arm_groups["A00"]["evidence_correctness"])
    if len(groups) != EXPECTED_GROUPS:
        raise AssertionError("independent group count changed")
    for arm in EXPECTED_ARMS[1:]:
        if groups != sorted(arm_groups[arm]["evidence_correctness"]):
            raise AssertionError("group coverage mismatch between arms")

    logo = logo_effects(arm_groups, groups)
    if any(len(per_comp) != EXPECTED_GROUPS for per_comp in logo.values()):
        raise AssertionError("each primary comparison must contain seven omitted-group estimates")

    full_point_estimates: dict[str, dict[str, float]] = {}
    for name, spec in PRIMARY_COMPARISONS.items():
        lhs, rhs = spec["lhs"], spec["rhs"]
        full_point_estimates[name] = {
            metric: round(mean(arm_groups[lhs][metric][g] - arm_groups[rhs][metric][g] for g in groups), 6)
            for metric in spec["metrics"]
        }

    result = {
        "schema_version": "p12-c4-logo-sensitivity-result-v1",
        "status": "PASS_C4_LEAVE_ONE_GROUP_OUT_SENSITIVITY_COMPLETE",
        "experiment_id": EXPECTED_EXPERIMENT_ID,
        "partition": EXPECTED_PARTITION,
        "input": {
            "deterministic_score_rows_sha256": EXPECTED_SCORE_SHA256,
            "bootstrap_result_sha256": EXPECTED_BOOTSTRAP_SHA256,
            "rows": EXPECTED_ROWS,
            "common_parents": EXPECTED_PARENTS,
            "participating_arms": EXPECTED_ARMS,
            "independent_groups": EXPECTED_GROUPS,
            "group_ids": groups,
        },
        "protocol": {
            "omission_unit": "asset_story_group",
            "omitted_groups_per_estimate": 1,
            "retained_groups_per_estimate": 6,
            "estimates_per_primary_comparison": 7,
            "primary_comparison_graph": PRIMARY_COMPARISONS,
            "semantics": "exact historical C2 logo_effects: omit one whole group and mean paired group effects over six retained groups",
        },
        "full_seven_group_primary_point_estimates": full_point_estimates,
        "leave_one_group_out_primary_contrasts": logo,
        "execution_boundaries": {
            "provider_calls": 0,
            "model_calls": 0,
            "network_io": 0,
            "private_oracle_loaded": False,
            "scores_recomputed_or_changed": False,
            "candidate_regeneration": False,
            "slice_analysis_executed": False,
            "semantic_stage_executed": False,
            "fresh_blind_accesses": 0,
            "legacy_locked_test_accesses": 0,
            "survivor_decision_executed": False,
        },
        "claim_boundary": {
            "this_result_proves": "the preregistered primary paired contrasts have been recomputed under each whole-group omission using the exact frozen C4 score rows and frozen historical C2 LOGO semantics",
            "this_result_does_not_prove": [
                "modality or failure-family robustness",
                "any arm is a final survivor or PREFERRED candidate",
                "semantic eligibility or semantic quality",
                "independent generalization",
                "production readiness",
            ],
        },
        "next_gate_authorized_by_this_runner": None,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "groups": groups,
        "comparisons": list(PRIMARY_COMPARISONS),
        "deterministic_score_rows_sha256": EXPECTED_SCORE_SHA256,
        "bootstrap_result_sha256": EXPECTED_BOOTSTRAP_SHA256,
        "later_gates_executed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
