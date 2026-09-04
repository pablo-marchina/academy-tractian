from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from academy_tractian.hosted_state_identity_pilot import (
    HostedStateIdentityPilotEvidence,
    HostedStateIdentityPilotPolicy,
    decide_hosted_state_identity_pilot,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed verifier for sanitized hosted state+identity pilot evidence."
    )
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--expected-code-sha", required=True)
    parser.add_argument("--expected-bundle-id", default="neon-plus-auth0")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    expected_sha = args.expected_code_sha.strip().lower()
    if not (7 <= len(expected_sha) <= 64) or any(ch not in "0123456789abcdef" for ch in expected_sha):
        print(json.dumps({"outcome": "PILOT_FAIL", "reason_codes": ["EXPECTED_CODE_SHA_INVALID"]}))
        return 2

    try:
        evidence = HostedStateIdentityPilotEvidence.model_validate_json(
            args.evidence.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "outcome": "PILOT_FAIL",
                    "reason_codes": ["EVIDENCE_INVALID"],
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
            )
        )
        return 2

    reason_codes: list[str] = []
    if evidence.code_sha != expected_sha:
        reason_codes.append("CODE_SHA_MISMATCH")

    decision = decide_hosted_state_identity_pilot(
        evidence=evidence,
        policy=HostedStateIdentityPilotPolicy(expected_bundle_id=args.expected_bundle_id),
    )
    reason_codes.extend(decision.reason_codes)
    outcome = "PILOT_FAIL" if reason_codes else "PILOT_PASS"
    print(
        json.dumps(
            {
                "schema_version": "hosted-state-identity-pilot-gate-v1",
                "bundle_id": evidence.bundle_id,
                "code_sha": evidence.code_sha,
                "evidence_sha256": evidence.artifact_sha256,
                "outcome": outcome,
                "reason_codes": list(dict.fromkeys(reason_codes)),
            },
            sort_keys=True,
        )
    )
    return 0 if outcome == "PILOT_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
