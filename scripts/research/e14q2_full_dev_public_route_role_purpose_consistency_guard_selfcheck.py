#!/usr/bin/env python3
"""Public synthetic self-check for E14q2. No benchmark/private inputs."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14q2_full_dev_public_route_role_purpose_consistency_guard.py"
SPEC = importlib.util.spec_from_file_location("e14q2_selfcheck_target", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14q2")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def output(
    *,
    decision: str,
    action_now: bool,
    escalation: bool,
    endpoint: str,
    proposed: str,
) -> dict:
    return {
        "decision_class": decision,
        "evidence_plan": [
            "GET /users/me",
            "GET /analyses/{analysisId}",
            "GET /assets/{assetId}",
        ],
        "should_take_action_now": action_now,
        "requires_human_escalation": escalation,
        "proposed_next_step": proposed,
        "risk_notes": "Proceed only under the public contract.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": not action_now,
            "safe_to_act": action_now,
            "needs_human_escalation": escalation,
            "action_endpoint": endpoint,
            "calibration_reason": "Public route-role consistency check.",
        },
    }


def assert_preserved(before: dict, after: dict) -> None:
    assert before["evidence_plan"] == after["evidence_plan"]
    assert before["proposed_next_step"] == after["proposed_next_step"]
    assert before["risk_notes"] == after["risk_notes"]
    assert before["action_escalation_rubric"]["calibration_reason"] == after["action_escalation_rubric"]["calibration_reason"]
    assert before["trace_quality_self_check"] == after["trace_quality_self_check"]


def main() -> int:
    valid_action = output(
        decision="action_candidate",
        action_now=True,
        escalation=False,
        endpoint="POST /analyses/{analysisId}/reprocess",
        proposed="Reprocess using POST /analyses/{analysisId}/reprocess after the public reads.",
    )
    guarded, meta = m.transform_output(valid_action)
    assert guarded == valid_action
    assert meta["failure_reason"] is None

    valid_handoff = output(
        decision="escalation_candidate",
        action_now=True,
        escalation=True,
        endpoint="POST /analyses/{analysisId}/request-specialist",
        proposed="Request specialist via POST /analyses/{analysisId}/request-specialist.",
    )
    guarded, meta = m.transform_output(valid_handoff)
    assert guarded == valid_handoff
    assert meta["failure_reason"] is None

    wrong_role = output(
        decision="action_candidate",
        action_now=True,
        escalation=True,
        endpoint="POST /analyses/{analysisId}/reprocess",
        proposed="Reprocess using POST /analyses/{analysisId}/reprocess.",
    )
    guarded, meta = m.transform_output(wrong_role)
    assert meta["failure_reason"] is not None
    assert guarded["should_take_action_now"] is False
    assert guarded["requires_human_escalation"] is False
    assert guarded["action_escalation_rubric"]["action_endpoint"] == "none"
    assert_preserved(wrong_role, guarded)

    conflict = output(
        decision="action_candidate",
        action_now=True,
        escalation=False,
        endpoint="POST /analyses/{analysisId}/reprocess",
        proposed="Request retraining with POST /models/{modelId}/request-retraining.",
    )
    guarded, meta = m.transform_output(conflict)
    assert meta["failure_reason"] == "endpoint_conflicts_with_explicit_free_text_action_signature"
    assert guarded["should_take_action_now"] is False
    assert guarded["action_escalation_rubric"]["action_endpoint"] == "none"
    assert_preserved(conflict, guarded)

    no_purpose = output(
        decision="action_candidate",
        action_now=True,
        escalation=False,
        endpoint="PATCH /assets/{assetId}",
        proposed="Proceed after the public reads.",
    )
    guarded, meta = m.transform_output(no_purpose)
    assert meta["failure_reason"] == "endpoint_family_lacks_explicit_public_intent_marker"
    assert guarded["should_take_action_now"] is False
    assert_preserved(no_purpose, guarded)

    prospective = output(
        decision="action_candidate",
        action_now=False,
        escalation=False,
        endpoint="none",
        proposed="Consider reprocessing later if evidence supports it.",
    )
    guarded, meta = m.transform_output(prospective)
    assert guarded == prospective
    assert meta["failure_reason"] is None

    print("E14Q2_PUBLIC_SYNTHETIC_SELFCHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
