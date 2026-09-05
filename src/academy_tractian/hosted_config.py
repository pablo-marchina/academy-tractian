from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import os
from typing import Mapping
from urllib.parse import parse_qsl, urlsplit


_SUPPORTED_PROVIDERS = frozenset({"cloudflare", "google", "groq", "openai"})
_SUPPORTED_OIDC_ALGORITHMS = frozenset(
    {"RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512", "EdDSA"}
)
_PROVIDER_KEY_ENV = {
    "cloudflare": "CLOUDFLARE_API_TOKEN",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
}
_LOCAL_NAMES = frozenset({"localhost", "localhost.localdomain", "host.docker.internal"})
_CLOUD_SQL_SOCKET_PREFIX = "/cloudsql/"
_POSTGRES_SOCKET_SUFFIX = "/.s.PGSQL.5432"


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ValueError(f"missing_required_environment:{name}")
    return value


def _optional(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name, "").strip()
    return value or None


def _csv(env: Mapping[str, str], name: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item.strip() for item in env.get(name, "").split(",") if item.strip()))


def _bool(env: Mapping[str, str], name: str, default: bool = False) -> bool:
    raw = env.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"invalid_boolean_environment:{name}")


def _int(env: Mapping[str, str], name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = env.get(name, "").strip()
    try:
        value = default if not raw else int(raw)
    except ValueError as exc:
        raise ValueError(f"invalid_integer_environment:{name}") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"out_of_range_environment:{name}")
    return value


def _is_local(host: str | None) -> bool:
    if not host:
        return True
    normalized = host.rstrip(".").lower()
    if normalized in _LOCAL_NAMES or normalized.endswith(".localhost"):
        return True
    try:
        address = ipaddress.ip_address(normalized.split("%", 1)[0])
    except ValueError:
        return False
    return address.is_loopback or address.is_unspecified or address.is_link_local


def _https(value: str, *, name: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError(f"invalid_https_url:{name}")
    if parsed.query or parsed.fragment or _is_local(parsed.hostname):
        raise ValueError(f"non_public_https_url:{name}")
    return value.rstrip("/")


def _validate_cloud_sql_socket(socket_dir: str, *, name: str) -> None:
    if not socket_dir.startswith(_CLOUD_SQL_SOCKET_PREFIX):
        raise ValueError(f"non_cloud_sql_socket_forbidden:{name}")
    connection_name = socket_dir[len(_CLOUD_SQL_SOCKET_PREFIX) :]
    if not connection_name or "/" in connection_name or any(character.isspace() for character in connection_name):
        raise ValueError(f"invalid_cloud_sql_socket:{name}")
    try:
        project, region, instance = connection_name.rsplit(":", 2)
    except ValueError as exc:
        raise ValueError(f"invalid_cloud_sql_socket:{name}") from exc
    if not project or not region or not instance:
        raise ValueError(f"invalid_cloud_sql_socket:{name}")
    if not all(character.isalnum() or character in {"-", ".", ":"} for character in project):
        raise ValueError(f"invalid_cloud_sql_socket:{name}")
    if not all(character.islower() or character.isdigit() or character == "-" for character in region):
        raise ValueError(f"invalid_cloud_sql_socket:{name}")
    if not all(character.islower() or character.isdigit() or character == "-" for character in instance):
        raise ValueError(f"invalid_cloud_sql_socket:{name}")
    # Linux sockaddr_un.sun_path is 108 bytes including the terminating NUL. libpq appends the
    # PostgreSQL socket filename to the directory provided in the host parameter.
    effective_socket_path = f"{socket_dir}{_POSTGRES_SOCKET_SUFFIX}".encode("utf-8")
    if len(effective_socket_path) > 107:
        raise ValueError(f"cloud_sql_socket_path_too_long:{name}")


def _postgres(value: str, *, name: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.path or parsed.path == "/" or parsed.fragment:
        raise ValueError(f"invalid_postgres_dsn:{name}")
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    host_values = [query_value for query_name, query_value in query_pairs if query_name == "host"]

    if parsed.hostname is not None:
        # A query-level host can override the URI authority in libpq; forbid that ambiguity so a
        # superficially remote DSN cannot redirect the serving process to localhost or a socket.
        if host_values:
            raise ValueError(f"ambiguous_postgres_host:{name}")
        if _is_local(parsed.hostname):
            raise ValueError(f"local_postgres_forbidden:{name}")
        return value

    # Hostless PostgreSQL URIs are accepted only for Cloud Run's managed Cloud SQL Unix socket.
    # Keep the shape intentionally narrow: arbitrary local sockets and extra libpq query overrides
    # are not part of the production contract.
    if len(query_pairs) != 1 or len(host_values) != 1:
        raise ValueError(f"invalid_postgres_dsn:{name}")
    _validate_cloud_sql_socket(host_values[0], name=name)
    return value


def _cors(env: Mapping[str, str]) -> tuple[str, ...]:
    values = _csv(env, "ACADEMY_CORS_ORIGINS")
    if not values:
        raise ValueError("missing_required_environment:ACADEMY_CORS_ORIGINS")
    normalized: list[str] = []
    for value in values:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.netloc or parsed.path not in {"", "/"}:
            raise ValueError("invalid_cors_origin")
        normalized.append(_https(f"https://{parsed.netloc}", name="ACADEMY_CORS_ORIGINS"))
    return tuple(dict.fromkeys(normalized))


@dataclass(frozen=True, repr=False)
class HostedProductConfig:
    """Production serving contract. It contains no migration/DDL credential and no demo identity."""

    postgres_service_dsn: str
    postgres_scoped_dsn: str
    postgres_schema: str
    cors_origins: tuple[str, ...]
    oidc_issuer: str
    oidc_audience: str
    oidc_jwks_url: str
    oidc_algorithms: tuple[str, ...]
    oidc_organization_claim: str
    oidc_role_claim: str
    oidc_permissions_claim: str
    oidc_identity_claim: str
    oidc_authorized_parties: tuple[str, ...]
    allowed_claim_permissions: tuple[str, ...]
    tractian_base_url: str
    tractian_bearer_token: str | None
    provider: str
    model: str
    provider_api_key: str
    provider_account_id: str | None
    actions_enabled: bool
    max_workers: int
    heartbeat_interval_ms: int
    host: str
    port: int

    def __repr__(self) -> str:
        return (
            "HostedProductConfig("
            f"postgres_schema={self.postgres_schema!r}, provider={self.provider!r}, model={self.model!r}, "
            f"actions_enabled={self.actions_enabled!r}, cors_origins={self.cors_origins!r}, "
            "postgres_service_dsn=<redacted>, postgres_scoped_dsn=<redacted>, "
            "provider_api_key=<redacted>, tractian_bearer_token=<redacted>)"
        )

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "HostedProductConfig":
        env = os.environ if environment is None else environment
        provider = _required(env, "ACADEMY_PROVIDER").lower()
        if provider not in _SUPPORTED_PROVIDERS:
            raise ValueError("unsupported_hosted_provider")
        algorithms = _csv(env, "ACADEMY_OIDC_ALGORITHMS")
        if not algorithms:
            raise ValueError("missing_required_environment:ACADEMY_OIDC_ALGORITHMS")
        if not set(algorithms).issubset(_SUPPORTED_OIDC_ALGORITHMS):
            raise ValueError("unsupported_oidc_algorithm")
        model = _required(env, "ACADEMY_MODEL")
        provider_account_id = _optional(env, "CLOUDFLARE_ACCOUNT_ID") if provider == "cloudflare" else None
        if provider == "cloudflare" and provider_account_id is None:
            raise ValueError("missing_required_environment:CLOUDFLARE_ACCOUNT_ID")
        return cls(
            postgres_service_dsn=_postgres(_required(env, "ACADEMY_POSTGRES_SERVICE_DSN"), name="ACADEMY_POSTGRES_SERVICE_DSN"),
            postgres_scoped_dsn=_postgres(_required(env, "ACADEMY_POSTGRES_SCOPED_DSN"), name="ACADEMY_POSTGRES_SCOPED_DSN"),
            postgres_schema=_optional(env, "ACADEMY_POSTGRES_SCHEMA") or "academy_operational",
            cors_origins=_cors(env),
            oidc_issuer=_https(_required(env, "ACADEMY_OIDC_ISSUER"), name="ACADEMY_OIDC_ISSUER"),
            oidc_audience=_required(env, "ACADEMY_OIDC_AUDIENCE"),
            oidc_jwks_url=_https(_required(env, "ACADEMY_OIDC_JWKS_URL"), name="ACADEMY_OIDC_JWKS_URL"),
            oidc_algorithms=algorithms,
            oidc_organization_claim=_optional(env, "ACADEMY_OIDC_ORGANIZATION_CLAIM") or "organization_id",
            oidc_role_claim=_optional(env, "ACADEMY_OIDC_ROLE_CLAIM") or "role",
            oidc_permissions_claim=_optional(env, "ACADEMY_OIDC_PERMISSIONS_CLAIM") or "permissions",
            oidc_identity_claim=_optional(env, "ACADEMY_OIDC_IDENTITY_CLAIM") or "sid",
            oidc_authorized_parties=_csv(env, "ACADEMY_OIDC_AUTHORIZED_PARTIES"),
            allowed_claim_permissions=_csv(env, "ACADEMY_OIDC_ALLOWED_PERMISSIONS"),
            tractian_base_url=_https(_required(env, "ACADEMY_TRACTIAN_BASE_URL"), name="ACADEMY_TRACTIAN_BASE_URL"),
            tractian_bearer_token=_optional(env, "ACADEMY_TRACTIAN_BEARER_TOKEN"),
            provider=provider,
            model=model,
            provider_api_key=_required(env, _PROVIDER_KEY_ENV[provider]),
            provider_account_id=provider_account_id,
            actions_enabled=_bool(env, "ACADEMY_ACTIONS_ENABLED", False),
            max_workers=_int(env, "ACADEMY_MAX_WORKERS", 4, minimum=1, maximum=64),
            heartbeat_interval_ms=_int(env, "ACADEMY_HEARTBEAT_INTERVAL_MS", 1000, minimum=250, maximum=10000),
            host=env.get("HOST", "0.0.0.0").strip() or "0.0.0.0",
            port=_int(env, "PORT", 8000, minimum=1, maximum=65535),
        )

    def sanitized_summary(self) -> dict[str, object]:
        return {
            "schema_version": "hosted-product-config-v1",
            "deployment": {"profile": "production-hosted", "required_local_components": 0, "runtime_ddl_credential": False},
            "identity": {
                "backend": "oidc-jwks-v1",
                "issuer": self.oidc_issuer,
                "audience": self.oidc_audience,
                "algorithms": list(self.oidc_algorithms),
                "authorized_parties": list(self.oidc_authorized_parties),
            },
            "persistence": {"backend": "postgresql", "schema": self.postgres_schema, "service_role": True, "scoped_rls_role": True},
            "provider": {"provider": self.provider, "model": self.model, "api_key_configured": True},
            "tractian": {"base_url_configured": True, "bearer_configured": self.tractian_bearer_token is not None},
            "actions": {"kill_switch_enabled": not self.actions_enabled},
        }
