from __future__ import annotations

import pytest
from fastapi import FastAPI

import academy_tractian.remote_server as remote_server
from academy_tractian.production_config import RemoteProductionConfig


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


def test_infrastructure_probe_uses_provider_closed_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(remote_server, "load_remote_production_config", lambda: CONFIG)

    def fake_create_remote_production_app(**kwargs):
        captured.update(kwargs)
        return FastAPI()

    monkeypatch.setattr(
        remote_server,
        "create_remote_production_app",
        fake_create_remote_production_app,
    )

    app = remote_server.app_factory()

    assert captured["decision_source_factory"] is remote_server.NoSelectedProviderDecisionSource
    assert captured["transport_factory"] is remote_server.NoSelectedProviderTransport
    assert captured["authorization_resolver"] is remote_server.deny_production_action_principal
    assert app.state.provider_selection_state == "NO_SELECTION"
    assert app.state.infrastructure_probe is True


def test_infrastructure_probe_refuses_provider_enablement_before_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enabled = CONFIG.model_copy(update={"provider_calls_enabled": True})
    monkeypatch.setattr(remote_server, "load_remote_production_config", lambda: enabled)

    with pytest.raises(RuntimeError, match="NO_SELECTION"):
        remote_server.app_factory()


def test_no_selected_provider_dependencies_fail_if_called() -> None:
    with pytest.raises(RuntimeError, match="production_provider_not_selected"):
        remote_server.NoSelectedProviderDecisionSource().decide(object())  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="production_provider_not_selected"):
        remote_server.NoSelectedProviderTransport().request(object())  # type: ignore[arg-type]

    with pytest.raises(PermissionError, match="production_actions_not_enabled"):
        remote_server.deny_production_action_principal(user_id="user-a")
