from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4


BASE_URL = os.environ.get(
    "ACADEMY_PRODUCTION_WEB_BASE_URL",
    "https://production-web-production-c9d1.up.railway.app",
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


def main() -> None:
    payload = json.dumps(
        {
            "email": f"academy-g3-redirect-{uuid4().hex}@example.com",
            "password": f"G3-{uuid4().hex}-Secure!",
            "name": "G3 Redirect Probe",
        }
    ).encode("utf-8")
    request = Request(
        f"{BASE_URL}/auth/sign-up/email",
        data=payload,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "User-Agent": "academy-tractian-hosted-g3-redirect-probe/1",
        },
    )
    try:
        with build_opener(NoRedirect()).open(request, timeout=20) as response:  # noqa: S310
            status = int(response.status)
            location = response.headers.get("Location")
    except HTTPError as exc:
        status = int(exc.code)
        location = exc.headers.get("Location")
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("hosted auth redirect probe unavailable") from exc

    print(
        json.dumps(
            {
                "schema_version": "hosted-g3-auth-redirect-probe-v1",
                "status": status,
                "location": safe_location(location),
                "credentials_printed": False,
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
