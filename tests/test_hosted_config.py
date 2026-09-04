from __future__ import annotations

import pytest

from academy_tractian.hosted_config import HostedProductConfig


def _base_env() -> dict[str, str]:
    return {
        "ACADEMY_POSTGRES_INTERNAL_DSN": "postgresql://internal:secret@db.example.com:5432/academy",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://scoped:secret@db.example.com:5432/academy",
        "ACADEMY_RUNTIME_IDENTITY_SECRET": "x" * 40,
        "ACADEMY_RUNTIME_IDENTITY_ISSUER": "academy-hosted",
        "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": "academy-product",
        "ACADEMY_CORS_ORIGINS": "https://app.example.com, https://review.example.com/",
    }


def test_hosted_config_allows_infrastructure_validation_before_provider_selection() -> None:
    env = _base_env()
    config = HostedProductConfig.from_environment(env)
    summary = config.sanitized_summary()

    assert config.provider is None
    assert summary["provider"] == {
        "selection": "NO_SELECTION",
        "api_key_configured": False,
    }
    assert summary["persistence"]["operational"] == "postgresql"  # type: ignore[index]
    assert summary["persistence"]["observability"] == "postgresql"  # type: ignore[index]
    rendered = repr(summary)
    assert env["ACADEMY_POSTGRES_INTERNAL_DSN"] not in rendered
    assert env["ACADEMY_POSTGRES_SCOPED_DSN"] not in rendered
    assert env["ACADEMY_RUNTIME_IDENTITY_SECRET"] not in rendered


def test_hosted_config_requires_provider_and_tractian_endpoint_for_serving() -> None:
    with pytest.raises(ValueError, match="hosted_provider_not_selected"):
        HostedProductConfig.from_environment(_base_env(), require_serving_ready=True)

    env = {
        **_base_env(),
        "ACADEMY_PROVIDER": "openai",
        "OPENAI_API_KEY": "test-provider-key",
    }
    with pytest.raises(ValueError, match="tractian_base_url_missing"):
        HostedProductConfig.from_environment(env, require_serving_ready=True)

    ready = HostedProductConfig.from_environment(
        {**env, "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com"},
        require_serving_ready=True,
    )
    assert ready.provider == "openai"
    assert "test-provider-key" not in repr(ready.sanitized_summary())


def test_hosted_config_rejects_unsafe_or_ambiguous_network_configuration() -> None:
    env = _base_env()
    with pytest.raises(ValueError, match="invalid_cors_origin"):
        HostedProductConfig.from_environment({**env, "ACADEMY_CORS_ORIGINS": "http://app.example.com"})

    with pytest.raises(ValueError, match="url_credentials_forbidden"):
        HostedProductConfig.from_environment(
            {**env, "ACADEMY_TRACTIAN_BASE_URL": "https://user:pass@tractian.example.com"}
        )

    with pytest.raises(ValueError, match="unsupported_hosted_provider"):
        HostedProductConfig.from_environment({**env, "ACADEMY_PROVIDER": "local-ollama"})


def test_hosted_config_rejects_short_identity_secret_and_invalid_runtime_bounds() -> None:
    env = _base_env()
    with pytest.raises(ValueError, match="runtime_identity_secret_too_short"):
        HostedProductConfig.from_environment({**env, "ACADEMY_RUNTIME_IDENTITY_SECRET": "short"})

    with pytest.raises(ValueError, match="ACADEMY_MAX_WORKERS_exceeds_64"):
        HostedProductConfig.from_environment({**env, "ACADEMY_MAX_WORKERS": "65"})

    with pytest.raises(ValueError, match="ACADEMY_HEARTBEAT_INTERVAL_MS_out_of_range"):
        HostedProductConfig.from_environment({**env, "ACADEMY_HEARTBEAT_INTERVAL_MS": "100"})
