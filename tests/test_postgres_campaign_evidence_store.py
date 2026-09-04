from __future__ import annotations

from datetime import datetime, timezone
import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from academy_tractian.postgres_campaign_evidence_store import PostgresCampaignEvidenceStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    CampaignProofRecord,
)


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.operational_schema = f"academy_campaign_ops_{suffix}"
        self.observability_schema = f"academy_campaign_obs_{suffix}"
        self.role = f"academy_campaign_scoped_{suffix}"
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


def _database(postgres_fixture, *, initialize: bool) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.operational_schema,
        initialize=initialize,
    )


def _evidence(
    *,
    dimension: str = "response_normalization_verified",
    passed: bool = True,
) -> CampaignProofRecord:
    return CampaignProofRecord.model_validate(
        {
            "operation": "get_company",
            "dimension": dimension,
            "environment": "hosted_live",
            "passed": passed,
            "observed_at": datetime.now(timezone.utc),
            "probe_id": f"postgres-campaign-{uuid4().hex}",
            "evidence_ref": "postgres-campaign-test",
            "fingerprint": "sha256:" + uuid4().hex.ljust(64, "0"),
        }
    )


def test_postgres_campaign_store_is_bounded_and_survives_database_reopen(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresCampaignEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        assert store.ready() is True

        store.persist(_evidence())
        store.persist(_evidence())
        store.persist(_evidence(dimension="invalid_parameters_rejected"))

        assert store.observation_counts() == {
            ("get_company", "invalid_parameters_rejected", True): 1,
            ("get_company", "response_normalization_verified", True): 2,
        }
        ledger = store.ledger()
        assert ledger.state == "VALID"
        assert len(ledger.records) == 2
        assert len(ledger.records_for("get_company", "response_normalization_verified")) == 1
    finally:
        database.close()

    reopened = _database(postgres_fixture, initialize=False)
    try:
        store = PostgresCampaignEvidenceStore(
            reopened,
            schema=postgres_fixture.observability_schema,
            initialize=False,
        )
        assert store.ready() is True
        assert store.ledger().state == "VALID"
        assert store.observation_counts()[
            ("get_company", "response_normalization_verified", True)
        ] == 2
    finally:
        reopened.close()


def test_postgres_campaign_store_preserves_fail_and_pass_as_separate_proof(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresCampaignEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        store.persist(_evidence(passed=True))
        store.persist(_evidence(passed=False))
        store.persist(_evidence(passed=True))

        ledger = store.ledger()
        records = ledger.records_for("get_company", "response_normalization_verified")
        assert ledger.state == "VALID"
        assert {record.passed for record in records} == {True, False}
        assert store.observation_counts() == {
            ("get_company", "response_normalization_verified", False): 1,
            ("get_company", "response_normalization_verified", True): 2,
        }
    finally:
        database.close()


def test_postgres_campaign_store_rejects_invalid_atomic_ledger(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresCampaignEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        with pytest.raises(ValueError, match="invalid campaign evidence ledger"):
            store.persist_ledger(
                CampaignEvidenceLedger(
                    source_label="test:invalid",
                    state="INVALID",
                    validation_errors=("contract:unknown_operation",),
                )
            )
        assert store.observation_counts() == {}
    finally:
        database.close()


def test_corrupted_semantic_operation_fails_closed_instead_of_inflating_campaign(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        store = PostgresCampaignEvidenceStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        store.persist(_evidence())
        with database.internal_pool.connection() as connection:
            connection.execute(
                f'UPDATE "{postgres_fixture.observability_schema}".tractian_campaign_evidence '
                "SET operation = 'invented_operation' WHERE operation = 'get_company'"
            )
            connection.commit()

        ledger = store.ledger()
        assert ledger.state == "INVALID"
        assert ledger.records == ()
        assert ledger.validation_errors == ("contract:unknown_operation",)
    finally:
        database.close()
