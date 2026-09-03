from __future__ import annotations

import json
import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql
from psycopg.errors import CheckViolation

from academy_tractian.operational_value_pilot import OperationalPilotTask
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.postgres_operational_value_v5 import PostgresOperationalPilotStoreV5


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_pilot_v5_{suffix}"
        self.role = f"academy_pilot_v5_scoped_{suffix}"
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


def _database(fixture: _PgFixture) -> PostgresOperationalDatabase:
    return PostgresOperationalDatabase(
        internal_dsn=fixture.admin_dsn,
        scoped_dsn=fixture.scoped_dsn,
        schema=fixture.schema,
        initialize=True,
    )


def _seed_active_assignment(
    database: PostgresOperationalDatabase,
    *,
    assignment_id: str,
    user_id: str,
) -> tuple[str, str, str]:
    packet_id = "ovpkt_" + "a" * 24
    task_id = "ovt_" + "b" * 24
    pair_id = "ovpair_" + "c" * 24
    task = OperationalPilotTask(
        task_id=task_id,
        condition="MANUAL",
        ticket_request="Investigate the operational ticket and record a conclusion.",
    )
    with database.internal_pool.connection() as connection:
        with connection.transaction():
            connection.execute(
                f"""
                INSERT INTO "{database.schema}".operational_pilot_tasks(
                    organization_id, packet_id, task_id, pair_id, condition,
                    display_order, task_payload, active
                )
                VALUES (%s, %s, %s, %s, 'MANUAL', 0, %s::jsonb, TRUE)
                """,
                (
                    "org-a",
                    packet_id,
                    task_id,
                    pair_id,
                    json.dumps(task.model_dump(mode="json")),
                ),
            )
            connection.execute(
                f"""
                INSERT INTO "{database.schema}".operational_pilot_assignments(
                    assignment_id, organization_id, packet_id, task_id, pair_id,
                    user_id, operator_ref_sha256, host_session_id, state
                )
                VALUES (%s, 'org-a', %s, %s, %s, %s, %s, %s, 'ACTIVE')
                """,
                (
                    assignment_id,
                    packet_id,
                    task_id,
                    pair_id,
                    user_id,
                    "d" * 64,
                    "ovhost_" + "e" * 24,
                ),
            )
    return packet_id, task_id, pair_id


def test_v5_human_termination_persists_only_invalid_trial_material(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        store = PostgresOperationalPilotStoreV5(database, initialize=True)
        assert store.ready() is True
        assignment_id = "ova_" + "1" * 24
        packet_id, task_id, _ = _seed_active_assignment(
            database,
            assignment_id=assignment_id,
            user_id="user-a",
        )

        completion = store.terminate_active(
            assignment_id=assignment_id,
            organization_id="org-a",
            user_id="user-a",
            terminal_status="WITHDRAWN",
        )
        assert completion.packet_id == packet_id
        assert completion.task_id == task_id
        assert completion.status == "WITHDRAWN"
        assert completion.elapsed_seconds is None
        assert completion.terminal_decision is None
        assert completion.conclusion_summary is None
        assert completion.invalid_reason == "operator_withdrew"

        with database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT state, elapsed_seconds, terminal_decision, conclusion_summary, invalid_reason
                FROM "{database.schema}".operational_pilot_assignments
                WHERE assignment_id = %s
                """,
                (assignment_id,),
            ).fetchone()
        assert row == ("WITHDRAWN", None, None, None, "operator_withdrew")
    finally:
        database.close()


def test_v5_database_rejects_invalid_trial_with_elapsed_or_conclusion(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        store = PostgresOperationalPilotStoreV5(database, initialize=True)
        assert store.ready() is True
        assignment_id = "ova_" + "2" * 24
        _seed_active_assignment(database, assignment_id=assignment_id, user_id="user-b")

        with pytest.raises(CheckViolation):
            with database.internal_pool.connection() as connection:
                with connection.transaction():
                    connection.execute(
                        f"""
                        UPDATE "{database.schema}".operational_pilot_assignments
                        SET state = 'INTERRUPTED',
                            finished_at = CURRENT_TIMESTAMP,
                            elapsed_seconds = 3.5,
                            terminal_decision = 'FINAL',
                            conclusion_summary = 'Must be rejected.',
                            invalid_reason = 'operator_interrupted'
                        WHERE assignment_id = %s
                        """,
                        (assignment_id,),
                    )
    finally:
        database.close()


def test_v5_ready_requires_validated_v5_constraint_and_migrates_from_v4_metadata(
    postgres_fixture: _PgFixture,
) -> None:
    database = _database(postgres_fixture)
    try:
        store = PostgresOperationalPilotStoreV5(database, initialize=True)
        assert store.ready() is True

        with database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    ALTER TABLE "{database.schema}".operational_pilot_assignments
                    DROP CONSTRAINT operational_pilot_assignment_state_shape_v5
                    """
                )
                connection.execute(
                    f"""
                    UPDATE "{database.schema}".operational_meta
                    SET value = 'operational-value-collection-v4'
                    WHERE key = 'operational_value_collection_schema_version'
                    """
                )
        assert store.ready() is False

        store.initialize_schema()
        assert store.ready() is True
        with database.internal_pool.connection() as connection:
            row = connection.execute(
                """
                SELECT c.convalidated
                FROM pg_constraint c
                JOIN pg_class t ON t.oid = c.conrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE n.nspname = %s
                  AND t.relname = 'operational_pilot_assignments'
                  AND c.conname = 'operational_pilot_assignment_state_shape_v5'
                """,
                (database.schema,),
            ).fetchone()
        assert row is not None and bool(row[0]) is True
    finally:
        database.close()
