from __future__ import annotations

from types import SimpleNamespace

from academy_tractian import remote_server
from academy_tractian.release_provider_v15 import NVIDIA_PROVIDER_ID


def test_decision_source_factory_routes_nvidia_only_to_v15(monkeypatch) -> None:
    config = SimpleNamespace(provider_calls_enabled=True, provider_id=NVIDIA_PROVIDER_ID)
    sentinel = object()
    calls: list[str] = []

    monkeypatch.setattr(
        remote_server,
        "validate_release_provider_config_v15",
        lambda _config: calls.append("validate-v15"),
    )
    monkeypatch.setattr(
        remote_server,
        "build_release_provider_decision_source_factory_v15",
        lambda _config: sentinel,
    )
    monkeypatch.setattr(
        remote_server,
        "validate_release_provider_config_v14",
        lambda _config: calls.append("validate-v14"),
    )
    monkeypatch.setattr(
        remote_server,
        "build_release_provider_decision_source_factory_v14",
        lambda _config: (_ for _ in ()).throw(AssertionError("V14 must not build NVIDIA")),
    )

    assert remote_server._decision_source_factory(config) is sentinel
    assert calls == ["validate-v15"]


def test_decision_source_factory_preserves_existing_v14_path(monkeypatch) -> None:
    config = SimpleNamespace(provider_calls_enabled=True, provider_id="openrouter")
    sentinel = object()
    calls: list[str] = []

    monkeypatch.setattr(
        remote_server,
        "validate_release_provider_config_v14",
        lambda _config: calls.append("validate-v14"),
    )
    monkeypatch.setattr(
        remote_server,
        "build_release_provider_decision_source_factory_v14",
        lambda _config: sentinel,
    )
    monkeypatch.setattr(
        remote_server,
        "validate_release_provider_config_v15",
        lambda _config: (_ for _ in ()).throw(AssertionError("V15 must not validate V14 providers")),
    )

    assert remote_server._decision_source_factory(config) is sentinel
    assert calls == ["validate-v14"]


def test_decision_source_factory_still_fails_closed_when_provider_calls_disabled() -> None:
    config = SimpleNamespace(provider_calls_enabled=False, provider_id=None)

    assert remote_server._decision_source_factory(config) is remote_server.NoSelectedProviderDecisionSource
