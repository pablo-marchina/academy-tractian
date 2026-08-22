#!/usr/bin/env python3
"""Oracle-free structural self-check for E14p epistemic serialization."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14p_public_epistemic_serialization_guard.py"
SPEC = importlib.util.spec_from_file_location("e14p_target", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14p target")
e14p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14p)


def main() -> int:
    output = {
        "decision_class": "action_candidate",
        "evidence_plan": [
            "GET /assets/asset-123 then GET /assets/asset-123/analyses because the bearing has failed.",
            "GET /analyses/analysis-456 and GET /assets/asset-123/data-quality to confirm the diagnosis.",
        ],
        "should_take_action_now": True,
        "requires_human_escalation": False,
        "proposed_next_step": "The bearing has failed, so reprocess analysis-456 now.",
        "risk_notes": "Severe failure is present.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": True,
            "action_endpoint": "POST /analyses/{analysisId}/reprocess",
            "needs_human_escalation": False,
            "calibration_reason": "The bearing is definitely failed.",
        },
    }

    before_decision = e14p._decision_signature(output)
    before_signatures = e14p._evidence_signatures(output)
    transformed, stats = e14p.serialize_output(output)
    after_decision = e14p._decision_signature(transformed)
    after_signatures = e14p._evidence_signatures(transformed)

    assert before_signatures == [
        "GET /assets/{assetId}",
        "GET /assets/{assetId}/analyses",
        "GET /analyses/{analysisId}",
        "GET /assets/{assetId}/data-quality",
    ]
    assert after_signatures == before_signatures
    assert stats["evidence_public_signature_loss"] == 0
    assert stats["evidence_public_signature_gain"] == 0
    assert stats["evidence_public_signature_order_changed"] == 0
    assert before_decision == after_decision
    assert transformed["action_escalation_rubric"]["action_endpoint"] == "POST /analyses/{analysisId}/reprocess"
    assert transformed["trace_quality_self_check"] == output["trace_quality_self_check"]

    rendered_blob = json.dumps({
        "evidence_plan": transformed["evidence_plan"],
        "proposed_next_step": transformed["proposed_next_step"],
        "risk_notes": transformed["risk_notes"],
        "calibration_reason": transformed["action_escalation_rubric"]["calibration_reason"],
    }).lower()
    assert "bearing" not in rendered_blob
    assert "definitely failed" not in rendered_blob
    assert "severe failure" not in rendered_blob
    assert "unobserved tool results" in rendered_blob
    assert "rubric metadata only" in rendered_blob
    assert "post /analyses/{analysisid}/reprocess" in rendered_blob

    print(json.dumps({
        "status": "E14P_PUBLIC_EPISTEMIC_SERIALIZATION_SELFCHECK_PASS",
        "decision_action_escalation_preserved": True,
        "action_endpoint_preserved": True,
        "evidence_signature_set_and_order_preserved": True,
        "synthetic_task_world_factual_prose_removed": True,
        "provider_calls_made": 0,
        "private_oracle_used": False,
        "validation_used": False,
        "locked_test_used": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
