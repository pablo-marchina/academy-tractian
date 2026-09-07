from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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
