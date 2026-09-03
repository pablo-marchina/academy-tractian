from __future__ import annotations

import json

from fastapi.testclient import TestClient

from research.e2.models import RunTrace, TraceEvent

from academy_tractian.observability import safe_run_id
from academy_tractian.observability_api import create_observability_app


def _completed_trace() -> RunTrace:
    return RunTrace(
        run_id="sse-raw-run",
        scenario_id="prod:sse",
        config_hash="c" * 64,
        identity_binding_id="private-identity",
        seed_ref="private-seed",
        events=[
            TraceEvent(sequence=0, event_type="run_started", metadata={"execution_mode": "live"}),
            TraceEvent(
                sequence=1,
                event_type="decision",
                result={"kind": "FINAL", "turn_index": 0, "tool_call_count": 0},
            ),
            TraceEvent(
                sequence=2,
                event_type="final_response",
                result={
                    "decision": "ORIENT",
                    "response_mode": "complete",
                    "message": "Safe SSE result",
                },
            ),
            TraceEvent(sequence=3, event_type="run_finished"),
        ],
    )


def _data_records(body: str) -> list[dict]:
    records: list[dict] = []
    for line in body.splitlines():
        if line.startswith("data: "):
            records.append(json.loads(line.removeprefix("data: ")))
    return records


def test_sse_emits_persisted_safe_events_in_sequence(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "sse.duckdb")
    trace = _completed_trace()
    run_id = app.state.observability_store.persist_trace(trace)
    client = TestClient(app)

    response = client.get(f"/api/stream?run_id={run_id}&follow=false")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    records = _data_records(response.text)
    assert [record["sequence"] for record in records] == [0, 1, 2, 3]
    assert [record["event_id"] for record in records] == [
        f"{run_id}:0",
        f"{run_id}:1",
        f"{run_id}:2",
        f"{run_id}:3",
    ]
    assert "private-identity" not in response.text
    assert "private-seed" not in response.text
    assert "sse-raw-run" not in response.text
    assert "Safe SSE result" in response.text


def test_sse_last_event_id_returns_only_missing_events(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "sse.duckdb")
    trace = _completed_trace()
    run_id = app.state.observability_store.persist_trace(trace)
    client = TestClient(app)

    response = client.get(
        f"/api/stream?run_id={run_id}&follow=false",
        headers={"Last-Event-ID": f"{run_id}:1"},
    )

    assert response.status_code == 200
    records = _data_records(response.text)
    assert [record["sequence"] for record in records] == [2, 3]


def test_sse_explicit_sequence_cursor_replays_missing_events_then_emits_caught_up(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "sse.duckdb")
    trace = _completed_trace()
    run_id = app.state.observability_store.persist_trace(trace)
    client = TestClient(app)

    response = client.get(f"/api/stream?run_id={run_id}&after_sequence=1")

    assert response.status_code == 200
    records = _data_records(response.text)
    trace_records = [record for record in records if "sequence" in record]
    stream_states = [record for record in records if record.get("state") == "caught_up"]
    assert [record["sequence"] for record in trace_records] == [2, 3]
    assert stream_states == [
        {"run_id": run_id, "state": "caught_up", "after_sequence": 3}
    ]
    assert "event: stream_state" in response.text


def test_sse_rejects_ambiguous_header_and_explicit_cursor(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "sse.duckdb")
    run_id = app.state.observability_store.persist_trace(_completed_trace())
    client = TestClient(app)

    response = client.get(
        f"/api/stream?run_id={run_id}&after_sequence=1",
        headers={"Last-Event-ID": f"{run_id}:1"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "stream reconnect cursor is ambiguous"


def test_sse_rejects_cursor_from_another_run(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "sse.duckdb")
    trace = _completed_trace()
    run_id = app.state.observability_store.persist_trace(trace)
    client = TestClient(app)

    response = client.get(
        f"/api/stream?run_id={run_id}&follow=false",
        headers={"Last-Event-ID": f"{safe_run_id('other-run')}:1"},
    )

    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"]


def test_sse_unknown_run_is_404(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "sse.duckdb")
    client = TestClient(app)

    response = client.get("/api/stream?run_id=run_missing&follow=false")
    assert response.status_code == 404