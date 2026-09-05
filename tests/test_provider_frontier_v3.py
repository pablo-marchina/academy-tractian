from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from academy_tractian.eval_driven import EvalDrivenDecisionReport
from academy_tractian.provider_frontier_v3 import (
    EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256,
    ProviderFrontierEligibilityEvidence,
    ProviderFrontierManifestV3,
    build_provider_frontier_eligibility_artifact,
    decide_provider_frontier_v3,
)
from academy_tractian.provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderCandidateEvidence,
    ProviderPromotionPolicy,
    build_provider_human_calibration_artifact,
)


MANIFEST_PATH = Path("research/experiments/provider-model-frontier-preregistration-v3.json")
PROMOTABLE = (
    "google:gemini-3.8-flash",
    "groq:openai/gpt-oss-120b",
    "cloudflare:@cf/zai-org/glm-4.7-flash",
    "cloudflare:@cf/nvidia/nemotron-3-120b-a12b",
)
REFERENCE = "openai:gpt-5.6-sol"
WINNER = PROMOTABLE[0]
CODE_SHA = "abcdef1234567890"


def _manifest() -> ProviderFrontierManifestV3:
    return ProviderFrontierManifestV3.model_validate(json.loads(MANIFEST_PATH.read_text()))


def _human(candidate_id: str, *, ready: bool = True):
    return build_provider_human_calibration_artifact(
        candidate_id=candidate_id,
        config_hash=f"cfg-{candidate_id}",
        protocol_id="human-v1",
        protocol_hash="sha256:human-v1",
        source_manifest_sha256="1" * 64,
        annotation_manifest_sha256="2" * 64,
        resolution_report_sha256="3" * 64,
        calibration_ready=ready,
        case_count=60,
        human_agreement_rate=0.95,
        operational_conclusion_accuracy=0.93,
        operational_conclusion_accuracy_ci_low=0.86,
    )


def _candidate(candidate_id: str, *, human_ready: bool = True) -> ProviderCandidateEvidence:
    provider_id, model_id = candidate_id.split(":", 1)
    return ProviderCandidateEvidence(
        candidate_id=candidate_id,
        provider_id=provider_id,
        model_id=model_id,
        config_hash=f"cfg-{candidate_id}",
        scenario_count=60,
        repeat_count=3,
        human_calibration=_human(candidate_id, ready=human_ready),
    )


def _report(baseline: str, candidate: str, decision: str) -> EvalDrivenDecisionReport:
    return EvalDrivenDecisionReport.model_validate(
        {
            "baseline_config_id": baseline,
            "candidate_config_id": candidate,
            "comparison_id": "a" * 64,
            "paired_groups": tuple(f"group-{index}" for index in range(60)),
            "metric_deltas": (),
            "response_mode_slices": (),
            "candidate_hard_gate_failures": (),
            "comparison_issues": (),
            "decision": decision,
            "decision_reasons": ("test-fixture",),
        }
    )


def _complete_reports() -> tuple[EvalDrivenDecisionReport, ...]:
    reports: list[EvalDrivenDecisionReport] = []
    for baseline in PROMOTABLE:
        for candidate in PROMOTABLE:
            if baseline == candidate:
                continue
            reports.append(
                _report(
                    baseline,
                    candidate,
                    "PROMOTE" if candidate == WINNER else "INCONCLUSIVE",
                )
            )
    # A paid/reference-only model may look strong analytically but must never enter production selection.
    reports.append(_report(WINNER, REFERENCE, "PROMOTE"))
    reports.append(_report(REFERENCE, WINNER, "INCONCLUSIVE"))
    return tuple(reports)


def _benchmark(*, human_ready: bool = True) -> ProviderBenchmarkEvidence:
    return ProviderBenchmarkEvidence(
        corpus_id="golden-v1",
        corpus_hash="sha256:golden",
        evaluator_version="production-evaluator-v1",
        rule_set_id="provider-rules-v1",
        rule_set_hash="sha256:rules",
        human_calibration_protocol_id="human-v1",
        human_calibration_protocol_hash="sha256:human-v1",
        code_sha=CODE_SHA,
        generated_at=datetime(2026, 9, 4, tzinfo=UTC),
        candidates=tuple(
            _candidate(candidate_id, human_ready=human_ready)
            for candidate_id in (*PROMOTABLE, REFERENCE)
        ),
        pairwise_reports=_complete_reports(),
    )


def _policy() -> ProviderPromotionPolicy:
    return ProviderPromotionPolicy(
        required_candidate_ids=PROMOTABLE,
        expected_corpus_id="golden-v1",
        expected_corpus_hash="sha256:golden",
        expected_evaluator_version="production-evaluator-v1",
        expected_rule_set_id="provider-rules-v1",
        expected_rule_set_hash="sha256:rules",
        expected_human_calibration_protocol_id="human-v1",
        expected_human_calibration_protocol_hash="sha256:human-v1",
        expected_code_sha=CODE_SHA,
        min_scenarios=50,
        min_repeats=3,
        min_paired_groups=50,
        min_human_calibration_cases=50,
        min_human_agreement_rate=0.90,
        min_operational_conclusion_accuracy=0.90,
        min_operational_conclusion_accuracy_ci_low=0.80,
    )


def _eligibility(candidate_id: str, **overrides: object) -> ProviderFrontierEligibilityEvidence:
    payload: dict[str, object] = {
        "manifest_sha256": EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256,
        "candidate_id": candidate_id,
        "config_hash": f"cfg-{candidate_id}",
        "generated_at": datetime(2026, 9, 4, tzinfo=UTC),
        "hosted_only": True,
        "required_local_components": 0,
        "strict_usd0_eligible": True,
        "observed_cash_cost_usd": 0.0,
        "privacy_eligible": True,
        "live_evidence_complete": True,
        "live_attempt_count": 60,
        "qualification_source_sha256": "4" * 64,
    }
    payload.update(overrides)
    return build_provider_frontier_eligibility_artifact(**payload)  # type: ignore[arg-type]


def _all_eligibility(**candidate_overrides: dict[str, object]):
    return tuple(
        _eligibility(candidate_id, **candidate_overrides.get(candidate_id, {}))
        for candidate_id in PROMOTABLE
    )


def test_frozen_manifest_hash_matches_preregistered_source() -> None:
    manifest = _manifest()
    assert manifest.canonical_sha256 == EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256
    assert tuple(item.candidate_id for item in manifest.candidate_set if item.role == "promotable") == PROMOTABLE
    assert tuple(item.candidate_id for item in manifest.candidate_set if item.role == "reference_only") == (REFERENCE,)


def test_reference_only_candidate_cannot_win_even_with_promote_report() -> None:
    decision = decide_provider_frontier_v3(
        manifest=_manifest(),
        eligibility_evidence=_all_eligibility(),
        benchmark_evidence=_benchmark(),
        promotion_policy=_policy(),
    )

    assert decision.outcome == "PROMOTE"
    assert decision.selected_candidate_id == WINNER
    assert REFERENCE in decision.reference_only_candidate_ids
    assert REFERENCE not in decision.eligible_promotable_candidate_ids


@pytest.mark.parametrize(
    ("override", "reason"),
    [
        ({"hosted_only": False}, "HOSTED_ONLY_REQUIRED"),
        ({"required_local_components": 1}, "LOCAL_COMPONENT_REQUIRED"),
        ({"strict_usd0_eligible": False}, "USD0_INELIGIBLE"),
        ({"observed_cash_cost_usd": 0.01}, "NONZERO_CASH_COST_OBSERVED"),
        ({"privacy_eligible": False}, "PRIVACY_INELIGIBLE"),
        ({"live_evidence_complete": False}, "LIVE_EVIDENCE_INCOMPLETE"),
        ({"live_attempt_count": 0}, "LIVE_EVIDENCE_EMPTY"),
    ],
)
def test_noncompensatory_frontier_gate_excludes_candidate(
    override: dict[str, object],
    reason: str,
) -> None:
    target = PROMOTABLE[1]
    decision = decide_provider_frontier_v3(
        manifest=_manifest(),
        eligibility_evidence=_all_eligibility(**{target: override}),
        benchmark_evidence=_benchmark(),
        promotion_policy=_policy(),
    )

    assert target in decision.excluded_promotable_candidate_ids
    assert reason in decision.reason_codes
    assert decision.selected_candidate_id == WINNER


def test_less_than_two_eligible_promotables_is_no_selection() -> None:
    overrides = {
        candidate_id: {"live_evidence_complete": False}
        for candidate_id in PROMOTABLE[1:]
    }
    decision = decide_provider_frontier_v3(
        manifest=_manifest(),
        eligibility_evidence=_all_eligibility(**overrides),
        benchmark_evidence=_benchmark(),
        promotion_policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_candidate_id is None
    assert "INSUFFICIENT_ELIGIBLE_PROMOTABLES" in decision.reason_codes


def test_human_calibration_gate_remains_mandatory_after_frontier_filtering() -> None:
    decision = decide_provider_frontier_v3(
        manifest=_manifest(),
        eligibility_evidence=_all_eligibility(),
        benchmark_evidence=_benchmark(human_ready=False),
        promotion_policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.delegated_promotion is not None
    assert "HUMAN_SEMANTIC_CALIBRATION_REQUIRED" in decision.reason_codes


def test_manifest_tamper_fails_closed_before_promotion() -> None:
    payload = json.loads(MANIFEST_PATH.read_text())
    payload["date"] = "2026-09-05"
    tampered = ProviderFrontierManifestV3.model_validate(payload)
    decision = decide_provider_frontier_v3(
        manifest=tampered,
        eligibility_evidence=_all_eligibility(),
        benchmark_evidence=_benchmark(),
        promotion_policy=_policy(),
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.reason_codes == ("MANIFEST_HASH_MISMATCH",)


def test_promotion_policy_cannot_silently_drop_preregistered_challenger() -> None:
    payload = _policy().model_dump(mode="json")
    payload["required_candidate_ids"] = PROMOTABLE[:3]
    altered = ProviderPromotionPolicy.model_validate(payload)
    decision = decide_provider_frontier_v3(
        manifest=_manifest(),
        eligibility_evidence=_all_eligibility(),
        benchmark_evidence=_benchmark(),
        promotion_policy=altered,
    )

    assert decision.outcome == "NO_SELECTION"
    assert decision.reason_codes == ("PROMOTION_POLICY_FRONTIER_MISMATCH",)


def test_eligibility_is_bound_to_exact_runtime_config_hash() -> None:
    target = PROMOTABLE[1]
    decision = decide_provider_frontier_v3(
        manifest=_manifest(),
        eligibility_evidence=_all_eligibility(**{target: {"config_hash": "cfg-different"}}),
        benchmark_evidence=_benchmark(),
        promotion_policy=_policy(),
    )

    assert target in decision.excluded_promotable_candidate_ids
    assert "ELIGIBILITY_CONFIG_HASH_MISMATCH" in decision.reason_codes


def test_eligibility_artifact_detects_tampering_and_rejects_unknown_fields() -> None:
    artifact = _eligibility(PROMOTABLE[0])
    tampered = artifact.model_dump(mode="json")
    tampered["observed_cash_cost_usd"] = 1.0
    with pytest.raises(ValidationError, match="frontier_eligibility_artifact_hash_mismatch"):
        ProviderFrontierEligibilityEvidence.model_validate(tampered)

    with pytest.raises(ValidationError):
        ProviderFrontierEligibilityEvidence.model_validate(
            {**artifact.model_dump(mode="json"), "raw_provider_response": "forbidden"}
        )
