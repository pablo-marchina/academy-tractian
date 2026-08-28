from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
for import_root in (ROOT, ROOT / "src"):
    value = str(import_root)
    if value not in sys.path:
        sys.path.insert(0, value)

from academy_tractian.decision_source import ProviderDecisionRequest
from academy_tractian.provider_clients import ProviderUsageRecord
from academy_tractian.provider_comparison import (
    AUTHORIZATION_GIT_BLOB,
    DESIGN_MANIFEST_GIT_BLOB,
    POPULATION_GIT_BLOB,
    POPULATION_SHA256,
    PROVIDER_CLIENTS_GIT_BLOB,
    PROVIDER_COMPARISON_EXECUTOR_VERSION,
    ProviderComparisonExecutor,
    load_frozen_provider_comparison_bundle,
)


EXPECTED_PATH = ROOT / "research/results/provider-comparison-executor-provider-free-fixture-2026-08-28.json"
OPENAI_ID = "openai_gpt_5_6_sol_responses_standard"
GOOGLE_ID = "google_gemini_3_7_flash_interactions_stateless"


def _decision(kind: str, **kwargs: Any) -> str:
    return json.dumps(
        {"schema_version": "provider-decision-payload-v1", "kind": kind, **kwargs},
        sort_keys=True,
    )


def _fixture_response(request: ProviderDecisionRequest) -> str:
    text = request.user_request
    if "asset_dev_probe_001" in text:
        return _decision("TOOL", tool_name="get_asset", arguments={"asset_id": "asset_dev_probe_001"})
    if "asset_dev_probe_002" in text:
        return _decision("TOOL", tool_name="list_analyses", arguments={"asset_id": "asset_dev_probe_002"})
    if "asset_dev_probe_003" in text:
        return _decision("TOOL", tool_name="get_data_quality", arguments={"asset_id": "asset_dev_probe_003"})
    if "BPFO" in text:
        return _decision("TOOL", tool_name="search_knowledge", arguments={"q": "Explain BPFO", "type": "glossary"})
    if "asset I mentioned" in text:
        return _decision("CLARIFY", message="Which asset should I investigate?", reason_code="MISSING_ASSET")
    if "human specialist" in text:
        return _decision("ESCALATE", message="A human specialist should review this case.", reason_code="USER_REQUESTED_HUMAN")
    if "asset_dev_probe_007" in text:
        return _decision("ABSTAIN", message="The requested evidence is unavailable.", reason_code="UPSTREAM_UNAVAILABLE")
    if "analysis_dev_probe_008" in text:
        return _decision(
            "FINAL",
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "The action remains blocked by policy.",
            },
        )
    raise AssertionError(f"unrecognized frozen fixture request hash={request.request_sha256}")


class FixtureClient:
    def __init__(self, *, provider_id: str, model_id: str, route_id: str) -> None:
        self.provider_id = provider_id
        self.model_id = model_id
        self.route_id = route_id
        self._usage: list[ProviderUsageRecord] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self._usage.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=100,
                output_tokens=20,
                total_tokens=120,
                reasoning_tokens=5,
            )
        )
        return _fixture_response(request)

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage)
        self._usage.clear()
        return records


def _clients(bundle) -> dict[str, FixtureClient]:
    result: dict[str, FixtureClient] = {}
    for item in bundle.authorization["live_candidates"]:
        result[item["candidate_id"]] = FixtureClient(
            provider_id=item["provider_id"],
            model_id=item["model_id"],
            route_id=item["route_id"],
        )
    return result


def stable_projection() -> dict[str, Any]:
    bundle = load_frozen_provider_comparison_bundle(ROOT)
    executor = ProviderComparisonExecutor(
        bundle=bundle,
        clients=_clients(bundle),
        fixture_result=True,
    )
    attempts = executor.run_all_fixture()
    result = executor.finalize(
        fixed_failure_probe_passed={OPENAI_ID: True, GOOGLE_ID: True}
    )

    assert len(attempts) == 32
    assert all(item.fixture_result for item in attempts)
    assert all(item.trace_integrity for item in attempts)
    assert all(item.rubric_pass for item in attempts)
    assert all(not item.raw_material_recorded for item in attempts)
    assert result.selection == "NO_SELECTION"
    assert result.production_selection_claim is False
    assert result.raw_provider_material_recorded is False

    summaries: dict[str, Any] = {}
    for summary in result.candidates:
        assert summary.M6_latency_count == 16
        assert summary.M6_median_ms is not None and summary.M6_median_ms >= 0
        assert summary.M6_p90_ms is not None and summary.M6_p90_ms >= 0
        assert summary.M6_p95_ms is not None and summary.M6_p95_ms >= 0
        assert summary.M6_max_ms is not None and summary.M6_max_ms >= 0
        summaries[summary.candidate_id] = {
            "attempts": summary.attempts,
            "complete": summary.complete,
            "M1_structured_decision_adherence": summary.M1_structured_decision_adherence,
            "M2_known_tool_selection_validity": summary.M2_known_tool_selection_validity,
            "M3_b1_argument_validity": summary.M3_b1_argument_validity,
            "M3_identity_seed_attempts": summary.M3_identity_seed_attempts,
            "M4_public_task_quality": summary.M4_public_task_quality,
            "M5_safe_failure_behavior": summary.M5_safe_failure_behavior,
            "M6_latency_count": summary.M6_latency_count,
            "M6_values_frozen": False,
            "M7_success_rate": summary.M7_success_rate,
            "M7_signature_stability": summary.M7_signature_stability,
            "M8_usage_records": summary.M8_usage_records,
            "M8_normalized_cost_usd": summary.M8_normalized_cost_usd,
            "M9_portability": summary.M9_portability,
            "M10_trace_integrity": summary.M10_trace_integrity,
            "hard_gate_pass": summary.hard_gate_pass,
            "hard_gate_failures": list(summary.hard_gate_failures),
        }

    serialized = result.model_dump_json()
    for forbidden in (
        "Authorization",
        "x-goog-api-key",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "expected_paths",
        "private_truth",
    ):
        assert forbidden not in serialized

    return {
        "schema_version": "provider-comparison-executor-provider-free-fixture-v1",
        "status": "PASS_PROVIDER_FREE_FIXTURE_NO_SELECTION",
        "date": "2026-08-28",
        "issue": 38,
        "executor_version": PROVIDER_COMPARISON_EXECUTOR_VERSION,
        "fixture_result": True,
        "frozen_inputs": {
            "design_manifest_git_blob": DESIGN_MANIFEST_GIT_BLOB,
            "population_git_blob": POPULATION_GIT_BLOB,
            "population_sha256": POPULATION_SHA256,
            "authorization_git_blob": AUTHORIZATION_GIT_BLOB,
            "provider_clients_git_blob": PROVIDER_CLIENTS_GIT_BLOB,
        },
        "plan": {
            "sha256": executor.plan.plan_sha256,
            "attempts": 32,
            "attempts_per_live_candidate": 16,
            "units": 8,
            "repeats": 2,
            "warmup_calls": 0,
            "automatic_retries": 0,
            "fallbacks": 0,
            "parallel_live_calls": False,
        },
        "baseline_quality_rate": result.baseline_quality_rate,
        "candidates": summaries,
        "selection": result.selection,
        "production_selection_claim": False,
        "production_live_calls_consumed": 0,
        "production_actions_executed": 0,
        "raw_provider_material_recorded": False,
        "semantic_private_blind_access": False,
        "scientific_gate_changed": False,
        "note": "M6 latency is exercised and checked nonnegative for all 16 attempts per candidate, but provider-free wall-clock values are intentionally excluded from frozen fixture identity.",
    }


def run() -> dict[str, Any]:
    actual = stable_projection()
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    if actual != expected:
        raise AssertionError(
            "provider comparison fixture projection mismatch:\n"
            + json.dumps({"expected": expected, "actual": actual}, indent=2, sort_keys=True)
        )
    return actual


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
