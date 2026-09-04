from __future__ import annotations

from academy_tractian.hosted_config import HostedProductConfig
from academy_tractian.hosted_product import _runtime_context_provider
from academy_tractian.oidc_runtime_identity import OIDCRuntimeContextProvider
from academy_tractian.runtime_identity import SignedBearerRuntimeContextProvider


def _shared() -> dict[str, str]:
    return {
        "ACADEMY_POSTGRES_INTERNAL_DSN": "postgresql://internal:secret@db.example.com:5432/academy",
        "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://scoped:secret@db.example.com:5432/academy",
        "ACADEMY_RUNTIME_IDENTITY_ISSUER": "academy-hosted",
        "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": "academy-api",
        "ACADEMY_CORS_ORIGINS": "https://app.example.com",
    }


def test_hosted_identity_factory_preserves_signed_bearer_regression_backend() -> None:
    config = HostedProductConfig.from_environment(
        {**_shared(), "ACADEMY_RUNTIME_IDENTITY_SECRET": "x" * 40}
    )
    provider = _runtime_context_provider(config)
    assert isinstance(provider, SignedBearerRuntimeContextProvider)


def test_hosted_identity_factory_promotes_provider_neutral_oidc_without_fetching_jwks_at_startup() -> None:
    config = HostedProductConfig.from_environment(
        {
            **_shared(),
            "ACADEMY_IDENTITY_BACKEND": "oidc",
            "ACADEMY_RUNTIME_IDENTITY_ISSUER": "https://identity.example.com",
            "ACADEMY_OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
            "ACADEMY_OIDC_ALGORITHMS": "RS256",
            "ACADEMY_OIDC_AUTHORIZED_PARTIES": "https://app.example.com",
        }
    )
    provider = _runtime_context_provider(config)
    assert isinstance(provider, OIDCRuntimeContextProvider)
