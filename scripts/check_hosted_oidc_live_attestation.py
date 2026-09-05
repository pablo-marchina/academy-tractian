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
from academy_tractian.oidc_candidate_profiles import resolve_oidc_pilot_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fail-closed verifier for sanitized live OIDC evidence")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--expected-code-sha", required=True)
    parser.add_argument("--expected-deployment-origin-sha256", required=True)
    parser.add_argument("--expected-issuer-sha256", required=True)
    parser.add_argument("--expected-audience-sha256", required=True)
    parser.add_argument("--expected-jwks-url-sha256", required=True)
    parser.add_argument("--expected-authorized-party-sha256", required=True)
    parser.add_argument("--candidate-id", default="auth0-free")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        evidence = HostedOIDCLiveEvidence.model_validate_json(args.evidence.read_text(encoding="utf-8"))
        profile = resolve_oidc_pilot_profile(args.candidate_id)
        policy = HostedOIDCLivePolicy(
            expected_candidate_id=profile.candidate_id,
            expected_code_sha=args.expected_code_sha,
            expected_deployment_origin_sha256=args.expected_deployment_origin_sha256,
            expected_profile_sha256=oidc_profile_sha256(profile),
            expected_issuer_sha256=args.expected_issuer_sha256,
            expected_audience_sha256=args.expected_audience_sha256,
            expected_jwks_url_sha256=args.expected_jwks_url_sha256,
            expected_authorized_party_sha256=args.expected_authorized_party_sha256,
            allowed_algorithms=profile.algorithms,
            max_token_ttl_seconds=profile.max_token_ttl_seconds,
        )
        decision = decide_hosted_oidc_live(evidence=evidence, policy=policy)
    except Exception as exc:
        print(json.dumps({
            "schema_version": "hosted-oidc-live-gate-v1",
            "outcome": "OIDC_FAIL",
            "reason_codes": ["OIDC_EVIDENCE_INVALID"],
            "error_type": type(exc).__name__,
        }, sort_keys=True))
        return 2

    print(json.dumps({
        "schema_version": "hosted-oidc-live-gate-v1",
        "candidate_id": evidence.candidate_id,
        "code_sha": evidence.code_sha,
        "deployment_id": evidence.deployment_id,
        "evidence_sha256": evidence.artifact_sha256,
        "outcome": decision.outcome,
        "reason_codes": list(decision.reason_codes),
    }, sort_keys=True))
    return 0 if decision.outcome == "OIDC_PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
