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


def _oidc_env() -> dict[str, str]:
    env = _base_env()
    env.pop("ACADEMY_RUNTIME_IDENTITY_SECRET")
    env.update(
        {
            "ACADEMY_IDENTITY_BACKEND": "oidc",
            "ACADEMY_RUNTIME_IDENTITY_ISSUER": "https://identity.example.com",
            "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": "academy-api",
            "ACADEMY_OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
            "ACADEMY_OIDC_ALGORITHMS": "RS256, ES256,RS256",
            "ACADEMY_OIDC_AUTHORIZED_PARTIES": "https://app.example.com,academy-mobile",
        }
    )
    return env


def _serving_env() -> dict[str, str]:
    return {
        **_oidc_env(),
        "ACADEMY_PROVIDER": "openai",
        "ACADEMY_MODEL": "gpt-5.6-sol",
        "OPENAI_API_KEY": "test-provider-key",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
    }


def _cloudflare_serving_env() -> dict[str, str]:
    return {
        **_oidc_env(),
        "ACADEMY_PROVIDER": "cloudflare",
        "ACADEMY_MODEL": "@cf/nvidia/nemotron-3-120b-a12b",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare-token",
        "CLOUDFLARE_ACCOUNT_ID": "account123",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
    }


def test_hosted_config_allows_infrastructure_validation_before_provider_selection() -> None:
    env = _base_env()
    config = HostedProductConfig.from_environment(env)
    summary = config.sanitized_summary()

    assert config.provider is None
    assert config.model is None
    assert config.identity_backend == "signed_bearer"
    assert summary["provider"] == {
        "selection": "NO_SELECTION",
        "model": "NO_SELECTION",
        "candidate_id": "NO_SELECTION",
        "api_key_configured": False,
    }
    assert summary["deployment"] == {
        "contract_profile": "hosted-only-v1",
        "required_local_components": 0,
        "production_identity": "oidc-jwks-v1",
    }
    assert summary["persistence"]["operational"] == "postgresql"  # type: ignore[index]
    assert summary["persistence"]["observability"] == "postgresql"  # type: ignore[index]
    rendered = repr(summary)
    assert env["ACADEMY_POSTGRES_INTERNAL_DSN"] not in rendered
    assert env["ACADEMY_POSTGRES_SCOPED_DSN"] not in rendered
    assert env["ACADEMY_RUNTIME_IDENTITY_SECRET"] not in rendered


def test_hosted_config_accepts_provider_neutral_oidc_without_application_signing_secret() -> None:
    env = _oidc_env()
    config = HostedProductConfig.from_environment(env)
    summary = config.sanitized_summary()

    assert config.identity_backend == "oidc"
    assert config.runtime_identity_secret is None
    assert config.oidc_algorithms == ("RS256", "ES256")
    assert summary["identity"] == {
        "backend": "oidc-jwks-v1",
        "issuer": "https://identity.example.com",
        "audience": "academy-api",
        "jwks_url_configured": True,
        "algorithms": ["RS256", "ES256"],
        "organization_claim": "organization_id",
        "role_claim": "role",
        "permissions_claim": "permissions",
        "identity_claim": "sid",
        "authorized_parties": ["https://app.example.com", "academy-mobile"],
    }
    assert env["ACADEMY_OIDC_JWKS_URL"] not in repr(summary)


def test_hosted_config_requires_provider_model_and_tractian_endpoint_for_serving() -> None:
    with pytest.raises(ValueError, match="hosted_provider_not_selected"):
        HostedProductConfig.from_environment(_oidc_env(), require_serving_ready=True)

    provider_only = {
        **_oidc_env(),
        "ACADEMY_PROVIDER": "openai",
        "OPENAI_API_KEY": "test-provider-key",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
    }
    with pytest.raises(ValueError, match="hosted_model_not_selected"):
        HostedProductConfig.from_environment(provider_only, require_serving_ready=True)

    candidate = {
        **_oidc_env(),
        "ACADEMY_PROVIDER": "openai",
        "ACADEMY_MODEL": "gpt-5.6-sol",
        "OPENAI_API_KEY": "test-provider-key",
    }
    with pytest.raises(ValueError, match="tractian_base_url_missing"):
        HostedProductConfig.from_environment(candidate, require_serving_ready=True)

    ready = HostedProductConfig.from_environment(_serving_env(), require_serving_ready=True)
    assert ready.provider == "openai"
    assert ready.model == "gpt-5.6-sol"
    assert ready.sanitized_summary()["provider"] == {
        "selection": "openai",
        "model": "gpt-5.6-sol",
        "candidate_id": "openai:gpt-5.6-sol",
        "api_key_configured": True,
    }
    assert "test-provider-key" not in repr(ready.sanitized_summary())


def test_cloudflare_hosted_config_requires_account_id_and_never_exposes_it() -> None:
    env = _cloudflare_serving_env()
    missing_account = dict(env)
    missing_account.pop("CLOUDFLARE_ACCOUNT_ID")
    with pytest.raises(ValueError, match="cloudflare_account_id_required"):
        HostedProductConfig.from_environment(missing_account, require_serving_ready=True)

    ready = HostedProductConfig.from_environment(env, require_serving_ready=True)
    assert ready.provider_account_id == "account123"
    assert ready.sanitized_summary()["provider"] == {
        "selection": "cloudflare",
        "model": "@cf/nvidia/nemotron-3-120b-a12b",
        "candidate_id": "cloudflare:@cf/nvidia/nemotron-3-120b-a12b",
        "api_key_configured": True,
        "account_id_configured": True,
    }
    rendered = repr(ready.sanitized_summary())
    assert env["CLOUDFLARE_API_TOKEN"] not in rendered
    assert env["CLOUDFLARE_ACCOUNT_ID"] not in rendered


def test_hosted_config_rejects_model_without_provider_or_invalid_pair() -> None:
    with pytest.raises(ValueError, match="hosted_model_without_provider"):
        HostedProductConfig.from_environment(
            {**_oidc_env(), "ACADEMY_MODEL": "gemini-3.8-flash"}
        )

    with pytest.raises(ValueError, match="unsupported_hosted_candidate"):
        HostedProductConfig.from_environment(
            {
                **_oidc_env(),
                "ACADEMY_PROVIDER": "google",
                "ACADEMY_MODEL": "gpt-5.6-sol",
            }
        )


def test_signed_bearer_remains_regression_only_and_cannot_claim_hosted_production_ready() -> None:
    env = {
        **_base_env(),
        "ACADEMY_PROVIDER": "openai",
        "ACADEMY_MODEL": "gpt-5.6-sol",
        "OPENAI_API_KEY": "test-provider-key",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
    }
    with pytest.raises(ValueError, match="hosted_production_requires_oidc"):
        HostedProductConfig.from_environment(env, require_serving_ready=True)


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

    with pytest.raises(ValueError, match="unsupported_identity_backend"):
        HostedProductConfig.from_environment({**env, "ACADEMY_IDENTITY_BACKEND": "browser_headers"})


@pytest.mark.parametrize(
    ("environment_name", "local_value"),
    [
        (
            "ACADEMY_POSTGRES_INTERNAL_DSN",
            "postgresql://internal:secret@localhost:5432/academy",
        ),
        (
            "ACADEMY_POSTGRES_SCOPED_DSN",
            "postgresql://scoped:secret@127.0.0.1:5432/academy",
        ),
        ("ACADEMY_RUNTIME_IDENTITY_ISSUER", "https://localhost"),
        ("ACADEMY_OIDC_JWKS_URL", "https://127.0.0.1/.well-known/jwks.json"),
        ("ACADEMY_CORS_ORIGINS", "https://localhost"),
        ("ACADEMY_TRACTIAN_BASE_URL", "https://[::1]"),
    ],
)
def test_serving_ready_rejects_local_machine_dependencies(
    environment_name: str,
    local_value: str,
) -> None:
    env = _serving_env()
    env[environment_name] = local_value
    with pytest.raises(ValueError, match=f"local_endpoint_forbidden:{environment_name}"):
        HostedProductConfig.from_environment(env, require_serving_ready=True)


def test_serving_ready_requires_https_oidc_issuer() -> None:
    env = _serving_env()
    env["ACADEMY_RUNTIME_IDENTITY_ISSUER"] = "http://identity.example.com"
    with pytest.raises(ValueError, match="invalid_http_url:ACADEMY_RUNTIME_IDENTITY_ISSUER"):
        HostedProductConfig.from_environment(env, require_serving_ready=True)


def test_hosted_config_rejects_incomplete_or_symmetric_oidc_configuration() -> None:
    env = _oidc_env()
    env.pop("ACADEMY_OIDC_JWKS_URL")
    with pytest.raises(ValueError, match="ACADEMY_OIDC_JWKS_URL"):
        HostedProductConfig.from_environment(env)

    env = _oidc_env()
    env["ACADEMY_OIDC_ALGORITHMS"] = ""
    with pytest.raises(ValueError, match="ACADEMY_OIDC_ALGORITHMS"):
        HostedProductConfig.from_environment(env)

    env = _oidc_env()
    env["ACADEMY_OIDC_ALGORITHMS"] = "HS256"
    with pytest.raises(ValueError, match="unsupported_oidc_algorithm"):
        HostedProductConfig.from_environment(env)


def test_hosted_config_rejects_short_identity_secret_and_invalid_runtime_bounds() -> None:
    env = _base_env()
    with pytest.raises(ValueError, match="runtime_identity_secret_too_short"):
        HostedProductConfig.from_environment({**env, "ACADEMY_RUNTIME_IDENTITY_SECRET": "short"})

    with pytest.raises(ValueError, match="ACADEMY_MAX_WORKERS_exceeds_64"):
        HostedProductConfig.from_environment({**env, "ACADEMY_MAX_WORKERS": "65"})

    with pytest.raises(ValueError, match="ACADEMY_HEARTBEAT_INTERVAL_MS_out_of_range"):
        HostedProductConfig.from_environment({**env, "ACADEMY_HEARTBEAT_INTERVAL_MS": "100"})
