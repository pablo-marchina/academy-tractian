from __future__ import annotations

import argparse
import json
import os
import sys

from academy_tractian.hosted_postgres_preflight import (
    build_hosted_postgres_preflight_evidence,
    decide_hosted_postgres_preflight,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only, secret-safe preflight for hosted PostgreSQL production identities."
    )
    parser.add_argument("--required-server-major", type=int, default=18)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    internal_dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "")
    scoped_dsn = os.environ.get("ACADEMY_POSTGRES_SCOPED_DSN", "")
    if not internal_dsn or not scoped_dsn:
        print(
            json.dumps(
                {
                    "schema_version": "hosted-postgres-preflight-cli-v1",
                    "outcome": "PREFLIGHT_FAIL",
                    "reason_codes": ["POSTGRES_DSN_ENVIRONMENT_MISSING"],
                },
                sort_keys=True,
            )
        )
        return 2

    try:
        evidence = build_hosted_postgres_preflight_evidence(
            internal_dsn=internal_dsn,
            scoped_dsn=scoped_dsn,
        )
        decision = decide_hosted_postgres_preflight(
            evidence,
            required_server_major=args.required_server_major,
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema_version": "hosted-postgres-preflight-cli-v1",
                    "outcome": "PREFLIGHT_FAIL",
                    "reason_codes": ["PREFLIGHT_EXECUTION_FAILED"],
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "schema_version": "hosted-postgres-preflight-cli-v1",
                "outcome": decision.outcome,
                "reason_codes": list(decision.reason_codes),
                "evidence": evidence.model_dump(mode="json"),
            },
            sort_keys=True,
        )
    )
    return 0 if decision.outcome == "PREFLIGHT_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
