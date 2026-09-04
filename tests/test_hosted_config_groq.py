from __future__ import annotations

import pytest

from academy_tractian.hosted_config import HostedProductConfig


def _groq_env(*, include_key: bool) -> dict[str, str]:
    env = {
        "ACADEMY_POSTGRES_INTERNAL_DSN": "postgresql://internal:secret@db.example.com:5432/academy",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://scoped:secret@db.example.com:5432/academy",
        "ACADEMY_CORS_ORIGINS": "https://app.example.com",
        "ACADEMY_IDENTITY_BACKEND": "oidc",
        "ACADEMY_RUNTIME_IDENTITY_ISSUER": "https://identity.example.com",
        "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": "academy-api",
        "ACADEMY_OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
        "ACADEMY_OIDC_ALGORITHMS": "RS256",
        "ACADEMY_PROVIDER": "groq",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian.example.com",
    }
    if include_key:
        env["GROQ_API_KEY"] = "groq-test-secret"
    return env


def test_groq_hosted_candidate_requires_explicit_groq_key_for_serving() -> None:
    with pytest.raises(ValueError, match="hosted_provider_api_key_missing"):
        HostedProductConfig.from_environment(
            _groq_env(include_key=False),
            require_serving_ready=True,
        )


def test_groq_hosted_candidate_is_serving_configurable_without_secret_projection() -> None:
    env = _groq_env(include_key=True)
    config = HostedProductConfig.from_environment(env, require_serving_ready=True)
    summary = config.sanitized_summary()

    assert config.provider == "groq"
    assert config.provider_api_key == "groq-test-secret"
    assert summary["provider"] == {"selection": "groq", "api_key_configured": True}
    assert "groq-test-secret" not in repr(summary)
