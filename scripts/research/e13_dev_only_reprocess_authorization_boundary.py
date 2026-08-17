#!/usr/bin/env python3
"""E13 DEV-only reprocess-specific authorization boundary.

E12 identified that E11 did execute on the full DEV+VALIDATION capture, but it
was over-permissive or used the wrong authorization class: every output was
authorized as an autonomous state-changing reprocess action, and generic
visible evidence-family counts did not distinguish the failing full behavior.

E13 implements only the preregistered root-cause-specific change: do not
authorize POST /analyses/{analysis_id}/reprocess from generic evidence-family
counts or generic human-review markers. A reprocess action is allowed only when
visible, endpoint-specific evidence indicates that the current analysis itself
is invalid, failed, stale, incomplete, blocked by data-quality failure, or unsafe
to rely on without recomputation.

This runner is DEV-only. It must not inspect private expected paths, evaluator
labels, validation rows, validation feedback, reference trajectories, or
LOCKED_TEST material. Non-dry-run outputs are fixed parsed outputs for local
private scoring only and must not be committed.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

E11_PATH = Path(__file__).with_name("e11_dev_only_independent_action_authorization.py")
E13_MANIFEST = Path("research/experiments/e13-dev-only-reprocess-authorization-boundary-manifest.json")

SPEC_11 = importlib.util.spec_from_file_location("e11_policy", E11_PATH)
if SPEC_11 is None or SPEC_11.loader is None:
    raise RuntimeError("failed to load e11_dev_only_independent_action_authorization.py")
e11 = importlib.util.module_from_spec(SPEC_11)
SPEC_11.loader.exec_module(e11)
base = e11.base

REPROCESS_ENDPOINT = "post /analyses/{analysis_id}/reprocess"

REPROCESS_DEFECT_PATTERNS: dict[str, tuple[str, ...]] = {
    "analysis_failed_or_error": (
        "analysis failed",
        "failed analysis",
        "analysis failure",
        "analysis error",
        "analysis errored",
        "analysis exception",
        "analysis timeout",
        "failed to process",
        "processing failed",
        "erro na análise",
        "falha na análise",
        "falha de análise",
    ),
    "analysis_invalid_or_unreliable": (
        "analysis invalid",
        "invalid analysis",
        "unreliable analysis",
        "analysis unreliable",
        "analysis cannot be trusted",
        "cannot rely on the analysis",
        "unsafe to rely",
        "not safe to rely",
        "analysis is not reliable",
        "análise inválida",
        "analise invalida",
        "análise não confiável",
        "analise nao confiavel",
    ),
    "analysis_stale_or_outdated": (
        "analysis stale",
        "stale analysis",
        "analysis outdated",
        "outdated analysis",
        "analysis expired",
        "expired analysis",
        "older analysis",
        "stale result",
        "outdated result",
        "resultado desatualizado",
        "análise desatualizada",
        "analise desatualizada",
    ),
    "analysis_incomplete_or_missing_required_data": (
        "analysis incomplete",
        "incomplete analysis",
        "missing analysis",
        "missing required data",
        "missing data for analysis",
        "incomplete data for analysis",
        "insufficient data for analysis",
        "analysis missing required",
        "data gap",
        "gap in the analysis",
        "lacuna de dados",
        "dados insuficientes",
        "análise incompleta",
        "analise incompleta",
    ),
    "data_quality_blocked_analysis": (
        "data quality failed",
        "data-quality failed",
        "data quality failure",
        "quality gate failed",
        "quality gate blocked",
        "data-quality blocked",
        "blocked by data quality",
        "dq failed",
        "bad data quality",
        "sensor data invalid",
        "invalid sensor data",
        "qualidade dos dados falhou",
        "falha de qualidade dos dados",
    ),
    "unsafe_to_rely_without_recomputation": (
        "requires recomputation",
        "needs recomputation",
        "must recompute",
        "recompute before relying",
        "rerun the analysis before relying",
        "reprocess before relying",
        "cannot be used without recomputation",
        "unsafe without recomputation",
        "unsafe without reprocessing",
        "precisa recomputar",
        "recalcular antes",
        "reprocessar antes",
    ),
}

GENERIC_REPROCESS_WORDS = (
    "reprocess",
    "rerun",
    "recompute",
    "request reprocess",
    "run reprocess",
    "post /analyses/{analysis_id}/reprocess",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def marker_present(text: str, marker: str) -> bool:
    if " " in marker or "_" in marker or "-" in marker or "/" in marker:
        return marker in text
    return bool(re.search(rf"\b{re.escape(marker)}\b", text))


def output_rubric(output: dict[str, Any]) -> dict[str, Any]:
    rubric = output.get("action_escalation_rubric")
    return rubric if isinstance(rubric, dict) else {}


def output_endpoint(output: dict[str, Any]) -> str:
    return e11.normalize_endpoint(output_rubric(output).get("action_endpoint"))


def reprocess_evidence_text(output: dict[str, Any]) -> str:
    """Use visible support text only; do not use scorer/oracle material."""
    return e11.evidence_text(output)


def reprocess_defect_categories(output: dict[str, Any]) -> set[str]:
    text = reprocess_evidence_text(output)
    categories: set[str] = set()
    for category, patterns in REPROCESS_DEFECT_PATTERNS.items():
        if any(marker_present(text, pattern) for pattern in patterns):
            categories.add(category)
    return categories


def has_visible_analysis_identifier(call: dict[str, Any], output: dict[str, Any]) -> bool:
    text = reprocess_evidence_text(output)
    families = e11.evidence_families(output)
    return (
        "analysis" in families
        or "analysis_id" in text
        or "/analyses/" in text
        or output_endpoint(output) == REPROCESS_ENDPOINT
    )


def has_only_generic_reprocess_support(output: dict[str, Any], defect_categories: set[str]) -> bool:
    text = reprocess_evidence_text(output)
    has_generic = any(marker_present(text, marker) for marker in GENERIC_REPROCESS_WORDS)
    return has_generic and not defect_categories


def e13_reprocess_authorization(call: dict[str, Any]) -> dict[str, Any]:
    output = call.get("parsed_output")
    if not isinstance(output, dict):
        return {
            "authorized": False,
            "reason": "no_parsed_output",
            "target_endpoint": REPROCESS_ENDPOINT,
            "is_target_reprocess_action": False,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
        }

    endpoint = output_endpoint(output)
    defect_categories = sorted(reprocess_defect_categories(output))
    families = sorted(e11.evidence_families(output))
    requested_action = output.get("should_take_action_now") is True
    is_target = requested_action and endpoint == REPROCESS_ENDPOINT

    if not requested_action:
        return {
            "authorized": True,
            "reason": "no_immediate_action_requested",
            "target_endpoint": REPROCESS_ENDPOINT,
            "is_target_reprocess_action": False,
            "endpoint": endpoint,
            "evidence_families": families,
            "reprocess_defect_categories": defect_categories,
            "uses_generic_evidence_family_count_as_sufficient": False,
            "uses_generic_human_review_markers_as_sufficient": False,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
        }

    if endpoint != REPROCESS_ENDPOINT:
        return {
            "authorized": True,
            "reason": "not_reprocess_endpoint_boundary_target",
            "target_endpoint": REPROCESS_ENDPOINT,
            "is_target_reprocess_action": False,
            "endpoint": endpoint,
            "evidence_families": families,
            "reprocess_defect_categories": defect_categories,
            "uses_generic_evidence_family_count_as_sufficient": False,
            "uses_generic_human_review_markers_as_sufficient": False,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
        }

    if not has_visible_analysis_identifier(call, output):
        return {
            "authorized": False,
            "reason": "reprocess_missing_visible_analysis_identifier",
            "target_endpoint": REPROCESS_ENDPOINT,
            "is_target_reprocess_action": True,
            "endpoint": endpoint,
            "evidence_families": families,
            "reprocess_defect_categories": defect_categories,
            "uses_generic_evidence_family_count_as_sufficient": False,
            "uses_generic_human_review_markers_as_sufficient": False,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
        }

    if not defect_categories:
        return {
            "authorized": False,
            "reason": "missing_endpoint_specific_reprocess_defect_evidence",
            "target_endpoint": REPROCESS_ENDPOINT,
            "is_target_reprocess_action": True,
            "endpoint": endpoint,
            "evidence_families": families,
            "reprocess_defect_categories": defect_categories,
            "only_generic_reprocess_support": has_only_generic_reprocess_support(output, set()),
            "uses_generic_evidence_family_count_as_sufficient": False,
            "uses_generic_human_review_markers_as_sufficient": False,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
        }

    return {
        "authorized": True,
        "reason": "authorized_reprocess_with_endpoint_specific_defect_evidence",
        "target_endpoint": REPROCESS_ENDPOINT,
        "is_target_reprocess_action": True,
        "endpoint": endpoint,
        "evidence_families": families,
        "reprocess_defect_categories": defect_categories,
        "uses_generic_evidence_family_count_as_sufficient": False,
        "uses_generic_human_review_markers_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    }


def apply_reprocess_boundary_to_output(call: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    output = call.get("parsed_output")
    if not isinstance(output, dict):
        return output, e13_reprocess_authorization(call)
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    decision = e13_reprocess_authorization({**call, "parsed_output": guarded})
    changed = False
    if decision.get("is_target_reprocess_action") is True and decision.get("authorized") is not True:
        changed = True
        guarded["should_take_action_now"] = False
        guarded["requires_human_escalation"] = True
        decision_class = e11.normalize_endpoint(guarded.get("decision_class"))
        if decision_class in {"action_candidate", "execute_action", "autonomous_state_change"}:
            guarded["decision_class"] = "investigate_only"
        proposed = str(guarded.get("proposed_next_step", "") or "").strip()
        safety_step = (
            "E13 reprocess-specific authorization did not approve autonomous reprocess; investigate the analysis defect and route to human review before any POST /analyses/{analysis_id}/reprocess call."
        )
        guarded["proposed_next_step"] = (proposed + " " + safety_step).strip() if proposed else safety_step
        risk_notes = str(guarded.get("risk_notes", "") or "").strip()
        suffix = f" E13 blocked autonomous reprocess: {decision.get('reason')}."
        guarded["risk_notes"] = (risk_notes + suffix).strip() if risk_notes else suffix.strip()
        rubric = output_rubric(guarded)
        if rubric:
            rubric["safe_to_act"] = False
            rubric["needs_more_evidence"] = True
            calibration_reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric_suffix = f" Reprocess-specific authorization reason: {decision.get('reason')}."
            rubric["calibration_reason"] = (calibration_reason + rubric_suffix).strip() if calibration_reason else rubric_suffix.strip()
    guarded["reprocess_specific_authorization_boundary"] = {
        **decision,
        "applied": changed,
        "policy_input": "visible_parsed_output_plus_public_project_tool_invariants",
        "preregistered_root_cause_class": "policy_executed_but_over_permissive_or_wrong_authorization_class",
        "changed_fields": [
            "should_take_action_now",
            "decision_class",
            "requires_human_escalation",
            "proposed_next_step",
            "risk_notes",
            "action_escalation_rubric.safe_to_act",
            "action_escalation_rubric.needs_more_evidence",
            "action_escalation_rubric.calibration_reason",
        ] if changed else [],
        "preserved_fields": ["evidence_plan"],
    }
    return guarded, guarded["reprocess_specific_authorization_boundary"]


def apply_boundary_to_summary(summary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded_output, boundary_meta = apply_reprocess_boundary_to_output(call)
        call["parsed_output"] = guarded_output
        call["output_hash"] = base.stable_hash(guarded_output)
        call["score"] = e11.e10g.e10e.e10d.e10b.capture.score_output(guarded_output, json.dumps(guarded_output, ensure_ascii=False))
        call.setdefault("trace_events", []).append(
            "reprocess_specific_authorization_boundary_blocked" if boundary_meta["applied"] else "reprocess_specific_authorization_boundary_checked"
        )
        rows.append(
            {
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "is_target_reprocess_action": boundary_meta.get("is_target_reprocess_action"),
                "authorized": boundary_meta.get("authorized"),
                "applied": boundary_meta.get("applied"),
                "reason": boundary_meta.get("reason"),
                "endpoint": boundary_meta.get("endpoint"),
                "evidence_family_count": len(boundary_meta.get("evidence_families") or []),
                "reprocess_defect_categories": boundary_meta.get("reprocess_defect_categories"),
                "output_hash_after_boundary": call.get("output_hash"),
            }
        )
    if isinstance(stage, dict):
        parsed = [call for call in calls if isinstance(call.get("parsed_output"), dict)]
        schema_valid = [call.get("score", {}).get("schema_valid", False) for call in calls]
        task_success = [call.get("score", {}).get("task_success_proxy", False) for call in calls]
        no_locked = [call.get("score", {}).get("no_locked_test_claim", False) for call in calls]
        trace_complete = [bool(call.get("trace_complete")) for call in calls]
        successful = [call for call in calls if call.get("error") is None]
        stage["stage"] = "DEV_E13_REPROCESS_AUTHORIZATION_BOUNDARY"
        stage["successful_calls"] = len(successful)
        stage["passed"] = bool(calls) and len(successful) == len(calls) and all(schema_valid) and all(no_locked) and all(trace_complete)
        stage["task_success_proxy"] = round(sum(1 for item in task_success if item) / len(task_success), 4) if task_success else 0.0
        stage["schema_valid_rate"] = round(sum(1 for item in schema_valid if item) / len(schema_valid), 4) if schema_valid else 0.0
        stage["no_locked_test_claim_rate"] = round(sum(1 for item in no_locked if item) / len(no_locked), 4) if no_locked else 0.0
        stage["trace_completeness"] = all(trace_complete) if trace_complete else False
        stage["fixed_outputs_after_reprocess_boundary"] = True
        summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed)
    summary["report_version"] = "e13-dev-only-reprocess-authorization-boundary-capture-v1"
    upstream_status = summary.get("status")
    summary["status"] = (
        "E13_DEV_ONLY_REPROCESS_AUTHORIZATION_BOUNDARY_CAPTURE_PASS"
        if upstream_status == "E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_PASS"
        else "E13_DEV_ONLY_REPROCESS_AUTHORIZATION_BOUNDARY_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs after E13 reprocess-specific authorization boundary"
    summary["candidate_policy_changes_under_measurement"] = manifest.get("candidate_change", {})
    summary["scope"] = {
        "measurement_splits": ["DEV"],
        "validation_used_for_tuning": False,
        "validation_ran": False,
        "locked_test_accessed": False,
        "forbidden_splits": ["VALIDATION", "LOCKED_TEST"],
    }
    summary["gold_leakage_controls"] = {
        **summary.get("gold_leakage_controls", {}),
        "model_prompt_receives_oracle": False,
        "reprocess_boundary_receives_oracle": False,
        "validation_feedback_in_prompt_or_policy": False,
        "locked_test_forbidden_before_final": True,
        "outputs_hashed_before_scoring": all(call.get("output_hash") for call in calls if isinstance(call.get("parsed_output"), dict)),
    }
    summary["reprocess_specific_authorization_boundary"] = {
        "enabled": True,
        "target_endpoint": REPROCESS_ENDPOINT,
        "uses_generic_evidence_family_count_as_sufficient": False,
        "uses_generic_human_review_markers_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(rows),
        "target_reprocess_outputs_checked": sum(1 for row in rows if row.get("is_target_reprocess_action")),
        "outputs_changed": sum(1 for row in rows if row.get("applied")),
        "authorized_target_reprocess_outputs": sum(1 for row in rows if row.get("is_target_reprocess_action") and row.get("authorized")),
        "blocked_target_reprocess_outputs": sum(1 for row in rows if row.get("is_target_reprocess_action") and not row.get("authorized")),
        "rows": rows,
    }
    summary["quality_policy_changes"] = {
        **summary.get("quality_policy_changes", {}),
        "reprocess_specific_authorization_boundary": True,
        "do_not_authorize_reprocess_from_generic_evidence_family_count": True,
        "do_not_authorize_reprocess_from_generic_human_review_markers": True,
        "require_endpoint_specific_reprocess_defect_evidence": True,
    }
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e13-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e13-dev-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise AssertionError("manifest must be a JSON object")
    e11_args = copy.copy(args)
    # Keep the inherited E11 runner DEV-only. The E13 manifest is used only for
    # the additional preregistered boundary metadata in this runner.
    summary = e11.run(e11_args)
    summary = apply_boundary_to_summary(summary, manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E13_MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E13 DEV-only boundary shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    boundary = summary.get("reprocess_specific_authorization_boundary", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "boundary_outputs_checked": boundary.get("total_outputs_checked"),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "boundary_outputs_changed": boundary.get("outputs_changed"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E13_DEV_ONLY_REPROCESS_AUTHORIZATION_BOUNDARY_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
