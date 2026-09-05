from __future__ import annotations

import json

from academy_tractian.hosted_oidc_live_attestation import (
    OIDCNegativeMatrix,
    build_hosted_oidc_live_evidence,
    oidc_profile_sha256,
)
from academy_tractian.hosted_state_identity_pilot import build_hosted_state_identity_pilot_evidence
from academy_tractian.oidc_candidate_profiles import AUTH0_PILOT_PROFILE
from scripts.check_hosted_state_identity_pilot import main


CODE_SHA = "a" * 40
ORIGIN_SHA = "1" * 64
ISSUER_SHA = "2" * 64
AUDIENCE_SHA = "3" * 64
JWKS_SHA = "4" * 64
AZP_SHA = "5" * 64


def _state():
    return build_hosted_state_identity_pilot_evidence(
        bundle_id="neon-plus-auth0",
        code_sha=CODE_SHA,
        collected_at="2026-09-04T20:15:00Z",
        deployment_origin_sha256=ORIGIN_SHA,
        database_endpoint_sha256="6" * 64,
        identity_issuer_sha256=ISSUER_SHA,
        required_local_components=0,
        observed_unexpected_cash_charge_usd=0.0,
        organization_count=2,
        user_count=2,
        clean_migration_passed=True,
        pooled_tls_postgres_passed=True,
        oidc_valid_token_accepted=True,
        oidc_jwks_rs256_verified=True,
        exact_audience_verified=True,
        exact_issuer_verified=True,
        organization_claim_verified=True,
        role_claim_verified=True,
        permission_allowlist_verified=True,
        token_ttl_verified=True,
        allowed_tenant_request_passed=True,
        cross_tenant_read_denied=True,
        cross_tenant_mutation_denied=True,
        expired_token_rejected=True,
        wrong_audience_rejected=True,
        wrong_issuer_rejected=True,
        malformed_token_rejected=True,
        unknown_organization_rejected=True,
        sse_reconnect_tenant_isolation_passed=True,
        restart_persistence_passed=True,
    )


def _oidc(**overrides):
    values = {
        "candidate_id": "auth0-free",
        "code_sha": CODE_SHA,
        "deployment_id": "deploy-1",
        "deployment_origin_sha256": ORIGIN_SHA,
        "profile_sha256": oidc_profile_sha256(AUTH0_PILOT_PROFILE),
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
        "negative_matrix": OIDCNegativeMatrix(
            expired_token_rejected=True,
            wrong_audience_rejected=True,
            wrong_issuer_rejected=True,
            unauthorized_azp_rejected=True,
            malformed_token_rejected=True,
            unsupported_algorithm_rejected=True,
            missing_organization_rejected=True,
            unknown_organization_rejected=True,
            missing_required_role_rejected=True,
            malformed_permissions_rejected=True,
        ),
    }
    values.update(overrides)
    return build_hosted_oidc_live_evidence(**values)


def _argv(state_path, oidc_path):
    return [
        "--evidence", str(state_path),
        "--oidc-evidence", str(oidc_path),
        "--expected-code-sha", CODE_SHA,
        "--expected-oidc-audience-sha256", AUDIENCE_SHA,
        "--expected-oidc-jwks-url-sha256", JWKS_SHA,
        "--expected-oidc-authorized-party-sha256", AZP_SHA,
    ]


def test_state_identity_gate_requires_bound_live_oidc_pass(tmp_path, capsys) -> None:
    state_path = tmp_path / "state.json"
    oidc_path = tmp_path / "oidc.json"
    state_path.write_text(_state().model_dump_json(), encoding="utf-8")
    oidc_path.write_text(_oidc().model_dump_json(), encoding="utf-8")
    assert main(_argv(state_path, oidc_path)) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "PILOT_PASS"
    assert payload["oidc_evidence_sha256"] == _oidc().artifact_sha256


def test_state_identity_gate_rejects_oidc_from_other_origin(tmp_path, capsys) -> None:
    state_path = tmp_path / "state.json"
    oidc_path = tmp_path / "oidc.json"
    state_path.write_text(_state().model_dump_json(), encoding="utf-8")
    oidc_path.write_text(_oidc(deployment_origin_sha256="9" * 64).model_dump_json(), encoding="utf-8")
    assert main(_argv(state_path, oidc_path)) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "PILOT_FAIL"
    assert "OIDC_DEPLOYMENT_ORIGIN_MISMATCH" in payload["reason_codes"]


def test_state_identity_gate_rejects_oidc_negative_matrix_failure(tmp_path, capsys) -> None:
    state_path = tmp_path / "state.json"
    oidc_path = tmp_path / "oidc.json"
    state_path.write_text(_state().model_dump_json(), encoding="utf-8")
    broken = _oidc(
        negative_matrix=_oidc().negative_matrix.model_copy(update={"unauthorized_azp_rejected": False})
    )
    oidc_path.write_text(broken.model_dump_json(), encoding="utf-8")
    assert main(_argv(state_path, oidc_path)) == 1
    payload = json.loads(capsys.readouterr().out)
    assert "OIDC_LIVE_ATTESTATION_FAILED" in payload["reason_codes"]
    assert "OIDC_UNAUTHORIZED_AZP_NOT_REJECTED" in payload["reason_codes"]
