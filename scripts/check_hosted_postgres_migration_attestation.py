from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

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


def _object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("migration_plan_manifest_must_be_object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Secret-safe hosted PostgreSQL migration attestation")
    parser.add_argument("--code-sha", required=True)
    parser.add_argument("--migration-plan-manifest", type=Path, required=True)
    args = parser.parse_args()

    internal_dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "")
    scoped_dsn = os.environ.get("ACADEMY_POSTGRES_SCOPED_DSN", "")
    if not internal_dsn or not scoped_dsn:
        print(json.dumps({
            "schema_version": "hosted-postgres-migration-attestation-cli-v1",
            "outcome": "MIGRATION_FAIL",
            "reason_codes": ["POSTGRES_DSN_ENVIRONMENT_MISSING"],
        }, sort_keys=True))
        return 2

    try:
        manifest = _object(args.migration_plan_manifest)
        preflight = build_hosted_postgres_preflight_evidence(
            internal_dsn=internal_dsn,
            scoped_dsn=scoped_dsn,
        )
        preflight_decision = decide_hosted_postgres_preflight(preflight)
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
            "schema_version": "hosted-postgres-migration-attestation-cli-v1",
            "outcome": "MIGRATION_FAIL",
            "reason_codes": ["MIGRATION_ATTESTATION_EXECUTION_FAILED"],
            "error_type": type(exc).__name__,
        }, sort_keys=True))
        return 2

    print(json.dumps({
        "schema_version": "hosted-postgres-migration-attestation-cli-v1",
        "outcome": decision.outcome,
        "reason_codes": list(decision.reason_codes),
        "preflight_evidence_sha256": preflight.artifact_sha256,
        "migration_evidence": evidence.model_dump(mode="json"),
    }, sort_keys=True))
    return 0 if decision.outcome == "MIGRATION_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
