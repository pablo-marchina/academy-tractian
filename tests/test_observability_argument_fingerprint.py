from __future__ import annotations

import json

from academy_tractian.observability import project_trace
from research.e2.models import RunTrace, TraceEvent


def test_tool_argument_fingerprint_detects_exact_repeats_without_exposing_values():
    secret_value = "asset-secret-identifier"
    trace = RunTrace(
        run_id="argument-fingerprint-run",
        scenario_id="prod:test",
        config_hash="f" * 64,
        identity_binding_id="identity",
        seed_ref="none",
        events=[
            TraceEvent(sequence=0, event_type="run_started"),
            TraceEvent(
                sequence=1,
                event_type="tool_call",
                tool_name="get_rms",
                arguments={"asset_id": secret_value, "point_id": "ftf_hz"},
                metadata={"method": "GET", "path": "/assets/{assetId}/rms", "kind": "read"},
            ),
            TraceEvent(
                sequence=2,
                event_type="tool_call",
                tool_name="get_rms",
                arguments={"point_id": "ftf_hz", "asset_id": secret_value},
                metadata={"method": "GET", "path": "/assets/{assetId}/rms", "kind": "read"},
            ),
            TraceEvent(
                sequence=3,
                event_type="tool_call",
                tool_name="get_rms",
                arguments={"asset_id": secret_value, "point_id": "other"},
                metadata={"method": "GET", "path": "/assets/{assetId}/rms", "kind": "read"},
            ),
            TraceEvent(sequence=4, event_type="run_finished"),
        ],
    )

    _, events, _ = project_trace(trace)
    first = events[1]
    same = events[2]
    different = events[3]

    assert first.arguments_sha256 is not None
    assert first.arguments_sha256 == same.arguments_sha256
    assert first.arguments_sha256 != different.arguments_sha256
    serialized = json.dumps([event.model_dump(mode="json") for event in events])
    assert secret_value not in serialized
    assert "ftf_hz" not in serialized
