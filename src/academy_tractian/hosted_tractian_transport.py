from __future__ import annotations

import json
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse


class HostedTractianTransport:
    """One-shot HTTPS transport for the supplied hosted TRACTIAN API.

    No retry or fallback is hidden here. Non-2xx responses are returned to the existing runtime
    boundary as observations so the controller/evaluator can contain failures explicitly.
    Credentials are constructor-owned and redacted from repr.
    """

    def __init__(
        self,
        *,
        base_url: str,
        bearer_token: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("hosted TRACTIAN transport requires an absolute HTTPS base URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("hosted TRACTIAN base URL contains forbidden components")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._base_url = base_url.rstrip("/")
        self._bearer_token = None if bearer_token is None else bearer_token.strip() or None
        self._timeout_seconds = float(timeout_seconds)

    def __repr__(self) -> str:
        return (
            f"HostedTractianTransport(base_url={self._base_url!r}, "
            "bearer_token=<redacted>, timeout_seconds="
            f"{self._timeout_seconds!r})"
        )

    def _url(self, request: BoundRequest) -> str:
        path = request.path if request.path.startswith("/") else f"/{request.path}"
        query = urllib.parse.urlencode(request.query, doseq=True)
        url = f"{self._base_url}{path}"
        return url if not query else f"{url}?{query}"

    def request(self, request: BoundRequest) -> TransportResponse:
        headers = {str(key): str(value) for key, value in request.headers.items()}
        headers.setdefault("Accept", "application/json")
        if self._bearer_token is not None:
            headers["Authorization"] = f"Bearer {self._bearer_token}"

        data: bytes | None = None
        if request.body is not None:
            data = json.dumps(
                request.body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

        raw_request = urllib.request.Request(
            self._url(request),
            data=data,
            headers=headers,
            method=request.method,
        )
        try:
            with urllib.request.urlopen(raw_request, timeout=self._timeout_seconds) as response:
                status_code = int(response.status)
                response_headers = dict(response.headers.items())
                raw_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            status_code = int(exc.code)
            response_headers = dict(exc.headers.items()) if exc.headers is not None else {}
            raw_body = exc.read().decode("utf-8") if exc.fp is not None else ""
        except Exception as exc:
            raise RuntimeError("tractian_transport_failure") from exc

        body: Any
        if not raw_body:
            body = None
        else:
            try:
                body = json.loads(raw_body)
            except ValueError:
                body = raw_body
        return TransportResponse(
            status_code=status_code,
            headers=response_headers,
            body=body,
        )
