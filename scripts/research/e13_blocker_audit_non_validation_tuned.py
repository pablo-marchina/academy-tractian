#!/usr/bin/env python3
"""E13 non-validation-tuned blocker audit.

This is an audit-only script. It does not create a new candidate, does not tune on
VALIDATION, and does not use private expected paths or scorer rows. It audits the
local non-committed E13 DEV-only capture to explain the DEV action collapse and
missing parsed output before any later preregistered change is allowed.

Do not commit non-dry-run captures, raw parsed outputs, output hashes, private
paths, private oracle values, raw scorer rows, or validation/LOCKED_TEST material.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EXPECTED_DEV_CALLS = 6


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_metric(summary: dict[str, Any], key: str, default: Any = None) -> Any:
    value = summary.get("aggregate_metrics", {}).get(key, default)
    return value


def synthetic_capture() -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    for group_id in ("asset_G501", "asset_C710", "asset_S420"):
        for repeat_index in (0, 1):
            boundary = {
                "is_target_reprocess_action": True,
                "authorized": False,
                "applied": True,
                "reason": "missing_endpoint_specific_reprocess_defect_evidence",
                "endpoint": "post /analyses/{analysis_id}/reprocess",
                "evidence_families": ["analysis", "asset", "baseline", "company", "data_quality", "rms", "spectrum"],
                "reprocess_defect_categories": [],
                "uses_private_oracle": False,
                "uses_validation_feedback": False,
                "uses_locked_test": False,
            }
            output: dict[str, Any] | None = {
                "should_take_action_now": False,
                "requires_human_escalation": True,
                "decision_class": "investigate_only",
                "action_escalation_rubric": {"action_endpoint": "post /analyses/{analysis_id}/reprocess"},
                "reprocess_specific_authorization_boundary": boundary,
            }
            if group_id == "asset_S420" and repeat_index == 0:
                output = None
            calls.append(
                {
                    "group_id": group_id,
                    "split": "DEV",
                    "repeat_index": repeat_index,
                    "parsed_output": output,
                    "error": None if output is not None else "parsed_model_output_missing",
                    "trace_events": ["reprocess_specific_authorization_boundary_blocked"] if output else [],
                    "trace_complete": output is not None,
                }
            )
    return {
        "report_version": "synthetic-e13-dev-only-capture-for-audit-ci",
        "status": "SYNTHETIC_E13_CAPTURE_FOR_AUDIT_DRY_RUN",
        "dry_run": True,
        "scope": {"measurement_splits": ["DEV"], "validation_used_for_tuning": False, "locked_test_accessed": False},
        "dev_action_escalation_calibration": {"calls": calls},
        "reprocess_specific_authorization_boundary": {"enabled": True, "total_outputs_checked": 5, "outputs_changed": 5},
    }


def collect_calls(capture: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for key, value in capture.items():
        if isinstance(value, dict) and isinstance(value.get("calls"), list):
            calls.extend(call for call in value["calls"] if isinstance(call, dict))
    if not calls and isinstance(capture.get("calls"), list):
        calls.extend(call for call in capture["calls"] if isinstance(call, dict))
    return calls


def output_boundary(call: dict[str, Any]) -> dict[str, Any] | None:
    output = call.get("parsed_output")
    if isinstance(output, dict):
        boundary = output.get("reprocess_specific_authorization_boundary")
        if isinstance(boundary, dict):
            return boundary
    boundary = call.get("reprocess_specific_authorization_boundary")
    return boundary if isinstance(boundary, dict) else None


def sanitized_call_id(call: dict[str, Any]) -> dict[str, Any]:
    return {
        "group_id": call.get("group_id"),
        "split": call.get("split"),
        "repeat_index": call.get("repeat_index"),
    }


def counter_to_plain(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in counter.items()}


def nested_counter_to_plain(counter: dict[str, Counter[Any]]) -> dict[str, dict[str, int]]:
    return {str(key): counter_to_plain(value) for key, value in counter.items()}


def audit_capture(capture: dict[str, Any], sanitized_score: dict[str, Any] | None, manifest: dict[str, Any]) -> dict[str, Any]:
    calls = collect_calls(capture)
    dev_calls = [call for call in calls if str(call.get("split", "DEV")).upper() == "DEV"]
    validation_like_calls = [call for call in calls if str(call.get("split", "")).upper() == "VALIDATION"]
    locked_like_calls = [call for call in calls if str(call.get("split", "")).upper() == "LOCKED_TEST"]

    parsed_calls = [call for call in dev_calls if isinstance(call.get("parsed_output"), dict)]
    missing_parsed = [sanitized_call_id(call) for call in dev_calls if not isinstance(call.get("parsed_output"), dict)]

    boundary_rows: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    endpoint_counts: Counter[str] = Counter()
    group_applied: dict[str, Counter[str]] = defaultdict(Counter)
    group_reasons: dict[str, Counter[str]] = defaultdict(Counter)
    defect_counts: Counter[str] = Counter()
    trace_event_counts: Counter[str] = Counter()

    for call in dev_calls:
        for event in call.get("trace_events", []) if isinstance(call.get("trace_events"), list) else []:
            trace_event_counts[str(event)] += 1
        boundary = output_boundary(call)
        if boundary is None:
            boundary_rows.append({**sanitized_call_id(call), "boundary_present": False})
            continue
        reason = str(boundary.get("reason"))
        endpoint = str(boundary.get("endpoint") or boundary.get("target_endpoint") or "unknown")
        applied = bool(boundary.get("applied"))
        authorized = boundary.get("authorized")
        target = bool(boundary.get("is_target_reprocess_action"))
        defects = boundary.get("reprocess_defect_categories") if isinstance(boundary.get("reprocess_defect_categories"), list) else []
        for defect in defects:
            defect_counts[str(defect)] += 1
        reason_counts[reason] += 1
        endpoint_counts[endpoint] += 1
        group_id = str(call.get("group_id"))
        group_applied[group_id]["applied" if applied else "not_applied"] += 1
        group_reasons[group_id][reason] += 1
        boundary_rows.append(
            {
                **sanitized_call_id(call),
                "boundary_present": True,
                "is_target_reprocess_action": target,
                "authorized": authorized,
                "applied": applied,
                "reason": reason,
                "endpoint": endpoint,
                "evidence_family_count": len(boundary.get("evidence_families") or []),
                "reprocess_defect_category_count": len(defects),
            }
        )

    rows_with_boundary = [row for row in boundary_rows if row.get("boundary_present")]
    target_rows = [row for row in rows_with_boundary if row.get("is_target_reprocess_action")]
    changed_rows = [row for row in rows_with_boundary if row.get("applied")]
    authorized_rows = [row for row in rows_with_boundary if row.get("authorized") is True]
    blocked_rows = [row for row in rows_with_boundary if row.get("authorized") is False]

    agg = sanitized_score.get("aggregate_metrics", {}) if isinstance(sanitized_score, dict) else {}
    score_context = {
        "provided": isinstance(sanitized_score, dict),
        "scoreable_calls": agg.get("scoreable_calls"),
        "parsed_model_outputs_available": sanitized_score.get("inputs", {}).get("parsed_model_outputs_available") if isinstance(sanitized_score, dict) else None,
        "real_task_quality": agg.get("real_task_quality"),
        "decision_correctness": agg.get("decision_correctness"),
        "evidence_correctness": agg.get("evidence_correctness"),
        "action_correctness": agg.get("action_correctness"),
        "escalation_correctness": agg.get("escalation_correctness"),
        "premature_action_rate": agg.get("premature_action_rate"),
        "unsupported_final_claim_rate": agg.get("unsupported_final_claim_rate"),
        "proxy_vs_real_disagreement_rate": agg.get("proxy_vs_real_disagreement_rate"),
    }

    root_causes: list[str] = []
    if missing_parsed:
        root_causes.append("parsed_output_missing_in_dev_capture")
    if target_rows and changed_rows and len(changed_rows) == len(target_rows):
        root_causes.append("boundary_changed_all_target_reprocess_actions")
    if score_context.get("action_correctness") == 0.0 and changed_rows:
        root_causes.append("action_collapse_consistent_with_overblocking_reprocess_boundary")
    if score_context.get("decision_correctness") is not None and float(score_context["decision_correctness"]) < 0.75:
        root_causes.append("decision_regression_after_reprocess_downgrade")
    if not root_causes:
        root_causes.append("root_cause_not_identified_from_sanitized_audit")

    findings: list[str] = []
    findings.append(f"DEV calls observed: {len(dev_calls)}; parsed DEV outputs: {len(parsed_calls)}.")
    if missing_parsed:
        findings.append("At least one DEV call has no parsed output, so E13 failed the completeness prerequisite before quality metrics are considered.")
    findings.append(f"Boundary rows present: {len(rows_with_boundary)}; target reprocess rows: {len(target_rows)}; changed rows: {len(changed_rows)}.")
    if target_rows and len(changed_rows) == len(target_rows):
        findings.append("The boundary appears to have downgraded every detected target reprocess action, which is consistent with action collapse.")
    if reason_counts:
        findings.append("Dominant public/sanitized boundary reasons: " + ", ".join(f"{k}={v}" for k, v in reason_counts.most_common(5)) + ".")
    if score_context.get("action_correctness") == 0.0:
        findings.append("Sanitized score context reports action_correctness = 0.0, so E13 overcorrected on DEV and cannot advance to full measurement.")

    return {
        "report_version": "e13-blocker-audit-non-validation-tuned-v1",
        "date": manifest.get("date", "2026-08-16"),
        "status": "E13_BLOCKER_AUDIT_PASS",
        "is_demo": False,
        "is_integration": False,
        "is_new_product": False,
        "is_new_guard": False,
        "is_next_candidate": False,
        "scope": {
            "allowed_splits": ["DEV"],
            "validation_used_for_tuning": False,
            "validation_calls_read": len(validation_like_calls),
            "locked_test_accessed": bool(locked_like_calls),
            "locked_test_calls_read": len(locked_like_calls),
            "final_architecture_freeze": False,
        },
        "capture_audit": {
            "dev_calls_observed": len(dev_calls),
            "expected_dev_calls": EXPECTED_DEV_CALLS,
            "parsed_dev_outputs_available": len(parsed_calls),
            "missing_parsed_output_count": len(missing_parsed),
            "missing_parsed_output_call_ids": missing_parsed,
            "boundary_rows_available": len(rows_with_boundary),
            "target_reprocess_rows": len(target_rows),
            "authorized_rows": len(authorized_rows),
            "blocked_rows": len(blocked_rows),
            "changed_rows": len(changed_rows),
            "unchanged_rows": len(rows_with_boundary) - len(changed_rows),
            "reason_counts": counter_to_plain(reason_counts),
            "endpoint_counts": counter_to_plain(endpoint_counts),
            "defect_category_counts": counter_to_plain(defect_counts),
            "applied_counts_by_group": nested_counter_to_plain(group_applied),
            "reason_counts_by_group": nested_counter_to_plain(group_reasons),
            "trace_event_counts": counter_to_plain(trace_event_counts),
        },
        "sanitized_score_context": score_context,
        "root_cause": {
            "root_cause_classes": root_causes,
            "findings": findings,
            "next_candidate_allowed_now": False,
            "next_candidate_condition": "Only after this audit is reviewed and a later change is preregistered without VALIDATION tuning.",
        },
        "sanitization": {
            "raw_fixed_outputs_committed": False,
            "score_rows_committed": False,
            "output_hashes_committed": False,
            "private_paths_committed": False,
            "private_oracle_values_committed": False,
            "validation_feedback_used_for_tuning": False,
            "locked_test_material_used": False,
        },
        "gate_decision": {
            "integration_allowed": False,
            "demo_allowed": False,
            "full_rerun_allowed": False,
            "next_candidate_allowed_now": False,
            "reason": "E13 DEV-only failed; this audit is diagnostic only and does not authorize a next candidate.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e13-blocker-audit-non-validation-tuned-manifest.json"))
    parser.add_argument("--fixed-output-file", type=Path, default=None, help="Local non-committed E13 DEV-only capture file")
    parser.add_argument("--sanitized-score-summary", type=Path, default=None, help="Optional sanitized E13 score summary committed in repo")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    if args.dry_run:
        capture = synthetic_capture()
    else:
        if args.fixed_output_file is None:
            raise SystemExit("--fixed-output-file is required outside --dry-run")
        capture = load_json(args.fixed_output_file)

    sanitized_score = None
    if args.sanitized_score_summary is not None and args.sanitized_score_summary.exists():
        sanitized_score = load_json(args.sanitized_score_summary)

    report = audit_capture(capture, sanitized_score, manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "validation_used_for_tuning": report["scope"]["validation_used_for_tuning"],
        "validation_calls_read": report["scope"]["validation_calls_read"],
        "locked_test_accessed": report["scope"]["locked_test_accessed"],
        "dev_calls_observed": report["capture_audit"]["dev_calls_observed"],
        "parsed_dev_outputs_available": report["capture_audit"]["parsed_dev_outputs_available"],
        "missing_parsed_output_count": report["capture_audit"]["missing_parsed_output_count"],
        "target_reprocess_rows": report["capture_audit"]["target_reprocess_rows"],
        "changed_rows": report["capture_audit"]["changed_rows"],
        "root_cause_classes": report["root_cause"]["root_cause_classes"],
        "integration_allowed": report["gate_decision"]["integration_allowed"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
