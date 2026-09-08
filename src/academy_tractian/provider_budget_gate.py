from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from typing import Final
from uuid import uuid4

import psycopg
from psycopg import sql


LEASE_NAME: Final[str] = "workers-ai-usd0-budget"
DEFAULT_SCHEMA: Final[str] = "academy_operational"


class ProviderBudgetReservedError(RuntimeError):
    pass


class ProviderBudgetLeaseError(RuntimeError):
    pass


def _identifier(value: str) -> sql.Identifier:
    if not value or not value.replace("_", "").isalnum():
        raise ValueError("invalid PostgreSQL identifier")
    return sql.Identifier(value)


@dataclass(frozen=True)
class ProviderBudgetLease:
    lease_name: str
    owner_token: str
    acquired_at: datetime
    expires_at: datetime


class PostgresProviderBudgetGate:
    """Cross-process fail-closed budget lease for the shared Workers AI allocation."""

    def __init__(self, *, dsn: str, schema: str = DEFAULT_SCHEMA) -> None:
        if not dsn:
            raise ValueError("provider budget gate requires PostgreSQL DSN")
        self.dsn = dsn
        self.schema = schema

    def ensure_schema(self) -> None:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(_identifier(self.schema)))
                cur.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.provider_budget_leases (
                            lease_name text PRIMARY KEY,
                            owner_token text NOT NULL,
                            acquired_at timestamptz NOT NULL,
                            expires_at timestamptz NOT NULL,
                            released_at timestamptz NULL,
                            purpose text NOT NULL,
                            CHECK (expires_at > acquired_at)
                        )
                        """
                    ).format(_identifier(self.schema))
                )
            conn.commit()

    def assert_provider_available(self, *, now: datetime | None = None) -> None:
        current = now or datetime.now(timezone.utc)
        with psycopg.connect(self.dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        "SELECT owner_token, expires_at FROM {}.provider_budget_leases "
                        "WHERE lease_name = %s AND released_at IS NULL AND expires_at > %s"
                    ).format(_identifier(self.schema)),
                    (LEASE_NAME, current),
                )
                row = cur.fetchone()
        if row is not None:
            raise ProviderBudgetReservedError("provider_budget_reserved_for_governed_campaign")

    def acquire(
        self,
        *,
        purpose: str,
        ttl: timedelta = timedelta(minutes=45),
        now: datetime | None = None,
    ) -> ProviderBudgetLease:
        current = now or datetime.now(timezone.utc)
        if ttl <= timedelta(0) or ttl > timedelta(hours=2):
            raise ValueError("provider budget lease ttl must be in (0, 2h]")
        owner = uuid4().hex
        expires = current + ttl
        allow_same_campaign_recovery = (
            os.environ.get("ACADEMY_PROVIDER_BUDGET_ALLOW_SAME_PURPOSE_RECOVERY", "").strip() == "1"
        )
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (LEASE_NAME,))
                cur.execute(
                    sql.SQL(
                        "SELECT owner_token, expires_at, purpose FROM {}.provider_budget_leases "
                        "WHERE lease_name = %s AND released_at IS NULL AND expires_at > %s"
                    ).format(_identifier(self.schema)),
                    (LEASE_NAME, current),
                )
                existing = cur.fetchone()
                if existing is not None:
                    existing_purpose = existing[2]
                    if not (allow_same_campaign_recovery and existing_purpose == purpose):
                        raise ProviderBudgetLeaseError("active provider budget lease already exists")
                cur.execute(
                    sql.SQL(
                        """
                        INSERT INTO {}.provider_budget_leases
                            (lease_name, owner_token, acquired_at, expires_at, released_at, purpose)
                        VALUES (%s, %s, %s, %s, NULL, %s)
                        ON CONFLICT (lease_name) DO UPDATE SET
                            owner_token = EXCLUDED.owner_token,
                            acquired_at = EXCLUDED.acquired_at,
                            expires_at = EXCLUDED.expires_at,
                            released_at = NULL,
                            purpose = EXCLUDED.purpose
                        """
                    ).format(_identifier(self.schema)),
                    (LEASE_NAME, owner, current, expires, purpose),
                )
            conn.commit()
        return ProviderBudgetLease(LEASE_NAME, owner, current, expires)

    def release(self, lease: ProviderBudgetLease, *, now: datetime | None = None) -> None:
        current = now or datetime.now(timezone.utc)
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        "UPDATE {}.provider_budget_leases SET released_at = %s "
                        "WHERE lease_name = %s AND owner_token = %s AND released_at IS NULL"
                    ).format(_identifier(self.schema)),
                    (current, lease.lease_name, lease.owner_token),
                )
                if cur.rowcount != 1:
                    raise ProviderBudgetLeaseError("provider budget lease ownership lost")
            conn.commit()


def production_provider_budget_gate_from_env() -> PostgresProviderBudgetGate:
    dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "").strip()
    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", DEFAULT_SCHEMA).strip() or DEFAULT_SCHEMA
    return PostgresProviderBudgetGate(dsn=dsn, schema=schema)
