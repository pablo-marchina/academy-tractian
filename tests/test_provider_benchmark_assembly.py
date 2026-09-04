from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.eval_driven import EvalMetricBundle, EvalMetricRule, EvalScenarioRecord
from academy_tractian.hosted_provider import hosted_runtime_configuration_identity
from academy_tractian.provider_benchmark_assembly import (
    ProviderCandidateBenchmarkInput,
    assemble_provider_benchmark_evidence,
    eval_rule_set_sha256,
)
from academy_tractian.provider_human_calibration import build_provider_human_calibration_protocol
from academy_tractian.runtime import (
    ProductionRuntimeConfig,
    canonical_tool_registry,
    production_runtime_config_hash,
)


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


def _bundle(provider: str, values: tuple[float, float, float, float]) -> EvalMetricBundle:
    identity = hosted_runtime_configuration_identity(provider)
    config_hash = production_runtime_config_hash(
        RUNTIME_CONFIG,
        canonical_tool_registry(),
        identity,
    )
    records = (
        EvalScenarioRecord(group_id="scenario-a", case_id="repeat-1", metrics={"quality": values[0]}),
        EvalScenarioRecord(group_id="scenario-a", case_id="repeat-2", metrics={"quality": values[1]}),
        EvalScenarioRecord(group_id="scenario-b", case_id="repeat-1", metrics={"quality": values[2]}),
        EvalScenarioRecord(group_id="scenario-b", case_id="repeat-2", metrics={"quality": values[3]}),
    )
    return EvalMetricBundle(
        config_id=identity.candidate_id,
        records=records,
        metadata={"runtime_config_hash": config_hash},
    )


def _input(provider: str, values: tuple[float, float, float, float]) -> ProviderCandidateBenchmarkInput:
    return ProviderCandidateBenchmarkInput(
        identity=hosted_runtime_configuration_identity(provider),
        bundle=_bundle(provider, values),
    )


def test_assembly_recomputes_runtime_hashes_maturity_and_full_pairwise_matrix() -> None:
    assembly = assemble_provider_benchmark_evidence(
        candidates=(
            _input("openai", (0.8, 0.8, 0.8, 0.8)),
            _input("google", (0.9, 0.9, 0.9, 0.9)),
        ),
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

    evidence = assembly.evidence
    assert len(evidence.candidates) == 2
    assert len(evidence.pairwise_reports) == 2
    assert {candidate.scenario_count for candidate in evidence.candidates} == {2}
    assert {candidate.repeat_count for candidate in evidence.candidates} == {2}
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


def test_bundle_candidate_id_must_match_code_owned_identity() -> None:
    bundle = _bundle("openai", (0.8, 0.8, 0.8, 0.8))
    payload = bundle.model_dump(mode="json")
    payload["config_id"] = "google:gemini-3.7-flash"

    with pytest.raises(ValidationError, match="bundle_candidate_id_mismatch"):
        ProviderCandidateBenchmarkInput(
            identity=hosted_runtime_configuration_identity("openai"),
            bundle=EvalMetricBundle.model_validate(payload),
        )


def test_bundle_runtime_hash_is_recomputed_not_trusted_from_metadata() -> None:
    bundle = _bundle("openai", (0.8, 0.8, 0.8, 0.8))
    payload = bundle.model_dump(mode="json")
    payload["metadata"]["runtime_config_hash"] = "0" * 64
    bad = ProviderCandidateBenchmarkInput(
        identity=hosted_runtime_configuration_identity("openai"),
        bundle=EvalMetricBundle.model_validate(payload),
    )

    with pytest.raises(ValueError, match="runtime_config_hash_mismatch"):
        assemble_provider_benchmark_evidence(
            candidates=(
                bad,
                _input("google", (0.9, 0.9, 0.9, 0.9)),
            ),
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


def test_scenario_and_repeat_counts_are_derived_from_records() -> None:
    assembly = assemble_provider_benchmark_evidence(
        candidates=(
            _input("openai", (0.8, 0.8, 0.8, 0.8)),
            _input("google", (0.8, 0.8, 0.8, 0.8)),
        ),
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

    by_id = {candidate.candidate_id: candidate for candidate in assembly.evidence.candidates}
    assert by_id["openai:gpt-5.6-sol"].scenario_count == 2
    assert by_id["openai:gpt-5.6-sol"].repeat_count == 2
