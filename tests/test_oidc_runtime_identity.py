from __future__ import annotations

from dataclasses import dataclass
from time import time

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import jwt
import pytest

from academy_tractian.oidc_runtime_identity import OIDCClaimMapping, OIDCRuntimeContextProvider


ISSUER = "https://identity.example.com"
AUDIENCE = "academy-api"
JWKS_URL = "https://identity.example.com/.well-known/jwks.json"


@dataclass(frozen=True)
class _SigningKey:
    key: object


class _StaticSigningKeyProvider:
    def __init__(self, key: object) -> None:
        self.key = key
        self.calls = 0

    def get_signing_key_from_jwt(self, _token: str) -> _SigningKey:
        self.calls += 1
        return _SigningKey(self.key)


@pytest.fixture(scope="module")
def rsa_keys():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private, private.public_key()


def _token(private_key, **overrides) -> str:
    now = int(time())
    payload = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "user-123",
        "sid": "session-123",
        "organization_id": "org-123",
        "role": "operator",
        "permissions": ["runs:read:org", "unknown:permission"],
        "azp": "https://app.example.com",
        "iat": now - 10,
        "nbf": now - 10,
        "exp": now + 300,
    }
    payload.update(overrides)
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "test-key"})


def _client(provider: OIDCRuntimeContextProvider) -> TestClient:
    app = FastAPI()

    @app.get("/context")
    def context(request: Request):
        return provider(request).model_dump(mode="json")

    return TestClient(app)


def _provider(public_key, **kwargs) -> OIDCRuntimeContextProvider:
    return OIDCRuntimeContextProvider(
        issuer=ISSUER,
        audience=AUDIENCE,
        jwks_url=JWKS_URL,
        algorithms=("RS256",),
        claim_mapping=OIDCClaimMapping(),
        allowed_claim_permissions=("runs:read:org",),
        authorized_parties=("https://app.example.com",),
        signing_key_provider=_StaticSigningKeyProvider(public_key),
        **kwargs,
    )


def test_oidc_provider_verifies_asymmetric_jwt_and_maps_tenant_context(rsa_keys) -> None:
    private, public = rsa_keys
    client = _client(_provider(public))

    response = client.get("/context", headers={"Authorization": f"Bearer {_token(private)}"})
    assert response.status_code == 200
    body = response.json()
    assert body["organization_id"] == "org-123"
    assert body["identity_id"] == "session-123"
    assert body["user_id"] == "user-123"
    assert body["role"] == "operator"
    assert set(body["permissions"]) == {
        "actions:confirm:self",
        "actions:read:self",
        "runs:create",
        "runs:read:org",
        "runs:read:self",
    }
    assert body["seed"] is None


def test_oidc_provider_rejects_wrong_audience_missing_org_and_wrong_authorized_party(rsa_keys) -> None:
    private, public = rsa_keys
    client = _client(_provider(public))

    wrong_audience = client.get(
        "/context",
        headers={"Authorization": f"Bearer {_token(private, aud='other-api')}"},
    )
    assert wrong_audience.status_code == 401

    missing_org = client.get(
        "/context",
        headers={"Authorization": f"Bearer {_token(private, organization_id=None)}"},
    )
    assert missing_org.status_code == 401

    wrong_party = client.get(
        "/context",
        headers={"Authorization": f"Bearer {_token(private, azp='https://evil.example.com')}"},
    )
    assert wrong_party.status_code == 401


def test_oidc_provider_enforces_configured_required_claims_without_vendor_logic(rsa_keys) -> None:
    private, public = rsa_keys
    provider = OIDCRuntimeContextProvider(
        issuer=ISSUER,
        audience=AUDIENCE,
        jwks_url=JWKS_URL,
        algorithms=("RS256",),
        claim_mapping=OIDCClaimMapping(required_claims=("role",)),
        signing_key_provider=_StaticSigningKeyProvider(public),
    )
    client = _client(provider)

    accepted = client.get(
        "/context",
        headers={"Authorization": f"Bearer {_token(private)}"},
    )
    assert accepted.status_code == 200

    rejected = client.get(
        "/context",
        headers={"Authorization": f"Bearer {_token(private, role=None)}"},
    )
    assert rejected.status_code == 401


def test_oidc_provider_rejects_excessive_ttl_and_privileged_configuration_without_second_gate(
    rsa_keys,
) -> None:
    private, public = rsa_keys
    now = int(time())
    client = _client(_provider(public, max_ttl_seconds=600))
    response = client.get(
        "/context",
        headers={
            "Authorization": f"Bearer {_token(private, iat=now - 10, exp=now + 7200)}"
        },
    )
    assert response.status_code == 401

    with pytest.raises(ValueError, match="privileged claim permission"):
        OIDCRuntimeContextProvider(
            issuer=ISSUER,
            audience=AUDIENCE,
            jwks_url=JWKS_URL,
            algorithms=("RS256",),
            allowed_claim_permissions=("analytics:read:global",),
            signing_key_provider=_StaticSigningKeyProvider(public),
        )


def test_oidc_provider_rejects_symmetric_or_attacker_selected_algorithm(rsa_keys) -> None:
    _, public = rsa_keys
    with pytest.raises(ValueError, match="asymmetric"):
        OIDCRuntimeContextProvider(
            issuer=ISSUER,
            audience=AUDIENCE,
            jwks_url=JWKS_URL,
            algorithms=("HS256",),
            signing_key_provider=_StaticSigningKeyProvider(public),
        )

    with pytest.raises(ValueError, match="configured explicitly"):
        OIDCRuntimeContextProvider(
            issuer=ISSUER,
            audience=AUDIENCE,
            jwks_url=JWKS_URL,
            algorithms=(),
            signing_key_provider=_StaticSigningKeyProvider(public),
        )


def test_oidc_provider_requires_exact_bearer_header(rsa_keys) -> None:
    _, public = rsa_keys
    client = _client(_provider(public))
    response = client.get("/context")
    assert response.status_code == 401
    assert response.json()["detail"] == "oidc_bearer_required"
