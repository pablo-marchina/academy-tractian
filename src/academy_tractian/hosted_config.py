from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping
from urllib.parse import urlsplit


_SUPPORTED_PROVIDERS = frozenset({"openai", "google"})


def _required(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "").strip()
    if not value:
        raise ValueError(f"missing_required_environment:{name}")
    return value


def _optional(environment: Mapping[str, str], name: str) -> str | None:
    value = environment.get(name, "").strip()
    return value or None


def _positive_int(environment: Mapping[str, str], name: str, default: int) -> int:
    raw = environment.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"invalid_integer_environment:{name}") from exc
    if value <= 0:
        raise ValueError(f"non_positive_integer_environment:{name}")
    return value


def _http_url(value: str, *, name: str, require_https: bool) -> str:
    parsed = urlsplit(value)
    allowed = {"https"} if require_https else {"http", "https"}
    if parsed.scheme not in allowed or not parsed.netloc:
        raise ValueError(f"invalid_http_url:{name}")
    if parsed.username or parsed.password:
        raise ValueError(f"url_credentials_forbidden:{name}")
    if parsed.query or parsed.fragment:
        raise ValueError(f"url_query_or_fragment_forbidden:{name}")
    return value.rstrip("/")


def _postgres_dsn(value: str, *, name: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname or not parsed.path:
        raise ValueError(f"invalid_postgres_dsn:{name}")
    return value


def _cors_origins(environment: Mapping[str, str]) -> tuple[str, ...]:
    raw = environment.get("ACADEMY_CORS_ORIGINS", "")
    origins = tuple(item.strip().rstrip("/") for item in raw.split(",") if item.strip())
    if not origins:
        raise ValueError("missing_required_environment:ACADEMY_CORS_ORIGINS")
    normalized: list[str] = []
    for origin in origins:
        parsed = urlsplit(origin)
        if parsed.scheme != "https" or not parsed.netloc or parsed.path not in {"", "/"}:
            raise ValueError("invalid_cors_origin")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("invalid_cors_origin")
        normalized.append(f"{parsed.scheme}://{parsed.netloc}")
    return tuple(dict.fromkeys(normalized))


@dataclass(frozen=True)
class HostedProductConfig:
    """Fail-closed configuration contract for the hosted-only production path.

    Secrets are stored only as private process values and are deliberately omitted from
    ``sanitized_summary``. The config distinguishes infrastructure readiness from agent-serving
    readiness so cloud resources can be validated before a provider/model is scientifically
    promoted.
    """

    postgres_internal_dsn: str
    postgres_scoped_dsn: str
    postgres_schema: str
    observability_schema: str
    cors_origins: tuple[str, ...]
    runtime_identity_secret: str
    runtime_identity_issuer: str
    runtime_identity_audience: str
    tractian_base_url: str | None
    tractian_bearer_token: str | None
    provider: str | None
    provider_api_key: str | None
    max_workers: int
    heartbeat_interval_ms: int

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
        *,
        require_serving_ready: bool = False,
    ) -> "HostedProductConfig":
        env = os.environ if environment is None else environment
        internal_dsn = _postgres_dsn(
            _required(env, "ACADEMY_POSTGRES_INTERNAL_DSN"),
            name="ACADEMY_POSTGRES_INTERNAL_DSN",
        )
        scoped_dsn = _postgres_dsn(
            _required(env, "ACADEMY_POSTGRES_SCOPED_DSN"),
            name="ACADEMY_POSTGRES_SCOPED_DSN",
        )
        secret = _required(env, "ACADEMY_RUNTIME_IDENTITY_SECRET")
        if len(secret.encode("utf-8")) < 32:
            raise ValueError("runtime_identity_secret_too_short")

        provider = _optional(env, "ACADEMY_PROVIDER")
        if provider is not None:
            provider = provider.lower()
            if provider not in _SUPPORTED_PROVIDERS:
                raise ValueError("unsupported_hosted_provider")
        provider_api_key = None
        if provider == "openai":
            provider_api_key = _optional(env, "OPENAI_API_KEY")
        elif provider == "google":
            provider_api_key = _optional(env, "GOOGLE_API_KEY")

        tractian_raw = _optional(env, "ACADEMY_TRACTIAN_BASE_URL")
        tractian_base_url = (
            None
            if tractian_raw is None
            else _http_url(tractian_raw, name="ACADEMY_TRACTIAN_BASE_URL", require_https=True)
        )

        config = cls(
            postgres_internal_dsn=internal_dsn,
            postgres_scoped_dsn=scoped_dsn,
            postgres_schema=_optional(env, "ACADEMY_POSTGRES_SCHEMA") or "academy_operational",
            observability_schema=_optional(env, "ACADEMY_OBSERVABILITY_SCHEMA")
            or "academy_observability",
            cors_origins=_cors_origins(env),
            runtime_identity_secret=secret,
            runtime_identity_issuer=_required(env, "ACADEMY_RUNTIME_IDENTITY_ISSUER"),
            runtime_identity_audience=_required(env, "ACADEMY_RUNTIME_IDENTITY_AUDIENCE"),
            tractian_base_url=tractian_base_url,
            tractian_bearer_token=_optional(env, "ACADEMY_TRACTIAN_BEARER_TOKEN"),
            provider=provider,
            provider_api_key=provider_api_key,
            max_workers=_positive_int(env, "ACADEMY_MAX_WORKERS", 4),
            heartbeat_interval_ms=_positive_int(env, "ACADEMY_HEARTBEAT_INTERVAL_MS", 1000),
        )
        if config.max_workers > 64:
            raise ValueError("ACADEMY_MAX_WORKERS_exceeds_64")
        if not 250 <= config.heartbeat_interval_ms <= 10000:
            raise ValueError("ACADEMY_HEARTBEAT_INTERVAL_MS_out_of_range")
        if require_serving_ready:
            config.assert_serving_ready()
        return config

    def assert_serving_ready(self) -> None:
        if self.provider is None:
            raise ValueError("hosted_provider_not_selected")
        if not self.provider_api_key:
            raise ValueError("hosted_provider_api_key_missing")
        if self.tractian_base_url is None:
            raise ValueError("tractian_base_url_missing")

    def sanitized_summary(self) -> dict[str, object]:
        return {
            "schema_version": "hosted-product-config-v1",
            "persistence": {
                "operational": "postgresql",
                "observability": "postgresql",
                "postgres_schema": self.postgres_schema,
                "observability_schema": self.observability_schema,
                "internal_dsn_configured": bool(self.postgres_internal_dsn),
                "scoped_dsn_configured": bool(self.postgres_scoped_dsn),
            },
            "http": {
                "cors_origins": list(self.cors_origins),
                "tractian_base_url_configured": self.tractian_base_url is not None,
                "tractian_bearer_configured": self.tractian_bearer_token is not None,
            },
            "identity": {
                "backend": "signed-bearer-hmac-sha256-v1",
                "issuer": self.runtime_identity_issuer,
                "audience": self.runtime_identity_audience,
                "secret_configured": bool(self.runtime_identity_secret),
            },
            "provider": {
                "selection": self.provider or "NO_SELECTION",
                "api_key_configured": self.provider_api_key is not None,
            },
            "runtime": {
                "max_workers": self.max_workers,
                "heartbeat_interval_ms": self.heartbeat_interval_ms,
            },
        }
