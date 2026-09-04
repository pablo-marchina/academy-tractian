from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from academy_tractian.managed_state_identity_feasibility import (
    HostedIdentityPolicy,
    ManagedPostgresPolicy,
    build_hosted_identity_evidence,
    build_managed_postgres_evidence,
    decide_hosted_identity_feasibility,
    decide_managed_postgres_feasibility,
    decide_state_identity_bundle,
)


NOW = datetime(2026, 9, 4, 20, 0, tzinfo=UTC)
SOURCE_HASH = "2" * 64
DB_POLICY = ManagedPostgresPolicy(
    max_evidence_age_days=7,
    min_restore_window_hours=6,
    min_free_storage_mb=500,
)
IDENTITY_POLICY = HostedIdentityPolicy(
    max_evidence_age_days=7,
    max_token_ttl_seconds=3600,
    min_free_active_users=1_000,
    min_free_organizations=10,
)


def _database(**overrides):
    values = {
        "candidate_id": "neon-free",
        "collected_at": NOW - timedelta(hours=1),
        "source_manifest_sha256": SOURCE_HASH,
        "hosted_service": True,
        "required_local_components": 0,
        "zero_cost_guardrail": "yes",
        "service_maturity": "ga",
        "postgres_wire_compatible": "yes",
        "tls_external_connections": "yes",
        "pooled_connections": "yes",
        "row_level_security": "yes",
        "transaction_support": "yes",
        "inactivity_requires_manual_reactivation": "no",
        "restore_supported": "yes",
        "restore_window_hours": 6.0,
        "automatic_backups": "yes",
        "free_storage_mb": 512,
        "migration_class": "none",
    }
    values.update(overrides)
    return build_managed_postgres_evidence(**values)


def _identity(**overrides):
    values = {
        "candidate_id": "clerk-hobby",
        "collected_at": NOW - timedelta(hours=1),
        "source_manifest_sha256": SOURCE_HASH,
        "hosted_service": True,
        "required_local_components": 0,
        "zero_cost_guardrail": "yes",
        "production_without_billing_instrument": "yes",
        "service_maturity": "ga",
        "asymmetric_jwks": "yes",
        "issuer_claim": "yes",
        "audience_claim_configurable": "yes",
        "subject_claim": "yes",
        "organization_claim_configurable": "yes",
        "role_claim_configurable": "yes",
        "permissions_claim_configurable": "yes",
        "authorized_party_claim": "yes",
        "token_ttl_configurable_to_max_seconds": 60,
        "first_class_organizations": "yes",
        "free_active_users": 50_000,
        "free_organizations": 100,
        "inactivity_requires_manual_reactivation": "no",
        "migration_class": "minor",
    }
    values.update(overrides)
    return build_hosted_identity_evidence(**values)


def test_database_and_identity_are_independently_admissible() -> None:
    database = decide_managed_postgres_feasibility(
        evidence=_database(), policy=DB_POLICY, evaluated_at=NOW
    )
    identity = decide_hosted_identity_feasibility(
        evidence=_identity(), policy=IDENTITY_POLICY, evaluated_at=NOW
    )
    bundle = decide_state_identity_bundle(
        bundle_id="neon-plus-clerk", database=database, identity=identity
    )
    assert database.outcome == "PILOT_ADMISSIBLE"
    assert identity.outcome == "PILOT_ADMISSIBLE"
    assert bundle.outcome == "PILOT_ADMISSIBLE"
    assert bundle.reason_codes == ()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"required_local_components": 1}, "LOCAL_COMPONENT_LIMIT_EXCEEDED"),
        ({"zero_cost_guardrail": "no"}, "ZERO_COST_GUARDRAIL_REQUIRED"),
        ({"zero_cost_guardrail": "unknown"}, "ZERO_COST_GUARDRAIL_UNKNOWN"),
        ({"postgres_wire_compatible": "no"}, "POSTGRES_WIRE_REQUIRED"),
        ({"tls_external_connections": "no"}, "TLS_EXTERNAL_CONNECTIONS_REQUIRED"),
        ({"pooled_connections": "no"}, "POOLED_CONNECTIONS_REQUIRED"),
        ({"row_level_security": "no"}, "ROW_LEVEL_SECURITY_REQUIRED"),
        ({"transaction_support": "no"}, "TRANSACTION_SUPPORT_REQUIRED"),
        ({"inactivity_requires_manual_reactivation": "yes"}, "MANUAL_INACTIVITY_REACTIVATION_FORBIDDEN"),
        ({"restore_supported": "no"}, "RESTORE_SUPPORT_REQUIRED"),
        ({"restore_window_hours": 5.9}, "RESTORE_WINDOW_INSUFFICIENT"),
        ({"free_storage_mb": 499}, "FREE_STORAGE_INSUFFICIENT"),
        ({"migration_class": "major"}, "MIGRATION_CLASS_NOT_ALLOWED"),
    ],
)
def test_database_hard_gates_are_non_compensatory(overrides, reason: str) -> None:
    decision = decide_managed_postgres_feasibility(
        evidence=_database(**overrides), policy=DB_POLICY, evaluated_at=NOW
    )
    assert decision.outcome == "STATIC_REJECT"
    assert reason in decision.reason_codes


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"required_local_components": 1}, "LOCAL_COMPONENT_LIMIT_EXCEEDED"),
        ({"zero_cost_guardrail": "no"}, "ZERO_COST_GUARDRAIL_REQUIRED"),
        ({"production_without_billing_instrument": "no"}, "PRODUCTION_REQUIRES_BILLING_INSTRUMENT"),
        ({"asymmetric_jwks": "no"}, "ASYMMETRIC_JWKS_REQUIRED"),
        ({"audience_claim_configurable": "no"}, "AUDIENCE_CLAIM_REQUIRED"),
        ({"organization_claim_configurable": "no"}, "ORGANIZATION_CLAIM_REQUIRED"),
        ({"role_claim_configurable": "no"}, "ROLE_CLAIM_REQUIRED"),
        ({"permissions_claim_configurable": "no"}, "PERMISSIONS_CLAIM_REQUIRED"),
        ({"token_ttl_configurable_to_max_seconds": 3601}, "TOKEN_TTL_TOO_LONG"),
        ({"first_class_organizations": "no"}, "FIRST_CLASS_ORGANIZATIONS_REQUIRED"),
        ({"free_active_users": 999}, "FREE_USER_CAPACITY_INSUFFICIENT"),
        ({"free_organizations": 9}, "FREE_ORGANIZATION_CAPACITY_INSUFFICIENT"),
        ({"inactivity_requires_manual_reactivation": "yes"}, "MANUAL_INACTIVITY_REACTIVATION_FORBIDDEN"),
        ({"service_maturity": "beta"}, "SERVICE_MATURITY_NOT_ALLOWED"),
    ],
)
def test_identity_hard_gates_are_non_compensatory(overrides, reason: str) -> None:
    decision = decide_hosted_identity_feasibility(
        evidence=_identity(**overrides), policy=IDENTITY_POLICY, evaluated_at=NOW
    )
    assert decision.outcome == "STATIC_REJECT"
    assert reason in decision.reason_codes


def test_database_strength_cannot_compensate_identity_failure() -> None:
    database = decide_managed_postgres_feasibility(
        evidence=_database(free_storage_mb=100_000), policy=DB_POLICY, evaluated_at=NOW
    )
    identity = decide_hosted_identity_feasibility(
        evidence=_identity(audience_claim_configurable="no"),
        policy=IDENTITY_POLICY,
        evaluated_at=NOW,
    )
    bundle = decide_state_identity_bundle(
        bundle_id="strong-db-bad-auth", database=database, identity=identity
    )
    assert database.outcome == "PILOT_ADMISSIBLE"
    assert bundle.outcome == "STATIC_REJECT"
    assert "IDENTITY:AUDIENCE_CLAIM_REQUIRED" in bundle.reason_codes


def test_identity_strength_cannot_compensate_database_failure() -> None:
    database = decide_managed_postgres_feasibility(
        evidence=_database(inactivity_requires_manual_reactivation="yes"),
        policy=DB_POLICY,
        evaluated_at=NOW,
    )
    identity = decide_hosted_identity_feasibility(
        evidence=_identity(free_active_users=1_000_000), policy=IDENTITY_POLICY, evaluated_at=NOW
    )
    bundle = decide_state_identity_bundle(
        bundle_id="bad-db-strong-auth", database=database, identity=identity
    )
    assert identity.outcome == "PILOT_ADMISSIBLE"
    assert bundle.outcome == "STATIC_REJECT"
    assert "DATABASE:MANUAL_INACTIVITY_REACTIVATION_FORBIDDEN" in bundle.reason_codes


def test_scale_to_zero_is_allowed_when_reactivation_is_automatic() -> None:
    decision = decide_managed_postgres_feasibility(
        evidence=_database(inactivity_requires_manual_reactivation="no"),
        policy=DB_POLICY,
        evaluated_at=NOW,
    )
    assert decision.outcome == "PILOT_ADMISSIBLE"


def test_stale_and_future_evidence_fail_closed() -> None:
    stale = decide_managed_postgres_feasibility(
        evidence=_database(collected_at=NOW - timedelta(days=8)), policy=DB_POLICY, evaluated_at=NOW
    )
    future = decide_hosted_identity_feasibility(
        evidence=_identity(collected_at=NOW + timedelta(seconds=1)),
        policy=IDENTITY_POLICY,
        evaluated_at=NOW,
    )
    assert stale.reason_codes[0] == "EVIDENCE_STALE"
    assert future.reason_codes[0] == "EVIDENCE_FROM_FUTURE"


def test_evidence_hashes_are_tamper_evident() -> None:
    database = _database()
    payload = database.model_dump(mode="json")
    payload["free_storage_mb"] = 100_000
    with pytest.raises(ValidationError, match="managed_postgres_artifact_hash_mismatch"):
        type(database).model_validate(payload)

    identity = _identity()
    payload = identity.model_dump(mode="json")
    payload["free_organizations"] = 1_000
    with pytest.raises(ValidationError, match="hosted_identity_artifact_hash_mismatch"):
        type(identity).model_validate(payload)
