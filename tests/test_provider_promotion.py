from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.provider_promotion import (
    CandidateBenchmark,
    PairedPrimaryComparison,
    ProviderBenchmarkEvidence,
    ProviderPromotionPolicy,
    decide_provider_promotion,
)


CANDIDATES = ("openai:gpt-5.6-sol", "google:gemini-3.7-flash")
CODE_SHA = "abcdef1234567890"


def _candidate(candidate_id: str, **overrides: object) -> CandidateBenchmark:
    provider_id, model_id = candidate_id.split(":", 1)
    payload: dict[str, object] = {
        "candidate_id": candidate_id,
        "provider_id": provider_id,
        "model_id": model_id,
        "scenario_count": 60,
        "repeat_count": 3,
        "human_semantic_calibrated": True,
        "operational_conclusion_accuracy": 0.90,
        "tool_choice_accuracy": 0.95,
        "argument_validity_rate": 0.97,
        "evidence_grounding_rate": 0.94,
        "failure_behavior_pass_rate": 0.98,
        "stability_rate": 0.96,
        "critical_safety_failures": 0,
        "high_impact_action_failures": 0,
    }
    payload.update(overrides)
    return CandidateBenchmark.model_validate(payload)


def _policy(**overrides: object) -> ProviderPromotionPolicy:
    payload: dict[str, object] = {
        "required_candidate_ids": CANDIDATES,
        "expected_corpus_id": "golden-v1",
        "expected_corpus_hash": "sha256:golden",
        "expected_evaluator_version": "production-evaluator-v1",
        "expected_code_sha": CODE_SHA,
        "min_scenarios": 50,
        "min_repeats": 3,
        "min_paired_scenarios": 50,
        "min_operational_conclusion_accuracy": 0.85,
        "min_tool_choice_accuracy": 0.90,
        "min_argument_validity_rate": 0.90,
        "min_evidence_grounding_rate": 0.90,
        "min_failure_behavior_pass_rate": 0.95,
        "min_stability_rate": 0.90,
        "preregistered_primary_margin": 0.01,
    }
    payload.update(overrides)
    return ProviderPromotionPolicy.model_validate(payload)


def _evidence(
    *,
    candidates: tuple[CandidateBenchmark, ...] | None = None,
    comparisons: tuple[PairedPrimaryComparison, ...] = (),
    **overrides: object,
) -> ProviderBenchmarkEvidence:
    payload: dict[str, object] = {
        "corpus_id": "golden-v1",
        "corpus_hash": "sha256:golden",
        "evaluator_version": "production-evaluator-v1",
        "code_sha": CODE_SHA,
        "generated_at": datetime(2026, 9, 4, tzinfo=UTC),
        "candidates": candidates
        or tuple(_candidate(candidate_id) for candidate_id in CANDIDATES),
        "paired_primary_comparisons": comparisons,
    }
    payload.update(overrides)
    return ProviderBenchmarkEvidence.model_validate(payload)


def _superiority(winner_id: str, loser_id: str) -> PairedPrimaryComparison:
    return PairedPrimaryComparison(
        winner_id=winner_id,
        loser_id=loser_id,
        effect=0.06,
        confidence_interval_low=0.02,
        confidence_interval_high=0.10,
        paired_scenarios=60,
    )


def test_missing_human_semantic_calibration_invalidates_comparison() -> None:
    candidates = (
        _candidate(CANDIDATES[0], human_semantic_calibrated=False),
        _candidate(CANDIDATES[1]),
    )
    decision = decide_provider_promotion(
        evidence=_evidence(
            candidates=candidates,
            comparisons=(_superiority(CANDIDATES[1], CANDIDATES[0]),),
        ),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.qualified_candidate_ids == ()
    assert decision.reason_codes == ("HUMAN_SEMANTIC_CALIBRATION_REQUIRED",)


def test_safety_failure_cannot_be_promoted_despite_better_accuracy() -> None:
    unsafe = _candidate(
        CANDIDATES[0],
        operational_conclusion_accuracy=0.99,
        critical_safety_failures=1,
    )
    safe = _candidate(CANDIDATES[1], operational_conclusion_accuracy=0.88)
    decision = decide_provider_promotion(
        evidence=_evidence(
            candidates=(unsafe, safe),
            comparisons=(_superiority(CANDIDATES[0], CANDIDATES[1]),),
        ),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert "CRITICAL_SAFETY_FAILURE" in decision.reason_codes


def test_two_qualified_candidates_without_unique_paired_superiority_are_no_selection() -> None:
    decision = decide_provider_promotion(evidence=_evidence(), policy=_policy())

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.qualified_candidate_ids == CANDIDATES
    assert decision.reason_codes == ("NO_UNIQUE_PAIRED_SUPERIORITY",)


def test_unique_preregistered_paired_superiority_promotes_candidate() -> None:
    decision = decide_provider_promotion(
        evidence=_evidence(comparisons=(_superiority(CANDIDATES[0], CANDIDATES[1]),)),
        policy=_policy(),
    )

    assert decision.outcome == "PROMOTE"
    assert decision.selected_candidate_id == CANDIDATES[0]
    assert decision.reason_codes == ("UNIQUE_PAIRED_SUPERIORITY_AFTER_HARD_GATES",)


def test_ci_must_clear_preregistered_margin_not_merely_zero() -> None:
    comparison = PairedPrimaryComparison(
        winner_id=CANDIDATES[0],
        loser_id=CANDIDATES[1],
        effect=0.03,
        confidence_interval_low=0.005,
        confidence_interval_high=0.05,
        paired_scenarios=60,
    )
    decision = decide_provider_promotion(
        evidence=_evidence(comparisons=(comparison,)),
        policy=_policy(preregistered_primary_margin=0.01),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.reason_codes == ("NO_UNIQUE_PAIRED_SUPERIORITY",)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("corpus_id", "other-corpus", "CORPUS_ID_MISMATCH"),
        ("corpus_hash", "sha256:other", "CORPUS_HASH_MISMATCH"),
        ("evaluator_version", "other-evaluator", "EVALUATOR_VERSION_MISMATCH"),
        ("code_sha", "1234567", "CODE_SHA_MISMATCH"),
    ],
)
def test_provenance_mismatch_is_no_selection(field: str, value: str, reason: str) -> None:
    decision = decide_provider_promotion(
        evidence=_evidence(**{field: value}),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert reason in decision.reason_codes


def test_insufficient_sample_or_repeats_invalidates_comparison() -> None:
    candidates = (
        _candidate(CANDIDATES[0], scenario_count=49),
        _candidate(CANDIDATES[1], repeat_count=2),
    )
    decision = decide_provider_promotion(
        evidence=_evidence(
            candidates=candidates,
            comparisons=(_superiority(CANDIDATES[0], CANDIDATES[1]),),
        ),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.qualified_candidate_ids == ()
    assert "INSUFFICIENT_SCENARIOS" in decision.reason_codes
    assert "INSUFFICIENT_REPEATS" in decision.reason_codes


def test_strict_artifacts_reject_unknown_fields_instead_of_accepting_raw_payloads() -> None:
    with pytest.raises(ValidationError):
        CandidateBenchmark.model_validate(
            {
                **_candidate(CANDIDATES[0]).model_dump(),
                "raw_provider_response": "secret-bearing body",
            }
        )

    with pytest.raises(ValidationError):
        ProviderBenchmarkEvidence.model_validate(
            {
                **_evidence().model_dump(),
                "prompt": "raw prompt must not enter the promotion artifact",
            }
        )
