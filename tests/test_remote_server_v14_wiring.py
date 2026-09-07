from __future__ import annotations

from typing import cast

import academy_tractian.remote_server as remote_server
from academy_tractian.production_config import RemoteProductionConfig


class _ProviderEnabledConfig:
    provider_calls_enabled = True


def test_remote_decision_source_factory_uses_v14_builder(monkeypatch) -> None:
    config = cast(RemoteProductionConfig, _ProviderEnabledConfig())
    sentinel = object()
    seen: dict[str, object] = {}

    def fake_validate(received: RemoteProductionConfig) -> None:
        seen["validated"] = received

    def fake_build(received: RemoteProductionConfig):
        seen["built"] = received
        return sentinel

    monkeypatch.setattr(remote_server, "validate_release_provider_config", fake_validate)
    monkeypatch.setattr(
        remote_server,
        "build_release_provider_decision_source_factory_v14",
        fake_build,
    )

    assert remote_server._decision_source_factory(config) is sentinel
    assert seen == {"validated": config, "built": config}
