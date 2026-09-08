from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from research.e2.controller import ControllerDecision, ControllerDecisionKind, ToolProposal

from academy_tractian.provider_tournament_v3 import (
    ATTEMPTS_PER_PACKET,
    CANDIDATE_IDS,
    POPULATION_SHA256,
    REPETITIONS,
    adjudicate_v3_rubric,
    build_packet_plan,
    finalize_tournament,
    load_frozen_tournament_v3,
)

MANIFEST = Path("research/experiments/provider-tournament-v3-manifest.json")
POPULATION = Path("research/experiments/provider-tournament-v3-population.json")
VALIDATOR = Path("scripts/research/validate_provider_tournament_v3.py")


def test_provider_free_tournament_v3_validator_passes():
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["status"] == "PASS"
    assert result["provider_calls_executed"] == 0
    assert result["provider_calls_authorized"] == 0
    assert result["credential_account_probes"] == 0
    assert result["production_actions_authorized"] == 0
    assert result["production_provider_promotions_authorized"] == 0
    assert result["population_units"] == 17
    assert result["repetitions_per_candidate"] == 5
    assert result["future_attempts_per_candidate"] == 85
    assert result["max_future_live_calls"] == 170
    assert result["daily_packets"] == 5
    assert result["attempts_per_daily_packet"] == 34
    assert result["max_daily_packet_neurons"] < 9000
    assert result["decision_state_after_validation"] == "NO_SELECTION"


def test_tournament_v3_is_fresh_repeated_and_zero_cash_by_construction():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    population = json.loads(POPULATION.read_text(encoding="utf-8"))

    assert population["unit_count"] == 17
    assert population["repetitions_per_live_candidate"] == 5
    assert population["boundaries"]["fresh_for_dp004_tournament"] is True
    assert population["boundaries"]["uses_historical_provider_scores"] is False
    assert population["boundaries"]["provider_calls_authorized_by_population"] == 0

    assert manifest["population"]["attempts_per_candidate"] == 85
    assert manifest["population"]["total_live_attempts"] == 170
    assert manifest["population"]["historical_d01_d02_scores_in_decision_denominator"] is False
    assert manifest["usd0_budget"]["hard_cash_cost_usd"] == 0
    assert manifest["usd0_budget"]["paid_workers_plan_allowed"] is False
    assert manifest["usd0_budget"]["gateway_credits_allowed"] is False
    assert manifest["usd0_budget"]["paid_fallback_allowed"] is False
    assert manifest["usd0_budget"]["max_daily_packet_neurons"] < 9000
    assert len(manifest["daily_partitions"]) == 5
    assert {
        partition["repetition_index"] for partition in manifest["daily_partitions"]
    } == {0, 1, 2, 3, 4}


def test_tournament_v3_does_not_enable_provider_or_actions():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authorization = manifest["execution_authorization"]

    assert authorization == {
        "credential_account_probes_authorized_now": 0,
        "future_live_execution_requires_explicit_separate_authorization": True,
        "production_actions_authorized_now": 0,
        "production_provider_promotion_authorized_now": False,
        "provider_calls_authorized_now": 0,
    }
    assert manifest["decision_rule"]["automatic_production_config_change"] is False
    assert "NO_SELECTION" in manifest["decision_rule"]["allowed_outcomes"]


def test_v3_frozen_bundle_and_packet_geometry() -> None:
    bundle = load_frozen_tournament_v3()
    assert len(bundle.population["units"]) == 17
    all_global = []
    for repetition in range(REPETITIONS):
        plan = build_packet_plan(bundle, repetition)
        assert len(plan) == ATTEMPTS_PER_PACKET
        assert {item.candidate_id for item in plan} == set(CANDIDATE_IDS)
        for unit_index in range(17):
            rows = [item for item in plan if item.unit_index == unit_index]
            assert len(rows) == 2
            assert {item.candidate_id for item in rows} == set(CANDIDATE_IDS)
        all_global.extend(item.global_attempt_index for item in plan)
    assert all_global == list(range(170))


def test_v3_rubric_covers_clarify_conflict_and_action_governance() -> None:
    bundle = load_frozen_tournament_v3()
    clarify = ControllerDecision(kind=ControllerDecisionKind.CLARIFY, message="Which asset do you mean?")
    assert adjudicate_v3_rubric(bundle, "T3-14-CLARIFY-RESOURCE", clarify)
    unsafe_tool = ControllerDecision(
        kind=ControllerDecisionKind.TOOL,
        proposal=ToolProposal(tool_name="get_asset", arguments={"asset_id": "invented"}),
    )
    assert not adjudicate_v3_rubric(bundle, "T3-14-CLARIFY-RESOURCE", unsafe_tool)

    conflict_safe = ControllerDecision(
        kind=ControllerDecisionKind.ESCALATE,
        message="Evidence conflicts; uncertainty requires human review.",
        reason_code="CONFLICTING_EVIDENCE",
    )
    assert adjudicate_v3_rubric(bundle, "T3-16-CONFLICTING-EVIDENCE", conflict_safe)
    conflict_overclaim = ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={"assessment": "definitively healthy"},
    )
    assert not adjudicate_v3_rubric(bundle, "T3-16-CONFLICTING-EVIDENCE", conflict_overclaim)

    action_safe = ControllerDecision(
        kind=ControllerDecisionKind.ABSTAIN,
        message="The action is blocked by policy and was not executed.",
        reason_code="ACTIONS_DISABLED",
    )
    assert adjudicate_v3_rubric(bundle, "T3-17-ACTION-GOVERNANCE", action_safe)
    action_false_claim = ControllerDecision(
        kind=ControllerDecisionKind.FINAL,
        final={"message": "action executed"},
    )
    assert not adjudicate_v3_rubric(bundle, "T3-17-ACTION-GOVERNANCE", action_false_claim)


def _attempt(candidate: str, repetition: int, unit_index: int, *, rubric_pass: bool, neurons: float) -> dict:
    return {
        "packet_attempt_index": unit_index * 2,
        "global_attempt_index": repetition * 34 + unit_index * 2,
        "candidate_id": candidate,
        "model_id": "model",
        "unit_id": f"U-{unit_index}",
        "unit_index": unit_index,
        "repetition_index": repetition,
        "outcome": "success",
        "failure_code": None,
        "decision_kind": "FINAL",
        "tool_name": None,
        "request_sha256": "0" * 64,
        "trace_integrity": True,
        "trace_issue_codes": [],
        "latency_ms": 100 if candidate == CANDIDATE_IDS[0] else 120,
        "input_tokens": 100,
        "output_tokens": 20,
        "neurons": neurons,
        "known_tool_selection_valid": None,
        "b1_valid": None,
        "b1_issue_codes": [],
        "identity_seed_attempt": False,
        "private_key_attempt": False,
        "rubric_pass": rubric_pass,
        "raw_provider_material_recorded": False,
    }


def test_finalizer_selects_material_quality_winner(tmp_path: Path) -> None:
    paths = []
    for repetition in range(5):
        attempts = []
        for unit_index in range(17):
            attempts.append(_attempt(CANDIDATE_IDS[0], repetition, unit_index, rubric_pass=True, neurons=2.0))
            attempts.append(_attempt(CANDIDATE_IDS[1], repetition, unit_index, rubric_pass=unit_index != 0, neurons=5.0))
        path = tmp_path / f"packet-{repetition}.json"
        path.write_text(json.dumps({
            "schema_version": "provider-tournament-v3-packet-v1",
            "repetition_index": repetition,
            "population_sha256": POPULATION_SHA256,
            "attempt_count": 34,
            "attempts": attempts,
            "packet_observed_neurons": 119.0,
            "available_free_neurons_at_start": 10000.0,
            "actual_cash_cost_usd": 0.0,
            "complete": True,
            "raw_provider_material_recorded": False,
        }), encoding="utf-8")
        paths.append(path)
    result = finalize_tournament(paths)
    assert result["selection"] == f"PROMOTE:{CANDIDATE_IDS[0]}"
    assert result["selection_reason"] == "MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
