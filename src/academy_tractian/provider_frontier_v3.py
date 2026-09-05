from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .hosted_candidate_registry import resolve_hosted_candidate
from .provider_promotion import (
    ProviderBenchmarkEvidence,
    ProviderPromotionDecision,
    ProviderPromotionPolicy,
    decide_provider_promotion,
)


EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256 = (
    "031cefe7a8231c2522ac4ad3f8513219d3f3d20a5d7150d544a615e5e5386cd2"
)
CandidateRole = Literal["promotable", "reference_only"]
FrontierOutcome = Literal["PROMOTE", "NO_SELECTION"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


class ProviderFrontierCandidateRule(_StrictModel):
    candidate_id: str = Field(min_length=1, max_length=256)
    provider_id: str = Field(min_length=1, max_length=64)
    model_id: str = Field(min_length=1, max_length=192)
    role: CandidateRole
    hosted_registry_required: bool
    strict_usd0_required: bool
    privacy_eligible_required: bool
    live_evidence_required: bool

    @model_validator(mode="after")
    def validate_identity_and_role(self) -> "ProviderFrontierCandidateRule":
        if self.candidate_id != f"{self.provider_id}:{self.model_id}":
            raise ValueError("frontier_candidate_identity_mismatch")
        if self.role == "promotable" and not all(
            (
                self.hosted_registry_required,
                self.strict_usd0_required,
                self.privacy_eligible_required,
                self.live_evidence_required,
            )
        ):
            raise ValueError("promotable_candidate_must_require_all_frontier_gates")
        return self


class ProviderFrontierSelectionContract(_StrictModel):
    terminal_outcomes: tuple[Literal["PROMOTE", "NO_SELECTION"], ...]
    promotion_requires_unique_edd_winner: Literal[True]
    promotion_requires_existing_human_calibration_gate: Literal[True]
    promotion_requires_complete_pairwise_matrix_among_eligible_promotables: Literal[True]
    missing_or_mismatched_evidence: Literal["NO_SELECTION"]
    reference_only_candidate_may_never_be_selected: Literal[True]
    deployment_configuration_is_not_selection_evidence: Literal[True]

    @model_validator(mode="after")
    def validate_terminal_outcomes(self) -> "ProviderFrontierSelectionContract":
        if self.terminal_outcomes != ("PROMOTE", "NO_SELECTION"):
            raise ValueError("frontier_terminal_outcomes_changed")
        return self


class ProviderFrontierSupersession(_StrictModel):
    provider_model_comparison_design_v2: Literal["immutable historical evidence"]
    scope: Literal["current hosted provider/model frontier eligibility and final promotion only"]


class ProviderFrontierManifestV3(_StrictModel):
    schema_version: Literal["provider-model-frontier-preregistration-v3"]
    status: Literal["PREREGISTERED_PROVIDER_FREE_DESIGN"]
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    decision_id: Literal["D01-v3"]
    production_provider_model_selected: Literal[False]
    provider_model_calls_authorized_now: Literal[0]
    credential_probes_authorized_now: Literal[0]
    minimum_eligible_promotable_candidates: int = Field(ge=2)
    weighted_composite_score_forbidden: Literal[True]
    reference_only_selection_forbidden: Literal[True]
    decision_order: tuple[str, ...] = Field(min_length=4)
    candidate_set: tuple[ProviderFrontierCandidateRule, ...] = Field(min_length=3)
    selection_contract: ProviderFrontierSelectionContract
    supersession: ProviderFrontierSupersession

    @model_validator(mode="after")
    def validate_candidate_set(self) -> "ProviderFrontierManifestV3":
        ids = [candidate.candidate_id for candidate in self.candidate_set]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate_frontier_candidate_id")
        promotable = [candidate for candidate in self.candidate_set if candidate.role == "promotable"]
        reference = [candidate for candidate in self.candidate_set if candidate.role == "reference_only"]
        if len(promotable) < self.minimum_eligible_promotable_candidates:
            raise ValueError("insufficient_preregistered_promotable_candidates")
        if not reference:
            raise ValueError("frontier_reference_only_control_required")
        return self

    @property
    def canonical_sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class ProviderFrontierEligibilityEvidence(_StrictModel):
    """Candidate/config-bound eligibility evidence; contains no credentials or raw model data."""

    schema_version: Literal["provider-frontier-eligibility-v1"] = "provider-frontier-eligibility-v1"
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    candidate_id: str = Field(min_length=1, max_length=256)
    config_hash: str = Field(min_length=1, max_length=256)
    generated_at: datetime
    hosted_only: bool
    required_local_components: int = Field(ge=0)
    strict_usd0_eligible: bool
    observed_cash_cost_usd: float = Field(ge=0.0)
    privacy_eligible: bool
    live_evidence_complete: bool
    live_attempt_count: int = Field(ge=0)
    qualification_source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_artifact_hash(self) -> "ProviderFrontierEligibilityEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("frontier_eligibility_artifact_hash_mismatch")
        return self


class ProviderFrontierDecisionV3(_StrictModel):
    schema_version: Literal["provider-frontier-decision-v3"] = "provider-frontier-decision-v3"
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    outcome: FrontierOutcome
    selected_candidate_id: str | None
    eligible_promotable_candidate_ids: tuple[str, ...]
    excluded_promotable_candidate_ids: tuple[str, ...]
    reference_only_candidate_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    delegated_promotion: ProviderPromotionDecision | None = None


_REASON_ORDER = (
    "MANIFEST_HASH_MISMATCH",
    "PROMOTION_POLICY_FRONTIER_MISMATCH",
    "HOSTED_REGISTRY_MISMATCH",
    "ELIGIBILITY_EVIDENCE_MISSING",
    "ELIGIBILITY_MANIFEST_MISMATCH",
    "BENCHMARK_CANDIDATE_MISSING",
    "ELIGIBILITY_CONFIG_HASH_MISMATCH",
    "BENCHMARK_CANDIDATE_IDENTITY_MISMATCH",
    "HOSTED_ONLY_REQUIRED",
    "LOCAL_COMPONENT_REQUIRED",
    "USD0_INELIGIBLE",
    "NONZERO_CASH_COST_OBSERVED",
    "PRIVACY_INELIGIBLE",
    "LIVE_EVIDENCE_INCOMPLETE",
    "LIVE_EVIDENCE_EMPTY",
    "INSUFFICIENT_ELIGIBLE_PROMOTABLES",
    "REFERENCE_ONLY_SELECTION_FORBIDDEN",
)


def _ordered_reasons(reasons: list[str]) -> tuple[str, ...]:
    rank = {reason: index for index, reason in enumerate(_REASON_ORDER)}
    return tuple(
        dict.fromkeys(sorted(reasons, key=lambda reason: (rank.get(reason, len(rank)), reason)))
    )


def build_provider_frontier_eligibility_artifact(
    *,
    manifest_sha256: str,
    candidate_id: str,
    config_hash: str,
    generated_at: datetime,
    hosted_only: bool,
    required_local_components: int,
    strict_usd0_eligible: bool,
    observed_cash_cost_usd: float,
    privacy_eligible: bool,
    live_evidence_complete: bool,
    live_attempt_count: int,
    qualification_source_sha256: str,
) -> ProviderFrontierEligibilityEvidence:
    material = {
        "schema_version": "provider-frontier-eligibility-v1",
        "manifest_sha256": manifest_sha256,
        "candidate_id": candidate_id,
        "config_hash": config_hash,
        "generated_at": generated_at,
        "hosted_only": hosted_only,
        "required_local_components": required_local_components,
        "strict_usd0_eligible": strict_usd0_eligible,
        "observed_cash_cost_usd": observed_cash_cost_usd,
        "privacy_eligible": privacy_eligible,
        "live_evidence_complete": live_evidence_complete,
        "live_attempt_count": live_attempt_count,
        "qualification_source_sha256": qualification_source_sha256,
    }
    json_material = ProviderFrontierEligibilityEvidence.model_validate(
        {
            **material,
            "artifact_sha256": "0" * 64,
        },
        context={"skip_hash": True},
    ).model_dump(mode="json", exclude={"artifact_sha256"})
    return ProviderFrontierEligibilityEvidence.model_validate(
        {
            **json_material,
            "artifact_sha256": _canonical_sha256(json_material),
        }
    )


def decide_provider_frontier_v3(
    *,
    manifest: ProviderFrontierManifestV3,
    eligibility_evidence: tuple[ProviderFrontierEligibilityEvidence, ...],
    benchmark_evidence: ProviderBenchmarkEvidence,
    promotion_policy: ProviderPromotionPolicy,
) -> ProviderFrontierDecisionV3:
    """Apply non-compensatory frontier eligibility before the existing EDD promotion gate."""

    manifest_hash = manifest.canonical_sha256
    promotable_rules = tuple(
        candidate for candidate in manifest.candidate_set if candidate.role == "promotable"
    )
    reference_ids = tuple(
        candidate.candidate_id
        for candidate in manifest.candidate_set
        if candidate.role == "reference_only"
    )
    all_promotable_ids = tuple(candidate.candidate_id for candidate in promotable_rules)

    if manifest_hash != EXPECTED_PROVIDER_FRONTIER_V3_MANIFEST_SHA256:
        return ProviderFrontierDecisionV3(
            manifest_sha256=manifest_hash,
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            eligible_promotable_candidate_ids=(),
            excluded_promotable_candidate_ids=all_promotable_ids,
            reference_only_candidate_ids=reference_ids,
            reason_codes=("MANIFEST_HASH_MISMATCH",),
        )

    if promotion_policy.required_candidate_ids != all_promotable_ids:
        return ProviderFrontierDecisionV3(
            manifest_sha256=manifest_hash,
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            eligible_promotable_candidate_ids=(),
            excluded_promotable_candidate_ids=all_promotable_ids,
            reference_only_candidate_ids=reference_ids,
            reason_codes=("PROMOTION_POLICY_FRONTIER_MISMATCH",),
        )

    evidence_by_id: dict[str, ProviderFrontierEligibilityEvidence] = {}
    duplicate_eligibility_ids: set[str] = set()
    for item in eligibility_evidence:
        if item.candidate_id in evidence_by_id:
            duplicate_eligibility_ids.add(item.candidate_id)
        evidence_by_id[item.candidate_id] = item
    if duplicate_eligibility_ids:
        return ProviderFrontierDecisionV3(
            manifest_sha256=manifest_hash,
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            eligible_promotable_candidate_ids=(),
            excluded_promotable_candidate_ids=all_promotable_ids,
            reference_only_candidate_ids=reference_ids,
            reason_codes=("ELIGIBILITY_EVIDENCE_DUPLICATE",),
        )

    benchmark_candidates = {
        candidate.candidate_id: candidate for candidate in benchmark_evidence.candidates
    }
    eligible: list[str] = []
    excluded: list[str] = []
    reasons: list[str] = []

    for rule in promotable_rules:
        candidate_reasons: list[str] = []
        if rule.hosted_registry_required:
            try:
                registered = resolve_hosted_candidate(rule.provider_id, rule.model_id)
            except ValueError:
                candidate_reasons.append("HOSTED_REGISTRY_MISMATCH")
            else:
                if registered.candidate_id != rule.candidate_id:
                    candidate_reasons.append("HOSTED_REGISTRY_MISMATCH")

        eligibility = evidence_by_id.get(rule.candidate_id)
        benchmark_candidate = benchmark_candidates.get(rule.candidate_id)
        if eligibility is None:
            candidate_reasons.append("ELIGIBILITY_EVIDENCE_MISSING")
        elif eligibility.manifest_sha256 != manifest_hash:
            candidate_reasons.append("ELIGIBILITY_MANIFEST_MISMATCH")

        if benchmark_candidate is None:
            candidate_reasons.append("BENCHMARK_CANDIDATE_MISSING")
        elif (
            benchmark_candidate.provider_id != rule.provider_id
            or benchmark_candidate.model_id != rule.model_id
        ):
            candidate_reasons.append("BENCHMARK_CANDIDATE_IDENTITY_MISMATCH")

        if eligibility is not None and benchmark_candidate is not None:
            if eligibility.config_hash != benchmark_candidate.config_hash:
                candidate_reasons.append("ELIGIBILITY_CONFIG_HASH_MISMATCH")
            if not eligibility.hosted_only:
                candidate_reasons.append("HOSTED_ONLY_REQUIRED")
            if eligibility.required_local_components != 0:
                candidate_reasons.append("LOCAL_COMPONENT_REQUIRED")
            if rule.strict_usd0_required and not eligibility.strict_usd0_eligible:
                candidate_reasons.append("USD0_INELIGIBLE")
            if rule.strict_usd0_required and eligibility.observed_cash_cost_usd != 0.0:
                candidate_reasons.append("NONZERO_CASH_COST_OBSERVED")
            if rule.privacy_eligible_required and not eligibility.privacy_eligible:
                candidate_reasons.append("PRIVACY_INELIGIBLE")
            if rule.live_evidence_required and not eligibility.live_evidence_complete:
                candidate_reasons.append("LIVE_EVIDENCE_INCOMPLETE")
            if rule.live_evidence_required and eligibility.live_attempt_count < 1:
                candidate_reasons.append("LIVE_EVIDENCE_EMPTY")

        if candidate_reasons:
            excluded.append(rule.candidate_id)
            reasons.extend(candidate_reasons)
        else:
            eligible.append(rule.candidate_id)

    if len(eligible) < manifest.minimum_eligible_promotable_candidates:
        reasons.append("INSUFFICIENT_ELIGIBLE_PROMOTABLES")
        return ProviderFrontierDecisionV3(
            manifest_sha256=manifest_hash,
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            eligible_promotable_candidate_ids=tuple(eligible),
            excluded_promotable_candidate_ids=tuple(excluded),
            reference_only_candidate_ids=reference_ids,
            reason_codes=_ordered_reasons(reasons),
        )

    eligible_set = set(eligible)
    filtered_benchmark = ProviderBenchmarkEvidence.model_validate(
        {
            **benchmark_evidence.model_dump(mode="json"),
            "candidates": [
                candidate.model_dump(mode="json")
                for candidate in benchmark_evidence.candidates
                if candidate.candidate_id in eligible_set
            ],
            "pairwise_reports": [
                report.model_dump(mode="json")
                for report in benchmark_evidence.pairwise_reports
                if report.baseline_config_id in eligible_set
                and report.candidate_config_id in eligible_set
            ],
        }
    )
    filtered_policy = ProviderPromotionPolicy.model_validate(
        {
            **promotion_policy.model_dump(mode="json"),
            "required_candidate_ids": eligible,
        }
    )
    delegated = decide_provider_promotion(
        evidence=filtered_benchmark,
        policy=filtered_policy,
    )

    if delegated.outcome != "PROMOTE" or delegated.selected_candidate_id is None:
        return ProviderFrontierDecisionV3(
            manifest_sha256=manifest_hash,
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            eligible_promotable_candidate_ids=tuple(eligible),
            excluded_promotable_candidate_ids=tuple(excluded),
            reference_only_candidate_ids=reference_ids,
            reason_codes=_ordered_reasons(reasons + list(delegated.reason_codes)),
            delegated_promotion=delegated,
        )

    if delegated.selected_candidate_id in reference_ids:
        return ProviderFrontierDecisionV3(
            manifest_sha256=manifest_hash,
            outcome="NO_SELECTION",
            selected_candidate_id=None,
            eligible_promotable_candidate_ids=tuple(eligible),
            excluded_promotable_candidate_ids=tuple(excluded),
            reference_only_candidate_ids=reference_ids,
            reason_codes=_ordered_reasons(reasons + ["REFERENCE_ONLY_SELECTION_FORBIDDEN"]),
            delegated_promotion=delegated,
        )

    return ProviderFrontierDecisionV3(
        manifest_sha256=manifest_hash,
        outcome="PROMOTE",
        selected_candidate_id=delegated.selected_candidate_id,
        eligible_promotable_candidate_ids=tuple(eligible),
        excluded_promotable_candidate_ids=tuple(excluded),
        reference_only_candidate_ids=reference_ids,
        reason_codes=_ordered_reasons(
            reasons + ["UNIQUE_ELIGIBLE_PROMOTABLE_SELECTED_BY_EXISTING_EDD_GATE"]
        ),
        delegated_promotion=delegated,
    )
