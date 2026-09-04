from __future__ import annotations

from datetime import UTC, datetime

from academy_tractian.provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderCandidateEvidence,
    ProviderPromotionPolicy,
    decide_provider_promotion,
)


def test_missing_human_calibration_is_representable_and_fails_closed() -> None:
    candidate_ids = ("provider-a:model-a", "provider-b:model-b")
    candidates = tuple(
        ProviderCandidateEvidence(
            candidate_id=candidate_id,
            provider_id=candidate_id.split(":", 1)[0],
            model_id=candidate_id.split(":", 1)[1],
            scenario_count=60,
            repeat_count=3,
            human_calibration=None,
        )
        for candidate_id in candidate_ids
    )
    evidence = ProviderBenchmarkEvidence(
        corpus_id="golden-v1",
        corpus_hash="sha256:golden",
        evaluator_version="production-evaluator-v1",
        rule_set_id="provider-rules-v1",
        rule_set_hash="sha256:rules",
        human_calibration_protocol_id="provider-human-oca-v1",
        human_calibration_protocol_hash="a" * 64,
        code_sha="abcdef1234567890",
        generated_at=datetime(2026, 9, 4, tzinfo=UTC),
        candidates=candidates,
        pairwise_reports=(),
    )
    policy = ProviderPromotionPolicy(
        required_candidate_ids=candidate_ids,
        expected_corpus_id="golden-v1",
        expected_corpus_hash="sha256:golden",
        expected_evaluator_version="production-evaluator-v1",
        expected_rule_set_id="provider-rules-v1",
        expected_rule_set_hash="sha256:rules",
        expected_human_calibration_protocol_id="provider-human-oca-v1",
        expected_human_calibration_protocol_hash="a" * 64,
        expected_code_sha="abcdef1234567890",
        min_scenarios=50,
        min_repeats=3,
        min_paired_groups=50,
        min_human_calibration_cases=50,
        min_human_agreement_rate=0.90,
        min_operational_conclusion_accuracy=0.90,
        min_operational_conclusion_accuracy_ci_low=0.80,
    )

    decision = decide_provider_promotion(evidence=evidence, policy=policy)

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert decision.comparison_ready_candidate_ids == ()
    assert decision.reason_codes == ("HUMAN_SEMANTIC_CALIBRATION_REQUIRED",)
