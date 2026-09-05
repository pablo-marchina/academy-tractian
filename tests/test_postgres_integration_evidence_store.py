from __future__ import annotations

from datetime import datetime, timezone
import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from academy_tractian.postgres_integration_evidence_store import PostgresIntegrationEvidenceStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.tractian_integration_evidence import OperationEvidence


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.operational_schema = f"academy_evidence_ops_{suffix}"
        self.observability_schema = f"academy_evidence_obs_{suffix}"
        self.role = f"academy_evidence_scoped_{suffix}"
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
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(self.operational_schema)
                )
            )
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role)))


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _evidence(
    *,
    outcome: str = "success",
    status: int | None = 200,
    environment: str = "hosted_live",
) -> OperationEvidence:
    return OperationEvidence(
        operation="get_company",
        environment=environment,
        outcome=outcome,
        method="GET",
        path_template="/companies/{companyId}",
        observed_at=datetime.now(timezone.utc),
        probe_id=f"postgres-evidence-{uuid4().hex}",
        evidence_ref="postgres-evidence-test",
        fingerprint="sha256:" + uuid4().hex.ljust(64, "0"),
        http_status=status,
    )


def _database(postgres_fixture, *, initialize: bool) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.operational_schema,
        initialize=initialize,
    )


def test_postgres_evidence_store_is_bounded_and_survives_database_reopen(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresIntegrationEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        assert store.ready() is True

        store.persist(_evidence())
        store.persist(_evidence())
        store.persist(_evidence(outcome="http_error_observed", status=503))

        assert store.observation_counts() == {
            ("get_company", "http_error_observed"): 1,
            ("get_company", "success"): 2,
        }
        ledger = store.ledger()
        assert ledger.state == "VALID"
        assert ledger.unique_route_observed_operations("hosted_live") == {"get_company"}
        assert ledger.unique_success_operations("hosted_live") == {"get_company"}
        # The persistent table is bounded by operation/outcome, not request volume.
        assert len(ledger.records) == 2
    finally:
        database.close()

    reopened = _database(postgres_fixture, initialize=False)
    try:
        store = PostgresIntegrationEvidenceStore(
            reopened,
            schema=postgres_fixture.observability_schema,
            initialize=False,
        )
        assert store.ready() is True
        ledger = store.ledger()
        assert ledger.state == "VALID"
        assert ledger.unique_route_observed_operations("hosted_live") == {"get_company"}
        assert store.observation_counts()[("get_company", "success")] == 2
    finally:
        reopened.close()


def test_postgres_store_rejects_non_hosted_evidence(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresIntegrationEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        with pytest.raises(ValueError, match="hosted_live"):
            store.persist(_evidence(environment="frozen"))
        assert store.observation_counts() == {}
    finally:
        database.close()


def test_corrupted_persistent_route_fails_closed_instead_of_inflating_coverage(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresIntegrationEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        store.persist(_evidence())
        with database.internal_pool.connection() as connection:
            connection.execute(
                f'UPDATE "{postgres_fixture.observability_schema}".tractian_integration_evidence '
                "SET path_template = '/tampered' WHERE operation = 'get_company'"
            )
            connection.commit()

        ledger = store.ledger()
        assert ledger.state == "INVALID"
        assert ledger.records == ()
        assert ledger.validation_errors == ("contract:route_mismatch",)
    finally:
        database.close()
