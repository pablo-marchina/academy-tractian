from __future__ import annotations
from typing import Any, Protocol
from .hash import sha256_json

class ObservationTransport(Protocol):
    def execute(self, request: dict[str, Any]) -> dict[str, Any]: ...

class ReplayStore:
    """Deterministic request->observation store. It never invents observations."""
    def __init__(self, observations: dict[str, dict[str, Any]] | None = None) -> None:
        self._observations = dict(observations or {})

    @staticmethod
    def fingerprint(request: dict[str, Any]) -> str:
        return sha256_json(request)

    def record(self, request: dict[str, Any], observation: dict[str, Any]) -> str:
        key = self.fingerprint(request)
        if key in self._observations and self._observations[key] != observation:
            raise ValueError(f"non-deterministic replay observation for request {key}")
        self._observations[key] = observation
        return key

    def replay(self, request: dict[str, Any]) -> dict[str, Any]:
        key = self.fingerprint(request)
        if key not in self._observations:
            raise KeyError(f"no recorded observation for request {key}")
        return self._observations[key]

    def export(self) -> dict[str, dict[str, Any]]:
        return dict(self._observations)
