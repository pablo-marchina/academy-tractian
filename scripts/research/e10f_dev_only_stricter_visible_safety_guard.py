#!/usr/bin/env python3
"""E10f DEV-only stricter visible-output safety guard.

E10e passed DEV-only but full DEV+VALIDATION remeasurement showed the
premature-action safety regression persisted. E10f remains DEV-only and does
not use private oracles, validation feedback, validation rows, or LOCKED_TEST.

It reuses E10e, then applies a stricter deterministic guard based only on the
visible parsed output and general state-changing action safety invariants.

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

HIGH_AUTONOMY_STATE_CHANGE_ENDPOINTS = {
    "post /analyses/{analysis_id}/reprocess",
    "post /models/{model_id}/request-retraining",
    "patch /assets/{asset_id}",
}

SUPPORTED_ENDPOINTS = HUMAN_HANDOFF_ENDPOINTS | HIGH_AUTONOMY_STATE_CHANGE_ENDPOINTS

ACTION_SUPPORT_MARKERS = (
    "because",
    "based on",
    "due to",
    "therefore",
    "justification",
    "justified",
    "com base",
    "devido",
    "porque",
    "portanto",
    "evidence supports",
    "supports action",
    "safe to act",
    "safe_to_act=true",
    "endpoint",
    "action_endpoint",
)

HIGH_AUTONOMY_RISK_MARKERS = (
    "retrain",
    "retraining",
    "retreinamento",
    "patch",
    "update asset",
    "alterar ativo",
    "change asset",
    "reprocess",
    "reprocessar",
    "state-changing",
    "maintenance action",
)

WEAK_SUPPORT_MARKERS = (
    "may",
    "might",
    "could",
    "possibly",
    "provável",
    "talvez",
    "pode ser",
    "conditional",
    "condicional",
    "uncertain",
    "unclear",
    "ambiguous",
    "ambíguo",
    "not enough",
    "insufficient",
    "inconclusive",
    "missing",
    "low confidence",
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


def token_contains(text: str, marker: str) -> bool:
    if " " in marker or "/" in marker or "_" in marker or "-" in marker:
        return marker in text
    return bool(re.search(rf"\b{re.escape(marker)}\b", text))


def visible_action_support_count(output: dict[str, Any]) -> int:
    text = normalized_text(
        {
            "proposed_next_step": output.get("proposed_next_step"),
            "risk_notes": output.get("risk_notes"),
            "trace_quality_self_check": output.get("trace_quality_self_check"),
            "action_escalation_rubric": output.get("action_escalation_rubric"),
        }
    )
    return sum(1 for marker in ACTION_SUPPORT_MARKERS if token_contains(text, marker))


def visible_weak_support_count(output: dict[str, Any]) -> int:
    text = normalized_text(
        {
            "proposed_next_step": output.get("proposed_next_step"),
            "risk_notes": output.get("risk_notes"),
            "trace_quality_self_check": output.get("trace_quality_self_check"),
            "action_escalation_rubric": output.get("action_escalation_rubric"),
        }
    )
    return sum(1 for marker in WEAK_SUPPORT_MARKERS if token_contains(text, marker))


def endpoint_appears_in_visible_plan(output: dict[str, Any], endpoint: str) -> bool:
    if not endpoint:
        return False
    text = normalized_text(
        {
            "proposed_next_step": output.get("proposed_next_step"),
            "risk_notes": output.get("risk_notes"),
            "action_escalation_rubric": output.get("action_escalation_rubric"),
        }
    )
    endpoint_tail = endpoint.split(" ", 1)[-1]
    endpoint_verb = endpoint.split(" ", 1)[0]
    return endpoint in text or endpoint_tail in text or (endpoint_verb in text and "action_endpoint" in text)


def high_autonomy_risk_visible(output: dict[str, Any]) -> bool:
    text = normalized_text(output)
    return any(token_contains(text, marker) for marker in HIGH_AUTONOMY_RISK_MARKERS)


def strict_visible_safety_reason(output: dict[str, Any]) -> str | None:
    """Return a visible-output-only reason to block a premature action.

    This must never inspect split, group id, private expected paths, validation
    feedback, evaluator labels, or LOCKED_TEST material.
    """
    if output.get("should_take_action_now") is not True:
        return None

    rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
    endpoint = normalize_endpoint(rubric.get("action_endpoint"))
    decision_class = normalize_endpoint(output.get("decision_class"))
    evidence_count = e10e.evidence_marker_count(output)
    action_support_count = visible_action_support_count(output)
    weak_support_count = visible_weak_support_count(output)
    endpoint_visible = endpoint_appears_in_visible_plan(output, endpoint)

    if endpoint in {"", "none", "null", "n/a", "na", "no endpoint"}:
        return "strict_guard_no_action_endpoint_visible"
    if endpoint not in SUPPORTED_ENDPOINTS:
        return "strict_guard_unsupported_action_endpoint"

    # Human handoff endpoints are allowed at lower evidence thresholds because
    # they route to human review instead of autonomous maintenance change.
    if endpoint in HUMAN_HANDOFF_ENDPOINTS:
        if evidence_count < 2:
            return "strict_guard_human_handoff_without_minimum_visible_evidence"
        return None

    # High-autonomy maintenance actions need stronger visible support than a
    # generic action candidate. This is a general policy-level invariant, not a
    # validation-row rule.
    if endpoint in HIGH_AUTONOMY_STATE_CHANGE_ENDPOINTS:
        if decision_class not in {"action_candidate", "execute_action"}:
            return "strict_guard_decision_class_not_action_candidate_for_state_change"
        if not endpoint_visible:
            return "strict_guard_endpoint_not_explicitly_supported_by_visible_plan"
        if evidence_count < 4:
            return "strict_guard_marginal_evidence_for_high_autonomy_state_change"
        if action_support_count < 2:
            return "strict_guard_marginal_action_support_for_state_change"
        if weak_support_count > 0 and action_support_count < 3:
            return "strict_guard_weak_or_conditional_language_without_strong_action_support"
        if high_autonomy_risk_visible(output) and output.get("requires_human_escalation") is not True:
            return "strict_guard_high_autonomy_risk_without_human_escalation"
    return None


def apply_strict_visible_safety_guard_to_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    reason = strict_visible_safety_reason(guarded)
    changed = False
    if reason is not None:
        changed = True
        guarded["should_take_action_now"] = False
        if normalize_endpoint(guarded.get("decision_class")) in {"action_candidate", "execute_action"}:
            guarded["decision_class"] = "investigate_only"
        # State-changing action is blocked, but human review remains useful.
        guarded["requires_human_escalation"] = True
        proposed = str(guarded.get("proposed_next_step", "") or "").strip()
        safety_step = (
            "Do not execute the state-changing maintenance action yet; collect stronger concrete evidence or route to human review before action."
        )
        guarded["proposed_next_step"] = (proposed + " " + safety_step).strip() if proposed else safety_step
        risk_notes = str(guarded.get("risk_notes", "") or "").strip()
        suffix = f" E10f strict visible-output safety guard applied: {reason}."
        guarded["risk_notes"] = (risk_notes + suffix).strip() if risk_notes else suffix.strip()
        rubric = guarded.get("action_escalation_rubric")
        if isinstance(rubric, dict):
            rubric["safe_to_act"] = False
            rubric["needs_more_evidence"] = True
            calibration_reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric_suffix = f" E10f strict guard reason: {reason}."
            rubric["calibration_reason"] = (calibration_reason + rubric_suffix).strip() if calibration_reason else rubric_suffix.strip()
    guarded["e10f_strict_visible_safety_guard"] = {
        "applied": changed,
        "reason": reason,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "visible_evidence_marker_count": e10e.evidence_marker_count(guarded),
        "visible_action_support_count": visible_action_support_count(guarded),
        "visible_weak_support_count": visible_weak_support_count(guarded),
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
    return guarded, guarded["e10f_strict_visible_safety_guard"]


def apply_guard_to_summary(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    guard_rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded_output, guard_meta = apply_strict_visible_safety_guard_to_output(output)
        call["parsed_output"] = guarded_output
        call["output_hash"] = base.stable_hash(guarded_output)
        call.setdefault("trace_events", []).append(
            "e10f_strict_visible_safety_guard_applied" if guard_meta["applied"] else "e10f_strict_visible_safety_guard_checked"
        )
        guard_rows.append(
            {
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "applied": guard_meta["applied"],
                "reason": guard_meta["reason"],
                "visible_evidence_marker_count": guard_meta["visible_evidence_marker_count"],
                "visible_action_support_count": guard_meta["visible_action_support_count"],
                "visible_weak_support_count": guard_meta["visible_weak_support_count"],
                "output_hash_after_guard": call.get("output_hash"),
            }
        )
    summary["report_version"] = "e10f-dev-only-stricter-visible-safety-guard-capture-v1"
    summary["status"] = (
        "E10F_DEV_ONLY_STRICTER_VISIBLE_SAFETY_GUARD_CAPTURE_PASS"
        if summary.get("status") == "E10E_DEV_ONLY_PREMATURE_ACTION_GUARD_CAPTURE_PASS"
        else "E10F_DEV_ONLY_STRICTER_VISIBLE_SAFETY_GUARD_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs after E10f stricter visible-output safety guard"
    summary["e10f_strict_visible_safety_guard"] = {
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
        "e10f_stricter_visible_safety_guard": True,
        "block_high_autonomy_state_change_when_evidence_support_is_marginal": True,
        "require_action_endpoint_to_be_supported_by_visible_plan": True,
        "route_blocked_state_change_to_human_review": True,
    }
    if isinstance(stage, dict):
        parsed = [call for call in calls if isinstance(call.get("parsed_output"), dict)]
        stage["fixed_outputs_after_e10f_strict_visible_safety_guard"] = True
        summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed)
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e10f-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e10f-dev-e9-summary.json> --include-rows"
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
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10f-dev-only-stricter-visible-safety-guard-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10f DEV-only guard shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    guard = summary.get("e10f_strict_visible_safety_guard", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "guard_outputs_checked": guard.get("total_outputs_checked"),
        "guard_outputs_changed": guard.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10F_DEV_ONLY_STRICTER_VISIBLE_SAFETY_GUARD_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
