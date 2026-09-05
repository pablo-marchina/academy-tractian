from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
import json
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .hosted_candidate_registry import Maturity, resolve_hosted_candidate


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


def _canonical_datetime(value: datetime) -> str:
    rendered = value.isoformat()
    return rendered[:-6] + "Z" if rendered.endswith("+00:00") else rendered


ZeroCostStatus = Literal["available", "unavailable", "unknown"]


class ProviderFeasibilityEvidence(_StrictModel):
    """Timestamped external-feasibility facts for one explicit provider+model candidate.

    Stable identity/maturity facts are recomputed from the code-owned registry. Volatile facts
    such as free-tier eligibility, metered price and account capacity are hash-bound here. Unknown
    is explicit: absence of account-level proof is never silently converted to false or true.
    """

    schema_version: Literal["provider-feasibility-evidence-v1"] = "provider-feasibility-evidence-v1"
    candidate_id: str = Field(min_length=1, max_length=256)
    collected_at: datetime
    source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    hosted_service: bool
    required_local_components: int = Field(ge=0)
    zero_cost_execution_status: ZeroCostStatus
    metered_input_usd_per_million: float | None = Field(default=None, ge=0.0)
    metered_output_usd_per_million: float | None = Field(default=None, ge=0.0)
    structured_output_supported: bool
    free_requests_per_day: int | None = Field(default=None, ge=0)
    free_tokens_per_day: int | None = Field(default=None, ge=0)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "ProviderFeasibilityEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("provider_feasibility_artifact_hash_mismatch")
        return self


class ProviderFeasibilityPolicy(_StrictModel):
    """Preregistered non-compensatory hard constraints applied before quality EDD."""

    schema_version: Literal["provider-feasibility-policy-v1"] = "provider-feasibility-policy-v1"
    max_evidence_age_days: int = Field(ge=0, le=365)
    allowed_model_maturities: tuple[Maturity, ...] = ("ga",)
    allowed_api_maturities: tuple[Maturity, ...] = ("ga",)
    require_hosted_service: bool = True
    max_required_local_components: int = Field(default=0, ge=0)
    require_zero_cost_execution: bool = True
    require_structured_output: bool = True
    min_free_requests_per_day: int = Field(default=0, ge=0)
    min_free_tokens_per_day: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_maturity_sets(self) -> "ProviderFeasibilityPolicy":
        if not self.allowed_model_maturities or not self.allowed_api_maturities:
            raise ValueError("provider_feasibility_allowed_maturities_empty")
        if len(set(self.allowed_model_maturities)) != len(self.allowed_model_maturities):
            raise ValueError("provider_feasibility_duplicate_model_maturity")
        if len(set(self.allowed_api_maturities)) != len(self.allowed_api_maturities):
            raise ValueError("provider_feasibility_duplicate_api_maturity")
        return self


FeasibilityOutcome = Literal["ELIGIBLE", "INELIGIBLE"]


class ProviderFeasibilityDecision(_StrictModel):
    schema_version: Literal["provider-feasibility-decision-v1"] = "provider-feasibility-decision-v1"
    candidate_id: str
    outcome: FeasibilityOutcome
    reason_codes: tuple[str, ...]
    model_maturity: Maturity
    api_maturity: Maturity
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def decide_provider_feasibility(
    *,
    evidence: ProviderFeasibilityEvidence,
    policy: ProviderFeasibilityPolicy,
    evaluated_at: datetime,
) -> ProviderFeasibilityDecision:
    """Apply non-compensatory production constraints before provider quality comparison."""

    if evaluated_at.tzinfo is None or evidence.collected_at.tzinfo is None:
        raise ValueError("provider_feasibility_requires_timezone_aware_datetimes")

    provider_id, separator, model_id = evidence.candidate_id.partition(":")
    if not separator or not provider_id or not model_id:
        raise ValueError("provider_feasibility_candidate_id_invalid")
    spec = resolve_hosted_candidate(provider_id, model_id)
    if spec.candidate_id != evidence.candidate_id:
        raise ValueError("provider_feasibility_candidate_identity_mismatch")

    reasons: list[str] = []
    if evidence.collected_at > evaluated_at:
        reasons.append("EVIDENCE_FROM_FUTURE")
    elif evaluated_at - evidence.collected_at > timedelta(days=policy.max_evidence_age_days):
        reasons.append("EVIDENCE_STALE")

    if spec.model_maturity not in policy.allowed_model_maturities:
        reasons.append("MODEL_MATURITY_NOT_ALLOWED")
    if spec.api_maturity not in policy.allowed_api_maturities:
        reasons.append("API_MATURITY_NOT_ALLOWED")
    if policy.require_hosted_service and not evidence.hosted_service:
        reasons.append("HOSTED_SERVICE_REQUIRED")
    if evidence.required_local_components > policy.max_required_local_components:
        reasons.append("LOCAL_COMPONENT_LIMIT_EXCEEDED")
    if policy.require_zero_cost_execution:
        if evidence.zero_cost_execution_status == "unknown":
            reasons.append("ZERO_COST_EXECUTION_UNKNOWN")
        elif evidence.zero_cost_execution_status != "available":
            reasons.append("ZERO_COST_EXECUTION_REQUIRED")
    if policy.require_structured_output and not evidence.structured_output_supported:
        reasons.append("STRUCTURED_OUTPUT_REQUIRED")

    if policy.min_free_requests_per_day > 0:
        if evidence.free_requests_per_day is None:
            reasons.append("FREE_REQUEST_CAPACITY_UNKNOWN")
        elif evidence.free_requests_per_day < policy.min_free_requests_per_day:
            reasons.append("FREE_REQUEST_CAPACITY_INSUFFICIENT")
    if policy.min_free_tokens_per_day > 0:
        if evidence.free_tokens_per_day is None:
            reasons.append("FREE_TOKEN_CAPACITY_UNKNOWN")
        elif evidence.free_tokens_per_day < policy.min_free_tokens_per_day:
            reasons.append("FREE_TOKEN_CAPACITY_INSUFFICIENT")

    return ProviderFeasibilityDecision(
        candidate_id=spec.candidate_id,
        outcome="INELIGIBLE" if reasons else "ELIGIBLE",
        reason_codes=tuple(dict.fromkeys(reasons)),
        model_maturity=spec.model_maturity,
        api_maturity=spec.api_maturity,
        evidence_sha256=evidence.artifact_sha256,
    )


def decide_provider_feasibility_set(
    *,
    evidence: Sequence[ProviderFeasibilityEvidence],
    policy: ProviderFeasibilityPolicy,
    evaluated_at: datetime,
) -> tuple[ProviderFeasibilityDecision, ...]:
    """Evaluate a candidate set once each; duplicate candidate evidence fails closed."""

    candidate_ids = [item.candidate_id for item in evidence]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("provider_feasibility_duplicate_candidate_evidence")
    return tuple(
        decide_provider_feasibility(evidence=item, policy=policy, evaluated_at=evaluated_at)
        for item in evidence
    )


def build_provider_feasibility_evidence(
    *,
    candidate_id: str,
    collected_at: datetime,
    source_manifest_sha256: str,
    hosted_service: bool,
    required_local_components: int,
    zero_cost_execution_status: ZeroCostStatus,
    metered_input_usd_per_million: float | None,
    metered_output_usd_per_million: float | None,
    structured_output_supported: bool,
    free_requests_per_day: int | None,
    free_tokens_per_day: int | None,
) -> ProviderFeasibilityEvidence:
    material = {
        "schema_version": "provider-feasibility-evidence-v1",
        "candidate_id": candidate_id,
        "collected_at": _canonical_datetime(collected_at),
        "source_manifest_sha256": source_manifest_sha256,
        "hosted_service": hosted_service,
        "required_local_components": required_local_components,
        "zero_cost_execution_status": zero_cost_execution_status,
        "metered_input_usd_per_million": metered_input_usd_per_million,
        "metered_output_usd_per_million": metered_output_usd_per_million,
        "structured_output_supported": structured_output_supported,
        "free_requests_per_day": free_requests_per_day,
        "free_tokens_per_day": free_tokens_per_day,
    }
    return ProviderFeasibilityEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )
