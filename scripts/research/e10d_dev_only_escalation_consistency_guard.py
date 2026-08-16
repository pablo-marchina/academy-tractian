#!/usr/bin/env python3
"""E10d DEV-only visible-output escalation consistency guard.

E10c preserved decision/evidence/action quality on DEV but escalation correctness
stayed 0.0. E10d does not add oracle access. It applies a deterministic guard
after model generation and before private scoring, using only the visible parsed
model output and already visible harness policy.

The generated non-dry-run file contains fixed parsed outputs for private scorer
use. Do not commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

E10C_PATH = Path(__file__).with_name("e10c_dev_only_escalation_capture.py")
SPEC = importlib.util.spec_from_file_location("e10c_capture", E10C_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10c_dev_only_escalation_capture.py")
e10c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10c)
e10b = e10c.e10b
base = e10b.base

HUMAN_ESCALATION_MARKERS = (
    "request-specialist",
    "request specialist",
    "case escalate",
    "cases/{case_id}/escalate",
    "escalate",
    "escalation",
    "specialist",
    "especialista",
    "human",
    "humano",
    "approval",
    "aprovação",
    "permission",
    "permissão",
    "safety",
    "segurança",
    "severity",
    "severe",
    "critical",
    "crítico",
    "high impact",
    "alto impacto",
    "risk",
    "risco",
    "engineering review",
    "engineer",
    "engenheiro",
)

STATE_CHANGING_ACTION_ENDPOINTS = (
    "post /analyses/{analysis_id}/reprocess",
    "post /analyses/{analysis_id}/request-specialist",
    "post /models/{model_id}/request-retraining",
    "patch /assets/{asset_id}",
    "post /cases/{case_id}/escalate",
)

SPECIALIST_OR_ESCALATE_ENDPOINTS = (
    "post /analyses/{analysis_id}/request-specialist",
    "post /cases/{case_id}/escalate",
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


def visible_guard_reason(output: dict[str, Any]) -> str | None:
    """Return a visible-output-only reason to set human escalation.

    This uses no oracle, no private expected paths, no split feedback and no
    group-specific hardcoding. It only checks whether the model's own visible
    output selected a human/specialist/escalation condition or a state-changing
    maintenance action that should be guarded by a human-in-the-loop.
    """
    text = normalized_output_text(output)
    rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
    endpoint = str(rubric.get("action_endpoint", "") or "").strip().lower()
    decision_class = str(output.get("decision_class", "") or "").strip().lower()

    if output.get("requires_human_escalation") is True:
        return None
    if rubric.get("needs_human_escalation") is True:
        return "rubric_needs_human_escalation_true"
    if decision_class == "escalation_candidate":
        return "decision_class_escalation_candidate"
    if endpoint in SPECIALIST_OR_ESCALATE_ENDPOINTS:
        return "specialist_or_case_escalate_endpoint"
    if any(marker in text for marker in HUMAN_ESCALATION_MARKERS):
        return "visible_human_escalation_marker"
    if output.get("should_take_action_now") is True and endpoint in STATE_CHANGING_ACTION_ENDPOINTS:
        return "state_changing_action_requires_visible_human_loop_guard"
    return None


def apply_visible_escalation_guard_to_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    guarded = json.loads(json.dumps(output, ensure_ascii=False))
    reason = visible_guard_reason(guarded)
    changed = False
    if reason is not None:
        guarded["requires_human_escalation"] = True
        changed = True
        risk_notes = str(guarded.get("risk_notes", "") or "").strip()
        suffix = f" Visible-output escalation consistency guard applied: {reason}."
        guarded["risk_notes"] = (risk_notes + suffix).strip() if risk_notes else suffix.strip()
        rubric = guarded.get("action_escalation_rubric")
        if isinstance(rubric, dict):
            rubric["needs_human_escalation"] = True
            calibration_reason = str(rubric.get("calibration_reason", "") or "").strip()
            rubric_suffix = f" Visible guard reason: {reason}."
            rubric["calibration_reason"] = (calibration_reason + rubric_suffix).strip() if calibration_reason else rubric_suffix.strip()
    guarded["visible_escalation_consistency_guard"] = {
        "applied": changed,
        "reason": reason,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "changed_fields": ["requires_human_escalation", "risk_notes", "action_escalation_rubric.needs_human_escalation", "action_escalation_rubric.calibration_reason"] if changed else [],
        "preserved_fields": ["decision_class", "evidence_plan", "should_take_action_now", "proposed_next_step"],
    }
    return guarded, guarded["visible_escalation_consistency_guard"]


def apply_guard_to_summary(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    guard_rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded_output, guard_meta = apply_visible_escalation_guard_to_output(output)
        call["parsed_output"] = guarded_output
        call["output_hash"] = base.stable_hash(guarded_output)
        call.setdefault("trace_events", []).append("visible_escalation_consistency_guard_applied" if guard_meta["applied"] else "visible_escalation_consistency_guard_checked")
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
    summary["report_version"] = "e10d-dev-only-escalation-consistency-guard-capture-v1"
    summary["status"] = (
        "E10D_DEV_ONLY_ESCALATION_GUARD_CAPTURE_PASS"
        if summary.get("status") in {"E10C_DEV_ONLY_ESCALATION_CAPTURE_PASS", "E10B_DEV_ONLY_ACTION_ESCALATION_CAPTURE_PASS"}
        else "E10D_DEV_ONLY_ESCALATION_GUARD_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs after visible-output escalation consistency guard"
    summary["visible_escalation_consistency_guard"] = {
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
        "visible_output_escalation_consistency_guard": True,
        "post_model_guard_uses_only_visible_output": True,
        "preserve_decision_evidence_action_fields": True,
    }
    if isinstance(stage, dict):
        parsed = [call for call in calls if isinstance(call.get("parsed_output"), dict)]
        stage["fixed_outputs_after_visible_guard"] = True
        summary.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed)
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e10d-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e10d-dev-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run(args: argparse.Namespace) -> dict[str, Any]:
    summary = e10c.run(args)
    summary = apply_guard_to_summary(summary)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10d-dev-only-escalation-consistency-guard-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10d DEV-only guard shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    guard = summary.get("visible_escalation_consistency_guard", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "guard_outputs_checked": guard.get("total_outputs_checked"),
        "guard_outputs_changed": guard.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10D_DEV_ONLY_ESCALATION_GUARD_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
