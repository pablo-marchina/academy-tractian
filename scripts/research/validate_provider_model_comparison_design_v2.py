#!/usr/bin/env python3
"""Provider-free validator for the preregistered Cloudflare comparison v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST = Path("research/experiments/provider-model-comparison-design-manifest-v2.json")
DEFAULT_POPULATION = Path("research/experiments/provider-model-comparison-dev-population-v1.json")
FORBIDDEN_PROVIDER_ENVS = (
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_AUTH_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
)
EXPECTED_LIVE_MODELS = {
    "@cf/zai-org/glm-4.7-flash",
    "@cf/nvidia/nemotron-3-120b-a12b",
}
EXPECTED_METRICS = {f"M{i}" for i in range(1, 11)}
EXPECTED_POPULATION_SHA256 = "561d252d06a3be30e7d631053906e2e29fbcdd151f05b03b56cbf5ead024c251"
EXPECTED_PACKET_NEURONS = 7937.522688
EXPECTED_HEADROOM_NEURONS = 2062.477312


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_provider_free_environment() -> None:
    present = sorted(name for name in FORBIDDEN_PROVIDER_ENVS if os.getenv(name))
    if present:
        raise AssertionError(
            f"provider/account credentials must not be present during preregistration validation: {present}"
        )


def validate_population(population: dict[str, Any], population_path: Path) -> None:
    assert population["schema_version"] == "provider-model-comparison-dev-population-v1"
    assert population["status"] == "PROSPECTIVE_PUBLIC_DEV_ONLY"
    assert population["unit_count"] == len(population["units"]) == 8
    assert population["repetitions_per_live_candidate"] == 2
    boundaries = population["boundaries"]
    assert boundaries["uses_private_oracle"] is False
    assert boundaries["uses_expected_paths"] is False
    assert boundaries["uses_validation"] is False
    assert boundaries["uses_locked_test"] is False
    assert boundaries["uses_fresh_blind"] is False
    assert boundaries["uses_historical_real_task_quality"] is False
    assert boundaries["provider_calls_authorized_by_population"] == 0
    assert sha256_bytes(population_path) == EXPECTED_POPULATION_SHA256


def validate_manifest(manifest: dict[str, Any], population_path: Path) -> None:
    assert manifest["schema_version"] == "provider-model-comparison-design-v2"
    assert manifest["status"] == "DESIGN_CANDIDATE_PROVIDER_FREE_ONLY"
    assert manifest["date"] == "2026-08-31"
    assert manifest["issue"] == 68
    assert manifest["decision_id"] == "D01"
    assert manifest["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert manifest["scientific_state_changed"] is False
    assert manifest["provider_model_calls_authorized_now"] == 0
    assert manifest["credential_account_probes_authorized_now"] == 0
    assert manifest["production_provider_model_selected"] is False
    assert manifest["production_actions_enabled"] is False
    assert manifest["prospective_relationship"]["consumed_old_live_calls"] == 0
    assert manifest["prospective_relationship"]["old_live_candidate_execution"] == "FORBIDDEN_AS_IS"

    sources = manifest["official_sources"]
    assert sources
    source_ids = {source["source_id"] for source in sources}
    assert len(source_ids) == len(sources)
    for source in sources:
        assert source["retrieved_date"] == manifest["source_retrieval_date"] == "2026-08-31"
        assert source["url"].startswith("https://developers.cloudflare.com/")

    candidates = manifest["candidate_set"]
    baseline = [candidate for candidate in candidates if not candidate["live_call"]]
    live = [candidate for candidate in candidates if candidate["live_call"]]
    assert len(candidates) == 3
    assert len(baseline) == 1
    assert baseline[0]["candidate_id"] == "baseline_scripted_null_v1"
    assert baseline[0]["eligible_for_production_selection"] is False
    assert len(live) == 2
    assert {candidate["provider_id"] for candidate in live} == {"cloudflare"}
    assert {candidate["model_id"] for candidate in live} == EXPECTED_LIVE_MODELS
    assert {candidate["candidate_class"] for candidate in live} == {
        "efficient_hosted_free",
        "capacity_hosted_free",
    }
    for candidate in candidates:
        assert candidate["retry_count"] == 0
        assert candidate["fallback_used"] is False
        for source_id in candidate.get("source_ids", []):
            assert source_id in source_ids
    for candidate in live:
        assert candidate["route_id"] == "cloudflare.workers_ai.openai_compat.chat_completions.v1"
        assert candidate["endpoint_template"].endswith("/ai/v1/chat/completions")
        assert candidate["account_access"] == "UNVERIFIED_NO_CREDENTIAL_PROBE"

    population = manifest["population"]
    assert population["path"] == population_path.as_posix()
    assert population["sha256"] == sha256_bytes(population_path) == EXPECTED_POPULATION_SHA256
    assert population["unit_count"] == 8
    assert population["repetitions_per_live_candidate"] == 2
    assert population["private_oracle_required"] is False
    assert population["population_reused_without_mutation"] is True

    request = manifest["request_contract"]
    assert request["application_controller_owns_loop"] is True
    assert request["harnessrunner_only_real_tool_execution_boundary"] is True
    assert request["provider_native_tool_execution_enabled"] is False
    assert request["provider_side_conversation_state_enabled"] is False
    assert request["ai_gateway_enabled"] is False
    assert request["built_in_web_search_enabled"] is False
    assert request["stream"] is False
    assert request["n"] == 1
    assert request["temperature"] == 0
    assert request["max_completion_tokens"] == 512
    assert request["provider_seed_forwarded"] is False
    assert request["store"] is False
    assert request["automatic_repair"] is False

    execution = manifest["execution"]
    assert execution["live_candidate_count"] == 2
    assert execution["provider_calls_per_unit_per_live_candidate"] == 2
    assert execution["attempts_per_live_candidate"] == 16
    assert execution["max_live_provider_calls_total"] == 32
    assert execution["warmup_calls"] == 0
    assert execution["automatic_retries"] == 0
    assert execution["provider_fallbacks"] == 0
    assert execution["parallel_live_calls"] is False
    assert execution["provider_seed_forwarded"] is False
    assert execution["operational_failures_remain_in_denominators"] is True

    budget = manifest["zero_cost_resource_budget"]
    assert budget["required_workers_plan"] == "Workers Free"
    assert budget["prepaid_ai_gateway_credits_allowed"] is False
    assert budget["workers_paid_plan_allowed"] is False
    assert budget["published_free_neurons_per_day"] == 10000
    assert budget["max_accounted_input_tokens_per_attempt"] == 8000
    assert budget["max_completion_tokens_per_attempt"] == 512
    assert budget["minimum_free_neurons_remaining_before_attempt_1"] == 9000

    expected_glm_attempt = (8000 * 5500 + 512 * 36400) / 1_000_000
    expected_nemotron_attempt = (8000 * 45455 + 512 * 136364) / 1_000_000
    expected_total = 16 * (expected_glm_attempt + expected_nemotron_attempt)
    expected_headroom = 10000 - expected_total
    assert math.isclose(budget["glm_max_neurons_per_attempt"], expected_glm_attempt, abs_tol=1e-9)
    assert math.isclose(budget["nemotron_max_neurons_per_attempt"], expected_nemotron_attempt, abs_tol=1e-9)
    assert math.isclose(budget["max_packet_neurons"], expected_total, abs_tol=1e-9)
    assert math.isclose(budget["max_packet_neurons"], EXPECTED_PACKET_NEURONS, abs_tol=1e-9)
    assert math.isclose(budget["free_allocation_headroom_neurons"], expected_headroom, abs_tol=1e-9)
    assert math.isclose(budget["free_allocation_headroom_neurons"], EXPECTED_HEADROOM_NEURONS, abs_tol=1e-9)
    assert budget["max_packet_neurons"] < budget["minimum_free_neurons_remaining_before_attempt_1"]
    assert budget["free_allocation_headroom_fraction"] >= 0.20
    assert len(budget["fail_closed_rules"]) >= 4

    gates = manifest["hard_gates"]
    assert len(gates) >= 10
    assert all(gate["disqualifying"] is True for gate in gates.values())

    metrics = manifest["metrics"]
    assert set(metrics) == EXPECTED_METRICS
    assert metrics["M1"]["minimum"] == 0.9375
    assert metrics["M2"]["minimum"] == 1.0
    assert metrics["M4"]["minimum"] == 0.75
    assert metrics["M4"]["semantic_judge_used"] is False
    assert metrics["M4"]["population_sha256"] == EXPECTED_POPULATION_SHA256
    assert metrics["M7"]["minimum_success_rate"] == 0.9375
    assert metrics["M7"]["minimum_signature_stability"] == 0.75
    assert metrics["M8"]["actual_cash_cost_required_usd"] == 0
    assert math.isclose(metrics["M8"]["packet_neuron_ceiling"], EXPECTED_PACKET_NEURONS, abs_tol=1e-9)
    assert metrics["M8"]["selection_resource_axis"] == "total_observed_neurons"
    assert metrics["M10"]["minimum"] == 1.0

    selection = manifest["selection_rule"]
    assert selection["baseline_eligible"] is False
    assert selection["weighted_global_score_forbidden"] is True
    assert selection["post_result_threshold_changes_forbidden"] is True
    assert "NO_SELECTION" in selection["allowed_outcomes"]
    assert set(selection["allowed_outcomes"]) == {
        "cloudflare_glm_4_7_flash_workers_free",
        "cloudflare_nemotron_3_120b_a12b_workers_free",
        "NO_SELECTION",
    }

    custody = manifest["custody_and_provenance"]
    assert custody["write_ahead_attempt_claim_required"] is True
    assert custody["one_durable_custody_root_required"] is True
    assert custody["raw_provider_request_persisted"] is False
    assert custody["raw_provider_response_persisted"] is False
    assert custody["secret_material_persisted"] is False
    assert custody["claimed_or_uncertain_attempt_auto_replay_forbidden"] is True
    assert custody["ADR_007_model_call_provenance_required"] is True

    amendments = manifest["amendment_rules"]
    assert amendments["credential_probe_before_separate_live_authorization"] is False
    assert amendments["implementation_before_this_design_freezes"] is False

    forbidden = set(manifest["forbidden_inputs"])
    assert {
        "eval/expected-paths.json",
        "docs/test-scenarios.md",
        "data/cases.parquet",
        "FRESH_BLIND",
        "LEGACY_LOCKED_TEST",
    }.issubset(forbidden)
    assert "zero provider/model calls" in manifest["next_authorization"].lower()


def run(manifest_path: Path, population_path: Path) -> dict[str, Any]:
    assert_provider_free_environment()
    manifest = load_json(manifest_path)
    population = load_json(population_path)
    assert isinstance(manifest, dict)
    assert isinstance(population, dict)
    validate_population(population, population_path)
    validate_manifest(manifest, population_path)
    return {
        "status": "PASS",
        "provider_calls_executed": 0,
        "provider_calls_authorized": 0,
        "credential_account_probes": 0,
        "live_candidate_count": 2,
        "population_units": 8,
        "max_future_live_calls": 32,
        "max_packet_neurons": EXPECTED_PACKET_NEURONS,
        "free_allocation_headroom_neurons": EXPECTED_HEADROOM_NEURONS,
        "population_sha256": sha256_bytes(population_path),
        "metrics": sorted(EXPECTED_METRICS, key=lambda item: int(item[1:])),
        "scientific_gate": manifest["scientific_gate"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--population", type=Path, default=DEFAULT_POPULATION)
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.population), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
