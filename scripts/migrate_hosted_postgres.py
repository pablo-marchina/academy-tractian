from __future__ import annotations

import json
import sys

from academy_tractian.hosted_config import HostedProductConfig
from academy_tractian.postgres_product_api import initialize_postgres_operational_schema


def main() -> int:
    try:
        config = HostedProductConfig.from_environment(require_serving_ready=False)
        initialize_postgres_operational_schema(
            internal_dsn=config.postgres_internal_dsn,
            scoped_dsn=config.postgres_scoped_dsn,
            schema=config.postgres_schema,
            observability_schema=config.observability_schema,
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema_version": "hosted-postgres-migration-v1",
                    "status": "FAIL",
                    "reason": type(exc).__name__,
                },
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "schema_version": "hosted-postgres-migration-v1",
                "status": "PASS",
                "operational_schema": config.postgres_schema,
                "observability_schema": config.observability_schema,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
