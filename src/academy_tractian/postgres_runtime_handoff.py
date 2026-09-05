from __future__ import annotations

from typing import Any

from .postgres_operational import PostgresOperationalDatabase
from .product_storage_contracts import (
    RUNTIME_HANDOFF_SCHEMA_VERSION,
    DurableExecution,
    ExecutionState,
    RuntimeExecutionEnvelope,
    RuntimeHandoffClaim,
)


class PostgresRuntimeHandoffStore:
    """Durable multi-replica queue/lease for read-only runtime executions.

    The queue is deliberately PostgreSQL-native: consumers claim rows with
    ``FOR UPDATE ... SKIP LOCKED`` and receive a monotonically increasing generation token.
    Only the current non-expired owner/generation may use tools, publish or finalize a run.
    Runtime envelopes are deleted on terminal completion/failure so private user input is
    retained only while recovery needs it.

    This store owns read-only runtime recovery only. Consequential action execution has a separate
    non-transferable lease/custody/idempotency authority and must never be terminalized here. Legacy
    runtime rows without a private handoff envelope become interrupted; recoverable runtime rows
    with an envelope remain available for lease-based takeover.
    """

    def __init__(
        self,
        database: PostgresOperationalDatabase,
        *,
        initialize: bool = False,
    ) -> None:
        self.database = database
        self.schema = database.schema
        if initialize:
            self.initialize_schema()

    def _table(self) -> str:
        return f'"{self.schema}".runtime_work_items'

    def initialize_schema(self) -> None:
        table = self._table()
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table} (
                        run_id TEXT PRIMARY KEY REFERENCES "{self.schema}".run_executions(run_id)
                            ON DELETE CASCADE,
                        request_id TEXT NOT NULL,
                        identity_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        user_request TEXT NOT NULL,
                        seed TEXT,
                        owner_instance_id TEXT,
                        claim_generation INTEGER NOT NULL DEFAULT 0 CHECK (claim_generation >= 0),
                        claim_count INTEGER NOT NULL DEFAULT 0 CHECK (claim_count >= 0),
                        recovery_count INTEGER NOT NULL DEFAULT 0 CHECK (recovery_count >= 0),
                        lease_expires_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CHECK (
                            (owner_instance_id IS NULL AND lease_expires_at IS NULL)
                            OR (owner_instance_id IS NOT NULL AND lease_expires_at IS NOT NULL)
                        )
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS runtime_work_items_claim_idx
                    ON {table} (lease_expires_at, created_at, run_id)
                    """
                )
                connection.execute(
                    f"""
                    INSERT INTO "{self.schema}".operational_meta(key, value)
                    VALUES ('runtime_handoff_schema_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (RUNTIME_HANDOFF_SCHEMA_VERSION,),
                )

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                version_row = connection.execute(
                    f"""
                    SELECT value FROM "{self.schema}".operational_meta
                    WHERE key = 'runtime_handoff_schema_version'
                    """
                ).fetchone()
                if version_row is None or str(version_row[0]) != RUNTIME_HANDOFF_SCHEMA_VERSION:
                    return False
                connection.execute(f"SELECT run_id FROM {self._table()} LIMIT 1").fetchall()
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

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if not 1 <= limit <= 64:
            raise ValueError("claim limit must be within [1, 64]")

    @staticmethod
    def _validate_generation(claim_generation: int) -> None:
        if claim_generation < 1:
            raise ValueError("claim_generation must be >= 1")

    def enqueue(self, envelope: RuntimeExecutionEnvelope) -> None:
        if not all(
            (
                envelope.run_id,
                envelope.request_id,
                envelope.identity_id,
                envelope.user_id,
                envelope.user_request,
            )
        ):
            raise ValueError("runtime handoff envelope fields must be non-empty")
        if len(envelope.user_request) > 20000:
            raise ValueError("runtime handoff user_request exceeds product request limit")

        table = self._table()
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                execution = connection.execute(
                    f"""
                    SELECT e.execution_kind, e.state, o.user_id
                    FROM "{self.schema}".run_executions AS e
                    JOIN "{self.schema}".run_ownership AS o USING (run_id)
                    WHERE e.run_id = %s
                    FOR UPDATE OF e
                    """,
                    (envelope.run_id,),
                ).fetchone()
                if execution is None:
                    raise RuntimeError("runtime_handoff_execution_missing")
                if str(execution[0]) != "runtime" or str(execution[1]) != "accepted":
                    raise RuntimeError("runtime_handoff_requires_accepted_runtime")
                if str(execution[2]) != envelope.user_id:
                    raise RuntimeError("runtime_handoff_user_ownership_mismatch")

                inserted = connection.execute(
                    f"""
                    INSERT INTO {table}(
                        run_id, request_id, identity_id, user_id, user_request, seed
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO NOTHING
                    RETURNING run_id
                    """,
                    (
                        envelope.run_id,
                        envelope.request_id,
                        envelope.identity_id,
                        envelope.user_id,
                        envelope.user_request,
                        envelope.seed,
                    ),
                ).fetchone()
                if inserted is not None:
                    return

                existing = connection.execute(
                    f"""
                    SELECT request_id, identity_id, user_id, user_request, seed
                    FROM {table}
                    WHERE run_id = %s
                    """,
                    (envelope.run_id,),
                ).fetchone()
                expected = (
                    envelope.request_id,
                    envelope.identity_id,
                    envelope.user_id,
                    envelope.user_request,
                    envelope.seed,
                )
                if existing != expected:
                    raise RuntimeError("runtime_handoff_envelope_conflict")

    @staticmethod
    def _claim_from_values(values: tuple[object, ...], *, owner: str) -> RuntimeHandoffClaim:
        return RuntimeHandoffClaim(
            envelope=RuntimeExecutionEnvelope(
                run_id=str(values[0]),
                request_id=str(values[1]),
                identity_id=str(values[2]),
                user_id=str(values[3]),
                user_request=str(values[4]),
                seed=None if values[5] is None else str(values[5]),
            ),
            owner_instance_id=owner,
            claim_generation=int(values[6]),
            previous_state=str(values[7]),  # type: ignore[arg-type]
            recovery_count=int(values[8]),
        )

    def _claim(
        self,
        *,
        owner_instance_id: str,
        lease_seconds: float,
        limit: int,
        run_id: str | None,
    ) -> tuple[RuntimeHandoffClaim, ...]:
        self._validate_owner(owner_instance_id)
        self._validate_lease(lease_seconds)
        self._validate_limit(limit)
        if run_id is not None and not run_id:
            raise ValueError("run_id must be non-empty")

        table = self._table()
        claims: list[RuntimeHandoffClaim] = []
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                parameters: list[object] = []
                run_filter = ""
                if run_id is not None:
                    run_filter = "AND w.run_id = %s"
                    parameters.append(run_id)
                parameters.append(limit)
                rows = connection.execute(
                    f"""
                    SELECT
                        w.run_id,
                        w.request_id,
                        w.identity_id,
                        w.user_id,
                        w.user_request,
                        w.seed,
                        w.claim_generation,
                        e.state,
                        w.recovery_count
                    FROM {table} AS w
                    JOIN "{self.schema}".run_executions AS e USING (run_id)
                    WHERE e.execution_kind = 'runtime'
                      AND e.state IN ('accepted', 'running')
                      AND (
                          w.owner_instance_id IS NULL
                          OR w.lease_expires_at <= CURRENT_TIMESTAMP
                      )
                      {run_filter}
                    ORDER BY w.created_at, w.run_id
                    FOR UPDATE OF w, e SKIP LOCKED
                    LIMIT %s
                    """,
                    tuple(parameters),
                ).fetchall()

                for row in rows:
                    values = tuple(row)
                    current_generation = int(values[6])
                    previous_state = str(values[7])
                    current_recovery_count = int(values[8])
                    new_generation = current_generation + 1
                    new_recovery_count = current_recovery_count + (1 if previous_state == "running" else 0)
                    connection.execute(
                        f"""
                        UPDATE {table}
                        SET owner_instance_id = %s,
                            claim_generation = %s,
                            claim_count = claim_count + 1,
                            recovery_count = %s,
                            lease_expires_at = CURRENT_TIMESTAMP + (%s * INTERVAL '1 second'),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE run_id = %s
                        """,
                        (
                            owner_instance_id,
                            new_generation,
                            new_recovery_count,
                            lease_seconds,
                            str(values[0]),
                        ),
                    )
                    connection.execute(
                        f"""
                        UPDATE "{self.schema}".run_executions
                        SET state = 'running',
                            transition_count = transition_count + 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE run_id = %s AND state IN ('accepted', 'running')
                        """,
                        (str(values[0]),),
                    )
                    claim_values = (
                        values[0],
                        values[1],
                        values[2],
                        values[3],
                        values[4],
                        values[5],
                        new_generation,
                        previous_state,
                        new_recovery_count,
                    )
                    claims.append(self._claim_from_values(claim_values, owner=owner_instance_id))
        return tuple(claims)

    def claim_specific(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        lease_seconds: float,
    ) -> RuntimeHandoffClaim | None:
        claims = self._claim(
            owner_instance_id=owner_instance_id,
            lease_seconds=lease_seconds,
            limit=1,
            run_id=run_id,
        )
        return claims[0] if claims else None

    def claim_available(
        self,
        *,
        owner_instance_id: str,
        lease_seconds: float,
        limit: int,
    ) -> tuple[RuntimeHandoffClaim, ...]:
        return self._claim(
            owner_instance_id=owner_instance_id,
            lease_seconds=lease_seconds,
            limit=limit,
            run_id=None,
        )

    def is_current_owner(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
    ) -> bool:
        self._validate_owner(owner_instance_id)
        self._validate_generation(claim_generation)
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT 1
                FROM {self._table()} AS w
                JOIN "{self.schema}".run_executions AS e USING (run_id)
                WHERE w.run_id = %s
                  AND w.owner_instance_id = %s
                  AND w.claim_generation = %s
                  AND w.lease_expires_at > CURRENT_TIMESTAMP
                  AND e.execution_kind = 'runtime'
                  AND e.state = 'running'
                """,
                (run_id, owner_instance_id, claim_generation),
            ).fetchone()
        return row is not None

    def renew(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
        lease_seconds: float,
    ) -> bool:
        self._validate_owner(owner_instance_id)
        self._validate_lease(lease_seconds)
        self._validate_generation(claim_generation)
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE {self._table()} AS w
                    SET lease_expires_at = CURRENT_TIMESTAMP + (%s * INTERVAL '1 second'),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE w.run_id = %s
                      AND w.owner_instance_id = %s
                      AND w.claim_generation = %s
                      AND w.lease_expires_at > CURRENT_TIMESTAMP
                      AND EXISTS (
                          SELECT 1 FROM "{self.schema}".run_executions AS e
                          WHERE e.run_id = w.run_id
                            AND e.execution_kind = 'runtime'
                            AND e.state = 'running'
                      )
                    RETURNING w.run_id
                    """,
                    (lease_seconds, run_id, owner_instance_id, claim_generation),
                ).fetchone()
                return row is not None

    def _finish(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
        state: ExecutionState,
    ) -> bool:
        self._validate_owner(owner_instance_id)
        self._validate_generation(claim_generation)
        if state not in {"completed", "failed"}:
            raise ValueError("runtime handoff terminal state must be completed or failed")

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                owned = connection.execute(
                    f"""
                    SELECT run_id FROM {self._table()}
                    WHERE run_id = %s
                      AND owner_instance_id = %s
                      AND claim_generation = %s
                      AND lease_expires_at > CURRENT_TIMESTAMP
                    FOR UPDATE
                    """,
                    (run_id, owner_instance_id, claim_generation),
                ).fetchone()
                if owned is None:
                    return False
                updated = connection.execute(
                    f"""
                    UPDATE "{self.schema}".run_executions
                    SET state = %s,
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE run_id = %s
                      AND execution_kind = 'runtime'
                      AND state = 'running'
                    RETURNING run_id
                    """,
                    (state, run_id),
                ).fetchone()
                if updated is None:
                    return False
                connection.execute(
                    f"DELETE FROM {self._table()} WHERE run_id = %s",
                    (run_id,),
                )
                return True

    def complete(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
    ) -> bool:
        return self._finish(
            run_id=run_id,
            owner_instance_id=owner_instance_id,
            claim_generation=claim_generation,
            state="completed",
        )

    def fail(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
    ) -> bool:
        return self._finish(
            run_id=run_id,
            owner_instance_id=owner_instance_id,
            claim_generation=claim_generation,
            state="failed",
        )

    @staticmethod
    def _execution(row: object) -> DurableExecution:
        values = tuple(row)  # type: ignore[arg-type]
        return DurableExecution(
            run_id=str(values[0]),
            execution_kind=str(values[1]),  # type: ignore[arg-type]
            state=str(values[2]),  # type: ignore[arg-type]
            related_action_id=None if values[3] is None else str(values[3]),
            transition_count=int(values[4]),
        )

    def reconcile_unrecoverable(self) -> tuple[DurableExecution, ...]:
        """Interrupt only read-only runtimes that cannot be reconstructed after replica loss.

        Action executions are outside this store's authority. Their non-transferable lease layer
        decides whether an attempt is healthy, in setup grace, expired or otherwise uncertain.
        Recoverable runtime rows with a private handoff envelope are left untouched for takeover.
        """

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                runtime_rows = connection.execute(
                    f"""
                    UPDATE "{self.schema}".run_executions AS e
                    SET state = 'interrupted',
                        transition_count = transition_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE e.execution_kind = 'runtime'
                      AND e.state IN ('accepted', 'running')
                      AND NOT EXISTS (
                          SELECT 1 FROM {self._table()} AS w WHERE w.run_id = e.run_id
                      )
                    RETURNING e.run_id, e.execution_kind, e.state, e.related_action_id,
                              e.transition_count
                    """
                ).fetchall()
        return tuple(sorted((self._execution(row) for row in runtime_rows), key=lambda item: item.run_id))

    def snapshot(self) -> dict[str, Any]:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT
                    COUNT(*) AS queued_or_running,
                    COUNT(*) FILTER (
                        WHERE owner_instance_id IS NULL
                           OR lease_expires_at <= CURRENT_TIMESTAMP
                    ) AS claimable,
                    COUNT(*) FILTER (
                        WHERE owner_instance_id IS NOT NULL
                          AND lease_expires_at > CURRENT_TIMESTAMP
                    ) AS active_leases,
                    COALESCE(SUM(claim_count), 0) AS claims,
                    COALESCE(SUM(recovery_count), 0) AS recoveries
                FROM {self._table()}
                """
            ).fetchone()
        assert row is not None
        return {
            "schema_version": RUNTIME_HANDOFF_SCHEMA_VERSION,
            "backend": "postgresql_skip_locked_lease",
            "queued_or_running": int(row[0]),
            "claimable": int(row[1]),
            "active_leases": int(row[2]),
            "claims": int(row[3]),
            "recoveries": int(row[4]),
        }
