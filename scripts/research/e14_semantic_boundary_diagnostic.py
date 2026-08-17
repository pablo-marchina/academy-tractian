#!/usr/bin/env python3
"""Sanitized semantic/boundary diagnostic for real E14/E14b DEV captures.

Reads an already-existing private fixed-output capture and prints only aggregate
counts derived from model-visible/final fields and public boundary metadata.
It never prints parsed outputs, group-level rows, hashes, prompts, private paths,
provider raw errors, oracle data, expected paths, or evaluator labels.

Purpose: distinguish model decision/action collapse from deterministic post-model
boundary downgrades before creating another DEV-only candidate.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

PUBLIC_EVIDENCE_MARKERS = (
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

PUBLIC_ACTION_ENDPOINTS = {
    "post /analyses/{analysis_id}/reprocess",
    "post /analyses/{analysis_id}/request-specialist",
    "post /models/{model_id}/request-retraining",
    "patch /assets/{asset_id}",
    "post /cases/{case_id}/escalate",
    "none",
}

# These values are deterministic implementation reason codes, not model text or
# evaluator labels. Anything outside this public allowlist is collapsed to
# "other_public_reason" instead of being printed verbatim.
PUBLIC_BOUNDARY_REASON_CODES = {
    # E10d
    "rubric_needs_human_escalation_true",
    "decision_class_escalation_candidate",
    "specialist_or_case_escalate_endpoint",
    "visible_human_escalation_marker",
    "state_changing_action_requires_visible_human_loop_guard",
    # E10e
    "visible_rubric_needs_more_evidence",
    "visible_rubric_not_safe_to_act",
    "no_supported_action_endpoint_visible",
    "unsupported_action_endpoint_visible",
    "visible_text_mentions_insufficient_evidence_for_state_change",
    "too_few_concrete_evidence_resources_for_state_change",
    "decision_class_conflicts_with_state_changing_action",
    # E10g
    "balanced_guard_visible_rubric_needs_more_evidence",
    "balanced_guard_visible_rubric_not_safe_to_act",
    "balanced_guard_no_action_endpoint_visible",
    "balanced_guard_unsupported_action_endpoint",
    "balanced_guard_handoff_without_minimum_visible_evidence",
    "balanced_guard_decision_not_action_for_state_change",
    "balanced_guard_marginal_evidence_for_state_change",
    "balanced_guard_no_visible_action_support_for_state_change",
    "balanced_guard_uncertainty_without_strong_visible_support",
    "balanced_guard_state_change_without_human_escalation",
    # E11
    "no_parsed_output",
    "no_immediate_action_requested",
    "no_supported_endpoint_visible",
    "unsupported_endpoint",
    "missing_endpoint_required_evidence_family",
    "required_identifier_not_visible",
    "insufficient_independent_evidence_for_handoff",
    "authorized_human_handoff_review_path",
    "insufficient_independent_evidence_for_state_change",
    "state_change_without_independent_human_review_path",
    "authorized_state_change_with_independent_evidence_and_human_review",
}

BOUNDARY_SECTIONS = {
    "visible_escalation_consistency_guard": "e10d_escalation_consistency_guard",
    "visible_premature_action_safety_guard": "e10e_premature_action_guard",
    "visible_balanced_safety_action_guard": "e10g_balanced_action_guard",
    "independent_action_authorization_policy": "e11_independent_action_authorization",
    "selective_reprocess_authorization_boundary": "e14_selective_reprocess_boundary",
}

CONCRETE_ENDPOINT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("concrete_analysis_reprocess_path", re.compile(r"^post\s+/analyses/[^/\s]+/reprocess/?$")),
    ("concrete_analysis_request_specialist_path", re.compile(r"^post\s+/analyses/[^/\s]+/request-specialist/?$")),
    ("concrete_model_request_retraining_path", re.compile(r"^post\s+/models/[^/\s]+/request-retraining/?$")),
    ("concrete_asset_patch_path", re.compile(r"^patch\s+/assets/[^/\s]+/?$")),
    ("concrete_case_escalate_path", re.compile(r"^post\s+/cases/[^/\s]+/escalate/?$")),
)

ENDPOINT_LIKE_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("analysis_reprocess_like", ("/analyses/", "reprocess")),
    ("analysis_request_specialist_like", ("/analyses/", "request-specialist")),
    ("model_request_retraining_like", ("/models/", "request-retraining")),
    ("asset_patch_like", ("patch", "/assets/")),
    ("case_escalate_like", ("/cases/", "escalate")),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def number_summary(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 3),
    }


def safe_reason(value: Any) -> str:
    reason = str(value or "none").strip()
    if reason in PUBLIC_BOUNDARY_REASON_CODES or reason == "none":
        return reason
    return "other_public_reason"


def classify_unrecognized_endpoint_shape(value: Any) -> str:
    """Classify endpoint shape without printing concrete identifiers or raw text."""
    endpoint = normalize(value)
    for label, pattern in CONCRETE_ENDPOINT_PATTERNS:
        if pattern.fullmatch(endpoint):
            return label
    matched_like = [label for label, markers in ENDPOINT_LIKE_MARKERS if all(marker in endpoint for marker in markers)]
    if len(matched_like) > 1:
        return "multiple_supported_endpoint_shapes_in_one_value"
    if len(matched_like) == 1:
        return f"{matched_like[0]}_with_extra_or_noncanonical_text"
    return "other_unrecognized_shape"


def public_boundary_summary(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for source, label in BOUNDARY_SECTIONS.items():
        section = payload.get(source)
        if not isinstance(section, dict):
            continue
        result[label] = {
            "total_outputs_checked": int(section.get("total_outputs_checked") or 0),
            "outputs_changed": int(section.get("outputs_changed") or 0),
        }
        if source == "selective_reprocess_authorization_boundary":
            result[label].update(
                {
                    "target_reprocess_outputs_checked": int(section.get("target_reprocess_outputs_checked") or 0),
                    "authorized_target_reprocess_outputs": int(section.get("authorized_target_reprocess_outputs") or 0),
                    "blocked_target_reprocess_outputs": int(section.get("blocked_target_reprocess_outputs") or 0),
                }
            )
    return result


def summary_level_reason_counts(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for source, label in BOUNDARY_SECTIONS.items():
        section = payload.get(source)
        if not isinstance(section, dict):
            continue
        rows = section.get("rows")
        if not isinstance(rows, list):
            continue
        counts: Counter[str] = Counter()
        for row in rows:
            if not isinstance(row, dict):
                continue
            counts[safe_reason(row.get("reason"))] += 1
        if counts:
            result[label] = dict(sorted(counts.items()))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    payload = load_json(args.capture)
    if not isinstance(payload, dict):
        raise AssertionError("capture must be a JSON object")
    stage = payload.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []

    decision_counts: Counter[str] = Counter()
    endpoint_counts: Counter[str] = Counter()
    unrecognized_endpoint_shape_counts: Counter[str] = Counter()
    trace_counts: Counter[str] = Counter()
    embedded_applied_counts: Counter[str] = Counter()
    embedded_reason_counts: dict[str, Counter[str]] = {}
    evidence_resource_call_coverage: Counter[str] = Counter()
    evidence_plan_lengths: list[int] = []
    concrete_evidence_marker_counts: list[int] = []
    parsed_calls = 0
    action_now_true = 0
    human_escalation_true = 0
    safe_to_act_true = 0
    needs_more_evidence_true = 0
    action_endpoint_public = 0
    action_endpoint_unrecognized = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        for event in call.get("trace_events") or []:
            if isinstance(event, str):
                trace_counts[event] += 1

        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        parsed_calls += 1
        decision_counts[normalize(output.get("decision_class")) or "missing"] += 1
        action_now_true += int(output.get("should_take_action_now") is True)
        human_escalation_true += int(output.get("requires_human_escalation") is True)

        evidence_plan = output.get("evidence_plan")
        plan_items = evidence_plan if isinstance(evidence_plan, list) else []
        evidence_plan_lengths.append(len(plan_items))
        plan_text = "\n".join(str(x) for x in plan_items).lower()
        marker_hits = 0
        for marker in PUBLIC_EVIDENCE_MARKERS:
            if marker in plan_text:
                evidence_resource_call_coverage[marker] += 1
                marker_hits += 1
        concrete_evidence_marker_counts.append(marker_hits)

        rubric = output.get("action_escalation_rubric")
        if isinstance(rubric, dict):
            safe_to_act_true += int(rubric.get("safe_to_act") is True)
            needs_more_evidence_true += int(rubric.get("needs_more_evidence") is True)
            endpoint = normalize(rubric.get("action_endpoint")) or "none"
            if endpoint in PUBLIC_ACTION_ENDPOINTS:
                endpoint_counts[endpoint] += 1
                action_endpoint_public += 1
            else:
                endpoint_counts["unrecognized_or_missing"] += 1
                unrecognized_endpoint_shape_counts[classify_unrecognized_endpoint_shape(endpoint)] += 1
                action_endpoint_unrecognized += 1

        for key, value in output.items():
            if not isinstance(value, dict):
                continue
            lowered = str(key).lower()
            if not ("guard" in lowered or "authorization" in lowered or "boundary" in lowered):
                continue
            if value.get("applied") is True:
                embedded_applied_counts[str(key)] += 1
            reason_counter = embedded_reason_counts.setdefault(str(key), Counter())
            reason_counter[safe_reason(value.get("reason"))] += 1

    result = {
        "status": "E14_SANITIZED_SEMANTIC_BOUNDARY_DIAGNOSTIC",
        "total_calls": len(calls),
        "parsed_calls": parsed_calls,
        "final_output_distribution": {
            "decision_class_counts": dict(sorted(decision_counts.items())),
            "should_take_action_now_true": action_now_true,
            "requires_human_escalation_true": human_escalation_true,
            "safe_to_act_true": safe_to_act_true,
            "needs_more_evidence_true": needs_more_evidence_true,
            "public_action_endpoint_counts": dict(sorted(endpoint_counts.items())),
            "public_action_endpoint_values_counted": action_endpoint_public,
            "unrecognized_action_endpoint_values": action_endpoint_unrecognized,
            "unrecognized_endpoint_shape_counts": dict(sorted(unrecognized_endpoint_shape_counts.items())),
        },
        "evidence_plan_aggregates": {
            "plan_length": number_summary(evidence_plan_lengths),
            "concrete_public_resource_marker_count": number_summary(concrete_evidence_marker_counts),
            "calls_covering_each_public_resource": dict(sorted(evidence_resource_call_coverage.items())),
        },
        "summary_level_boundary_effects": public_boundary_summary(payload),
        "summary_level_boundary_reason_counts": summary_level_reason_counts(payload),
        "embedded_boundary_applied_counts": dict(sorted(embedded_applied_counts.items())),
        "embedded_boundary_reason_counts": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(embedded_reason_counts.items())
        },
        "selected_trace_event_counts": {
            key: value
            for key, value in sorted(trace_counts.items())
            if any(token in key for token in ("guard", "authorization", "selective_reprocess", "model_called", "output_parsed"))
        },
        "prints_private_outputs": False,
        "prints_group_level_rows": False,
        "prints_hashes": False,
        "prints_prompts": False,
        "prints_private_paths": False,
        "prints_oracle_data": False,
        "prints_evaluator_labels": False,
        "prints_unallowlisted_reason_text": False,
        "prints_concrete_endpoint_identifiers": False,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
