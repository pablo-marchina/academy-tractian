from __future__ import annotations

from typing import Any

from .models import RunTrace

_VOLATILE_METADATA_KEYS = {"timestamp", "action_id", "request_id", "response_id"}


def normalize_trace(trace: RunTrace) -> dict[str, Any]:
    """Remove run-volatile identifiers for replay/equivalence comparison."""
    events: list[dict[str, Any]] = []
    for event in trace.events:
        payload = event.model_dump(mode="json", exclude_none=True)
        payload.pop("timestamp", None)
        if payload.get("call_id"):
            payload["call_id"] = "<CALL_ID>"
        metadata = dict(payload.get("metadata") or {})
        for key in list(metadata):
            if key in _VOLATILE_METADATA_KEYS:
                metadata[key] = f"<{key.upper()}>"
        if metadata:
            payload["metadata"] = metadata
        if isinstance(payload.get("result"), dict) and "action_id" in payload["result"]:
            payload["result"] = {**payload["result"], "action_id": "<ACTION_ID>"}
        events.append(payload)
    return {
        "trace_version": trace.trace_version,
        "scenario_id": trace.scenario_id,
        "events": events,
    }
