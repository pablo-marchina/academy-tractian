from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from academy_tractian.hosted_postgres_preflight import (
    ObservedPostgresSession,
    build_hosted_postgres_preflight_evidence,
    decide_hosted_postgres_preflight,
)


INTERNAL_DSN = (
    "postgresql://owner:internal-secret@db.example.com/academy?sslmode=require&channel_binding=require"
)
SCOPED_DSN = (
    "postgresql://scoped:scoped-secret@db.example.com/academy?sslmode=require&channel_binding=require"
)


def _observed(role: str, **overrides) -> ObservedPostgresSession:
    values = {
        "database_name": "academy",
        "role_name": role,
        "server_version": "18.6 (test)",
        "role_superuser": False,
        "role_bypass_rls": False,
        "role_create_role": False,
        "role_create_db": False,
        "role_inherit": False,
        "role_can_login": True,
        "tls_active": True,
    }
    values.update(overrides)
    return ObservedPostgresSession(**values)


def _evidence(*, internal=None, scoped=None, internal_dsn=INTERNAL_DSN, scoped_dsn=SCOPED_DSN):
    internal_observed = internal or _observed(
        "owner", role_create_role=True, role_create_db=True, role_bypass_rls=True, role_inherit=True
    )
    scoped_observed = scoped or _observed("scoped")
    observations = {
        internal_dsn: internal_observed,
        scoped_dsn: scoped_observed,
    }
    return build_hosted_postgres_preflight_evidence(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        inspector=observations.__getitem__,
    )


def test_hosted_postgres_preflight_accepts_distinct_tls_rls_safe_roles() -> None:
    evidence = _evidence()
    decision = decide_hosted_postgres_preflight(evidence)
    assert decision.outcome == "PREFLIGHT_PASS"
    assert decision.reason_codes == ()
    assert evidence.internal.role_sha256 != evidence.scoped.role_sha256
    assert evidence.internal.endpoint_sha256 == evidence.scoped.endpoint_sha256
    assert evidence.internal.channel_binding_required is True


@pytest.mark.parametrize(
    ("internal", "scoped", "internal_dsn", "scoped_dsn", "reason"),
    [
        (_observed("same"), _observed("same"), INTERNAL_DSN, SCOPED_DSN, "INTERNAL_AND_SCOPED_ROLE_NOT_DISTINCT"),
        (None, _observed("scoped", role_superuser=True), INTERNAL_DSN, SCOPED_DSN, "SCOPED_ROLE_SUPERUSER"),
        (None, _observed("scoped", role_bypass_rls=True), INTERNAL_DSN, SCOPED_DSN, "SCOPED_ROLE_BYPASSES_RLS"),
        (None, _observed("scoped", role_create_role=True), INTERNAL_DSN, SCOPED_DSN, "SCOPED_ROLE_CAN_CREATE_ROLE"),
        (None, _observed("scoped", role_create_db=True), INTERNAL_DSN, SCOPED_DSN, "SCOPED_ROLE_CAN_CREATE_DB"),
        (None, _observed("scoped", role_inherit=True), INTERNAL_DSN, SCOPED_DSN, "SCOPED_ROLE_INHERITS_PRIVILEGES"),
        (None, _observed("scoped", tls_active=False), INTERNAL_DSN, SCOPED_DSN, "LIVE_TLS_NOT_ACTIVE"),
        (
            None,
            None,
            "postgresql://owner:secret@db.example.com/academy",
            "postgresql://scoped:secret@db.example.com/academy?sslmode=require",
            "DSN_TLS_NOT_REQUIRED",
        ),
        (None, _observed("scoped", server_version="17.9"), INTERNAL_DSN, SCOPED_DSN, "POSTGRES_MAJOR_MISMATCH"),
    ],
)
def test_hosted_postgres_preflight_hard_gates_do_not_compensate(
    internal, scoped, internal_dsn, scoped_dsn, reason: str
) -> None:
    evidence = _evidence(
        internal=internal,
        scoped=scoped,
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
    )
    decision = decide_hosted_postgres_preflight(evidence)
    assert decision.outcome == "PREFLIGHT_FAIL"
    assert reason in decision.reason_codes


def test_preflight_evidence_is_hash_bound_and_contains_no_connection_secrets() -> None:
    evidence = _evidence()
    rendered = json.dumps(evidence.model_dump(mode="json"), sort_keys=True)
    assert "internal-secret" not in rendered
    assert "scoped-secret" not in rendered
    assert "db.example.com" not in rendered
    assert '"role_name"' not in rendered

    payload = evidence.model_dump(mode="json")
    payload["scoped"]["tls_active"] = False
    with pytest.raises(ValidationError, match="hosted_postgres_preflight_artifact_hash_mismatch"):
        type(evidence).model_validate(payload)


def test_preflight_rejects_local_database_endpoint_before_connecting() -> None:
    called = False

    def inspector(_dsn: str) -> ObservedPostgresSession:
        nonlocal called
        called = True
        return _observed("never-used")

    with pytest.raises(ValueError, match="local_hosted_postgres_endpoint_forbidden"):
        build_hosted_postgres_preflight_evidence(
            internal_dsn="postgresql://owner:secret@localhost/academy?sslmode=require",
            scoped_dsn=SCOPED_DSN,
            inspector=inspector,
        )
    assert called is False
