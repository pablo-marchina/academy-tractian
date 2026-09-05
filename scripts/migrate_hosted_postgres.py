from __future__ import annotations

import json
import sys

from academy_tractian.hosted_config import HostedProductConfig
from academy_tractian.postgres_campaign_evidence_store import PostgresCampaignEvidenceStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.postgres_product_api import initialize_postgres_operational_schema


def main() -> int:
    database: PostgresOperationalDatabase | None = None
    try:
        config = HostedProductConfig.from_environment(require_serving_ready=False)
        initialize_postgres_operational_schema(
            internal_dsn=config.postgres_internal_dsn,
            scoped_dsn=config.postgres_scoped_dsn,
            schema=config.postgres_schema,
            observability_schema=config.observability_schema,
        )
        database = PostgresOperationalDatabase(
            internal_dsn=config.postgres_internal_dsn,
            scoped_dsn=config.postgres_scoped_dsn,
            schema=config.postgres_schema,
            initialize=False,
        )
        campaign_store = PostgresCampaignEvidenceStore(
            database,
            schema=config.observability_schema,
            initialize=True,
        )
        if not campaign_store.ready():
            raise RuntimeError("postgres_campaign_evidence_schema_not_ready_after_initialize")
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema_version": "hosted-postgres-migration-v2",
                    "status": "FAIL",
                    "reason": type(exc).__name__,
                },
                sort_keys=True,
            )
        )
        return 2
    finally:
        if database is not None:
            database.close()

    print(
        json.dumps(
            {
                "schema_version": "hosted-postgres-migration-v2",
                "status": "PASS",
                "operational_schema": config.postgres_schema,
                "observability_schema": config.observability_schema,
                "campaign_evidence_store": "ready",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
