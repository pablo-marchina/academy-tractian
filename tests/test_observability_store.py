import json

import duckdb

from research.e2.models import RunTrace, TraceEvent

from academy_tractian.observability import safe_run_id
from academy_tractian.observability_store import ObservabilityStore


def _trace(secret: str = "DB-SECRET") -> RunTrace:
    return RunTrace(
        run_id="raw-store-run",
        scenario_id="prod:store",
        config_hash="a" * 64,
        identity_binding_id="private-identity",
        seed_ref="private-seed",
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
                result={"headers": {"authorization": secret}, "body": {"secret": secret}},
                metadata={"status_code": 200},
            ),
            TraceEvent(
                sequence=4,
                event_type="observation",
                tool_name="get_asset",
                result={"secret": secret},
                metadata={"status_code": 200, "evidence_id": "EV-store-safe"},
            ),
            TraceEvent(
                sequence=5,
                event_type="final_response",
                result={
                    "decision": "ORIENT",
                    "response_mode": "complete",
                    "message": "Safe operator-visible conclusion",
                    "secret": secret,
                },
            ),
            TraceEvent(sequence=6, event_type="run_finished"),
        ],
    )


def test_store_persists_only_safe_projection_and_is_idempotent(tmp_path) -> None:
    db_path = tmp_path / "observability.duckdb"
    store = ObservabilityStore(db_path)
    trace = _trace()

    first_run_id = store.persist_trace(trace)
    second_run_id = store.persist_trace(trace)

    assert first_run_id == second_run_id == safe_run_id(trace.run_id)
    assert store.ready()

    overview = store.overview()
    assert overview["total_runs"] == 1
    assert overview["completed_runs"] == 1
    assert overview["tool_calls"] == 1

    events = store.get_events(first_run_id)
    evidence = store.get_evidence(first_run_id)
    assert len(events) == len(trace.events)
    assert len(evidence) == 1
    assert evidence[0]["evidence_id"] == "EV-store-safe"

    serialized = json.dumps(
        {
            "run": store.get_run(first_run_id),
            "events": events,
            "evidence": evidence,
        },
        sort_keys=True,
        default=str,
    )
    assert "DB-SECRET" not in serialized
    assert "private-identity" not in serialized
    assert "private-seed" not in serialized
    assert "raw-store-run" not in serialized
    assert "authorization" not in serialized
    assert "resolved_path" not in serialized
    assert "Safe operator-visible conclusion" in serialized
    assert "asset_id" in serialized


def test_database_file_itself_contains_no_raw_secret_rows(tmp_path) -> None:
    db_path = tmp_path / "observability.duckdb"
    store = ObservabilityStore(db_path)
    store.persist_trace(_trace("RAW-MATERIAL-MUST-NOT-PERSIST"))

    connection = duckdb.connect(str(db_path), read_only=True)
    try:
        for table in ("runs", "events", "evidence", "evaluations"):
            rows = connection.execute(f"SELECT * FROM {table}").fetchall()
            assert "RAW-MATERIAL-MUST-NOT-PERSIST" not in repr(rows)
    finally:
        connection.close()


def test_memory_database_is_rejected_to_preserve_multi_connection_semantics() -> None:
    try:
        ObservabilityStore(":memory:")
    except ValueError as exc:
        assert "persistent DuckDB path" in str(exc)
    else:
        raise AssertionError("expected :memory: store to be rejected")
