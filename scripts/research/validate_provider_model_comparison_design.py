#!/usr/bin/env python3
"""Provider-free validator for the production provider/model comparison design."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST = Path("research/experiments/provider-model-comparison-design-manifest-v1.json")
DEFAULT_POPULATION = Path("research/experiments/provider-model-comparison-dev-population-v1.json")
FORBIDDEN_PROVIDER_ENVS = (
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
)
FORBIDDEN_INPUT_FRAGMENTS = (
    "eval/expected-paths.json",
    "docs/test-scenarios.md",
    "data/cases.parquet",
)
EXPECTED_METRICS = {f"M{i}" for i in range(1, 11)}
EXPECTED_LIVE_CLASSES = {"quality_frontier", "lower_cost_hosted"}
KNOWN_TOOL_NAMES = {
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
ALLOWED_DECISION_KINDS = {"TOOL", "FINAL", "CLARIFY", "ESCALATE", "ABSTAIN"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_population_identity(population_path: Path) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    resolved = population_path.resolve()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except ValueError:
        return resolved.as_posix()


def assert_provider_free_environment() -> None:
    present = sorted(name for name in FORBIDDEN_PROVIDER_ENVS if os.getenv(name))
    if present:
        raise AssertionError(
            f"provider credentials must not be present during design validation: {present}"
        )


def validate_population(population: dict[str, Any]) -> None:
    assert population["schema_version"] == "provider-model-comparison-dev-population-v1"
    assert population["status"] == "PROSPECTIVE_PUBLIC_DEV_ONLY"
    boundaries = population["boundaries"]
    assert boundaries["uses_private_oracle"] is False
    assert boundaries["uses_expected_paths"] is False
    assert boundaries["uses_validation"] is False
    assert boundaries["uses_locked_test"] is False
    assert boundaries["uses_fresh_blind"] is False
    assert boundaries["uses_historical_real_task_quality"] is False
    assert boundaries["provider_calls_authorized_by_population"] == 0

    units = population["units"]
    assert population["unit_count"] == len(units) == 8
    assert population["repetitions_per_live_candidate"] == 2
    ids = [unit["unit_id"] for unit in units]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)

    for unit in units:
        context = unit["context"]
        rubric = unit["rubric"]
        assert context["user_request"].strip()
        assert context["turn_index"] >= 0
        assert context["tool_call_count"] >= 0
        assert isinstance(context["observations"], list)

        exact = rubric.get("kind")
        allowed = rubric.get("allowed_kinds")
        assert (exact is None) != (allowed is None)
        if exact:
            assert exact in ALLOWED_DECISION_KINDS
        else:
            assert allowed and set(allowed).issubset(ALLOWED_DECISION_KINDS)

        if exact == "TOOL":
            assert rubric["tool_name"] in KNOWN_TOOL_NAMES
            forbidden = set(rubric["arguments"].get("forbidden_keys", []))
            assert {"user_id", "x-user-id", "seed"}.issubset(forbidden)

        retry = rubric.get("forbidden_tool_retry")
        if retry is not None:
            assert retry in KNOWN_TOOL_NAMES


def validate_manifest(manifest: dict[str, Any], population_path: Path) -> None:
    assert manifest["schema_version"] == "provider-model-comparison-design-v1"
    assert manifest["status"] == "DESIGN_CANDIDATE_PROVIDER_FREE_ONLY"
    assert manifest["issue"] == 32
    assert manifest["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert manifest["scientific_state_changed"] is False
    assert manifest["provider_model_calls_authorized_now"] == 0
    assert manifest["production_provider_model_selected"] is False
    assert manifest["actions_enabled"] is False

    sources = manifest["official_sources"]
    assert sources
    source_ids = {source["source_id"] for source in sources}
    assert len(source_ids) == len(sources)
    for source in sources:
        assert source["retrieved_date"] == manifest["source_retrieval_date"]
        assert source["url"].startswith("https://")

    candidates = manifest["candidate_set"]
    assert len(candidates) == 3
    baseline = [c for c in candidates if c["candidate_class"] == "provider_free_baseline"]
    live = [c for c in candidates if c["live_call"]]
    assert len(baseline) == 1
    assert baseline[0]["eligible_for_production_selection"] is False
    assert len(live) == 2
    assert {c["candidate_class"] for c in live} == EXPECTED_LIVE_CLASSES
    assert {c["provider_id"] for c in live} == {"openai", "google"}
    assert {c["model_id"] for c in live} == {"gpt-5.6-sol", "gemini-3.7-flash"}
    for candidate in candidates:
        assert candidate["retry_count"] == 0
        assert candidate["fallback_used"] is False
        for source_id in candidate.get("source_ids", []):
            assert source_id in source_ids

    population = manifest["population"]
    assert population["path"] == _normalized_population_identity(population_path)
    assert population["sha256"] == sha256_bytes(population_path)
    assert population["unit_count"] == 8
    assert population["repetitions_per_live_candidate"] == 2
    assert population["private_oracle_required"] is False

    execution = manifest["execution"]
    assert execution["live_candidate_count"] == len(live) == 2
    assert execution["provider_calls_per_unit_per_live_candidate"] == 2
    assert execution["max_live_provider_calls_total"] == population["unit_count"] * 2 * len(live) == 32
    assert execution["warmup_calls"] == 0
    assert execution["automatic_retries"] == 0
    assert execution["provider_fallbacks"] == 0
    assert execution["parallel_live_calls"] is False
    assert execution["provider_seed_forwarded"] is False
    assert execution["operational_failures_remain_in_denominators"] is True

    assert all(gate["disqualifying"] is True for gate in manifest["hard_gates"].values())

    metrics = manifest["metrics"]
    assert set(metrics) == EXPECTED_METRICS
    assert metrics["M4"]["population_sha256"] == population["sha256"]
    assert metrics["M4"]["semantic_judge_used"] is False
    assert metrics["M10"]["minimum"] == 1.0

    selection = manifest["selection_rule"]
    assert selection["baseline_eligible"] is False
    assert "NO_SELECTION" in selection["allowed_outcomes"]
    assert selection["post_result_threshold_changes_forbidden"] is True
    assert any(
        "NO_SELECTION" in str(value)
        for key, value in selection.items()
        if key.startswith("step_")
    )

    forbidden = set(manifest["forbidden_inputs"])
    assert set(FORBIDDEN_INPUT_FRAGMENTS).issubset(forbidden)
    assert "FRESH_BLIND" in forbidden
    assert "LEGACY_LOCKED_TEST" in forbidden
    assert manifest["amendment_rules"]["credential_probe_before_authorization"] is False
    assert "zero provider/model calls" in manifest["next_authorization"].lower()


def run(manifest_path: Path, population_path: Path) -> dict[str, Any]:
    assert_provider_free_environment()
    manifest = load_json(manifest_path)
    population = load_json(population_path)
    assert isinstance(manifest, dict)
    assert isinstance(population, dict)
    validate_population(population)
    validate_manifest(manifest, population_path)
    return {
        "status": "PASS",
        "provider_calls_executed": 0,
        "provider_calls_authorized": 0,
        "candidate_count": len(manifest["candidate_set"]),
        "live_candidate_count": manifest["execution"]["live_candidate_count"],
        "population_units": population["unit_count"],
        "max_future_live_calls": manifest["execution"]["max_live_provider_calls_total"],
        "population_sha256": sha256_bytes(population_path),
        "metrics": sorted(manifest["metrics"], key=lambda item: int(item[1:])),
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
