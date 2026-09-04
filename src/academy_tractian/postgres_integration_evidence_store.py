from __future__ import annotations

import re

from .postgres_operational import PostgresOperationalDatabase
from .tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    OperationEvidence,
    parse_integration_evidence_document,
)


POSTGRES_INTEGRATION_EVIDENCE_BACKEND_VERSION = "postgres-tractian-integration-evidence-v1"
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier(value: str, *, label: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


class PostgresIntegrationEvidenceStore:
    """Bounded managed-PostgreSQL store for safe hosted TRACTIAN route evidence.

    The table keeps only the latest safe observation plus a count per canonical
    operation/outcome pair. It never stores request arguments, query values,
    headers, request/response bodies, credentials or tenant-private payloads.
    """

    def __init__(
        self,
        database: PostgresOperationalDatabase,
        *,
        schema: str = "academy_observability",
        initialize: bool = False,
    ) -> None:
        self.database = database
        self.schema = _identifier(schema, label="integration evidence schema")
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
                    CREATE TABLE IF NOT EXISTS {self._table("tractian_integration_meta")} (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._table("tractian_integration_evidence")} (
                        operation TEXT NOT NULL,
                        outcome TEXT NOT NULL CHECK (
                            outcome IN (
                                'success',
                                'http_error_observed',
                                'transport_failure',
                                'unavailable',
                                'blocked_by_safety'
                            )
                        ),
                        environment TEXT NOT NULL CHECK (environment = 'hosted_live'),
                        method TEXT NOT NULL,
                        path_template TEXT NOT NULL,
                        first_observed_at TIMESTAMPTZ NOT NULL,
                        last_observed_at TIMESTAMPTZ NOT NULL,
                        observation_count BIGINT NOT NULL CHECK (observation_count > 0),
                        latest_probe_id TEXT NOT NULL,
                        latest_evidence_ref TEXT NOT NULL,
                        latest_fingerprint TEXT NOT NULL,
                        latest_http_status INTEGER CHECK (
                            latest_http_status IS NULL
                            OR latest_http_status BETWEEN 100 AND 599
                        ),
                        PRIMARY KEY (operation, outcome)
                    )
                    """
                )
                connection.execute(
                    f"""
                    INSERT INTO {self._table("tractian_integration_meta")}(key, value)
                    VALUES ('backend_version', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (POSTGRES_INTEGRATION_EVIDENCE_BACKEND_VERSION,),
                )

    def ready(self) -> bool:
        try:
            with self.database.internal_pool.connection() as connection:
                row = connection.execute(
                    f"SELECT value FROM {self._table('tractian_integration_meta')} "
                    "WHERE key = 'backend_version'"
                ).fetchone()
        except Exception:
            return False
        return row is not None and str(row[0]) == POSTGRES_INTEGRATION_EVIDENCE_BACKEND_VERSION

    def persist(self, evidence: OperationEvidence) -> None:
        if evidence.environment != "hosted_live":
            raise ValueError("postgres integration evidence accepts hosted_live records only")

        table = self._table("tractian_integration_evidence")
        with self.database.internal_pool.connection() as connection:
            with connection.transaction():
                connection.execute(
                    f"""
                    INSERT INTO {table} AS existing (
                        operation,
                        outcome,
                        environment,
                        method,
                        path_template,
                        first_observed_at,
                        last_observed_at,
                        observation_count,
                        latest_probe_id,
                        latest_evidence_ref,
                        latest_fingerprint,
                        latest_http_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s, %s, %s, %s)
                    ON CONFLICT (operation, outcome) DO UPDATE SET
                        first_observed_at = LEAST(
                            existing.first_observed_at,
                            EXCLUDED.first_observed_at
                        ),
                        last_observed_at = GREATEST(
                            existing.last_observed_at,
                            EXCLUDED.last_observed_at
                        ),
                        observation_count = existing.observation_count + 1,
                        method = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.method ELSE existing.method END,
                        path_template = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.path_template ELSE existing.path_template END,
                        latest_probe_id = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_probe_id ELSE existing.latest_probe_id END,
                        latest_evidence_ref = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_evidence_ref ELSE existing.latest_evidence_ref END,
                        latest_fingerprint = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_fingerprint ELSE existing.latest_fingerprint END,
                        latest_http_status = CASE
                            WHEN EXCLUDED.last_observed_at >= existing.last_observed_at
                            THEN EXCLUDED.latest_http_status ELSE existing.latest_http_status END
                    """,
                    (
                        evidence.operation,
                        evidence.outcome,
                        evidence.environment,
                        evidence.method,
                        evidence.path_template,
                        evidence.observed_at,
                        evidence.observed_at,
                        evidence.probe_id,
                        evidence.evidence_ref,
                        evidence.fingerprint,
                        evidence.http_status,
                    ),
                )

    def ledger(self) -> IntegrationEvidenceLedger:
        try:
            with self.database.internal_pool.connection() as connection:
                rows = connection.execute(
                    f"""
                    SELECT
                        operation,
                        outcome,
                        environment,
                        method,
                        path_template,
                        last_observed_at,
                        latest_probe_id,
                        latest_evidence_ref,
                        latest_fingerprint,
                        latest_http_status
                    FROM {self._table("tractian_integration_evidence")}
                    ORDER BY operation, outcome
                    """
                ).fetchall()
        except Exception:
            return IntegrationEvidenceLedger(
                source_label="hosted_live:postgres",
                state="INVALID",
                validation_errors=("postgres:evidence_unavailable",),
            )

        payload = {
            "schema_version": "tractian-integration-evidence-v1",
            "records": [
                {
                    "operation": str(row[0]),
                    "outcome": str(row[1]),
                    "environment": str(row[2]),
                    "method": str(row[3]),
                    "path_template": str(row[4]),
                    "observed_at": row[5],
                    "probe_id": str(row[6]),
                    "evidence_ref": str(row[7]),
                    "fingerprint": str(row[8]),
                    "http_status": None if row[9] is None else int(row[9]),
                }
                for row in rows
            ],
        }
        return parse_integration_evidence_document(
            payload,
            source_label="hosted_live:postgres",
            expected_environment="hosted_live",
        )

    def observation_counts(self) -> dict[tuple[str, str], int]:
        """Return safe aggregate counts for diagnostics/tests; no raw evidence leaves the store."""

        with self.database.internal_pool.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT operation, outcome, observation_count
                FROM {self._table("tractian_integration_evidence")}
                ORDER BY operation, outcome
                """
            ).fetchall()
        return {(str(row[0]), str(row[1])): int(row[2]) for row in rows}
