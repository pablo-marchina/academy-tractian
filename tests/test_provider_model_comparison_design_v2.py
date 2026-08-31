from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


MANIFEST = Path("research/experiments/provider-model-comparison-design-manifest-v2.json")
POPULATION = Path("research/experiments/provider-model-comparison-dev-population-v1.json")
VALIDATOR = Path("scripts/research/validate_provider_model_comparison_design_v2.py")


def test_provider_free_v2_validator_passes() -> None:
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
    assert result["max_future_live_calls"] == 32
    assert result["population_units"] == 8
    assert result["max_packet_neurons"] < 9000


def test_v2_manifest_keeps_population_and_zero_cost_boundary() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    population = json.loads(POPULATION.read_text(encoding="utf-8"))

    assert manifest["population"]["unit_count"] == population["unit_count"] == 8
    assert manifest["population"]["repetitions_per_live_candidate"] == 2
    assert manifest["zero_cost_resource_budget"]["required_workers_plan"] == "Workers Free"
    assert manifest["zero_cost_resource_budget"]["workers_paid_plan_allowed"] is False
    assert manifest["zero_cost_resource_budget"]["prepaid_ai_gateway_credits_allowed"] is False
    assert manifest["request_contract"]["ai_gateway_enabled"] is False
    assert manifest["request_contract"]["provider_native_tool_execution_enabled"] is False
    assert manifest["provider_model_calls_authorized_now"] == 0


def test_v2_core_live_set_is_exactly_two_cloudflare_models() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    live = [candidate for candidate in manifest["candidate_set"] if candidate["live_call"]]
    assert [candidate["model_id"] for candidate in live] == [
        "@cf/zai-org/glm-4.7-flash",
        "@cf/nvidia/nemotron-3-120b-a12b",
    ]
    assert all(candidate["provider_id"] == "cloudflare" for candidate in live)
    assert all(candidate["retry_count"] == 0 for candidate in live)
    assert all(candidate["fallback_used"] is False for candidate in live)
