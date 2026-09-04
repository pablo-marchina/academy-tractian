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
ServiceMaturity = Literal["ga", "beta", "preview", "unknown"]
MigrationClass = Literal["none", "minor", "major", "unknown"]
FeasibilityOutcome = Literal["PILOT_ADMISSIBLE", "STATIC_REJECT"]


def _require_yes(value: TriState, *, unknown: str, negative: str, reasons: list[str]) -> None:
    if value == "unknown":
        reasons.append(unknown)
    elif value != "yes":
        reasons.append(negative)


def _validate_time(*, collected_at: datetime, evaluated_at: datetime, max_age_days: int) -> list[str]:
    if collected_at.tzinfo is None or evaluated_at.tzinfo is None:
        raise ValueError("feasibility_requires_timezone_aware_datetimes")
    if collected_at > evaluated_at:
        return ["EVIDENCE_FROM_FUTURE"]
    if evaluated_at - collected_at > timedelta(days=max_age_days):
        return ["EVIDENCE_STALE"]
    return []


class ManagedPostgresEvidence(_StrictModel):
    """Timestamped evidence for one managed PostgreSQL candidate.

    Only facts used by the admission decision are stored. Platform strengths cannot compensate for
    an identity failure later in the bundle gate.
    """

    schema_version: Literal["managed-postgres-evidence-v1"] = "managed-postgres-evidence-v1"
    candidate_id: str = Field(min_length=1, max_length=128)
    collected_at: datetime
    source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    hosted_service: bool
    required_local_components: int = Field(ge=0)
    zero_cost_guardrail: TriState
    service_maturity: ServiceMaturity
    postgres_wire_compatible: TriState
    tls_external_connections: TriState
    pooled_connections: TriState
    row_level_security: TriState
    transaction_support: TriState
    inactivity_requires_manual_reactivation: TriState
    restore_supported: TriState
    restore_window_hours: float | None = Field(default=None, ge=0.0)
    free_storage_mb: int | None = Field(default=None, ge=0)
    migration_class: MigrationClass
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "ManagedPostgresEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("managed_postgres_artifact_hash_mismatch")
        return self


class ManagedPostgresPolicy(_StrictModel):
    schema_version: Literal["managed-postgres-policy-v1"] = "managed-postgres-policy-v1"
    max_evidence_age_days: int = Field(ge=0, le=365)
    max_required_local_components: int = Field(default=0, ge=0)
    allowed_service_maturities: tuple[ServiceMaturity, ...] = ("ga",)
    require_zero_cost_guardrail: bool = True
    require_postgres_wire: bool = True
    require_tls_external_connections: bool = True
    require_pooled_connections: bool = True
    require_row_level_security: bool = True
    require_transactions: bool = True
    forbid_manual_inactivity_reactivation: bool = True
    require_restore: bool = True
    min_restore_window_hours: float = Field(default=0.0, ge=0.0)
    min_free_storage_mb: int = Field(default=0, ge=0)
    allowed_migration_classes: tuple[MigrationClass, ...] = ("none", "minor")

    @model_validator(mode="after")
    def validate_sets(self) -> "ManagedPostgresPolicy":
        if not self.allowed_service_maturities or not self.allowed_migration_classes:
            raise ValueError("managed_postgres_allowed_sets_empty")
        if len(set(self.allowed_service_maturities)) != len(self.allowed_service_maturities):
            raise ValueError("managed_postgres_duplicate_service_maturity")
        if len(set(self.allowed_migration_classes)) != len(self.allowed_migration_classes):
            raise ValueError("managed_postgres_duplicate_migration_class")
        return self


class ManagedPostgresDecision(_StrictModel):
    schema_version: Literal["managed-postgres-decision-v1"] = "managed-postgres-decision-v1"
    candidate_id: str
    outcome: FeasibilityOutcome
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def decide_managed_postgres_feasibility(
    *, evidence: ManagedPostgresEvidence, policy: ManagedPostgresPolicy, evaluated_at: datetime
) -> ManagedPostgresDecision:
    reasons = _validate_time(
        collected_at=evidence.collected_at,
        evaluated_at=evaluated_at,
        max_age_days=policy.max_evidence_age_days,
    )
    if not evidence.hosted_service:
        reasons.append("HOSTED_SERVICE_REQUIRED")
    if evidence.required_local_components > policy.max_required_local_components:
        reasons.append("LOCAL_COMPONENT_LIMIT_EXCEEDED")
    if policy.require_zero_cost_guardrail:
        _require_yes(
            evidence.zero_cost_guardrail,
            unknown="ZERO_COST_GUARDRAIL_UNKNOWN",
            negative="ZERO_COST_GUARDRAIL_REQUIRED",
            reasons=reasons,
        )
    if evidence.service_maturity not in policy.allowed_service_maturities:
        reasons.append("SERVICE_MATURITY_NOT_ALLOWED")

    required = (
        (policy.require_postgres_wire, evidence.postgres_wire_compatible, "POSTGRES_WIRE_UNKNOWN", "POSTGRES_WIRE_REQUIRED"),
        (policy.require_tls_external_connections, evidence.tls_external_connections, "TLS_EXTERNAL_CONNECTIONS_UNKNOWN", "TLS_EXTERNAL_CONNECTIONS_REQUIRED"),
        (policy.require_pooled_connections, evidence.pooled_connections, "POOLED_CONNECTIONS_UNKNOWN", "POOLED_CONNECTIONS_REQUIRED"),
        (policy.require_row_level_security, evidence.row_level_security, "ROW_LEVEL_SECURITY_UNKNOWN", "ROW_LEVEL_SECURITY_REQUIRED"),
        (policy.require_transactions, evidence.transaction_support, "TRANSACTION_SUPPORT_UNKNOWN", "TRANSACTION_SUPPORT_REQUIRED"),
    )
    for is_required, value, unknown, negative in required:
        if is_required:
            _require_yes(value, unknown=unknown, negative=negative, reasons=reasons)

    if policy.forbid_manual_inactivity_reactivation:
        if evidence.inactivity_requires_manual_reactivation == "unknown":
            reasons.append("INACTIVITY_REACTIVATION_UNKNOWN")
        elif evidence.inactivity_requires_manual_reactivation == "yes":
            reasons.append("MANUAL_INACTIVITY_REACTIVATION_FORBIDDEN")

    if policy.require_restore:
        _require_yes(
            evidence.restore_supported,
            unknown="RESTORE_SUPPORT_UNKNOWN",
            negative="RESTORE_SUPPORT_REQUIRED",
            reasons=reasons,
        )
        if evidence.restore_window_hours is None:
            reasons.append("RESTORE_WINDOW_UNKNOWN")
        elif evidence.restore_window_hours < policy.min_restore_window_hours:
            reasons.append("RESTORE_WINDOW_INSUFFICIENT")

    if policy.min_free_storage_mb > 0:
        if evidence.free_storage_mb is None:
            reasons.append("FREE_STORAGE_UNKNOWN")
        elif evidence.free_storage_mb < policy.min_free_storage_mb:
            reasons.append("FREE_STORAGE_INSUFFICIENT")
    if evidence.migration_class not in policy.allowed_migration_classes:
        reasons.append("MIGRATION_CLASS_NOT_ALLOWED")

    return ManagedPostgresDecision(
        candidate_id=evidence.candidate_id,
        outcome="STATIC_REJECT" if reasons else "PILOT_ADMISSIBLE",
        reason_codes=tuple(dict.fromkeys(reasons)),
        evidence_sha256=evidence.artifact_sha256,
    )


class HostedIdentityEvidence(_StrictModel):
    """Timestamped evidence for a hosted browser-identity candidate."""

    schema_version: Literal["hosted-identity-evidence-v1"] = "hosted-identity-evidence-v1"
    candidate_id: str = Field(min_length=1, max_length=128)
    collected_at: datetime
    source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    hosted_service: bool
    required_local_components: int = Field(ge=0)
    zero_cost_guardrail: TriState
    production_without_billing_instrument: TriState
    service_maturity: ServiceMaturity
    asymmetric_jwks: TriState
    issuer_claim: TriState
    audience_claim_configurable: TriState
    subject_claim: TriState
    organization_claim_configurable: TriState
    role_claim_configurable: TriState
    permissions_claim_configurable: TriState
    authorized_party_claim: TriState
    token_ttl_configurable_to_max_seconds: int | None = Field(default=None, ge=1)
    first_class_organizations: TriState
    free_active_users: int | None = Field(default=None, ge=0)
    free_organizations: int | None = Field(default=None, ge=0)
    inactivity_requires_manual_reactivation: TriState
    migration_class: MigrationClass
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "HostedIdentityEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("hosted_identity_artifact_hash_mismatch")
        return self


class HostedIdentityPolicy(_StrictModel):
    schema_version: Literal["hosted-identity-policy-v1"] = "hosted-identity-policy-v1"
    max_evidence_age_days: int = Field(ge=0, le=365)
    max_required_local_components: int = Field(default=0, ge=0)
    allowed_service_maturities: tuple[ServiceMaturity, ...] = ("ga",)
    require_zero_cost_guardrail: bool = True
    require_production_without_billing_instrument: bool = True
    require_asymmetric_jwks: bool = True
    require_audience_claim: bool = True
    require_organization_claim: bool = True
    require_role_claim: bool = True
    require_permissions_claim: bool = True
    max_token_ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    require_first_class_organizations: bool = True
    min_free_active_users: int = Field(default=0, ge=0)
    min_free_organizations: int = Field(default=0, ge=0)
    forbid_manual_inactivity_reactivation: bool = True
    allowed_migration_classes: tuple[MigrationClass, ...] = ("none", "minor")

    @model_validator(mode="after")
    def validate_sets(self) -> "HostedIdentityPolicy":
        if not self.allowed_service_maturities or not self.allowed_migration_classes:
            raise ValueError("hosted_identity_allowed_sets_empty")
        return self


class HostedIdentityDecision(_StrictModel):
    schema_version: Literal["hosted-identity-decision-v1"] = "hosted-identity-decision-v1"
    candidate_id: str
    outcome: FeasibilityOutcome
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def decide_hosted_identity_feasibility(
    *, evidence: HostedIdentityEvidence, policy: HostedIdentityPolicy, evaluated_at: datetime
) -> HostedIdentityDecision:
    reasons = _validate_time(
        collected_at=evidence.collected_at,
        evaluated_at=evaluated_at,
        max_age_days=policy.max_evidence_age_days,
    )
    if not evidence.hosted_service:
        reasons.append("HOSTED_SERVICE_REQUIRED")
    if evidence.required_local_components > policy.max_required_local_components:
        reasons.append("LOCAL_COMPONENT_LIMIT_EXCEEDED")
    if policy.require_zero_cost_guardrail:
        _require_yes(evidence.zero_cost_guardrail, unknown="ZERO_COST_GUARDRAIL_UNKNOWN", negative="ZERO_COST_GUARDRAIL_REQUIRED", reasons=reasons)
    if policy.require_production_without_billing_instrument:
        _require_yes(
            evidence.production_without_billing_instrument,
            unknown="PRODUCTION_BILLING_INSTRUMENT_UNKNOWN",
            negative="PRODUCTION_REQUIRES_BILLING_INSTRUMENT",
            reasons=reasons,
        )
    if evidence.service_maturity not in policy.allowed_service_maturities:
        reasons.append("SERVICE_MATURITY_NOT_ALLOWED")

    required = (
        (policy.require_asymmetric_jwks, evidence.asymmetric_jwks, "ASYMMETRIC_JWKS_UNKNOWN", "ASYMMETRIC_JWKS_REQUIRED"),
        (True, evidence.issuer_claim, "ISSUER_CLAIM_UNKNOWN", "ISSUER_CLAIM_REQUIRED"),
        (True, evidence.subject_claim, "SUBJECT_CLAIM_UNKNOWN", "SUBJECT_CLAIM_REQUIRED"),
        (policy.require_audience_claim, evidence.audience_claim_configurable, "AUDIENCE_CLAIM_UNKNOWN", "AUDIENCE_CLAIM_REQUIRED"),
        (policy.require_organization_claim, evidence.organization_claim_configurable, "ORGANIZATION_CLAIM_UNKNOWN", "ORGANIZATION_CLAIM_REQUIRED"),
        (policy.require_role_claim, evidence.role_claim_configurable, "ROLE_CLAIM_UNKNOWN", "ROLE_CLAIM_REQUIRED"),
        (policy.require_permissions_claim, evidence.permissions_claim_configurable, "PERMISSIONS_CLAIM_UNKNOWN", "PERMISSIONS_CLAIM_REQUIRED"),
    )
    for is_required, value, unknown, negative in required:
        if is_required:
            _require_yes(value, unknown=unknown, negative=negative, reasons=reasons)

    if evidence.token_ttl_configurable_to_max_seconds is None:
        reasons.append("TOKEN_TTL_CONTROL_UNKNOWN")
    elif evidence.token_ttl_configurable_to_max_seconds > policy.max_token_ttl_seconds:
        reasons.append("TOKEN_TTL_TOO_LONG")
    if policy.require_first_class_organizations:
        _require_yes(
            evidence.first_class_organizations,
            unknown="ORGANIZATION_SUPPORT_UNKNOWN",
            negative="FIRST_CLASS_ORGANIZATIONS_REQUIRED",
            reasons=reasons,
        )
    if policy.min_free_active_users > 0:
        if evidence.free_active_users is None:
            reasons.append("FREE_USER_CAPACITY_UNKNOWN")
        elif evidence.free_active_users < policy.min_free_active_users:
            reasons.append("FREE_USER_CAPACITY_INSUFFICIENT")
    if policy.min_free_organizations > 0:
        if evidence.free_organizations is None:
            reasons.append("FREE_ORGANIZATION_CAPACITY_UNKNOWN")
        elif evidence.free_organizations < policy.min_free_organizations:
            reasons.append("FREE_ORGANIZATION_CAPACITY_INSUFFICIENT")
    if policy.forbid_manual_inactivity_reactivation:
        if evidence.inactivity_requires_manual_reactivation == "unknown":
            reasons.append("INACTIVITY_REACTIVATION_UNKNOWN")
        elif evidence.inactivity_requires_manual_reactivation == "yes":
            reasons.append("MANUAL_INACTIVITY_REACTIVATION_FORBIDDEN")
    if evidence.migration_class not in policy.allowed_migration_classes:
        reasons.append("MIGRATION_CLASS_NOT_ALLOWED")

    return HostedIdentityDecision(
        candidate_id=evidence.candidate_id,
        outcome="STATIC_REJECT" if reasons else "PILOT_ADMISSIBLE",
        reason_codes=tuple(dict.fromkeys(reasons)),
        evidence_sha256=evidence.artifact_sha256,
    )


class StateIdentityBundleDecision(_StrictModel):
    schema_version: Literal["state-identity-bundle-decision-v1"] = "state-identity-bundle-decision-v1"
    bundle_id: str
    database_candidate_id: str
    identity_candidate_id: str
    outcome: FeasibilityOutcome
    reason_codes: tuple[str, ...]


def decide_state_identity_bundle(
    *, bundle_id: str, database: ManagedPostgresDecision, identity: HostedIdentityDecision
) -> StateIdentityBundleDecision:
    reasons: list[str] = []
    if database.outcome != "PILOT_ADMISSIBLE":
        reasons.extend(f"DATABASE:{reason}" for reason in database.reason_codes)
    if identity.outcome != "PILOT_ADMISSIBLE":
        reasons.extend(f"IDENTITY:{reason}" for reason in identity.reason_codes)
    return StateIdentityBundleDecision(
        bundle_id=bundle_id,
        database_candidate_id=database.candidate_id,
        identity_candidate_id=identity.candidate_id,
        outcome="STATIC_REJECT" if reasons else "PILOT_ADMISSIBLE",
        reason_codes=tuple(reasons),
    )


def decide_managed_postgres_set(
    *, evidence: Sequence[ManagedPostgresEvidence], policy: ManagedPostgresPolicy, evaluated_at: datetime
) -> tuple[ManagedPostgresDecision, ...]:
    ids = [item.candidate_id for item in evidence]
    if len(ids) != len(set(ids)):
        raise ValueError("managed_postgres_duplicate_candidate_evidence")
    return tuple(
        decide_managed_postgres_feasibility(evidence=item, policy=policy, evaluated_at=evaluated_at)
        for item in evidence
    )


def decide_hosted_identity_set(
    *, evidence: Sequence[HostedIdentityEvidence], policy: HostedIdentityPolicy, evaluated_at: datetime
) -> tuple[HostedIdentityDecision, ...]:
    ids = [item.candidate_id for item in evidence]
    if len(ids) != len(set(ids)):
        raise ValueError("hosted_identity_duplicate_candidate_evidence")
    return tuple(
        decide_hosted_identity_feasibility(evidence=item, policy=policy, evaluated_at=evaluated_at)
        for item in evidence
    )


def build_managed_postgres_evidence(**values: object) -> ManagedPostgresEvidence:
    material = {"schema_version": "managed-postgres-evidence-v1", **values}
    if isinstance(material.get("collected_at"), datetime):
        material["collected_at"] = _canonical_datetime(material["collected_at"])
    return ManagedPostgresEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )


def build_hosted_identity_evidence(**values: object) -> HostedIdentityEvidence:
    material = {"schema_version": "hosted-identity-evidence-v1", **values}
    if isinstance(material.get("collected_at"), datetime):
        material["collected_at"] = _canonical_datetime(material["collected_at"])
    return HostedIdentityEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )
