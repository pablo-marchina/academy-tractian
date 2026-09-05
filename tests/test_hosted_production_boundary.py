from __future__ import annotations

import inspect

import pytest

import academy_tractian.hosted_product as hosted_product_module
from academy_tractian.hosted_config import HostedProductConfig
from academy_tractian.hosted_product import HostedTractianTransport


SECRET_MARKERS = {
    "service-password",
    "scoped-password",
    "provider-secret",
    "tractian-secret",
}


def _environment() -> dict[str, str]:
    return {
        "ACADEMY_POSTGRES_SERVICE_DSN": "postgresql://academy_service:service-password@db.example.com/academy",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://academy_scoped:scoped-password@db.example.com/academy",
        "ACADEMY_CORS_ORIGINS": "https://app.example.com",
        "ACADEMY_OIDC_ISSUER": "https://identity.example.com",
        "ACADEMY_OIDC_AUDIENCE": "academy-api",
        "ACADEMY_OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
        "ACADEMY_OIDC_ALGORITHMS": "RS256",
        "ACADEMY_OIDC_AUTHORIZED_PARTIES": "academy-web",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
        "ACADEMY_TRACTIAN_BEARER_TOKEN": "tractian-secret",
        "ACADEMY_PROVIDER": "groq",
        "ACADEMY_MODEL": "openai/gpt-oss-120b",
        "GROQ_API_KEY": "provider-secret",
    }


def test_hosted_config_is_production_only_and_secret_safe() -> None:
    config = HostedProductConfig.from_environment(_environment())
    assert config.provider == "groq"
    assert config.model == "openai/gpt-oss-120b"
    assert config.actions_enabled is False
    assert config.cors_origins == ("https://app.example.com",)
    summary = config.sanitized_summary()
    assert summary["deployment"] == {
        "profile": "production-hosted",
        "required_local_components": 0,
        "runtime_ddl_credential": False,
    }
    assert summary["actions"] == {"kill_switch_enabled": True}
    representation = repr(config)
    for marker in SECRET_MARKERS:
        assert marker not in representation
    assert "DEMO_MODE" not in representation


def test_hosted_actions_require_explicit_opt_in_and_default_to_kill_switch_on() -> None:
    default_config = HostedProductConfig.from_environment(_environment())
    assert default_config.actions_enabled is False

    enabled_config = HostedProductConfig.from_environment(
        {**_environment(), "ACADEMY_ACTIONS_ENABLED": "true"}
    )
    assert enabled_config.actions_enabled is True
    assert enabled_config.sanitized_summary()["actions"] == {"kill_switch_enabled": False}


def test_hosted_config_requires_oidc_remote_postgres_https_cors_and_remote_tractian() -> None:
    base = _environment()
    invalid_cases = [
        ("ACADEMY_POSTGRES_SERVICE_DSN", "postgresql://service:pw@127.0.0.1/academy"),
        ("ACADEMY_POSTGRES_SCOPED_DSN", "postgresql://scoped:pw@localhost/academy"),
        ("ACADEMY_CORS_ORIGINS", "http://app.example.com"),
        ("ACADEMY_OIDC_ISSUER", "http://identity.example.com"),
        ("ACADEMY_OIDC_JWKS_URL", "https://localhost/jwks.json"),
        ("ACADEMY_TRACTIAN_BASE_URL", "http://tractian.example.com"),
    ]
    for key, value in invalid_cases:
        env = {**base, key: value}
        with pytest.raises(ValueError):
            HostedProductConfig.from_environment(env)

    env = dict(base)
    del env["ACADEMY_OIDC_JWKS_URL"]
    with pytest.raises(ValueError, match="ACADEMY_OIDC_JWKS_URL"):
        HostedProductConfig.from_environment(env)


def test_hosted_product_has_no_demo_identity_or_runtime_migration_escape_hatch() -> None:
    source = inspect.getsource(hosted_product_module)
    forbidden = (
        "DEMO_MODE",
        "x-demo-user",
        "x-demo-organization",
        "ProviderFreeScenarioDecisionSource",
        "ProviderFreeTransport",
        "initialize_schema=True",
        "ACADEMY_POSTGRES_INTERNAL_DSN",
    )
    for marker in forbidden:
        assert marker not in source
    assert "initialize_schema=False" in source
    assert "actions_enabled=active.actions_enabled" in source
    assert "HostedActionAuthorizationResolver" in source
    assert "TenantGuardedTractianTransport" in source
    assert "hosted_action_authorization_backend = \"exact-target-revalidated-v1\"" in source
    assert "hosted_runtime_ddl_credential_present = False" in source


def test_hosted_tractian_transport_redacts_application_bearer() -> None:
    transport = HostedTractianTransport(
        base_url="https://tractian.example.com",
        bearer_token="tractian-secret",
    )
    assert "tractian-secret" not in repr(transport)
    assert "<redacted>" in repr(transport)


def test_hosted_config_rejects_symmetric_oidc_and_missing_explicit_provider_model() -> None:
    env = {**_environment(), "ACADEMY_OIDC_ALGORITHMS": "HS256"}
    with pytest.raises(ValueError, match="unsupported_oidc_algorithm"):
        HostedProductConfig.from_environment(env)

    env = _environment()
    del env["ACADEMY_MODEL"]
    with pytest.raises(ValueError, match="ACADEMY_MODEL"):
        HostedProductConfig.from_environment(env)
