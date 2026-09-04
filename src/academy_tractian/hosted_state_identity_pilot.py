from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _canonical_datetime(value: datetime) -> str:
    rendered = value.isoformat()
    return rendered[:-6] + "Z" if rendered.endswith("+00:00") else rendered


class HostedStateIdentityPilotEvidence(_StrictModel):
    """Sanitized live evidence for one hosted state+identity bundle.

    The artifact stores outcomes and hashes only. It must never contain DSNs, credentials, bearer
    tokens, raw JWTs, raw JWKS documents or customer payloads.
    """

    schema_version: Literal["hosted-state-identity-pilot-evidence-v1"] = (
        "hosted-state-identity-pilot-evidence-v1"
    )
    bundle_id: str = Field(min_length=1, max_length=128)
    code_sha: str = Field(pattern=r"^[0-9a-f]{7,64}$")
    collected_at: datetime
    deployment_origin_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    database_endpoint_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    identity_issuer_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    required_local_components: int = Field(ge=0)
    observed_unexpected_cash_charge_usd: float = Field(ge=0.0)
    organization_count: int = Field(ge=0)
    user_count: int = Field(ge=0)
    clean_migration_passed: bool
    pooled_tls_postgres_passed: bool
    oidc_valid_token_accepted: bool
    oidc_jwks_rs256_verified: bool
    exact_audience_verified: bool
    exact_issuer_verified: bool
    organization_claim_verified: bool
    role_claim_verified: bool
    permission_allowlist_verified: bool
    token_ttl_verified: bool
    allowed_tenant_request_passed: bool
    cross_tenant_read_denied: bool
    cross_tenant_mutation_denied: bool
    expired_token_rejected: bool
    wrong_audience_rejected: bool
    wrong_issuer_rejected: bool
    malformed_token_rejected: bool
    unknown_organization_rejected: bool
    sse_reconnect_tenant_isolation_passed: bool
    restart_persistence_passed: bool
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "HostedStateIdentityPilotEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("hosted_state_identity_pilot_artifact_hash_mismatch")
        return self


class HostedStateIdentityPilotPolicy(_StrictModel):
    schema_version: Literal["hosted-state-identity-pilot-policy-v1"] = (
        "hosted-state-identity-pilot-policy-v1"
    )
    expected_bundle_id: str = "neon-plus-auth0"
    max_required_local_components: int = 0
    max_unexpected_cash_charge_usd: float = 0.0
    min_organizations: int = Field(default=2, ge=2)
    min_users: int = Field(default=2, ge=2)


PilotOutcome = Literal["PILOT_PASS", "PILOT_FAIL"]


class HostedStateIdentityPilotDecision(_StrictModel):
    schema_version: Literal["hosted-state-identity-pilot-decision-v1"] = (
        "hosted-state-identity-pilot-decision-v1"
    )
    bundle_id: str
    outcome: PilotOutcome
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def decide_hosted_state_identity_pilot(
    *, evidence: HostedStateIdentityPilotEvidence, policy: HostedStateIdentityPilotPolicy
) -> HostedStateIdentityPilotDecision:
    reasons: list[str] = []
    if evidence.bundle_id != policy.expected_bundle_id:
        reasons.append("BUNDLE_ID_MISMATCH")
    if evidence.required_local_components > policy.max_required_local_components:
        reasons.append("LOCAL_COMPONENT_LIMIT_EXCEEDED")
    if evidence.observed_unexpected_cash_charge_usd > policy.max_unexpected_cash_charge_usd:
        reasons.append("UNEXPECTED_CASH_CHARGE")
    if evidence.organization_count < policy.min_organizations:
        reasons.append("INSUFFICIENT_ORGANIZATIONS")
    if evidence.user_count < policy.min_users:
        reasons.append("INSUFFICIENT_USERS")

    required_checks = {
        "CLEAN_MIGRATION_FAILED": evidence.clean_migration_passed,
        "POOLED_TLS_POSTGRES_FAILED": evidence.pooled_tls_postgres_passed,
        "OIDC_VALID_TOKEN_NOT_ACCEPTED": evidence.oidc_valid_token_accepted,
        "OIDC_RS256_JWKS_NOT_VERIFIED": evidence.oidc_jwks_rs256_verified,
        "OIDC_AUDIENCE_NOT_VERIFIED": evidence.exact_audience_verified,
        "OIDC_ISSUER_NOT_VERIFIED": evidence.exact_issuer_verified,
        "OIDC_ORGANIZATION_CLAIM_NOT_VERIFIED": evidence.organization_claim_verified,
        "OIDC_ROLE_CLAIM_NOT_VERIFIED": evidence.role_claim_verified,
        "OIDC_PERMISSION_ALLOWLIST_NOT_VERIFIED": evidence.permission_allowlist_verified,
        "OIDC_TOKEN_TTL_NOT_VERIFIED": evidence.token_ttl_verified,
        "ALLOWED_TENANT_REQUEST_FAILED": evidence.allowed_tenant_request_passed,
        "CROSS_TENANT_READ_NOT_DENIED": evidence.cross_tenant_read_denied,
        "CROSS_TENANT_MUTATION_NOT_DENIED": evidence.cross_tenant_mutation_denied,
        "EXPIRED_TOKEN_NOT_REJECTED": evidence.expired_token_rejected,
        "WRONG_AUDIENCE_NOT_REJECTED": evidence.wrong_audience_rejected,
        "WRONG_ISSUER_NOT_REJECTED": evidence.wrong_issuer_rejected,
        "MALFORMED_TOKEN_NOT_REJECTED": evidence.malformed_token_rejected,
        "UNKNOWN_ORGANIZATION_NOT_REJECTED": evidence.unknown_organization_rejected,
        "SSE_TENANT_ISOLATION_FAILED": evidence.sse_reconnect_tenant_isolation_passed,
        "RESTART_PERSISTENCE_FAILED": evidence.restart_persistence_passed,
    }
    reasons.extend(reason for reason, passed in required_checks.items() if not passed)

    return HostedStateIdentityPilotDecision(
        bundle_id=evidence.bundle_id,
        outcome="PILOT_FAIL" if reasons else "PILOT_PASS",
        reason_codes=tuple(reasons),
        evidence_sha256=evidence.artifact_sha256,
    )


def build_hosted_state_identity_pilot_evidence(**values: object) -> HostedStateIdentityPilotEvidence:
    material = {"schema_version": "hosted-state-identity-pilot-evidence-v1", **values}
    if isinstance(material.get("collected_at"), datetime):
        material["collected_at"] = _canonical_datetime(material["collected_at"])
    return HostedStateIdentityPilotEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )
