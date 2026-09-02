from __future__ import annotations

from fastapi.testclient import TestClient

from academy_tractian.observability import (
    SafeEvaluation,
    SafeEvaluationCheck,
    SafeEvent,
    SafeRun,
)
from academy_tractian.observability_api import create_observability_app


def _seed(app) -> tuple[str, str]:
    store = app.state.observability_store
    run_a = SafeRun(
        run_id="run_scope_a",
        scenario_id="scope:a",
        config_hash="a" * 64,
        event_count=4,
        model_calls=0,
        tool_proposals=1,
        tool_calls=1,
        policy_blocks=1,
        errors=0,
        completed=True,
    )
    store.persist_projection(
        run_a,
        (
            SafeEvent(event_id="run_scope_a:0", run_id=run_a.run_id, sequence=0, event_type="run_started", origin="SYSTEM"),
            SafeEvent(event_id="run_scope_a:1", run_id=run_a.run_id, sequence=1, event_type="tool_proposal", origin="TOOL", tool_name="get_asset"),
            SafeEvent(event_id="run_scope_a:2", run_id=run_a.run_id, sequence=2, event_type="policy_check", origin="POLICY", tool_name="get_asset", policy_stage="B2", policy_allowed=False, policy_contained=True, policy_violation="RESOURCE_SCOPE"),
            SafeEvent(event_id="run_scope_a:3", run_id=run_a.run_id, sequence=3, event_type="tool_call", origin="TOOL", tool_name="get_asset"),
        ),
        (),
        evaluation=SafeEvaluation(
            run_id=run_a.run_id,
            blocking_pass=True,
            checks=(SafeEvaluationCheck(name="trace_integrity", passed=True, blocking=True),),
        ),
    )

    run_b = SafeRun(
        run_id="run_scope_b",
        scenario_id="scope:b",
        config_hash="b" * 64,
        event_count=4,
        model_calls=0,
        tool_proposals=1,
        tool_calls=1,
        policy_blocks=0,
        errors=0,
        completed=True,
    )
    store.persist_projection(
        run_b,
        (
            SafeEvent(event_id="run_scope_b:0", run_id=run_b.run_id, sequence=0, event_type="run_started", origin="SYSTEM"),
            SafeEvent(event_id="run_scope_b:1", run_id=run_b.run_id, sequence=1, event_type="tool_proposal", origin="TOOL", tool_name="get_sensor"),
            SafeEvent(event_id="run_scope_b:2", run_id=run_b.run_id, sequence=2, event_type="policy_check", origin="POLICY", tool_name="get_sensor", policy_stage="B1", policy_allowed=True, policy_contained=False),
            SafeEvent(event_id="run_scope_b:3", run_id=run_b.run_id, sequence=3, event_type="tool_call", origin="TOOL", tool_name="get_sensor"),
        ),
        (),
        evaluation=SafeEvaluation(
            run_id=run_b.run_id,
            blocking_pass=False,
            checks=(SafeEvaluationCheck(name="trace_integrity", passed=False, blocking=True),),
        ),
    )
    return run_a.run_id, run_b.run_id


def test_global_analytics_scope_filters_tools_policy_eval_and_dynamic_query(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "scope.duckdb")
    run_a, run_b = _seed(app)
    client = TestClient(app)

    global_tools = client.get("/api/tools/metrics").json()
    scoped_tools = client.get("/api/tools/metrics", params={"run_id": run_a}).json()
    assert global_tools["count"] == 2
    assert global_tools["scope"]["run_id"] is None
    assert scoped_tools["schema_version"] == "tools-metrics-v2"
    assert scoped_tools["scope"]["run_id"] == run_a
    assert [item["tool_name"] for item in scoped_tools["items"]] == ["get_asset"]

    scoped_policy = client.get("/api/policies/metrics", params={"run_id": run_a}).json()
    assert scoped_policy["scope"]["run_id"] == run_a
    assert scoped_policy["items"][0]["policy_stage"] == "B2"
    assert scoped_policy["items"][0]["block_rate"] == 1.0

    scoped_eval = client.get("/api/evaluations/metrics", params={"run_id": run_b}).json()
    assert scoped_eval["scope"]["run_id"] == run_b
    assert scoped_eval["rows"] == 1
    assert scoped_eval["overall_pass_rate"] == 0.0

    schema = client.get("/api/query/schema").json()
    assert schema["schema_version"] == "dynamic-analytics-schema-v2"
    assert schema["global_scope_fields"] == ["run_id"]
    assert "run_id" not in schema["datasets"]["events"]["dimensions"]

    scoped_query = client.post(
        "/api/query",
        json={
            "dataset": "events",
            "run_id": run_a,
            "dimensions": ["tool_name"],
            "measure": "count",
            "chart_type": "bar",
        },
    )
    assert scoped_query.status_code == 200
    payload = scoped_query.json()
    assert payload["schema_version"] == "dynamic-analytics-result-v2"
    assert payload["run_id"] == run_a
    assert payload["source_row_count"] == 4
    rows = {row["tool_name"]: row["value"] for row in payload["rows"]}
    assert rows["get_asset"] == 3
    assert "get_sensor" not in rows


def test_cross_filter_rejects_unknown_run_and_keeps_sql_closed(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "scope-negative.duckdb")
    run_a, _ = _seed(app)
    client = TestClient(app)

    assert client.get("/api/tools/metrics", params={"run_id": "run_missing"}).status_code == 404
    unknown_query = client.post(
        "/api/query",
        json={"dataset": "runs", "run_id": "run_missing", "measure": "count", "chart_type": "table"},
    )
    assert unknown_query.status_code == 404

    sql_field = client.post(
        "/api/query",
        json={
            "dataset": "events",
            "run_id": run_a,
            "measure": "count",
            "chart_type": "table",
            "sql": "select * from events",
        },
    )
    assert sql_field.status_code == 422
