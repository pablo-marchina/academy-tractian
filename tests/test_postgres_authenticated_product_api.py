from __future__ import annotations

import os
from pathlib import Path
from time import time
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from psycopg import connect, sql

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from academy_tractian.product_api import DEFAULT_RUNTIME_PERMISSIONS
from academy_tractian.production_actions_v2 import ProductionActionPrincipal
from academy_tractian.runtime_identity import SignedRuntimeIdentityClaims, issue_signed_runtime_token


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)

SECRET = "postgres-authenticated-runtime-secret-at-least-32-bytes"
ISSUER = "academy-postgres-test-issuer"
AUDIENCE = "academy-product"


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Authenticated Postgres run completed.",
            },
        )


class NoopTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("final-only authenticated Postgres test must not call transport")


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-a",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(),
    )


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_auth_{suffix}"
        self.role = f"academy_auth_scoped_{suffix}"
        self.password = "scoped-test-password"
        with connect(admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOBYPASSRLS").format(
                    sql.Identifier(self.role),
                    sql.Literal(self.password),
                )
            )
        parsed = urlsplit(admin_dsn)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 5432
        database = parsed.path or "/postgres"
        self.scoped_dsn = urlunsplit(
            (
                parsed.scheme or "postgresql",
                f"{self.role}:{self.password}@{host}:{port}",
                database,
                "",
                "",
            )
        )

    def cleanup(self) -> None:
        with connect(self.admin_dsn, autocommit=True) as connection:
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema))
            )
            connection.execute(
                sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role))
            )


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _headers(*, user_id: str, organization_id: str) -> dict[str, str]:
    now = int(time())
    token = issue_signed_runtime_token(
        secret=SECRET,
        claims=SignedRuntimeIdentityClaims(
            issuer=ISSUER,
            audience=AUDIENCE,
            token_id=f"token-{organization_id}-{user_id}",
            identity_id=f"identity-{organization_id}-{user_id}",
            user_id=user_id,
            organization_id=organization_id,
            permissions=tuple(sorted(DEFAULT_RUNTIME_PERMISSIONS)),
            issued_at=now - 30,
            expires_at=now + 300,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def test_signed_bearer_identity_and_postgres_rls_close_tenant_boundary(
    tmp_path: Path,
    postgres_fixture,
) -> None:
    app = create_authenticated_postgres_action_capable_product_app(
        db_path=tmp_path / "authenticated-postgres.duckdb",
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        decision_source_factory=FinalSource,
        transport_factory=NoopTransport,
        authorization_resolver=_resolver,
        runtime_identity_secret=SECRET,
        runtime_identity_issuer=ISSUER,
        runtime_identity_audience=AUDIENCE,
        schema=postgres_fixture.schema,
        initialize_schema=True,
        actions_enabled=False,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            headers=_headers(user_id="user-a", organization_id="org-a"),
            json={"user_request": "Check authenticated tenant isolation."},
        )
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        future = app.state.run_execution_registry.future(run_id)
        assert future is not None
        future.result(timeout=15)

        assert app.state.runtime_identity_backend == "signed-bearer-hmac-sha256-v1"
        assert client.get(
            f"/api/runs/{run_id}",
            headers=_headers(user_id="user-a", organization_id="org-a"),
        ).status_code == 200
        cross_tenant = client.get(
            f"/api/runs/{run_id}",
            headers=_headers(user_id="user-a", organization_id="org-b"),
        )
        assert cross_tenant.status_code == 404
        assert cross_tenant.json()["detail"] == "run_not_found"
        assert client.get(f"/api/runs/{run_id}").status_code == 401

        database = app.state.postgres_operational_database
        with database.scoped_connection("org-b") as connection:
            rows = connection.execute(
                f'SELECT run_id FROM "{database.schema}".run_ownership WHERE run_id = %s',
                (run_id,),
            ).fetchall()
        assert rows == []
        with database.scoped_connection("org-a") as connection:
            rows = connection.execute(
                f'SELECT run_id FROM "{database.schema}".run_ownership WHERE run_id = %s',
                (run_id,),
            ).fetchall()
        assert [str(row[0]) for row in rows] == [run_id]
