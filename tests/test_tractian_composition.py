from __future__ import annotations

import pytest
from fastapi import FastAPI
from pydantic import ValidationError

import academy_tractian.remote_production as remote_production
import academy_tractian.remote_server as remote_server
import academy_tractian.tractian_transport as tractian_transport
from academy_tractian.production_config import RemoteProductionConfig
from academy_tractian.release_identity import ArtifactReleaseIdentity
from academy_tractian.tractian_transport import ProductionTractianTransport


ARTIFACT_IDENTITY = ArtifactReleaseIdentity(
    schema_version="academy-release-artifact-v1",
    git_sha="d" * 40,
)


def _values() -> dict[str, object]:
    return {
        "environment": "production",
        "internal_dsn": "postgresql://internal_role@db.example.net:5432/academy?sslmode=require",
        "scoped_dsn": "postgresql://scoped_role@db.example.net:5432/academy?sslmode=require",
        "runtime_identity_secret": "x" * 40,
        "runtime_identity_issuer": "academy-production",
        "runtime_identity_audience": "academy-product",
        "public_base_url": "https://app.example.net",
        "release_git_sha": "d" * 40,
        "deployment_id": "composition-test",
        "cost_policy": "usd0-hard-gate",
        "paid_fallback_enabled": False,
        "local_serving_enabled": False,
        "provider_calls_enabled": False,
    }


def _config(**overrides: object) -> RemoteProductionConfig:
    return RemoteProductionConfig.model_validate({**_values(), **overrides})


def test_default_tractian_transport_is_unconfigured_and_fails_before_io() -> None:
    config = _config()

    transport = remote_server.build_tractian_transport(config)

    assert isinstance(transport, remote_server.NoConfiguredTractianTransport)
    assert remote_server._tractian_transport_state(config) == "UNCONFIGURED"
    with pytest.raises(RuntimeError, match="production_tractian_transport_unconfigured"):
        transport.request(object())  # type: ignore[arg-type]


def test_disabled_transport_rejects_stray_endpoint_or_headers() -> None:
    with pytest.raises(ValidationError, match="cannot be configured while"):
        _config(tractian_base_url="https://partner.example.net/api")

    with pytest.raises(ValidationError, match="cannot be configured while"):
        _config(tractian_server_headers_json='{"X-Integration-Mode":"academy"}')


def test_enabled_transport_requires_complete_remote_contract() -> None:
    with pytest.raises(ValidationError, match="enabled TRACTIAN transport requires"):
        _config(tractian_transport_enabled=True)

    with pytest.raises(ValidationError, match="TRACTIAN base URL must be a remote HTTPS"):
        _config(
            tractian_transport_enabled=True,
            tractian_base_url="http://localhost:8080/api",
            tractian_server_headers_json='{"X-Integration-Mode":"academy"}',
        )


@pytest.mark.parametrize(
    "headers_json",
    [
        "not-json",
        "[]",
        "{}",
        '{"X-Integration-Mode":""}',
        '{"X-Integration-Mode":123}',
    ],
)
def test_enabled_transport_rejects_malformed_header_contract(headers_json: str) -> None:
    with pytest.raises(ValidationError, match="TRACTIAN server headers"):
        _config(
            tractian_transport_enabled=True,
            tractian_base_url="https://partner.example.net/api",
            tractian_server_headers_json=headers_json,
        )


def test_configured_transport_build_is_zero_io_and_state_is_not_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    open_calls: list[object] = []

    class NoIoOpener:
        def open(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN201
            open_calls.append((args, kwargs))
            raise AssertionError("transport construction must not perform network I/O")

    monkeypatch.setattr(tractian_transport, "build_opener", lambda *_handlers: NoIoOpener())
    config = _config(
        tractian_transport_enabled=True,
        tractian_base_url="https://partner.example.net/api",
        tractian_server_headers_json='{"X-Integration-Mode":"academy"}',
    )

    transport = remote_server.build_tractian_transport(config)

    assert isinstance(transport, ProductionTractianTransport)
    assert remote_server._tractian_transport_state(config) == "CONFIGURED_UNVERIFIED"
    assert open_calls == []
    assert config.provider_calls_enabled is False


def test_server_header_payload_is_secret_in_config_and_absent_from_public_metadata() -> None:
    marker = "opaque-marker-value"
    config = _config(
        tractian_transport_enabled=True,
        tractian_base_url="https://partner.example.net/api",
        tractian_server_headers_json=(
            '{"X-Integration-Mode":"academy","X-Opaque-Marker":"' + marker + '"}'
        ),
    )

    assert marker not in repr(config)
    assert marker not in repr(config.model_dump())
    assert marker not in repr(config.safe_metadata())
    assert "tractian_base_url" not in config.safe_metadata()
    assert "tractian_server_headers_json" not in config.safe_metadata()


def test_remote_app_rejects_false_tractian_state_before_delegate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_builder(**_kwargs):
        nonlocal called
        called = True
        return FastAPI()

    monkeypatch.setattr(
        remote_production,
        "create_authenticated_postgres_action_capable_product_app",
        fake_builder,
    )

    with pytest.raises(RuntimeError, match="tractian_transport_state_config_mismatch"):
        remote_production.create_remote_production_app(
            config=_config(),
            artifact_release_identity=ARTIFACT_IDENTITY,
            decision_source_factory=lambda: object(),
            transport_factory=lambda: object(),
            authorization_resolver=lambda **_: object(),
            tractian_transport_state="CONFIGURED_UNVERIFIED",
        )

    assert called is False


def test_configured_tractian_state_does_not_promote_provider_or_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config(
        tractian_transport_enabled=True,
        tractian_base_url="https://partner.example.net/api",
        tractian_server_headers_json='{"X-Integration-Mode":"academy"}',
    )
    captured: dict[str, object] = {}

    monkeypatch.setattr(remote_server, "load_remote_production_config", lambda: config)
    monkeypatch.setattr(
        remote_server,
        "load_artifact_release_identity",
        lambda: ARTIFACT_IDENTITY,
    )

    def fake_create_remote_production_app(**kwargs):
        captured.update(kwargs)
        app = FastAPI()
        app.state.tractian_transport_state = kwargs["tractian_transport_state"]
        return app

    monkeypatch.setattr(
        remote_server,
        "create_remote_production_app",
        fake_create_remote_production_app,
    )

    app = remote_server.app_factory()

    assert captured["tractian_transport_state"] == "CONFIGURED_UNVERIFIED"
    assert captured["decision_source_factory"] is remote_server.NoSelectedProviderDecisionSource
    assert captured["authorization_resolver"] is remote_server.deny_production_action_principal
    assert callable(captured["transport_factory"])
    assert isinstance(captured["transport_factory"](), ProductionTractianTransport)  # type: ignore[operator]
    assert app.state.provider_selection_state == "NO_SELECTION"
    assert app.state.tractian_transport_state == "CONFIGURED_UNVERIFIED"
    assert config.provider_calls_enabled is False
    with pytest.raises(PermissionError, match="production_actions_not_enabled"):
        remote_server.deny_production_action_principal(user_id="user-a")
