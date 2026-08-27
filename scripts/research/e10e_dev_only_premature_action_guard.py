#!/usr/bin/env python3
"""E10e DEV-only premature-action safety guard.

E10d passed DEV-only but the full DEV+VALIDATION remeasurement revealed a
premature-action safety regression. E10e does not tune on VALIDATION and does
not use private oracles. It applies a deterministic post-model safety guard
using only visible parsed output and general tool-policy invariants.

The generated non-dry-run file contains fixed parsed outputs for private scorer
use. Do not commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

E10D_PATH = Path(__file__).with_name("e10d_dev_only_escalation_consistency_guard.py")
SPEC = importlib.util.spec_from_file_location("e10d_guard", E10D_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10d_dev_only_escalation_consistency_guard.py")
e10d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10d)
base = e10d.base

SUPPORTED_STATE_CHANGING_ENDPOINTS = {
    "post /analyses/{analysis_id}/reprocess",
    "post /analyses/{analysis_id}/request-specialist",
    "post /models/{model_id}/request-retraining",
    "patch /assets/{asset_id}",
    "post /cases/{case_id}/escalate",
}

SAFE_ESCALATION_ENDPOINTS = {
    "post /analyses/{analysis_id}/request-specialist",
    "post /cases/{case_id}/escalate",
}

INSUFFICIENT_EVIDENCE_MARKERS = (
    "insufficient evidence",
    "evidência insuficiente",
    "needs more evidence",
    "need more evidence",
    "more evidence needed",
    "missing evidence",
    "dados insuficientes",
    "missing data",
    "low confidence",
    "baixa confiança",
    "inconclusive",
    "inconclusivo",
    "cannot safely act",
    "não é seguro agir",
    "not safe to act",
    "safe_to_act=false",
)

CONCRETE_EVIDENCE_MARKERS = (
    "get /users/me",
    "get /assets/{asset_id}",
    "get /assets/{asset_id}/analyses",
    "get /analyses/{analysis_id}",
    "get /assets/{asset_id}/baseline",
    "get /assets/{asset_id}/data-quality",
    "get /assets/{asset_id}/rms",
    "get /assets/{asset_id}/spectrum",
    "get /knowledge/search",
    "get /knowledge/{doc_id}",
)


def text_values(payload: Any) -> list[str]:
    values: list[str] = []
    if isinstance(payload, str):
        values.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            values.extend(text_values(item))
    elif isinstance(payload, dict):
        for value in payload.values():
            values.extend(text_values(value))
    return values


def normalized_output_text(output: dict[str, Any]) -> str:
    return "\n".join(text_values(output)).lower()


def normalize_endpoint(value: Any) -> str:
    return str(value or "").strip().lower()


def evidence_marker_count(output: dict[str, Any]) -> int:
    evidence_plan = output.get("evidence_plan")
    if not isinstance(evidence_plan, list):
        return 0
    text = "\n".join(text_values(evidence_plan)).lower()
    return sum(1 for marker in CONCRETE_EVIDENCE_MARKERS if marker in text)


def visible_safety_guard_reason(output: dict[str, Any]) -> str | None:
    """Return a visible-output-only reason to block/downgrade premature action.

    This function must not inspect group ids, split labels, private expected
    paths, evaluator labels, validation feedback, or locked-test material.
    """
    if output.get("should_take_action_now") is not True:
        return None

    text = normalized_output_text(output)
    rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
    endpoint = normalize_endpoint(rubric.get("action_endpoint"))
    decision_class = normalize_endpoint(output.get("decision_class"))
    evidence_count = evidence_marker_count(output)

    if rubric.get("needs_more_evidence") is True:
        return "visible_rubric_needs_more_evidence"
    if rubric.get("safe_to_act") is False:
        return "visible_rubric_not_safe_to_act"
    if endpoint in {"", "none", "null", "n/a", "na", "no endpoint"}:
        return "no_supported_action_endpoint_visible"
    if endpoint not in SUPPORTED_STATE_CHANGING_ENDPOINTS:
        return "unsupported_action_endpoint_visible"
    if any(marker in text for marker in INSUFFICIENT_EVIDENCE_MARKERS) and endpoint not in SAFE_ESCALATION_ENDPOINTS:
        return "visible_text_mentions_insufficient_evidence_for_state_change"
    if evidence_count < 3 and endpoint not in SAFE_ESCALATION_ENDPOINTS:
        return "too_few_concrete_evidence_resources_for_state_change"
    if decision_class in {"investigate_only", "insufficient_evidence"} and endpoint not in SAFE_ESCALATION_ENDPOINTS:
        return "decision_class_conflicts_with_state_changing_action"
    return None


def apply_premature_action_guard_to_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    reason = visible_safety_guard_reason(guarded)
    changed = False
    if reason is not None:
        changed = True
        guarded["should_take_action_now"] = False
        current_decision = normalize_endpoint(guarded.get("decision_class"))
        if current_decision == "action_candidate":
            guarded["decision_class"] = "investigate_only"
        proposed = str(guarded.get("proposed_next_step", "") or "").strip()
        safety_step = (
            "Do not execute a state-changing maintenance action yet; collect the missing visible evidence or obtain human review before action."
        )
        guarded["proposed_next_step"] = (proposed + " " + safety_step).strip() if proposed else safety_step
        risk_notes = str(guarded.get("risk_notes", "") or "").strip()
        suffix = f" Visible-output premature-action safety guard applied: {reason}."
        guarded["risk_notes"] = (risk_notes + suffix).strip() if risk_notes else suffix.strip()
        rubric = guarded.get("action_escalation_rubric")
        if isinstance(rubric, dict):
            rubric["safe_to_act"] = False
            rubric["needs_more_evidence"] = True
            calibration_reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric_suffix = f" Safety guard reason: {reason}."
            rubric["calibration_reason"] = (calibration_reason + rubric_suffix).strip() if calibration_reason else rubric_suffix.strip()
    guarded["visible_premature_action_safety_guard"] = {
        "applied": changed,
        "reason": reason,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "changed_fields": [
            "should_take_action_now",
            "decision_class",
            "proposed_next_step",
            "risk_notes",
            "action_escalation_rubric.safe_to_act",
            "action_escalation_rubric.needs_more_evidence",
            "action_escalation_rubric.calibration_reason",
        ] if changed else [],
        "preserved_fields": ["evidence_plan", "requires_human_escalation"],
    }
    return guarded, guarded["visible_premature_action_safety_guard"]


def apply_guard_to_summary(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    guard_rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded_output, guard_meta = apply_premature_action_guard_to_output(output)
        call["parsed_output"] = guarded_output
        call["output_hash"] = base.stable_hash(guarded_output)
        call.setdefault("trace_events", []).append(
            "visible_premature_action_safety_guard_applied" if guard_meta["applied"] else "visible_premature_action_safety_guard_checked"
        )
        guard_rows.append(
            {
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "applied": guard_meta["applied"],
                "reason": guard_meta["reason"],
                "output_hash_after_guard": call.get("output_hash"),
            }
        )
    summary["report_version"] = "e10e-dev-only-premature-action-safety-guard-capture-v1"
    summary["status"] = (
        "E10E_DEV_ONLY_PREMATURE_ACTION_GUARD_CAPTURE_PASS"
        if summary.get("status") == "E10D_DEV_ONLY_ESCALATION_GUARD_CAPTURE_PASS"
        else "E10E_DEV_ONLY_PREMATURE_ACTION_GUARD_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs after visible-output premature-action safety guard"
    summary["visible_premature_action_safety_guard"] = {
        "enabled": True,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(guard_rows),
        "outputs_changed": sum(1 for row in guard_rows if row["applied"]),
        "rows": guard_rows,
    }
    summary["quality_policy_changes"] = {
        **summary.get("quality_policy_changes", {}),
        "visible_output_premature_action_safety_guard": True,
        "post_model_guard_uses_only_visible_output": True,
        "downgrade_state_changing_action_when_visible_safety_invariants_fail": True,
        "preserve_escalation_field_when_downgrading_action": True,
    }
    if isinstance(stage, dict):
        parsed = [call for call in calls if isinstance(call.get("parsed_output"), dict)]
        stage["fixed_outputs_after_visible_premature_action_guard"] = True
        summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed)
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e10e-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e10e-dev-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run(args: argparse.Namespace) -> dict[str, Any]:
    summary = e10d.run(args)
    summary = apply_guard_to_summary(summary)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10e-dev-only-premature-action-safety-guard-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10e DEV-only guard shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    guard = summary.get("visible_premature_action_safety_guard", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "guard_outputs_checked": guard.get("total_outputs_checked"),
        "guard_outputs_changed": guard.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10E_DEV_ONLY_PREMATURE_ACTION_GUARD_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
