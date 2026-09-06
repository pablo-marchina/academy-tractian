from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4


PUBLIC_BASE_URL = os.environ.get(
    "ACADEMY_PRODUCTION_WEB_BASE_URL",
    "https://production-web-production-c9d1.up.railway.app",
).rstrip("/")
DIRECT_AUTH_BASE_URL = os.environ.get(
    "ACADEMY_NEON_AUTH_DIAGNOSTIC_BASE_URL",
    "https://ep-falling-leaf-acbmndwc.neonauth.sa-east-1.aws.neon.tech/academy_tractian/auth",
).rstrip("/")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201
        return None


def safe_location(value: str | None) -> dict[str, object] | None:
    if not value:
        return None
    parsed = urlsplit(value)
    return {
        "scheme": parsed.scheme or None,
        "host": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path,
        "query_present": bool(parsed.query),
        "fragment_present": bool(parsed.fragment),
    }


def probe(url: str, *, method: str = "GET", payload: bytes | None = None, origin: str | None = None) -> dict[str, object]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "academy-tractian-hosted-g3-redirect-probe/2",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if origin is not None:
        headers["Origin"] = origin
    request = Request(url, data=payload, method=method, headers=headers)
    try:
        with build_opener(NoRedirect()).open(request, timeout=20) as response:  # noqa: S310 - fixed production/Neon HTTPS origins
            status = int(response.status)
            location = response.headers.get("Location")
    except HTTPError as exc:
        status = int(exc.code)
        location = exc.headers.get("Location")
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("hosted auth canonicalization probe unavailable") from exc
    return {"status": status, "location": safe_location(location)}


def main() -> None:
    session_suffix = "/get-session?disableCookieCache=true"
    public_session = probe(f"{PUBLIC_BASE_URL}/auth{session_suffix}")
    direct_session = probe(f"{DIRECT_AUTH_BASE_URL}{session_suffix}")

    payload = json.dumps(
        {
            "email": f"academy-g3-redirect-{uuid4().hex}@example.com",
            "password": f"G3-{uuid4().hex}-Secure!",
            "name": "G3 Redirect Probe",
        }
    ).encode("utf-8")
    public_signup = probe(
        f"{PUBLIC_BASE_URL}/auth/sign-up/email",
        method="POST",
        payload=payload,
        origin=PUBLIC_BASE_URL,
    )

    print(
        json.dumps(
            {
                "schema_version": "hosted-g3-auth-canonicalization-probe-v2",
                "public_session_get": public_session,
                "direct_neon_session_get": direct_session,
                "public_signup_post": public_signup,
                "credentials_printed": False,
                "cookies_printed": False,
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
