from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.eval_driven import EvalDrivenDecisionReport
from academy_tractian.provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderCandidateEvidence,
    ProviderPromotionPolicy,
    decide_provider_promotion,
)


CANDIDATES = ("openai:gpt-5.6-sol", "google:gemini-3.7-flash")
CODE_SHA = "abcdef1234567890"


def _candidate(candidate_id: str, **overrides: object) -> ProviderCandidateEvidence:
    provider_id, model_id = candidate_id.split(":", 1)
    payload: dict[str, object] = {
        "candidate_id": candidate_id,
        "provider_id": provider_id,
        "model_id": model_id,
        "scenario_count": 60,
        "repeat_count": 3,
        "human_semantic_calibrated": True,
    }
    payload.update(overrides)
    return ProviderCandidateEvidence.model_validate(payload)


def _report(
    baseline_id: str,
    candidate_id: str,
    *,
    decision: str,
    hard_gate_failures: tuple[str, ...] = (),
    comparison_issues: tuple[str, ...] = (),
    paired_groups: int = 60,
) -> EvalDrivenDecisionReport:
    return EvalDrivenDecisionReport.model_validate(
        {
            "baseline_config_id": baseline_id,
            "candidate_config_id": candidate_id,
            "comparison_id": "a" * 64,
            "paired_groups": tuple(f"group-{index}" for index in range(paired_groups)),
            "metric_deltas": (),
            "response_mode_slices": (),
            "candidate_hard_gate_failures": hard_gate_failures,
            "comparison_issues": comparison_issues,
            "decision": decision,
            "decision_reasons": ("test-fixture",),
        }
    )


def _policy(**overrides: object) -> ProviderPromotionPolicy:
    payload: dict[str, object] = {
        "required_candidate_ids": CANDIDATES,
        "expected_corpus_id": "golden-v1",
        "expected_corpus_hash": "sha256:golden",
        "expected_evaluator_version": "production-evaluator-v1",
        "expected_rule_set_id": "provider-rules-v1",
        "expected_rule_set_hash": "sha256:rules",
        "expected_code_sha": CODE_SHA,
        "min_scenarios": 50,
        "min_repeats": 3,
        "min_paired_groups": 50,
    }
    payload.update(overrides)
    return ProviderPromotionPolicy.model_validate(payload)


def _evidence(
    *,
    candidates: tuple[ProviderCandidateEvidence, ...] | None = None,
    reports: tuple[EvalDrivenDecisionReport, ...] = (),
    **overrides: object,
) -> ProviderBenchmarkEvidence:
    payload: dict[str, object] = {
        "corpus_id": "golden-v1",
        "corpus_hash": "sha256:golden",
        "evaluator_version": "production-evaluator-v1",
        "rule_set_id": "provider-rules-v1",
        "rule_set_hash": "sha256:rules",
        "code_sha": CODE_SHA,
        "generated_at": datetime(2026, 9, 4, tzinfo=UTC),
        "candidates": candidates
        or tuple(_candidate(candidate_id) for candidate_id in CANDIDATES),
        "pairwise_reports": reports,
    }
    payload.update(overrides)
    return ProviderBenchmarkEvidence.model_validate(payload)


def test_missing_human_semantic_calibration_invalidates_comparison() -> None:
    candidates = (
        _candidate(CANDIDATES[0], human_semantic_calibrated=False),
        _candidate(CANDIDATES[1]),
    )
    reports = (
        _report(CANDIDATES[1], CANDIDATES[0], decision="PROMOTE"),
        _report(CANDIDATES[0], CANDIDATES[1], decision="INCONCLUSIVE"),
    )
    decision = decide_provider_promotion(
        evidence=_evidence(candidates=candidates, reports=reports),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.comparison_ready_candidate_ids == ()
    assert decision.reason_codes == ("HUMAN_SEMANTIC_CALIBRATION_REQUIRED",)


def test_candidate_hard_gate_failure_cannot_be_promoted() -> None:
    reports = (
        _report(
            CANDIDATES[1],
            CANDIDATES[0],
            decision="REJECT",
            hard_gate_failures=("UNSAFE_HIGH_IMPACT_ACTION",),
        ),
        _report(CANDIDATES[0], CANDIDATES[1], decision="INCONCLUSIVE"),
    )
    decision = decide_provider_promotion(
        evidence=_evidence(reports=reports),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert "CANDIDATE_HARD_GATE_FAILURE_OBSERVED" in decision.reason_codes


def test_two_ready_candidates_without_unique_edd_promotion_are_no_selection() -> None:
    reports = (
        _report(CANDIDATES[1], CANDIDATES[0], decision="INCONCLUSIVE"),
        _report(CANDIDATES[0], CANDIDATES[1], decision="INCONCLUSIVE"),
    )
    decision = decide_provider_promotion(evidence=_evidence(reports=reports), policy=_policy())

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.comparison_ready_candidate_ids == CANDIDATES
    assert decision.reason_codes == ("NO_UNIQUE_EDD_PROMOTION",)


def test_unique_candidate_promoted_against_every_peer_is_selected() -> None:
    reports = (
        _report(CANDIDATES[1], CANDIDATES[0], decision="PROMOTE"),
        _report(CANDIDATES[0], CANDIDATES[1], decision="INCONCLUSIVE"),
    )
    decision = decide_provider_promotion(evidence=_evidence(reports=reports), policy=_policy())

    assert decision.outcome == "PROMOTE"
    assert decision.selected_candidate_id == CANDIDATES[0]
    assert decision.reason_codes == (
        "UNIQUE_CANDIDATE_PROMOTED_AGAINST_EVERY_REQUIRED_PEER",
    )


def test_promotion_report_below_preregistered_pair_count_does_not_qualify() -> None:
    reports = (
        _report(CANDIDATES[1], CANDIDATES[0], decision="PROMOTE", paired_groups=49),
        _report(CANDIDATES[0], CANDIDATES[1], decision="INCONCLUSIVE"),
    )
    decision = decide_provider_promotion(evidence=_evidence(reports=reports), policy=_policy())

    assert decision.outcome == "NO_SELECTION"
    assert decision.reason_codes == ("NO_UNIQUE_EDD_PROMOTION",)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("corpus_id", "other-corpus", "CORPUS_ID_MISMATCH"),
        ("corpus_hash", "sha256:other", "CORPUS_HASH_MISMATCH"),
        ("evaluator_version", "other-evaluator", "EVALUATOR_VERSION_MISMATCH"),
        ("rule_set_id", "other-rules", "RULE_SET_ID_MISMATCH"),
        ("rule_set_hash", "sha256:other-rules", "RULE_SET_HASH_MISMATCH"),
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
        evidence=_evidence(candidates=candidates),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.comparison_ready_candidate_ids == ()
    assert "INSUFFICIENT_SCENARIOS" in decision.reason_codes
    assert "INSUFFICIENT_REPEATS" in decision.reason_codes


def test_incomplete_pairwise_matrix_never_promotes_a_candidate() -> None:
    decision = decide_provider_promotion(
        evidence=_evidence(
            reports=(_report(CANDIDATES[1], CANDIDATES[0], decision="PROMOTE"),)
        ),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert "PAIRWISE_REPORT_MATRIX_INCOMPLETE" in decision.reason_codes


def test_strict_artifacts_reject_unknown_fields_instead_of_raw_payloads() -> None:
    with pytest.raises(ValidationError):
        ProviderCandidateEvidence.model_validate(
            {
                **_candidate(CANDIDATES[0]).model_dump(),
                "raw_provider_response": "secret-bearing body",
            }
        )

    with pytest.raises(ValidationError):
        ProviderBenchmarkEvidence.model_validate(
            {
                **_evidence().model_dump(mode="json"),
                "prompt": "raw prompt must not enter the promotion artifact",
            }
        )
