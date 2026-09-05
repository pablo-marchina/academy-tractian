from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .oidc_candidate_profiles import OIDCCandidateProfile


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def fingerprint_public_value(value: str) -> str:
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > 2048:
        raise ValueError("invalid_oidc_public_value_for_fingerprint")
    return sha256(normalized.encode("utf-8")).hexdigest()


def oidc_profile_sha256(profile: OIDCCandidateProfile) -> str:
    return _canonical_sha256(
        {
            "candidate_id": profile.candidate_id,
            "algorithms": list(profile.algorithms),
            "organization_claim": profile.organization_claim,
            "role_claim": profile.role_claim,
            "permissions_claim": profile.permissions_claim,
            "identity_claim": profile.identity_claim,
            "max_token_ttl_seconds": profile.max_token_ttl_seconds,
            "required_custom_claims": list(profile.required_custom_claims),
        }
    )


class OIDCNegativeMatrix(_StrictModel):
    expired_token_rejected: bool
    wrong_audience_rejected: bool
    wrong_issuer_rejected: bool
    unauthorized_azp_rejected: bool
    malformed_token_rejected: bool
    unsupported_algorithm_rejected: bool
    missing_organization_rejected: bool
    unknown_organization_rejected: bool
    missing_required_role_rejected: bool
    malformed_permissions_rejected: bool


class HostedOIDCLiveEvidence(_StrictModel):
    """Sanitized live OIDC resource-server evidence with no token/JWKS payload material."""

    schema_version: Literal["hosted-oidc-live-evidence-v1"] = "hosted-oidc-live-evidence-v1"
    candidate_id: str = Field(min_length=1, max_length=128)
    code_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    deployment_id: str = Field(min_length=1, max_length=256)
    deployment_origin_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    issuer_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    audience_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    jwks_url_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authorized_party_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    observed_algorithm: str = Field(min_length=1, max_length=32)
    observed_token_ttl_seconds: int = Field(ge=1, le=86400)
    valid_token_accepted: bool
    asymmetric_jwks_signature_verified: bool
    exact_issuer_verified: bool
    exact_audience_verified: bool
    authorized_party_verified: bool
    organization_claim_verified: bool
    required_role_claim_verified: bool
    permission_allowlist_verified: bool
    negative_matrix: OIDCNegativeMatrix
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "HostedOIDCLiveEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("hosted_oidc_live_evidence_hash_mismatch")
        return self


class HostedOIDCLivePolicy(_StrictModel):
    schema_version: Literal["hosted-oidc-live-policy-v1"] = "hosted-oidc-live-policy-v1"
    expected_candidate_id: str = Field(min_length=1, max_length=128)
    expected_code_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    expected_deployment_origin_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_issuer_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_audience_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_jwks_url_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_authorized_party_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    allowed_algorithms: tuple[str, ...]
    max_token_ttl_seconds: int = Field(ge=60, le=86400)

    @model_validator(mode="after")
    def validate_algorithms(self) -> "HostedOIDCLivePolicy":
        if not self.allowed_algorithms or len(set(self.allowed_algorithms)) != len(self.allowed_algorithms):
            raise ValueError("hosted_oidc_live_policy_algorithms_invalid")
        return self


class HostedOIDCLiveDecision(_StrictModel):
    schema_version: Literal["hosted-oidc-live-decision-v1"] = "hosted-oidc-live-decision-v1"
    outcome: Literal["OIDC_PASS", "OIDC_FAIL"]
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def build_hosted_oidc_live_evidence(**values: object) -> HostedOIDCLiveEvidence:
    material = {"schema_version": "hosted-oidc-live-evidence-v1", **values}
    negative_matrix = material.get("negative_matrix")
    if isinstance(negative_matrix, OIDCNegativeMatrix):
        material["negative_matrix"] = negative_matrix.model_dump(mode="json")
    return HostedOIDCLiveEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )


def decide_hosted_oidc_live(
    *, evidence: HostedOIDCLiveEvidence, policy: HostedOIDCLivePolicy
) -> HostedOIDCLiveDecision:
    reasons: list[str] = []
    bindings = (
        (evidence.candidate_id, policy.expected_candidate_id, "OIDC_CANDIDATE_MISMATCH"),
        (evidence.code_sha, policy.expected_code_sha, "OIDC_CODE_SHA_MISMATCH"),
        (
            evidence.deployment_origin_sha256,
            policy.expected_deployment_origin_sha256,
            "OIDC_DEPLOYMENT_ORIGIN_MISMATCH",
        ),
        (evidence.profile_sha256, policy.expected_profile_sha256, "OIDC_PROFILE_MISMATCH"),
        (evidence.issuer_sha256, policy.expected_issuer_sha256, "OIDC_ISSUER_FINGERPRINT_MISMATCH"),
        (
            evidence.audience_sha256,
            policy.expected_audience_sha256,
            "OIDC_AUDIENCE_FINGERPRINT_MISMATCH",
        ),
        (evidence.jwks_url_sha256, policy.expected_jwks_url_sha256, "OIDC_JWKS_FINGERPRINT_MISMATCH"),
        (
            evidence.authorized_party_sha256,
            policy.expected_authorized_party_sha256,
            "OIDC_AUTHORIZED_PARTY_FINGERPRINT_MISMATCH",
        ),
    )
    reasons.extend(reason for observed, expected, reason in bindings if observed != expected)
    if evidence.observed_algorithm not in policy.allowed_algorithms:
        reasons.append("OIDC_ALGORITHM_NOT_ALLOWED")
    if evidence.observed_token_ttl_seconds > policy.max_token_ttl_seconds:
        reasons.append("OIDC_TOKEN_TTL_EXCEEDED")

    positive = {
        "OIDC_VALID_TOKEN_NOT_ACCEPTED": evidence.valid_token_accepted,
        "OIDC_ASYMMETRIC_JWKS_NOT_VERIFIED": evidence.asymmetric_jwks_signature_verified,
        "OIDC_EXACT_ISSUER_NOT_VERIFIED": evidence.exact_issuer_verified,
        "OIDC_EXACT_AUDIENCE_NOT_VERIFIED": evidence.exact_audience_verified,
        "OIDC_AUTHORIZED_PARTY_NOT_VERIFIED": evidence.authorized_party_verified,
        "OIDC_ORGANIZATION_CLAIM_NOT_VERIFIED": evidence.organization_claim_verified,
        "OIDC_REQUIRED_ROLE_CLAIM_NOT_VERIFIED": evidence.required_role_claim_verified,
        "OIDC_PERMISSION_ALLOWLIST_NOT_VERIFIED": evidence.permission_allowlist_verified,
    }
    reasons.extend(reason for reason, passed in positive.items() if not passed)

    negative = evidence.negative_matrix.model_dump()
    reason_by_case = {
        "expired_token_rejected": "OIDC_EXPIRED_TOKEN_NOT_REJECTED",
        "wrong_audience_rejected": "OIDC_WRONG_AUDIENCE_NOT_REJECTED",
        "wrong_issuer_rejected": "OIDC_WRONG_ISSUER_NOT_REJECTED",
        "unauthorized_azp_rejected": "OIDC_UNAUTHORIZED_AZP_NOT_REJECTED",
        "malformed_token_rejected": "OIDC_MALFORMED_TOKEN_NOT_REJECTED",
        "unsupported_algorithm_rejected": "OIDC_UNSUPPORTED_ALGORITHM_NOT_REJECTED",
        "missing_organization_rejected": "OIDC_MISSING_ORGANIZATION_NOT_REJECTED",
        "unknown_organization_rejected": "OIDC_UNKNOWN_ORGANIZATION_NOT_REJECTED",
        "missing_required_role_rejected": "OIDC_MISSING_REQUIRED_ROLE_NOT_REJECTED",
        "malformed_permissions_rejected": "OIDC_MALFORMED_PERMISSIONS_NOT_REJECTED",
    }
    reasons.extend(reason_by_case[name] for name, passed in negative.items() if not passed)

    deduped = tuple(dict.fromkeys(reasons))
    return HostedOIDCLiveDecision(
        outcome="OIDC_PASS" if not deduped else "OIDC_FAIL",
        reason_codes=deduped,
        evidence_sha256=evidence.artifact_sha256,
    )
