from __future__ import annotations

from academy_tractian.neon_authenticated_postgres_product_api import public_session_context
from academy_tractian.product_api import AuthenticatedRuntimeContext


def _context(*, user_id: str, organization_id: str) -> AuthenticatedRuntimeContext:
    return AuthenticatedRuntimeContext(
        organization_id=organization_id,
        identity_id=f"neon-auth:{user_id}",
        user_id=user_id,
        role="operator",
        permissions=frozenset({"runs:create", "runs:read:self", "actions:read:self"}),
    )


def test_public_session_context_is_stable_and_hides_raw_managed_ids() -> None:
    context = _context(user_id="managed-user-123", organization_id="user:managed-user-123")

    first = public_session_context(context)
    second = public_session_context(context)

    assert first == second
    assert first["schema_version"] == "production-session-context-v1"
    assert first["organization_kind"] == "personal"
    assert first["server_owned"] is True
    assert first["role"] == "operator"
    assert first["permissions"] == ["actions:read:self", "runs:create", "runs:read:self"]

    serialized = repr(first)
    assert "managed-user-123" not in serialized
    assert "neon-auth:managed-user-123" not in serialized
    assert len(str(first["user_fingerprint"])) == 24
    assert len(str(first["organization_fingerprint"])) == 24


def test_public_session_context_distinguishes_users_and_organizations() -> None:
    first = public_session_context(_context(user_id="user-a", organization_id="user:user-a"))
    second = public_session_context(_context(user_id="user-b", organization_id="user:user-b"))

    assert first["user_fingerprint"] != second["user_fingerprint"]
    assert first["identity_fingerprint"] != second["identity_fingerprint"]
    assert first["organization_fingerprint"] != second["organization_fingerprint"]


def test_public_session_context_marks_managed_organization_without_exposing_it() -> None:
    payload = public_session_context(_context(user_id="user-a", organization_id="org-production-a"))

    assert payload["organization_kind"] == "managed"
    assert "org-production-a" not in repr(payload)
