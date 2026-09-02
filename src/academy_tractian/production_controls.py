from __future__ import annotations

from threading import Lock
from typing import Any


class ProductionControlState:
    """Host-owned kill-switch state excluded from model/controller context.

    Provider and confirmed-action execution can be disabled immediately by trusted host code.
    Defaults preserve the accepted production v1 behavior: provider calls enabled and
    consequential actions disabled. There is intentionally no public HTTP mutation endpoint.
    `ProductionRuntimeConfig.actions_enabled` remains literal False; the separate v2 confirmed
    action executor is the only consumer of this action switch.
    """

    def __init__(
        self,
        *,
        provider_calls_enabled: bool = True,
        actions_enabled: bool = False,
    ) -> None:
        self._lock = Lock()
        self._provider_calls_enabled = bool(provider_calls_enabled)
        self._actions_enabled = bool(actions_enabled)
        self._provider_revision = 0
        self._action_revision = 0

    def provider_calls_enabled(self) -> bool:
        with self._lock:
            return self._provider_calls_enabled

    def actions_enabled(self) -> bool:
        with self._lock:
            return self._actions_enabled

    def set_provider_calls_enabled(self, enabled: bool) -> None:
        with self._lock:
            normalized = bool(enabled)
            if normalized != self._provider_calls_enabled:
                self._provider_calls_enabled = normalized
                self._provider_revision += 1

    def set_actions_enabled(self, enabled: bool) -> None:
        with self._lock:
            normalized = bool(enabled)
            if normalized != self._actions_enabled:
                self._actions_enabled = normalized
                self._action_revision += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "schema_version": "production-controls-v2",
                "provider_kill_switch": {
                    "engaged": not self._provider_calls_enabled,
                    "provider_calls_enabled": self._provider_calls_enabled,
                    "revision": self._provider_revision,
                    "mutation_surface": "host_owned_no_public_http_mutator",
                },
                "action_kill_switch": {
                    "engaged": not self._actions_enabled,
                    "actions_enabled": self._actions_enabled,
                    "revision": self._action_revision,
                    "source": "host_owned_confirmed_action_executor_v2",
                    "mutation_surface": "host_owned_no_public_http_mutator",
                    "base_runtime_actions_enabled": False,
                },
            }
