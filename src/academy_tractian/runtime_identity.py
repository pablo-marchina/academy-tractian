from __future__ import annotations

import base64
import binascii
from collections.abc import Callable, Iterable
from hashlib import sha256
import hmac
import json
import re
from time import time
from typing import Literal

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .product_api import AuthenticatedRuntimeContext


_TOKEN_PREFIX = "academy-runtime-v1"
_TOKEN_SEGMENT = re.compile(r"^[A-Za-z0-9_-]+$")
_MIN_SECRET_BYTES = 32
_MAX_TOKEN_BYTES = 8192
PRIVILEGED_RUNTIME_PERMISSIONS = frozenset({"runs:read:any", "analytics:read:global"})


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SignedRuntimeIdentityClaims(_FrozenModel):
    """Claims signed by a trusted identity issuer outside the request body.

    `seed` is intentionally absent: benchmark/replay seeds are not an authenticated production
    identity claim and must never be supplied by a browser token.
    """

    schema_version: Literal["runtime-identity-v1"] = "runtime-identity-v1"
    issuer: str = Field(min_length=1, max_length=256)
    audience: str = Field(min_length=1, max_length=256)
    token_id: str = Field(min_length=8, max_length=256)
    identity_id: str = Field(min_length=1, max_length=256)
    user_id: str = Field(min_length=1, max_length=256)
    organization_id: str = Field(min_length=1, max_length=256)
    role: str = Field(default="operator", min_length=1, max_length=64)
    permissions: tuple[str, ...] = Field(default_factory=tuple, max_length=64)
    issued_at: int = Field(ge=0)
    expires_at: int = Field(ge=1)

    @field_validator(
        "issuer",
        "audience",
        "token_id",
        "identity_id",
        "user_id",
        "organization_id",
        "role",
    )
    @classmethod
    def reject_surrounding_whitespace(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("identity claim cannot contain surrounding whitespace")
        return value

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, permissions: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(permissions)) != len(permissions):
            raise ValueError("identity permissions must be unique")
        for permission in permissions:
            if not permission or permission != permission.strip() or len(permission) > 128:
                raise ValueError("identity permission is invalid")
        return permissions

    @model_validator(mode="after")
    def validate_lifetime_order(self) -> "SignedRuntimeIdentityClaims":
        if self.expires_at <= self.issued_at:
            raise ValueError("identity token expires_at must be after issued_at")
        return self


def _secret_bytes(secret: bytes | str) -> bytes:
    value = secret.encode("utf-8") if isinstance(secret, str) else bytes(secret)
    if len(value) < _MIN_SECRET_BYTES:
        raise ValueError("runtime identity signing secret must contain at least 32 bytes")
    return value


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str, *, label: str) -> bytes:
    if not value or not _TOKEN_SEGMENT.fullmatch(value):
        raise ValueError(f"invalid {label} encoding")
    padded = value + "=" * (-len(value) % 4)
    try:
        decoded = base64.b64decode(padded, altchars=b"-_", validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"invalid {label} encoding") from exc
    if _b64url_encode(decoded) != value:
        raise ValueError(f"non-canonical {label} encoding")
    return decoded


def _strict_json_object(raw: bytes) -> dict[str, object]:
    def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON claim: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid runtime identity JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("runtime identity payload must be a JSON object")
    return value


def _canonical_claim_bytes(claims: SignedRuntimeIdentityClaims) -> bytes:
    return json.dumps(
        claims.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def issue_signed_runtime_token(
    *,
    secret: bytes | str,
    claims: SignedRuntimeIdentityClaims,
) -> str:
    """Trusted issuer helper used by deployment tooling/tests, never by the browser API."""

    key = _secret_bytes(secret)
    encoded_payload = _b64url_encode(_canonical_claim_bytes(claims))
    signing_input = f"{_TOKEN_PREFIX}.{encoded_payload}".encode("ascii")
    signature = hmac.new(key, signing_input, sha256).digest()
    return f"{_TOKEN_PREFIX}.{encoded_payload}.{_b64url_encode(signature)}"


class SignedBearerRuntimeContextProvider:
    """Verify a signed bearer identity envelope and produce trusted runtime context.

    The provider deliberately has no fallback to user/tenant headers. Normal requests must carry
    one valid bearer token. Cross-tenant/global permissions are opt-in at server configuration,
    never inferred from a role name supplied by the token.
    """

    def __init__(
        self,
        *,
        secret: bytes | str,
        issuer: str,
        audience: str,
        max_ttl_seconds: int = 3600,
        clock_skew_seconds: int = 30,
        allowed_privileged_permissions: Iterable[str] = (),
        now: Callable[[], float] = time,
    ) -> None:
        if not issuer or issuer != issuer.strip():
            raise ValueError("runtime identity issuer must be non-empty and trimmed")
        if not audience or audience != audience.strip():
            raise ValueError("runtime identity audience must be non-empty and trimmed")
        if not 60 <= max_ttl_seconds <= 86400:
            raise ValueError("runtime identity max_ttl_seconds must be between 60 and 86400")
        if not 0 <= clock_skew_seconds <= 300:
            raise ValueError("runtime identity clock_skew_seconds must be between 0 and 300")
        privileged = frozenset(allowed_privileged_permissions)
        if not privileged.issubset(PRIVILEGED_RUNTIME_PERMISSIONS):
            raise ValueError("unknown privileged runtime permission configured")
        self._secret = _secret_bytes(secret)
        self._issuer = issuer
        self._audience = audience
        self._max_ttl_seconds = max_ttl_seconds
        self._clock_skew_seconds = clock_skew_seconds
        self._allowed_privileged_permissions = privileged
        self._now = now

    @staticmethod
    def _unauthorized(detail: str = "invalid_runtime_identity") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _extract_token(self, request: Request) -> str:
        values = request.headers.getlist("authorization")
        if len(values) != 1:
            raise self._unauthorized("runtime_identity_bearer_required")
        authorization = values[0]
        if len(authorization.encode("utf-8")) > _MAX_TOKEN_BYTES + 16:
            raise self._unauthorized()
        scheme, separator, token = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not token or " " in token:
            raise self._unauthorized("runtime_identity_bearer_required")
        if len(token.encode("ascii", errors="ignore")) != len(token) or len(token) > _MAX_TOKEN_BYTES:
            raise self._unauthorized()
        return token

    def _verify(self, token: str) -> SignedRuntimeIdentityClaims:
        parts = token.split(".")
        if len(parts) != 3 or parts[0] != _TOKEN_PREFIX:
            raise self._unauthorized()
        encoded_payload, encoded_signature = parts[1], parts[2]
        try:
            signature = _b64url_decode(encoded_signature, label="signature")
        except ValueError as exc:
            raise self._unauthorized() from exc
        if len(signature) != sha256().digest_size:
            raise self._unauthorized()
        signing_input = f"{_TOKEN_PREFIX}.{encoded_payload}".encode("ascii", errors="strict")
        expected = hmac.new(self._secret, signing_input, sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise self._unauthorized()

        try:
            raw_payload = _b64url_decode(encoded_payload, label="payload")
            payload = _strict_json_object(raw_payload)
            claims = SignedRuntimeIdentityClaims.model_validate(payload)
            if raw_payload != _canonical_claim_bytes(claims):
                raise ValueError("runtime identity JSON is not canonical")
        except Exception as exc:
            raise self._unauthorized() from exc
        if claims.issuer != self._issuer or claims.audience != self._audience:
            raise self._unauthorized()

        now = int(self._now())
        if claims.issued_at > now + self._clock_skew_seconds:
            raise self._unauthorized()
        if claims.expires_at <= now - self._clock_skew_seconds:
            raise self._unauthorized("runtime_identity_expired")
        if claims.expires_at - claims.issued_at > self._max_ttl_seconds:
            raise self._unauthorized()

        privileged = set(claims.permissions) & PRIVILEGED_RUNTIME_PERMISSIONS
        if not privileged.issubset(self._allowed_privileged_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="runtime_identity_privilege_not_enabled",
            )
        return claims

    def __call__(self, request: Request) -> AuthenticatedRuntimeContext:
        claims = self._verify(self._extract_token(request))
        return AuthenticatedRuntimeContext(
            organization_id=claims.organization_id,
            identity_id=claims.identity_id,
            user_id=claims.user_id,
            role=claims.role,
            permissions=frozenset(claims.permissions),
            seed=None,
        )
