from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from academy_tractian.live_deployment_attestation import (
    LiveDeploymentAttestation,
    LiveDeploymentPolicy,
    decide_live_deployment_attestation,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate secret-safe live deployment source/build/runtime attestation."
    )
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--required-python", default="3.11")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = LiveDeploymentAttestation.model_validate(
            json.loads(args.evidence.read_text(encoding="utf-8"))
        )
        decision = decide_live_deployment_attestation(
            evidence=evidence,
            policy=LiveDeploymentPolicy(required_python_major_minor=args.required_python),
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "schema_version": "live-deployment-attestation-cli-v1",
                    "outcome": "LIVE_ATTESTATION_FAIL",
                    "reason_codes": ["ATTESTATION_VALIDATION_FAILED"],
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "schema_version": "live-deployment-attestation-cli-v1",
                "candidate_id": decision.candidate_id,
                "deployment_id": decision.deployment_id,
                "outcome": decision.outcome,
                "reason_codes": list(decision.reason_codes),
                "evidence_sha256": decision.evidence_sha256,
            },
            sort_keys=True,
        )
    )
    return 0 if decision.outcome == "LIVE_ATTESTATION_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
