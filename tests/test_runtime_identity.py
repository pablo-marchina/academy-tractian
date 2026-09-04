from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest
from pydantic import ValidationError

from academy_tractian.runtime_identity import (
    SignedBearerRuntimeContextProvider,
    SignedRuntimeIdentityClaims,
    issue_signed_runtime_token,
)


SECRET = "test-runtime-identity-secret-that-is-at-least-32-bytes"
ISSUER = "academy-test-issuer"
AUDIENCE = "academy-product"
NOW = 2_000_000_000


def _claims(**overrides) -> SignedRuntimeIdentityClaims:
    values = {
        "issuer": ISSUER,
        "audience": AUDIENCE,
        "token_id": "token-0001",
        "identity_id": "identity-user-a",
        "user_id": "user-a",
        "organization_id": "org-a",
        "role": "operator",
        "permissions": ("runs:create", "runs:read:self"),
        "issued_at": NOW - 60,
        "expires_at": NOW + 300,
    }
    values.update(overrides)
    return SignedRuntimeIdentityClaims(**values)


def _app(provider: SignedBearerRuntimeContextProvider) -> FastAPI:
    app = FastAPI()

    @app.get("/whoami")
    def whoami(request: Request):
        context = provider(request)
        return context.model_dump(mode="json")

    return app


def _authorization(claims: SignedRuntimeIdentityClaims) -> dict[str, str]:
    return {"Authorization": f"Bearer {issue_signed_runtime_token(secret=SECRET, claims=claims)}"}


def test_signed_identity_round_trip_produces_explicit_tenant_context_without_seed():
    provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        now=lambda: NOW,
    )
    with TestClient(_app(provider)) as client:
        response = client.get("/whoami", headers=_authorization(_claims()))
    assert response.status_code == 200
    body = response.json()
    assert body["organization_id"] == "org-a"
    assert body["identity_id"] == "identity-user-a"
    assert body["user_id"] == "user-a"
    assert set(body["permissions"]) == {"runs:create", "runs:read:self"}
    assert body["seed"] is None


def test_identity_rejects_missing_malformed_tampered_wrong_scope_and_expired_tokens():
    provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        now=lambda: NOW,
    )
    with TestClient(_app(provider)) as client:
        missing = client.get("/whoami")
        assert missing.status_code == 401
        assert missing.headers["www-authenticate"] == "Bearer"

        malformed = client.get("/whoami", headers={"Authorization": "Basic abc"})
        assert malformed.status_code == 401

        valid = issue_signed_runtime_token(secret=SECRET, claims=_claims())
        replacement = "A" if valid[-1] != "A" else "B"
        tampered = client.get(
            "/whoami",
            headers={"Authorization": f"Bearer {valid[:-1]}{replacement}"},
        )
        assert tampered.status_code == 401

        wrong_issuer = client.get(
            "/whoami",
            headers=_authorization(_claims(issuer="other-issuer")),
        )
        assert wrong_issuer.status_code == 401

        wrong_audience = client.get(
            "/whoami",
            headers=_authorization(_claims(audience="other-product")),
        )
        assert wrong_audience.status_code == 401

        expired = client.get(
            "/whoami",
            headers=_authorization(_claims(issued_at=NOW - 600, expires_at=NOW - 60)),
        )
        assert expired.status_code == 401
        assert expired.json()["detail"] == "runtime_identity_expired"

        future = client.get(
            "/whoami",
            headers=_authorization(_claims(issued_at=NOW + 60, expires_at=NOW + 120)),
        )
        assert future.status_code == 401

        excessive_ttl = client.get(
            "/whoami",
            headers=_authorization(_claims(issued_at=NOW, expires_at=NOW + 7200)),
        )
        assert excessive_ttl.status_code == 401


def test_global_permissions_are_server_opt_in_not_role_derived():
    admin_claims = _claims(
        role="admin",
        permissions=("runs:create", "runs:read:any", "analytics:read:global"),
    )
    default_provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        now=lambda: NOW,
    )
    with TestClient(_app(default_provider)) as client:
        denied = client.get("/whoami", headers=_authorization(admin_claims))
    assert denied.status_code == 403
    assert denied.json()["detail"] == "runtime_identity_privilege_not_enabled"

    privileged_provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        allowed_privileged_permissions={"runs:read:any", "analytics:read:global"},
        now=lambda: NOW,
    )
    with TestClient(_app(privileged_provider)) as client:
        allowed = client.get("/whoami", headers=_authorization(admin_claims))
    assert allowed.status_code == 200


def test_identity_claims_require_explicit_tenant_and_reject_benchmark_seed_or_duplicates():
    base = _claims().model_dump(mode="json")
    base.pop("organization_id")
    with pytest.raises(ValidationError):
        SignedRuntimeIdentityClaims.model_validate(base)

    with pytest.raises(ValidationError):
        SignedRuntimeIdentityClaims.model_validate(
            {**_claims().model_dump(mode="json"), "seed": "CEN-01"}
        )

    with pytest.raises(ValidationError):
        _claims(permissions=("runs:create", "runs:create"))


def test_provider_configuration_rejects_weak_secret_and_unknown_privileged_capability():
    with pytest.raises(ValueError, match="32 bytes"):
        SignedBearerRuntimeContextProvider(
            secret="too-short",
            issuer=ISSUER,
            audience=AUDIENCE,
        )
    with pytest.raises(ValueError, match="unknown privileged"):
        SignedBearerRuntimeContextProvider(
            secret=SECRET,
            issuer=ISSUER,
            audience=AUDIENCE,
            allowed_privileged_permissions={"root:anything"},
        )
