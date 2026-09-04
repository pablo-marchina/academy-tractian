from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.eval_driven import EvalDrivenDecisionReport
from academy_tractian.provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderCandidateEvidence,
    ProviderHumanCalibrationEvidence,
    ProviderPromotionPolicy,
    build_provider_human_calibration_artifact,
    decide_provider_promotion,
)


CANDIDATES = ("openai:gpt-5.6-sol", "google:gemini-3.7-flash")
CODE_SHA = "abcdef1234567890"


def _human_calibration(
    candidate_id: str,
    **overrides: object,
) -> ProviderHumanCalibrationEvidence:
    payload: dict[str, object] = {
        "candidate_id": candidate_id,
        "config_hash": f"cfg-{candidate_id}",
        "protocol_id": "human-calibration-v1",
        "protocol_hash": "sha256:human-calibration-v1",
        "source_manifest_sha256": "1" * 64,
        "annotation_manifest_sha256": "2" * 64,
        "resolution_report_sha256": "3" * 64,
        "calibration_ready": True,
        "case_count": 60,
        "human_agreement_rate": 0.95,
        "operational_conclusion_accuracy": 0.93,
        "operational_conclusion_accuracy_ci_low": 0.86,
    }
    payload.update(overrides)
    return build_provider_human_calibration_artifact(**payload)  # type: ignore[arg-type]


def _candidate(
    candidate_id: str,
    *,
    human_overrides: dict[str, object] | None = None,
    **overrides: object,
) -> ProviderCandidateEvidence:
    provider_id, model_id = candidate_id.split(":", 1)
    payload: dict[str, object] = {
        "candidate_id": candidate_id,
        "provider_id": provider_id,
        "model_id": model_id,
        "scenario_count": 60,
        "repeat_count": 3,
        "human_calibration": _human_calibration(
            candidate_id,
            **(human_overrides or {}),
        ),
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
        "expected_human_calibration_protocol_id": "human-calibration-v1",
        "expected_human_calibration_protocol_hash": "sha256:human-calibration-v1",
        "expected_code_sha": CODE_SHA,
        "min_scenarios": 50,
        "min_repeats": 3,
        "min_paired_groups": 50,
        "min_human_calibration_cases": 50,
        "min_human_agreement_rate": 0.90,
        "min_operational_conclusion_accuracy": 0.90,
        "min_operational_conclusion_accuracy_ci_low": 0.80,
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
        "human_calibration_protocol_id": "human-calibration-v1",
        "human_calibration_protocol_hash": "sha256:human-calibration-v1",
        "code_sha": CODE_SHA,
        "generated_at": datetime(2026, 9, 4, tzinfo=UTC),
        "candidates": candidates
        or tuple(_candidate(candidate_id) for candidate_id in CANDIDATES),
        "pairwise_reports": reports,
    }
    payload.update(overrides)
    return ProviderBenchmarkEvidence.model_validate(payload)


def _winning_reports() -> tuple[EvalDrivenDecisionReport, ...]:
    return (
        _report(CANDIDATES[1], CANDIDATES[0], decision="PROMOTE"),
        _report(CANDIDATES[0], CANDIDATES[1], decision="INCONCLUSIVE"),
    )


def test_missing_human_semantic_calibration_invalidates_comparison() -> None:
    candidates = (
        _candidate(CANDIDATES[0], human_overrides={"calibration_ready": False}),
        _candidate(CANDIDATES[1]),
    )
    decision = decide_provider_promotion(
        evidence=_evidence(candidates=candidates, reports=_winning_reports()),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.comparison_ready_candidate_ids == ()
    assert decision.reason_codes == ("HUMAN_SEMANTIC_CALIBRATION_REQUIRED",)


@pytest.mark.parametrize(
    ("human_override", "reason"),
    [
        ({"case_count": 49}, "INSUFFICIENT_HUMAN_CALIBRATION_CASES"),
        ({"human_agreement_rate": 0.89}, "HUMAN_AGREEMENT_BELOW_THRESHOLD"),
        (
            {
                "operational_conclusion_accuracy": 0.89,
                "operational_conclusion_accuracy_ci_low": 0.79,
            },
            "OCA_BELOW_THRESHOLD",
        ),
        (
            {"operational_conclusion_accuracy_ci_low": 0.79},
            "OCA_CONFIDENCE_LOWER_BOUND_BELOW_THRESHOLD",
        ),
    ],
)
def test_quantitative_human_calibration_gates_block_promotion(
    human_override: dict[str, object],
    reason: str,
) -> None:
    candidates = (
        _candidate(CANDIDATES[0], human_overrides=human_override),
        _candidate(CANDIDATES[1]),
    )
    decision = decide_provider_promotion(
        evidence=_evidence(candidates=candidates, reports=_winning_reports()),
        policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.comparison_ready_candidate_ids == ()
    assert reason in decision.reason_codes


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
    decision = decide_provider_promotion(
        evidence=_evidence(reports=_winning_reports()),
        policy=_policy(),
    )

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
        (
            "human_calibration_protocol_id",
            "other-human-protocol",
            "HUMAN_CALIBRATION_PROTOCOL_ID_MISMATCH",
        ),
        (
            "human_calibration_protocol_hash",
            "sha256:other-human-protocol",
            "HUMAN_CALIBRATION_PROTOCOL_HASH_MISMATCH",
        ),
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


def test_candidate_human_protocol_must_match_benchmark_protocol() -> None:
    candidates = (
        _candidate(CANDIDATES[0], human_overrides={"protocol_id": "different-protocol"}),
        _candidate(CANDIDATES[1]),
    )

    with pytest.raises(ValidationError, match="candidate_human_calibration_protocol_id_mismatch"):
        _evidence(candidates=candidates)


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


def test_invalid_oca_confidence_bound_is_rejected_by_schema() -> None:
    with pytest.raises(ValidationError, match="oca_ci_low_cannot_exceed_point_estimate"):
        _human_calibration(
            CANDIDATES[0],
            operational_conclusion_accuracy=0.80,
            operational_conclusion_accuracy_ci_low=0.81,
        )


def test_human_calibration_artifact_detects_metric_tampering() -> None:
    artifact = _human_calibration(CANDIDATES[0])
    tampered = artifact.model_dump(mode="json")
    tampered["operational_conclusion_accuracy"] = 0.99

    with pytest.raises(
        ValidationError,
        match="provider_human_calibration_artifact_hash_mismatch",
    ):
        ProviderHumanCalibrationEvidence.model_validate(tampered)


def test_candidate_cannot_reference_another_candidates_human_artifact() -> None:
    with pytest.raises(ValidationError, match="human_calibration_candidate_id_mismatch"):
        ProviderCandidateEvidence.model_validate(
            {
                "candidate_id": CANDIDATES[0],
                "provider_id": "openai",
                "model_id": "gpt-5.6-sol",
                "scenario_count": 60,
                "repeat_count": 3,
                "human_calibration": _human_calibration(CANDIDATES[1]).model_dump(mode="json"),
            }
        )


def test_strict_artifacts_reject_unknown_fields_instead_of_raw_payloads() -> None:
    with pytest.raises(ValidationError):
        ProviderHumanCalibrationEvidence.model_validate(
            {
                **_human_calibration(CANDIDATES[0]).model_dump(mode="json"),
                "raw_human_notes": "must never enter promotion artifact",
            }
        )

    with pytest.raises(ValidationError):
        ProviderBenchmarkEvidence.model_validate(
            {
                **_evidence().model_dump(mode="json"),
                "prompt": "raw prompt must not enter the promotion artifact",
            }
        )
