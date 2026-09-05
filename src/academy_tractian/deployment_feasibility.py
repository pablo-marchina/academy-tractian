from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
import json
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


TriState = Literal["yes", "no", "unknown"]
RuntimeMaturity = Literal["ga", "beta", "preview", "unknown"]
MigrationClass = Literal["none", "minor", "major", "unknown"]


class DeploymentFeasibilityEvidence(_StrictModel):
    """Timestamped research evidence for one hosted backend-compute candidate.

    This gate evaluates whether a candidate deserves a live deployment experiment. It deliberately
    does not claim production SLOs or choose a winner. Unknown facts are explicit and fail closed
    whenever the policy marks the corresponding capability as required.
    """

    schema_version: Literal["deployment-feasibility-evidence-v1"] = (
        "deployment-feasibility-evidence-v1"
    )
    candidate_id: str = Field(min_length=1, max_length=128)
    collected_at: datetime
    source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    hosted_service: bool
    required_local_components: int = Field(ge=0)
    zero_cost_guardrail: TriState
    runtime_maturity: RuntimeMaturity
    dockerfile_compatible: TriState
    python_3_11_compatible: TriState
    outbound_https_supported: TriState
    managed_postgres_connectivity: TriState
    streaming_http_supported: TriState
    persistent_local_disk_required: bool
    provider_explicitly_discourages_production: TriState
    migration_class: MigrationClass
    published_compute_limit: str | None = Field(default=None, max_length=512)
    published_memory_limit: str | None = Field(default=None, max_length=512)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "DeploymentFeasibilityEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("deployment_feasibility_artifact_hash_mismatch")
        return self


class DeploymentFeasibilityPolicy(_StrictModel):
    """Non-compensatory admission policy for a hosted backend deployment pilot."""

    schema_version: Literal["deployment-feasibility-policy-v1"] = "deployment-feasibility-policy-v1"
    max_evidence_age_days: int = Field(ge=0, le=365)
    require_hosted_service: bool = True
    max_required_local_components: int = Field(default=0, ge=0)
    require_zero_cost_guardrail: bool = True
    allowed_runtime_maturities: tuple[RuntimeMaturity, ...] = ("ga",)
    require_dockerfile_compatibility: bool = True
    require_python_3_11_compatibility: bool = True
    require_outbound_https: bool = True
    require_managed_postgres_connectivity: bool = True
    require_streaming_http: bool = True
    forbid_persistent_local_disk_requirement: bool = True
    reject_provider_discouraged_production: bool = True
    allowed_migration_classes: tuple[MigrationClass, ...] = ("none", "minor")

    @model_validator(mode="after")
    def validate_sets(self) -> "DeploymentFeasibilityPolicy":
        if not self.allowed_runtime_maturities or not self.allowed_migration_classes:
            raise ValueError("deployment_feasibility_allowed_sets_empty")
        if len(set(self.allowed_runtime_maturities)) != len(self.allowed_runtime_maturities):
            raise ValueError("deployment_feasibility_duplicate_runtime_maturity")
        if len(set(self.allowed_migration_classes)) != len(self.allowed_migration_classes):
            raise ValueError("deployment_feasibility_duplicate_migration_class")
        return self


DeploymentFeasibilityOutcome = Literal["PILOT_ADMISSIBLE", "STATIC_REJECT"]


class DeploymentFeasibilityDecision(_StrictModel):
    schema_version: Literal["deployment-feasibility-decision-v1"] = (
        "deployment-feasibility-decision-v1"
    )
    candidate_id: str
    outcome: DeploymentFeasibilityOutcome
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _require_yes(value: TriState, *, missing: str, negative: str, reasons: list[str]) -> None:
    if value == "unknown":
        reasons.append(missing)
    elif value != "yes":
        reasons.append(negative)


def decide_deployment_feasibility(
    *,
    evidence: DeploymentFeasibilityEvidence,
    policy: DeploymentFeasibilityPolicy,
    evaluated_at: datetime,
) -> DeploymentFeasibilityDecision:
    if evaluated_at.tzinfo is None or evidence.collected_at.tzinfo is None:
        raise ValueError("deployment_feasibility_requires_timezone_aware_datetimes")

    reasons: list[str] = []
    if evidence.collected_at > evaluated_at:
        reasons.append("EVIDENCE_FROM_FUTURE")
    elif evaluated_at - evidence.collected_at > timedelta(days=policy.max_evidence_age_days):
        reasons.append("EVIDENCE_STALE")

    if policy.require_hosted_service and not evidence.hosted_service:
        reasons.append("HOSTED_SERVICE_REQUIRED")
    if evidence.required_local_components > policy.max_required_local_components:
        reasons.append("LOCAL_COMPONENT_LIMIT_EXCEEDED")
    if policy.require_zero_cost_guardrail:
        _require_yes(
            evidence.zero_cost_guardrail,
            missing="ZERO_COST_GUARDRAIL_UNKNOWN",
            negative="ZERO_COST_GUARDRAIL_REQUIRED",
            reasons=reasons,
        )
    if evidence.runtime_maturity not in policy.allowed_runtime_maturities:
        reasons.append("RUNTIME_MATURITY_NOT_ALLOWED")

    required_capabilities = (
        (
            policy.require_dockerfile_compatibility,
            evidence.dockerfile_compatible,
            "DOCKERFILE_COMPATIBILITY_UNKNOWN",
            "DOCKERFILE_COMPATIBILITY_REQUIRED",
        ),
        (
            policy.require_python_3_11_compatibility,
            evidence.python_3_11_compatible,
            "PYTHON_3_11_COMPATIBILITY_UNKNOWN",
            "PYTHON_3_11_COMPATIBILITY_REQUIRED",
        ),
        (
            policy.require_outbound_https,
            evidence.outbound_https_supported,
            "OUTBOUND_HTTPS_UNKNOWN",
            "OUTBOUND_HTTPS_REQUIRED",
        ),
        (
            policy.require_managed_postgres_connectivity,
            evidence.managed_postgres_connectivity,
            "MANAGED_POSTGRES_CONNECTIVITY_UNKNOWN",
            "MANAGED_POSTGRES_CONNECTIVITY_REQUIRED",
        ),
        (
            policy.require_streaming_http,
            evidence.streaming_http_supported,
            "STREAMING_HTTP_UNKNOWN",
            "STREAMING_HTTP_REQUIRED",
        ),
    )
    for required, value, unknown_reason, negative_reason in required_capabilities:
        if required:
            _require_yes(
                value,
                missing=unknown_reason,
                negative=negative_reason,
                reasons=reasons,
            )

    if policy.forbid_persistent_local_disk_requirement and evidence.persistent_local_disk_required:
        reasons.append("PERSISTENT_LOCAL_DISK_FORBIDDEN")
    if policy.reject_provider_discouraged_production:
        if evidence.provider_explicitly_discourages_production == "unknown":
            reasons.append("PRODUCTION_SUITABILITY_UNKNOWN")
        elif evidence.provider_explicitly_discourages_production == "yes":
            reasons.append("PROVIDER_DISCOURAGES_PRODUCTION")
    if evidence.migration_class not in policy.allowed_migration_classes:
        reasons.append("MIGRATION_CLASS_NOT_ALLOWED")

    return DeploymentFeasibilityDecision(
        candidate_id=evidence.candidate_id,
        outcome="STATIC_REJECT" if reasons else "PILOT_ADMISSIBLE",
        reason_codes=tuple(dict.fromkeys(reasons)),
        evidence_sha256=evidence.artifact_sha256,
    )


def decide_deployment_feasibility_set(
    *,
    evidence: Sequence[DeploymentFeasibilityEvidence],
    policy: DeploymentFeasibilityPolicy,
    evaluated_at: datetime,
) -> tuple[DeploymentFeasibilityDecision, ...]:
    candidate_ids = [item.candidate_id for item in evidence]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("deployment_feasibility_duplicate_candidate_evidence")
    return tuple(
        decide_deployment_feasibility(evidence=item, policy=policy, evaluated_at=evaluated_at)
        for item in evidence
    )


def build_deployment_feasibility_evidence(
    *,
    candidate_id: str,
    collected_at: datetime,
    source_manifest_sha256: str,
    hosted_service: bool,
    required_local_components: int,
    zero_cost_guardrail: TriState,
    runtime_maturity: RuntimeMaturity,
    dockerfile_compatible: TriState,
    python_3_11_compatible: TriState,
    outbound_https_supported: TriState,
    managed_postgres_connectivity: TriState,
    streaming_http_supported: TriState,
    persistent_local_disk_required: bool,
    provider_explicitly_discourages_production: TriState,
    migration_class: MigrationClass,
    published_compute_limit: str | None,
    published_memory_limit: str | None,
) -> DeploymentFeasibilityEvidence:
    material = {
        "schema_version": "deployment-feasibility-evidence-v1",
        "candidate_id": candidate_id,
        "collected_at": _canonical_datetime(collected_at),
        "source_manifest_sha256": source_manifest_sha256,
        "hosted_service": hosted_service,
        "required_local_components": required_local_components,
        "zero_cost_guardrail": zero_cost_guardrail,
        "runtime_maturity": runtime_maturity,
        "dockerfile_compatible": dockerfile_compatible,
        "python_3_11_compatible": python_3_11_compatible,
        "outbound_https_supported": outbound_https_supported,
        "managed_postgres_connectivity": managed_postgres_connectivity,
        "streaming_http_supported": streaming_http_supported,
        "persistent_local_disk_required": persistent_local_disk_required,
        "provider_explicitly_discourages_production": provider_explicitly_discourages_production,
        "migration_class": migration_class,
        "published_compute_limit": published_compute_limit,
        "published_memory_limit": published_memory_limit,
    }
    return DeploymentFeasibilityEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )
