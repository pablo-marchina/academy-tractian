#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14q_full_dev_public_action_authorization_consistency_guard.py"
SPEC = importlib.util.spec_from_file_location("e14q", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14q")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def base_output() -> dict:
    return {
        "decision_class": "action_candidate",
        "evidence_plan": [
            "GET /users/me to verify requester context",
            "GET /analyses/{analysisId} to inspect analysis evidence",
        ],
        "should_take_action_now": True,
        "requires_human_escalation": False,
        "proposed_next_step": "Proceed conditionally through the public action endpoint.",
        "risk_notes": "Proceed only under visible evidence and permission constraints.",
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
            "calibration_reason": "Action remains conditional on the listed public evidence reads.",
        },
    }


def check_authorized_action_preserved() -> None:
    source = base_output()
    guarded, meta = m.transform_output(source)
    assert guarded["should_take_action_now"] is True
    assert guarded["decision_class"] == "action_candidate"
    assert guarded["action_escalation_rubric"]["action_endpoint"] == "POST /analyses/{analysisId}/reprocess"
    assert meta["authorization_failure_reason"] is None
    assert meta["evidence_plan_preserved"] is True
    assert meta["free_text_and_trace_preserved"] is True


def check_missing_auth_read_demotes_and_clears() -> None:
    source = base_output()
    source["evidence_plan"] = ["GET /analyses/{analysisId} to inspect analysis evidence"]
    before_plan = list(source["evidence_plan"])
    before_text = m._output_free_text_signature(source)
    guarded, meta = m.transform_output(source)
    assert meta["authorization_failure_reason"] == "missing_users_me_authorization_read"
    assert guarded["should_take_action_now"] is False
    assert guarded["decision_class"] == "investigate_only"
    assert guarded["action_escalation_rubric"]["action_endpoint"] == "none"
    assert guarded["evidence_plan"] == before_plan
    assert m._output_free_text_signature(guarded) == before_text


def check_non_action_endpoint_is_cleared() -> None:
    source = base_output()
    source["should_take_action_now"] = False
    source["decision_class"] = "investigate_only"
    guarded, meta = m.transform_output(source)
    assert guarded["should_take_action_now"] is False
    assert guarded["action_escalation_rubric"]["action_endpoint"] == "none"
    assert meta["endpoint_cleared"] is True
    assert meta["evidence_plan_preserved"] is True
    assert meta["free_text_and_trace_preserved"] is True


def check_unsupported_escalation_flag_is_demoted() -> None:
    source = base_output()
    source["should_take_action_now"] = False
    source["decision_class"] = "escalation_candidate"
    source["requires_human_escalation"] = True
    source["action_escalation_rubric"]["action_endpoint"] = "none"
    source["risk_notes"] = "Uncertainty remains; collect more data before deciding."
    source["action_escalation_rubric"]["calibration_reason"] = "No explicit human-handling reason is visible."
    guarded, meta = m.transform_output(source)
    assert guarded["requires_human_escalation"] is False
    assert guarded["decision_class"] == "investigate_only"
    assert meta["escalation_demoted"] is True
    assert meta["free_text_and_trace_preserved"] is True


def check_supported_handoff_preserved() -> None:
    source = base_output()
    source["decision_class"] = "escalation_candidate"
    source["requires_human_escalation"] = True
    source["action_escalation_rubric"]["action_endpoint"] = "POST /analyses/{analysisId}/request-specialist"
    source["risk_notes"] = "Specialist review is required before further state change."
    guarded, meta = m.transform_output(source)
    assert guarded["should_take_action_now"] is True
    assert guarded["requires_human_escalation"] is True
    assert guarded["decision_class"] == "escalation_candidate"
    assert guarded["action_escalation_rubric"]["action_endpoint"] == "POST /analyses/{analysisId}/request-specialist"
    assert meta["authorization_failure_reason"] is None


def main() -> None:
    check_authorized_action_preserved()
    check_missing_auth_read_demotes_and_clears()
    check_non_action_endpoint_is_cleared()
    check_unsupported_escalation_flag_is_demoted()
    check_supported_handoff_preserved()
    print("E14Q_PUBLIC_ACTION_AUTHORIZATION_CONSISTENCY_SELFCHECK_PASS")


if __name__ == "__main__":
    main()
