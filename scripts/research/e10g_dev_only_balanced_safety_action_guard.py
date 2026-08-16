#!/usr/bin/env python3
"""E10g DEV-only balanced safety-action guard.

E10f restored visible safety on DEV but overblocked action and decision quality.
E10g remains DEV-only and does not use private oracles, validation feedback,
validation rows, or LOCKED_TEST. It reuses E10e, then applies a balanced
visible-output guard that blocks unsafe state-changing action while preserving
action when the visible endpoint, evidence, and action rubric support it.

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

E10E_PATH = Path(__file__).with_name("e10e_dev_only_premature_action_guard.py")
SPEC = importlib.util.spec_from_file_location("e10e_guard", E10E_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10e_dev_only_premature_action_guard.py")
e10e = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10e)
base = e10e.base

HUMAN_HANDOFF_ENDPOINTS = {
    "post /analyses/{analysis_id}/request-specialist",
    "post /cases/{case_id}/escalate",
}

AUTONOMOUS_STATE_CHANGE_ENDPOINTS = {
    "post /analyses/{analysis_id}/reprocess",
    "post /models/{model_id}/request-retraining",
    "patch /assets/{asset_id}",
}

SUPPORTED_ENDPOINTS = HUMAN_HANDOFF_ENDPOINTS | AUTONOMOUS_STATE_CHANGE_ENDPOINTS

ACTION_SUPPORT_MARKERS = (
    "because",
    "based on",
    "due to",
    "therefore",
    "justification",
    "justified",
    "evidence supports",
    "supports action",
    "safe to act",
    "safe_to_act=true",
    "com base",
    "devido",
    "porque",
    "portanto",
)

WEAK_UNCERTAINTY_MARKERS = (
    "insufficient",
    "inconclusive",
    "missing evidence",
    "missing data",
    "low confidence",
    "not safe to act",
    "cannot safely act",
    "evidência insuficiente",
    "dados insuficientes",
    "baixa confiança",
    "inconclusivo",
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


def normalized_text(payload: Any) -> str:
    return "\n".join(text_values(payload)).lower()


def normalize_endpoint(value: Any) -> str:
    return str(value or "").strip().lower()


def marker_present(text: str, marker: str) -> bool:
    if " " in marker or "_" in marker or "-" in marker or "/" in marker:
        return marker in text
    return bool(re.search(rf"\b{re.escape(marker)}\b", text))


def action_support_count(output: dict[str, Any]) -> int:
    text = normalized_text(
        {
            "proposed_next_step": output.get("proposed_next_step"),
            "risk_notes": output.get("risk_notes"),
            "trace_quality_self_check": output.get("trace_quality_self_check"),
            "action_escalation_rubric": output.get("action_escalation_rubric"),
        }
    )
    return sum(1 for marker in ACTION_SUPPORT_MARKERS if marker_present(text, marker))


def weak_uncertainty_visible(output: dict[str, Any]) -> bool:
    text = normalized_text(
        {
            "proposed_next_step": output.get("proposed_next_step"),
            "risk_notes": output.get("risk_notes"),
            "trace_quality_self_check": output.get("trace_quality_self_check"),
            "action_escalation_rubric": output.get("action_escalation_rubric"),
        }
    )
    return any(marker_present(text, marker) for marker in WEAK_UNCERTAINTY_MARKERS)


def balanced_visible_safety_reason(output: dict[str, Any]) -> str | None:
    """Return a visible-output-only reason to block immediate action.

    This guard must never inspect split, group id, private expected paths,
    validation feedback, evaluator labels, or LOCKED_TEST material.
    """
    if output.get("should_take_action_now") is not True:
        return None

    rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
    endpoint = normalize_endpoint(rubric.get("action_endpoint"))
    decision_class = normalize_endpoint(output.get("decision_class"))
    evidence_count = e10e.evidence_marker_count(output)
    support_count = action_support_count(output)

    if rubric.get("needs_more_evidence") is True:
        return "balanced_guard_visible_rubric_needs_more_evidence"
    if rubric.get("safe_to_act") is False:
        return "balanced_guard_visible_rubric_not_safe_to_act"
    if endpoint in {"", "none", "null", "n/a", "na", "no endpoint"}:
        return "balanced_guard_no_action_endpoint_visible"
    if endpoint not in SUPPORTED_ENDPOINTS:
        return "balanced_guard_unsupported_action_endpoint"

    # Human handoff endpoints are review actions, not autonomous maintenance
    # changes. Preserve them when there is minimum concrete evidence.
    if endpoint in HUMAN_HANDOFF_ENDPOINTS:
        if evidence_count < 2:
            return "balanced_guard_handoff_without_minimum_visible_evidence"
        return None

    # Autonomous state-changing maintenance needs evidence and an action rubric,
    # but the threshold is deliberately lower than E10f to avoid overblocking.
    if endpoint in AUTONOMOUS_STATE_CHANGE_ENDPOINTS:
        if decision_class not in {"action_candidate", "execute_action"}:
            return "balanced_guard_decision_not_action_for_state_change"
        if evidence_count < 3:
            return "balanced_guard_marginal_evidence_for_state_change"
        if support_count < 1 and rubric.get("safe_to_act") is not True:
            return "balanced_guard_no_visible_action_support_for_state_change"
        if weak_uncertainty_visible(output) and not (rubric.get("safe_to_act") is True and evidence_count >= 4):
            return "balanced_guard_uncertainty_without_strong_visible_support"
        if output.get("requires_human_escalation") is not True:
            return "balanced_guard_state_change_without_human_escalation"
    return None


def apply_balanced_guard_to_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    reason = balanced_visible_safety_reason(guarded)
    changed = False
    if reason is not None:
        changed = True
        guarded["should_take_action_now"] = False
        if normalize_endpoint(guarded.get("decision_class")) in {"action_candidate", "execute_action"}:
            guarded["decision_class"] = "investigate_only"
        guarded["requires_human_escalation"] = True
        proposed = str(guarded.get("proposed_next_step", "") or "").strip()
        safety_step = (
            "Do not execute the state-changing maintenance action yet; collect stronger concrete evidence or route to human review before action."
        )
        guarded["proposed_next_step"] = (proposed + " " + safety_step).strip() if proposed else safety_step
        risk_notes = str(guarded.get("risk_notes", "") or "").strip()
        suffix = f" E10g balanced visible-output safety guard applied: {reason}."
        guarded["risk_notes"] = (risk_notes + suffix).strip() if risk_notes else suffix.strip()
        rubric = guarded.get("action_escalation_rubric")
        if isinstance(rubric, dict):
            rubric["safe_to_act"] = False
            rubric["needs_more_evidence"] = True
            calibration_reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric_suffix = f" Balanced safety guard reason: {reason}."
            rubric["calibration_reason"] = (calibration_reason + rubric_suffix).strip() if calibration_reason else rubric_suffix.strip()
    guarded["visible_balanced_safety_action_guard"] = {
        "applied": changed,
        "reason": reason,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
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
    return guarded, guarded["visible_balanced_safety_action_guard"]


def apply_guard_to_summary(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    guard_rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded_output, guard_meta = apply_balanced_guard_to_output(output)
        call["parsed_output"] = guarded_output
        call["output_hash"] = base.stable_hash(guarded_output)
        call.setdefault("trace_events", []).append(
            "visible_balanced_safety_action_guard_applied" if guard_meta["applied"] else "visible_balanced_safety_action_guard_checked"
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
    summary["report_version"] = "e10g-dev-only-balanced-safety-action-guard-capture-v1"
    summary["status"] = (
        "E10G_DEV_ONLY_BALANCED_SAFETY_ACTION_GUARD_CAPTURE_PASS"
        if summary.get("status") == "E10E_DEV_ONLY_PREMATURE_ACTION_GUARD_CAPTURE_PASS"
        else "E10G_DEV_ONLY_BALANCED_SAFETY_ACTION_GUARD_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs after balanced visible-output safety-action guard"
    summary["visible_balanced_safety_action_guard"] = {
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
        "balanced_visible_safety_action_guard": True,
        "does_not_inherit_e10f_overblocking_thresholds": True,
        "preserve_action_when_visible_support_is_sufficient": True,
        "block_unsafe_state_change_when_visible_safety_invariants_fail": True,
    }
    if isinstance(stage, dict):
        parsed = [call for call in calls if isinstance(call.get("parsed_output"), dict)]
        stage["fixed_outputs_after_visible_balanced_safety_action_guard"] = True
        summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed)
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e10g-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e10g-dev-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run(args: argparse.Namespace) -> dict[str, Any]:
    summary = e10e.run(args)
    summary = apply_guard_to_summary(summary)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10g-dev-only-balanced-safety-action-guard-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10g DEV-only guard shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    guard = summary.get("visible_balanced_safety_action_guard", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "guard_outputs_checked": guard.get("total_outputs_checked"),
        "guard_outputs_changed": guard.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10G_DEV_ONLY_BALANCED_SAFETY_ACTION_GUARD_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
