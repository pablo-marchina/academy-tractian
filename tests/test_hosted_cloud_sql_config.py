from __future__ import annotations

import pytest

from academy_tractian.hosted_config import HostedProductConfig


def _environment() -> dict[str, str]:
    return {
        "ACADEMY_POSTGRES_SERVICE_DSN": (
            "postgresql://academy_service:service-secret@/academy"
            "?host=/cloudsql/academy-prod:southamerica-east1:academy-pg"
        ),
        "ACADEMY_POSTGRES_SCOPED_DSN": (
            "postgresql://academy_scoped:scoped-secret@/academy"
            "?host=/cloudsql/academy-prod:southamerica-east1:academy-pg"
        ),
        "ACADEMY_CORS_ORIGINS": "https://app.example.com",
        "ACADEMY_OIDC_ISSUER": "https://identity.example.com",
        "ACADEMY_OIDC_AUDIENCE": "academy-api",
        "ACADEMY_OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
        "ACADEMY_OIDC_ALGORITHMS": "RS256",
        "ACADEMY_OIDC_AUTHORIZED_PARTIES": "academy-web",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
        "ACADEMY_PROVIDER": "groq",
        "ACADEMY_MODEL": "openai/gpt-oss-120b",
        "GROQ_API_KEY": "provider-secret",
    }


def test_cloud_run_cloud_sql_socket_dsns_are_accepted_without_localhost() -> None:
    config = HostedProductConfig.from_environment(_environment())

    assert "host=/cloudsql/academy-prod:southamerica-east1:academy-pg" in config.postgres_service_dsn
    assert "host=/cloudsql/academy-prod:southamerica-east1:academy-pg" in config.postgres_scoped_dsn


@pytest.mark.parametrize(
    "dsn",
    [
        "postgresql://academy:secret@/academy?host=/tmp/postgres",
        "postgresql://academy:secret@/academy?host=/var/run/postgresql",
        "postgresql://academy:secret@/academy",
        "postgresql://academy:secret@/academy?host=/cloudsql/missing-region-instance",
        "postgresql://academy:secret@/academy?host=/cloudsql/project:REGION:instance",
        "postgresql://academy:secret@/academy?host=/cloudsql/project:region:instance&port=5432",
    ],
)
def test_arbitrary_or_ambiguous_unix_socket_dsns_are_rejected(dsn: str) -> None:
    env = {**_environment(), "ACADEMY_POSTGRES_SERVICE_DSN": dsn}
    with pytest.raises(ValueError):
        HostedProductConfig.from_environment(env)


def test_remote_tcp_dsn_cannot_hide_query_level_local_host_override() -> None:
    env = {
        **_environment(),
        "ACADEMY_POSTGRES_SERVICE_DSN": (
            "postgresql://academy:secret@db.example.com/academy?host=127.0.0.1"
        ),
    }
    with pytest.raises(ValueError, match="ambiguous_postgres_host"):
        HostedProductConfig.from_environment(env)


def test_existing_remote_tcp_postgres_contract_remains_supported() -> None:
    env = {
        **_environment(),
        "ACADEMY_POSTGRES_SERVICE_DSN": "postgresql://academy:secret@db.example.com/academy?sslmode=require",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://academy_scoped:secret@db.example.com/academy?sslmode=require",
    }
    config = HostedProductConfig.from_environment(env)

    assert config.postgres_service_dsn.endswith("sslmode=require")
    assert config.postgres_scoped_dsn.endswith("sslmode=require")


def test_cloud_sql_socket_path_must_fit_linux_unix_socket_limit() -> None:
    very_long_instance = "i" * 80
    env = {
        **_environment(),
        "ACADEMY_POSTGRES_SERVICE_DSN": (
            "postgresql://academy:secret@/academy?host=/cloudsql/"
            f"project:southamerica-east1:{very_long_instance}"
        ),
    }
    with pytest.raises(ValueError, match="cloud_sql_socket_path_too_long"):
        HostedProductConfig.from_environment(env)
