from __future__ import annotations

import argparse
import json
import sys

from academy_tractian.tractian_integration_evidence import load_integration_evidence_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a machine-readable TRACTIAN integration-evidence artifact without "
            "printing response bodies, credentials or other raw evidence."
        )
    )
    parser.add_argument("path", help="path to the JSON evidence artifact")
    parser.add_argument(
        "--environment",
        choices=("hosted_live", "frozen"),
        default="hosted_live",
        help="environment the artifact is allowed to claim",
    )
    args = parser.parse_args()

    ledger = load_integration_evidence_path(
        args.path,
        expected_environment=args.environment,
    )
    route_observed = ledger.unique_route_observed_operations(args.environment)
    success = ledger.unique_success_operations(args.environment)
    blocked = ledger.unique_outcome_operations(args.environment, "blocked_by_safety")

    payload = {
        "schema_version": "tractian-integration-evidence-validation-v1",
        "status": "PASS" if ledger.valid else "FAIL",
        "evidence_state": ledger.state,
        "source": ledger.source_label,
        "validation_errors": list(ledger.validation_errors),
        "record_count": len(ledger.records) if ledger.valid else 0,
        "route_observed_operation_count": len(route_observed),
        "successful_operation_count": len(success),
        "safety_blocked_operation_count": len(blocked),
        "route_observed_operations": sorted(route_observed),
        "successful_operations": sorted(success),
        "safety_blocked_operations": sorted(blocked),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if ledger.valid else 2


if __name__ == "__main__":
    sys.exit(main())
