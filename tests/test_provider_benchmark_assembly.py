from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.eval_driven import EvalMetricRule
from academy_tractian.hosted_provider import hosted_runtime_configuration_identity
from academy_tractian.provider_benchmark_assembly import (
    ProviderBenchmarkObservation,
    ProviderCandidateBenchmarkInput,
    assemble_provider_benchmark_evidence,
    eval_rule_set_sha256,
)
from academy_tractian.provider_human_calibration import build_provider_human_calibration_protocol
from academy_tractian.runtime import ProductionRuntimeConfig, canonical_tool_registry
from academy_tractian.runtime_configuration_identity import production_runtime_config_hash


RUNTIME_CONFIG = ProductionRuntimeConfig()
RULES = (
    EvalMetricRule(
        name="quality",
        direction="higher_is_better",
        max_allowed_regression=0.0,
        min_material_improvement=0.01,
    ),
)
PROTOCOL = build_provider_human_calibration_protocol(protocol_id="provider-human-oca-v1")


def _observations(values: tuple[float, float, float, float, float, float]):
    return (
        ProviderBenchmarkObservation(
            group_id="asset-b204",
            scenario_id="CEN-07",
            repeat_index=1,
            metrics={"quality": values[0]},
        ),
        ProviderBenchmarkObservation(
            group_id="asset-b204",
            scenario_id="CEN-07",
            repeat_index=2,
            metrics={"quality": values[1]},
        ),
        ProviderBenchmarkObservation(
            group_id="asset-b204",
            scenario_id="CEN-12",
            repeat_index=1,
            metrics={"quality": values[2]},
        ),
        ProviderBenchmarkObservation(
            group_id="asset-b204",
            scenario_id="CEN-12",
            repeat_index=2,
            metrics={"quality": values[3]},
        ),
        ProviderBenchmarkObservation(
            group_id="asset-m102",
            scenario_id="CEN-09",
            repeat_index=1,
            metrics={"quality": values[4]},
        ),
        ProviderBenchmarkObservation(
            group_id="asset-m102",
            scenario_id="CEN-09",
            repeat_index=2,
            metrics={"quality": values[5]},
        ),
    )


def _input(
    provider: str,
    values: tuple[float, float, float, float, float, float],
    *,
    runtime_hash: str | None = None,
) -> ProviderCandidateBenchmarkInput:
    identity = hosted_runtime_configuration_identity(provider)
    config_hash = production_runtime_config_hash(
        RUNTIME_CONFIG,
        canonical_tool_registry(),
        identity,
    )
    return ProviderCandidateBenchmarkInput(
        identity=identity,
        runtime_config_hash=runtime_hash or config_hash,
        observations=_observations(values),
    )


def _assemble(*candidates: ProviderCandidateBenchmarkInput):
    return assemble_provider_benchmark_evidence(
        candidates=candidates,
        runtime_config=RUNTIME_CONFIG,
        rules=RULES,
        corpus_id="held-out-validation-v1",
        corpus_hash="sha256:held-out-validation-v1",
        evaluator_version="production-evaluator-v1",
        rule_set_id="provider-quality-v1",
        code_sha="abcdef1234567890",
        human_calibration_protocol=PROTOCOL,
        generated_at=datetime(2026, 9, 4, tzinfo=UTC),
        bootstrap_samples=100,
    )


def test_assembly_recomputes_runtime_hashes_maturity_and_full_pairwise_matrix() -> None:
    assembly = _assemble(
        _input("openai", (0.8, 0.8, 0.8, 0.8, 0.8, 0.8)),
        _input("google", (0.9, 0.9, 0.9, 0.9, 0.9, 0.9)),
    )

    evidence = assembly.evidence
    assert len(evidence.candidates) == 2
    assert len(evidence.pairwise_reports) == 2
    assert {candidate.scenario_count for candidate in evidence.candidates} == {3}
    assert {candidate.repeat_count for candidate in evidence.candidates} == {2}
    assert set(assembly.independent_group_counts.values()) == {2}
    assert all(candidate.human_calibration is None for candidate in evidence.candidates)
    assert assembly.rule_set_hash == eval_rule_set_sha256(RULES)
    assert set(assembly.runtime_config_hashes) == {
        "openai:gpt-5.6-sol",
        "google:gemini-3.7-flash",
    }
    assert len(set(assembly.runtime_config_hashes.values())) == 2
    assert {
        (report.baseline_config_id, report.candidate_config_id)
        for report in evidence.pairwise_reports
    } == {
        ("openai:gpt-5.6-sol", "google:gemini-3.7-flash"),
        ("google:gemini-3.7-flash", "openai:gpt-5.6-sol"),
    }
    assert {len(report.paired_groups) for report in evidence.pairwise_reports} == {2}


def test_runtime_hash_is_recomputed_not_trusted_from_input() -> None:
    bad = _input(
        "openai",
        (0.8, 0.8, 0.8, 0.8, 0.8, 0.8),
        runtime_hash="0" * 64,
    )

    with pytest.raises(ValueError, match="runtime_config_hash_mismatch"):
        _assemble(
            bad,
            _input("google", (0.9, 0.9, 0.9, 0.9, 0.9, 0.9)),
        )


def test_candidate_coverage_must_be_identical_for_paired_comparison() -> None:
    google = _input("google", (0.9, 0.9, 0.9, 0.9, 0.9, 0.9))
    payload = google.model_dump(mode="json")
    payload["observations"] = payload["observations"][:-1]
    incomplete = ProviderCandidateBenchmarkInput.model_validate(payload)

    with pytest.raises(ValueError, match="candidate_coverage_mismatch"):
        _assemble(
            _input("openai", (0.8, 0.8, 0.8, 0.8, 0.8, 0.8)),
            incomplete,
        )


def test_scenario_cannot_cross_independent_story_groups() -> None:
    item = _input("openai", (0.8, 0.8, 0.8, 0.8, 0.8, 0.8))
    payload = item.model_dump(mode="json")
    payload["observations"][1]["group_id"] = "asset-other"

    with pytest.raises(ValidationError, match="scenario_crosses_independent_groups"):
        ProviderCandidateBenchmarkInput.model_validate(payload)


def test_duplicate_scenario_repeat_is_rejected() -> None:
    item = _input("openai", (0.8, 0.8, 0.8, 0.8, 0.8, 0.8))
    payload = item.model_dump(mode="json")
    payload["observations"][1]["repeat_index"] = 1

    with pytest.raises(ValidationError, match="duplicate_scenario_repeat"):
        ProviderCandidateBenchmarkInput.model_validate(payload)


def test_eval_bundle_preserves_independent_groups_while_cases_are_scenario_repeats() -> None:
    item = _input("openai", (0.8, 0.8, 0.8, 0.8, 0.8, 0.8))
    bundle = item.eval_bundle()

    assert bundle.config_id == "openai:gpt-5.6-sol"
    assert {record.group_id for record in bundle.records} == {"asset-b204", "asset-m102"}
    assert {record.case_id for record in bundle.records} == {
        "CEN-07::repeat-1",
        "CEN-07::repeat-2",
        "CEN-12::repeat-1",
        "CEN-12::repeat-2",
        "CEN-09::repeat-1",
        "CEN-09::repeat-2",
    }
    assert bundle.metadata["scenario_count"] == 3
    assert bundle.metadata["independent_group_count"] == 2
