import json

from fastapi.testclient import TestClient

from research.e2.models import RunTrace, TraceEvent

from academy_tractian.observability import safe_run_id
from academy_tractian.observability_api import create_observability_app


def _trace(secret: str = "HTTP-SECRET") -> RunTrace:
    return RunTrace(
        run_id="raw-api-run",
        scenario_id="prod:api",
        config_hash="b" * 64,
        identity_binding_id="api-private-identity",
        seed_ref="api-private-seed",
        events=[
            TraceEvent(sequence=0, event_type="run_started", metadata={"execution_mode": "live"}),
            TraceEvent(
                sequence=1,
                event_type="model_call",
                call_id="c" * 64,
                metadata={
                    "provider_id": "provider-safe",
                    "model_id": "model-safe",
                    "route_id": "direct",
                    "live_call": False,
                    "outcome": "success",
                    "decision_kind": "TOOL",
                    "latency_ms": 123,
                    "turn_index": 0,
                    "tool_call_count": 0,
                    "request_sha256": "d" * 64,
                    "response_sha256": "e" * 64,
                },
            ),
            TraceEvent(
                sequence=2,
                event_type="tool_proposal",
                tool_name="get_asset",
                arguments={"asset_id": secret},
            ),
            TraceEvent(
                sequence=3,
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
                sequence=4,
                event_type="tool_result",
                tool_name="get_asset",
                result={"headers": {"authorization": secret}, "body": {"secret": secret}},
                metadata={"status_code": 200},
            ),
            TraceEvent(
                sequence=5,
                event_type="observation",
                tool_name="get_asset",
                result={"secret": secret},
                metadata={"status_code": 200, "evidence_id": "EV-api-safe"},
            ),
            TraceEvent(
                sequence=6,
                event_type="final_response",
                result={
                    "decision": "ORIENT",
                    "response_mode": "complete",
                    "message": "Safe API-visible conclusion",
                },
            ),
            TraceEvent(sequence=7, event_type="run_finished"),
        ],
    )


def test_health_ready_version_and_safe_run_queries(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "api.duckdb")
    client = TestClient(app)
    trace = _trace()
    run_id = app.state.observability_store.persist_trace(trace)

    assert client.get("/health").status_code == 200
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").status_code == 200

    version_payload = client.get("/version").json()
    assert version_payload["service"] == "observability-api"
    assert len(version_payload["config_hash"]) == 64
    assert str(tmp_path) not in json.dumps(version_payload)

    overview = client.get("/api/overview")
    assert overview.status_code == 200
    assert overview.json()["total_runs"] == 1

    runs = client.get("/api/runs")
    assert runs.status_code == 200
    assert runs.json()["count"] == 1
    assert runs.json()["items"][0]["run_id"] == run_id

    detail = client.get(f"/api/runs/{run_id}")
    events = client.get(f"/api/runs/{run_id}/events")
    evidence = client.get(f"/api/runs/{run_id}/evidence")
    evaluation = client.get(f"/api/runs/{run_id}/evaluation")

    assert detail.status_code == 200
    assert events.status_code == 200
    assert evidence.status_code == 200
    assert evaluation.status_code == 200
    assert events.json()["count"] == len(trace.events)
    assert evidence.json()["count"] == 1
    assert evaluation.json()["count"] == 0

    serialized = json.dumps(
        {
            "detail": detail.json(),
            "events": events.json(),
            "evidence": evidence.json(),
            "version": version_payload,
        },
        sort_keys=True,
    )
    assert "HTTP-SECRET" not in serialized
    assert "api-private-identity" not in serialized
    assert "api-private-seed" not in serialized
    assert "raw-api-run" not in serialized
    assert "authorization" not in serialized
    assert "request_sha256" not in serialized
    assert "response_sha256" not in serialized
    assert "Safe API-visible conclusion" in serialized
    assert "EV-api-safe" in serialized
    assert safe_run_id(trace.run_id) in serialized


def test_unknown_run_returns_404(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "api.duckdb")
    client = TestClient(app)

    response = client.get("/api/runs/run_does_not_exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "run_not_found"


def test_run_limit_validation_is_bounded(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "api.duckdb")
    client = TestClient(app)

    assert client.get("/api/runs?limit=0").status_code == 422
    assert client.get("/api/runs?limit=1001").status_code == 422
