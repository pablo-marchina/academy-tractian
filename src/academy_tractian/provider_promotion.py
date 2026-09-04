from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .eval_driven import EvalDrivenDecisionReport


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderCandidateEvidence(_StrictModel):
    candidate_id: str = Field(min_length=1, max_length=128)
    provider_id: str = Field(min_length=1, max_length=64)
    model_id: str = Field(min_length=1, max_length=128)
    scenario_count: int = Field(ge=1)
    repeat_count: int = Field(ge=1)
    human_semantic_calibrated: bool
    human_calibration_case_count: int = Field(ge=0)
    human_agreement_rate: float = Field(ge=0.0, le=1.0)
    operational_conclusion_accuracy: float = Field(ge=0.0, le=1.0)
    operational_conclusion_accuracy_ci_low: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_calibration_statistics(self) -> "ProviderCandidateEvidence":
        if self.operational_conclusion_accuracy_ci_low > self.operational_conclusion_accuracy:
            raise ValueError("oca_ci_low_cannot_exceed_point_estimate")
        return self


class ProviderBenchmarkEvidence(_StrictModel):
    """Safe promotion envelope around existing Eval-Driven Development reports."""

    schema_version: Literal["provider-benchmark-v1"] = "provider-benchmark-v1"
    corpus_id: str = Field(min_length=1, max_length=256)
    corpus_hash: str = Field(min_length=1, max_length=256)
    evaluator_version: str = Field(min_length=1, max_length=128)
    rule_set_id: str = Field(min_length=1, max_length=128)
    rule_set_hash: str = Field(min_length=1, max_length=256)
    human_calibration_protocol_id: str = Field(min_length=1, max_length=128)
    human_calibration_protocol_hash: str = Field(min_length=1, max_length=256)
    code_sha: str = Field(min_length=7, max_length=64)
    generated_at: datetime
    candidates: tuple[ProviderCandidateEvidence, ...] = Field(min_length=2)
    pairwise_reports: tuple[EvalDrivenDecisionReport, ...] = ()

    @model_validator(mode="after")
    def validate_candidate_and_report_ids(self) -> "ProviderBenchmarkEvidence":
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate_candidate_id")
        known = set(ids)
        pairs: set[tuple[str, str]] = set()
        for report in self.pairwise_reports:
            pair = (report.baseline_config_id, report.candidate_config_id)
            if pair[0] not in known or pair[1] not in known:
                raise ValueError("pairwise_report_unknown_candidate")
            if pair[0] == pair[1]:
                raise ValueError("pairwise_report_requires_distinct_candidates")
            if pair in pairs:
                raise ValueError("duplicate_pairwise_report")
            pairs.add(pair)
        return self


class ProviderPromotionPolicy(_StrictModel):
    """Preregistered provenance and maturity gates for provider/model promotion.

    Statistical metric thresholds remain in ``EvalMetricRule`` and are evaluated
    by ``compare_eval_bundles``. Human calibration is deliberately quantitative:
    sample size, human agreement, OCA and the OCA lower confidence bound are hard
    maturity gates rather than a subjective production-readiness label.
    """

    schema_version: Literal["provider-promotion-policy-v1"] = "provider-promotion-policy-v1"
    required_candidate_ids: tuple[str, ...] = Field(min_length=2)
    expected_corpus_id: str = Field(min_length=1, max_length=256)
    expected_corpus_hash: str = Field(min_length=1, max_length=256)
    expected_evaluator_version: str = Field(min_length=1, max_length=128)
    expected_rule_set_id: str = Field(min_length=1, max_length=128)
    expected_rule_set_hash: str = Field(min_length=1, max_length=256)
    expected_human_calibration_protocol_id: str = Field(min_length=1, max_length=128)
    expected_human_calibration_protocol_hash: str = Field(min_length=1, max_length=256)
    expected_code_sha: str = Field(min_length=7, max_length=64)
    min_scenarios: int = Field(ge=1)
    min_repeats: int = Field(ge=1)
    min_paired_groups: int = Field(ge=1)
    min_human_calibration_cases: int = Field(ge=1)
    min_human_agreement_rate: float = Field(ge=0.0, le=1.0)
    min_operational_conclusion_accuracy: float = Field(ge=0.0, le=1.0)
    min_operational_conclusion_accuracy_ci_low: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_required_candidates(self) -> "ProviderPromotionPolicy":
        if len(self.required_candidate_ids) != len(set(self.required_candidate_ids)):
            raise ValueError("duplicate_required_candidate_id")
        if any(not candidate_id.strip() for candidate_id in self.required_candidate_ids):
            raise ValueError("blank_required_candidate_id")
        if (
            self.min_operational_conclusion_accuracy_ci_low
            > self.min_operational_conclusion_accuracy
        ):
            raise ValueError("minimum_oca_ci_low_cannot_exceed_minimum_oca")
        return self


PromotionOutcome = Literal["PROMOTE", "NO_SELECTION"]


class ProviderPromotionDecision(_StrictModel):
    schema_version: Literal["provider-promotion-decision-v1"] = "provider-promotion-decision-v1"
    outcome: PromotionOutcome
    selected_candidate_id: str | None
    comparison_ready_candidate_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    statistical_source: Literal["eval-driven-decision-v1"] = "eval-driven-decision-v1"


def decide_provider_promotion(
    *,
    evidence: ProviderBenchmarkEvidence,
    policy: ProviderPromotionPolicy,
) -> ProviderPromotionDecision:
    """Select only a unique candidate that EDD promoted against every peer.

    The function is deliberately fail-closed. It never creates a composite score,
    never promotes the first candidate that passes, and never treats latency/cost
    as a correctness substitute. All metric thresholds, regressions, response-mode
    slices, bootstrap confidence intervals, and hard gates are inherited from the
    existing ``EvalDrivenDecisionReport`` objects. Human semantic readiness is an
    additional preregistered quantitative maturity gate.
    """

    provenance_reasons: list[str] = []
    expected_pairs = (
        (evidence.corpus_id, policy.expected_corpus_id, "CORPUS_ID_MISMATCH"),
        (evidence.corpus_hash, policy.expected_corpus_hash, "CORPUS_HASH_MISMATCH"),
        (evidence.evaluator_version, policy.expected_evaluator_version, "EVALUATOR_VERSION_MISMATCH"),
        (evidence.rule_set_id, policy.expected_rule_set_id, "RULE_SET_ID_MISMATCH"),
        (evidence.rule_set_hash, policy.expected_rule_set_hash, "RULE_SET_HASH_MISMATCH"),
        (
            evidence.human_calibration_protocol_id,
            policy.expected_human_calibration_protocol_id,
            "HUMAN_CALIBRATION_PROTOCOL_ID_MISMATCH",
        ),
        (
            evidence.human_calibration_protocol_hash,
            policy.expected_human_calibration_protocol_hash,
            "HUMAN_CALIBRATION_PROTOCOL_HASH_MISMATCH",
        ),
        (evidence.code_sha, policy.expected_code_sha, "CODE_SHA_MISMATCH"),
    )
    for actual, expected, reason in expected_pairs:
        if actual != expected:
            provenance_reasons.append(reason)

    candidates = {candidate.candidate_id: candidate for candidate in evidence.candidates}
    required = set(policy.required_candidate_ids)
    if required.difference(candidates):
        provenance_reasons.append("REQUIRED_CANDIDATE_MISSING")

    if provenance_reasons:
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            comparison_ready_candidate_ids=(),
            reason_codes=tuple(dict.fromkeys(provenance_reasons)),
        )

    maturity_reasons: list[str] = []
    for candidate_id in policy.required_candidate_ids:
        candidate = candidates[candidate_id]
        if not candidate.human_semantic_calibrated:
            maturity_reasons.append("HUMAN_SEMANTIC_CALIBRATION_REQUIRED")
        if candidate.human_calibration_case_count < policy.min_human_calibration_cases:
            maturity_reasons.append("INSUFFICIENT_HUMAN_CALIBRATION_CASES")
        if candidate.human_agreement_rate < policy.min_human_agreement_rate:
            maturity_reasons.append("HUMAN_AGREEMENT_BELOW_THRESHOLD")
        if (
            candidate.operational_conclusion_accuracy
            < policy.min_operational_conclusion_accuracy
        ):
            maturity_reasons.append("OCA_BELOW_THRESHOLD")
        if (
            candidate.operational_conclusion_accuracy_ci_low
            < policy.min_operational_conclusion_accuracy_ci_low
        ):
            maturity_reasons.append("OCA_CONFIDENCE_LOWER_BOUND_BELOW_THRESHOLD")
        if candidate.scenario_count < policy.min_scenarios:
            maturity_reasons.append("INSUFFICIENT_SCENARIOS")
        if candidate.repeat_count < policy.min_repeats:
            maturity_reasons.append("INSUFFICIENT_REPEATS")
    if maturity_reasons:
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            comparison_ready_candidate_ids=(),
            reason_codes=tuple(dict.fromkeys(maturity_reasons)),
        )

    comparison_ready = tuple(policy.required_candidate_ids)
    report_by_pair = {
        (report.baseline_config_id, report.candidate_config_id): report
        for report in evidence.pairwise_reports
    }
    required_pairs = {
        (baseline_id, candidate_id)
        for candidate_id in policy.required_candidate_ids
        for baseline_id in policy.required_candidate_ids
        if baseline_id != candidate_id
    }
    if not required_pairs.issubset(report_by_pair):
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            comparison_ready_candidate_ids=comparison_ready,
            reason_codes=("PAIRWISE_REPORT_MATRIX_INCOMPLETE",),
        )

    def promoted_against(candidate_id: str, baseline_id: str) -> bool:
        report = report_by_pair[(baseline_id, candidate_id)]
        return bool(
            report.decision == "PROMOTE"
            and len(report.paired_groups) >= policy.min_paired_groups
            and not report.comparison_issues
            and not report.candidate_hard_gate_failures
        )

    evidence_backed_winners = tuple(
        candidate_id
        for candidate_id in policy.required_candidate_ids
        if all(
            promoted_against(candidate_id, other_id)
            for other_id in policy.required_candidate_ids
            if other_id != candidate_id
        )
    )

    if len(evidence_backed_winners) != 1:
        reasons = ["NO_UNIQUE_EDD_PROMOTION"]
        if any(report.candidate_hard_gate_failures for report in evidence.pairwise_reports):
            reasons.append("CANDIDATE_HARD_GATE_FAILURE_OBSERVED")
        if any(report.comparison_issues for report in evidence.pairwise_reports):
            reasons.append("PAIRWISE_COMPARISON_ISSUE_OBSERVED")
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            comparison_ready_candidate_ids=comparison_ready,
            reason_codes=tuple(reasons),
        )

    return ProviderPromotionDecision(
        outcome="PROMOTE",
        selected_candidate_id=evidence_backed_winners[0],
        comparison_ready_candidate_ids=comparison_ready,
        reason_codes=("UNIQUE_CANDIDATE_PROMOTED_AGAINST_EVERY_REQUIRED_PEER",),
    )
