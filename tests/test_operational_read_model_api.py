from __future__ import annotations

import json

from fastapi.testclient import TestClient

from academy_tractian.observability import (
    SafeEvaluation,
    SafeEvaluationCheck,
    SafeEvent,
    SafeEvidenceRef,
    SafeRun,
)
from academy_tractian.observability_api import create_observability_app


def _seed(app) -> tuple[str, str]:
    store = app.state.observability_store
    run_a = SafeRun(
        run_id="run_safe_a",
        scenario_id="prod:a",
        config_hash="a" * 64,
        event_count=9,
        model_calls=1,
        tool_proposals=1,
        tool_calls=1,
        policy_blocks=1,
        errors=0,
        terminal_decision="ORIENT",
        terminal_response_mode="complete",
        terminal_message="Safe terminal output",
        completed=True,
    )
    events_a = (
        SafeEvent(event_id="run_safe_a:0", run_id=run_a.run_id, sequence=0, event_type="run_started", origin="SYSTEM", outcome="live"),
        SafeEvent(event_id="run_safe_a:1", run_id=run_a.run_id, sequence=1, event_type="model_call", origin="MODEL", provider_id="provider-safe", model_id="model-safe", outcome="success", latency_ms=100),
        SafeEvent(event_id="run_safe_a:2", run_id=run_a.run_id, sequence=2, event_type="tool_proposal", origin="TOOL", tool_name="get_asset", argument_names=("asset_id",)),
        SafeEvent(event_id="run_safe_a:3", run_id=run_a.run_id, sequence=3, event_type="policy_check", origin="POLICY", tool_name="get_asset", policy_stage="B2", policy_allowed=False, policy_contained=True, policy_violation="RESOURCE_SCOPE"),
        SafeEvent(event_id="run_safe_a:4", run_id=run_a.run_id, sequence=4, event_type="tool_call", origin="TOOL", tool_name="get_asset", method="GET", path_template="/assets/{assetId}", tool_kind="read"),
        SafeEvent(event_id="run_safe_a:5", run_id=run_a.run_id, sequence=5, event_type="tool_result", origin="TOOL", tool_name="get_asset", status_code=200),
        SafeEvent(event_id="run_safe_a:6", run_id=run_a.run_id, sequence=6, event_type="observation", origin="OBSERVATION", tool_name="get_asset", status_code=200, evidence_id="EV-safe-1"),
        SafeEvent(event_id="run_safe_a:7", run_id=run_a.run_id, sequence=7, event_type="final_response", origin="CONTROLLER", decision_kind="ORIENT", response_mode="complete", message="Safe terminal output"),
        SafeEvent(event_id="run_safe_a:8", run_id=run_a.run_id, sequence=8, event_type="run_finished", origin="SYSTEM"),
    )
    evidence_a = (
        SafeEvidenceRef(evidence_id="EV-safe-1", run_id=run_a.run_id, sequence=6, tool_name="get_asset", status_code=200),
    )
    evaluation_a = SafeEvaluation(
        run_id=run_a.run_id,
        blocking_pass=True,
        checks=(
            SafeEvaluationCheck(name="trace_integrity", passed=True, blocking=True),
            SafeEvaluationCheck(name="known_tool_validity", passed=True, blocking=True),
        ),
    )
    store.persist_projection(run_a, events_a, evidence_a, evaluation=evaluation_a)

    run_b = SafeRun(
        run_id="run_safe_b",
        scenario_id="prod:b",
        config_hash="b" * 64,
        event_count=3,
        model_calls=1,
        tool_proposals=0,
        tool_calls=0,
        policy_blocks=0,
        errors=1,
        completed=False,
    )
    events_b = (
        SafeEvent(event_id="run_safe_b:0", run_id=run_b.run_id, sequence=0, event_type="run_started", origin="SYSTEM", outcome="live"),
        SafeEvent(event_id="run_safe_b:1", run_id=run_b.run_id, sequence=1, event_type="model_call", origin="MODEL", provider_id="provider-safe", model_id="model-safe", outcome="failure", failure_code="CLIENT_FAILURE", latency_ms=300),
        SafeEvent(event_id="run_safe_b:2", run_id=run_b.run_id, sequence=2, event_type="error", origin="SYSTEM", failure_code="CLIENT_FAILURE"),
    )
    store.persist_projection(run_b, events_b, ())
    return run_a.run_id, run_b.run_id


def test_operational_endpoints_are_safe_and_evidence_backed(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "ops.duckdb")
    run_a, _ = _seed(app)
    client = TestClient(app)

    health = client.get("/api/production/health")
    tools = client.get("/api/tools/metrics")
    policies = client.get("/api/policies/metrics")
    evaluations = client.get("/api/evaluations/metrics")
    lineage = client.get(f"/api/runs/{run_a}/lineage")

    assert health.status_code == 200
    assert health.json()["overall_status"] == "ready"
    components = {item["component"]: item for item in health.json()["components"]}
    assert components["observability_store"]["status"] == "ready"
    assert components["runtime"]["status"] == "not_instrumented"
    assert components["provider_kill_switch"]["status"] == "not_instrumented"
    assert "persistence_to_browser_ms" in health.json()["not_measured_yet"]

    assert tools.json()["count"] == 1
    assert tools.json()["items"][0]["tool_name"] == "get_asset"
    assert tools.json()["items"][0]["calls"] == 1

    assert policies.json()["count"] == 1
    assert policies.json()["items"][0]["policy_stage"] == "B2"
    assert policies.json()["items"][0]["block_rate"] == 1.0

    assert evaluations.json()["rows"] == 2
    assert evaluations.json()["blocking_pass_rate"] == 1.0

    payload = lineage.json()
    assert payload["runtime_card_count"] == 9
    assert payload["evaluation_card_count"] == 1
    assert payload["cards"][-1]["origin"] == "EVALUATOR"
    assert payload["cards"][6]["evidence_ref"]["evidence_id"] == "EV-safe-1"

    serialized = json.dumps(
        {
            "health": health.json(),
            "tools": tools.json(),
            "policies": policies.json(),
            "evaluations": evaluations.json(),
            "lineage": lineage.json(),
        },
        sort_keys=True,
    ).lower()
    for forbidden in ("identity_id", "user_id", "seed_ref", "authorization\":", "raw_response", "chain_of_thought", "request_sha256"):
        assert forbidden not in serialized


def test_dynamic_analytics_is_allow_listed_and_never_accepts_sql(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "query.duckdb")
    _seed(app)
    client = TestClient(app)

    schema = client.get("/api/query/schema")
    assert schema.status_code == 200
    assert schema.json()["limits"]["max_dimensions"] == 2
    assert "event_type" in schema.json()["datasets"]["events"]["dimensions"]

    grouped = client.post(
        "/api/query",
        json={
            "dataset": "events",
            "dimensions": ["event_type"],
            "measure": "count",
            "chart_type": "bar",
        },
    )
    assert grouped.status_code == 200
    rows = {row["event_type"]: row["value"] for row in grouped.json()["rows"]}
    assert rows["model_call"] == 2
    assert rows["run_started"] == 2

    histogram = client.post(
        "/api/query",
        json={
            "dataset": "events",
            "measure": "latency_ms_distribution",
            "chart_type": "histogram",
        },
    )
    assert histogram.status_code == 200
    assert histogram.json()["source_row_count"] == 12
    assert sum(row["value"] for row in histogram.json()["rows"]) == 2

    forbidden_dimension = client.post(
        "/api/query",
        json={
            "dataset": "events",
            "dimensions": ["select * from events"],
            "measure": "count",
            "chart_type": "bar",
        },
    )
    assert forbidden_dimension.status_code == 422
    assert "dimension_not_allowed" in forbidden_dimension.json()["detail"]

    arbitrary_sql_field = client.post(
        "/api/query",
        json={
            "dataset": "runs",
            "measure": "count",
            "chart_type": "table",
            "sql": "DROP TABLE runs",
        },
    )
    assert arbitrary_sql_field.status_code == 422

    invalid_heatmap = client.post(
        "/api/query",
        json={
            "dataset": "events",
            "dimensions": ["event_type"],
            "measure": "count",
            "chart_type": "heatmap",
        },
    )
    assert invalid_heatmap.status_code == 422


def test_provider_lab_integrates_d02_without_inventing_attempt_matrix(tmp_path) -> None:
    app = create_observability_app(db_path=tmp_path / "providers.duckdb")
    client = TestClient(app)

    response = client.get("/api/providers/experiments")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["registry_sha256"]) == 64
    experiments = {item["experiment_id"]: item for item in payload["experiments"]}

    d01 = experiments["D01"]
    assert d01["status"] == "COMPLETE"
    assert d01["selection"] == "NO_SELECTION"
    assert d01["attempted_calls"] == 32
    assert d01["cash_cost_usd"] == 0.0
    assert d01["diagnostic"]["client_failures_at_completion_cap"] == 24
    assert d01["attempt_matrix_available"] is False

    d02 = experiments["D02"]
    assert d02["status"] == "COMPLETE"
    assert d02["attempted_calls"] == 32
    assert d02["expected_calls"] == 32
    assert d02["selection"] == "NO_SELECTION"
    assert d02["production_selection_claim"] is False
    assert d02["cash_cost_usd"] == 0.0
    assert d02["packet_observed_neurons"] == 3344.1308560000007
    assert d02["completion_cap_tokens"] == 1024
    assert d02["resource_accounting_complete"] is True
    assert d02["raw_provider_material_recorded"] is False
    assert d02["attempt_matrix_available"] is False
    assert d02["diagnostic"] is None
    assert len(d02["candidates"]) == 2

    candidates = {item["candidate_id"]: item for item in d02["candidates"]}
    glm = candidates["cloudflare_glm_4_7_flash_workers_free"]
    nemotron = candidates["cloudflare_nemotron_3_120b_a12b_workers_free"]

    assert glm["success_rate"] == 0.4375
    assert glm["structured_decision_adherence"] == 0.4375
    assert glm["public_task_quality"] == 0.375
    assert glm["hard_gate_pass"] is False

    assert nemotron["success_rate"] == 0.5625
    assert nemotron["structured_decision_adherence"] == 0.5625
    assert nemotron["public_task_quality"] == 0.5625
    assert nemotron["hard_gate_pass"] is False

    assert glm["hard_gate_failures"] == ["M1_BELOW_MINIMUM", "M4_BELOW_MINIMUM", "M7_BELOW_MINIMUM"]
    assert nemotron["hard_gate_failures"] == ["M1_BELOW_MINIMUM", "M4_BELOW_MINIMUM", "M7_BELOW_MINIMUM"]

    serialized = json.dumps(d02, sort_keys=True).lower()
    for forbidden in ("api_token", "account_id", "authorization\":", "raw_response", "raw_request", "chain_of_thought"):
        assert forbidden not in serialized
