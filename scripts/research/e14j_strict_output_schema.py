#!/usr/bin/env python3
"""Public strict JSON Schema for the existing E10b/E14 output contract.

This module formalizes the output shape already required by the public system
prompt. It does not encode private expected paths, evaluator labels, case IDs,
action answers, evidence answers, or benchmark-specific semantics.
"""

from __future__ import annotations

from typing import Any

SCHEMA_NAME = "tractian_dev_action_escalation_output"

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "decision_class": {
            "type": "string",
            "enum": [
                "investigate_only",
                "action_candidate",
                "escalation_candidate",
                "insufficient_evidence",
            ],
        },
        "evidence_plan": {
            "type": "array",
            "items": {"type": "string"},
        },
        "should_take_action_now": {"type": "boolean"},
        "requires_human_escalation": {"type": "boolean"},
        "proposed_next_step": {"type": "string"},
        "risk_notes": {"type": "string"},
        "trace_quality_self_check": {
            "type": "object",
            "properties": {
                "uses_only_visible_packet": {"type": "boolean"},
                "no_locked_test": {"type": "boolean"},
                "no_gold_claim": {"type": "boolean"},
            },
            "required": [
                "uses_only_visible_packet",
                "no_locked_test",
                "no_gold_claim",
            ],
            "additionalProperties": False,
        },
        "action_escalation_rubric": {
            "type": "object",
            "properties": {
                "needs_more_evidence": {"type": "boolean"},
                "safe_to_act": {"type": "boolean"},
                "action_endpoint": {"type": "string"},
                "needs_human_escalation": {"type": "boolean"},
                "calibration_reason": {"type": "string"},
            },
            "required": [
                "needs_more_evidence",
                "safe_to_act",
                "action_endpoint",
                "needs_human_escalation",
                "calibration_reason",
            ],
            "additionalProperties": False,
        },
    },
    "required": [
        "decision_class",
        "evidence_plan",
        "should_take_action_now",
        "requires_human_escalation",
        "proposed_next_step",
        "risk_notes",
        "trace_quality_self_check",
        "action_escalation_rubric",
    ],
    "additionalProperties": False,
}


def strict_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": SCHEMA_NAME,
            "strict": True,
            "schema": OUTPUT_SCHEMA,
        },
    }


def run_self_checks() -> None:
    root_properties = OUTPUT_SCHEMA.get("properties", {})
    root_required = set(OUTPUT_SCHEMA.get("required", []))
    if root_required != set(root_properties):
        raise AssertionError("strict root schema must require every declared field")
    if OUTPUT_SCHEMA.get("additionalProperties") is not False:
        raise AssertionError("strict root schema must be closed")

    for nested_name in ("trace_quality_self_check", "action_escalation_rubric"):
        nested = root_properties.get(nested_name, {})
        if set(nested.get("required", [])) != set(nested.get("properties", {})):
            raise AssertionError(f"strict nested schema must require every field: {nested_name}")
        if nested.get("additionalProperties") is not False:
            raise AssertionError(f"strict nested schema must be closed: {nested_name}")

    endpoint_schema = root_properties.get("action_escalation_rubric", {}).get("properties", {}).get("action_endpoint", {})
    if "enum" in endpoint_schema:
        raise AssertionError("E14j must not add endpoint semantic enumeration")


if __name__ == "__main__":
    run_self_checks()
