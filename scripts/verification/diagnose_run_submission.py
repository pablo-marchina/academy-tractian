from __future__ import annotations

import http.cookiejar
import json
import os
import urllib.error
import urllib.request


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing_{name.lower()}")
    return value.rstrip("/") if name.endswith("BASE_URL") else value


def request(opener, url: str, *, method: str = "GET", body: dict | None = None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data else {})},
    )
    try:
        with opener.open(req, timeout=30) as resp:
            raw = resp.read()
            return int(resp.status), json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw) if raw else None
        except Exception:
            payload = None
        return int(exc.code), payload


def safe_detail(payload):
    if not isinstance(payload, dict):
        return None
    detail = payload.get("detail")
    if isinstance(detail, str) and len(detail) <= 128:
        return detail
    return None


def main() -> int:
    product = required("TARGET_BASE_URL")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    email = required("QA_EMAIL").lower()
    password = required("QA_PASSWORD")

    signin_status, _ = request(
        opener,
        f"{product}/auth/sign-in/email",
        method="POST",
        body={"email": email, "password": password, "rememberMe": True},
    )
    session_status, session = request(opener, f"{product}/auth/get-session?disableCookieCache=true")
    submission_status, submission = request(
        opener,
        f"{product}/api/runs",
        method="POST",
        body={"user_request": "For asset R310, explain its current condition and what evidence supports that conclusion."},
    )
    print(json.dumps({
        "schema_version": "run-submission-diagnostic-v1",
        "signin_status": signin_status,
        "session_status": session_status,
        "session_valid": isinstance(session, dict) and isinstance(session.get("user"), dict),
        "submission_status": submission_status,
        "submission_detail": safe_detail(submission),
        "credentials_recorded": False,
        "cookie_recorded": False,
        "response_body_recorded": False,
    }, sort_keys=True))
    return 0 if submission_status == 202 else 1


if __name__ == "__main__":
    raise SystemExit(main())
