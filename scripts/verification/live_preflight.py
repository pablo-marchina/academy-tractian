from __future__ import annotations

import http.cookiejar
import json
import os
import urllib.error
import urllib.request


def origin(name: str) -> str:
    value = os.environ.get(name, "").strip().rstrip("/")
    if not value:
        raise RuntimeError(f"missing_{name.lower()}")
    return value


def request(opener, url: str, *, method: str = "GET", body: dict | None = None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data else {})},
    )
    try:
        with opener.open(req, timeout=20) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        return exc.code, None


def main() -> int:
    product = origin("TARGET_BASE_URL")
    api = os.environ.get("TARGET_API_BASE_URL", "").strip().rstrip("/") or product
    expected = os.environ.get("EXPECTED_RELEASE_SHA", "").strip()
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    release_status, payload = request(opener, f"{api}/api/release0/capabilities")
    release = payload.get("release") if isinstance(payload, dict) else None
    actual = release.get("git_sha") if isinstance(release, dict) else None
    release_match = bool(expected and actual == expected)
    print(json.dumps({"phase": "release", "http_status": release_status, "expected_present": bool(expected), "sha_match": release_match}, sort_keys=True))

    email = os.environ.get("QA_EMAIL", "").strip().lower()
    password = os.environ.get("QA_PASSWORD", "")
    auth_status, _ = request(opener, f"{product}/auth/sign-in/email", method="POST", body={"email": email, "password": password, "rememberMe": True})
    session_status, session = request(opener, f"{product}/auth/get-session?disableCookieCache=true") if auth_status == 200 else (0, None)
    session_valid = isinstance(session, dict) and isinstance(session.get("user"), dict)
    print(json.dumps({"phase": "auth", "signin_status": auth_status, "session_status": session_status, "session_valid": session_valid, "credentials_recorded": False}, sort_keys=True))
    return 0 if release_status == 200 and release_match and auth_status == 200 and session_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
