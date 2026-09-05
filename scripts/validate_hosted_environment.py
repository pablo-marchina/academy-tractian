from __future__ import annotations

import argparse
import json
import sys

from academy_tractian.hosted_config import HostedProductConfig


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the hosted-only production environment without printing secrets."
    )
    parser.add_argument(
        "--serving-ready",
        action="store_true",
        help="also require a selected hosted provider, provider credential and TRACTIAN base URL",
    )
    args = parser.parse_args()

    try:
        config = HostedProductConfig.from_environment(require_serving_ready=args.serving_ready)
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "schema_version": "hosted-environment-validation-v1",
                    "status": "FAIL",
                    "reason": str(exc),
                },
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "schema_version": "hosted-environment-validation-v1",
                "status": "PASS",
                "serving_ready_required": bool(args.serving_ready),
                "config": config.sanitized_summary(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
