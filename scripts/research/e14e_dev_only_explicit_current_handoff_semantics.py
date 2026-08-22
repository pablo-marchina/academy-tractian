#!/usr/bin/env python3
"""E14e DEV-only explicit current-handoff semantics candidate.

E14e inherits E14d and changes only the final free-text fallback inside E10d's
visible escalation-consistency guard. Historical E10d treats any marker token
such as risk/safety/severity/escalation as enough to force current human
escalation. E14e requires an explicit positive current-handoff phrase for that
fallback while preserving all stronger structured E10d conditions and the
state-changing-action human-loop branch.

No prompt/model/settings/scorer/threshold change. No VALIDATION tuning. No
LOCKED_TEST. No private oracle input to model or policy. Stored model output is
not rewritten except by the same E10d guard when an unchanged or refined public
condition legitimately applies.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).parent
E14D_PATH = HERE / "e14d_dev_only_public_evidence_resource_canonicalization.py"
HANDOFF_SEMANTICS_PATH = HERE / "e14e_explicit_current_handoff_semantics.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14d = load_module("e14d_parent_for_e14e", E14D_PATH)
handoff_semantics = load_module("e14e_handoff_semantics", HANDOFF_SEMANTICS_PATH)
e10d = e14d.e14c.e10d

E14E_MANIFEST = Path("research/experiments/e14e-dev-only-explicit-current-handoff-semantics-manifest.json")


def refined_visible_guard_reason(output: dict[str, Any]) -> str | None:
    """E10d with only the generic marker fallback refined.

    Ordering intentionally mirrors historical E10d. The first four structured
    handoff conditions and the final state-changing-action condition are
    unchanged. Only `any(marker in text ...)` is replaced.
    """
    rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
    endpoint = str(rubric.get("action_endpoint", "") or "").strip().lower()
    decision_class = str(output.get("decision_class", "") or "").strip().lower()

    if output.get("requires_human_escalation") is True:
        return None
    if rubric.get("needs_human_escalation") is True:
        return "rubric_needs_human_escalation_true"
    if decision_class == "escalation_candidate":
        return "decision_class_escalation_candidate"
    if endpoint in e10d.SPECIALIST_OR_ESCALATE_ENDPOINTS:
        return "specialist_or_case_escalate_endpoint"
    if handoff_semantics.has_explicit_current_handoff(output):
        return "explicit_current_handoff_phrase"
    if output.get("should_take_action_now") is True and endpoint in e10d.STATE_CHANGING_ACTION_ENDPOINTS:
        return "state_changing_action_requires_visible_human_loop_guard"
    return None


def _capture_e10d_stats(summary: dict[str, Any]) -> dict[str, Any]:
    guard = summary.get("visible_escalation_consistency_guard")
    rows = guard.get("rows", []) if isinstance(guard, dict) else []
    reason_counts: Counter[str] = Counter()
    changed = 0
    checked = 0
    allow = {
        "none",
        "rubric_needs_human_escalation_true",
        "decision_class_escalation_candidate",
        "specialist_or_case_escalate_endpoint",
        "explicit_current_handoff_phrase",
        "state_changing_action_requires_visible_human_loop_guard",
    }
    for row in rows:
        if not isinstance(row, dict):
            continue
        checked += 1
        changed += int(row.get("applied") is True)
        reason = str(row.get("reason") or "none")
        reason_counts[reason if reason in allow else "other_public_reason"] += 1

    return {
        "enabled": True,
        "change_scope": "historical_e10d_generic_text_marker_fallback_only",
        "historical_any_marker_substring_fallback_enabled": False,
        "explicit_positive_current_handoff_fallback_enabled": True,
        "negative_phrase_authorizes_current_handoff": False,
        "conditional_phrase_authorizes_current_handoff": False,
        "bare_generic_marker_authorizes_current_handoff": False,
        "requires_human_escalation_structured_condition_preserved": True,
        "rubric_needs_human_escalation_condition_preserved": True,
        "decision_class_escalation_candidate_condition_preserved": True,
        "specialist_or_case_escalate_endpoint_condition_preserved": True,
        "state_changing_action_human_loop_condition_preserved": True,
        "stored_model_output_pre_guard_rewritten": False,
        "private_oracle_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "total_outputs_checked": checked,
        "outputs_changed": changed,
        "reason_counts": dict(sorted(reason_counts.items())),
        "semantic_fields_checked_by_refined_fallback": list(handoff_semantics.SEMANTIC_FIELDS),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    original_reason: Callable[[dict[str, Any]], str | None] = e10d.visible_guard_reason
    try:
        # E14c wraps whatever E10d reason function is active with its temporary
        # canonical public endpoint comparison view. Patching before entering
        # E14d therefore preserves E14c endpoint normalization automatically.
        e10d.visible_guard_reason = refined_visible_guard_reason
        summary = e14d.run(args)
    finally:
        e10d.visible_guard_reason = original_reason

    parent_status = summary.get("status")
    capture_pass = parent_status == "E14D_DEV_ONLY_PUBLIC_EVIDENCE_RESOURCE_CANONICALIZATION_CAPTURE_PASS"
    summary["report_version"] = "e14e-dev-only-explicit-current-handoff-semantics-v1"
    summary["status"] = (
        "E14E_DEV_ONLY_EXPLICIT_CURRENT_HANDOFF_SEMANTICS_CAPTURE_PASS"
        if capture_pass
        else "E14E_DEV_ONLY_EXPLICIT_CURRENT_HANDOFF_SEMANTICS_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14d_capture_status"] = parent_status
    summary["e14e_explicit_current_handoff_semantics"] = _capture_e10d_stats(summary)
    summary["e14e_candidate"] = {
        "parent_gate": "E14",
        "comparison_anchor": "E14d_same_gpt_oss_settings",
        "change_class": "deterministic_explicit_current_handoff_semantics_refinement_only",
        "e14c_action_endpoint_canonicalization_preserved": True,
        "e14d_public_evidence_resource_canonicalization_preserved": True,
        "e10e_policy_changed": False,
        "e10g_policy_changed": False,
        "e11_policy_changed": False,
        "e14_selective_reprocess_policy_changed": False,
        "thresholds_changed": False,
        "prompt_changed": False,
        "model_changed": False,
        "reasoning_effort_changed": False,
        "completion_budget_changed": False,
        "scorer_changed": False,
        "acceptance_thresholds_changed": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "private_oracle_used_by_policy": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _base_sample() -> dict[str, Any]:
    return {
        "decision_class": "investigate_only",
        "evidence_plan": ["GET /assets/asset-selfcheck", "GET /knowledge/doc-selfcheck"],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Collect more public evidence before deciding.",
        "risk_notes": "Review risk, safety, and severity before action.",
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "needs_human_escalation": False,
            "action_endpoint": None,
            "calibration_reason": "Escalation context is documented for completeness.",
        },
    }


def run_self_checks() -> None:
    e14d.run_self_checks()

    bare = _base_sample()
    if refined_visible_guard_reason(bare) is not None:
        raise AssertionError("bare escalation/risk/safety/severity context must not trigger current handoff")

    negative = _base_sample()
    negative["action_escalation_rubric"]["calibration_reason"] = "Escalation is not required based on the current visible evidence."
    if refined_visible_guard_reason(negative) is not None:
        raise AssertionError("explicit negative handoff language must not trigger current handoff")

    conditional = _base_sample()
    conditional["proposed_next_step"] = "If severity increases, escalate to a specialist."
    if refined_visible_guard_reason(conditional) is not None:
        raise AssertionError("conditional handoff language must not become an immediate handoff")

    positive = _base_sample()
    positive["proposed_next_step"] = "Human review is required before proceeding."
    if refined_visible_guard_reason(positive) != "explicit_current_handoff_phrase":
        raise AssertionError("explicit positive current-handoff phrase must trigger refined fallback")

    already = _base_sample()
    already["requires_human_escalation"] = True
    if refined_visible_guard_reason(already) is not None:
        raise AssertionError("already-escalated output must remain unchanged")

    rubric_explicit = _base_sample()
    rubric_explicit["action_escalation_rubric"]["needs_human_escalation"] = True
    if refined_visible_guard_reason(rubric_explicit) != "rubric_needs_human_escalation_true":
        raise AssertionError("structured rubric handoff condition must be preserved")

    decision_explicit = _base_sample()
    decision_explicit["decision_class"] = "escalation_candidate"
    if refined_visible_guard_reason(decision_explicit) != "decision_class_escalation_candidate":
        raise AssertionError("escalation_candidate condition must be preserved")

    endpoint_explicit = _base_sample()
    endpoint_explicit["action_escalation_rubric"]["action_endpoint"] = "post /cases/{case_id}/escalate"
    if refined_visible_guard_reason(endpoint_explicit) != "specialist_or_case_escalate_endpoint":
        raise AssertionError("canonical case-escalate endpoint condition must be preserved")

    state_change = _base_sample()
    state_change["should_take_action_now"] = True
    state_change["action_escalation_rubric"]["needs_more_evidence"] = False
    state_change["action_escalation_rubric"]["safe_to_act"] = True
    state_change["action_escalation_rubric"]["action_endpoint"] = "post /analyses/{analysis_id}/reprocess"
    if refined_visible_guard_reason(state_change) != "state_changing_action_requires_visible_human_loop_guard":
        raise AssertionError("state-changing immediate action must retain human-loop E10d condition")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14E_MANIFEST)
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
    e10d_stats = summary.get("e14e_explicit_current_handoff_semantics", {})
    boundary = summary.get("selective_reprocess_authorization_boundary", {})
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
        "e10d_outputs_changed": e10d_stats.get("outputs_changed"),
        "explicit_current_handoff_phrase_outputs": e10d_stats.get("reason_counts", {}).get("explicit_current_handoff_phrase", 0),
        "state_changing_human_loop_outputs": e10d_stats.get("reason_counts", {}).get("state_changing_action_requires_visible_human_loop_guard", 0),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs"),
    }, indent=2))
    return 0 if summary["status"] == "E14E_DEV_ONLY_EXPLICIT_CURRENT_HANDOFF_SEMANTICS_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
