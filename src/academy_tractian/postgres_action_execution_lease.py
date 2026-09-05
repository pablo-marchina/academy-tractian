from __future__ import annotations

from typing import Any

from .action_execution_lease import (
    ACTION_EXECUTION_LEASE_SCHEMA_VERSION,
    ActionExecutionLeaseClaim,
    ActionExecutionRecoveryReport,
)
from .postgres_operational import PostgresOperationalDatabase


class PostgresActionExecutionLeaseStore:
    """Non-replay lease for one consequential action transport attempt.

    The row is deliberately *not* a queue. An expired row cannot be claimed by another replica.
    Reconciliation converts the action, its execution run and any consumed idempotency claim to
    UNCERTAIN, because the external side effect may already have occurred.

    ``orphan_grace_seconds`` closes the small confirmation setup window in which custody has
    atomically moved to EXECUTING but the accepted execution row/lease has not yet been written.
    A recent lease-less action is left alone; a periodically observed lease-less action older than
    the grace converges to UNCERTAIN. An explicitly expired lease is uncertain immediately.
    """

    def __init__(
        self,
        database: PostgresOperationalDatabase,
        *,
        initialize: bool = False,
        orphan_grace_seconds: float = 5.0,
    ) -> None:
        if not 1.0 <= orphan_grace_seconds <= 300.0:
            raise ValueError("orphan_grace_seconds must be within [1, 300]")
        self.database = database
        self.schema = database.schema
        self.orphan_grace_seconds = float(orphan_grace_seconds)
        if initialize:
            self.initialize_schema()

    def _table(self) -> str:
        return f'"{self.schema}".action_execution_leases'

    def initialize_schema(self) -> None:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table()} (
                        action_id TEXT PRIMARY KEY
                            REFERENCES "{self.schema}".pending_actions(action_id) ON DELETE CASCADE,
                        execution_run_id TEXT UNIQUE NOT NULL
                            REFERENCES "{self.schema}".run_executions(run_id) ON DELETE CASCADE,
                        owner_instance_id TEXT NOT NULL,
                        generation INTEGER NOT NULL DEFAULT 1 CHECK (generation >= 1),
                        lease_expires_at TIMESTAMPTZ NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS action_execution_leases_expiry_idx
                    ON {self._table()} (lease_expires_at, action_id)
                    """
                )
                connection.execute(
                    f"""
                    INSERT INTO "{self.schema}".operational_meta(key, value)
                    VALUES ('action_execution_lease_schema_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (ACTION_EXECUTION_LEASE_SCHEMA_VERSION,),
                )

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                version = connection.execute(
                    f"""
                    SELECT value FROM "{self.schema}".operational_meta
                    WHERE key = 'action_execution_lease_schema_version'
                    """
                ).fetchone()
                if version is None or str(version[0]) != ACTION_EXECUTION_LEASE_SCHEMA_VERSION:
                    return False
                connection.execute(f"SELECT action_id FROM {self._table()} LIMIT 1").fetchall()
            return True
        except Exception:
            return False

    @staticmethod
    def _validate_owner(owner_instance_id: str) -> None:
        if not owner_instance_id or len(owner_instance_id) > 128:
            raise ValueError("owner_instance_id must be within [1, 128] characters")

    @staticmethod
    def _validate_lease(lease_seconds: float) -> None:
        if not 1.0 <= lease_seconds <= 3600.0:
            raise ValueError("lease_seconds must be within [1, 3600]")

    def acquire(
        self,
        *,
        action_id: str,
        execution_run_id: str,
        owner_instance_id: str,
        lease_seconds: float,
    ) -> ActionExecutionLeaseClaim | None:
        self._validate_owner(owner_instance_id)
        self._validate_lease(lease_seconds)
        if not action_id or not execution_run_id:
            raise ValueError("action_id and execution_run_id must be non-empty")

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                eligible = connection.execute(
                    f"""
                    SELECT a.action_id
                    FROM "{self.schema}".pending_actions AS a
                    JOIN "{self.schema}".run_executions AS e
                      ON e.run_id = a.execution_run_id
                    WHERE a.action_id = %s
                      AND a.execution_run_id = %s
                      AND a.state = 'EXECUTING'
                      AND e.execution_kind = 'action'
                      AND e.state IN ('accepted', 'running')
                    FOR UPDATE OF a, e
                    """,
                    (action_id, execution_run_id),
                ).fetchone()
                if eligible is None:
                    return None
                inserted = connection.execute(
                    f"""
                    INSERT INTO {self._table()}(
                        action_id, execution_run_id, owner_instance_id, generation,
                        lease_expires_at
                    ) VALUES (
                        %s, %s, %s, 1,
                        CURRENT_TIMESTAMP + (%s * INTERVAL '1 second')
                    )
                    ON CONFLICT DO NOTHING
                    RETURNING generation
                    """,
                    (action_id, execution_run_id, owner_instance_id, lease_seconds),
                ).fetchone()
                if inserted is None:
                    return None
        return ActionExecutionLeaseClaim(
            action_id=action_id,
            execution_run_id=execution_run_id,
            owner_instance_id=owner_instance_id,
            generation=int(inserted[0]),
        )

    def renew(
        self,
        *,
        claim: ActionExecutionLeaseClaim,
        lease_seconds: float,
    ) -> bool:
        self._validate_owner(claim.owner_instance_id)
        self._validate_lease(lease_seconds)
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE {self._table()} AS l
                    SET lease_expires_at = CURRENT_TIMESTAMP + (%s * INTERVAL '1 second'),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE l.action_id = %s
                      AND l.execution_run_id = %s
                      AND l.owner_instance_id = %s
                      AND l.generation = %s
                      AND l.lease_expires_at > CURRENT_TIMESTAMP
                      AND EXISTS (
                          SELECT 1 FROM "{self.schema}".pending_actions AS a
                          WHERE a.action_id = l.action_id AND a.state = 'EXECUTING'
                      )
                    RETURNING l.action_id
                    """,
                    (
                        lease_seconds,
                        claim.action_id,
                        claim.execution_run_id,
                        claim.owner_instance_id,
                        claim.generation,
                    ),
                ).fetchone()
        return row is not None

    def is_current_owner(self, claim: ActionExecutionLeaseClaim) -> bool:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT 1
                FROM {self._table()} AS l
                JOIN "{self.schema}".pending_actions AS a USING (action_id)
                WHERE l.action_id = %s
                  AND l.execution_run_id = %s
                  AND l.owner_instance_id = %s
                  AND l.generation = %s
                  AND l.lease_expires_at > CURRENT_TIMESTAMP
                  AND a.state = 'EXECUTING'
                """,
                (
                    claim.action_id,
                    claim.execution_run_id,
                    claim.owner_instance_id,
                    claim.generation,
                ),
            ).fetchone()
        return row is not None

    def release_terminal(self, claim: ActionExecutionLeaseClaim) -> bool:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    DELETE FROM {self._table()}
                    WHERE action_id = %s
                      AND execution_run_id = %s
                      AND owner_instance_id = %s
                      AND generation = %s
                      AND lease_expires_at > CURRENT_TIMESTAMP
                    RETURNING action_id
                    """,
                    (
                        claim.action_id,
                        claim.execution_run_id,
                        claim.owner_instance_id,
                        claim.generation,
                    ),
                ).fetchone()
        return row is not None

    def reconcile_expired(self) -> ActionExecutionRecoveryReport:
        """Fence orphaned attempts to UNCERTAIN without ever issuing another transport call."""

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                rows = connection.execute(
                    f"""
                    SELECT a.action_id, a.execution_run_id
                    FROM "{self.schema}".pending_actions AS a
                    LEFT JOIN {self._table()} AS l USING (action_id)
                    WHERE a.state = 'EXECUTING'
                      AND (
                          l.lease_expires_at <= CURRENT_TIMESTAMP
                          OR (
                              l.action_id IS NULL
                              AND a.updated_at <= CURRENT_TIMESTAMP - (%s * INTERVAL '1 second')
                          )
                      )
                    ORDER BY a.action_id
                    FOR UPDATE OF a
                    """,
                    (self.orphan_grace_seconds,),
                ).fetchall()
                action_ids = tuple(str(row[0]) for row in rows)
                execution_run_ids = tuple(str(row[1]) for row in rows if row[1] is not None)
                if not action_ids:
                    return ActionExecutionRecoveryReport((), (), ())

                connection.execute(
                    f"""
                    UPDATE "{self.schema}".pending_actions
                    SET state = 'UNCERTAIN', updated_at = CURRENT_TIMESTAMP
                    WHERE action_id = ANY(%s) AND state = 'EXECUTING'
                    """,
                    (list(action_ids),),
                )
                ledger_rows = connection.execute(
                    f"""
                    UPDATE "{self.schema}".action_claims
                    SET state = 'UNCERTAIN', updated_at = CURRENT_TIMESTAMP
                    WHERE action_id = ANY(%s) AND state = 'CLAIMED'
                    RETURNING action_id
                    """,
                    (list(action_ids),),
                ).fetchall()
                if execution_run_ids:
                    execution_rows = connection.execute(
                        f"""
                        UPDATE "{self.schema}".run_executions
                        SET state = 'uncertain',
                            transition_count = transition_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE run_id = ANY(%s)
                          AND execution_kind = 'action'
                          AND state IN ('accepted', 'running')
                        RETURNING run_id
                        """,
                        (list(execution_run_ids),),
                    ).fetchall()
                else:
                    execution_rows = []
                connection.execute(
                    f"DELETE FROM {self._table()} WHERE action_id = ANY(%s)",
                    (list(action_ids),),
                )

        return ActionExecutionRecoveryReport(
            actions_marked_uncertain=tuple(sorted(action_ids)),
            execution_runs_marked_uncertain=tuple(sorted(str(row[0]) for row in execution_rows)),
            ledger_entries_marked_uncertain=tuple(sorted(str(row[0]) for row in ledger_rows)),
        )

    def snapshot(self) -> dict[str, Any]:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT
                    COUNT(*) FILTER (WHERE lease_expires_at > CURRENT_TIMESTAMP),
                    COUNT(*) FILTER (WHERE lease_expires_at <= CURRENT_TIMESTAMP),
                    COUNT(*)
                FROM {self._table()}
                """
            ).fetchone()
        assert row is not None
        return {
            "schema_version": ACTION_EXECUTION_LEASE_SCHEMA_VERSION,
            "active_leases": int(row[0]),
            "expired_leases": int(row[1]),
            "total_leases": int(row[2]),
            "orphan_grace_seconds": self.orphan_grace_seconds,
            "automatic_replay_enabled": False,
        }
