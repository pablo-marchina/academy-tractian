#!/usr/bin/env python3
"""Provider-free validator for the preregistered production provider tournament v3."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST = Path("research/experiments/provider-tournament-v3-manifest.json")
DEFAULT_POPULATION = Path("research/experiments/provider-tournament-v3-population.json")
DEFAULT_TOOL_REGISTRY = Path("research/e2/tool_registry.py")

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

EXPECTED_MODELS = {
    "@cf/zai-org/glm-4.7-flash",
    "@cf/nvidia/nemotron-3-120b-a12b",
}
EXPECTED_CANDIDATES = {
    "cloudflare-glm-4.7-flash",
    "cloudflare-nemotron-3-120b-a12b",
}
EXPECTED_TOOLS = {
    "get_company",
    "list_assets_by_company",
    "get_current_user",
    "get_asset",
    "update_asset_config",
    "list_analyses",
    "get_analysis",
    "reprocess_analysis",
    "request_specialist_analysis",
    "get_baseline",
    "get_rms",
    "get_spectrum",
    "get_data_quality",
    "get_model",
    "request_retraining",
    "search_knowledge",
    "get_knowledge_doc",
    "escalate_case",
}
EXPECTED_POPULATION_SHA256 = "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9"
EXPECTED_TOOL_REGISTRY_GIT_BLOB = "85b0cefe5fb207518feb264b0c765c9267760c75"
EXPECTED_GLM_MAX_NEURONS = 62.6368
EXPECTED_NEMOTRON_MAX_NEURONS = 433.458368
EXPECTED_DAILY_PACKET_NEURONS = 8433.617856
EXPECTED_TOTAL_CAMPAIGN_NEURONS = 42168.08928


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def assert_provider_free_environment() -> None:
    present = sorted(name for name in FORBIDDEN_PROVIDER_ENVS if os.getenv(name))
    if present:
        raise AssertionError(
            "provider/account credentials must not be present during provider-free "
            f"tournament validation: {present}"
        )


def validate_population(population: dict[str, Any], population_path: Path, tool_registry_path: Path) -> None:
    assert population["schema_version"] == "provider-tournament-v3-population"
    assert population["status"] == "PROSPECTIVE_PUBLIC_PROVIDER_SELECTION_ONLY"
    assert population["created_date"] == "2026-09-05"
    assert population["decision_id"] == "DP-004"
    assert population["unit_count"] == len(population["units"]) == 17
    assert population["repetitions_per_live_candidate"] == 5
    assert sha256_bytes(population_path) == EXPECTED_POPULATION_SHA256

    boundaries = population["boundaries"]
    assert boundaries["fresh_for_dp004_tournament"] is True
    assert boundaries["uses_private_oracle"] is False
    assert boundaries["uses_expected_private_trajectory"] is False
    assert boundaries["uses_validation_split"] is False
    assert boundaries["uses_locked_test"] is False
    assert boundaries["uses_historical_provider_scores"] is False
    assert boundaries["provider_calls_authorized_by_population"] == 0
    assert boundaries["production_actions_authorized"] == 0
    assert boundaries["production_provider_selection_authorized"] is False

    provenance = population["source_provenance"]
    assert provenance["tool_registry_path"] == tool_registry_path.as_posix()
    assert provenance["tool_registry_git_blob"] == EXPECTED_TOOL_REGISTRY_GIT_BLOB
    assert provenance["tool_registry_operation_count"] == 18
    assert provenance["tool_registry_unique_path_count"] == 17
    assert git_blob_sha1(tool_registry_path) == EXPECTED_TOOL_REGISTRY_GIT_BLOB
    assert "provider-model-comparison-dev-population-v1.json" in " ".join(
        provenance["historical_provider_populations_excluded_from_v3_denominator"]
    )

    unit_ids = [unit["unit_id"] for unit in population["units"]]
    assert len(unit_ids) == len(set(unit_ids)) == 17
    assert all(unit_id.startswith("T3-") for unit_id in unit_ids)

    referenced_tools: set[str] = set()
    categories: set[str] = set()
    for unit in population["units"]:
        categories.add(unit["category"])
        rubric = unit["rubric"]
        if "tool_name" in rubric:
            referenced_tools.add(rubric["tool_name"])
        if "forbidden_tool_retry" in rubric:
            referenced_tools.add(rubric["forbidden_tool_retry"])
        continuing = rubric.get("tool_if_continuing", {})
        referenced_tools.update(continuing.get("allowed", []))
        for observation in unit["context"].get("observations", []):
            referenced_tools.add(observation["tool_name"])

    assert referenced_tools
    assert referenced_tools.issubset(EXPECTED_TOOLS)
    assert {
        "clarify",
        "unavailable_evidence",
        "conflicting_evidence",
        "action_safety",
        "investigate_data_quality",
    }.issubset(categories)


def validate_manifest(manifest: dict[str, Any], population_path: Path) -> None:
    assert manifest["schema_version"] == "provider-tournament-v3-manifest"
    assert manifest["status"] == "PREREGISTERED_PROVIDER_FREE_ONLY"
    assert manifest["created_date"] == "2026-09-05"
    assert manifest["decision_id"] == "DP-004"

    population = manifest["population"]
    assert population["path"] == population_path.as_posix()
    assert population["sha256"] == sha256_bytes(population_path) == EXPECTED_POPULATION_SHA256
    assert population["unit_count"] == 17
    assert population["repetitions_per_candidate"] == 5
    assert population["attempts_per_candidate"] == 85
    assert population["candidate_count"] == 2
    assert population["total_live_attempts"] == 170
    assert population["historical_d01_d02_scores_in_decision_denominator"] is False

    candidates = manifest["candidates"]
    assert len(candidates) == 2
    assert {candidate["candidate_id"] for candidate in candidates} == EXPECTED_CANDIDATES
    assert {candidate["model"] for candidate in candidates} == EXPECTED_MODELS
    assert {candidate["provider"] for candidate in candidates} == {"cloudflare-workers-ai"}
    for candidate in candidates:
        assert candidate["workers_free_eligible_verified_date"] == "2026-09-05"
        assert candidate["provider_native_tools"] is False
        assert candidate["fallback_used"] is False
        assert candidate["retry_count"] == 0

    by_model = {candidate["model"]: candidate for candidate in candidates}
    assert math.isclose(
        by_model["@cf/zai-org/glm-4.7-flash"]["max_neurons_per_attempt"],
        EXPECTED_GLM_MAX_NEURONS,
        abs_tol=1e-9,
    )
    assert math.isclose(
        by_model["@cf/nvidia/nemotron-3-120b-a12b"]["max_neurons_per_attempt"],
        EXPECTED_NEMOTRON_MAX_NEURONS,
        abs_tol=1e-9,
    )

    sources = manifest["current_external_evidence"]
    assert len(sources) >= 2
    for source in sources:
        assert source["url"].startswith("https://developers.cloudflare.com/")
        assert source["verified_date"] == "2026-09-05"

    request = manifest["request_contract"]
    assert request["controller_owns_agent_loop"] is True
    assert request["harness_runner_owns_tool_execution"] is True
    assert request["provider_native_tool_execution"] is False
    assert request["provider_side_state"] is False
    assert request["ai_gateway_used"] is False
    assert request["web_search_used"] is False
    assert request["stream"] is False
    assert request["n"] == 1
    assert request["temperature"] == 0
    assert request["max_input_tokens"] == 8000
    assert request["max_output_tokens"] == 512
    assert request["structured_output"] == "strict_json"
    assert request["automatic_json_repair"] is False
    assert request["automatic_retries"] == 0
    assert request["automatic_fallbacks"] == 0
    assert request["warmup_calls"] == 0
    assert request["failed_attempts_remain_in_denominator"] is True

    budget = manifest["usd0_budget"]
    assert budget["hard_cash_cost_usd"] == 0
    assert budget["workers_plan_required"] == "Free"
    assert budget["paid_workers_plan_allowed"] is False
    assert budget["gateway_credits_allowed"] is False
    assert budget["paid_fallback_allowed"] is False
    assert budget["daily_free_neuron_limit"] == 10000
    assert budget["minimum_reported_neurons_available_before_packet"] == 9000
    assert budget["other_workers_ai_usage_during_packet_allowed"] is False
    assert budget["daily_packet_count"] == 5
    assert budget["attempts_per_daily_packet"] == 34
    assert budget["attempts_per_candidate_per_daily_packet"] == 17
    assert budget["campaign_spans_at_least_distinct_utc_days"] == 5
    assert budget["budget_failure_behavior"] == "FAIL_CLOSED_NO_PROVIDER_CALL"
    assert math.isclose(
        budget["max_daily_packet_neurons"], EXPECTED_DAILY_PACKET_NEURONS, abs_tol=1e-9
    )
    assert math.isclose(
        budget["max_total_campaign_neurons"], EXPECTED_TOTAL_CAMPAIGN_NEURONS, abs_tol=1e-9
    )
    assert budget["max_daily_packet_neurons"] < budget["minimum_reported_neurons_available_before_packet"]
    assert budget["max_daily_packet_neurons"] < budget["daily_free_neuron_limit"]
    assert budget["daily_packet_headroom_to_free_limit_neurons"] > 1500

    partitions = manifest["daily_partitions"]
    assert len(partitions) == 5
    expected_scenarios = {f"T3-{index:02d}-" for index in range(1, 18)}
    repetitions = set()
    for packet in partitions:
        repetitions.add(packet["repetition_index"])
        assert packet["attempt_count"] == 34
        assert set(packet["candidate_ids"]) == EXPECTED_CANDIDATES
        assert len(packet["scenario_ids"]) == len(set(packet["scenario_ids"])) == 17
        assert all(
            any(scenario_id.startswith(prefix) for prefix in expected_scenarios)
            for scenario_id in packet["scenario_ids"]
        )
        assert math.isclose(packet["max_neurons"], EXPECTED_DAILY_PACKET_NEURONS, abs_tol=1e-9)
    assert repetitions == {0, 1, 2, 3, 4}

    metrics = manifest["metrics"]
    assert len(metrics) >= 12
    required_metric_prefixes = {f"M{i:02d}" for i in range(1, 13)}
    assert {key.split("_", 1)[0] for key in metrics} == required_metric_prefixes

    gates = manifest["hard_gates"]
    assert len(gates) >= 12
    required_gate_prefixes = {f"H{i:02d}" for i in range(1, 13)}
    assert {key.split("_", 1)[0] for key in gates} == required_gate_prefixes

    rule = manifest["decision_rule"]
    assert set(rule["allowed_outcomes"]) == {"PROMOTE", "REJECT", "INCONCLUSIVE", "NO_SELECTION"}
    assert rule["hard_gate_failure_precedence"] is True
    assert rule["quality_primary"] is True
    assert rule["automatic_production_config_change"] is False

    authorization = manifest["execution_authorization"]
    assert authorization["provider_calls_authorized_now"] == 0
    assert authorization["credential_account_probes_authorized_now"] == 0
    assert authorization["production_actions_authorized_now"] == 0
    assert authorization["production_provider_promotion_authorized_now"] is False
    assert authorization["future_live_execution_requires_explicit_separate_authorization"] is True

    assert len(manifest["revalidation_triggers"]) >= 5
    assert "NO_SELECTION" in manifest["rollback"]


def run(manifest_path: Path, population_path: Path, tool_registry_path: Path) -> dict[str, Any]:
    assert_provider_free_environment()
    manifest = load_json(manifest_path)
    population = load_json(population_path)
    assert isinstance(manifest, dict)
    assert isinstance(population, dict)
    validate_population(population, population_path, tool_registry_path)
    validate_manifest(manifest, population_path)
    return {
        "status": "PASS",
        "provider_calls_executed": 0,
        "provider_calls_authorized": 0,
        "credential_account_probes": 0,
        "production_actions_authorized": 0,
        "production_provider_promotions_authorized": 0,
        "live_candidate_count": 2,
        "population_units": 17,
        "repetitions_per_candidate": 5,
        "future_attempts_per_candidate": 85,
        "max_future_live_calls": 170,
        "daily_packets": 5,
        "attempts_per_daily_packet": 34,
        "max_daily_packet_neurons": EXPECTED_DAILY_PACKET_NEURONS,
        "max_total_campaign_neurons": EXPECTED_TOTAL_CAMPAIGN_NEURONS,
        "population_sha256": sha256_bytes(population_path),
        "decision_id": "DP-004",
        "decision_state_after_validation": "NO_SELECTION",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--population", type=Path, default=DEFAULT_POPULATION)
    parser.add_argument("--tool-registry", type=Path, default=DEFAULT_TOOL_REGISTRY)
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.population, args.tool_registry), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
