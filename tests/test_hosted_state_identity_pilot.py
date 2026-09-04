from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.hosted_state_identity_pilot import (
    HostedStateIdentityPilotPolicy,
    build_hosted_state_identity_pilot_evidence,
    decide_hosted_state_identity_pilot,
)


NOW = datetime(2026, 9, 4, 20, 15, tzinfo=UTC)
POLICY = HostedStateIdentityPilotPolicy()


def _evidence(**overrides):
    values = {
        "bundle_id": "neon-plus-auth0",
        "code_sha": "a" * 40,
        "collected_at": NOW,
        "deployment_origin_sha256": "1" * 64,
        "database_endpoint_sha256": "2" * 64,
        "identity_issuer_sha256": "3" * 64,
        "required_local_components": 0,
        "observed_unexpected_cash_charge_usd": 0.0,
        "organization_count": 2,
        "user_count": 2,
        "clean_migration_passed": True,
        "pooled_tls_postgres_passed": True,
        "oidc_valid_token_accepted": True,
        "oidc_jwks_rs256_verified": True,
        "exact_audience_verified": True,
        "exact_issuer_verified": True,
        "organization_claim_verified": True,
        "role_claim_verified": True,
        "permission_allowlist_verified": True,
        "token_ttl_verified": True,
        "allowed_tenant_request_passed": True,
        "cross_tenant_read_denied": True,
        "cross_tenant_mutation_denied": True,
        "expired_token_rejected": True,
        "wrong_audience_rejected": True,
        "wrong_issuer_rejected": True,
        "malformed_token_rejected": True,
        "unknown_organization_rejected": True,
        "sse_reconnect_tenant_isolation_passed": True,
        "restart_persistence_passed": True,
    }
    values.update(overrides)
    return build_hosted_state_identity_pilot_evidence(**values)


def test_complete_hosted_bundle_evidence_passes() -> None:
    decision = decide_hosted_state_identity_pilot(evidence=_evidence(), policy=POLICY)
    assert decision.outcome == "PILOT_PASS"
    assert decision.reason_codes == ()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"bundle_id": "other-bundle"}, "BUNDLE_ID_MISMATCH"),
        ({"required_local_components": 1}, "LOCAL_COMPONENT_LIMIT_EXCEEDED"),
        ({"observed_unexpected_cash_charge_usd": 0.01}, "UNEXPECTED_CASH_CHARGE"),
        ({"organization_count": 1}, "INSUFFICIENT_ORGANIZATIONS"),
        ({"user_count": 1}, "INSUFFICIENT_USERS"),
        ({"clean_migration_passed": False}, "CLEAN_MIGRATION_FAILED"),
        ({"pooled_tls_postgres_passed": False}, "POOLED_TLS_POSTGRES_FAILED"),
        ({"oidc_valid_token_accepted": False}, "OIDC_VALID_TOKEN_NOT_ACCEPTED"),
        ({"oidc_jwks_rs256_verified": False}, "OIDC_RS256_JWKS_NOT_VERIFIED"),
        ({"exact_audience_verified": False}, "OIDC_AUDIENCE_NOT_VERIFIED"),
        ({"exact_issuer_verified": False}, "OIDC_ISSUER_NOT_VERIFIED"),
        ({"organization_claim_verified": False}, "OIDC_ORGANIZATION_CLAIM_NOT_VERIFIED"),
        ({"role_claim_verified": False}, "OIDC_ROLE_CLAIM_NOT_VERIFIED"),
        ({"permission_allowlist_verified": False}, "OIDC_PERMISSION_ALLOWLIST_NOT_VERIFIED"),
        ({"token_ttl_verified": False}, "OIDC_TOKEN_TTL_NOT_VERIFIED"),
        ({"allowed_tenant_request_passed": False}, "ALLOWED_TENANT_REQUEST_FAILED"),
        ({"cross_tenant_read_denied": False}, "CROSS_TENANT_READ_NOT_DENIED"),
        ({"cross_tenant_mutation_denied": False}, "CROSS_TENANT_MUTATION_NOT_DENIED"),
        ({"expired_token_rejected": False}, "EXPIRED_TOKEN_NOT_REJECTED"),
        ({"wrong_audience_rejected": False}, "WRONG_AUDIENCE_NOT_REJECTED"),
        ({"wrong_issuer_rejected": False}, "WRONG_ISSUER_NOT_REJECTED"),
        ({"malformed_token_rejected": False}, "MALFORMED_TOKEN_NOT_REJECTED"),
        ({"unknown_organization_rejected": False}, "UNKNOWN_ORGANIZATION_NOT_REJECTED"),
        ({"sse_reconnect_tenant_isolation_passed": False}, "SSE_TENANT_ISOLATION_FAILED"),
        ({"restart_persistence_passed": False}, "RESTART_PERSISTENCE_FAILED"),
    ],
)
def test_each_live_pilot_gate_is_non_compensatory(overrides, reason: str) -> None:
    decision = decide_hosted_state_identity_pilot(evidence=_evidence(**overrides), policy=POLICY)
    assert decision.outcome == "PILOT_FAIL"
    assert reason in decision.reason_codes


def test_multiple_failures_are_preserved_in_one_decision() -> None:
    decision = decide_hosted_state_identity_pilot(
        evidence=_evidence(
            cross_tenant_read_denied=False,
            cross_tenant_mutation_denied=False,
            wrong_audience_rejected=False,
        ),
        policy=POLICY,
    )
    assert decision.outcome == "PILOT_FAIL"
    assert set(decision.reason_codes) == {
        "CROSS_TENANT_READ_NOT_DENIED",
        "CROSS_TENANT_MUTATION_NOT_DENIED",
        "WRONG_AUDIENCE_NOT_REJECTED",
    }


def test_live_pilot_artifact_is_hash_bound_and_contains_no_secret_material_fields() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    forbidden_markers = (
        "raw_token",
        "bearer",
        "password",
        "secret",
        "dsn",
        "credential",
        "api_key",
        "private_key",
    )
    assert not any(marker in key.lower() for key in payload for marker in forbidden_markers)

    payload["cross_tenant_read_denied"] = False
    with pytest.raises(ValidationError, match="hosted_state_identity_pilot_artifact_hash_mismatch"):
        type(evidence).model_validate(payload)
