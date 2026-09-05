from __future__ import annotations

from collections.abc import Callable
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request as UrlRequest, urlopen

from fastapi import HTTPException, Request, status

from .product_api import AuthenticatedRuntimeContext, DEFAULT_RUNTIME_PERMISSIONS


_MAX_COOKIE_BYTES = 16 * 1024
_MAX_SESSION_RESPONSE_BYTES = 64 * 1024
_DEFAULT_TIMEOUT_SECONDS = 5.0


SessionFetcher = Callable[[str], tuple[int, bytes]]


def _validated_auth_base_url(value: str) -> str:
    normalized = value.strip().rstrip("/")
    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or parsed.hostname is None:
        raise ValueError("Neon Auth base URL must be a remote HTTPS URL")
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError("Neon Auth base URL must not contain credentials, query or fragment")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".localhost"):
        raise ValueError("Neon Auth base URL must not be local")
    return normalized


def _bounded_json_object(raw: bytes) -> dict[str, Any]:
    if not raw or len(raw) > _MAX_SESSION_RESPONSE_BYTES:
        raise ValueError("invalid Neon Auth session response size")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid Neon Auth session JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("invalid Neon Auth session payload")
    return value


class NeonAuthRuntimeContextProvider:
    """Resolve a browser session through the managed Neon Auth server boundary.

    The browser supplies only the opaque cookie created by the managed auth service. Tenant,
    identity, role and permissions are never accepted from request headers or JSON payloads.
    A valid managed session is revalidated with cookie-cache bypass before each API/SSE request.

    Until shared-organization onboarding is exposed in the product, an authenticated user with no
    active organization receives a deterministic personal tenant derived from the server-verified
    user id. If Neon Auth has an active organization, its server-side session value becomes the
    tenant id instead. Both paths remain browser-non-authoritative.
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
        fetch_session: SessionFetcher | None = None,
    ) -> None:
        if not 0.5 <= timeout_seconds <= 30.0:
            raise ValueError("Neon Auth timeout must be between 0.5 and 30 seconds")
        self._base_url = _validated_auth_base_url(base_url)
        self._timeout_seconds = timeout_seconds
        self._fetch_session_override = fetch_session

    @staticmethod
    def _unauthorized(detail: str = "managed_session_invalid") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    def _cookie(self, request: Request) -> str:
        values = request.headers.getlist("cookie")
        if len(values) != 1:
            raise self._unauthorized("managed_session_required")
        cookie = values[0]
        if not cookie.strip() or len(cookie.encode("utf-8")) > _MAX_COOKIE_BYTES:
            raise self._unauthorized("managed_session_required")
        return cookie

    def _network_fetch(self, cookie: str) -> tuple[int, bytes]:
        url = f"{self._base_url}/get-session?disableCookieCache=true"
        request = UrlRequest(
            url,
            headers={
                "Accept": "application/json",
                "Cookie": cookie,
                "User-Agent": "academy-tractian-production/1",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:  # noqa: S310 - URL is validated HTTPS config
                raw = response.read(_MAX_SESSION_RESPONSE_BYTES + 1)
                return int(response.status), raw
        except HTTPError as exc:
            raw = exc.read(_MAX_SESSION_RESPONSE_BYTES + 1)
            return int(exc.code), raw
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError("managed_session_service_unavailable") from exc

    def _fetch(self, cookie: str) -> tuple[int, bytes]:
        if self._fetch_session_override is not None:
            return self._fetch_session_override(cookie)
        return self._network_fetch(cookie)

    def __call__(self, request: Request) -> AuthenticatedRuntimeContext:
        cookie = self._cookie(request)
        try:
            response_status, raw = self._fetch(cookie)
        except RuntimeError as exc:
            raise self._unauthorized("managed_session_unavailable") from exc

        if response_status in {401, 403}:
            raise self._unauthorized("managed_session_invalid")
        if response_status != 200:
            raise self._unauthorized("managed_session_unavailable")

        try:
            payload = _bounded_json_object(raw)
            user = payload.get("user")
            session = payload.get("session")
            if not isinstance(user, dict) or not isinstance(session, dict):
                raise ValueError("session/user missing")

            user_id = user.get("id")
            session_user_id = session.get("userId")
            if not isinstance(user_id, str) or not user_id.strip() or session_user_id != user_id:
                raise ValueError("session user mismatch")
            if session.get("impersonatedBy") not in {None, ""}:
                raise ValueError("impersonated sessions are not eligible for production runtime")

            active_organization = session.get("activeOrganizationId")
            if active_organization is not None and not isinstance(active_organization, str):
                raise ValueError("invalid active organization")
            organization_id = (
                active_organization.strip()
                if isinstance(active_organization, str) and active_organization.strip()
                else f"user:{user_id}"
            )
        except (TypeError, ValueError, KeyError) as exc:
            raise self._unauthorized("managed_session_invalid") from exc

        return AuthenticatedRuntimeContext(
            organization_id=organization_id,
            identity_id=f"neon-auth:{user_id}",
            user_id=user_id,
            role="operator",
            permissions=DEFAULT_RUNTIME_PERMISSIONS,
            seed=None,
        )
