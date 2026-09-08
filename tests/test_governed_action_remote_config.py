from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from academy_tractian.production_config import RemoteProductionConfig


BASE_ENV = {
    "ACADEMY_ENVIRONMENT": "production",
    "ACADEMY_POSTGRES_INTERNAL_DSN": "postgresql://academy_internal:internal-password@db.academy-cloud.net:5432/academy?sslmode=require",
    "ACADEMY_POSTGRES_SCOPED_DSN": "postgresql://academy_scoped:scoped-password@db.academy-cloud.net:5432/academy?sslmode=require",
    "ACADEMY_RUNTIME_IDENTITY_SECRET": "runtime-identity-secret-with-more-than-32-bytes",
    "ACADEMY_RUNTIME_IDENTITY_ISSUER": "academy-production",
    "ACADEMY_RUNTIME_IDENTITY_AUDIENCE": "academy-product",
    "ACADEMY_PUBLIC_BASE_URL": "https://app.academy-cloud.net",
    "ACADEMY_RELEASE_GIT_SHA": "a" * 40,
    "ACADEMY_DEPLOYMENT_ID": "deploy-governed-actions",
    "ACADEMY_COST_POLICY": "usd0-hard-gate",
    "ACADEMY_PAID_FALLBACK_ENABLED": "false",
    "ACADEMY_LOCAL_SERVING_ENABLED": "false",
}


def _grant_json() -> str:
    return json.dumps(
        [
            {
                "user_id": "user-1",
                "organization_id": "org-1",
                "user_company_id": "company-1",
                "permissions": ["action_low", "action_high", "escalate"],
                "resource_company_bindings": [
                    {"resource_id": "asset-1", "company_id": "company-1"},
                    {"resource_id": "analysis-1", "company_id": "company-1"},
                    {"resource_id": "model-1", "company_id": "company-1"},
                    {"resource_id": "case-1", "company_id": "company-1"},
                ],
                "policy_revision": "governed-execute-v1",
                "active": True,
                "source_owned": True,
            }
        ]
    )


def _fully_enabled_env() -> dict[str, str]:
    return {
        **BASE_ENV,
        "ACADEMY_PROVIDER_CALLS_ENABLED": "true",
        "ACADEMY_PROVIDER_SELECTION_STATE": "PROVISIONAL_RELEASE_PROVIDER",
        "ACADEMY_PROVIDER_ID": "cloudflare",
        "ACADEMY_PROVIDER_MODEL_ID": "release-model",
        "ACADEMY_PROVIDER_ACCOUNT_ID": "account123",
        "ACADEMY_PROVIDER_API_TOKEN": "server-provider-token",
        "ACADEMY_TRACTIAN_TRANSPORT_ENABLED": "true",
        "ACADEMY_TRACTIAN_BASE_URL": "https://tractian-api.example.net",
        "ACADEMY_TRACTIAN_SERVER_HEADERS_JSON": json.dumps({"Authorization": "Bearer server-token"}),
        "ACADEMY_ACTIONS_ENABLED": "true",
        "ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON": _grant_json(),
    }


def test_actions_are_disabled_by_default() -> None:
    config = RemoteProductionConfig.from_env(
        {**BASE_ENV, "ACADEMY_PROVIDER_CALLS_ENABLED": "false"}
    )
    assert config.actions_enabled is False
    assert config.action_authorization_grants_json is None


def test_fully_configured_governed_action_path_is_accepted_without_exposing_grants() -> None:
    config = RemoteProductionConfig.from_env(_fully_enabled_env())

    assert config.actions_enabled is True
    assert config.provider_calls_enabled is True
    assert config.tractian_transport_enabled is True
    assert config.action_authorization_grants_json is not None
    metadata = config.safe_metadata()
    assert metadata["actions_enabled"] is True
    rendered = repr(metadata)
    assert "user-1" not in rendered
    assert "asset-1" not in rendered
    assert "server-token" not in rendered
    assert "server-provider-token" not in rendered


def test_action_switch_alone_cannot_open_execution() -> None:
    with pytest.raises((ValidationError, ValueError), match="provider"):
        RemoteProductionConfig.from_env(
            {
                **BASE_ENV,
                "ACADEMY_PROVIDER_CALLS_ENABLED": "false",
                "ACADEMY_ACTIONS_ENABLED": "true",
                "ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON": _grant_json(),
            }
        )


def test_actions_require_tractian_transport_even_with_provider_and_grants() -> None:
    env = _fully_enabled_env()
    env["ACADEMY_TRACTIAN_TRANSPORT_ENABLED"] = "false"
    env.pop("ACADEMY_TRACTIAN_BASE_URL")
    env.pop("ACADEMY_TRACTIAN_SERVER_HEADERS_JSON")
    with pytest.raises(ValidationError, match="TRACTIAN transport"):
        RemoteProductionConfig.from_env(env)


def test_actions_require_server_owned_grants() -> None:
    env = _fully_enabled_env()
    env.pop("ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON")
    with pytest.raises(ValueError, match="ACADEMY_ACTION_AUTHORIZATION_GRANTS_JSON"):
        RemoteProductionConfig.from_env(env)


def test_dormant_grants_are_rejected_when_action_switch_is_off() -> None:
    env = _fully_enabled_env()
    env["ACADEMY_ACTIONS_ENABLED"] = "false"
    with pytest.raises(ValidationError, match="grants cannot be configured"):
        RemoteProductionConfig.from_env(env)
