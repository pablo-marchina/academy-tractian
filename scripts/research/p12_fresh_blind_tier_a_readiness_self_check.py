#!/usr/bin/env python3
"""Provider-free, outcome-blind readiness check for the P12 FRESH_BLIND Tier A handoff."""
from __future__ import annotations

import json
from pathlib import Path

REGISTRY = Path("research/frozen/big-b4-blind-source-registry-v1.json")
PACKET = Path("research/experiments/p12-fresh-blind-tier-a-readiness-packet-v1.json")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    r = load(REGISTRY)
    p = load(PACKET)
    assert r["schema_version"] == "big-b4-blind-source-registry-v1"
    assert r["authorization_state"] == "NO_BLIND_SOURCE_AUTHORIZED"
    assert r["authorized_sources"] == []
    assert r["default_fail_closed"] is True
    assert p["schema_version"] == "p12-fresh-blind-tier-a-readiness-packet-v1"
    assert p["protocol_id"] == r["protocol_id"]
    assert p["status"] == "READY_FOR_EXTERNAL_ATTESTATION_NO_SOURCE_AUTHORIZED"
    assert p["planning_tier"] == r["active_planning_tier"]
    assert p["tier_a_cutoff"] == r["tier_a_cutoff"]
    assert p["tier_b_cutoff"] == r["tier_b_cutoff"]
    assert p["source_authorization_state"] == "NO_BLIND_SOURCE_AUTHORIZED"
    assert p["source_id"] is None
    assert p["hidden_case_content_committed"] is False
    assert p["expected_outcomes_committed"] is False
    assert p["developer_hidden_semantic_access"] is False
    assert p["candidate_generation_frozen"] is False
    assert p["final_measurement_authorized"] is False
    assert p["authorization"] == {
        "source_registration": False,
        "hidden_content_access": False,
        "fresh_blind_candidate_execution": False,
        "fresh_blind_private_scoring": False,
        "adaptive_feedback": False,
    }
    handoff = p["custodian_handoff_contract"]
    assert handoff["iterative_partial_feedback_allowed"] is False
    forbidden = set(handoff["developer_must_not_receive_before_generation_freeze"])
    for required in ("hidden_case_content", "expected_paths", "labels", "scores", "partial_results", "candidate_specific_feedback"):
        assert required in forbidden
    required_record_fields = set(r["required_source_record_fields"])
    attestation = p["external_attestation_required"]
    represented = {
        "source_id", "tier", "custodian_identity_or_role", "author_identity_or_role",
        "adjudicator_identity_or_role", "author_isolated_from_candidate_development",
        "adjudicator_isolated_from_candidate_development",
        "developer_cannot_access_hidden_semantics_before_freeze", "no_iterative_partial_feedback",
        "asset_story_group_independence_confirmed", "group_count", "modality_coverage",
        "safety_critical_coverage", "provenance_record", "custody_start",
        "expected_measurement_window", "breach_state"
    }
    assert represented == required_record_fields
    assert attestation["independence"]["author_isolated_from_candidate_development"] is True
    assert attestation["independence"]["adjudicator_isolated_from_candidate_development"] is True
    assert attestation["independence"]["developer_cannot_access_hidden_semantics_before_freeze"] is True
    assert attestation["independence"]["no_iterative_partial_feedback"] is True
    evidence = {
        "schema_version": "p12-fresh-blind-tier-a-readiness-self-check-v1",
        "status": "PASS",
        "source_authorized": False,
        "hidden_content_accesses": 0,
        "expected_outcome_accesses": 0,
        "candidate_outputs_read": 0,
        "adaptive_feedback_events": 0,
        "tier_a_handoff_ready_for_external_attestation": True,
        "next_gate": "EXTERNAL_TIER_A_ATTESTATION_AND_SOURCE_REGISTRATION_WITHOUT_HIDDEN_SEMANTIC_DISCLOSURE"
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
