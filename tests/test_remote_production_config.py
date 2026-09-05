from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

import academy_tractian.remote_production as remote_production
from academy_tractian.production_config import RemoteProductionConfig


BASE_ENV = {
    "ACADEMY_ENVIRONMENT": "production",
    "ACADEMY_POSTGRES_INTERNAL_DSN": (
        "postgresql://academy_internal:internal-password@db.academy-cloud.net:5432/academy?sslmode=require"
    ),
    "ACADEMY_POSTGRES_SCOPED_DSN": (
        "postgresql://academy_scoped:scoped-password@db.academy-cloud.net:5432/academy?sslmode=require"
    ),
    "ACADEMY_RUNTIME_IDENTITY_SECRET": "runtime-identity-secret-with-more-than-32-bytes",
    "ACADEMY_RUNTIME_IDENTITY_ISSUER": "academy-production",
    "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": "academy-product",
    "ACADEMY_PUBLIC_BASE_URL": "https://app.academy-cloud.net",
    "ACADEMY_RELEASE_GIT_SHA": "a" * 40,
    "ACADEMY_DEPLOYMENT_ID": "deploy-20260905-001",
    "ACADEMY_COST_POLICY": "usd0-hard-gate",
    "ACADEMY_PAID_FALLBACK_ENABLED": "false",
    "ACADEMY_LOCAL_SERVING_ENABLED": "false",
    "ACADEMY_PROVIDER_CALLS_ENABLED": "false",
}


def _config(**overrides: str) -> RemoteProductionConfig:
    env = {**BASE_ENV, **overrides}
    return RemoteProductionConfig.from_env(env)


def test_valid_remote_usd0_configuration_is_accepted_and_metadata_is_sanitized() -> None:
    config = _config()

    assert config.environment == "production"
    assert config.cost_policy == "usd0-hard-gate"
    assert config.paid_fallback_enabled is False
    assert config.local_serving_enabled is False
    assert config.provider_calls_enabled is False

    metadata = config.safe_metadata()
    assert metadata == {
        "schema_version": "remote-production-release-v1",
        "environment": "production",
        "public_base_url": "https://app.academy-cloud.net",
        "release_git_sha": "a" * 40,
        "deployment_id": "deploy-20260905-001",
        "cost_policy": "usd0-hard-gate",
        "paid_fallback_enabled": False,
        "local_serving_enabled": False,
        "provider_calls_enabled": False,
    }
    rendered = repr(metadata)
    assert "internal-password" not in rendered
    assert "scoped-password" not in rendered
    assert "runtime-identity-secret" not in rendered
    assert "db.academy-cloud.net" not in rendered


@pytest.mark.parametrize(
    "dsn",
    [
        "postgresql://academy_internal:secret@localhost:5432/academy",
        "postgresql://academy_internal:secret@127.0.0.1:5432/academy",
        "postgresql://academy_internal:secret@[::1]:5432/academy",
        "postgresql://academy_internal:secret@0.0.0.0:5432/academy",
        "postgresql://academy_internal:secret@host.docker.internal:5432/academy",
        "postgresql:///academy?host=/var/run/postgresql",
        "sqlite:///tmp/academy.db",
    ],
)
def test_production_database_rejects_local_socket_loopback_and_non_postgres_dsn(dsn: str) -> None:
    with pytest.raises(ValidationError, match="remote PostgreSQL"):
        _config(ACADEMY_POSTGRES_INTERNAL_DSN=dsn)


def test_private_remote_database_address_is_not_confused_with_localhost() -> None:
    config = _config(
        ACADEMY_POSTGRES_INTERNAL_DSN=(
            "postgresql://academy_internal:secret@10.20.30.40:5432/academy?sslmode=require"
        ),
        ACADEMY_POSTGRES_SCOPED_DSN=(
            "postgresql://academy_scoped:secret@10.20.30.40:5432/academy?sslmode=require"
        ),
    )
    assert config.environment == "production"


def test_internal_and_scoped_database_roles_must_be_distinct() -> None:
    with pytest.raises(ValidationError, match="distinct PostgreSQL roles"):
        _config(
            ACADEMY_POSTGRES_SCOPED_DSN=(
                "postgresql://academy_internal:other-password@db.academy-cloud.net:5432/academy?sslmode=require"
            )
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://app.academy-cloud.net",
        "https://localhost:8443",
        "https://127.0.0.1:8443",
        "https://host.docker.internal:8443",
    ],
)
def test_public_production_url_requires_remote_https(url: str) -> None:
    with pytest.raises(ValidationError, match="remote HTTPS"):
        _config(ACADEMY_PUBLIC_BASE_URL=url)


def test_weak_runtime_secret_fails_before_product_boot() -> None:
    with pytest.raises(ValidationError, match="at least 32 bytes"):
        _config(ACADEMY_RUNTIME_IDENTITY_SECRET="change-me")


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("ACADEMY_COST_POLICY", "best-effort-free", "usd0-hard-gate"),
        ("ACADEMY_PAID_FALLBACK_ENABLED", "true", "paid fallback"),
        ("ACADEMY_LOCAL_SERVING_ENABLED", "true", "local serving"),
        ("ACADEMY_ENVIRONMENT", "development", "production"),
    ],
)
def test_hard_project_constraints_cannot_be_relaxed_by_environment(
    key: str,
    value: str,
    message: str,
) -> None:
    with pytest.raises((ValidationError, ValueError), match=message):
        _config(**{key: value})


def test_release_identity_is_mandatory_and_git_sha_is_exact() -> None:
    with pytest.raises(ValueError, match="ACADEMY_DEPLOYMENT_ID"):
        RemoteProductionConfig.from_env(
            {key: value for key, value in BASE_ENV.items() if key != "ACADEMY_DEPLOYMENT_ID"}
        )
    with pytest.raises(ValidationError, match="40-character"):
        _config(ACADEMY_RELEASE_GIT_SHA="abc123")


def test_remote_app_wrapper_validates_before_delegate_and_exposes_only_safe_release_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_builder(**kwargs):
        captured.update(kwargs)
        return FastAPI()

    monkeypatch.setattr(
        remote_production,
        "create_authenticated_postgres_action_capable_product_app",
        fake_builder,
    )
    config = _config()
    app = remote_production.create_remote_production_app(
        config=config,
        decision_source_factory=lambda: object(),
        transport_factory=lambda: object(),
        authorization_resolver=lambda **_: object(),
    )

    assert captured["initialize_schema"] is False
    assert captured["provider_calls_enabled"] is False
    assert captured["actions_enabled"] is False
    assert captured["runtime_identity_secret"] == config.runtime_identity_secret.get_secret_value()
    assert app.state.remote_production is True

    with TestClient(app) as client:
        response = client.get("/api/meta/release")
    assert response.status_code == 200
    assert response.json() == config.safe_metadata()
    assert "runtime_identity_secret" not in response.text
    assert "postgres" not in response.text.lower()
