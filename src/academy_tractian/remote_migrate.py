from __future__ import annotations

import json
import os

from .postgres_product_api import initialize_postgres_operational_schema
from .remote_production import load_remote_production_config


def migrate() -> dict[str, object]:
    """Run the trusted PostgreSQL bootstrap separately from the serving process."""

    config = load_remote_production_config()
    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational")
    initialize_postgres_operational_schema(
        internal_dsn=config.internal_dsn.get_secret_value(),
        scoped_dsn=config.scoped_dsn.get_secret_value(),
        schema=schema,
    )
    return {
        "schema_version": "remote-production-migration-result-v1",
        "status": "ready",
        "schema": schema,
        "release_git_sha": config.release_git_sha,
        "deployment_id": config.deployment_id,
        "cost_policy": config.cost_policy,
    }


def main() -> None:
    print(json.dumps(migrate(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
