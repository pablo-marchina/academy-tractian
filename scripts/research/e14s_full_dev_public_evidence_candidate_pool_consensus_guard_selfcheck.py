#!/usr/bin/env python3
"""Public synthetic self-checks for E14s. No provider or private benchmark data."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14s_full_dev_public_evidence_candidate_pool_consensus_guard.py"
SPEC = importlib.util.spec_from_file_location("e14s_under_test", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14s")
e14s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14s)


def base_output() -> dict:
    return {
        "decision_class": "investigate_only",
        "evidence_plan": [
            "GET /assets/{assetId}/baseline to inspect baseline context.",
            "GET /knowledge/search to find guidance.",
            "GET /assets/{assetId}/data-quality to inspect signal trustworthiness.",
            "GET /assets/{assetId}/spectrum to inspect frequency evidence.",
            "GET /users/me to inspect authorization context.",
            "GET /models/{modelId} to inspect model state.",
            "GET /knowledge/{docId} to inspect the selected guidance.",
        ],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Continue public evidence acquisition.",
        "risk_notes": "Do not act until the planned evidence is checked.",
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
            "calibration_reason": "Evidence collection remains necessary.",
        },
    }


def main() -> int:
    # Non-action case: E14r contributes its public core while the original plan
    # supplies additional candidates. Selection is capped at six and preserves
    # all non-evidence fields.
    original = base_output()
    visible = {"summary": "baseline and rms trend should be reviewed"}
    before_non_evidence = e14s._non_evidence_signature(original)
    transformed, meta = e14s.transform_output(copy.deepcopy(original), visible)
    selected = e14s._ordered_observed_reads(transformed)
    assert len(selected) <= e14s.MAX_SELECTED_READS == 6
    assert meta["non_evidence_preserved"] is True
    assert e14s._non_evidence_signature(transformed) == before_non_evidence
    assert meta["exact_selected_routes"] is True
    assert meta["each_item_exactly_one_read"] is True
    assert set(selected).issubset(
        set(e14s._ordered_observed_reads(original))
        | set(e14s.e14r.selected_read_signatures(visible, original)[0])
    )

    # Active action dependencies are highest priority and must survive the cap.
    active = base_output()
    active["decision_class"] = "action_candidate"
    active["should_take_action_now"] = True
    active["action_escalation_rubric"]["needs_more_evidence"] = False
    active["action_escalation_rubric"]["safe_to_act"] = True
    active["action_escalation_rubric"]["action_endpoint"] = "POST /models/{modelId}/request-retraining"
    active_visible = {"summary": "model drift and false positive behavior"}
    selected_active, _ = e14s.selected_read_signatures(active_visible, active)
    assert "GET /users/me" in selected_active
    assert "GET /models/{modelId}" in selected_active
    assert len(selected_active) <= 6

    # Consensus routes rank ahead of remaining E14r-only and original-only
    # candidates; no route can be synthesized outside the frozen union.
    consensus_case = {"summary": "baseline investigation"}
    consensus_output = base_output()
    selected_consensus, meta_consensus = e14s.selected_read_signatures(consensus_case, consensus_output)
    pool = set(e14s._ordered_observed_reads(consensus_output)) | set(
        e14s.e14r.selected_read_signatures(consensus_case, consensus_output)[0]
    )
    assert set(selected_consensus).issubset(pool)
    assert meta_consensus["candidate_pool_count"] == len(pool)

    print("E14S_PUBLIC_SYNTHETIC_SELFCHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
