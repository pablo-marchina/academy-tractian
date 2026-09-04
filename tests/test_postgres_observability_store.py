from __future__ import annotations

import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from academy_tractian.observability import (
    SafeEvaluation,
    SafeEvaluationCheck,
    SafeEvidenceRef,
    SafeEvent,
    SafeRun,
)
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
        self.operational_schema = f"academy_obs_ops_{suffix}"
        self.observability_schema = f"academy_obs_{suffix}"
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


def _safe_run(*, completed: bool = False, event_count: int = 1) -> SafeRun:
    return SafeRun(
        run_id="run_postgres_observability",
        scenario_id="hosted-observability-test",
        config_hash="config-hash",
        event_count=event_count,
        model_calls=0,
        tool_proposals=0,
        tool_calls=0,
        policy_blocks=0,
        errors=0,
        terminal_decision="ORIENT" if completed else None,
        terminal_response_mode="complete" if completed else None,
        terminal_reason_code=None,
        terminal_message="Completed safely." if completed else None,
        completed=completed,
    )


def _event(*, sequence: int = 0, event_type: str = "run_started") -> SafeEvent:
    return SafeEvent(
        event_id=f"run_postgres_observability:{sequence}",
        run_id="run_postgres_observability",
        sequence=sequence,
        event_type=event_type,
        origin="SYSTEM" if event_type == "run_started" else "OBSERVATION",
        evidence_id="EV-postgres" if event_type == "observation" else None,
        status_code=200 if event_type == "observation" else None,
    )


def test_postgres_observability_store_round_trip_and_idempotency(postgres_fixture) -> None:
    database = PostgresOperationalDatabase(
        internal_dsn=postgres_fixture.admin_dsn,
        scoped_dsn=postgres_fixture.scoped_dsn,
        schema=postgres_fixture.operational_schema,
        initialize=True,
    )
    try:
        store = PostgresObservabilityStore(
            database,
            schema=postgres_fixture.observability_schema,
            initialize=True,
        )
        assert store.ready() is True

        first = _event()
        assert store.persist_live_update(run=_safe_run(), event=first) is True
        assert store.persist_live_update(run=_safe_run(), event=first) is False

        observation = _event(sequence=1, event_type="observation")
        evidence = SafeEvidenceRef(
            evidence_id="EV-postgres",
            run_id="run_postgres_observability",
            sequence=1,
            tool_name="get_asset",
            status_code=200,
        )
        assert (
            store.persist_live_update(
                run=_safe_run(event_count=2),
                event=observation,
                evidence=evidence,
            )
            is True
        )

        evaluation = SafeEvaluation(
            run_id="run_postgres_observability",
            blocking_pass=True,
            checks=(SafeEvaluationCheck(name="trace_integrity", passed=True, blocking=True),),
        )
        store.persist_projection(
            _safe_run(completed=True, event_count=2),
            (first, observation),
            (evidence,),
            evaluation=evaluation,
        )

        run = store.get_run("run_postgres_observability")
        assert run is not None
        assert run["completed"] is True
        assert run["terminal_decision"] == "ORIENT"
        assert len(store.get_events("run_postgres_observability")) == 2
        assert len(store.get_events_after("run_postgres_observability", after_sequence=0)) == 1
        assert store.get_evidence("run_postgres_observability") == [
            {
                "evidence_id": "EV-postgres",
                "run_id": "run_postgres_observability",
                "sequence": 1,
                "tool_name": "get_asset",
                "status_code": 200,
            }
        ]
        assert store.get_evaluation("run_postgres_observability") == [
            {
                "run_id": "run_postgres_observability",
                "check_name": "trace_integrity",
                "passed": True,
                "blocking": True,
                "blocking_pass": True,
            }
        ]
        assert store.overview()["completed_runs"] == 1
        assert len(store.list_runs()) == 1
    finally:
        database.close()
