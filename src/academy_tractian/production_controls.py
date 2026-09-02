from __future__ import annotations

from threading import Lock
from typing import Any


class ProductionControlState:
    """Runtime-owned kill-switch state excluded from model/controller context.

    Provider calls may be disabled immediately through the host-owned object. Consequential
    actions remain disabled by the frozen ProductionRuntimeConfig v1 contract and cannot be
    enabled through this control object.
    """

    def __init__(self, *, provider_calls_enabled: bool = True) -> None:
        self._lock = Lock()
        self._provider_calls_enabled = bool(provider_calls_enabled)
        self._provider_revision = 0

    def provider_calls_enabled(self) -> bool:
        with self._lock:
            return self._provider_calls_enabled

    def set_provider_calls_enabled(self, enabled: bool) -> None:
        with self._lock:
            normalized = bool(enabled)
            if normalized != self._provider_calls_enabled:
                self._provider_calls_enabled = normalized
                self._provider_revision += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema_version": "production-controls-v1",
                "provider_kill_switch": {
                    "engaged": not self._provider_calls_enabled,
                    "provider_calls_enabled": self._provider_calls_enabled,
                    "revision": self._provider_revision,
                    "mutation_surface": "host_owned_no_public_http_mutator",
                },
                "action_kill_switch": {
                    "engaged": True,
                    "actions_enabled": False,
                    "source": "ProductionRuntimeConfig.actions_enabled_literal_false",
                    "mutation_surface": "none_in_prod_runtime_v1",
                },
            }
