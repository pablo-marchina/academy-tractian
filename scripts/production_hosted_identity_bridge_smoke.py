from __future__ import annotations

import http.cookiejar
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener
from uuid import uuid4


BASE_URL = os.environ.get(
    "ACADEMY_PRODUCTION_WEB_BASE_URL",
    "https://production-web-production-c9d1.up.railway.app",
).rstrip("/")
TIMEOUT_SECONDS = 25
RUN_WAIT_SECONDS = 150


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
    ) -> tuple[int, bytes]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{BASE_URL}{path}",
            data=body,
            headers={
                "Accept": "application/json",
                "User-Agent": "academy-tractian-identity-bridge-smoke/1",
                **({"Content-Type": "application/json"} if body is not None else {}),
                **(headers or {}),
            },
            method=method,
        )
        try:
            with self.opener.open(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed production HTTPS origin
                return int(response.status), response.read()
        except HTTPError as exc:
            return int(exc.code), exc.read()
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"production request unavailable for {path}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def json_object(body: bytes) -> dict[str, Any]:
    payload = json.loads(body.decode("utf-8")) if body else {}
    require(isinstance(payload, dict), "expected JSON object")
    return payload


def sign_up() -> BrowserSession:
    browser = BrowserSession()
    status, _ = browser.request(
        "/auth/sign-up/email",
        method="POST",
        payload={
            "email": f"academy-identity-bridge-{uuid4().hex}@example.com",
            "password": f"IdentityBridge-{uuid4().hex}-Secure!",
            "name": "Identity bridge hosted acceptance",
        },
        headers={"Origin": BASE_URL},
    )
    require(status in {200, 201}, f"hosted sign-up failed with HTTP {status}")
    status, body = browser.request("/api/session/context")
    require(status == 200, f"managed session context failed with HTTP {status}")
    require(json_object(body).get("server_owned") is True, "session context is not server-owned")
    return browser


def wait_for_execution(browser: BrowserSession, path: str) -> str:
    deadline = time.monotonic() + RUN_WAIT_SECONDS
    while time.monotonic() < deadline:
        status, body = browser.request(path)
        require(status == 200, f"execution status failed with HTTP {status}")
        state = json_object(body).get("status")
        if state in {"completed", "failed"}:
            return str(state)
        time.sleep(1.5)
    raise RuntimeError("identity bridge smoke did not reach a terminal execution state")


def safe_items(browser: BrowserSession, path: str) -> list[dict[str, Any]]:
    status, body = browser.request(path)
    require(status == 200, f"{path} failed with HTTP {status}")
    items = json_object(body).get("items")
    require(isinstance(items, list), f"{path} did not return items")
    require(all(isinstance(item, dict) for item in items), f"{path} returned an invalid item")
    return items


def main() -> None:
    browser = sign_up()
    prompt = (
        "Identify the current TRACTIAN user for this signed-in session. "
        "You must call get_current_user exactly once before answering. "
        "Do not call any other tool and do not propose or execute actions. "
        "If the current TRACTIAN user cannot be read, abstain without retrying."
    )
    status, body = browser.request("/api/runs", method="POST", payload={"user_request": prompt})
    require(status == 202, f"identity bridge run was not accepted: HTTP {status}")
    accepted = json_object(body)
    run_id = accepted.get("run_id")
    execution_path = accepted.get("execution_path")
    require(isinstance(run_id, str) and run_id, "accepted run_id missing")
    require(isinstance(execution_path, str) and execution_path, "execution_path missing")

    state = wait_for_execution(browser, execution_path)
    require(state == "completed", f"identity bridge execution ended as {state}")
    events = safe_items(browser, f"/api/runs/{run_id}/events")

    calls = [
        item
        for item in events
        if item.get("event_type") == "tool_call" and item.get("tool_name") == "get_current_user"
    ]
    results = [
        item
        for item in events
        if item.get("event_type") == "tool_result" and item.get("tool_name") == "get_current_user"
    ]
    other_calls = [
        item
        for item in events
        if item.get("event_type") == "tool_call" and item.get("tool_name") != "get_current_user"
    ]

    require(len(calls) == 1, f"get_current_user call count drift: {len(calls)}")
    require(len(results) == 1, f"get_current_user result count drift: {len(results)}")
    require(not other_calls, "identity bridge smoke called an unrelated tool")
    status_code = results[0].get("status_code")
    require(isinstance(status_code, int) and 200 <= status_code < 300, f"get_current_user returned HTTP {status_code}")

    status, _ = browser.request("/auth/sign-out", method="POST", payload={}, headers={"Origin": BASE_URL})
    require(status in {200, 204}, f"sign-out failed with HTTP {status}")

    print(
        json.dumps(
            {
                "schema_version": "hosted-tractian-identity-bridge-smoke-v1",
                "status": "PASS",
                "run_id": run_id,
                "get_current_user_calls": 1,
                "http_status": status_code,
                "cross_identity_translation": "server-side",
                "raw_domain_identity_recorded": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
