from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from time import time
from typing import Any, Protocol
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status
import jwt
from jwt import PyJWKClient

from .product_api import AuthenticatedRuntimeContext, DEFAULT_RUNTIME_PERMISSIONS
from .runtime_identity import PRIVILEGED_RUNTIME_PERMISSIONS


_MAX_TOKEN_BYTES = 16384
_ALLOWED_ASYMMETRIC_ALGORITHMS = frozenset(
    {"RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512", "EdDSA"}
)


class SigningKeyProvider(Protocol):
    def get_signing_key_from_jwt(self, token: str) -> Any: ...


def _trimmed(value: str, *, label: str, max_length: int = 512) -> str:
    if not value or value != value.strip() or len(value) > max_length:
        raise ValueError(f"invalid {label}")
    return value


def _https_url(value: str, *, label: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label} must be an absolute HTTPS URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f"{label} contains forbidden URL components")
    return value.rstrip("/")


def _claim_string(claims: Mapping[str, Any], name: str, *, required: bool = True) -> str | None:
    value = claims.get(name)
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        raise ValueError(f"invalid identity claim:{name}")
    return value


def _claim_permissions(value: Any) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, str):
        raw = tuple(item for item in value.split() if item)
    elif isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        raw = tuple(value)
    else:
        raise ValueError("invalid permission claim")
    if len(raw) > 64 or len(set(raw)) != len(raw):
        raise ValueError("invalid permission claim")
    for permission in raw:
        if not permission or permission != permission.strip() or len(permission) > 128:
            raise ValueError("invalid permission claim")
    return frozenset(raw)


@dataclass(frozen=True)
class OIDCClaimMapping:
    organization_claim: str = "organization_id"
    role_claim: str | None = "role"
    permissions_claim: str | None = "permissions"
    identity_claim: str | None = "sid"
    required_claims: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for label, value in (
            ("organization_claim", self.organization_claim),
            ("role_claim", self.role_claim),
            ("permissions_claim", self.permissions_claim),
            ("identity_claim", self.identity_claim),
        ):
            if value is not None:
                _trimmed(value, label=label, max_length=128)
        normalized_required = tuple(
            dict.fromkeys(_trimmed(value, label="required_claim", max_length=128) for value in self.required_claims)
        )
        object.__setattr__(self, "required_claims", normalized_required)


class OIDCRuntimeContextProvider:
    """Fail-closed OIDC/JWT resource-server boundary using asymmetric JWKS verification.

    Authentication is delegated to a hosted issuer while authorization remains application-owned:
    issuer/audience/algorithm are immutable configuration, tenant is mandatory, token permissions
    are intersected with a server allow-list, and privileged permissions need an additional
    explicit server allow-list. Browser-supplied tenant/role headers are never a fallback.
    """

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_url: str,
        algorithms: Iterable[str],
        claim_mapping: OIDCClaimMapping = OIDCClaimMapping(),
        base_permissions: Iterable[str] = DEFAULT_RUNTIME_PERMISSIONS,
        allowed_claim_permissions: Iterable[str] = (),
        allowed_privileged_permissions: Iterable[str] = (),
        authorized_parties: Iterable[str] = (),
        max_ttl_seconds: int = 3600,
        clock_skew_seconds: int = 30,
        signing_key_provider: SigningKeyProvider | None = None,
        now=time,
    ) -> None:
        self._issuer = _trimmed(issuer, label="OIDC issuer")
        self._audience = _trimmed(audience, label="OIDC audience")
        self._jwks_url = _https_url(jwks_url, label="OIDC JWKS URL")
        normalized_algorithms = tuple(dict.fromkeys(item.strip() for item in algorithms if item.strip()))
        if not normalized_algorithms:
            raise ValueError("OIDC algorithms must be configured explicitly")
        if not set(normalized_algorithms).issubset(_ALLOWED_ASYMMETRIC_ALGORITHMS):
            raise ValueError("OIDC algorithms must use supported asymmetric verification")
        self._algorithms = normalized_algorithms
        if not 60 <= max_ttl_seconds <= 86400:
            raise ValueError("OIDC max_ttl_seconds must be between 60 and 86400")
        if not 0 <= clock_skew_seconds <= 300:
            raise ValueError("OIDC clock_skew_seconds must be between 0 and 300")

        self._mapping = claim_mapping
        self._base_permissions = frozenset(base_permissions)
        self._allowed_claim_permissions = frozenset(allowed_claim_permissions)
        privileged = frozenset(allowed_privileged_permissions)
        if not privileged.issubset(PRIVILEGED_RUNTIME_PERMISSIONS):
            raise ValueError("unknown privileged runtime permission configured")
        if (self._allowed_claim_permissions & PRIVILEGED_RUNTIME_PERMISSIONS) - privileged:
            raise ValueError("privileged claim permission requires explicit privileged enablement")
        self._allowed_privileged_permissions = privileged
        self._authorized_parties = frozenset(
            _trimmed(item, label="authorized party", max_length=512) for item in authorized_parties
        )
        self._max_ttl_seconds = max_ttl_seconds
        self._clock_skew_seconds = clock_skew_seconds
        self._now = now
        self._key_provider = signing_key_provider or PyJWKClient(
            self._jwks_url,
            cache_keys=True,
            max_cached_keys=16,
            lifespan=300,
            timeout=5,
        )

    @staticmethod
    def _unauthorized(detail: str = "invalid_oidc_identity") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _extract_token(self, request: Request) -> str:
        values = request.headers.getlist("authorization")
        if len(values) != 1:
            raise self._unauthorized("oidc_bearer_required")
        authorization = values[0]
        scheme, separator, token = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not token or " " in token:
            raise self._unauthorized("oidc_bearer_required")
        try:
            token_bytes = token.encode("ascii")
        except UnicodeEncodeError as exc:
            raise self._unauthorized() from exc
        if len(token_bytes) > _MAX_TOKEN_BYTES:
            raise self._unauthorized()
        return token

    def _decode(self, token: str) -> Mapping[str, Any]:
        try:
            signing_key = self._key_provider.get_signing_key_from_jwt(token)
            key = getattr(signing_key, "key", signing_key)
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(self._algorithms),
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._clock_skew_seconds,
                options={
                    "require": ["exp", "iat", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "verify_iss": True,
                    "verify_aud": True,
                },
            )
        except jwt.ExpiredSignatureError as exc:
            raise self._unauthorized("oidc_identity_expired") from exc
        except Exception as exc:
            raise self._unauthorized() from exc
        if not isinstance(claims, Mapping):
            raise self._unauthorized()
        return claims

    def _to_context(self, claims: Mapping[str, Any]) -> AuthenticatedRuntimeContext:
        subject = _claim_string(claims, "sub")
        organization_id = _claim_string(claims, self._mapping.organization_claim)
        assert subject is not None and organization_id is not None

        for claim_name in self._mapping.required_claims:
            if claims.get(claim_name) is None:
                raise ValueError(f"required OIDC claim missing:{claim_name}")

        issued_at = claims.get("iat")
        expires_at = claims.get("exp")
        if isinstance(issued_at, bool) or not isinstance(issued_at, (int, float)):
            raise ValueError("invalid iat claim")
        if isinstance(expires_at, bool) or not isinstance(expires_at, (int, float)):
            raise ValueError("invalid exp claim")
        now = int(self._now())
        if int(issued_at) > now + self._clock_skew_seconds:
            raise ValueError("OIDC token issued in the future")
        if int(expires_at) - int(issued_at) > self._max_ttl_seconds:
            raise ValueError("OIDC token TTL exceeds configured maximum")

        if self._authorized_parties:
            azp = _claim_string(claims, "azp")
            if azp not in self._authorized_parties:
                raise ValueError("OIDC authorized party rejected")

        role = "operator"
        if self._mapping.role_claim is not None:
            token_role = _claim_string(claims, self._mapping.role_claim, required=False)
            if token_role is not None:
                role = token_role

        identity_id = subject
        if self._mapping.identity_claim is not None:
            token_identity = _claim_string(claims, self._mapping.identity_claim, required=False)
            if token_identity is not None:
                identity_id = token_identity

        claim_permissions = frozenset()
        if self._mapping.permissions_claim is not None:
            claim_permissions = _claim_permissions(claims.get(self._mapping.permissions_claim))
        accepted_claim_permissions = claim_permissions & self._allowed_claim_permissions
        privileged = accepted_claim_permissions & PRIVILEGED_RUNTIME_PERMISSIONS
        if not privileged.issubset(self._allowed_privileged_permissions):
            raise ValueError("OIDC privileged permission rejected")

        return AuthenticatedRuntimeContext(
            organization_id=organization_id,
            identity_id=identity_id,
            user_id=subject,
            role=role,
            permissions=self._base_permissions | accepted_claim_permissions,
            seed=None,
        )

    def __call__(self, request: Request) -> AuthenticatedRuntimeContext:
        try:
            return self._to_context(self._decode(self._extract_token(request)))
        except HTTPException:
            raise
        except Exception as exc:
            raise self._unauthorized() from exc
