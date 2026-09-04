from __future__ import annotations

from fastapi.testclient import TestClient

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.product_api import DEFAULT_RUNTIME_PERMISSIONS, create_product_app
from academy_tractian.realtime_runtime import RealtimeProductionRuntime
from academy_tractian.runtime_identity import (
    SignedBearerRuntimeContextProvider,
    SignedRuntimeIdentityClaims,
    issue_signed_runtime_token,
)


SECRET = "integration-runtime-identity-secret-at-least-32-bytes"
ISSUER = "academy-integration-issuer"
AUDIENCE = "academy-product"
NOW = 2_000_000_000


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Authenticated scoped run completed.",
            },
        )


class NoopTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("final-only authenticated product test must not call transport")


def _runtime_factory(sink) -> RealtimeProductionRuntime:
    return RealtimeProductionRuntime(
        decision_source=FinalSource(),
        transport=NoopTransport(),
        observability_sink=sink,
    )


def _claims(
    *,
    user_id: str,
    organization_id: str,
    permissions: frozenset[str] = DEFAULT_RUNTIME_PERMISSIONS,
) -> SignedRuntimeIdentityClaims:
    return SignedRuntimeIdentityClaims(
        issuer=ISSUER,
        audience=AUDIENCE,
        token_id=f"token-{organization_id}-{user_id}",
        identity_id=f"identity-{organization_id}-{user_id}",
        user_id=user_id,
        organization_id=organization_id,
        permissions=tuple(sorted(permissions)),
        issued_at=NOW - 30,
        expires_at=NOW + 300,
    )


def _headers(
    *,
    user_id: str,
    organization_id: str,
    permissions: frozenset[str] = DEFAULT_RUNTIME_PERMISSIONS,
) -> dict[str, str]:
    token = issue_signed_runtime_token(
        secret=SECRET,
        claims=_claims(
            user_id=user_id,
            organization_id=organization_id,
            permissions=permissions,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def _submit_wait(client: TestClient, app, *, user_id: str, organization_id: str) -> str:
    response = client.post(
        "/api/runs",
        headers=_headers(user_id=user_id, organization_id=organization_id),
        json={"user_request": "Investigate this authenticated tenant ticket."},
    )
    assert response.status_code == 202
    run_id = response.json()["run_id"]
    future = app.state.run_execution_registry.future(run_id)
    assert future is not None
    future.result(timeout=10)
    return run_id


def test_signed_identity_drives_run_ownership_and_cross_tenant_reads_fail_closed(tmp_path):
    provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        now=lambda: NOW,
    )
    app = create_product_app(
        db_path=tmp_path / "authenticated.duckdb",
        access_db_path=tmp_path / "authenticated-access.duckdb",
        execution_db_path=tmp_path / "authenticated-execution.duckdb",
        runtime_factory=_runtime_factory,
        context_provider=provider,
    )

    with TestClient(app) as client:
        run_id = _submit_wait(client, app, user_id="user-a", organization_id="org-a")

        owner = client.get(
            f"/api/runs/{run_id}",
            headers=_headers(user_id="user-a", organization_id="org-a"),
        )
        assert owner.status_code == 200

        same_user_wrong_tenant = client.get(
            f"/api/runs/{run_id}",
            headers=_headers(user_id="user-a", organization_id="org-b"),
        )
        assert same_user_wrong_tenant.status_code == 404
        assert same_user_wrong_tenant.json()["detail"] == "run_not_found"

        same_tenant_wrong_user = client.get(
            f"/api/runs/{run_id}",
            headers=_headers(user_id="user-b", organization_id="org-a"),
        )
        assert same_tenant_wrong_user.status_code == 404

        missing_identity = client.get(f"/api/runs/{run_id}")
        assert missing_identity.status_code == 401


def test_browser_cannot_spoof_signed_tenant_identity_permissions_or_seed_in_payload(tmp_path):
    provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        now=lambda: NOW,
    )
    app = create_product_app(
        db_path=tmp_path / "spoof.duckdb",
        access_db_path=tmp_path / "spoof-access.duckdb",
        execution_db_path=tmp_path / "spoof-execution.duckdb",
        runtime_factory=_runtime_factory,
        context_provider=provider,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            headers=_headers(user_id="user-a", organization_id="org-a"),
            json={
                "user_request": "Attempt to override authenticated context.",
                "organization_id": "org-attacker",
                "identity_id": "identity-attacker",
                "user_id": "user-attacker",
                "role": "admin",
                "permissions": ["runs:read:any", "analytics:read:global"],
                "seed": "CEN-99",
            },
        )
    assert response.status_code == 422


def test_global_access_requires_both_signed_claim_and_server_side_enablement(tmp_path):
    normal_provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        now=lambda: NOW,
    )
    normal_app = create_product_app(
        db_path=tmp_path / "global-normal.duckdb",
        access_db_path=tmp_path / "global-normal-access.duckdb",
        runtime_factory=_runtime_factory,
        context_provider=normal_provider,
    )
    privileged_permissions = DEFAULT_RUNTIME_PERMISSIONS | frozenset(
        {"runs:read:any", "analytics:read:global"}
    )
    with TestClient(normal_app) as client:
        denied = client.get(
            "/api/overview",
            headers=_headers(
                user_id="admin",
                organization_id="org-admin",
                permissions=privileged_permissions,
            ),
        )
    assert denied.status_code == 403
    assert denied.json()["detail"] == "runtime_identity_privilege_not_enabled"

    privileged_provider = SignedBearerRuntimeContextProvider(
        secret=SECRET,
        issuer=ISSUER,
        audience=AUDIENCE,
        allowed_privileged_permissions={"runs:read:any", "analytics:read:global"},
        now=lambda: NOW,
    )
    privileged_app = create_product_app(
        db_path=tmp_path / "global-enabled.duckdb",
        access_db_path=tmp_path / "global-enabled-access.duckdb",
        runtime_factory=_runtime_factory,
        context_provider=privileged_provider,
    )
    with TestClient(privileged_app) as client:
        allowed = client.get(
            "/api/overview",
            headers=_headers(
                user_id="admin",
                organization_id="org-admin",
                permissions=privileged_permissions,
            ),
        )
    assert allowed.status_code == 200
