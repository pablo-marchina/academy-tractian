from __future__ import annotations

from dataclasses import dataclass
from time import time

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import jwt
import pytest

from academy_tractian.hosted_config import HostedProductConfig
from academy_tractian.oidc_candidate_profiles import AUTH0_PILOT_PROFILE
from academy_tractian.oidc_runtime_identity import OIDCRuntimeContextProvider


ISSUER = "https://academy-tractian.us.auth0.com/"
AUDIENCE = "https://api.academy-tractian.example"
JWKS_URL = "https://academy-tractian.us.auth0.com/.well-known/jwks.json"
CLIENT_ID = "auth0-client-id"


@dataclass(frozen=True)
class _SigningKey:
    key: object


class _StaticSigningKeyProvider:
    def __init__(self, key: object) -> None:
        self.key = key

    def get_signing_key_from_jwt(self, _token: str) -> _SigningKey:
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
        "sub": "auth0|user-123",
        "azp": CLIENT_ID,
        "org_id": "org_alpha",
        "permissions": ["runs:read:org", "unknown:provider-permission"],
        "https://academy.tractian/role": "operator",
        "iat": now - 10,
        "nbf": now - 10,
        "exp": now + 300,
    }
    payload.update(overrides)
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "auth0-test-key"})


def _provider(public_key) -> OIDCRuntimeContextProvider:
    return OIDCRuntimeContextProvider(
        issuer=ISSUER,
        audience=AUDIENCE,
        jwks_url=JWKS_URL,
        algorithms=AUTH0_PILOT_PROFILE.algorithms,
        claim_mapping=AUTH0_PILOT_PROFILE.claim_mapping(),
        allowed_claim_permissions=("runs:read:org",),
        authorized_parties=(CLIENT_ID,),
        max_ttl_seconds=AUTH0_PILOT_PROFILE.max_token_ttl_seconds,
        signing_key_provider=_StaticSigningKeyProvider(public_key),
    )


def _client(provider: OIDCRuntimeContextProvider) -> TestClient:
    app = FastAPI()

    @app.get("/context")
    def context(request: Request):
        return provider(request).model_dump(mode="json")

    return TestClient(app)


def test_auth0_profile_maps_org_role_permissions_and_identity_without_vendor_sdk(rsa_keys) -> None:
    private, public = rsa_keys
    response = _client(_provider(public)).get(
        "/context", headers={"Authorization": f"Bearer {_token(private)}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["organization_id"] == "org_alpha"
    assert body["user_id"] == "auth0|user-123"
    assert body["identity_id"] == "auth0|user-123"
    assert body["role"] == "operator"
    assert "runs:read:org" in body["permissions"]
    assert "unknown:provider-permission" not in body["permissions"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"aud": "https://wrong.example"},
        {"azp": "attacker-client"},
        {"org_id": None},
        {"https://academy.tractian/role": None},
        {"permissions": {"runs:read:org": True}},
    ],
)
def test_auth0_profile_fails_closed_on_contract_violations(rsa_keys, overrides) -> None:
    private, public = rsa_keys
    response = _client(_provider(public)).get(
        "/context",
        headers={"Authorization": f"Bearer {_token(private, **overrides)}"},
    )
    assert response.status_code == 401


def test_auth0_profile_rejects_token_ttl_above_frozen_limit(rsa_keys) -> None:
    private, public = rsa_keys
    now = int(time())
    response = _client(_provider(public)).get(
        "/context",
        headers={
            "Authorization": f"Bearer {_token(private, iat=now - 10, exp=now + 7200)}"
        },
    )
    assert response.status_code == 401


def test_auth0_profile_is_expressible_through_existing_hosted_config() -> None:
    env = {
        "ACADEMY_POSTGRES_INTERNAL_DSN": "postgresql://internal:secret@db.example.com:5432/academy",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://scoped:secret@db.example.com:5432/academy",
        "ACADEMY_CORS_ORIGINS": "https://app.example.com",
        "ACADEMY_IDENTITY_BACKEND": "oidc",
        "ACADEMY_RUNTIME_IDENTITY_ISSUER": ISSUER,
        "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": AUDIENCE,
        "ACADEMY_OIDC_JWKS_URL": JWKS_URL,
        "ACADEMY_OIDC_AUTHORIZED_PARTIES": CLIENT_ID,
        **AUTH0_PILOT_PROFILE.environment_overrides(),
    }
    config = HostedProductConfig.from_environment(env)
    assert config.oidc_algorithms == ("RS256",)
    assert config.oidc_organization_claim == "org_id"
    assert config.oidc_role_claim == "https://academy.tractian/role"
    assert config.oidc_permissions_claim == "permissions"
    assert config.oidc_identity_claim == "sub"
    rendered = repr(config.sanitized_summary())
    assert "secret" not in rendered
    assert AUTH0_PILOT_PROFILE.candidate_id not in rendered
