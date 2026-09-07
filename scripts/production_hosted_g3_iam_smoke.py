from __future__ import annotations

from dataclasses import dataclass
import http.cookiejar
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener
from uuid import uuid4


BASE_URL = os.environ.get(
    "ACADEMY_PRODUCTION_WEB_BASE_URL",
    "https://production-web-production-c9d1.up.railway.app",
).rstrip("/")
CROSS_TENANT_RUN_ID = os.environ.get(
    "ACADEMY_G3_CROSS_TENANT_RUN_ID",
    "g2-durability-234655d9",
)
TIMEOUT_SECONDS = 20


@dataclass
class HttpResult:
    status: int
    body: bytes
    headers: Any

    def json_object(self) -> dict[str, Any]:
        payload = json.loads(self.body.decode("utf-8")) if self.body else {}
        if not isinstance(payload, dict):
            raise RuntimeError("expected JSON object")
        return payload


class BrowserSession:
    def __init__(self) -> None:
        self.cookies = http.cookiejar.CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookies))

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResult:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request_headers = {
            "Accept": "application/json",
            "User-Agent": "academy-tractian-hosted-g3-iam/1",
            **({"Content-Type": "application/json"} if body is not None else {}),
            **(headers or {}),
        }
        request = Request(
            f"{BASE_URL}{path}",
            data=body,
            headers=request_headers,
            method=method,
        )
        try:
            with self.opener.open(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed remote HTTPS product origin
                return HttpResult(int(response.status), response.read(), response.headers)
        except HTTPError as exc:
            return HttpResult(int(exc.code), exc.read(), exc.headers)
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"remote request unavailable for {path}") from exc

    def cookie_names(self) -> list[str]:
        return sorted(cookie.name for cookie in self.cookies)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def error_detail(result: HttpResult) -> str | None:
    try:
        payload = result.json_object()
    except Exception:
        return None
    detail = payload.get("detail")
    return detail if isinstance(detail, str) else None


def sign_up(label: str) -> tuple[BrowserSession, dict[str, Any], dict[str, Any], dict[str, bool]]:
    browser = BrowserSession()
    unique = uuid4().hex
    email = f"academy-g3-{label}-{unique}@example.com"
    password = f"G3-{uuid4().hex}-Secure!"

    result = browser.request(
        "/auth/sign-up/email",
        method="POST",
        payload={"email": email, "password": password, "name": f"G3 {label}"},
        headers={"Origin": BASE_URL},
    )
    require(result.status in {200, 201}, f"{label} sign-up failed with HTTP {result.status}")
    require(bool(browser.cookie_names()), f"{label} sign-up did not establish a managed cookie")

    set_cookie_headers = result.headers.get_all("Set-Cookie") or []
    combined = ";".join(set_cookie_headers).lower()
    cookie_policy = {
        "httponly": "httponly" in combined,
        "secure": "secure" in combined,
        "samesite": "samesite" in combined,
    }
    require(all(cookie_policy.values()), f"{label} managed session cookie policy is incomplete")

    session_result = browser.request("/auth/get-session?disableCookieCache=true")
    require(session_result.status == 200, f"{label} get-session failed")
    session = session_result.json_object()
    require(isinstance(session.get("user"), dict), f"{label} session user missing")
    require(isinstance(session.get("session"), dict), f"{label} managed session missing")
    require(bool(session["session"].get("expiresAt")), f"{label} session expiry is not observable")

    context_result = browser.request("/api/session/context")
    require(context_result.status == 200, f"{label} server-owned context failed")
    context = context_result.json_object()
    require(context.get("schema_version") == "production-session-context-v1", "context schema drift")
    require(context.get("server_owned") is True, "context is not marked server-owned")
    require(context.get("organization_kind") in {"personal", "managed"}, "invalid organization kind")
    require(isinstance(context.get("user_fingerprint"), str), "user fingerprint missing")
    require(isinstance(context.get("organization_fingerprint"), str), "organization fingerprint missing")
    require("email" not in json.dumps(context).lower(), "session context unexpectedly exposes email")

    return browser, session, context, cookie_policy


def assert_spoof_is_ignored(browser: BrowserSession, expected_context: dict[str, Any]) -> None:
    result = browser.request(
        "/api/session/context",
        headers={
            "X-Organization-Id": "attacker-org",
            "X-User-Id": "attacker-user",
            "X-Role": "admin",
            "X-Permissions": "runs:read:any,action_high,escalate",
        },
    )
    require(result.status == 200, "forged browser headers changed authentication status")
    require(result.json_object() == expected_context, "browser headers altered trusted runtime context")


def assert_other_tenant_run_hidden(browser: BrowserSession) -> None:
    paths = [
        f"/api/runs/{CROSS_TENANT_RUN_ID}",
        f"/api/runs/{CROSS_TENANT_RUN_ID}/events",
        f"/api/runs/{CROSS_TENANT_RUN_ID}/evidence",
        f"/api/runs/{CROSS_TENANT_RUN_ID}/evaluation",
        f"/api/runs/{CROSS_TENANT_RUN_ID}/lineage",
        f"/api/runs/{CROSS_TENANT_RUN_ID}/actions",
        f"/api/stream?run_id={CROSS_TENANT_RUN_ID}&follow=false",
    ]
    for path in paths:
        result = browser.request(path)
        require(result.status == 404, f"cross-tenant path {path} returned HTTP {result.status}, expected 404")
        require(error_detail(result) in {"run_not_found", None}, f"cross-tenant path {path} leaked detail")

    listing = browser.request("/api/runs?limit=100")
    require(listing.status == 200, "tenant-scoped run listing failed")
    require(CROSS_TENANT_RUN_ID not in listing.body.decode("utf-8", errors="replace"), "cross-tenant run leaked in list")


def assert_provider_remains_fail_closed(browser: BrowserSession) -> None:
    result = browser.request(
        "/api/runs",
        method="POST",
        payload={"user_request": "G3 IAM boundary probe; provider execution must remain disabled."},
    )
    require(result.status == 503, f"provider kill switch probe returned HTTP {result.status}")
    require(error_detail(result) == "provider_kill_switch_engaged", "provider kill switch was not authoritative")


def assert_anonymous_and_tampered_fail_closed(cookie_name: str) -> None:
    anonymous = BrowserSession()
    result = anonymous.request("/api/session/context")
    require(result.status == 401, f"anonymous context returned HTTP {result.status}")

    request = Request(
        f"{BASE_URL}/api/session/context",
        headers={
            "Accept": "application/json",
            "User-Agent": "academy-tractian-hosted-g3-iam/1",
            "Cookie": f"{cookie_name}=tampered-{uuid4().hex}",
        },
        method="GET",
    )
    try:
        with build_opener().open(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed product HTTPS origin
            status = int(response.status)
    except HTTPError as exc:
        status = int(exc.code)
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("tampered-cookie probe unavailable") from exc
    require(status == 401, f"tampered cookie returned HTTP {status}")


def assert_bad_origin_rejected(browser: BrowserSession) -> int:
    # Send the same JSON media type/body as the valid sign-out below so this probe reaches
    # Better Auth's Origin/CSRF boundary instead of being rejected earlier as a simple request.
    result = browser.request(
        "/auth/sign-out",
        method="POST",
        payload={},
        headers={"Origin": "https://attacker.invalid"},
    )
    require(result.status in {400, 401, 403}, f"malicious Origin was accepted with HTTP {result.status}")
    return result.status


def sign_out_and_require_invalidation(browser: BrowserSession) -> None:
    result = browser.request(
        "/auth/sign-out",
        method="POST",
        payload={},
        headers={"Origin": BASE_URL},
    )
    require(result.status in {200, 204}, f"valid sign-out failed with HTTP {result.status}")
    post = browser.request("/api/session/context")
    require(post.status == 401, f"signed-out session remained accepted with HTTP {post.status}")


def main() -> None:
    user_a, _session_a, context_a, cookie_policy_a = sign_up("A")
    user_b, _session_b, context_b, cookie_policy_b = sign_up("B")

    require(context_a["user_fingerprint"] != context_b["user_fingerprint"], "two users collapsed to one identity")
    require(
        context_a["organization_fingerprint"] != context_b["organization_fingerprint"],
        "two independent users unexpectedly share a tenant context",
    )

    assert_spoof_is_ignored(user_a, context_a)
    assert_spoof_is_ignored(user_b, context_b)
    assert_other_tenant_run_hidden(user_a)
    assert_other_tenant_run_hidden(user_b)
    assert_provider_remains_fail_closed(user_a)
    assert_provider_remains_fail_closed(user_b)

    cookie_names = user_a.cookie_names()
    require(len(cookie_names) >= 1, "managed cookie name unavailable for tamper probe")
    assert_anonymous_and_tampered_fail_closed(cookie_names[0])

    malicious_origin_status = assert_bad_origin_rejected(user_a)
    # A rejected malicious-origin sign-out must leave the valid session usable.
    require(user_a.request("/api/session/context").status == 200, "bad-origin rejection invalidated valid session")

    sign_out_and_require_invalidation(user_a)
    sign_out_and_require_invalidation(user_b)

    report = {
        "schema_version": "hosted-g3-iam-acceptance-v1",
        "status": "PASS",
        "users": 2,
        "distinct_user_fingerprints": True,
        "distinct_tenant_fingerprints": True,
        "browser_spoof_ignored": True,
        "cross_tenant_rest_sse_hidden": True,
        "anonymous_rejected": True,
        "tampered_cookie_rejected": True,
        "malicious_origin_rejected": True,
        "malicious_origin_status": malicious_origin_status,
        "sign_out_invalidation": True,
        "provider_kill_switch_preserved": True,
        "cookie_policy": {
            "user_a": cookie_policy_a,
            "user_b": cookie_policy_b,
        },
        "raw_user_ids_printed": False,
        "raw_organization_ids_printed": False,
        "emails_printed": False,
        "cookies_printed": False,
        "passwords_printed": False,
    }
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
