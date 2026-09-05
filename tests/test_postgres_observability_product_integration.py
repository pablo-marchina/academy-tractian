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

SECRET = "postgres-observability-product-secret-at-least-32-bytes"
ISSUER = "academy-postgres-observability-test"
AUDIENCE = "academy-product"


class FinalSource:
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Hosted PostgreSQL observability run completed.",
            },
        )


class NoopTransport:
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("final-only hosted observability test must not call transport")


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
        self.schema = f"academy_hosted_ops_{suffix}"
        self.observability_schema = f"academy_hosted_obs_{suffix}"
        self.role = f"academy_hosted_scoped_{suffix}"
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
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(self.observability_schema)
                )
            )
            connection.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(self.schema))
            )
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role)))


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _headers() -> dict[str, str]:
    now = int(time())
    token = issue_signed_runtime_token(
        secret=SECRET,
        claims=SignedRuntimeIdentityClaims(
            issuer=ISSUER,
            audience=AUDIENCE,
            token_id="hosted-postgres-observability-token",
            identity_id="identity-org-a-user-a",
            user_id="user-a",
            organization_id="org-a",
            permissions=tuple(sorted(DEFAULT_RUNTIME_PERMISSIONS)),
            issued_at=now - 30,
            expires_at=now + 300,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


def test_product_can_persist_runtime_and_safe_observability_without_local_duckdb(
    tmp_path: Path,
    postgres_fixture,
) -> None:
    unused_duckdb_path = tmp_path / "must-not-exist.duckdb"
    app = create_authenticated_postgres_action_capable_product_app(
        db_path=unused_duckdb_path,
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        decision_source_factory=FinalSource,
        transport_factory=NoopTransport,
        authorization_resolver=_resolver,
        runtime_identity_secret=SECRET,
        runtime_identity_issuer=ISSUER,
        runtime_identity_audience=AUDIENCE,
        schema=postgres_fixture.schema,
        observability_schema=postgres_fixture.observability_schema,
        observability_backend="postgresql",
        initialize_schema=True,
        actions_enabled=False,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            headers=_headers(),
            json={"user_request": "Prove hosted PostgreSQL observability."},
        )
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        future = app.state.run_execution_registry.future(run_id)
        assert future is not None
        future.result(timeout=15)

        assert app.state.observability_backend == "postgresql"
        assert client.get(f"/api/runs/{run_id}", headers=_headers()).status_code == 200
        assert client.get(f"/api/runs/{run_id}/evaluation", headers=_headers()).status_code == 200

        database = app.state.postgres_operational_database
        with database.internal_pool.connection() as connection:
            run_rows = connection.execute(
                f'SELECT run_id, completed FROM "{postgres_fixture.observability_schema}".runs '
                "WHERE run_id = %s",
                (run_id,),
            ).fetchall()
            event_count = connection.execute(
                f'SELECT COUNT(*) FROM "{postgres_fixture.observability_schema}".events '
                "WHERE run_id = %s",
                (run_id,),
            ).fetchone()[0]
        assert [(str(row[0]), bool(row[1])) for row in run_rows] == [(run_id, True)]
        assert int(event_count) > 0

    assert not unused_duckdb_path.exists()
    assert not unused_duckdb_path.with_name("must-not-exist.access.duckdb").exists()
    assert not unused_duckdb_path.with_name("must-not-exist.execution.duckdb").exists()
