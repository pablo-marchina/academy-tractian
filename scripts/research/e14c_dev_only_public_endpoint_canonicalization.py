#!/usr/bin/env python3
"""E14c DEV-only public action-endpoint canonicalization candidate.

E14c stays inside the unchanged E14 hard gate. Relative to the recovered E14
baseline it changes only how deterministic post-model guards compare public
action endpoints: concrete resource paths are canonicalized to the frozen
ToolSpec template in a temporary comparison view. The model output itself is
not rewritten.

No prompt/model/settings/scorer/threshold change. No VALIDATION tuning. No
LOCKED_TEST. No private oracle input to model or policy.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).parent
E14_PATH = HERE / "e14_dev_only_completeness_selective_reprocess.py"
NORMALIZER_PATH = HERE / "e14c_public_action_endpoint_normalization.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14 = load_module("e14_parent_for_e14c", E14_PATH)
endpoint_norm = load_module("e14c_endpoint_norm", NORMALIZER_PATH)
e11 = e14.e11
e10g = e11.e10g
e10e = e10g.e10e
e10d = e10e.e10d

E14C_MANIFEST = Path("research/experiments/e14c-dev-only-public-endpoint-canonicalization-manifest.json")


def _canonicalized_guard_view(output: dict[str, Any]) -> dict[str, Any]:
    """Clone only for guard evaluation; never mutate the stored model output."""

    view = copy.deepcopy(output)
    rubric = view.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        rubric["action_endpoint"] = endpoint_norm.canonicalize_public_action_endpoint(
            rubric.get("action_endpoint")
        )
    return view


def _canonical_normalize(value: Any) -> str:
    return endpoint_norm.canonicalize_public_action_endpoint(value)


def _capture_endpoint_stats(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    shapes: Counter[str] = Counter()
    canonical_views: Counter[str] = Counter()
    parsed = 0
    for call in calls:
        if not isinstance(call, dict):
            continue
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        parsed += 1
        rubric = output.get("action_escalation_rubric")
        endpoint = rubric.get("action_endpoint") if isinstance(rubric, dict) else None
        shape = endpoint_norm.endpoint_shape(endpoint)
        shapes[shape] += 1
        canonical = endpoint_norm.canonical_public_endpoint_or_none(endpoint)
        if canonical is not None:
            canonical_views[canonical] += 1
    return {
        "enabled": True,
        "source": "research.e2.tool_registry.TOOLS",
        "policy_input_only": True,
        "stored_model_output_endpoint_mutated": False,
        "concrete_resource_identifiers_printed": False,
        "private_oracle_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "parsed_outputs_checked": parsed,
        "endpoint_shape_counts": dict(sorted(shapes.items())),
        "canonical_public_endpoint_view_counts": dict(sorted(canonical_views.items())),
        "guards_using_canonical_endpoint_view": [
            "e10d_escalation_consistency_guard",
            "e10e_premature_action_guard",
            "e10g_balanced_action_guard",
            "e11_independent_action_authorization",
            "e13/e14_reprocess_authorization",
        ],
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    # E10e/E10g/E11 already centralize endpoint normalization through helper
    # functions. Patch those helpers only for this candidate.
    original_e10e_normalize = e10e.normalize_endpoint
    original_e10g_normalize = e10g.normalize_endpoint
    original_e11_normalize = e11.normalize_endpoint

    # E10d historically normalized inline, so give only its guard predicate a
    # canonicalized clone. Its stored parsed output remains untouched.
    original_e10d_reason: Callable[[dict[str, Any]], str | None] = e10d.visible_guard_reason

    def e10d_reason_with_public_endpoint_view(output: dict[str, Any]) -> str | None:
        return original_e10d_reason(_canonicalized_guard_view(output))

    try:
        e10e.normalize_endpoint = _canonical_normalize
        e10g.normalize_endpoint = _canonical_normalize
        e11.normalize_endpoint = _canonical_normalize
        e10d.visible_guard_reason = e10d_reason_with_public_endpoint_view
        summary = e14.run(args)
    finally:
        e10e.normalize_endpoint = original_e10e_normalize
        e10g.normalize_endpoint = original_e10g_normalize
        e11.normalize_endpoint = original_e11_normalize
        e10d.visible_guard_reason = original_e10d_reason

    parent_status = summary.get("status")
    capture_pass = parent_status == "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_PASS"
    summary["report_version"] = "e14c-dev-only-public-endpoint-canonicalization-v1"
    summary["status"] = (
        "E14C_DEV_ONLY_PUBLIC_ENDPOINT_CANONICALIZATION_CAPTURE_PASS"
        if capture_pass
        else "E14C_DEV_ONLY_PUBLIC_ENDPOINT_CANONICALIZATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14_capture_status"] = parent_status
    summary["e14c_public_action_endpoint_canonicalization"] = _capture_endpoint_stats(summary)
    summary["e14c_candidate"] = {
        "parent_gate": "E14",
        "comparison_anchor": "recovered_E14_same_gpt_oss_settings",
        "change_class": "deterministic_public_contract_endpoint_comparison_normalization_only",
        "model_output_rewritten": False,
        "prompt_changed": False,
        "model_changed": False,
        "reasoning_effort_changed": False,
        "completion_budget_changed": False,
        "thresholds_changed": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "private_oracle_used_by_policy": False,
        "explicit_safe_to_act_false_still_blocks": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    e14.run_dry_run_self_checks()

    examples = {
        "POST /analyses/analysis-123/reprocess": "post /analyses/{analysis_id}/reprocess",
        "POST /analyses/analysis-123/request-specialist": "post /analyses/{analysis_id}/request-specialist",
        "POST /models/model-123/request-retraining": "post /models/{model_id}/request-retraining",
        "PATCH /assets/asset-123": "patch /assets/{asset_id}",
        "POST /cases/case-123/escalate": "post /cases/{case_id}/escalate",
    }
    for concrete, expected in examples.items():
        actual = endpoint_norm.canonicalize_public_action_endpoint(concrete)
        if actual != expected:
            raise AssertionError(f"canonicalization self-check failed: {concrete} -> {actual}, expected {expected}")

    if endpoint_norm.canonicalize_public_action_endpoint("POST /cases/case-123/escalate extra") in endpoint_norm.PUBLIC_ACTION_ENDPOINTS:
        raise AssertionError("extra endpoint text must fail closed")
    if endpoint_norm.canonicalize_public_action_endpoint("GET /cases/case-123/escalate") in endpoint_norm.PUBLIC_ACTION_ENDPOINTS:
        raise AssertionError("wrong HTTP method must fail closed")

    sample = {
        "decision_class": "escalation_candidate",
        "evidence_plan": [],
        "should_take_action_now": True,
        "requires_human_escalation": True,
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": True,
            "action_endpoint": "POST /cases/case-123/escalate",
        },
    }
    original = e10e.normalize_endpoint
    try:
        e10e.normalize_endpoint = _canonical_normalize
        if e10e.visible_safety_guard_reason(sample) is not None:
            raise AssertionError("supported concrete case-escalation endpoint must not be rejected as unsupported")
        unsafe = copy.deepcopy(sample)
        unsafe["action_escalation_rubric"]["safe_to_act"] = False
        if e10e.visible_safety_guard_reason(unsafe) != "visible_rubric_not_safe_to_act":
            raise AssertionError("explicit safe_to_act=false must remain blocked after canonicalization")
    finally:
        e10e.normalize_endpoint = original


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14C_MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        run_self_checks()
    summary = run(args)
    completeness = summary.get("e14_completeness", {})
    boundary = summary.get("selective_reprocess_authorization_boundary", {})
    canon = summary.get("e14c_public_action_endpoint_canonicalization", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "concrete_public_action_endpoints_seen": canon.get("endpoint_shape_counts", {}).get("concrete_public_action_endpoint", 0),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs"),
    }, indent=2))
    return 0 if summary["status"] == "E14C_DEV_ONLY_PUBLIC_ENDPOINT_CANONICALIZATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
