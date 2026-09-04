from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PRIMARY_METRIC = "operational_conclusion_accuracy"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CandidateBenchmark(_StrictModel):
    candidate_id: str = Field(min_length=1, max_length=128)
    provider_id: str = Field(min_length=1, max_length=64)
    model_id: str = Field(min_length=1, max_length=128)
    scenario_count: int = Field(ge=1)
    repeat_count: int = Field(ge=1)
    human_semantic_calibrated: bool
    operational_conclusion_accuracy: float = Field(ge=0.0, le=1.0)
    tool_choice_accuracy: float = Field(ge=0.0, le=1.0)
    argument_validity_rate: float = Field(ge=0.0, le=1.0)
    evidence_grounding_rate: float = Field(ge=0.0, le=1.0)
    failure_behavior_pass_rate: float = Field(ge=0.0, le=1.0)
    stability_rate: float = Field(ge=0.0, le=1.0)
    critical_safety_failures: int = Field(ge=0)
    high_impact_action_failures: int = Field(ge=0)


class PairedPrimaryComparison(_StrictModel):
    winner_id: str = Field(min_length=1, max_length=128)
    loser_id: str = Field(min_length=1, max_length=128)
    metric: Literal["operational_conclusion_accuracy"] = PRIMARY_METRIC
    effect: float = Field(ge=-1.0, le=1.0)
    confidence_interval_low: float = Field(ge=-1.0, le=1.0)
    confidence_interval_high: float = Field(ge=-1.0, le=1.0)
    paired_scenarios: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_pair(self) -> "PairedPrimaryComparison":
        if self.winner_id == self.loser_id:
            raise ValueError("paired_comparison_requires_distinct_candidates")
        if self.confidence_interval_low > self.confidence_interval_high:
            raise ValueError("paired_comparison_invalid_confidence_interval")
        return self


class ProviderBenchmarkEvidence(_StrictModel):
    schema_version: Literal["provider-benchmark-v1"] = "provider-benchmark-v1"
    corpus_id: str = Field(min_length=1, max_length=256)
    corpus_hash: str = Field(min_length=1, max_length=256)
    evaluator_version: str = Field(min_length=1, max_length=128)
    code_sha: str = Field(min_length=7, max_length=64)
    generated_at: datetime
    candidates: tuple[CandidateBenchmark, ...] = Field(min_length=2)
    paired_primary_comparisons: tuple[PairedPrimaryComparison, ...] = ()

    @model_validator(mode="after")
    def validate_candidate_ids(self) -> "ProviderBenchmarkEvidence":
        ids = [candidate.candidate_id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate_candidate_id")
        known = set(ids)
        for comparison in self.paired_primary_comparisons:
            if comparison.winner_id not in known or comparison.loser_id not in known:
                raise ValueError("paired_comparison_unknown_candidate")
        return self


class ProviderPromotionPolicy(_StrictModel):
    schema_version: Literal["provider-promotion-policy-v1"] = "provider-promotion-policy-v1"
    required_candidate_ids: tuple[str, ...] = Field(min_length=2)
    expected_corpus_id: str = Field(min_length=1, max_length=256)
    expected_corpus_hash: str = Field(min_length=1, max_length=256)
    expected_evaluator_version: str = Field(min_length=1, max_length=128)
    expected_code_sha: str = Field(min_length=7, max_length=64)
    min_scenarios: int = Field(ge=1)
    min_repeats: int = Field(ge=1)
    min_paired_scenarios: int = Field(ge=1)
    min_operational_conclusion_accuracy: float = Field(ge=0.0, le=1.0)
    min_tool_choice_accuracy: float = Field(ge=0.0, le=1.0)
    min_argument_validity_rate: float = Field(ge=0.0, le=1.0)
    min_evidence_grounding_rate: float = Field(ge=0.0, le=1.0)
    min_failure_behavior_pass_rate: float = Field(ge=0.0, le=1.0)
    min_stability_rate: float = Field(ge=0.0, le=1.0)
    preregistered_primary_margin: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_required_candidates(self) -> "ProviderPromotionPolicy":
        if len(self.required_candidate_ids) != len(set(self.required_candidate_ids)):
            raise ValueError("duplicate_required_candidate_id")
        if any(not candidate_id.strip() for candidate_id in self.required_candidate_ids):
            raise ValueError("blank_required_candidate_id")
        return self


PromotionOutcome = Literal["PROMOTE", "NO_SELECTION"]


class ProviderPromotionDecision(_StrictModel):
    schema_version: Literal["provider-promotion-decision-v1"] = "provider-promotion-decision-v1"
    outcome: PromotionOutcome
    selected_candidate_id: str | None
    qualified_candidate_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    primary_metric: Literal["operational_conclusion_accuracy"] = PRIMARY_METRIC


def _candidate_threshold_failures(
    candidate: CandidateBenchmark,
    policy: ProviderPromotionPolicy,
) -> tuple[str, ...]:
    failures: list[str] = []
    if not candidate.human_semantic_calibrated:
        failures.append("HUMAN_SEMANTIC_CALIBRATION_REQUIRED")
    if candidate.scenario_count < policy.min_scenarios:
        failures.append("INSUFFICIENT_SCENARIOS")
    if candidate.repeat_count < policy.min_repeats:
        failures.append("INSUFFICIENT_REPEATS")
    if candidate.critical_safety_failures:
        failures.append("CRITICAL_SAFETY_FAILURE")
    if candidate.high_impact_action_failures:
        failures.append("HIGH_IMPACT_ACTION_FAILURE")
    if candidate.operational_conclusion_accuracy < policy.min_operational_conclusion_accuracy:
        failures.append("OCA_BELOW_THRESHOLD")
    if candidate.tool_choice_accuracy < policy.min_tool_choice_accuracy:
        failures.append("TOOL_CHOICE_BELOW_THRESHOLD")
    if candidate.argument_validity_rate < policy.min_argument_validity_rate:
        failures.append("ARGUMENT_VALIDITY_BELOW_THRESHOLD")
    if candidate.evidence_grounding_rate < policy.min_evidence_grounding_rate:
        failures.append("EVIDENCE_GROUNDING_BELOW_THRESHOLD")
    if candidate.failure_behavior_pass_rate < policy.min_failure_behavior_pass_rate:
        failures.append("FAILURE_BEHAVIOR_BELOW_THRESHOLD")
    if candidate.stability_rate < policy.min_stability_rate:
        failures.append("STABILITY_BELOW_THRESHOLD")
    return tuple(failures)


def decide_provider_promotion(
    *,
    evidence: ProviderBenchmarkEvidence,
    policy: ProviderPromotionPolicy,
) -> ProviderPromotionDecision:
    """Return a fail-closed, evidence-backed provider/model promotion decision.

    There is deliberately no composite score. Safety is a hard constraint, the
    primary correctness comparison is paired by scenario, and ambiguity resolves
    to ``NO_SELECTION`` rather than an arbitrary winner.
    """

    reason_codes: list[str] = []
    if evidence.corpus_id != policy.expected_corpus_id:
        reason_codes.append("CORPUS_ID_MISMATCH")
    if evidence.corpus_hash != policy.expected_corpus_hash:
        reason_codes.append("CORPUS_HASH_MISMATCH")
    if evidence.evaluator_version != policy.expected_evaluator_version:
        reason_codes.append("EVALUATOR_VERSION_MISMATCH")
    if evidence.code_sha != policy.expected_code_sha:
        reason_codes.append("CODE_SHA_MISMATCH")

    candidates = {candidate.candidate_id: candidate for candidate in evidence.candidates}
    required = set(policy.required_candidate_ids)
    missing = required.difference(candidates)
    if missing:
        reason_codes.append("REQUIRED_CANDIDATE_MISSING")

    if reason_codes:
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            qualified_candidate_ids=(),
            reason_codes=tuple(dict.fromkeys(reason_codes)),
        )

    threshold_failures: dict[str, tuple[str, ...]] = {}
    for candidate_id in policy.required_candidate_ids:
        failures = _candidate_threshold_failures(candidates[candidate_id], policy)
        if failures:
            threshold_failures[candidate_id] = failures

    qualified = tuple(
        candidate_id
        for candidate_id in policy.required_candidate_ids
        if candidate_id not in threshold_failures
    )
    if not qualified:
        candidate_reasons = [
            reason
            for candidate_id in policy.required_candidate_ids
            for reason in threshold_failures.get(candidate_id, ())
        ]
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            qualified_candidate_ids=(),
            reason_codes=tuple(dict.fromkeys(candidate_reasons or ["NO_CANDIDATE_PASSED_HARD_GATES"])),
        )

    comparisons = evidence.paired_primary_comparisons

    def has_superiority(winner_id: str, loser_id: str) -> bool:
        return any(
            comparison.winner_id == winner_id
            and comparison.loser_id == loser_id
            and comparison.metric == PRIMARY_METRIC
            and comparison.paired_scenarios >= policy.min_paired_scenarios
            and comparison.confidence_interval_low > policy.preregistered_primary_margin
            for comparison in comparisons
        )

    evidence_backed_winners = tuple(
        candidate_id
        for candidate_id in qualified
        if all(
            has_superiority(candidate_id, other_id)
            for other_id in policy.required_candidate_ids
            if other_id != candidate_id
        )
    )

    if len(evidence_backed_winners) != 1:
        reasons = ["NO_UNIQUE_PAIRED_SUPERIORITY"]
        if threshold_failures:
            reasons.extend(
                reason
                for candidate_id in policy.required_candidate_ids
                for reason in threshold_failures.get(candidate_id, ())
            )
        return ProviderPromotionDecision(
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            qualified_candidate_ids=qualified,
            reason_codes=tuple(dict.fromkeys(reasons)),
        )

    selected = evidence_backed_winners[0]
    return ProviderPromotionDecision(
        outcome="PROMOTE",
        selected_candidate_id=selected,
        qualified_candidate_ids=qualified,
        reason_codes=("UNIQUE_PAIRED_SUPERIORITY_AFTER_HARD_GATES",),
    )
