from concurrent.futures import ThreadPoolExecutor
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


def test_concurrent_frontend_polling_and_trace_persistence_share_one_safe_file_handle(tmp_path) -> None:
    """Regress the REST/SSE + realtime writer race observed in full-product Chromium E2E."""

    db_path = tmp_path / "concurrent-observability.duckdb"
    store = ObservabilityStore(db_path)
    trace = _trace("CONCURRENT-RAW-MATERIAL")
    run_id = store.persist_trace(trace)

    def poll_reader(worker_index: int) -> None:
        for iteration in range(20):
            selector = (worker_index + iteration) % 6
            if selector == 0:
                assert store.ready() is True
            elif selector == 1:
                assert store.get_run(run_id) is not None
            elif selector == 2:
                assert store.get_events_after(run_id, after_sequence=-1)
            elif selector == 3:
                assert store.get_events(run_id)
            elif selector == 4:
                assert store.get_evidence(run_id)
            else:
                assert store.overview()["total_runs"] == 1

    def realtime_writer() -> None:
        for _ in range(20):
            assert store.persist_trace(trace) == run_id

    with ThreadPoolExecutor(max_workers=13) as executor:
        futures = [executor.submit(poll_reader, worker_index) for worker_index in range(12)]
        futures.append(executor.submit(realtime_writer))
        for future in futures:
            future.result(timeout=30)

    assert store.ready() is True
    assert store.get_run(run_id) is not None
    assert len(store.get_events(run_id)) == len(trace.events)
    assert len(store.get_evidence(run_id)) == 1

    serialized = json.dumps(
        {
            "run": store.get_run(run_id),
            "events": store.get_events(run_id),
            "evidence": store.get_evidence(run_id),
        },
        sort_keys=True,
        default=str,
    )
    assert "CONCURRENT-RAW-MATERIAL" not in serialized
