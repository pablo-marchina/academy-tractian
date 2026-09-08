from __future__ import annotations

import json

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from academy_tractian.neon_auth_identity import NeonAuthRuntimeContextProvider


def _payload() -> bytes:
    return json.dumps(
        {
            "user": {"id": "user-a"},
            "session": {
                "id": "session-a",
                "userId": "user-a",
                "activeOrganizationId": "org-a",
                "impersonatedBy": None,
            },
        }
    ).encode("utf-8")


class RecordingProvider(NeonAuthRuntimeContextProvider):
    def __init__(self, *, clock) -> None:
        super().__init__(
            base_url="https://example.neonauth.example/academy/auth",
            clock=clock,
        )
        self.force_fresh_calls: list[bool] = []

    def _fetch(self, cookie: str, *, force_fresh: bool):
        assert "better-auth.session_token=opaque" in cookie
        self.force_fresh_calls.append(force_fresh)
        return 200, _payload()


def _client(provider: RecordingProvider) -> TestClient:
    app = FastAPI()

    def context(request: Request):
        value = provider(request)
        return {"user_id": value.user_id}

    app.add_api_route("/read", context, methods=["GET"])
    app.add_api_route("/api/runs", context, methods=["POST"])
    app.add_api_route("/api/runs/", context, methods=["POST"])
    app.add_api_route("/api/actions/{action_id}/confirm", context, methods=["POST"])
    app.add_api_route("/admin/control", context, methods=["POST"])
    return TestClient(app)


def test_run_submission_reuses_recent_read_only_validation_but_action_confirmation_is_fresh() -> None:
    now = [100.0]
    provider = RecordingProvider(clock=lambda: now[0])
    with _client(provider) as client:
        cookie = {"better-auth.session_token": "opaque"}
        assert client.get("/read", cookies=cookie).status_code == 200
        assert client.post("/api/runs", cookies=cookie).status_code == 200
        assert provider.force_fresh_calls == [False]

        assert client.post("/api/actions/action-1/confirm", cookies=cookie).status_code == 200

    assert provider.force_fresh_calls == [False, True]


def test_expired_run_submission_cache_revalidates_without_bypassing_upstream_cookie_cache() -> None:
    now = [100.0]
    provider = RecordingProvider(clock=lambda: now[0])
    with _client(provider) as client:
        cookie = {"better-auth.session_token": "opaque"}
        assert client.post("/api/runs", cookies=cookie).status_code == 200
        now[0] += 2.01
        assert client.post("/api/runs", cookies=cookie).status_code == 200

    assert provider.force_fresh_calls == [False, False]


def test_trailing_slash_run_submission_is_cache_eligible() -> None:
    now = [100.0]
    provider = RecordingProvider(clock=lambda: now[0])
    with _client(provider) as client:
        cookie = {"better-auth.session_token": "opaque"}
        assert client.post("/api/runs/", cookies=cookie).status_code == 200
        assert client.post("/api/runs", cookies=cookie).status_code == 200

    assert provider.force_fresh_calls == [False]


def test_unrecognized_write_route_remains_fresh_even_when_read_cache_is_hot() -> None:
    now = [100.0]
    provider = RecordingProvider(clock=lambda: now[0])
    with _client(provider) as client:
        cookie = {"better-auth.session_token": "opaque"}
        assert client.get("/read", cookies=cookie).status_code == 200
        assert client.post("/admin/control", cookies=cookie).status_code == 200

    assert provider.force_fresh_calls == [False, True]
