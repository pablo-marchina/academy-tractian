#!/usr/bin/env python3
"""Sanitized E14d diagnostic for E10d escalation-marker polarity and field location.

Reads an already-fixed E14d DEV capture. It only inspects calls whose embedded
E10d reason is `visible_human_escalation_marker` and reports aggregate counts of
public schema fields containing allowlisted escalation/risk markers plus
allowlisted positive, negative, or conditional handoff phrase classes.

It does not read private oracle/scorer data and never prints parsed output text,
group IDs, concrete resource identifiers, hashes, prompts, private paths,
evaluator labels, or evidence-plan text.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

TARGET_REASON = "visible_human_escalation_marker"

FIELDS = (
    "proposed_next_step",
    "risk_notes",
    "evidence_plan",
    "action_escalation_rubric.calibration_reason",
)

# Narrow signals of a current human handoff requirement. These are deliberately
# stronger than E10d's historical single-token marker test.
POSITIVE_HANDOFF_PATTERNS = (
    r"\brequires?\s+(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bneeds?\s+(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bescalate\s+(?:to|this|the)\b",
    r"\broute\s+(?:this\s+)?to\s+(?:a\s+)?(?:human|specialist|engineer)\b",
    r"\b(?:human|specialist|engineering)\s+review\s+(?:is\s+)?required\b",
    r"\bapproval\s+(?:is\s+)?required\b",
    r"\bobtain\s+(?:human\s+)?approval\b",
    r"\brequest\s+(?:a\s+)?specialist\b",
    r"\brequer\s+(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
    r"\bnecessita\s+(?:de\s+)?(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
    r"\bescalar\s+para\b",
    r"\brevis[aã]o\s+humana\s+(?:é\s+)?necess[aá]ria\b",
)

NEGATIVE_HANDOFF_PATTERNS = (
    r"\bno\s+(?:human\s+)?escalation\b",
    r"\bwithout\s+(?:human\s+)?escalation\b",
    r"\bdoes\s+not\s+require\s+(?:human\s+)?escalation\b",
    r"\bdoesn't\s+require\s+(?:human\s+)?escalation\b",
    r"\bescalation\s+(?:is\s+)?not\s+required\b",
    r"\bno\s+(?:human|specialist|engineering)\s+review\b",
    r"\b(?:human|specialist|engineering)\s+review\s+(?:is\s+)?not\s+required\b",
    r"\bno\s+approval\b",
    r"\bapproval\s+(?:is\s+)?not\s+required\b",
    r"\bn[aã]o\s+(?:requer|necessita\s+de)\s+escalonamento\b",
    r"\bsem\s+necessidade\s+de\s+escalonamento\b",
    r"\bescalonamento\s+n[aã]o\s+(?:é\s+)?necess[aá]rio\b",
)

CONDITIONAL_HANDOFF_PATTERNS = (
    r"\bif\b[^.\n]{0,100}\bescalat(?:e|ion)\b",
    r"\bescalat(?:e|ion)\b[^.\n]{0,100}\bif\b",
    r"\bconsider\s+(?:human\s+)?escalation\b",
    r"\bmay\s+require\s+(?:human\s+)?escalation\b",
    r"\bmight\s+require\s+(?:human\s+)?escalation\b",
    r"\bse\b[^.\n]{0,100}\bescalar\b",
    r"\bconsiderar\s+escalonamento\b",
)

GENERIC_RISK_MARKERS = ("risk", "safety", "severity", "severe", "critical", "high impact")
EXPLICIT_HANDOFF_TOKENS = ("escalation", "escalate", "human", "specialist", "approval", "engineering review")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_guard_added_text(output: dict[str, Any]) -> dict[str, Any]:
    cleaned = copy.deepcopy(output)
    for key in list(cleaned):
        lowered = str(key).lower()
        if "guard" in lowered or "authorization" in lowered or "boundary" in lowered:
            cleaned.pop(key, None)

    risk = str(cleaned.get("risk_notes", "") or "")
    for token in (
        " Visible-output escalation consistency guard applied:",
        " Visible-output premature-action safety guard applied:",
        " E10g balanced visible-output safety guard applied:",
        " E14 blocked autonomous reprocess:",
    ):
        if token in risk:
            risk = risk.split(token, 1)[0]
    cleaned["risk_notes"] = risk

    proposed = str(cleaned.get("proposed_next_step", "") or "")
    for token in (
        " Do not execute a state-changing maintenance action yet; collect the missing visible evidence or obtain human review before action.",
        " Do not execute the state-changing maintenance action yet; collect stronger concrete evidence or route to human review before action.",
        " E14 selective reprocess authorization did not approve immediate reprocess;",
    ):
        if token in proposed:
            proposed = proposed.split(token, 1)[0]
    cleaned["proposed_next_step"] = proposed

    rubric = cleaned.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        calibration = str(rubric.get("calibration_reason", "") or "")
        for token in (
            " Visible guard reason:",
            " Safety guard reason:",
            " Balanced safety guard reason:",
            " E14 selective reprocess reason:",
        ):
            if token in calibration:
                calibration = calibration.split(token, 1)[0]
        rubric["calibration_reason"] = calibration
    return cleaned


def field_text(output: dict[str, Any], field: str) -> str:
    if field == "action_escalation_rubric.calibration_reason":
        rubric = output.get("action_escalation_rubric")
        value = rubric.get("calibration_reason") if isinstance(rubric, dict) else ""
    else:
        value = output.get(field)
    if isinstance(value, list):
        return "\n".join(str(item) for item in value).lower()
    return str(value or "").lower()


def any_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    payload = load_json(args.capture)
    if not isinstance(payload, dict):
        raise AssertionError("capture must be a JSON object")
    stage = payload.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []

    target_calls = 0
    escalation_token_fields: Counter[str] = Counter()
    generic_risk_fields: Counter[str] = Counter()
    positive_fields: Counter[str] = Counter()
    negative_fields: Counter[str] = Counter()
    conditional_fields: Counter[str] = Counter()
    calls_with_positive = 0
    calls_with_negative = 0
    calls_with_conditional = 0
    calls_with_only_bare_or_generic_marker_context = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guard = output.get("visible_escalation_consistency_guard")
        if not isinstance(guard, dict) or str(guard.get("reason") or "") != TARGET_REASON:
            continue

        target_calls += 1
        cleaned = strip_guard_added_text(output)
        call_positive = False
        call_negative = False
        call_conditional = False

        for field in FIELDS:
            text = field_text(cleaned, field)
            if not text:
                continue
            if any(token in text for token in EXPLICIT_HANDOFF_TOKENS):
                escalation_token_fields[field] += 1
            if any(token in text for token in GENERIC_RISK_MARKERS):
                generic_risk_fields[field] += 1
            if any_pattern(text, POSITIVE_HANDOFF_PATTERNS):
                positive_fields[field] += 1
                call_positive = True
            if any_pattern(text, NEGATIVE_HANDOFF_PATTERNS):
                negative_fields[field] += 1
                call_negative = True
            if any_pattern(text, CONDITIONAL_HANDOFF_PATTERNS):
                conditional_fields[field] += 1
                call_conditional = True

        calls_with_positive += int(call_positive)
        calls_with_negative += int(call_negative)
        calls_with_conditional += int(call_conditional)
        if not call_positive and not call_negative and not call_conditional:
            calls_with_only_bare_or_generic_marker_context += 1

    result = {
        "status": "E14D_SANITIZED_E10D_ESCALATION_MARKER_POLARITY_DIAGNOSTIC",
        "total_calls": len(calls),
        "target_visible_human_escalation_marker_calls": target_calls,
        "field_location_counts": {
            "explicit_handoff_token_present": dict(sorted(escalation_token_fields.items())),
            "generic_risk_marker_present": dict(sorted(generic_risk_fields.items())),
        },
        "handoff_phrase_class_counts": {
            "calls_with_explicit_positive_current_handoff_phrase": calls_with_positive,
            "calls_with_explicit_negative_handoff_phrase": calls_with_negative,
            "calls_with_conditional_or_contingent_handoff_phrase": calls_with_conditional,
            "calls_with_only_bare_or_generic_marker_context": calls_with_only_bare_or_generic_marker_context,
        },
        "handoff_phrase_field_counts": {
            "positive": dict(sorted(positive_fields.items())),
            "negative": dict(sorted(negative_fields.items())),
            "conditional": dict(sorted(conditional_fields.items())),
        },
        "known_pre_e10d_contract_for_target_reason": {
            "requires_human_escalation_true": False,
            "rubric_needs_human_escalation_true": False,
            "decision_class_escalation_candidate": False,
            "specialist_or_case_escalate_endpoint_selected": False,
            "reason_reached_only_after_stronger_e10d_conditions_were_false": True,
        },
        "interpretation_contract": {
            "positive_phrase_is_stronger_than_single_marker_substring": True,
            "negative_or_conditional_phrase_is_not_automatic_current_handoff_authorization": True,
            "bare_generic_risk_marker_is_not_automatic_current_handoff_authorization": True,
            "diagnostic_changes_policy": False,
        },
        "prints_private_outputs": False,
        "prints_group_level_rows": False,
        "prints_hashes": False,
        "prints_prompts": False,
        "prints_private_paths": False,
        "prints_oracle_data": False,
        "prints_evaluator_labels": False,
        "prints_concrete_resource_identifiers": False,
        "prints_evidence_plan_text": False,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
