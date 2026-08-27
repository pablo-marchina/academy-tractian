#!/usr/bin/env python3
"""E12 hard-gate root-cause audit.

This is not a demo, not integration, not a new product and not a new guard.
It audits the E11 full DEV+VALIDATION capture instrumentation to determine
whether the independent action-authorization policy actually ran, how many
outputs it checked/changed, and which root-cause class best explains why the
full premature_action_rate remained above zero.

The audit must not read private expected paths, raw validation feedback,
evaluator labels, reference trajectories or LOCKED_TEST material. It may read a
local non-committed E11 full fixed capture file and an optional sanitized score
summary. It writes only sanitized aggregate diagnostics: no raw fixed parsed
outputs, no score rows, no output hashes, no private paths and no oracle values.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

FORBIDDEN_OUTPUT_KEYS = {
    "output_hash",
    "output_hash_after_policy",
    "fixed_output_file",
    "private_oracle_file_argument",
    "score_rows",
    "calls",
    "parsed_output",
    "raw_expected",
    "expected_paths",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nested_get(payload: Any, *keys: str, default: Any = None) -> Any:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default


def stage_keys(summary: dict[str, Any]) -> list[str]:
    return [
        key for key, value in summary.items()
        if isinstance(value, dict) and isinstance(value.get("calls"), list)
    ]


def collect_stage_policy_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in stage_keys(summary):
        stage = summary[key]
        policy = stage.get("independent_action_authorization_policy")
        if not isinstance(policy, dict):
            continue
        for row in policy.get("rows", []) if isinstance(policy.get("rows"), list) else []:
            if not isinstance(row, dict):
                continue
            rows.append({
                "stage_key": key,
                "split": str(row.get("split") or stage.get("split") or "UNKNOWN"),
                "authorized": bool(row.get("authorized")),
                "applied": bool(row.get("applied")),
                "reason": str(row.get("reason") or "unknown"),
                "action_class": str(row.get("action_class") or "unknown"),
                "endpoint": str(row.get("endpoint") or "unknown"),
                "evidence_family_count": len(row.get("evidence_families") or []) if isinstance(row.get("evidence_families"), list) else 0,
            })
    return rows


def collect_top_level_policy_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    policy = summary.get("independent_action_authorization_policy")
    if not isinstance(policy, dict):
        return []
    rows: list[dict[str, Any]] = []
    for row in policy.get("rows", []) if isinstance(policy.get("rows"), list) else []:
        if not isinstance(row, dict):
            continue
        rows.append({
            "split": str(row.get("split") or "UNKNOWN"),
            "authorized": bool(row.get("authorized")),
            "applied": bool(row.get("applied")),
            "reason": str(row.get("reason") or "unknown"),
            "action_class": str(row.get("action_class") or "unknown"),
            "endpoint": str(row.get("endpoint") or "unknown"),
            "evidence_family_count": len(row.get("evidence_families") or []) if isinstance(row.get("evidence_families"), list) else 0,
        })
    return rows


def collect_calls(summary: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for key in stage_keys(summary):
        stage = summary[key]
        for call in stage.get("calls", []):
            if isinstance(call, dict):
                calls.append(call)
    return calls


def count_by_split(rows: list[dict[str, Any]], field: str | None = None) -> dict[str, Any]:
    if field is None:
        counter = Counter(str(row.get("split") or "UNKNOWN") for row in rows)
        return dict(sorted(counter.items()))
    split_counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        split = str(row.get("split") or "UNKNOWN")
        split_counters[split][str(row.get(field) or "unknown")] += 1
    return {split: dict(counter.most_common()) for split, counter in sorted(split_counters.items())}


def summarize_policy(summary: dict[str, Any]) -> dict[str, Any]:
    top_policy = summary.get("independent_action_authorization_policy") if isinstance(summary.get("independent_action_authorization_policy"), dict) else {}
    stage_rows = collect_stage_policy_rows(summary)
    top_rows = collect_top_level_policy_rows(summary)
    rows = top_rows or stage_rows
    applied_rows = [row for row in rows if row.get("applied")]
    authorized_rows = [row for row in rows if row.get("authorized")]
    not_authorized_rows = [row for row in rows if not row.get("authorized")]

    calls = collect_calls(summary)
    split_call_counts = Counter(str(call.get("split") or "UNKNOWN") for call in calls)
    parsed_count = sum(1 for call in calls if isinstance(call.get("parsed_output"), dict))

    stage_policy_summary = {}
    for key in stage_keys(summary):
        policy = nested_get(summary, key, "independent_action_authorization_policy", default={})
        if not isinstance(policy, dict):
            stage_policy_summary[key] = {"policy_present": False}
            continue
        stage_policy_summary[key] = {
            "policy_present": True,
            "enabled": bool(policy.get("enabled")),
            "total_outputs_checked": int(policy.get("total_outputs_checked") or 0),
            "outputs_changed": int(policy.get("outputs_changed") or 0),
            "uses_private_oracle": bool(policy.get("uses_private_oracle")),
            "uses_validation_feedback": bool(policy.get("uses_validation_feedback")),
            "uses_locked_test": bool(policy.get("uses_locked_test")),
            "uses_model_safe_to_act_as_sufficient": bool(policy.get("uses_model_safe_to_act_as_sufficient")),
        }

    return {
        "top_level_policy_present": bool(top_policy),
        "top_level_policy_enabled": bool(top_policy.get("enabled")) if top_policy else False,
        "top_level_outputs_checked": int(top_policy.get("total_outputs_checked") or 0) if top_policy else 0,
        "top_level_outputs_changed": int(top_policy.get("outputs_changed") or 0) if top_policy else 0,
        "stage_policy_summary": stage_policy_summary,
        "rows_available_for_audit": len(rows),
        "rows_by_split": count_by_split(rows),
        "authorized_by_split": count_by_split(authorized_rows),
        "not_authorized_by_split": count_by_split(not_authorized_rows),
        "changed_by_split": count_by_split(applied_rows),
        "reason_counts_by_split": count_by_split(rows, "reason"),
        "action_class_counts_by_split": count_by_split(rows, "action_class"),
        "endpoint_counts_by_split": count_by_split(rows, "endpoint"),
        "evidence_family_count_distribution": dict(Counter(str(row.get("evidence_family_count", 0)) for row in rows).most_common()),
        "calls_by_split": dict(sorted(split_call_counts.items())),
        "parsed_outputs_available": parsed_count,
    }


def sanitized_score_context(score_summary: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(score_summary, dict):
        return {"provided": False}
    aggregate = score_summary.get("aggregate_metrics") if isinstance(score_summary.get("aggregate_metrics"), dict) else {}
    split_summary = score_summary.get("split_summary") if isinstance(score_summary.get("split_summary"), dict) else {}
    return {
        "provided": True,
        "aggregate_metrics": {
            "scoreable_calls": aggregate.get("scoreable_calls"),
            "real_task_quality": aggregate.get("real_task_quality"),
            "decision_correctness": aggregate.get("decision_correctness"),
            "evidence_correctness": aggregate.get("evidence_correctness"),
            "action_correctness": aggregate.get("action_correctness"),
            "escalation_correctness": aggregate.get("escalation_correctness"),
            "premature_action_rate": aggregate.get("premature_action_rate"),
            "unsupported_final_claim_rate": aggregate.get("unsupported_final_claim_rate"),
            "proxy_vs_real_disagreement_rate": aggregate.get("proxy_vs_real_disagreement_rate"),
        },
        "split_summary": split_summary,
    }


def derive_root_cause(capture: dict[str, Any], policy: dict[str, Any], score_context: dict[str, Any]) -> dict[str, Any]:
    total_calls = int(nested_get(capture, "aggregate_metrics", "total_calls", default=0) or 0)
    parsed = int(nested_get(capture, "aggregate_metrics", "parsed_model_outputs_available", default=0) or 0)
    top_checked = int(policy.get("top_level_outputs_checked") or 0)
    rows_available = int(policy.get("rows_available_for_audit") or 0)
    checked = max(top_checked, rows_available)
    changed = int(policy.get("top_level_outputs_changed") or 0)
    if changed == 0 and policy.get("changed_by_split"):
        changed = sum(int(v) for v in policy.get("changed_by_split", {}).values())

    agg = score_context.get("aggregate_metrics", {}) if isinstance(score_context.get("aggregate_metrics"), dict) else {}
    premature = agg.get("premature_action_rate")

    findings: list[str] = []
    root_cause_class = "undetermined_requires_local_audit_output"

    if checked == 0:
        root_cause_class = "policy_not_instrumented_or_metadata_missing"
        findings.append("No independent-action-authorization rows were found in the capture metadata.")
    elif total_calls and checked < total_calls:
        root_cause_class = "policy_partial_coverage"
        findings.append(f"Policy checked {checked} outputs while the capture reports {total_calls} total calls.")
    elif parsed and checked < parsed:
        root_cause_class = "policy_partial_parsed_output_coverage"
        findings.append(f"Policy checked {checked} outputs while {parsed} parsed outputs were available.")
    else:
        findings.append(f"Policy coverage appears complete: {checked} outputs checked.")

    if checked and changed == 0:
        findings.append("Policy executed but did not change any full output.")
        if premature not in (None, 0, 0.0):
            root_cause_class = "policy_executed_but_over_permissive_or_wrong_authorization_class"
            findings.append("Sanitized score context still reports premature_action_rate above 0.0, so the policy did not block the failing full behavior.")
        elif root_cause_class == "undetermined_requires_local_audit_output":
            root_cause_class = "policy_executed_without_interventions"
    elif changed > 0:
        findings.append(f"Policy changed {changed} outputs; if premature action persisted, the change may have targeted the wrong outputs/action class or insufficiently changed action semantics.")
        if premature not in (None, 0, 0.0):
            root_cause_class = "policy_intervened_but_failed_to_remove_premature_action"

    auth_by_split = policy.get("authorized_by_split", {}) if isinstance(policy.get("authorized_by_split"), dict) else {}
    changed_by_split = policy.get("changed_by_split", {}) if isinstance(policy.get("changed_by_split"), dict) else {}
    validation_authorized = int(auth_by_split.get("VALIDATION", 0) or 0)
    validation_changed = int(changed_by_split.get("VALIDATION", 0) or 0)
    if validation_authorized and validation_changed == 0 and premature not in (None, 0, 0.0):
        findings.append("VALIDATION outputs were authorized without intervention while the full premature-action rate remained above zero.")

    return {
        "root_cause_class": root_cause_class,
        "findings": findings,
        "next_design_allowed": False,
        "next_design_condition": "Only after reviewing this sanitized audit and preregistering a change that addresses the identified root-cause class without VALIDATION tuning.",
    }


def assert_no_forbidden_keys(payload: Any, path: str = "$", problems: list[str] | None = None) -> list[str]:
    if problems is None:
        problems = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_OUTPUT_KEYS:
                problems.append(f"{path}.{key}")
            assert_no_forbidden_keys(value, f"{path}.{key}", problems)
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            assert_no_forbidden_keys(item, f"{path}[{index}]", problems)
    return problems


def dry_run_capture() -> dict[str, Any]:
    rows = [
        {"split": "DEV", "authorized": True, "applied": False, "reason": "authorized_human_handoff_review_path", "action_class": "human_handoff_review_path", "endpoint": "post /cases/{case_id}/escalate", "evidence_families": ["asset", "case"]},
        {"split": "VALIDATION", "authorized": True, "applied": False, "reason": "authorized_state_change_with_independent_evidence_and_human_review", "action_class": "autonomous_state_change", "endpoint": "patch /assets/{asset_id}", "evidence_families": ["asset", "analysis", "knowledge"]},
    ]
    return {
        "status": "E11_FULL_DEV_VALIDATION_CAPTURE_PASS",
        "dry_run": True,
        "scope": {"measurement_splits": ["DEV", "VALIDATION"], "validation_used_for_tuning": False, "validation_ran": True, "locked_test_accessed": False},
        "aggregate_metrics": {"total_calls": 2, "parsed_model_outputs_available": 2},
        "independent_action_authorization_policy": {"enabled": True, "total_outputs_checked": 2, "outputs_changed": 0, "uses_private_oracle": False, "uses_validation_feedback": False, "uses_locked_test": False, "uses_model_safe_to_act_as_sufficient": False, "rows": rows},
        "dev_e11_full_remeasurement": {"split": "DEV", "calls": [{"split": "DEV", "parsed_output": {}}], "independent_action_authorization_policy": {"enabled": True, "total_outputs_checked": 1, "outputs_changed": 0, "uses_private_oracle": False, "uses_validation_feedback": False, "uses_locked_test": False, "uses_model_safe_to_act_as_sufficient": False, "rows": [rows[0]]}},
        "validation_e11_full_remeasurement": {"split": "VALIDATION", "calls": [{"split": "VALIDATION", "parsed_output": {}}], "independent_action_authorization_policy": {"enabled": True, "total_outputs_checked": 1, "outputs_changed": 0, "uses_private_oracle": False, "uses_validation_feedback": False, "uses_locked_test": False, "uses_model_safe_to_act_as_sufficient": False, "rows": [rows[1]]}},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e12-hard-gate-root-cause-audit-manifest.json"))
    parser.add_argument("--fixed-output-file", type=Path, default=None, help="Local non-committed E11 full capture JSON")
    parser.add_argument("--sanitized-score-summary", type=Path, default=None, help="Optional sanitized score summary JSON; never pass raw scorer rows here")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise AssertionError("manifest must be a JSON object")

    if args.dry_run:
        capture = dry_run_capture()
    else:
        if args.fixed_output_file is None:
            raise SystemExit("--fixed-output-file is required unless --dry-run is used")
        capture = load_json(args.fixed_output_file)
        if not isinstance(capture, dict):
            raise AssertionError("fixed output file must contain a JSON object")

    score_summary = None
    if args.sanitized_score_summary is not None:
        score_summary = load_json(args.sanitized_score_summary)
        if isinstance(score_summary, dict) and "score_rows" in score_summary:
            raise AssertionError("Refusing raw scorer rows. Provide a sanitized aggregate summary only.")

    policy_summary = summarize_policy(capture)
    score_context = sanitized_score_context(score_summary)
    root_cause = derive_root_cause(capture, policy_summary, score_context)

    audit = {
        "report_version": "e12-hard-gate-root-cause-audit-v1",
        "date": "2026-08-16",
        "status": "E12_HARD_GATE_ROOT_CAUSE_AUDIT_PASS" if policy_summary["top_level_policy_present"] or policy_summary["rows_available_for_audit"] else "E12_HARD_GATE_ROOT_CAUSE_AUDIT_NEEDS_REVIEW",
        "is_demo": False,
        "is_integration": False,
        "is_new_product": False,
        "is_new_guard": False,
        "scope": {
            "validation_used_for_tuning": False,
            "locked_test_accessed": bool(nested_get(capture, "scope", "locked_test_accessed", default=False)),
            "validation_ran": bool(nested_get(capture, "scope", "validation_ran", default=False)),
            "measurement_splits": nested_get(capture, "scope", "measurement_splits", default=[]),
            "final_architecture_freeze": False,
        },
        "policy_instrumentation_audit": policy_summary,
        "sanitized_score_context": score_context,
        "root_cause": root_cause,
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
            "next_candidate_allowed_now": False,
            "reason": "E12 is an audit gate only. A new candidate requires a preregistered change grounded in the audited root-cause class.",
        },
    }

    forbidden = assert_no_forbidden_keys(audit)
    if forbidden:
        raise AssertionError("Audit output contains forbidden keys: " + ", ".join(forbidden))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": audit["status"],
        "validation_ran": audit["scope"]["validation_ran"],
        "validation_used_for_tuning": audit["scope"]["validation_used_for_tuning"],
        "locked_test_accessed": audit["scope"]["locked_test_accessed"],
        "policy_outputs_checked": policy_summary.get("top_level_outputs_checked") or policy_summary.get("rows_available_for_audit"),
        "policy_outputs_changed": policy_summary.get("top_level_outputs_changed"),
        "root_cause_class": root_cause["root_cause_class"],
        "integration_allowed": False,
    }, indent=2))
    return 0 if audit["status"] == "E12_HARD_GATE_ROOT_CAUSE_AUDIT_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
