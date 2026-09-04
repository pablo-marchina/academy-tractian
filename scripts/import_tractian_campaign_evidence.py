from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

from academy_tractian.postgres_campaign_evidence_store import PostgresCampaignEvidenceStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.tractian_campaign_evidence import parse_campaign_evidence_document
from academy_tractian.tractian_integration_campaign import build_tractian_integration_campaign_report


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"missing_required_environment:{name}")
    return value


def _read_document(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid_campaign_evidence_document") from exc
    if not isinstance(payload, dict):
        raise ValueError("campaign_evidence_document_must_be_object")
    return payload


def _failure(reason: str, *, validation_errors: tuple[str, ...] = ()) -> int:
    print(
        json.dumps(
            {
                "schema_version": "tractian-campaign-evidence-import-v1",
                "status": "FAIL",
                "reason": reason,
                "validation_errors": list(validation_errors),
            },
            sort_keys=True,
        )
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and import bounded semantic TRACTIAN campaign proof into managed PostgreSQL. "
            "Raw requests, responses, prompts and credentials are never emitted."
        )
    )
    parser.add_argument("path", help="path to a tractian-campaign-evidence-v1 JSON document")
    args = parser.parse_args()

    database: PostgresOperationalDatabase | None = None
    try:
        payload = _read_document(Path(args.path))
        ledger = parse_campaign_evidence_document(
            payload,
            source_label="operator_import:validated_campaign_document",
        )
        if not ledger.valid:
            return _failure("campaign_evidence_validation_failed", validation_errors=ledger.validation_errors)

        internal_dsn = _required_environment("ACADEMY_POSTGRES_INTERNAL_DSN")
        scoped_dsn = _required_environment("ACADEMY_POSTGRES_SCOPED_DSN")
        operational_schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational").strip()
        observability_schema = os.environ.get(
            "ACADEMY_OBSERVABILITY_SCHEMA", "academy_observability"
        ).strip()

        database = PostgresOperationalDatabase(
            internal_dsn=internal_dsn,
            scoped_dsn=scoped_dsn,
            schema=operational_schema,
            initialize=False,
        )
        store = PostgresCampaignEvidenceStore(
            database,
            schema=observability_schema,
            initialize=False,
        )
        if not store.ready():
            return _failure("postgres_campaign_evidence_store_not_ready")

        store.persist_ledger(ledger)
        persisted = store.ledger()
        if not persisted.valid:
            return _failure(
                "persistent_campaign_evidence_invalid",
                validation_errors=persisted.validation_errors,
            )
        report = build_tractian_integration_campaign_report(campaign_evidence=persisted)
        print(
            json.dumps(
                {
                    "schema_version": "tractian-campaign-evidence-import-v1",
                    "status": "PASS",
                    "imported_record_count": len(ledger.records),
                    "persisted_aggregate_count": len(persisted.records),
                    "semantic_complete_operations": report.semantic_complete_operations,
                    "semantic_incomplete_operations": report.semantic_incomplete_operations,
                    "semantic_completion_status": report.semantic_completion_status,
                },
                sort_keys=True,
            )
        )
        return 0
    except ValueError as exc:
        reason = str(exc)
        if not reason.startswith(("missing_required_environment:", "invalid ")):
            reason = "campaign_evidence_import_rejected"
        return _failure(reason)
    except Exception:
        return _failure("campaign_evidence_import_failed")
    finally:
        if database is not None:
            database.close()


if __name__ == "__main__":
    sys.exit(main())
