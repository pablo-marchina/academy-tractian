from __future__ import annotations

import hashlib
import json

from academy_tractian.semantic_evaluation import (
    HumanSemanticReference,
    JudgeSemanticObservation,
    SemanticCalibrationAcceptancePolicy,
    calibrate_semantic_judge,
    semantic_rubric_v1,
)


def _hash(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _output_hash(seed: str) -> str:
    return _hash(seed)


def _context_hash(seed: str) -> str:
    return _hash(f"context:{seed}")


def _perfect_records():
    rubric = semantic_rubric_v1()
    output_sha = _output_hash("safe-output")
    context_sha = _context_hash("safe-evidence")
    human = []
    judge = []
    for dimension in (
        "groundedness",
        "operational_usefulness",
        "customer_safe_clarity",
        "escalation_quality",
    ):
        human.append(
            HumanSemanticReference(
                scenario_id="public-scenario-1",
                output_sha256=output_sha,
                context_sha256=context_sha,
                response_mode="escalation" if dimension == "escalation_quality" else "complete",
                dimension=dimension,
                score=2,
                resolution="AGREED",
                annotator_count=2,
            )
        )
        judge.append(
            JudgeSemanticObservation(
                scenario_id="public-scenario-1",
                output_sha256=output_sha,
                context_sha256=context_sha,
                response_mode="escalation" if dimension == "escalation_quality" else "complete",
                dimension=dimension,
                judge_id="candidate-judge-v1",
                rubric_sha256=rubric.rubric_sha256,
                valid=True,
                score=2,
            )
        )
    return human, judge


def _explicit_perfect_policy() -> SemanticCalibrationAcceptancePolicy:
    return SemanticCalibrationAcceptancePolicy(
        policy_id="test-explicit-perfect-only",
        minimum_pairs_per_dimension=1,
        minimum_exact_agreement=1.0,
        minimum_quadratic_weighted_kappa=1.0,
        maximum_mean_absolute_error=0.0,
        maximum_false_pass_rate=0.0,
        maximum_invalid_rate=0.0,
    )


def test_rubric_is_versioned_stable_and_small() -> None:
    first = semantic_rubric_v1()
    second = semantic_rubric_v1()

    assert first.rubric_sha256 == second.rubric_sha256
    assert len(first.rubric_sha256) == 64
    assert [criterion.dimension for criterion in first.criteria] == [
        "groundedness",
        "operational_usefulness",
        "customer_safe_clarity",
        "escalation_quality",
    ]
    assert first.criteria[-1].applicability == "ESCALATION_ONLY"


def test_matched_human_and_judge_labels_are_descriptive_without_policy() -> None:
    human, judge = _perfect_records()
    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
    )

    assert report.state == "DESCRIPTIVE_ONLY"
    assert report.gate_authorized is False
    assert report.acceptance_policy_id is None
    assert report.gate_failures == ()
    assert report.valid_pairs == 4
    assert all(metric.exact_agreement == 1.0 for metric in report.dimension_metrics)


def test_explicit_policy_is_required_and_can_authorize_only_when_satisfied() -> None:
    human, judge = _perfect_records()
    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=_explicit_perfect_policy(),
    )

    assert report.state == "CALIBRATED_GATE"
    assert report.gate_authorized is True
    assert report.acceptance_policy_id == "test-explicit-perfect-only"
    assert report.gate_failures == ()


def test_wrong_score_fails_explicit_policy_and_stays_descriptive() -> None:
    human, judge = _perfect_records()
    judge[0] = judge[0].model_copy(update={"score": 0})

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=_explicit_perfect_policy(),
    )

    assert report.state == "DESCRIPTIVE_ONLY"
    assert report.gate_authorized is False
    assert "GROUNDEDNESS_EXACT_AGREEMENT_BELOW_MINIMUM" in report.gate_failures
    assert "GROUNDEDNESS_KAPPA_BELOW_MINIMUM" in report.gate_failures
    assert "GROUNDEDNESS_MAE_ABOVE_MAXIMUM" in report.gate_failures


def test_unresolved_human_label_fails_closed() -> None:
    human, judge = _perfect_records()
    human[1] = human[1].model_copy(update={"resolution": "UNRESOLVED"})

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=_explicit_perfect_policy(),
    )

    assert report.state == "NOT_CALIBRATED"
    assert report.gate_authorized is False
    assert "UNRESOLVED_HUMAN_LABELS" in report.gate_failures
    assert report.unresolved_human_keys


def test_mismatched_response_mode_is_not_same_calibration_key() -> None:
    human, judge = _perfect_records()
    judge[0] = judge[0].model_copy(update={"response_mode": "partial"})

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=_explicit_perfect_policy(),
    )

    assert report.state == "NOT_CALIBRATED"
    assert report.gate_authorized is False
    assert "CALIBRATION_KEY_SET_MISMATCH" in report.gate_failures


def test_same_output_under_different_evidence_context_is_not_same_calibration_key() -> None:
    human, judge = _perfect_records()
    judge[0] = judge[0].model_copy(update={"context_sha256": _context_hash("different-evidence")})

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=_explicit_perfect_policy(),
    )

    assert report.state == "NOT_CALIBRATED"
    assert report.gate_authorized is False
    assert "CALIBRATION_KEY_SET_MISMATCH" in report.gate_failures
    assert report.unmatched_human_keys
    assert report.unmatched_judge_keys


def test_invalid_judge_output_is_measured_and_cannot_pass_zero_invalid_policy() -> None:
    human, judge = _perfect_records()
    judge[2] = JudgeSemanticObservation(
        scenario_id=judge[2].scenario_id,
        output_sha256=judge[2].output_sha256,
        context_sha256=judge[2].context_sha256,
        response_mode=judge[2].response_mode,
        dimension=judge[2].dimension,
        judge_id=judge[2].judge_id,
        rubric_sha256=judge[2].rubric_sha256,
        valid=False,
        error_code="SCHEMA_INVALID",
    )

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
        acceptance_policy=_explicit_perfect_policy(),
    )

    clarity = next(
        metric
        for metric in report.dimension_metrics
        if metric.dimension == "customer_safe_clarity"
    )
    assert clarity.invalid_rate == 1.0
    assert report.state == "DESCRIPTIVE_ONLY"
    assert report.gate_authorized is False
    assert "CUSTOMER_SAFE_CLARITY_INVALID_RATE_ABOVE_MAXIMUM" in report.gate_failures


def test_rubric_hash_mismatch_fails_closed() -> None:
    human, judge = _perfect_records()
    judge[0] = judge[0].model_copy(update={"rubric_sha256": "f" * 64})

    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
    )

    assert report.state == "NOT_CALIBRATED"
    assert "JUDGE_RUBRIC_HASH_MISMATCH" in report.gate_failures


def test_contract_cannot_serialize_raw_material_or_private_runtime_fields() -> None:
    human, judge = _perfect_records()
    report = calibrate_semantic_judge(
        human_references=human,
        judge_observations=judge,
    )
    serialized = json.dumps(
        {
            "rubric": semantic_rubric_v1().model_dump(mode="json"),
            "human": [item.model_dump(mode="json") for item in human],
            "judge": [item.model_dump(mode="json") for item in judge],
            "report": report.model_dump(mode="json"),
        },
        sort_keys=True,
    ).lower()

    for forbidden in (
        "chain_of_thought",
        "raw_prompt",
        "raw_response",
        "authorization",
        "api_token",
        "account_id",
        "identity_id",
        "user_id",
        "seed_ref",
        "gold_answer",
    ):
        assert forbidden not in serialized