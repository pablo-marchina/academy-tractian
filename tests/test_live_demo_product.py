from __future__ import annotations

import pytest

from academy_tractian.decision_source import ProviderDecisionSource
from academy_tractian.live_demo_product import (
    LiveDemoConfig,
    LiveDemoConfigurationError,
    LiveDemoHttpTransport,
    _decision_source_factory,
)
from academy_tractian.provider_free_product import ProviderFreeScenarioDecisionSource


def _base_env() -> dict[str, str]:
    return {
        "DEMO_MODE": "fallback",
        "ACADEMY_POSTGRES_INTERNAL_DSN": "postgresql://owner:secret@db.example.com:5432/academy",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://scoped:secret@pooler.example.com:5432/academy",
    }


def test_fallback_config_is_remote_fail_closed_and_secret_safe() -> None:
    config = LiveDemoConfig.from_env(_base_env())

    assert config.mode == "fallback"
    assert config.provider is None
    assert config.actions_enabled is False
    assert config.host == "0.0.0.0"
    assert config.port == 8000
    representation = repr(config)
    assert "owner:secret" not in representation
    assert "scoped:secret" not in representation
    assert "<redacted>" in representation
    assert _decision_source_factory(config) is ProviderFreeScenarioDecisionSource


def test_railway_port_wins_over_academy_port() -> None:
    config = LiveDemoConfig.from_env(
        {**_base_env(), "PORT": "9123", "ACADEMY_PORT": "8123"}
    )
    assert config.port == 9123


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("ACADEMY_POSTGRES_INTERNAL_DSN", "postgresql://owner:secret@127.0.0.1/db"),
        ("ACADEMY_POSTGRES_SCOPED_DSN", "postgresql://scoped:secret@localhost/db"),
    ],
)
def test_hosted_config_rejects_local_postgres(name: str, value: str) -> None:
    env = _base_env()
    env[name] = value
    with pytest.raises(LiveDemoConfigurationError, match=f"localhost_forbidden:{name}"):
        LiveDemoConfig.from_env(env)


def test_live_google_requires_key_and_public_tractian_url() -> None:
    env = {
        **_base_env(),
        "DEMO_MODE": "live",
        "LIVE_DEMO_PROVIDER": "google",
        "GOOGLE_API_KEY": "demo-google-secret",
        "TRACTIAN_API_BASE_URL": "https://tractian-sandbox.example.com",
        "ACADEMY_FRONTEND_ORIGINS": "https://demo.example.app",
    }
    config = LiveDemoConfig.from_env(env)

    assert config.mode == "live"
    assert config.provider == "google"
    assert config.provider_api_key == "demo-google-secret"
    assert config.tractian_base_url == "https://tractian-sandbox.example.com"
    assert config.frontend_origins == ("https://demo.example.app",)
    source = _decision_source_factory(config)()
    assert isinstance(source, ProviderDecisionSource)
    assert source.call_identity is not None
    assert source.call_identity.live_call is True
    assert source.call_identity.provider_id == "google"
    assert "demo-google-secret" not in repr(config)


def test_live_mode_requires_provider_secret_and_tractian_base_url() -> None:
    env = {**_base_env(), "DEMO_MODE": "live", "LIVE_DEMO_PROVIDER": "google"}
    with pytest.raises(LiveDemoConfigurationError, match="GOOGLE_API_KEY"):
        LiveDemoConfig.from_env(env)

    env["GOOGLE_API_KEY"] = "secret"
    with pytest.raises(LiveDemoConfigurationError, match="TRACTIAN_API_BASE_URL"):
        LiveDemoConfig.from_env(env)


def test_live_mode_rejects_local_tractian_and_frontend_urls() -> None:
    env = {
        **_base_env(),
        "DEMO_MODE": "live",
        "LIVE_DEMO_PROVIDER": "google",
        "GOOGLE_API_KEY": "secret",
        "TRACTIAN_API_BASE_URL": "http://localhost:9000",
    }
    with pytest.raises(
        LiveDemoConfigurationError,
        match="localhost_forbidden:TRACTIAN_API_BASE_URL",
    ):
        LiveDemoConfig.from_env(env)

    env["TRACTIAN_API_BASE_URL"] = "https://tractian.example.com"
    env["ACADEMY_FRONTEND_ORIGINS"] = "http://127.0.0.1:5173"
    with pytest.raises(
        LiveDemoConfigurationError,
        match="localhost_forbidden:ACADEMY_FRONTEND_ORIGINS",
    ):
        LiveDemoConfig.from_env(env)


def test_invalid_modes_booleans_and_ports_fail_closed() -> None:
    with pytest.raises(LiveDemoConfigurationError, match="invalid_demo_mode"):
        LiveDemoConfig.from_env({**_base_env(), "DEMO_MODE": "automatic"})
    with pytest.raises(LiveDemoConfigurationError, match="invalid_boolean:DEMO_ACTIONS_ENABLED"):
        LiveDemoConfig.from_env({**_base_env(), "DEMO_ACTIONS_ENABLED": "sometimes"})
    with pytest.raises(LiveDemoConfigurationError, match="invalid_port"):
        LiveDemoConfig.from_env({**_base_env(), "PORT": "99999"})


def test_tool_transport_repr_never_discloses_bearer_token() -> None:
    transport = LiveDemoHttpTransport(
        base_url="https://tractian.example.com",
        bearer_token="tractian-secret-token",
    )
    assert "tractian-secret-token" not in repr(transport)
    assert "<redacted>" in repr(transport)
