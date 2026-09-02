import json

from research.e2.models import RunTrace, TraceEvent

from academy_tractian.observability import project_trace, safe_run_id


def test_projection_does_not_serialize_raw_sensitive_trace_material() -> None:
    secret = "TOP-SECRET-CREDENTIAL"
    identity = "private-user-binding"
    seed = "private-seed"
    trace = RunTrace(
        run_id="raw-run-id",
        scenario_id="prod:test",
        config_hash="a" * 64,
        identity_binding_id=identity,
        seed_ref=seed,
        events=[
            TraceEvent(sequence=0, event_type="run_started", metadata={"execution_mode": "live"}),
            TraceEvent(
                sequence=1,
                event_type="tool_proposal",
                tool_name="get_asset",
                arguments={"asset_id": secret},
            ),
            TraceEvent(
                sequence=2,
                event_type="tool_call",
                tool_name="get_asset",
                arguments={"asset_id": secret},
                metadata={
                    "method": "GET",
                    "path": "/assets/{assetId}",
                    "resolved_path": f"/assets/{secret}",
                    "kind": "read",
                },
            ),
            TraceEvent(
                sequence=3,
                event_type="tool_result",
                tool_name="get_asset",
                result={
                    "headers": {"authorization": secret},
                    "body": {"secret": secret},
                },
                metadata={"status_code": 200},
            ),
            TraceEvent(
                sequence=4,
                event_type="observation",
                tool_name="get_asset",
                result={"secret": secret},
                metadata={"evidence_id": "EV-safe", "status_code": 200},
            ),
            TraceEvent(
                sequence=5,
                event_type="final_response",
                result={
                    "decision": "ORIENT",
                    "message": "Customer-safe result",
                    "secret": secret,
                },
            ),
            TraceEvent(sequence=6, event_type="run_finished"),
        ],
    )

    run, events, evidence = project_trace(trace)
    serialized = json.dumps(
        {
            "run": run.model_dump(mode="json"),
            "events": [event.model_dump(mode="json") for event in events],
            "evidence": [item.model_dump(mode="json") for item in evidence],
        },
        sort_keys=True,
    )

    assert secret not in serialized
    assert identity not in serialized
    assert seed not in serialized
    assert "raw-run-id" not in serialized
    assert "Customer-safe result" in serialized
    assert "EV-safe" in serialized
    assert run.run_id == safe_run_id("raw-run-id")
    assert events[1].argument_names == ("asset_id",)
    assert events[2].path_template == "/assets/{assetId}"


def test_model_call_projection_keeps_only_safe_operational_metadata() -> None:
    trace = RunTrace(
        run_id="run-2",
        scenario_id="prod:model",
        config_hash="b" * 64,
        identity_binding_id="identity",
        seed_ref="none",
        events=[
            TraceEvent(sequence=0, event_type="run_started"),
            TraceEvent(
                sequence=1,
                event_type="model_call",
                call_id="c" * 64,
                metadata={
                    "provider_id": "cloudflare",
                    "model_id": "model-x",
                    "route_id": "direct",
                    "live_call": True,
                    "outcome": "success",
                    "decision_kind": "TOOL",
                    "latency_ms": 321,
                    "turn_index": 0,
                    "tool_call_count": 0,
                    "request_sha256": "d" * 64,
                    "response_sha256": "e" * 64,
                },
            ),
            TraceEvent(
                sequence=2,
                event_type="final_response",
                result={"decision": "ORIENT", "message": "ok"},
            ),
            TraceEvent(sequence=3, event_type="run_finished"),
        ],
    )

    _, events, _ = project_trace(trace)
    event = events[1]

    assert event.provider_id == "cloudflare"
    assert event.model_id == "model-x"
    assert event.latency_ms == 321
    dumped = event.model_dump(mode="json")
    assert "request_sha256" not in dumped
    assert "response_sha256" not in dumped
