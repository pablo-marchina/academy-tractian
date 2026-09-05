from __future__ import annotations

from hashlib import sha256

from scripts.generate_hosted_postgres_migration_sql import (
    SCOPED_ROLE,
    SOURCE_PATHS,
    build_migration_manifest,
    build_migration_sql,
)


def test_generated_migration_is_deterministic_provider_free_and_fully_rendered() -> None:
    first = build_migration_sql()
    second = build_migration_sql()
    assert first == second
    assert first.startswith("-- hosted-postgres-migration-plan-v1\n")
    assert "-- provider_free_generation: true" in first
    assert "-- network_calls_performed: 0" in first
    assert "%s" not in first
    assert first.count("BEGIN;") == 1
    assert first.rstrip().endswith("COMMIT;")

    manifest = build_migration_manifest(first)
    assert manifest["provider_free_generation"] is True
    assert manifest["network_calls_performed"] == 0
    assert manifest["scoped_role"] == SCOPED_ROLE == "academy_tractian_rls"
    assert tuple(manifest["source_files"]) == SOURCE_PATHS
    assert manifest["statement_count"] >= 45
    assert manifest["sql_sha256"] == sha256(first.encode("utf-8")).hexdigest()


def test_generated_migration_contains_every_runtime_schema_surface() -> None:
    sql = build_migration_sql()
    required_tables = (
        '"academy_operational".operational_meta',
        '"academy_operational".run_ownership',
        '"academy_operational".run_executions',
        '"academy_operational".pending_actions',
        '"academy_operational".action_claims',
        '"academy_operational".operational_pilot_tasks',
        '"academy_operational".operational_pilot_assignments',
        '"academy_operational".semantic_review_tasks',
        '"academy_operational".semantic_review_assignments',
        '"academy_observability"."observability_meta"',
        '"academy_observability"."runs"',
        '"academy_observability"."events"',
        '"academy_observability"."evidence"',
        '"academy_observability"."evaluations"',
        '"academy_observability"."tractian_integration_meta"',
        '"academy_observability"."tractian_integration_evidence"',
        '"academy_observability"."tractian_campaign_evidence_meta"',
        '"academy_observability"."tractian_campaign_evidence"',
    )
    for table in required_tables:
        assert table in sql, table

    assert 'ENABLE ROW LEVEL SECURITY' in sql
    assert "current_setting('academy.organization_id', true)" in sql
    assert f'TO "{SCOPED_ROLE}"' in sql
    assert "operational-value-collection-v5" in sql
    assert "semantic-review-collection-v1" in sql
    assert "postgres-observability-v1" in sql
    assert "postgres-tractian-integration-evidence-v1" in sql
    assert "postgres-tractian-campaign-evidence-v1" in sql


def test_generator_never_records_runtime_reads_or_secret_material() -> None:
    sql = build_migration_sql().lower()
    forbidden = (
        "postgresql://",
        "postgres://",
        "password=",
        "bearer ",
        "api_key",
        "private_key",
        "raw_token",
    )
    assert not any(marker in sql for marker in forbidden)
    assert "select current_user" not in sql
