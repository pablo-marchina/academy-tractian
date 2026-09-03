from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any
from uuid import uuid4

from research.e2.models import ToolSpec

from .action_safety import action_fingerprint
from .observability import safe_run_id
from .postgres_operational import PostgresOperationalDatabase
from .production_actions_v2 import PendingActionSafe


@dataclass(frozen=True, slots=True)
class PostgresPendingActionPrivate:
    safe: PendingActionSafe
    requester_user_sha256: str
    arguments: dict[str, Any]
    idempotency_key: str


def _user_hash(user_id: str) -> str:
    return sha256(user_id.encode("utf-8")).hexdigest()


def _safe_action_id(origin_raw_run_id: str, fingerprint: str) -> str:
    material = f"{origin_raw_run_id}:{fingerprint}".encode("utf-8")
    return "act_" + sha256(material).hexdigest()[:24]


class PostgresPendingActionCustody:
    """Private PostgreSQL custody; raw payloads never enter observability/frontend."""

    def __init__(self, database: PostgresOperationalDatabase, *, initialize: bool = False) -> None:
        self.database = database
        self.schema = database.schema
        if initialize:
            self.initialize_schema()

    def initialize_schema(self) -> None:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{self.schema}".pending_actions (
                        action_id TEXT PRIMARY KEY,
                        origin_run_id TEXT NOT NULL REFERENCES "{self.schema}".run_ownership(run_id)
                            ON DELETE RESTRICT,
                        requester_user_sha256 TEXT NOT NULL,
                        tool_name TEXT NOT NULL,
                        action_fingerprint TEXT NOT NULL,
                        impact TEXT NOT NULL,
                        required_permissions_json JSONB NOT NULL,
                        arguments_json JSONB NOT NULL,
                        idempotency_key TEXT NOT NULL UNIQUE,
                        state TEXT NOT NULL CHECK (
                            state IN (
                                'PENDING_CONFIRMATION','CONFIRMED','EXECUTING','ACCEPTED',
                                'BLOCKED','NOT_ACCEPTED','UNCERTAIN'
                            )
                        ),
                        execution_run_id TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(origin_run_id, action_fingerprint)
                    )
                    """
                )

    @staticmethod
    def _safe(row: object) -> PendingActionSafe:
        values = tuple(row)  # type: ignore[arg-type]
        permissions = values[6]
        if isinstance(permissions, str):
            permissions = json.loads(permissions)
        return PendingActionSafe(
            action_id=str(values[0]),
            origin_run_id=str(values[1]),
            tool_name=str(values[3]),
            action_fingerprint=str(values[4]),
            impact=str(values[5]),
            required_permissions=tuple(str(value) for value in permissions),
            state=str(values[9]),  # type: ignore[arg-type]
            execution_run_id=None if values[10] is None else str(values[10]),
        )

    def create_or_get(
        self,
        *,
        origin_raw_run_id: str,
        requester_user_id: str,
        tool: ToolSpec,
        arguments: dict[str, Any],
    ) -> PendingActionSafe:
        fingerprint = action_fingerprint(tool, arguments)
        origin_run_id = safe_run_id(origin_raw_run_id)
        action_id = _safe_action_id(origin_raw_run_id, fingerprint)
        permissions = tuple(permission.value for permission in tool.required_permissions)
        idempotency_key = "idem-" + uuid4().hex
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    INSERT INTO "{self.schema}".pending_actions(
                        action_id, origin_run_id, requester_user_sha256, tool_name,
                        action_fingerprint, impact, required_permissions_json, arguments_json,
                        idempotency_key, state, execution_run_id
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,'PENDING_CONFIRMATION',NULL)
                    ON CONFLICT (origin_run_id, action_fingerprint) DO NOTHING
                    RETURNING action_id
                    """,
                    (
                        action_id,
                        origin_run_id,
                        _user_hash(requester_user_id),
                        tool.name,
                        fingerprint,
                        tool.impact.value,
                        json.dumps(permissions, separators=(",", ":")),
                        json.dumps(arguments, sort_keys=True, separators=(",", ":")),
                        idempotency_key,
                    ),
                ).fetchone()
                if row is None:
                    existing = connection.execute(
                        f"""
                        SELECT action_id FROM "{self.schema}".pending_actions
                        WHERE origin_run_id = %s AND action_fingerprint = %s
                        """,
                        (origin_run_id, fingerprint),
                    ).fetchone()
                    if existing is None:
                        raise RuntimeError("pending_action_upsert_failed")
                    action_id = str(existing[0])
        return self.get_safe(action_id)

    def _load_private(self, action_id: str) -> PostgresPendingActionPrivate | None:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT action_id, origin_run_id, requester_user_sha256, tool_name,
                       action_fingerprint, impact, required_permissions_json, arguments_json,
                       idempotency_key, state, execution_run_id
                FROM "{self.schema}".pending_actions
                WHERE action_id = %s
                """,
                (action_id,),
            ).fetchone()
        if row is None:
            return None
        values = tuple(row)
        arguments = values[7]
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        return PostgresPendingActionPrivate(
            safe=self._safe(row),
            requester_user_sha256=str(values[2]),
            arguments=dict(arguments),
            idempotency_key=str(values[8]),
        )

    def get_safe(self, action_id: str) -> PendingActionSafe:
        item = self._load_private(action_id)
        if item is None:
            raise KeyError(action_id)
        return item.safe

    def get_private_for_requester(
        self,
        *,
        action_id: str,
        requester_user_id: str,
    ) -> PostgresPendingActionPrivate:
        item = self._load_private(action_id)
        if item is None:
            raise KeyError(action_id)
        if item.requester_user_sha256 != _user_hash(requester_user_id):
            raise PermissionError("action_requester_mismatch")
        return item

    def list_safe_for_origin(self, origin_run_id: str) -> list[PendingActionSafe]:
        with self.database.internal_pool.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT action_id FROM "{self.schema}".pending_actions
                WHERE origin_run_id = %s ORDER BY action_id
                """,
                (origin_run_id,),
            ).fetchall()
        return [self.get_safe(str(row[0])) for row in rows]

    def transition(
        self,
        *,
        action_id: str,
        expected_states: frozenset[str],
        new_state: str,
        execution_run_id: str | None = None,
    ) -> bool:
        if not expected_states:
            raise ValueError("expected_states must be non-empty")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE "{self.schema}".pending_actions
                    SET state = %s,
                        execution_run_id = COALESCE(%s, execution_run_id),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE action_id = %s AND state = ANY(%s)
                    RETURNING action_id
                    """,
                    (new_state, execution_run_id, action_id, list(expected_states)),
                ).fetchone()
                return row is not None

    def reconcile_executing(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Mark orphaned executing actions uncertain and return recovered/all uncertain ids."""

        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                rows = connection.execute(
                    f"""
                    UPDATE "{self.schema}".pending_actions
                    SET state = 'UNCERTAIN', updated_at = CURRENT_TIMESTAMP
                    WHERE state = 'EXECUTING'
                    RETURNING action_id
                    """
                ).fetchall()
                recovered = tuple(sorted(str(row[0]) for row in rows))
                uncertain_rows = connection.execute(
                    f"""
                    SELECT action_id FROM "{self.schema}".pending_actions
                    WHERE state = 'UNCERTAIN' ORDER BY action_id
                    """
                ).fetchall()
                uncertain = tuple(str(row[0]) for row in uncertain_rows)
        return recovered, uncertain


class PostgresActionIdempotencyLedger:
    """Atomic one-shot consequential-action claim ledger in PostgreSQL."""

    def __init__(self, database: PostgresOperationalDatabase, *, initialize: bool = False) -> None:
        self.database = database
        self.schema = database.schema
        if initialize:
            self.initialize_schema()

    def initialize_schema(self) -> None:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{self.schema}".action_claims (
                        idempotency_key_sha256 TEXT PRIMARY KEY,
                        action_fingerprint TEXT UNIQUE NOT NULL,
                        action_id TEXT NOT NULL REFERENCES "{self.schema}".pending_actions(action_id)
                            ON DELETE RESTRICT,
                        state TEXT NOT NULL CHECK (
                            state IN ('CLAIMED','ACCEPTED','NOT_ACCEPTED','UNCERTAIN')
                        ),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

    def claim(self, *, key_sha256: str, action_fingerprint: str, action_id: str) -> bool:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    INSERT INTO "{self.schema}".action_claims(
                        idempotency_key_sha256, action_fingerprint, action_id, state
                    ) VALUES (%s,%s,%s,'CLAIMED')
                    ON CONFLICT DO NOTHING
                    RETURNING idempotency_key_sha256
                    """,
                    (key_sha256, action_fingerprint, action_id),
                ).fetchone()
                return row is not None

    def mark(self, *, key_sha256: str, state: str) -> None:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE "{self.schema}".action_claims
                    SET state = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE idempotency_key_sha256 = %s
                    RETURNING idempotency_key_sha256
                    """,
                    (state, key_sha256),
                ).fetchone()
                if row is None:
                    raise KeyError(key_sha256)

    def get(self, key_sha256: str) -> dict[str, str] | None:
        with self.database.internal_pool.connection() as connection:
            row = connection.execute(
                f"""
                SELECT action_fingerprint, action_id, state
                FROM "{self.schema}".action_claims
                WHERE idempotency_key_sha256 = %s
                """,
                (key_sha256,),
            ).fetchone()
        if row is None:
            return None
        return {
            "action_fingerprint": str(row[0]),
            "action_id": str(row[1]),
            "state": str(row[2]),
        }

    def reconcile_claimed_for_actions(self, action_ids: tuple[str, ...]) -> tuple[str, ...]:
        if not action_ids:
            return ()
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                rows = connection.execute(
                    f"""
                    UPDATE "{self.schema}".action_claims
                    SET state = 'UNCERTAIN', updated_at = CURRENT_TIMESTAMP
                    WHERE state = 'CLAIMED' AND action_id = ANY(%s)
                    RETURNING action_id
                    """,
                    (list(action_ids),),
                ).fetchall()
        return tuple(sorted(str(row[0]) for row in rows))
