from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from academy_tractian.hosted_oidc_live_attestation import (
    HostedOIDCLiveEvidence,
    HostedOIDCLivePolicy,
    decide_hosted_oidc_live,
    oidc_profile_sha256,
)
from academy_tractian.hosted_state_identity_pilot import (
    HostedStateIdentityPilotEvidence,
    HostedStateIdentityPilotPolicy,
    decide_hosted_state_identity_pilot,
)
from academy_tractian.oidc_candidate_profiles import AUTH0_PILOT_PROFILE


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed verifier for sanitized hosted state+identity pilot evidence."
    )
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--oidc-evidence", type=Path, required=True)
    parser.add_argument("--expected-code-sha", required=True)
    parser.add_argument("--expected-bundle-id", default="neon-plus-auth0")
    parser.add_argument("--expected-oidc-audience-sha256", required=True)
    parser.add_argument("--expected-oidc-jwks-url-sha256", required=True)
    parser.add_argument("--expected-oidc-authorized-party-sha256", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    expected_sha = args.expected_code_sha.strip().lower()
    if len(expected_sha) != 40 or any(ch not in "0123456789abcdef" for ch in expected_sha):
        print(json.dumps({"outcome": "PILOT_FAIL", "reason_codes": ["EXPECTED_CODE_SHA_INVALID"]}))
        return 2

    try:
        evidence = HostedStateIdentityPilotEvidence.model_validate_json(
            args.evidence.read_text(encoding="utf-8")
        )
        oidc_evidence = HostedOIDCLiveEvidence.model_validate_json(
            args.oidc_evidence.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(json.dumps({
            "outcome": "PILOT_FAIL",
            "reason_codes": ["EVIDENCE_INVALID"],
            "error_type": type(exc).__name__,
        }, sort_keys=True))
        return 2

    reason_codes: list[str] = []
    if evidence.code_sha != expected_sha:
        reason_codes.append("CODE_SHA_MISMATCH")

    oidc_policy = HostedOIDCLivePolicy(
        expected_candidate_id=AUTH0_PILOT_PROFILE.candidate_id,
        expected_code_sha=expected_sha,
        expected_deployment_origin_sha256=evidence.deployment_origin_sha256,
        expected_profile_sha256=oidc_profile_sha256(AUTH0_PILOT_PROFILE),
        expected_issuer_sha256=evidence.identity_issuer_sha256,
        expected_audience_sha256=args.expected_oidc_audience_sha256,
        expected_jwks_url_sha256=args.expected_oidc_jwks_url_sha256,
        expected_authorized_party_sha256=args.expected_oidc_authorized_party_sha256,
        allowed_algorithms=AUTH0_PILOT_PROFILE.algorithms,
        max_token_ttl_seconds=AUTH0_PILOT_PROFILE.max_token_ttl_seconds,
    )
    oidc_decision = decide_hosted_oidc_live(evidence=oidc_evidence, policy=oidc_policy)
    if oidc_decision.outcome != "OIDC_PASS":
        reason_codes.append("OIDC_LIVE_ATTESTATION_FAILED")
        reason_codes.extend(oidc_decision.reason_codes)

    decision = decide_hosted_state_identity_pilot(
        evidence=evidence,
        policy=HostedStateIdentityPilotPolicy(expected_bundle_id=args.expected_bundle_id),
    )
    reason_codes.extend(decision.reason_codes)
    outcome = "PILOT_FAIL" if reason_codes else "PILOT_PASS"
    print(json.dumps({
        "schema_version": "hosted-state-identity-pilot-gate-v2",
        "bundle_id": evidence.bundle_id,
        "code_sha": evidence.code_sha,
        "evidence_sha256": evidence.artifact_sha256,
        "oidc_evidence_sha256": oidc_evidence.artifact_sha256,
        "outcome": outcome,
        "reason_codes": list(dict.fromkeys(reason_codes)),
    }, sort_keys=True))
    return 0 if outcome == "PILOT_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
