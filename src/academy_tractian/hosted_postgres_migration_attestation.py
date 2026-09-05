from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .hosted_postgres_preflight import HostedPostgresPreflightDecision


REQUIRED_TABLES = (
    "academy_operational.operational_meta",
    "academy_operational.run_ownership",
    "academy_operational.run_executions",
    "academy_operational.pending_actions",
    "academy_operational.action_claims",
    "academy_operational.operational_pilot_tasks",
    "academy_operational.operational_pilot_assignments",
    "academy_operational.semantic_review_tasks",
    "academy_operational.semantic_review_assignments",
    "academy_observability.observability_meta",
    "academy_observability.runs",
    "academy_observability.events",
    "academy_observability.evidence",
    "academy_observability.evaluations",
    "academy_observability.tractian_integration_meta",
    "academy_observability.tractian_integration_evidence",
    "academy_observability.tractian_campaign_evidence_meta",
    "academy_observability.tractian_campaign_evidence",
)
RLS_TABLES = (
    "academy_operational.run_ownership",
    "academy_operational.operational_pilot_tasks",
    "academy_operational.operational_pilot_assignments",
    "academy_operational.semantic_review_tasks",
    "academy_operational.semantic_review_assignments",
)
EXPECTED_META = (
    ("academy_operational.operational_meta", "schema_version", "postgres-operational-v1"),
    ("academy_operational.operational_meta", "run_access_schema_version", "run-access-v1"),
    ("academy_operational.operational_meta", "run_execution_schema_version", "run-execution-store-v1"),
    (
        "academy_operational.operational_meta",
        "operational_value_collection_schema_version",
        "operational-value-collection-v5",
    ),
    (
        "academy_operational.operational_meta",
        "semantic_review_collection_schema_version",
        "semantic-review-collection-v1",
    ),
    ("academy_observability.observability_meta", "schema_version", "observability-store-v1"),
    (
        "academy_observability.observability_meta",
        "backend_version",
        "postgres-observability-v1",
    ),
    (
        "academy_observability.tractian_integration_meta",
        "backend_version",
        "postgres-tractian-integration-evidence-v1",
    ),
    (
        "academy_observability.tractian_campaign_evidence_meta",
        "backend_version",
        "postgres-tractian-campaign-evidence-v1",
    ),
)
SCOPED_ROLE = "academy_tractian_rls"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


class MetaVersion(_StrictModel):
    relation: str = Field(min_length=1, max_length=256)
    key: str = Field(min_length=1, max_length=128)
    value: str = Field(min_length=1, max_length=256)


class HostedPostgresMigrationObservation(_StrictModel):
    table_names: tuple[str, ...]
    rls_enabled_tables: tuple[str, ...]
    tenant_select_policy_tables: tuple[str, ...]
    scoped_select_grant_tables: tuple[str, ...]
    meta_versions: tuple[MetaVersion, ...]

    @model_validator(mode="after")
    def validate_canonical_sets(self) -> "HostedPostgresMigrationObservation":
        for values in (
            self.table_names,
            self.rls_enabled_tables,
            self.tenant_select_policy_tables,
            self.scoped_select_grant_tables,
        ):
            if values != tuple(sorted(set(values))):
                raise ValueError("hosted_postgres_migration_observation_set_not_canonical")
        meta_keys = [(item.relation, item.key) for item in self.meta_versions]
        if meta_keys != sorted(set(meta_keys)):
            raise ValueError("hosted_postgres_migration_meta_not_canonical")
        return self


class HostedPostgresMigrationEvidence(_StrictModel):
    schema_version: Literal["hosted-postgres-migration-attestation-v1"] = (
        "hosted-postgres-migration-attestation-v1"
    )
    code_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    migration_sql_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    preflight_artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    observation: HostedPostgresMigrationObservation
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_hash(self) -> "HostedPostgresMigrationEvidence":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("hosted_postgres_migration_attestation_hash_mismatch")
        return self


class HostedPostgresMigrationPolicy(_StrictModel):
    schema_version: Literal["hosted-postgres-migration-policy-v1"] = (
        "hosted-postgres-migration-policy-v1"
    )
    expected_code_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    expected_migration_sql_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_source_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_preflight_artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class HostedPostgresMigrationDecision(_StrictModel):
    schema_version: Literal["hosted-postgres-migration-decision-v1"] = (
        "hosted-postgres-migration-decision-v1"
    )
    outcome: Literal["MIGRATION_PASS", "MIGRATION_FAIL"]
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def build_hosted_postgres_migration_evidence(
    *,
    code_sha: str,
    migration_sql_sha256: str,
    source_manifest_sha256: str,
    preflight_artifact_sha256: str,
    observation: HostedPostgresMigrationObservation,
) -> HostedPostgresMigrationEvidence:
    material = {
        "schema_version": "hosted-postgres-migration-attestation-v1",
        "code_sha": code_sha,
        "migration_sql_sha256": migration_sql_sha256,
        "source_manifest_sha256": source_manifest_sha256,
        "preflight_artifact_sha256": preflight_artifact_sha256,
        "observation": observation.model_dump(mode="json"),
    }
    return HostedPostgresMigrationEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )


def decide_hosted_postgres_migration(
    *,
    evidence: HostedPostgresMigrationEvidence,
    policy: HostedPostgresMigrationPolicy,
    preflight_decision: HostedPostgresPreflightDecision,
) -> HostedPostgresMigrationDecision:
    reasons: list[str] = []
    if preflight_decision.outcome != "PREFLIGHT_PASS":
        reasons.append("POSTGRES_PREFLIGHT_NOT_PASSED")
    if evidence.code_sha != policy.expected_code_sha:
        reasons.append("CODE_SHA_MISMATCH")
    if evidence.migration_sql_sha256 != policy.expected_migration_sql_sha256:
        reasons.append("MIGRATION_SQL_SHA_MISMATCH")
    if evidence.source_manifest_sha256 != policy.expected_source_manifest_sha256:
        reasons.append("SOURCE_MANIFEST_SHA_MISMATCH")
    if evidence.preflight_artifact_sha256 != policy.expected_preflight_artifact_sha256:
        reasons.append("PREFLIGHT_ARTIFACT_SHA_MISMATCH")

    observation = evidence.observation
    table_names = set(observation.table_names)
    rls_tables = set(observation.rls_enabled_tables)
    policy_tables = set(observation.tenant_select_policy_tables)
    grant_tables = set(observation.scoped_select_grant_tables)
    if not set(REQUIRED_TABLES).issubset(table_names):
        reasons.append("REQUIRED_TABLES_MISSING")
    if not set(RLS_TABLES).issubset(rls_tables):
        reasons.append("RLS_NOT_ENABLED_ON_REQUIRED_TABLES")
    if not set(RLS_TABLES).issubset(policy_tables):
        reasons.append("TENANT_SELECT_POLICY_MISSING")
    if not set(RLS_TABLES).issubset(grant_tables):
        reasons.append("SCOPED_SELECT_GRANT_MISSING")

    observed_meta = {
        (item.relation, item.key): item.value for item in observation.meta_versions
    }
    for relation, key, value in EXPECTED_META:
        if observed_meta.get((relation, key)) != value:
            reasons.append("SCHEMA_META_VERSION_MISMATCH")
            break

    deduped = tuple(dict.fromkeys(reasons))
    return HostedPostgresMigrationDecision(
        outcome="MIGRATION_PASS" if not deduped else "MIGRATION_FAIL",
        reason_codes=deduped,
        evidence_sha256=evidence.artifact_sha256,
    )


def inspect_hosted_postgres_migration(
    internal_dsn: str,
    *,
    scoped_role: str = SCOPED_ROLE,
) -> HostedPostgresMigrationObservation:
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - packaging guard
        raise RuntimeError("hosted Postgres migration attestation requires psycopg") from exc

    schemas = ("academy_operational", "academy_observability")
    with psycopg.connect(internal_dsn, connect_timeout=8) as connection:
        tables = connection.execute(
            """
            SELECT table_schema || '.' || table_name
            FROM information_schema.tables
            WHERE table_schema = ANY(%s)
            ORDER BY 1
            """,
            (list(schemas),),
        ).fetchall()
        rls = connection.execute(
            """
            SELECT n.nspname || '.' || c.relname
            FROM pg_class AS c
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = ANY(%s) AND c.relkind = 'r' AND c.relrowsecurity
            ORDER BY 1
            """,
            (list(schemas),),
        ).fetchall()
        policies = connection.execute(
            """
            SELECT schemaname || '.' || tablename
            FROM pg_policies
            WHERE schemaname = ANY(%s) AND policyname = 'tenant_select'
            ORDER BY 1
            """,
            (list(schemas),),
        ).fetchall()
        # Ask PostgreSQL's privilege engine directly instead of relying on information_schema's
        # current-session role visibility. The attestation must prove what the scoped role can read,
        # even when the internal/owner role is not a member of that scoped role.
        grants = connection.execute(
            """
            SELECT n.nspname || '.' || c.relname
            FROM pg_class AS c
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            WHERE n.nspname = ANY(%s)
              AND c.relkind = 'r'
              AND has_table_privilege(%s, c.oid, 'SELECT')
            ORDER BY 1
            """,
            (list(schemas), scoped_role),
        ).fetchall()

        meta: list[MetaVersion] = []
        meta_relations = (
            "academy_operational.operational_meta",
            "academy_observability.observability_meta",
            "academy_observability.tractian_integration_meta",
            "academy_observability.tractian_campaign_evidence_meta",
        )
        for relation in meta_relations:
            schema, table = relation.split(".", 1)
            rows = connection.execute(
                f'SELECT key, value FROM "{schema}"."{table}" ORDER BY key'
            ).fetchall()
            meta.extend(
                MetaVersion(relation=relation, key=str(key), value=str(value))
                for key, value in rows
            )

    return HostedPostgresMigrationObservation(
        table_names=tuple(str(row[0]) for row in tables),
        rls_enabled_tables=tuple(str(row[0]) for row in rls),
        tenant_select_policy_tables=tuple(str(row[0]) for row in policies),
        scoped_select_grant_tables=tuple(str(row[0]) for row in grants),
        meta_versions=tuple(sorted(meta, key=lambda item: (item.relation, item.key))),
    )
