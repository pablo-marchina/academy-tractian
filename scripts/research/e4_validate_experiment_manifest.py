from __future__ import annotations

"""Validate the E4 B0-B3 experiment manifest.

The validator is deliberately policy-heavy. It protects the project from silently turning
E4 into prompt/model/runtime optimization on the locked test set or into a demo-first flow.
"""

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_VARIANTS = ["B0", "B1", "B2", "B3"]
EXPECTED_PRIMARY_METRICS = {
    "uncontained_policy_violation_count",
    "invalid_action_execution_count",
    "unauthorized_or_cross_company_action_execution_count",
    "argument_schema_valid",
    "required_argument_completeness",
    "action_execution_correct",
    "decision_correct",
    "required_fact_coverage",
    "forbidden_claim_rate",
    "evidence_source_coverage",
    "escalation_decision_correct",
    "handoff_completeness",
}
REQUIRED_FORBIDDEN_LOCKED_TEST_USES = {
    "prompt_tuning",
    "model_selection",
    "runtime_selection",
    "agent_policy_debugging",
    "architecture_ablation",
    "threshold_fitting",
    "optimizer_feedback",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("research/experiments/e4-b0-b3-experiment-manifest.json"),
    )
    parser.add_argument(
        "--split",
        type=Path,
        default=Path("research/frozen/benchmark-split-v1.json"),
    )
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    split = load_json(args.split)

    assert manifest["manifest_version"] == "e4-b0-b3-experiment-manifest-v1"
    assert manifest["status"] == "PREREGISTERED"
    assert split["schema_version"] == "benchmark-split-v1"
    assert split["status"] == "FROZEN"

    assert manifest["non_demo_policy"]["demo_first_development_forbidden"] is True
    assert manifest["non_demo_policy"]["scripted_reference_paths_are_quality_evidence"] is False
    assert manifest["non_demo_policy"]["test_doubles_are_quality_evidence"] is False
    assert manifest["non_demo_policy"]["agent_quality_requires_non_demo_proposal_source"] is True

    assert manifest["allowed_splits"] == ["DEV", "VALIDATION"]
    assert manifest["forbidden_splits_for_selection"] == ["LOCKED_TEST"]
    assert manifest["locked_test_policy"]["locked_test_used"] is False
    assert set(manifest["locked_test_policy"]["forbidden_before_final"]) >= REQUIRED_FORBIDDEN_LOCKED_TEST_USES
    assert split["rules"]["locked_test_available_for_architecture_selection"] is False
    assert split["rules"]["locked_test_available_for_prompt_or_model_selection"] is False

    variants = manifest["variants"]
    assert [variant["variant"] for variant in variants] == EXPECTED_VARIANTS

    by_variant = {variant["variant"]: variant for variant in variants}
    assert by_variant["B0"] == {
        "variant": "B0",
        "description": "minimal benchmark-valid wrapper",
        "strict_arguments": False,
        "permission_resource_guard": False,
        "evidence_action_gate": False,
        "confirmation_gate": False,
    }
    assert by_variant["B1"]["strict_arguments"] is True
    assert by_variant["B1"]["permission_resource_guard"] is False
    assert by_variant["B2"]["strict_arguments"] is True
    assert by_variant["B2"]["permission_resource_guard"] is True
    assert by_variant["B2"]["evidence_action_gate"] is False
    assert by_variant["B3"]["strict_arguments"] is True
    assert by_variant["B3"]["permission_resource_guard"] is True
    assert by_variant["B3"]["evidence_action_gate"] is True
    assert all(variant["confirmation_gate"] is False for variant in variants)
    assert manifest["excluded_variant"]["variant"] == "B4"

    primary = {item["name"] for item in manifest["primary_metrics"]}
    assert primary >= EXPECTED_PRIMARY_METRICS, sorted(EXPECTED_PRIMARY_METRICS - primary)
    hard_safety = {item["name"] for item in manifest["primary_metrics"] if item.get("hard_safety") is True}
    assert "uncontained_policy_violation_count" in hard_safety
    assert "unauthorized_or_cross_company_action_execution_count" in hard_safety

    constraints = manifest["analysis_constraints"]
    assert constraints["no_single_weighted_score"] is True
    assert constraints["hard_safety_reported_separately"] is True
    assert constraints["contained_proposals_not_counted_as_executed_safety_failures"] is True
    assert constraints["dev_runs_are_debugging_not_component_promotion"] is True
    assert constraints["validation_runs_support_selection"] is True
    assert constraints["locked_test_runs_forbidden"] is True

    assert manifest["run_plan"]["phase_1"]["splits"] == ["DEV"]
    assert manifest["run_plan"]["phase_2"]["splits"] == ["VALIDATION"]

    print(json.dumps({
        "status": "PASS",
        "experiment_id": manifest["experiment_id"],
        "variants": EXPECTED_VARIANTS,
        "allowed_splits": manifest["allowed_splits"],
        "locked_test_used": manifest["locked_test_policy"]["locked_test_used"],
        "primary_metric_count": len(manifest["primary_metrics"]),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
