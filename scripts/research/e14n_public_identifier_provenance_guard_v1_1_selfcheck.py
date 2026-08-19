#!/usr/bin/env python3
"""Oracle-free structural self-check for E14n v1.1 placeholder preservation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14n_public_identifier_provenance_guard_v1_1.py"
SPEC = importlib.util.spec_from_file_location("e14n_v11", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14n v1.1")
v11 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v11)
parent = v11.parent


def main() -> int:
    visible_case = {
        "asset_id": "asset-visible",
        "analysis_id": "analysis-visible",
    }
    output = {
        "decision_class": "investigate_only",
        "evidence_plan": [
            "GET /analyses/{analysis_id} then inspect analysis-hidden and analysis-hidden",
            "GET /assets/{asset_id} and retain asset-visible",
        ],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Use POST /cases/{case_id}/escalate only if later evidence supports it.",
        "risk_notes": "Do not infer a current fault from missing evidence.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "action_endpoint": "none",
            "needs_human_escalation": False,
            "calibration_reason": "Visible asset is asset-visible; analysis result remains unobserved.",
        },
    }

    before = parent.ground.audit_output(output, visible_case)
    _, stats_v1 = parent.sanitize_output(output, visible_case)
    # Parent v1 must exhibit the latent bug here: {case_id} is a public placeholder
    # but the synthetic visible case intentionally has no case_id key/value.
    assert int(stats_v1["unsupported_identifier_replacements"]) > int(before["unsupported_id_mentions"])

    original = parent._sanitize_text
    parent._sanitize_text = v11._sanitize_text_v1_1
    try:
        sanitized_v11, stats_v11 = parent.sanitize_output(output, visible_case)
    finally:
        parent._sanitize_text = original

    after = parent.ground.audit_output(sanitized_v11, visible_case)
    assert before["unsupported_id_mentions"] == 1
    assert stats_v11["unsupported_identifier_replacements"] == 1
    assert stats_v11["unsupported_identifier_replacement_occurrences"] == 2
    assert after["unsupported_id_mentions"] == 0
    assert parent._decision_signature(output) == parent._decision_signature(sanitized_v11)

    # Existing brace placeholders must remain literal; supported visible IDs remain literal.
    assert "{analysis_id}" in sanitized_v11["evidence_plan"][0]
    assert "{asset_id}" in sanitized_v11["evidence_plan"][1]
    assert "{case_id}" in sanitized_v11["proposed_next_step"]
    assert "asset-visible" in sanitized_v11["evidence_plan"][1]
    assert "asset-visible" in sanitized_v11["action_escalation_rubric"]["calibration_reason"]
    assert "analysis-hidden" not in sanitized_v11["evidence_plan"][0]

    print("E14n v1.1 placeholder-preservation self-check PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
