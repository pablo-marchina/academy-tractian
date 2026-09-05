from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.hosted_oidc_live_attestation import (
    HostedOIDCLivePolicy,
    OIDCNegativeMatrix,
    build_hosted_oidc_live_evidence,
    decide_hosted_oidc_live,
    oidc_profile_sha256,
)
from academy_tractian.oidc_candidate_profiles import AUTH0_PILOT_PROFILE


CODE_SHA = "a" * 40
ORIGIN_SHA = "1" * 64
ISSUER_SHA = "2" * 64
AUDIENCE_SHA = "3" * 64
JWKS_SHA = "4" * 64
AZP_SHA = "5" * 64
PROFILE_SHA = oidc_profile_sha256(AUTH0_PILOT_PROFILE)


def _negative(**overrides):
    values = {
        "expired_token_rejected": True,
        "wrong_audience_rejected": True,
        "wrong_issuer_rejected": True,
        "unauthorized_azp_rejected": True,
        "malformed_token_rejected": True,
        "unsupported_algorithm_rejected": True,
        "missing_organization_rejected": True,
        "unknown_organization_rejected": True,
        "missing_required_role_rejected": True,
        "malformed_permissions_rejected": True,
    }
    values.update(overrides)
    return OIDCNegativeMatrix(**values)


def _evidence(**overrides):
    values = {
        "candidate_id": "auth0-free",
        "code_sha": CODE_SHA,
        "deployment_id": "deployment-1",
        "deployment_origin_sha256": ORIGIN_SHA,
        "profile_sha256": PROFILE_SHA,
        "issuer_sha256": ISSUER_SHA,
        "audience_sha256": AUDIENCE_SHA,
        "jwks_url_sha256": JWKS_SHA,
        "authorized_party_sha256": AZP_SHA,
        "observed_algorithm": "RS256",
        "observed_token_ttl_seconds": 3600,
        "valid_token_accepted": True,
        "asymmetric_jwks_signature_verified": True,
        "exact_issuer_verified": True,
        "exact_audience_verified": True,
        "authorized_party_verified": True,
        "organization_claim_verified": True,
        "required_role_claim_verified": True,
        "permission_allowlist_verified": True,
        "negative_matrix": _negative(),
    }
    values.update(overrides)
    return build_hosted_oidc_live_evidence(**values)


def _policy(**overrides):
    values = {
        "expected_candidate_id": "auth0-free",
        "expected_code_sha": CODE_SHA,
        "expected_deployment_origin_sha256": ORIGIN_SHA,
        "expected_profile_sha256": PROFILE_SHA,
        "expected_issuer_sha256": ISSUER_SHA,
        "expected_audience_sha256": AUDIENCE_SHA,
        "expected_jwks_url_sha256": JWKS_SHA,
        "expected_authorized_party_sha256": AZP_SHA,
        "allowed_algorithms": ("RS256",),
        "max_token_ttl_seconds": 3600,
    }
    values.update(overrides)
    return HostedOIDCLivePolicy(**values)


def test_complete_live_oidc_attestation_passes() -> None:
    decision = decide_hosted_oidc_live(evidence=_evidence(), policy=_policy())
    assert decision.outcome == "OIDC_PASS"
    assert decision.reason_codes == ()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"code_sha": "b" * 40}, "OIDC_CODE_SHA_MISMATCH"),
        ({"deployment_origin_sha256": "9" * 64}, "OIDC_DEPLOYMENT_ORIGIN_MISMATCH"),
        ({"profile_sha256": "9" * 64}, "OIDC_PROFILE_MISMATCH"),
        ({"issuer_sha256": "9" * 64}, "OIDC_ISSUER_FINGERPRINT_MISMATCH"),
        ({"observed_algorithm": "HS256"}, "OIDC_ALGORITHM_NOT_ALLOWED"),
        ({"observed_token_ttl_seconds": 3601}, "OIDC_TOKEN_TTL_EXCEEDED"),
        ({"valid_token_accepted": False}, "OIDC_VALID_TOKEN_NOT_ACCEPTED"),
        ({"required_role_claim_verified": False}, "OIDC_REQUIRED_ROLE_CLAIM_NOT_VERIFIED"),
    ],
)
def test_positive_and_provenance_gates_are_non_compensatory(overrides, reason: str) -> None:
    decision = decide_hosted_oidc_live(evidence=_evidence(**overrides), policy=_policy())
    assert decision.outcome == "OIDC_FAIL"
    assert reason in decision.reason_codes


@pytest.mark.parametrize(
    ("negative_override", "reason"),
    [
        ({"expired_token_rejected": False}, "OIDC_EXPIRED_TOKEN_NOT_REJECTED"),
        ({"wrong_audience_rejected": False}, "OIDC_WRONG_AUDIENCE_NOT_REJECTED"),
        ({"unauthorized_azp_rejected": False}, "OIDC_UNAUTHORIZED_AZP_NOT_REJECTED"),
        ({"unsupported_algorithm_rejected": False}, "OIDC_UNSUPPORTED_ALGORITHM_NOT_REJECTED"),
        ({"missing_required_role_rejected": False}, "OIDC_MISSING_REQUIRED_ROLE_NOT_REJECTED"),
        ({"malformed_permissions_rejected": False}, "OIDC_MALFORMED_PERMISSIONS_NOT_REJECTED"),
    ],
)
def test_negative_matrix_is_fail_closed(negative_override, reason: str) -> None:
    decision = decide_hosted_oidc_live(
        evidence=_evidence(negative_matrix=_negative(**negative_override)), policy=_policy()
    )
    assert decision.outcome == "OIDC_FAIL"
    assert reason in decision.reason_codes


def test_live_oidc_evidence_hash_detects_tampering_and_has_no_raw_token_fields() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    forbidden = ("token", "jwks", "secret", "password", "credential", "private_key")
    # Outcome/TTL/fingerprint field names may mention token/JWKS, but no field can contain raw material.
    assert all(not isinstance(value, str) or "eyJ" not in value for value in payload.values())
    payload["observed_token_ttl_seconds"] = 10
    with pytest.raises(ValidationError, match="hosted_oidc_live_evidence_hash_mismatch"):
        type(evidence).model_validate(payload)
