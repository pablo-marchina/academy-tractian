#!/usr/bin/env python3
"""E14 DEV-only completeness-preserving selective reprocess runner."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


comp = load_module("e14_completeness", HERE / "e14_completeness_capture.py")
policy = load_module("e14_selective", HERE / "e14_selective_reprocess.py")
e11 = comp.e11
e10b = comp.e10b
e10c = e11.e10g.e10e.e10d.e10c
base = comp.base
capture = comp.capture
E14_MANIFEST = Path("research/experiments/e14-dev-only-completeness-selective-reprocess-manifest.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def e14_dry_output(packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    group_id = str(packet.get("group_id") or "asset_dry")
    strong = repeat_index % 2 == 0
    if strong:
        next_step = (
            "Because the RMS spike and baseline mismatch conflict with the current analysis, "
            "reprocess the current analysis to recompute the low-risk diagnostic result."
        )
        calibration = (
            "RMS spike plus baseline mismatch support reprocess; reprocess is the low-risk next diagnostic action."
        )
    else:
        next_step = "Reprocess the current analysis because the reprocess endpoint is available after reviewing the same evidence."
        calibration = "Generic reprocess request without a concrete observed defect or mismatch."
    output = {
        "decision_class": "action_candidate",
        "evidence_plan": [
            f"GET /assets/{{asset_id}} for visible asset context {group_id}",
            "GET /assets/{asset_id}/analyses then GET /analyses/{analysis_id} for the current analysis resource",
            "GET /assets/{asset_id}/baseline and GET /assets/{asset_id}/data-quality before reprocess",
            "GET /assets/{asset_id}/rms and GET /assets/{asset_id}/spectrum to ground the reprocess decision"
        ],
        "should_take_action_now": True,
        "requires_human_escalation": True,
        "proposed_next_step": next_step,
        "risk_notes": "Human review remains in the loop before the reprocess call.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True
        },
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": True,
            "action_endpoint": "POST /analyses/{analysis_id}/reprocess",
            "needs_human_escalation": True,
            "calibration_reason": calibration
        },
        "e14_dry_run_strength": "strong" if strong else "weak",
        "repeat_index": repeat_index,
        "packet_hash": base.stable_hash(packet)
    }
    return json.dumps(output), {"model": "dry_run_e14_selective_reprocess", "usage": {}}


def apply_to_summary(summary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    rows: list[dict[str, Any]] = []

    for call in calls:
        if not isinstance(call.get("parsed_output"), dict):
            rows.append({
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "is_target_reprocess_action": False,
                "authorized": False,
                "applied": False,
                "reason": "no_parsed_output",
                "support_anchor_count": 0,
                "support_anchors": []
            })
            continue
        guarded, meta = policy.apply(call)
        call["parsed_output"] = guarded
        call["output_hash"] = base.stable_hash(guarded)
        call["score"] = capture.score_output(guarded, json.dumps(guarded, ensure_ascii=False))
        call.setdefault("trace_events", []).append(
            "e14_selective_reprocess_blocked" if meta.get("applied") else "e14_selective_reprocess_checked"
        )
        rows.append({
            "group_id": call.get("group_id"),
            "split": call.get("split"),
            "repeat_index": call.get("repeat_index"),
            "is_target_reprocess_action": meta.get("is_target_reprocess_action"),
            "authorized": meta.get("authorized"),
            "applied": meta.get("applied"),
            "reason": meta.get("reason"),
            "endpoint": meta.get("endpoint"),
            "support_anchor_count": meta.get("support_anchor_count"),
            "support_anchors": meta.get("support_anchors")
        })

    parsed_calls = [c for c in calls if isinstance(c.get("parsed_output"), dict)]
    schema_valid = [bool(c.get("score", {}).get("schema_valid")) for c in calls]
    successful = [c for c in calls if c.get("error") is None]
    completeness_pass = len(calls) == 6 and len(parsed_calls) == 6 and len(successful) == 6 and all(schema_valid)
    upstream_status = summary.get("status")

    if isinstance(stage, dict):
        stage["stage"] = "DEV_E14_COMPLETENESS_SELECTIVE_REPROCESS"
        stage["successful_calls"] = len(successful)
        stage["parsed_outputs"] = len(parsed_calls)
        stage["scoreable_calls"] = sum(1 for x in schema_valid if x)
        stage["completeness_pass"] = completeness_pass
        stage["passed"] = bool(stage.get("passed")) and completeness_pass
        stage["fixed_outputs_after_selective_reprocess_boundary"] = True

    summary["report_version"] = "e14-dev-only-completeness-selective-reprocess-capture-v1"
    summary["status"] = (
        "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_PASS"
        if upstream_status == "E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_PASS" and completeness_pass
        else "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only complete fixed parsed outputs after E14 selective reprocess authorization"
    summary["candidate_policy_changes_under_measurement"] = manifest.get("candidate_change", {})
    summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed_calls)
    summary["aggregate_metrics"]["scoreable_calls"] = sum(1 for x in schema_valid if x)
    summary["scope"] = {
        "measurement_splits": ["DEV"],
        "validation_used_for_tuning": False,
        "validation_ran": False,
        "locked_test_accessed": False,
        "forbidden_splits": ["VALIDATION", "LOCKED_TEST"]
    }
    summary["e14_completeness"] = {
        "required_calls": 6,
        "required_parsed_outputs": 6,
        "required_scoreable_calls": 6,
        "actual_calls": len(calls),
        "actual_parsed_outputs": len(parsed_calls),
        "actual_scoreable_calls": sum(1 for x in schema_valid if x),
        "retry_count": sum((c.get("e14_completeness") or {}).get("retry_count", 0) for c in calls),
        "repair_count": sum((c.get("e14_completeness") or {}).get("repair_count", 0) for c in calls),
        "semantic_fields_invented_by_repair": False,
        "fail_closed": not completeness_pass,
        "passed": completeness_pass
    }
    summary["selective_reprocess_authorization_boundary"] = {
        "enabled": True,
        "target_endpoint": policy.REPROCESS_ENDPOINT,
        "required_concrete_support_anchors": 2,
        "uses_generic_evidence_family_count_as_sufficient": False,
        "uses_generic_human_review_markers_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(rows),
        "target_reprocess_outputs_checked": sum(1 for r in rows if r.get("is_target_reprocess_action")),
        "outputs_changed": sum(1 for r in rows if r.get("applied")),
        "authorized_target_reprocess_outputs": sum(1 for r in rows if r.get("is_target_reprocess_action") and r.get("authorized")),
        "blocked_target_reprocess_outputs": sum(1 for r in rows if r.get("is_target_reprocess_action") and not r.get("authorized")),
        "rows": rows
    }
    summary["quality_policy_changes"] = {
        **summary.get("quality_policy_changes", {}),
        "e14_retry_failed_calls_or_parse_failures_only": True,
        "e14_syntax_only_json_repair_without_semantic_invention": True,
        "e14_require_6_of_6_before_acceptance": True,
        "e14_selective_reprocess_authorization": True,
        "e14_require_all_mandatory_reprocess_support_conditions": True,
        "e14_require_at_least_two_concrete_support_anchors": True
    }
    summary["gold_leakage_controls"] = {
        **summary.get("gold_leakage_controls", {}),
        "model_prompt_receives_oracle": False,
        "selective_reprocess_boundary_receives_oracle": False,
        "validation_feedback_in_prompt_or_policy": False,
        "locked_test_forbidden_before_final": True,
        "outputs_hashed_before_scoring": all(c.get("output_hash") for c in parsed_calls)
    }
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e14-file> --oracle-file <private-eval/expected-paths.json> "
        "--out <e14-dev-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run_dry_run_self_checks() -> None:
    repaired, method = comp.syntax_only_json_repair('```json\n{"a": 1,}\n```')
    if repaired != {"a": 1} or method is None:
        raise AssertionError("E14 syntax-only repair self-check failed")
    strong = json.loads(e14_dry_output({"group_id": "asset_selfcheck"}, 0)[0])
    weak = json.loads(e14_dry_output({"group_id": "asset_selfcheck"}, 1)[0])
    strong_decision = policy.authorize({"group_id": "asset_selfcheck", "parsed_output": strong})
    weak_decision = policy.authorize({"group_id": "asset_selfcheck", "parsed_output": weak})
    if strong_decision.get("authorized") is not True or strong_decision.get("support_anchor_count", 0) < 2:
        raise AssertionError("E14 strong selective-reprocess self-check failed")
    if weak_decision.get("authorized") is not False:
        raise AssertionError("E14 weak selective-reprocess self-check failed")


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise AssertionError("manifest must be a JSON object")
    original_execute_stage = e10b.execute_stage
    original_dry_output = e10c.e10c_dry_output
    e10b.execute_stage = comp.execute_stage
    if args.dry_run:
        e10c.e10c_dry_output = e14_dry_output
    try:
        inherited_args = copy.copy(args)
        summary = e11.run(inherited_args)
    finally:
        e10b.execute_stage = original_execute_stage
        e10c.e10c_dry_output = original_dry_output
    summary = apply_to_summary(summary, manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14_MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        run_dry_run_self_checks()
    summary = run(args)
    boundary = summary.get("selective_reprocess_authorization_boundary", {})
    completeness = summary.get("e14_completeness", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "scoreable_calls": summary["aggregate_metrics"].get("scoreable_calls"),
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs")
    }, indent=2))
    return 0 if summary["status"] == "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
