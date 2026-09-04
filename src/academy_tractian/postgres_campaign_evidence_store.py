from __future__ import annotations

import re

from .postgres_operational import PostgresOperationalDatabase
from .tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    CampaignProofRecord,
    parse_campaign_evidence_document,
)


POSTGRES_CAMPAIGN_EVIDENCE_BACKEND_VERSION = "postgres-tractian-campaign-evidence-v1"
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str, *, label: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


class PostgresCampaignEvidenceStore:
    """Bounded managed-PostgreSQL store for semantic 18-tool campaign proof.

    Only safe proof metadata is persisted. Raw requests/responses, prompts, provider outputs,
    credentials and evaluator-private truth are deliberately outside the schema. PASS and FAIL are
    stored independently per operation/dimension so an observed failure cannot be erased by a later
    pass; the report layer therefore remains fail closed.
    """

    def __init__(
        self,
        database: PostgresOperationalDatabase,
        *,
        schema: str = "academy_observability",
        initialize: bool = False,
    ) -> None:
        self.database = database
        self.schema = _identifier(schema, label="campaign evidence schema")
        if initialize:
            self.initialize_schema()

    def _table(self, name: str) -> str:
        return f'"{self.schema}"."{_identifier(name, label="table")}"'

    def initialize_schema(self) -> None:
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"')
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table("tractian_campaign_evidence_meta")} (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table("tractian_campaign_evidence")} (
                        operation TEXT NOT NULL,
                        dimension TEXT NOT NULL CHECK (
                            dimension IN (
                                'invalid_parameters_rejected',
                                'response_normalization_verified',
                                'agent_evaluator_behavior_verified'
                            )
                        ),
                        passed BOOLEAN NOT NULL,
                        environment TEXT NOT NULL CHECK (environment = 'hosted_live'),
                        first_observed_at TIMESTAMPTZ NOT NULL,
                        last_observed_at TIMESTAMPTZ NOT NULL,
                        observation_count BIGINT NOT NULL CHECK (observation_count > 0),
                        latest_probe_id TEXT NOT NULL,
                        latest_evidence_ref TEXT NOT NULL,
                        latest_fingerprint TEXT NOT NULL,
                        PRIMARY KEY (operation, dimension, passed)
                    )
                    """
                )
                connection.execute(
                    f"""
                    INSERT INTO {self._table("tractian_campaign_evidence_meta")}(key, value)
                    VALUES ('backend_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (POSTGRES_CAMPAIGN_EVIDENCE_BACKEND_VERSION,),
                )

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                row = connection.execute(
                    f"SELECT value FROM {self._table('tractian_campaign_evidence_meta')} "
                    "WHERE key = 'backend_version'"
                ).fetchone()
        except Exception:
            return False
        return row is not None and str(row[0]) == POSTGRES_CAMPAIGN_EVIDENCE_BACKEND_VERSION

    def persist(self, evidence: CampaignProofRecord) -> None:
        if evidence.environment != "hosted_live":
            raise ValueError("postgres campaign evidence accepts hosted_live records only")

        table = self._table("tractian_campaign_evidence")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    INSERT INTO {table} AS existing (
                        operation,
                        dimension,
                        passed,
                        environment,
                        first_observed_at,
                        last_observed_at,
                        observation_count,
                        latest_probe_id,
                        latest_evidence_ref,
                        latest_fingerprint
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, 1, %s, %s, %s)
                    ON CONFLICT (operation, dimension, passed) DO UPDATE SET
                        first_observed_at = LEAST(
                            existing.first_observed_at,
                            EXCLUDED.first_observed_at
                        ),
                        last_observed_at = GREATEST(
                            existing.last_observed_at,
                            EXCLUDED.last_observed_at
                        ),
                        observation_count = existing.observation_count + 1,
                        latest_probe_id = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_probe_id ELSE existing.latest_probe_id END,
                        latest_evidence_ref = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_evidence_ref ELSE existing.latest_evidence_ref END,
                        latest_fingerprint = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_fingerprint ELSE existing.latest_fingerprint END
                    """,
                    (
                        evidence.operation,
                        evidence.dimension,
                        evidence.passed,
                        evidence.environment,
                        evidence.observed_at,
                        evidence.observed_at,
                        evidence.probe_id,
                        evidence.evidence_ref,
                        evidence.fingerprint,
                    ),
                )

    def persist_ledger(self, ledger: CampaignEvidenceLedger) -> None:
        if not ledger.valid:
            raise ValueError("cannot persist invalid campaign evidence ledger")
        for record in ledger.records:
            self.persist(record)

    def ledger(self) -> CampaignEvidenceLedger:
        try:
            with self.database.internal_pool.connection() as connection:
                rows = connection.execute(
                    f"""
                    SELECT
                        operation,
                        dimension,
                        passed,
                        environment,
                        last_observed_at,
                        latest_probe_id,
                        latest_evidence_ref,
                        latest_fingerprint
                    FROM {self._table("tractian_campaign_evidence")}
                    ORDER BY operation, dimension, passed
                    """
                ).fetchall()
        except Exception:
            return CampaignEvidenceLedger(
                source_label="hosted_live:postgres_campaign",
                state="INVALID",
                validation_errors=("postgres:campaign_evidence_unavailable",),
            )

        payload = {
            "schema_version": "tractian-campaign-evidence-v1",
            "records": [
                {
                    "operation": str(row[0]),
                    "dimension": str(row[1]),
                    "passed": bool(row[2]),
                    "environment": str(row[3]),
                    "observed_at": row[4],
                    "probe_id": str(row[5]),
                    "evidence_ref": str(row[6]),
                    "fingerprint": str(row[7]),
                }
                for row in rows
            ],
        }
        return parse_campaign_evidence_document(
            payload,
            source_label="hosted_live:postgres_campaign",
        )

    def observation_counts(self) -> dict[tuple[str, str, bool], int]:
        with self.database.internal_pool.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT operation, dimension, passed, observation_count
                FROM {self._table("tractian_campaign_evidence")}
                ORDER BY operation, dimension, passed
                """
            ).fetchall()
        return {
            (str(row[0]), str(row[1]), bool(row[2])): int(row[3])
            for row in rows
        }
