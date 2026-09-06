from __future__ import annotations

import pytest
from fastapi import FastAPI
from pydantic import SecretStr

import academy_tractian.remote_server as remote_server
from academy_tractian.decision_source import ProviderDecisionSource
from academy_tractian.production_config import RemoteProductionConfig
from academy_tractian.release_identity import ArtifactReleaseIdentity


CONFIG = RemoteProductionConfig.model_validate(
    {
        "environment": "production",
        "internal_dsn": "postgresql://internal:secret@db.example.net:5432/academy?sslmode=require",
        "scoped_dsn": "postgresql://scoped:secret@db.example.net:5432/academy?sslmode=require",
        "runtime_identity_secret": "runtime-identity-secret-with-more-than-32-bytes",
        "runtime_identity_issuer": "academy-production",
        "runtime_identity_audience": "academy-product",
        "public_base_url": "https://203.0.113.10",
        "release_git_sha": "b" * 40,
        "deployment_id": "deploy-test",
        "cost_policy": "usd0-hard-gate",
        "paid_fallback_enabled": False,
        "local_serving_enabled": False,
        "provider_calls_enabled": False,
    }
)
ARTIFACT_IDENTITY = ArtifactReleaseIdentity(
    schema_version="academy-release-artifact-v1",
    git_sha="b" * 40,
)


def _release_provider_config() -> RemoteProductionConfig:
    return CONFIG.model_copy(
        update={
            "provider_calls_enabled": True,
            "provider_selection_state": "PROVISIONAL_RELEASE_PROVIDER",
            "provider_id": "cloudflare",
            "provider_model_id": "@cf/zai-org/glm-4.7-flash",
            "provider_account_id": "abc123",
            "provider_api_token": SecretStr("release-provider-secret"),
            "tractian_transport_enabled": True,
            "tractian_base_url": "https://tractian.example.net",
            "tractian_server_headers_json": SecretStr('{"x-api-key":"server-secret"}'),
        }
    )


def test_infrastructure_probe_uses_provider_closed_dependencies_and_baked_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(remote_server, "load_remote_production_config", lambda: CONFIG)
    monkeypatch.setattr(
        remote_server,
        "load_artifact_release_identity",
        lambda: ARTIFACT_IDENTITY,
    )

    def fake_create_remote_production_app(**kwargs):
        captured.update(kwargs)
        return FastAPI()

    monkeypatch.setattr(
        remote_server,
        "create_remote_production_app",
        fake_create_remote_production_app,
    )

    app = remote_server.app_factory()

    assert captured["artifact_release_identity"] == ARTIFACT_IDENTITY
    assert captured["decision_source_factory"] is remote_server.NoSelectedProviderDecisionSource
    assert captured["transport_factory"] is remote_server.NoSelectedProviderTransport
    assert captured["authorization_resolver"] is remote_server.deny_production_action_principal
    assert app.state.provider_selection_state == "NO_SELECTION"
    assert app.state.infrastructure_probe is True
    assert app.state.release0_read_only is False


def test_release_provider_enablement_requires_real_tractian_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enabled_without_tractian = CONFIG.model_copy(
        update={
            "provider_calls_enabled": True,
            "provider_selection_state": "PROVISIONAL_RELEASE_PROVIDER",
            "provider_id": "cloudflare",
            "provider_model_id": "@cf/zai-org/glm-4.7-flash",
            "provider_account_id": "abc123",
            "provider_api_token": SecretStr("release-provider-secret"),
        }
    )
    monkeypatch.setattr(
        remote_server,
        "load_remote_production_config",
        lambda: enabled_without_tractian,
    )
    monkeypatch.setattr(
        remote_server,
        "load_artifact_release_identity",
        lambda: ARTIFACT_IDENTITY,
    )

    with pytest.raises(RuntimeError, match="requires_real_tractian_transport"):
        remote_server.app_factory()


def test_release_provider_is_composed_without_enabling_actions_or_boot_time_provider_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    config = _release_provider_config()

    monkeypatch.setattr(remote_server, "load_remote_production_config", lambda: config)
    monkeypatch.setattr(
        remote_server,
        "load_artifact_release_identity",
        lambda: ARTIFACT_IDENTITY,
    )

    def fake_create_remote_production_app(**kwargs):
        captured.update(kwargs)
        return FastAPI()

    monkeypatch.setattr(
        remote_server,
        "create_remote_production_app",
        fake_create_remote_production_app,
    )

    app = remote_server.app_factory()

    factory = captured["decision_source_factory"]
    assert callable(factory)
    source = factory()  # type: ignore[operator]
    assert isinstance(source, ProviderDecisionSource)
    assert captured["authorization_resolver"] is remote_server.deny_production_action_principal
    assert captured["tractian_transport_state"] == "CONFIGURED_UNVERIFIED"
    assert app.state.provider_selection_state == "PROVISIONAL_RELEASE_PROVIDER"
    assert app.state.infrastructure_probe is False
    assert app.state.release0_read_only is True


def test_no_selected_provider_dependencies_fail_if_called() -> None:
    with pytest.raises(RuntimeError, match="production_provider_not_selected"):
        remote_server.NoSelectedProviderDecisionSource().decide(object())  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="production_provider_not_selected"):
        remote_server.NoSelectedProviderTransport().request(object())  # type: ignore[arg-type]

    with pytest.raises(PermissionError, match="production_actions_not_enabled"):
        remote_server.deny_production_action_principal(user_id="user-a")
