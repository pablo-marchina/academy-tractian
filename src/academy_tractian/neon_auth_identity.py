from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
import hashlib
import json
from threading import Lock
from time import monotonic
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request as UrlRequest, build_opener

from fastapi import HTTPException, Request, status

from .product_api import AuthenticatedRuntimeContext, DEFAULT_RUNTIME_PERMISSIONS


_MAX_COOKIE_BYTES = 16 * 1024
_MAX_SESSION_RESPONSE_BYTES = 64 * 1024
_MAX_ID_BYTES = 256
_DEFAULT_TIMEOUT_SECONDS = 5.0
_READ_SESSION_CACHE_TTL_SECONDS = 2.0
_MAX_READ_SESSION_CACHE_ENTRIES = 256
_SESSION_SINGLEFLIGHT_STRIPES = 64


SessionFetcher = Callable[[str], tuple[int, bytes]]
Clock = Callable[[], float]


class _NoAuthRedirectHandler(HTTPRedirectHandler):
    """Never forward a managed-session cookie across an HTTP redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201
        return None


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


def _validated_managed_id(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"invalid {label}")
    encoded = value.encode("utf-8")
    if len(encoded) > _MAX_ID_BYTES:
        raise ValueError(f"invalid {label}")
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in value):
        raise ValueError(f"invalid {label}")
    return value


class NeonAuthRuntimeContextProvider:
    """Resolve a browser session through the managed Neon Auth server boundary.

    The browser supplies only the opaque cookie created by the managed auth service. Tenant,
    identity, role and permissions are never accepted from request headers or JSON payloads.

    Read-only request bursts are coalesced behind a bounded two-second server cache keyed by a
    one-way digest of the opaque cookie. This is deliberately much shorter than a normal session
    cache: it exists only to prevent dashboard fan-out from turning every GET/SSE into a separate
    managed-auth network validation. Non-read requests always bypass this cache and force a fresh
    managed-session validation. Expired cache entries are never used as stale-on-error fallback.

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
        clock: Clock = monotonic,
    ) -> None:
        if not 0.5 <= timeout_seconds <= 30.0:
            raise ValueError("Neon Auth timeout must be between 0.5 and 30 seconds")
        self._base_url = _validated_auth_base_url(base_url)
        self._timeout_seconds = timeout_seconds
        self._fetch_session_override = fetch_session
        self._clock = clock
        self._cache_lock = Lock()
        self._read_session_cache: OrderedDict[
            str,
            tuple[float, AuthenticatedRuntimeContext],
        ] = OrderedDict()
        self._singleflight_locks = tuple(Lock() for _ in range(_SESSION_SINGLEFLIGHT_STRIPES))

    @staticmethod
    def _unauthorized(detail: str = "managed_session_invalid") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    @staticmethod
    def _unavailable() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="managed_session_unavailable",
            headers={"Retry-After": "1"},
        )

    def _cookie(self, request: Request) -> str:
        values = request.headers.getlist("cookie")
        if len(values) != 1:
            raise self._unauthorized("managed_session_required")
        cookie = values[0]
        if not cookie.strip() or len(cookie.encode("utf-8")) > _MAX_COOKIE_BYTES:
            raise self._unauthorized("managed_session_required")
        return cookie

    @staticmethod
    def _cache_key(cookie: str) -> str:
        return hashlib.sha256(cookie.encode("utf-8")).hexdigest()

    def _cached_context(self, cache_key: str) -> AuthenticatedRuntimeContext | None:
        now = self._clock()
        with self._cache_lock:
            cached = self._read_session_cache.get(cache_key)
            if cached is None:
                return None
            expires_at, context = cached
            if expires_at <= now:
                self._read_session_cache.pop(cache_key, None)
                return None
            self._read_session_cache.move_to_end(cache_key)
            return context

    def _cache_context(self, cache_key: str, context: AuthenticatedRuntimeContext) -> None:
        expires_at = self._clock() + _READ_SESSION_CACHE_TTL_SECONDS
        with self._cache_lock:
            self._read_session_cache[cache_key] = (expires_at, context)
            self._read_session_cache.move_to_end(cache_key)
            while len(self._read_session_cache) > _MAX_READ_SESSION_CACHE_ENTRIES:
                self._read_session_cache.popitem(last=False)

    def _invalidate_cached_context(self, cache_key: str) -> None:
        with self._cache_lock:
            self._read_session_cache.pop(cache_key, None)

    def _singleflight_lock(self, cache_key: str) -> Lock:
        stripe = int(cache_key[:8], 16) % len(self._singleflight_locks)
        return self._singleflight_locks[stripe]

    def _network_fetch(self, cookie: str, *, force_fresh: bool = True) -> tuple[int, bytes]:
        suffix = "?disableCookieCache=true" if force_fresh else ""
        url = f"{self._base_url}/get-session{suffix}"
        request = UrlRequest(
            url,
            headers={
                "Accept": "application/json",
                "Cookie": cookie,
                "User-Agent": "academy-tractian-production/1",
            },
            method="GET",
        )
        opener = build_opener(_NoAuthRedirectHandler())
        try:
            with opener.open(request, timeout=self._timeout_seconds) as response:  # noqa: S310 - URL is validated HTTPS config and redirects are disabled
                raw = response.read(_MAX_SESSION_RESPONSE_BYTES + 1)
                return int(response.status), raw
        except HTTPError as exc:
            raw = exc.read(_MAX_SESSION_RESPONSE_BYTES + 1)
            return int(exc.code), raw
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError("managed_session_service_unavailable") from exc

    def _fetch(self, cookie: str, *, force_fresh: bool) -> tuple[int, bytes]:
        if self._fetch_session_override is not None:
            return self._fetch_session_override(cookie)
        return self._network_fetch(cookie, force_fresh=force_fresh)

    def _validated_context(self, *, cookie: str, cache_key: str, force_fresh: bool) -> AuthenticatedRuntimeContext:
        try:
            response_status, raw = self._fetch(cookie, force_fresh=force_fresh)
        except RuntimeError as exc:
            raise self._unavailable() from exc

        if response_status in {401, 403}:
            self._invalidate_cached_context(cache_key)
            raise self._unauthorized("managed_session_invalid")
        if response_status != 200:
            raise self._unavailable()

        try:
            payload = _bounded_json_object(raw)
            user = payload.get("user")
            session = payload.get("session")
            if not isinstance(user, dict) or not isinstance(session, dict):
                raise ValueError("session/user missing")

            user_id = _validated_managed_id(user.get("id"), label="managed user id")
            session_user_id = _validated_managed_id(
                session.get("userId"),
                label="managed session user id",
            )
            if session_user_id != user_id:
                raise ValueError("session user mismatch")
            if session.get("impersonatedBy") not in {None, ""}:
                raise ValueError("impersonated sessions are not eligible for production runtime")

            active_organization = session.get("activeOrganizationId")
            if active_organization in {None, ""}:
                organization_id = f"user:{user_id}"
            else:
                organization_id = _validated_managed_id(
                    active_organization,
                    label="managed active organization id",
                )
        except (TypeError, ValueError, KeyError) as exc:
            self._invalidate_cached_context(cache_key)
            raise self._unauthorized("managed_session_invalid") from exc

        return AuthenticatedRuntimeContext(
            organization_id=organization_id,
            identity_id=f"neon-auth:{user_id}",
            user_id=user_id,
            role="operator",
            permissions=DEFAULT_RUNTIME_PERMISSIONS,
            seed=None,
        )

    def __call__(self, request: Request) -> AuthenticatedRuntimeContext:
        cookie = self._cookie(request)
        cache_key = self._cache_key(cookie)
        read_only = request.method.upper() in {"GET", "HEAD"}

        if not read_only:
            return self._validated_context(
                cookie=cookie,
                cache_key=cache_key,
                force_fresh=True,
            )

        cached = self._cached_context(cache_key)
        if cached is not None:
            return cached

        # Collapse concurrent misses for the same digest stripe. Re-check after taking the lock so
        # one successful validation can satisfy the rest of the burst without another network call.
        with self._singleflight_lock(cache_key):
            cached = self._cached_context(cache_key)
            if cached is not None:
                return cached
            context = self._validated_context(
                cookie=cookie,
                cache_key=cache_key,
                force_fresh=False,
            )
            self._cache_context(cache_key, context)
            return context
