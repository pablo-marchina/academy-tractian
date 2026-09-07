from __future__ import annotations

from io import BytesIO
import json
from urllib.error import HTTPError

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest

import academy_tractian.neon_auth_identity as neon_auth_identity
from academy_tractian.neon_auth_identity import NeonAuthRuntimeContextProvider
from academy_tractian.product_api import DEFAULT_RUNTIME_PERMISSIONS


def _payload(
    *,
    user_id: str = "user-a",
    session_user_id: str | None = None,
    active_organization_id: object = None,
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


def _client(fetch_session=None, *, clock=None):
    kwargs = {
        "base_url": "https://example.neonauth.example/academy/auth",
        "fetch_session": fetch_session,
    }
    if clock is not None:
        kwargs["clock"] = clock
    provider = NeonAuthRuntimeContextProvider(**kwargs)
    app = FastAPI()

    @app.api_route("/context", methods=["GET", "POST"])
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
            headers={
                "x-organization-id": "attacker-org",
                "x-user-id": "attacker-user",
                "x-role": "admin",
                "x-permissions": "*",
            },
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


def test_duplicate_cookie_headers_fail_closed_before_auth_service() -> None:
    called = False

    def fetch(_cookie: str):
        nonlocal called
        called = True
        return 200, _payload()

    with _client(fetch) as client:
        response = client.get(
            "/context",
            headers=[
                ("cookie", "better-auth.session_token=first"),
                ("cookie", "better-auth.session_token=second"),
            ],
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_required"
    assert called is False


def test_oversized_cookie_fails_closed_before_auth_service() -> None:
    called = False

    def fetch(_cookie: str):
        nonlocal called
        called = True
        return 200, _payload()

    with _client(fetch) as client:
        response = client.get(
            "/context",
            headers={"cookie": f"better-auth.session_token={'x' * (16 * 1024)}"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_required"
    assert called is False


@pytest.mark.parametrize(
    "body",
    [
        _payload(user_id="user-a", session_user_id="user-b"),
        _payload(impersonated_by="admin-user"),
        _payload(user_id=" user-a "),
        _payload(user_id="user-a\nadmin"),
        _payload(user_id="x" * 257),
        _payload(active_organization_id=" org-a "),
        _payload(active_organization_id="org-a\norg-b"),
        _payload(active_organization_id="x" * 257),
        _payload(active_organization_id={"id": "org-a"}),
        b"{}",
        b"not-json",
    ],
)
def test_malformed_mismatched_or_impersonated_session_fails_closed(body: bytes) -> None:
    with _client(lambda _cookie: (200, body)) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_invalid"


def test_oversized_managed_session_response_fails_closed() -> None:
    with _client(lambda _cookie: (200, b"{" + b"x" * (64 * 1024) + b"}")) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_invalid"


@pytest.mark.parametrize("auth_status", [401, 403])
def test_expired_or_rejected_managed_session_is_unauthorized(auth_status: int) -> None:
    with _client(lambda _cookie: (auth_status, b"{}")) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 401
    assert response.json()["detail"] == "managed_session_invalid"


def test_managed_auth_service_failure_is_service_unavailable_not_logout() -> None:
    with _client(lambda _cookie: (503, b"{}")) as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 503
    assert response.json()["detail"] == "managed_session_unavailable"
    assert response.headers["retry-after"] == "1"


def test_read_burst_reuses_validated_context_for_two_seconds() -> None:
    now = [100.0]
    calls = 0

    def fetch(_cookie: str):
        nonlocal calls
        calls += 1
        return 200, _payload()

    with _client(fetch, clock=lambda: now[0]) as client:
        first = client.get("/context", cookies={"better-auth.session_token": "opaque"})
        second = client.get("/context", cookies={"better-auth.session_token": "opaque"})
        assert first.status_code == second.status_code == 200
        assert calls == 1

        now[0] += 2.01
        third = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert third.status_code == 200
    assert calls == 2


def test_post_always_bypasses_read_cache_and_revalidates_session() -> None:
    calls = 0

    def fetch(_cookie: str):
        nonlocal calls
        calls += 1
        return 200, _payload()

    with _client(fetch) as client:
        assert client.get("/context", cookies={"better-auth.session_token": "opaque"}).status_code == 200
        assert client.post("/context", cookies={"better-auth.session_token": "opaque"}).status_code == 200
        assert client.post("/context", cookies={"better-auth.session_token": "opaque"}).status_code == 200

    assert calls == 3


def test_rejected_fresh_post_invalidates_prior_read_cache() -> None:
    responses = iter(
        [
            (200, _payload()),
            (401, b"{}"),
            (200, _payload()),
        ]
    )
    calls = 0

    def fetch(_cookie: str):
        nonlocal calls
        calls += 1
        return next(responses)

    with _client(fetch) as client:
        assert client.get("/context", cookies={"better-auth.session_token": "opaque"}).status_code == 200
        rejected = client.post("/context", cookies={"better-auth.session_token": "opaque"})
        assert rejected.status_code == 401
        assert rejected.json()["detail"] == "managed_session_invalid"
        refreshed = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert refreshed.status_code == 200
    assert calls == 3


def test_expired_read_cache_is_never_used_when_auth_service_is_unavailable() -> None:
    now = [100.0]
    calls = 0

    def fetch(_cookie: str):
        nonlocal calls
        calls += 1
        if calls == 1:
            return 200, _payload()
        return 503, b"{}"

    with _client(fetch, clock=lambda: now[0]) as client:
        assert client.get("/context", cookies={"better-auth.session_token": "opaque"}).status_code == 200
        now[0] += 2.01
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 503
    assert response.json()["detail"] == "managed_session_unavailable"
    assert calls == 2


def test_different_cookies_never_share_cached_identity() -> None:
    calls = 0

    def fetch(cookie: str):
        nonlocal calls
        calls += 1
        user_id = "user-a" if "first" in cookie else "user-b"
        return 200, _payload(user_id=user_id)

    with _client(fetch) as client:
        first = client.get("/context", cookies={"better-auth.session_token": "first"})
        second = client.get("/context", cookies={"better-auth.session_token": "second"})

    assert first.json()["user_id"] == "user-a"
    assert second.json()["user_id"] == "user-b"
    assert calls == 2


def test_network_session_fetch_disables_redirects_before_forwarding_cookie(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {"urls": []}

    class FakeOpener:
        def open(self, request, timeout):  # noqa: ANN001, ANN201
            seen["request"] = request
            seen["timeout"] = timeout
            seen["urls"].append(request.full_url)
            raise HTTPError(
                request.full_url,
                302,
                "redirect forbidden",
                {"Location": "https://attacker.example/steal"},
                BytesIO(b"redirect forbidden"),
            )

    def fake_build_opener(handler):  # noqa: ANN001, ANN201
        seen["handler"] = handler
        return FakeOpener()

    monkeypatch.setattr(neon_auth_identity, "build_opener", fake_build_opener)
    provider = NeonAuthRuntimeContextProvider(
        base_url="https://auth.example.com/academy/auth",
    )

    status_code, body = provider._network_fetch(
        "better-auth.session_token=opaque",
        force_fresh=True,
    )
    cached_status, cached_body = provider._network_fetch(
        "better-auth.session_token=opaque",
        force_fresh=False,
    )

    assert status_code == cached_status == 302
    assert body == cached_body == b"redirect forbidden"
    assert isinstance(seen["handler"], neon_auth_identity._NoAuthRedirectHandler)
    request = seen["request"]
    assert request.get_header("Cookie") == "better-auth.session_token=opaque"
    assert seen["urls"] == [
        "https://auth.example.com/academy/auth/get-session?disableCookieCache=true",
        "https://auth.example.com/academy/auth/get-session",
    ]
    assert seen["handler"].redirect_request(None, None, 302, "", {}, "https://attacker.example") is None


def test_redirect_response_is_never_treated_as_a_valid_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        NeonAuthRuntimeContextProvider,
        "_network_fetch",
        lambda self, _cookie, *, force_fresh: (302, b"redirect"),
    )

    with _client() as client:
        response = client.get("/context", cookies={"better-auth.session_token": "opaque"})

    assert response.status_code == 503
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
