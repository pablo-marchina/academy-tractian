from __future__ import annotations

import json

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest

from academy_tractian.neon_auth_identity import NeonAuthRuntimeContextProvider
from academy_tractian.product_api import DEFAULT_RUNTIME_PERMISSIONS


def _payload(
    *,
    user_id: str = "user-a",
    session_user_id: str | None = None,
    active_organization_id: str | None = None,
    impersonated_by: str | None = None,
) -> bytes:
    return json.dumps(
        {
            "user": {"id": user_id, "email": "operator@example.com", "name": "Operator"},
            "session": {
                "id": "session-a",
                "userId": session_user_id or user_id,
                "activeOrganizationId": active_organization_id,
                "impersonatedBy": impersonated_by,
            },
        }
    ).encode("utf-8")


def _client(fetch_session):
    provider = NeonAuthRuntimeContextProvider(
        base_url="https://example.neonauth.example/academy/auth",
        fetch_session=fetch_session,
    )
    app = FastAPI()

    @app.get("/context")
    def context(request: Request):
        value = provider(request)
        return {
            "organization_id": value.organization_id,
            "identity_id": value.identity_id,
            "user_id": value.user_id,
            "role": value.role,
            "permissions": sorted(value.permissions),
            "seed": value.seed,
        }

    return TestClient(app)


def test_valid_managed_session_derives_personal_tenant_without_browser_authority() -> None:
    seen: list[str] = []

    def fetch(cookie: str):
        seen.append(cookie)
        return 200, _payload()

    with _client(fetch) as client:
        response = client.get(
            "/context",
            cookies={"better-auth.session_token": "opaque-session"},
            headers={"x-organization-id": "attacker-org", "x-role": "admin"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "organization_id": "user:user-a",
        "identity_id": "neon-auth:user-a",
        "user_id": "user-a",
        "role": "operator",
        "permissions": sorted(DEFAULT_RUNTIME_PERMISSIONS),
        "seed": None,
    }
    assert seen and "opaque-session" in seen[0]


def test_managed_active_organization_becomes_tenant() -> None:
    with _client(lambda _cookie: (200, _payload(active_organization_id="org-a"))) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 200
    assert response.json()["organization_id"] == "org-a"


def test_missing_cookie_fails_closed_without_calling_auth_service() -> None:
    called = False

    def fetch(_cookie: str):
        nonlocal called
        called = True
        return 200, _payload()

    with _client(fetch) as client:
        response = client.get("/context")

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_required"
    assert called is False


@pytest.mark.parametrize(
    "body",
    [
        _payload(user_id="user-a", session_user_id="user-b"),
        _payload(impersonated_by="admin-user"),
        b"{}",
        b"not-json",
    ],
)
def test_malformed_mismatched_or_impersonated_session_fails_closed(body: bytes) -> None:
    with _client(lambda _cookie: (200, body)) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_invalid"


@pytest.mark.parametrize("auth_status", [401, 403])
def test_expired_or_rejected_managed_session_is_unauthorized(auth_status: int) -> None:
    with _client(lambda _cookie: (auth_status, b"{}")) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_invalid"


def test_managed_auth_service_failure_fails_closed() -> None:
    with _client(lambda _cookie: (503, b"{}")) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_unavailable"


@pytest.mark.parametrize(
    "base_url",
    [
        "http://auth.example.com",
        "https://localhost/auth",
        "https://127.0.0.1/auth",
        "https://user:password@auth.example.com/auth",
    ],
)
def test_auth_base_url_must_be_remote_https_without_credentials(base_url: str) -> None:
    with pytest.raises(ValueError):
        NeonAuthRuntimeContextProvider(base_url=base_url)
