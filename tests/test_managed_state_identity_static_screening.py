from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path

from academy_tractian.managed_state_identity_feasibility import (
    HostedIdentityEvidence,
    HostedIdentityPolicy,
    ManagedPostgresEvidence,
    ManagedPostgresPolicy,
    decide_hosted_identity_set,
    decide_managed_postgres_set,
    decide_state_identity_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "research" / "managed-state-identity-source-manifest-2026-09-04.json"
SCREENING_PATH = ROOT / "research" / "managed-state-identity-static-screening-2026-09-04.json"
EVALUATED_AT = datetime(2026, 9, 4, 20, 0, tzinfo=UTC)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_source_manifest_hash_is_bound_into_screening_evidence() -> None:
    manifest = _load(MANIFEST_PATH)
    screening = _load(SCREENING_PATH)
    expected_hash = _canonical_sha256(manifest)
    assert expected_hash == screening["source_manifest_sha256"]
    for item in screening["database_candidates"] + screening["identity_candidates"]:
        assert item["source_manifest_sha256"] == expected_hash


def test_static_screening_reproduces_preregistered_database_and_identity_outcomes() -> None:
    screening = _load(SCREENING_PATH)
    db_policy = ManagedPostgresPolicy(
        max_evidence_age_days=screening["database_policy"]["max_evidence_age_days"],
        allowed_service_maturities=tuple(screening["database_policy"]["allowed_service_maturities"]),
        require_zero_cost_guardrail=screening["database_policy"]["require_zero_cost_guardrail"],
        min_restore_window_hours=screening["database_policy"]["min_restore_window_hours"],
        min_free_storage_mb=screening["database_policy"]["min_free_storage_mb"],
        forbid_manual_inactivity_reactivation=screening["database_policy"]["forbid_manual_inactivity_reactivation"],
    )
    identity_policy = HostedIdentityPolicy(
        max_evidence_age_days=screening["identity_policy"]["max_evidence_age_days"],
        allowed_service_maturities=tuple(screening["identity_policy"]["allowed_service_maturities"]),
        require_zero_cost_guardrail=screening["identity_policy"]["require_zero_cost_guardrail"],
        require_production_without_billing_instrument=screening["identity_policy"]["require_production_without_billing_instrument"],
        max_token_ttl_seconds=screening["identity_policy"]["max_token_ttl_seconds"],
        require_first_class_organizations=screening["identity_policy"]["require_first_class_organizations"],
        min_free_active_users=screening["identity_policy"]["min_free_active_users"],
        min_free_organizations=screening["identity_policy"]["min_free_organizations"],
        forbid_manual_inactivity_reactivation=screening["identity_policy"]["forbid_manual_inactivity_reactivation"],
    )

    db_evidence = tuple(ManagedPostgresEvidence.model_validate(item) for item in screening["database_candidates"])
    identity_evidence = tuple(HostedIdentityEvidence.model_validate(item) for item in screening["identity_candidates"])
    db_decisions = decide_managed_postgres_set(evidence=db_evidence, policy=db_policy, evaluated_at=EVALUATED_AT)
    identity_decisions = decide_hosted_identity_set(evidence=identity_evidence, policy=identity_policy, evaluated_at=EVALUATED_AT)

    assert {item.candidate_id: item.outcome for item in db_decisions} == screening["expected_static_decisions"]["databases"]
    assert {item.candidate_id: item.outcome for item in identity_decisions} == screening["expected_static_decisions"]["identities"]

    db_by_id = {item.candidate_id: item for item in db_decisions}
    identity_by_id = {item.candidate_id: item for item in identity_decisions}
    bundles = {
        "neon-plus-clerk": decide_state_identity_bundle(
            bundle_id="neon-plus-clerk", database=db_by_id["neon-free"], identity=identity_by_id["clerk-hobby"]
        ),
        "neon-plus-auth0": decide_state_identity_bundle(
            bundle_id="neon-plus-auth0", database=db_by_id["neon-free"], identity=identity_by_id["auth0-free"]
        ),
        "supabase-plus-clerk": decide_state_identity_bundle(
            bundle_id="supabase-plus-clerk", database=db_by_id["supabase-free"], identity=identity_by_id["clerk-hobby"]
        ),
        "neon-plus-neon-auth": decide_state_identity_bundle(
            bundle_id="neon-plus-neon-auth", database=db_by_id["neon-free"], identity=identity_by_id["neon-auth-free"]
        ),
    }
    assert {key: value.outcome for key, value in bundles.items()} == screening["expected_static_decisions"]["bundles"]


def test_static_screening_preserves_reason_codes_for_rejected_frontier() -> None:
    screening = _load(SCREENING_PATH)
    db_policy = ManagedPostgresPolicy(max_evidence_age_days=7, min_restore_window_hours=6, min_free_storage_mb=500)
    identity_policy = HostedIdentityPolicy(
        max_evidence_age_days=7,
        max_token_ttl_seconds=3600,
        min_free_active_users=1_000,
        min_free_organizations=2,
    )
    db = decide_managed_postgres_set(
        evidence=tuple(ManagedPostgresEvidence.model_validate(item) for item in screening["database_candidates"]),
        policy=db_policy,
        evaluated_at=EVALUATED_AT,
    )
    identity = decide_hosted_identity_set(
        evidence=tuple(HostedIdentityEvidence.model_validate(item) for item in screening["identity_candidates"]),
        policy=identity_policy,
        evaluated_at=EVALUATED_AT,
    )
    db_reasons = {item.candidate_id: set(item.reason_codes) for item in db}
    identity_reasons = {item.candidate_id: set(item.reason_codes) for item in identity}

    assert "MANUAL_INACTIVITY_REACTIVATION_FORBIDDEN" in db_reasons["supabase-free"]
    assert "RESTORE_SUPPORT_REQUIRED" in db_reasons["supabase-free"]
    assert "ORGANIZATION_CLAIM_UNKNOWN" in identity_reasons["clerk-hobby"]
    assert "SERVICE_MATURITY_NOT_ALLOWED" in identity_reasons["neon-auth-free"]
    assert "PRODUCTION_REQUIRES_BILLING_INSTRUMENT" in identity_reasons["workos-authkit-free"]
    assert identity_reasons["auth0-free"] == set()
