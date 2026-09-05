from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable

# Direct script execution puts scripts/ rather than the repository root on sys.path. Normalize the
# import root before importing the sibling generator so the same CLI works both as
# `python scripts/apply_hosted_postgres_migration_plan.py` and as a module imported by tests.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.hosted_postgres_migration_attestation import (
    HostedPostgresMigrationPolicy,
    build_hosted_postgres_migration_evidence,
    decide_hosted_postgres_migration,
    inspect_hosted_postgres_migration,
)
from academy_tractian.hosted_postgres_preflight import (
    build_hosted_postgres_preflight_evidence,
    decide_hosted_postgres_preflight,
)
from scripts.generate_hosted_postgres_migration_sql import (
    build_migration_manifest,
    build_migration_sql,
)


TargetEnvironment = str


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("hosted_postgres_migration_manifest_must_be_object")
    return payload


def validate_exact_migration_plan(*, sql_path: Path, manifest_path: Path) -> tuple[str, dict[str, Any]]:
    observed_sql = sql_path.read_text(encoding="utf-8")
    canonical_sql = build_migration_sql()
    if observed_sql != canonical_sql:
        raise ValueError("hosted_postgres_migration_sql_not_canonical")

    observed_manifest = _load_object(manifest_path)
    canonical_manifest = build_migration_manifest(canonical_sql)
    if observed_manifest != canonical_manifest:
        raise ValueError("hosted_postgres_migration_manifest_not_canonical")
    if not canonical_sql.startswith("-- hosted-postgres-migration-plan-v1\n"):
        raise ValueError("hosted_postgres_migration_header_invalid")
    if "\nBEGIN;\n" not in canonical_sql or not canonical_sql.rstrip().endswith("COMMIT;"):
        raise ValueError("hosted_postgres_migration_transaction_boundary_invalid")
    return canonical_sql, canonical_manifest


def assert_migration_authorized(
    *,
    allow_migration: bool,
    target_environment: TargetEnvironment,
    approval_ref: str | None,
) -> None:
    if not allow_migration:
        raise PermissionError("hosted_postgres_migration_not_explicitly_allowed")
    if target_environment not in {"temporary_validation", "candidate_main"}:
        raise ValueError("hosted_postgres_migration_target_invalid")
    if target_environment == "candidate_main" and (
        approval_ref is None or len(approval_ref.strip()) < 8
    ):
        raise PermissionError("candidate_main_migration_requires_approval_reference")


def execute_exact_migration_sql(
    dsn: str,
    sql: str,
    *,
    connection_factory: Callable[..., Any] | None = None,
) -> None:
    if connection_factory is None:
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - packaging guard
            raise RuntimeError("hosted Postgres migration requires psycopg") from exc
        connection_factory = psycopg.connect

    # autocommit prevents the driver from opening an outer transaction. The canonical artifact owns
    # its explicit BEGIN/COMMIT and is sent byte-for-byte in a single no-parameter execute() call.
    with connection_factory(dsn, autocommit=True, connect_timeout=8) as connection:
        connection.execute(sql)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply the exact CI-generated hosted PostgreSQL migration artifact with fail-closed provenance."
    )
    parser.add_argument("--code-sha", required=True)
    parser.add_argument("--sql", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-preflight-artifact-sha256", required=True)
    parser.add_argument("--expected-internal-endpoint-sha256", required=True)
    parser.add_argument(
        "--target-environment",
        choices=("temporary_validation", "candidate_main"),
        required=True,
    )
    parser.add_argument("--allow-migration", action="store_true")
    parser.add_argument("--approval-ref")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        assert_migration_authorized(
            allow_migration=args.allow_migration,
            target_environment=args.target_environment,
            approval_ref=args.approval_ref,
        )
        sql, manifest = validate_exact_migration_plan(sql_path=args.sql, manifest_path=args.manifest)

        internal_dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "")
        scoped_dsn = os.environ.get("ACADEMY_POSTGRES_SCOPED_DSN", "")
        if not internal_dsn or not scoped_dsn:
            raise RuntimeError("POSTGRES_DSN_ENVIRONMENT_MISSING")

        preflight = build_hosted_postgres_preflight_evidence(
            internal_dsn=internal_dsn,
            scoped_dsn=scoped_dsn,
        )
        preflight_decision = decide_hosted_postgres_preflight(preflight)
        if preflight_decision.outcome != "PREFLIGHT_PASS":
            raise RuntimeError("POSTGRES_PREFLIGHT_NOT_PASSED")
        if preflight.artifact_sha256 != args.expected_preflight_artifact_sha256:
            raise RuntimeError("PREFLIGHT_ARTIFACT_SHA_MISMATCH")
        if preflight.internal.endpoint_sha256 != args.expected_internal_endpoint_sha256:
            raise RuntimeError("INTERNAL_ENDPOINT_SHA_MISMATCH")

        execute_exact_migration_sql(internal_dsn, sql)
        observation = inspect_hosted_postgres_migration(internal_dsn)
        evidence = build_hosted_postgres_migration_evidence(
            code_sha=args.code_sha,
            migration_sql_sha256=str(manifest["sql_sha256"]),
            source_manifest_sha256=str(manifest["source_manifest_sha256"]),
            preflight_artifact_sha256=preflight.artifact_sha256,
            observation=observation,
        )
        policy = HostedPostgresMigrationPolicy(
            expected_code_sha=args.code_sha,
            expected_migration_sql_sha256=str(manifest["sql_sha256"]),
            expected_source_manifest_sha256=str(manifest["source_manifest_sha256"]),
            expected_preflight_artifact_sha256=preflight.artifact_sha256,
        )
        decision = decide_hosted_postgres_migration(
            evidence=evidence,
            policy=policy,
            preflight_decision=preflight_decision,
        )
    except Exception as exc:
        print(json.dumps({
            "schema_version": "hosted-postgres-migration-apply-v1",
            "status": "FAIL",
            "reason": str(exc) if str(exc).isupper() else type(exc).__name__,
        }, sort_keys=True))
        return 2

    print(json.dumps({
        "schema_version": "hosted-postgres-migration-apply-v1",
        "status": "PASS" if decision.outcome == "MIGRATION_PASS" else "FAIL",
        "target_environment": args.target_environment,
        "migration_sql_sha256": evidence.migration_sql_sha256,
        "source_manifest_sha256": evidence.source_manifest_sha256,
        "preflight_evidence_sha256": preflight.artifact_sha256,
        "migration_evidence_sha256": evidence.artifact_sha256,
        "reason_codes": list(decision.reason_codes),
    }, sort_keys=True))
    return 0 if decision.outcome == "MIGRATION_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
