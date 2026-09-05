from __future__ import annotations

from hashlib import sha256
import os
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from psycopg import connect, sql

from academy_tractian.observability import safe_run_id
from academy_tractian.postgres_action_execution_lease import PostgresActionExecutionLeaseStore
from academy_tractian.postgres_action_operational import (
    PostgresActionIdempotencyLedger,
    PostgresPendingActionCustody,
)
from academy_tractian.postgres_operational import (
    PostgresOperationalDatabase,
    PostgresRunAccessStore,
    PostgresRunExecutionStore,
)
from academy_tractian.runtime import canonical_tool_registry


pytestmark = pytest.mark.skipif(
    not os.environ.get("POSTGRES_OPERATIONAL_TEST_DSN"),
    reason="POSTGRES_OPERATIONAL_TEST_DSN is required",
)


ACTION_ARGS = {
    "analysis_id": "analysis-lease-1",
    "body": {"justification": "Exact confirmed action for lease fencing proof."},
}


class _PgFixture:
    def __init__(self, admin_dsn: str) -> None:
        self.admin_dsn = admin_dsn
        suffix = uuid4().hex[:12]
        self.schema = f"academy_action_lease_{suffix}"
        self.role = f"academy_action_lease_scoped_{suffix}"
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


def _seed_action(database: PostgresOperationalDatabase):
    origin_raw = "origin-action-lease"
    origin_run = safe_run_id(origin_raw)
    execution_run = safe_run_id("action-execution-lease")
    access = PostgresRunAccessStore(database)
    executions = PostgresRunExecutionStore(database)
    assert access.claim(run_id=origin_run, organization_id="org-a", user_id="user-a")

    custody = PostgresPendingActionCustody(database, initialize=True)
    ledger = PostgresActionIdempotencyLedger(database, initialize=True)
    lease_store = PostgresActionExecutionLeaseStore(
        database,
        initialize=True,
        orphan_grace_seconds=5,
    )
    tool = canonical_tool_registry()["reprocess_analysis"]
    pending = custody.create_or_get(
        origin_raw_run_id=origin_raw,
        requester_user_id="user-a",
        tool=tool,
        arguments=ACTION_ARGS,
    )
    private = custody.get_private_for_requester(
        action_id=pending.action_id,
        requester_user_id="user-a",
    )
    assert custody.transition(
        action_id=pending.action_id,
        expected_states=frozenset({"PENDING_CONFIRMATION"}),
        new_state="EXECUTING",
        execution_run_id=execution_run,
    )
    assert access.claim(run_id=execution_run, organization_id="org-a", user_id="user-a")
    executions.create_accepted(
        run_id=execution_run,
        execution_kind="action",
        related_action_id=pending.action_id,
    )
    key_sha = sha256(private.idempotency_key.encode("utf-8")).hexdigest()
    assert ledger.claim(
        key_sha256=key_sha,
        action_fingerprint=pending.action_fingerprint,
        action_id=pending.action_id,
    )
    return pending.action_id, execution_run, custody, ledger, executions, lease_store, key_sha


def _expire(database: PostgresOperationalDatabase, action_id: str) -> None:
    with database.internal_pool.connection() as connection:
        with connection.transaction():
            connection.execute(
                f"""
                UPDATE "{database.schema}".action_execution_leases
                SET lease_expires_at = CURRENT_TIMESTAMP - INTERVAL '1 second'
                WHERE action_id = %s
                """,
                (action_id,),
            )


def _age_lease_less_action(database: PostgresOperationalDatabase, action_id: str) -> None:
    with database.internal_pool.connection() as connection:
        with connection.transaction():
            connection.execute(
                f"""
                UPDATE "{database.schema}".pending_actions
                SET updated_at = CURRENT_TIMESTAMP - INTERVAL '10 seconds'
                WHERE action_id = %s
                """,
                (action_id,),
            )


def test_healthy_action_lease_is_not_reconciled_or_reclaimed(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, _, executions, leases, _ = _seed_action(database)
        claim = leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-a",
            lease_seconds=30,
        )
        assert claim is not None
        assert leases.is_current_owner(claim) is True
        assert leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-b",
            lease_seconds=30,
        ) is None

        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == ()
        assert custody.get_safe(action_id).state == "EXECUTING"
        assert executions.get(execution_run).state == "accepted"  # type: ignore[union-attr]
        assert leases.snapshot()["automatic_replay_enabled"] is False
    finally:
        database.close()


def test_expired_action_lease_converges_uncertain_and_never_transfers(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, ledger, executions, leases, key_sha = _seed_action(database)
        claim = leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-a",
            lease_seconds=30,
        )
        assert claim is not None
        _expire(database, action_id)

        assert leases.is_current_owner(claim) is False
        assert leases.renew(claim=claim, lease_seconds=30) is False
        assert leases.release_terminal(claim) is False
        assert leases.acquire(
            action_id=action_id,
            execution_run_id=execution_run,
            owner_instance_id="replica-b",
            lease_seconds=30,
        ) is None

        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == (action_id,)
        assert report.execution_runs_marked_uncertain == (execution_run,)
        assert report.ledger_entries_marked_uncertain == (action_id,)
        assert custody.get_safe(action_id).state == "UNCERTAIN"
        assert ledger.get(key_sha)["state"] == "UNCERTAIN"  # type: ignore[index]
        assert executions.get(execution_run).state == "uncertain"  # type: ignore[union-attr]
        assert leases.snapshot()["total_leases"] == 0
    finally:
        database.close()


def test_recent_executing_action_without_lease_gets_setup_grace(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, ledger, executions, leases, key_sha = _seed_action(database)
        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == ()
        assert custody.get_safe(action_id).state == "EXECUTING"
        assert ledger.get(key_sha)["state"] == "CLAIMED"  # type: ignore[index]
        assert executions.get(execution_run).state == "accepted"  # type: ignore[union-attr]
    finally:
        database.close()


def test_stale_executing_action_without_lease_is_fail_safe_uncertain(postgres_fixture) -> None:
    database = _database(postgres_fixture)
    try:
        action_id, execution_run, custody, ledger, executions, leases, key_sha = _seed_action(database)
        _age_lease_less_action(database, action_id)
        report = leases.reconcile_expired()
        assert report.actions_marked_uncertain == (action_id,)
        assert custody.get_safe(action_id).state == "UNCERTAIN"
        assert ledger.get(key_sha)["state"] == "UNCERTAIN"  # type: ignore[index]
        assert executions.get(execution_run).state == "uncertain"  # type: ignore[union-attr]
    finally:
        database.close()
