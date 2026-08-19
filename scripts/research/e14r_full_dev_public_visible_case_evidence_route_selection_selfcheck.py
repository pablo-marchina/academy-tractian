#!/usr/bin/env python3
"""Public synthetic self-check for E14r evidence-route selection."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14r_full_dev_public_visible_case_evidence_route_selection_guard.py"
SPEC = importlib.util.spec_from_file_location("e14r_under_test", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14r")
e14r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14r)


def base_output() -> dict:
    return {
        "decision_class": "investigate_only",
        "evidence_plan": [
            "GET /assets/{assetId} broad old plan",
            "GET /assets/{assetId}/rms broad old plan",
            "GET /knowledge/search broad old plan",
        ],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Continue evidence collection before any action.",
        "risk_notes": "No unsupported current-state claim is made.",
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
            "calibration_reason": "Visible evidence is not yet sufficient for action.",
        },
    }


def assert_only_evidence_changed(before: dict, after: dict) -> None:
    before_copy = copy.deepcopy(before)
    after_copy = copy.deepcopy(after)
    before_copy.pop("evidence_plan", None)
    after_copy.pop("evidence_plan", None)
    assert before_copy == after_copy


def main() -> int:
    # Generic investigation: no group/ticket-specific rule. Baseline/model cues
    # select only the public core + implicated public resources.
    output = base_output()
    case = {
        "mode": "investigate",
        "question": "Investigate a false positive after the baseline became invalid; check whether model behavior is implicated.",
    }
    transformed, meta = e14r.transform_output(output, case)
    selected, _ = e14r.selected_read_signatures(case, output)
    assert selected == [
        "GET /assets/{assetId}",
        "GET /assets/{assetId}/analyses",
        "GET /analyses/{analysisId}",
        "GET /assets/{assetId}/baseline",
        "GET /models/{modelId}",
    ]
    assert meta["non_evidence_preserved"] is True
    assert meta["exact_selected_routes"] is True
    assert meta["each_item_exactly_one_read"] is True
    assert meta["selected_read_count_within_cap"] is True
    assert_only_evidence_changed(output, transformed)

    # Contextualization switches the public core to knowledge retrieval and can
    # still add a public resource only when the visible case explicitly cues it.
    output2 = base_output()
    case2 = {
        "mode": "contextualize",
        "question": "Contextualize the procedure and source fidelity for baseline invalidation guidance.",
    }
    selected2, _ = e14r.selected_read_signatures(case2, output2)
    assert selected2 == [
        "GET /assets/{assetId}/baseline",
        "GET /knowledge/search",
        "GET /knowledge/{docId}",
    ]

    # Active public retraining action pulls authorization + target read even if
    # the visible text itself does not mention the model family.
    output3 = base_output()
    output3["decision_class"] = "action_candidate"
    output3["should_take_action_now"] = True
    output3["action_escalation_rubric"] = {
        "needs_more_evidence": False,
        "safe_to_act": True,
        "action_endpoint": "POST /models/{modelId}/request-retraining",
        "needs_human_escalation": False,
        "calibration_reason": "The already-fixed public action state authorizes the state change.",
    }
    case3 = {"mode": "investigate", "question": "Investigate the current asset state before the already-authorized next step."}
    selected3, _ = e14r.selected_read_signatures(case3, output3)
    assert "GET /users/me" in selected3
    assert "GET /models/{modelId}" in selected3
    transformed3, meta3 = e14r.transform_output(output3, case3)
    assert meta3["non_evidence_preserved"] is True
    assert_only_evidence_changed(output3, transformed3)

    # Broad cue coverage must remain bounded and must never introduce action
    # signatures into evidence_plan.
    output4 = base_output()
    case4 = {
        "mode": "investigate",
        "question": "Inspect baseline, data quality, RMS time series, spectrum frequency bands, model drift and knowledge guidance.",
    }
    selected4, _ = e14r.selected_read_signatures(case4, output4)
    assert len(selected4) <= e14r.MAX_SELECTED_READS
    transformed4, meta4 = e14r.transform_output(output4, case4)
    assert meta4["each_item_exactly_one_read"] is True
    assert all("POST " not in item and "PATCH " not in item for item in transformed4["evidence_plan"])

    # Explicitly forbidden public route families are not selected by this
    # preregistered intervention merely because company words appear.
    case5 = {"mode": "investigate", "question": "Review company and fleet context for this asset."}
    selected5, _ = e14r.selected_read_signatures(case5, base_output())
    assert "GET /companies/{companyId}" not in selected5
    assert "GET /companies/{companyId}/assets" not in selected5

    print("E14R_PUBLIC_SYNTHETIC_SELFCHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
