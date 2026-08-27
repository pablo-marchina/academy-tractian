#!/usr/bin/env python3
"""Oracle-free synthetic self-checks for the E9 v4.2 claim-packet builder."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
BUILDER_PATH = HERE / "e9_v4_2_semantic_claim_packet_builder.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_builder", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load v4.2 claim packet builder")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def run() -> dict[str, object]:
    segmented = builder.segment_claim_units(
        "The analysis is stale. If needed, GET /analyses/{analysisId}. Escalate only if risk is material; otherwise investigate."
    )
    if len(segmented) != 4:
        raise AssertionError(f"expected 4 deterministic sentence/clause units, got {len(segmented)}")

    output = {
        "decision_class": "investigate_only",
        "evidence_plan": [
            "GET /assets/{assetId} to inspect status. GET /assets/{assetId}/analyses to inspect analyses."
        ],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Inspect the visible case before acting.",
        "risk_notes": "No current severe condition is established.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "action_endpoint": "POST /analyses/{analysisId}/reprocess",
            "needs_human_escalation": False,
            "calibration_reason": "The visible case does not yet establish a safe state-changing action.",
        },
    }
    units = builder.build_claim_units(output)
    fields = [str(unit["source_field"]) for unit in units]
    texts = [str(unit["claim_text"]) for unit in units]

    if not units:
        raise AssertionError("claim packet builder returned zero units")
    if "evidence_plan[]" not in fields:
        raise AssertionError("evidence_plan must be included")
    if "proposed_next_step" not in fields or "risk_notes" not in fields:
        raise AssertionError("free-text output fields must be included")
    if "action_escalation_rubric.calibration_reason" not in fields:
        raise AssertionError("calibration_reason must be included")
    if any("reprocess" in text and text.startswith("POST") for text in texts):
        raise AssertionError("action_endpoint must not be independently injected as a semantic claim")
    if len(builder.v41.PUBLIC_TOOL_SPECS) != 18:
        raise AssertionError("public tool registry must remain the frozen 18-entry registry")

    return {
        "status": "E9_V4_2_SEMANTIC_CLAIM_PACKET_BUILDER_SELF_CHECK_PASS",
        "deterministic_segmentation": True,
        "semicolon_clause_split_verified": True,
        "all_preregistered_source_fields_included": True,
        "action_endpoint_excluded_as_independent_semantic_claim": True,
        "public_tool_registry_entries": len(builder.v41.PUBLIC_TOOL_SPECS),
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation": False,
        "uses_locked_test": False,
        "calls_semantic_judge": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
