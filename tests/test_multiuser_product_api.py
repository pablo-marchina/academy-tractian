from __future__ import annotations

from fastapi import Request
from fastapi.testclient import TestClient

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.product_api import (
    DEFAULT_RUNTIME_PERMISSIONS,
    AuthenticatedRuntimeContext,
    create_product_app,
)
from academy_tractian.realtime_runtime import RealtimeProductionRuntime


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Scoped product run completed.",
            },
        )


class NoopTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("final-only test must not call TRACTIAN transport")


def _context_provider(request: Request) -> AuthenticatedRuntimeContext:
    user_id = request.headers.get("X-Test-User")
    if not user_id:
        raise RuntimeError("missing synthetic authenticated user")
    organization_id = request.headers.get("X-Test-Organization", "org-1")
    permissions = DEFAULT_RUNTIME_PERMISSIONS
    if user_id == "admin":
        permissions = permissions | frozenset(
            {"runs:read:any", "analytics:read:global"}
        )
    return AuthenticatedRuntimeContext(
        organization_id=organization_id,
        identity_id=f"identity-{user_id}",
        user_id=user_id,
        permissions=permissions,
    )


def _runtime_factory(sink) -> RealtimeProductionRuntime:
    return RealtimeProductionRuntime(
        decision_source=FinalSource(),
        transport=NoopTransport(),
        observability_sink=sink,
    )


def _headers(user_id: str, organization_id: str = "org-1") -> dict[str, str]:
    return {
        "X-Test-User": user_id,
        "X-Test-Organization": organization_id,
    }


def _submit_and_wait(client: TestClient, app, user_id: str) -> str:
    response = client.post(
        "/api/runs",
        headers=_headers(user_id),
        json={"user_request": f"Investigate ticket for {user_id}."},
    )
    assert response.status_code == 202
    run_id = response.json()["run_id"]
    future = app.state.run_execution_registry.future(run_id)
    assert future is not None
    future.result(timeout=10)
    return run_id


def test_two_users_cannot_cross_read_run_surfaces_or_sse(tmp_path) -> None:
    app = create_product_app(
        db_path=tmp_path / "multiuser.duckdb",
        access_db_path=tmp_path / "multiuser-access.duckdb",
        runtime_factory=_runtime_factory,
        context_provider=_context_provider,
    )

    with TestClient(app) as client:
        run_a = _submit_and_wait(client, app, "user-a")
        run_b = _submit_and_wait(client, app, "user-b")

        own_a = client.get(f"/api/runs/{run_a}", headers=_headers("user-a"))
        own_b = client.get(f"/api/runs/{run_b}", headers=_headers("user-b"))
        assert own_a.status_code == 200
        assert own_b.status_code == 200

        user_a_runs = client.get("/api/runs", headers=_headers("user-a")).json()["items"]
        user_b_runs = client.get("/api/runs", headers=_headers("user-b")).json()["items"]
        assert {item["run_id"] for item in user_a_runs} == {run_a}
        assert {item["run_id"] for item in user_b_runs} == {run_b}

        cross_paths = (
            f"/api/runs/{run_a}",
            f"/api/runs/{run_a}/events",
            f"/api/runs/{run_a}/evidence",
            f"/api/runs/{run_a}/evaluation",
            f"/api/runs/{run_a}/lineage",
            f"/api/runs/{run_a}/execution",
        )
        for path in cross_paths:
            response = client.get(path, headers=_headers("user-b"))
            assert response.status_code == 404, path
            assert response.json()["detail"] == "run_not_found"

        cross_stream = client.get(
            f"/api/stream?run_id={run_a}&follow=false",
            headers=_headers("user-b"),
        )
        assert cross_stream.status_code == 404
        assert cross_stream.json()["detail"] == "run_not_found"

        cross_query = client.post(
            "/api/query",
            headers=_headers("user-b"),
            json={
                "dataset": "runs",
                "run_id": run_a,
                "dimensions": [],
                "measure": "count",
                "filters": [],
                "chart_type": "table",
                "limit": 20,
            },
        )
        assert cross_query.status_code == 404

        cross_org_same_user = client.get(
            f"/api/runs/{run_a}",
            headers=_headers("user-a", "org-2"),
        )
        assert cross_org_same_user.status_code == 404

        # Global analytics are fail-closed for normal users until an explicitly privileged
        # or tenant-scoped analytical view is selected.
        assert client.get("/api/overview", headers=_headers("user-a")).status_code == 403

        admin_runs = client.get("/api/runs", headers=_headers("admin")).json()["items"]
        assert {item["run_id"] for item in admin_runs} == {run_a, run_b}
        assert client.get("/api/overview", headers=_headers("admin")).status_code == 200


def test_run_ownership_survives_product_restart(tmp_path) -> None:
    db_path = tmp_path / "restart.duckdb"
    access_path = tmp_path / "restart-access.duckdb"

    first_app = create_product_app(
        db_path=db_path,
        access_db_path=access_path,
        runtime_factory=_runtime_factory,
        context_provider=_context_provider,
    )
    with TestClient(first_app) as client:
        run_id = _submit_and_wait(client, first_app, "user-a")
        assert client.get(f"/api/runs/{run_id}", headers=_headers("user-a")).status_code == 200

    second_app = create_product_app(
        db_path=db_path,
        access_db_path=access_path,
        runtime_factory=_runtime_factory,
        context_provider=_context_provider,
    )
    with TestClient(second_app) as client:
        assert second_app.state.run_access_store.ready() is True
        assert client.get(f"/api/runs/{run_id}", headers=_headers("user-a")).status_code == 200
        assert client.get(f"/api/runs/{run_id}", headers=_headers("user-b")).status_code == 404


def test_browser_cannot_override_tenant_role_or_permissions(tmp_path) -> None:
    app = create_product_app(
        db_path=tmp_path / "payload-boundary.duckdb",
        access_db_path=tmp_path / "payload-boundary-access.duckdb",
        runtime_factory=_runtime_factory,
        context_provider=_context_provider,
    )
    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            headers=_headers("user-a"),
            json={
                "user_request": "Attempt to override trusted scope.",
                "organization_id": "attacker-org",
                "role": "admin",
                "permissions": ["runs:read:any", "analytics:read:global"],
            },
        )
        assert response.status_code == 422
