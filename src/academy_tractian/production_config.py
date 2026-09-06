from __future__ import annotations

from ipaddress import ip_address
import json
import re
from typing import Literal, Mapping
from urllib.parse import parse_qs, urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator


_GIT_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
_PROVIDER_ACCOUNT_ID = re.compile(r"^[A-Za-z0-9]+$")
_LOCAL_HOST_ALIASES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "host.docker.internal",
        "gateway.docker.internal",
        "docker.for.mac.host.internal",
    }
)
_BASE_REQUIRED_ENV = (
    "ACADEMY_ENVIRONMENT",
    "ACADEMY_POSTGRES_INTERNAL_DSN",
    "ACADEMY_POSTGRES_SCOPED_DSN",
    "ACADEMY_PUBLIC_BASE_URL",
    "ACADEMY_RELEASE_GIT_SHA",
    "ACADEMY_DEPLOYMENT_ID",
    "ACADEMY_COST_POLICY",
    "ACADEMY_PAID_FALLBACK_ENABLED",
    "ACADEMY_LOCAL_SERVING_ENABLED",
)
_SIGNED_BEARER_REQUIRED_ENV = (
    "ACADEMY_RUNTIME_IDENTITY_SECRET",
    "ACADEMY_RUNTIME_IDENTITY_ISSUER",
    "ACADEMY_RUNTIME_IDENTITY_AUDIENCE",
)
_NEON_AUTH_REQUIRED_ENV = ("ACADEMY_NEON_AUTH_BASE_URL",)
_PROVIDER_REQUIRED_ENV = (
    "ACADEMY_PROVIDER_SELECTION_STATE",
    "ACADEMY_PROVIDER_ID",
    "ACADEMY_PROVIDER_MODEL_ID",
    "ACADEMY_PROVIDER_ACCOUNT_ID",
    "ACADEMY_PROVIDER_API_TOKEN",
)


def _parse_bool(value: str, *, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{name} must be explicitly true or false")


def _parse_positive_float(value: str, *, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive number") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive number")
    return parsed


def _is_local_endpoint(hostname: str) -> bool:
    host = hostname.strip().lower().rstrip(".")
    if host in _LOCAL_HOST_ALIASES or host.endswith(".localhost") or host.endswith(".local"):
        return True
    try:
        address = ip_address(host)
    except ValueError:
        return False
    return address.is_loopback or address.is_unspecified or address.is_link_local


def _validate_remote_postgres_dsn(value: SecretStr) -> SecretStr:
    raw = value.get_secret_value().strip()
    parsed = urlsplit(raw)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise ValueError("production database must use a remote PostgreSQL URI")
    if parsed.hostname is None or parsed.username is None:
        raise ValueError("production database must use a remote PostgreSQL URI with an explicit role")
    if _is_local_endpoint(parsed.hostname):
        raise ValueError("production database must use a remote PostgreSQL endpoint, not localhost")
    query = parse_qs(parsed.query, keep_blank_values=True)
    ssl_modes = [item.lower() for item in query.get("sslmode", [])]
    if not ssl_modes or any(item not in {"require", "verify-ca", "verify-full"} for item in ssl_modes):
        raise ValueError("remote PostgreSQL production DSN must require TLS via sslmode")
    return SecretStr(raw)


def _postgres_role(value: SecretStr) -> str:
    parsed = urlsplit(value.get_secret_value())
    if parsed.username is None:
        raise ValueError("production database role is missing")
    return parsed.username


def _validate_remote_https_origin(value: str, *, label: str) -> str:
    normalized = value.strip().rstrip("/")
    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or parsed.hostname is None or _is_local_endpoint(parsed.hostname):
        raise ValueError(f"{label} must be a remote HTTPS endpoint")
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError(f"{label} must not contain credentials/query/fragment")
    return normalized


def _parse_tractian_server_headers(value: SecretStr) -> dict[str, str]:
    raw = value.get_secret_value()
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("TRACTIAN server headers must be a valid JSON object") from exc
    if not isinstance(decoded, dict) or not decoded:
        raise ValueError("TRACTIAN server headers must be a non-empty JSON object")
    headers: dict[str, str] = {}
    for key, item in decoded.items():
        if not isinstance(key, str) or not isinstance(item, str) or not key.strip() or not item.strip():
            raise ValueError("TRACTIAN server headers must map non-empty strings to non-empty strings")
        headers[key] = item
    return headers


class RemoteProductionConfig(BaseModel):
    """Fail-closed configuration boundary for remotely served production."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    environment: str = Field(min_length=1)
    internal_dsn: SecretStr
    scoped_dsn: SecretStr
    browser_iam_mode: Literal["signed-bearer", "neon-auth"] = "signed-bearer"
    runtime_identity_secret: SecretStr | None = None
    runtime_identity_issuer: str | None = Field(default=None, max_length=200)
    runtime_identity_audience: str | None = Field(default=None, max_length=200)
    neon_auth_base_url: str | None = Field(default=None, max_length=2048)
    public_base_url: str = Field(min_length=1, max_length=2048)
    release_git_sha: str
    deployment_id: str = Field(min_length=1, max_length=200)
    cost_policy: str = Field(min_length=1)
    paid_fallback_enabled: bool
    local_serving_enabled: bool
    provider_calls_enabled: bool = False
    provider_selection_state: Literal["NO_SELECTION", "PROVISIONAL_RELEASE_PROVIDER"] = "NO_SELECTION"
    provider_id: str | None = Field(default=None, max_length=128)
    provider_model_id: str | None = Field(default=None, max_length=192)
    provider_account_id: str | None = Field(default=None, max_length=128)
    provider_api_token: SecretStr | None = None
    provider_timeout_seconds: float = Field(default=60.0, gt=0, le=120)
    tractian_transport_enabled: bool = False
    tractian_base_url: str | None = Field(default=None, max_length=2048)
    tractian_server_headers_json: SecretStr | None = None

    @field_validator("internal_dsn", "scoped_dsn")
    @classmethod
    def validate_postgres_dsn(cls, value: SecretStr) -> SecretStr:
        return _validate_remote_postgres_dsn(value)

    @field_validator("runtime_identity_secret")
    @classmethod
    def validate_runtime_identity_secret(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        raw = value.get_secret_value()
        if len(raw.encode("utf-8")) < 32:
            raise ValueError("runtime identity secret must be at least 32 bytes")
        normalized = raw.strip().lower()
        if any(marker in normalized for marker in ("change-me", "placeholder", "example-secret", "test-secret")):
            raise ValueError("runtime identity secret must not be a development placeholder")
        return value

    @field_validator("runtime_identity_issuer", "runtime_identity_audience")
    @classmethod
    def validate_optional_identity_label(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("runtime identity label must be non-empty when configured")
        return normalized

    @field_validator("provider_id", "provider_model_id")
    @classmethod
    def validate_optional_provider_label(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("provider label must be non-empty when configured")
        return normalized

    @field_validator("provider_account_id")
    @classmethod
    def validate_provider_account_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not _PROVIDER_ACCOUNT_ID.fullmatch(normalized):
            raise ValueError("provider account id must contain only ASCII letters and digits")
        return normalized

    @field_validator("provider_api_token")
    @classmethod
    def validate_provider_api_token(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        raw = value.get_secret_value().strip()
        if not raw:
            raise ValueError("provider API token must be non-empty")
        return SecretStr(raw)

    @field_validator("public_base_url")
    @classmethod
    def validate_public_base_url(cls, value: str) -> str:
        return _validate_remote_https_origin(value, label="production public base URL")

    @field_validator("neon_auth_base_url")
    @classmethod
    def validate_neon_auth_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_remote_https_origin(value, label="Neon Auth base URL")

    @field_validator("tractian_base_url")
    @classmethod
    def validate_tractian_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_remote_https_origin(value, label="TRACTIAN base URL")

    @field_validator("release_git_sha")
    @classmethod
    def validate_release_git_sha(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not _GIT_SHA.fullmatch(normalized):
            raise ValueError("release git SHA must be an exact 40-character hexadecimal commit SHA")
        return normalized

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        if value.strip().lower() != "production":
            raise ValueError("remote serving configuration must use the production environment")
        return "production"

    @field_validator("cost_policy")
    @classmethod
    def validate_cost_policy(cls, value: str) -> str:
        if value.strip().lower() != "usd0-hard-gate":
            raise ValueError("production cost policy must remain usd0-hard-gate")
        return "usd0-hard-gate"

    @model_validator(mode="after")
    def validate_hard_boundaries(self) -> "RemoteProductionConfig":
        if self.paid_fallback_enabled:
            raise ValueError("paid fallback is forbidden by the USD0 hard gate")
        if self.local_serving_enabled:
            raise ValueError("local serving is forbidden in the production topology")
        if _postgres_role(self.internal_dsn) == _postgres_role(self.scoped_dsn):
            raise ValueError("internal and scoped database DSNs must use distinct PostgreSQL roles")
        if self.internal_dsn.get_secret_value() == self.scoped_dsn.get_secret_value():
            raise ValueError("internal and scoped database DSNs must be distinct")

        if self.browser_iam_mode == "signed-bearer":
            if self.runtime_identity_secret is None or not self.runtime_identity_issuer or not self.runtime_identity_audience:
                raise ValueError("signed-bearer IAM requires runtime identity secret, issuer and audience")
        elif self.neon_auth_base_url is None:
            raise ValueError("neon-auth IAM requires ACADEMY_NEON_AUTH_BASE_URL")

        provider_fields_present = any(
            value is not None
            for value in (
                self.provider_id,
                self.provider_model_id,
                self.provider_account_id,
                self.provider_api_token,
            )
        )
        if self.provider_calls_enabled:
            if self.provider_selection_state != "PROVISIONAL_RELEASE_PROVIDER":
                raise ValueError("enabled provider calls require PROVISIONAL_RELEASE_PROVIDER state")
            if not all(
                (
                    self.provider_id,
                    self.provider_model_id,
                    self.provider_account_id,
                    self.provider_api_token,
                )
            ):
                raise ValueError("enabled provider calls require explicit provider id/model/account/token")
        elif self.provider_selection_state != "NO_SELECTION" or provider_fields_present:
            raise ValueError("provider configuration cannot be present while provider calls are disabled")

        if self.tractian_transport_enabled:
            if self.tractian_base_url is None or self.tractian_server_headers_json is None:
                raise ValueError(
                    "enabled TRACTIAN transport requires ACADEMY_TRACTIAN_BASE_URL and ACADEMY_TRACTIAN_SERVER_HEADERS_JSON"
                )
            _parse_tractian_server_headers(self.tractian_server_headers_json)
        elif self.tractian_base_url is not None or self.tractian_server_headers_json is not None:
            raise ValueError(
                "TRACTIAN endpoint/headers cannot be configured while ACADEMY_TRACTIAN_TRANSPORT_ENABLED is false"
            )
        return self

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> "RemoteProductionConfig":
        browser_iam_mode = environ.get("ACADEMY_BROWSER_IAM_MODE", "signed-bearer").strip().lower()
        provider_calls_enabled = _parse_bool(
            environ.get("ACADEMY_PROVIDER_CALLS_ENABLED", "false"),
            name="ACADEMY_PROVIDER_CALLS_ENABLED",
        )
        required = list(_BASE_REQUIRED_ENV)
        if browser_iam_mode == "signed-bearer":
            required.extend(_SIGNED_BEARER_REQUIRED_ENV)
        elif browser_iam_mode == "neon-auth":
            required.extend(_NEON_AUTH_REQUIRED_ENV)
        if provider_calls_enabled:
            required.extend(_PROVIDER_REQUIRED_ENV)
        missing = [name for name in required if not environ.get(name, "").strip()]
        if missing:
            raise ValueError(
                "missing required production environment variables: " + ", ".join(sorted(missing))
            )

        runtime_secret = environ.get("ACADEMY_RUNTIME_IDENTITY_SECRET", "").strip()
        provider_token = environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
        tractian_headers = environ.get("ACADEMY_TRACTIAN_SERVER_HEADERS_JSON", "")
        return cls(
            environment=environ["ACADEMY_ENVIRONMENT"],
            internal_dsn=SecretStr(environ["ACADEMY_POSTGRES_INTERNAL_DSN"]),
            scoped_dsn=SecretStr(environ["ACADEMY_POSTGRES_SCOPED_DSN"]),
            browser_iam_mode=browser_iam_mode,
            runtime_identity_secret=SecretStr(runtime_secret) if runtime_secret else None,
            runtime_identity_issuer=environ.get("ACADEMY_RUNTIME_IDENTITY_ISSUER") or None,
            runtime_identity_audience=environ.get("ACADEMY_RUNTIME_IDENTITY_AUDIENCE") or None,
            neon_auth_base_url=environ.get("ACADEMY_NEON_AUTH_BASE_URL") or None,
            public_base_url=environ["ACADEMY_PUBLIC_BASE_URL"],
            release_git_sha=environ["ACADEMY_RELEASE_GIT_SHA"],
            deployment_id=environ["ACADEMY_DEPLOYMENT_ID"],
            cost_policy=environ["ACADEMY_COST_POLICY"],
            paid_fallback_enabled=_parse_bool(
                environ["ACADEMY_PAID_FALLBACK_ENABLED"],
                name="ACADEMY_PAID_FALLBACK_ENABLED",
            ),
            local_serving_enabled=_parse_bool(
                environ["ACADEMY_LOCAL_SERVING_ENABLED"],
                name="ACADEMY_LOCAL_SERVING_ENABLED",
            ),
            provider_calls_enabled=provider_calls_enabled,
            provider_selection_state=environ.get("ACADEMY_PROVIDER_SELECTION_STATE", "NO_SELECTION").strip(),
            provider_id=environ.get("ACADEMY_PROVIDER_ID") or None,
            provider_model_id=environ.get("ACADEMY_PROVIDER_MODEL_ID") or None,
            provider_account_id=environ.get("ACADEMY_PROVIDER_ACCOUNT_ID") or None,
            provider_api_token=SecretStr(provider_token) if provider_token else None,
            provider_timeout_seconds=_parse_positive_float(
                environ.get("ACADEMY_PROVIDER_TIMEOUT_SECONDS", "60"),
                name="ACADEMY_PROVIDER_TIMEOUT_SECONDS",
            ),
            tractian_transport_enabled=_parse_bool(
                environ.get("ACADEMY_TRACTIAN_TRANSPORT_ENABLED", "false"),
                name="ACADEMY_TRACTIAN_TRANSPORT_ENABLED",
            ),
            tractian_base_url=environ.get("ACADEMY_TRACTIAN_BASE_URL") or None,
            tractian_server_headers_json=(
                SecretStr(tractian_headers) if tractian_headers.strip() else None
            ),
        )

    def tractian_server_headers(self) -> dict[str, str]:
        """Return server-managed TRACTIAN headers only inside the trusted composition boundary."""

        if self.tractian_server_headers_json is None:
            return {}
        return _parse_tractian_server_headers(self.tractian_server_headers_json)

    def safe_metadata(self) -> dict[str, object]:
        """Return browser-safe release identity without DSNs, hosts, account ids or secrets."""

        metadata: dict[str, object] = {
            "schema_version": "remote-production-release-v2",
            "environment": self.environment,
            "browser_iam_mode": self.browser_iam_mode,
            "public_base_url": self.public_base_url,
            "release_git_sha": self.release_git_sha,
            "deployment_id": self.deployment_id,
            "cost_policy": self.cost_policy,
            "paid_fallback_enabled": self.paid_fallback_enabled,
            "local_serving_enabled": self.local_serving_enabled,
            "provider_calls_enabled": self.provider_calls_enabled,
        }
        # Keep the existing NO_SELECTION metadata contract byte-compatible for infrastructure
        # probes. Release 0 adds only non-secret provider/model identity when calls are active.
        if self.provider_calls_enabled:
            metadata.update(
                {
                    "provider_selection_state": self.provider_selection_state,
                    "provider_id": self.provider_id,
                    "provider_model_id": self.provider_model_id,
                }
            )
        return metadata
