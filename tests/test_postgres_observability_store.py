from __future__ import annotations

import json
import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from research.e2.models import RunTrace, TraceEvent

from academy_tractian.observability import project_trace, safe_run_id
from academy_tractian.observability_store import ObservabilityStore
from academy_tractian.postgres_observability_store import PostgresObservabilityStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_obs_{suffix}"
        self.role = f"academy_obs_scoped_{suffix}"
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
            connection.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(self.role)))


@pytest.fixture
def postgres_fixture():
    fixture = _PgFixture(os.environ["POSTGRES_OPERATIONAL_TEST_DSN"])
    try:
        yield fixture
    finally:
        fixture.cleanup()


def _trace(secret: str = "POSTGRES-OBS-RAW-SECRET") -> RunTrace:
    return RunTrace(
        run_id="raw-postgres-observability-run",
        scenario_id="prod:postgres-observability",
        config_hash="b" * 64,
        identity_binding_id="private-identity",
        seed_ref="private-seed",
        events=[
            TraceEvent(sequence=0, event_type="run_started", metadata={"execution_mode": "live"}),
            TraceEvent(
                sequence=1,
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
                sequence=2,
                event_type="tool_result",
                tool_name="get_asset",
                result={"headers": {"authorization": secret}, "body": {"secret": secret}},
                metadata={"status_code": 200},
            ),
            TraceEvent(
                sequence=3,
                event_type="observation",
                tool_name="get_asset",
                result={"secret": secret},
                metadata={"status_code": 200, "evidence_id": "EV-postgres-safe"},
            ),
            TraceEvent(
                sequence=4,
                event_type="final_response",
                result={
                    "decision": "ORIENT",
                    "response_mode": "complete",
                    "message": "Safe shared-store conclusion",
                    "secret": secret,
                },
            ),
            TraceEvent(sequence=5, event_type="run_finished"),
        ],
    )


def _database(fixture: _PgFixture, *, initialize: bool) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize=initialize,
    )


def test_store_facade_selects_shared_postgres_backend(postgres_fixture) -> None:
    database = _database(postgres_fixture, initialize=True)
    try:
        PostgresObservabilityStore(database, initialize=True)
        store = ObservabilityStore(database)
        assert isinstance(store, PostgresObservabilityStore)
        assert store.ready() is True
    finally:
        database.close()


def test_two_independent_database_instances_share_safe_projection(postgres_fixture) -> None:
    first_database = _database(postgres_fixture, initialize=True)
    PostgresObservabilityStore(first_database, initialize=True)
    second_database = _database(postgres_fixture, initialize=False)
    first = PostgresObservabilityStore(first_database)
    second = PostgresObservabilityStore(second_database)
    trace = _trace()

    try:
        run_id = first.persist_trace(trace)
        assert run_id == safe_run_id(trace.run_id)
        assert second.ready() is True
        assert second.get_run(run_id) == first.get_run(run_id)
        assert second.get_events(run_id) == first.get_events(run_id)
        assert second.get_evidence(run_id) == first.get_evidence(run_id)

        serialized = json.dumps(
            {
                "run": second.get_run(run_id),
                "events": second.get_events(run_id),
                "evidence": second.get_evidence(run_id),
            },
            sort_keys=True,
            default=str,
        )
        assert "POSTGRES-OBS-RAW-SECRET" not in serialized
        assert "private-identity" not in serialized
        assert "private-seed" not in serialized
        assert "raw-postgres-observability-run" not in serialized
        assert "authorization" not in serialized
        assert "resolved_path" not in serialized
        assert "Safe shared-store conclusion" in serialized

        with second_database.internal_pool.connection() as connection:
            for table in (
                "observability_runs",
                "observability_events",
                "observability_evidence",
                "observability_evaluations",
            ):
                rows = connection.execute(
                    f'SELECT * FROM "{postgres_fixture.schema}".{table}'
                ).fetchall()
                assert "POSTGRES-OBS-RAW-SECRET" not in repr(rows)
    finally:
        second_database.close()
        first_database.close()


def test_duplicate_live_publication_is_idempotent_across_instances(postgres_fixture) -> None:
    first_database = _database(postgres_fixture, initialize=True)
    PostgresObservabilityStore(first_database, initialize=True)
    second_database = _database(postgres_fixture, initialize=False)
    first = PostgresObservabilityStore(first_database)
    second = PostgresObservabilityStore(second_database)
    run, events, _ = project_trace(_trace("DUPLICATE-RAW-SECRET"))

    try:
        assert first.persist_live_update(run=run, event=events[0]) is True
        assert second.persist_live_update(run=run, event=events[0]) is False
        persisted = second.get_events(run.run_id)
        assert len(persisted) == 1
        assert persisted[0]["event_id"] == events[0].event_id
    finally:
        second_database.close()
        first_database.close()
