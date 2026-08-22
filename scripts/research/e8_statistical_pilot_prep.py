#!/usr/bin/env python3
"""E8 statistical pilot/model benchmark preparation validator.

This script validates the E8 prep manifest and emits a deterministic summary.
It makes no model calls, reads no partner-private evaluator gold, and never touches
LOCKED_TEST beyond split-manifest metadata needed to assert blocking.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_CONSTANTS = {
    "runtime_candidate": "LangGraph",
    "tool_contract_source": "research.e2.tool_registry.TOOLS",
    "execution_boundary": "HarnessRunner",
    "boundary_candidate": "B3",
    "stopping_policy_candidate": "evidence_sufficiency_policy",
    "evidence_planning": "adaptive_from_missing_evidence_requirements",
    "transport_path": "HttpxTransport",
    "internal_tool_surface_candidate": "native_tools",
    "external_interoperability_surface_candidate": "mcp_compatible_adapter",
}

FORBIDDEN_GOLD_MARKERS = {
    "eval/expected-paths.json",
    "eval/test-scenarios.md",
    "docs/test-scenarios.md",
    "data/cases.parquet",
    "LOCKED_TEST_groups",
    "scorer_only_oracles",
    "final_expected_answers",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_split_groups(split_manifest: dict[str, Any], split_name: str) -> set[str]:
    split = split_manifest.get("splits", {}).get(split_name, {})
    groups = split.get("groups", [])
    result: set[str] = set()
    for group in groups:
        if isinstance(group, str):
            result.add(group)
        elif isinstance(group, dict):
            group_id = group.get("group_id") or group.get("id")
            if group_id:
                result.add(str(group_id))
    return result


def validate_manifest(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    scope = manifest.get("scope", {})
    if scope.get("locked_test_accessed") is not False:
        failures.append("scope.locked_test_accessed must be false")
    if scope.get("allowed_splits") != ["DEV", "VALIDATION"]:
        failures.append("allowed_splits must be exactly DEV + VALIDATION")
    if "LOCKED_TEST" not in scope.get("forbidden_splits", []):
        failures.append("LOCKED_TEST must be forbidden")

    constants = manifest.get("constants", {})
    for key, expected in REQUIRED_CONSTANTS.items():
        if constants.get(key) != expected:
            failures.append(f"constant {key!r} must be {expected!r}")
    for freeze_key in (
        "model_provider_freeze",
        "mcp_topology_freeze",
        "rag_freeze",
        "multi_agent_freeze",
        "observability_freeze",
        "ui_freeze",
        "final_architecture_freeze",
    ):
        if constants.get(freeze_key) is not False:
            failures.append(f"{freeze_key} must be false")

    candidate_slots = manifest.get("candidate_slots", [])
    if len(candidate_slots) < 4:
        failures.append("at least four model/provider candidate slots are expected")
    paid_enabled = [slot.get("id") for slot in candidate_slots if slot.get("cost_policy", "").startswith("paid") and slot.get("enabled_by_default")]
    if paid_enabled:
        failures.append(f"paid model slots must not be enabled by default: {paid_enabled}")
    if "no_model_policy_baseline" not in {slot.get("id") for slot in candidate_slots}:
        failures.append("no_model_policy_baseline is required")

    budget = manifest.get("budget_policy", {})
    if budget.get("default_mode") != "free_first":
        failures.append("budget_policy.default_mode must be free_first")
    if budget.get("paid_models_enabled_by_default") is not False:
        failures.append("paid models must be disabled by default")
    if budget.get("ci_makes_model_calls") is not False:
        failures.append("CI prep must not make model calls")
    if budget.get("secrets_committed") is not False:
        failures.append("secrets_committed must be false")

    representative = manifest.get("representative_groups", {})
    locked_groups = extract_split_groups(split_manifest, "LOCKED_TEST")
    representative_flat = {group for groups in representative.values() for group in groups}
    leakage = representative_flat.intersection(locked_groups)
    if leakage:
        failures.append(f"representative groups include LOCKED_TEST groups: {sorted(leakage)}")
    if set(representative) != {"DEV", "VALIDATION"}:
        failures.append("representative_groups must include DEV and VALIDATION only")

    design_axes = {axis.get("id") for axis in manifest.get("design_axes", [])}
    required_axes = {"model_stochasticity_fixed_observations", "environment_robustness_deterministic_modes"}
    if design_axes != required_axes:
        failures.append("design_axes must separate model stochasticity and environment robustness")

    metrics = manifest.get("metrics", {})
    for metric in ("task_success", "runtrace_completeness", "locked_test_access_flag"):
        if metric not in metrics.get("primary", []):
            failures.append(f"primary metric missing: {metric}")

    leakage_controls = manifest.get("leakage_controls", {})
    forbidden_inputs = set(leakage_controls.get("forbidden_model_inputs", []))
    missing_forbidden = FORBIDDEN_GOLD_MARKERS - forbidden_inputs
    if missing_forbidden:
        failures.append(f"missing forbidden leakage controls: {sorted(missing_forbidden)}")

    criteria = set(manifest.get("success_criteria", []))
    for criterion in ("LOCKED_TEST_blocked", "ci_prep_runner_validates_without_model_calls", "final_architecture_not_frozen"):
        if criterion not in criteria:
            failures.append(f"success criterion missing: {criterion}")

    return failures


def build_summary(manifest: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    candidate_slots = manifest.get("candidate_slots", [])
    design_axes = manifest.get("design_axes", [])
    representative = manifest.get("representative_groups", {})
    representative_case_groups = sum(len(groups) for groups in representative.values())
    max_repeats = max(
        [
            axis.get("validation_repeats_per_candidate_case", 0)
            for axis in design_axes
            if axis.get("id") == "model_stochasticity_fixed_observations"
        ]
        or [0]
    )

    return {
        "report_version": "e8-statistical-pilot-prep-summary-v1",
        "date": manifest.get("date"),
        "status": "E8_PREP_PASS" if not failures else "E8_PREP_FAIL",
        "failures": failures,
        "scope": manifest.get("scope"),
        "constants_preserved": manifest.get("constants"),
        "candidate_slots_defined": len(candidate_slots),
        "candidate_slot_ids": [slot.get("id") for slot in candidate_slots],
        "paid_models_enabled_by_default": any(slot.get("enabled_by_default") and str(slot.get("cost_policy", "")).startswith("paid") for slot in candidate_slots),
        "budget_policy": manifest.get("budget_policy"),
        "representative_case_groups": representative_case_groups,
        "representative_groups": representative,
        "design_axes": [axis.get("id") for axis in design_axes],
        "max_validation_repeats_per_candidate_case": max_repeats,
        "primary_metrics": manifest.get("metrics", {}).get("primary", []),
        "secondary_metrics": manifest.get("metrics", {}).get("secondary", []),
        "leakage_controls_defined": bool(manifest.get("leakage_controls")),
        "ci_model_calls": manifest.get("budget_policy", {}).get("ci_makes_model_calls"),
        "locked_test_accessed": manifest.get("scope", {}).get("locked_test_accessed"),
        "final_architecture_freeze": manifest.get("constants", {}).get("final_architecture_freeze"),
        "next_gate": "E8 pilot execution once local credentials/budget are confirmed",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--split-manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    failures = validate_manifest(manifest, split_manifest)
    summary = build_summary(manifest, failures)

    args.out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
