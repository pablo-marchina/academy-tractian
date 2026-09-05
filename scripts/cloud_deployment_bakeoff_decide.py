from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from academy_tractian.deployment_bakeoff import (
    EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
    EXPECTED_STATE_IDENTITY_BUNDLE_ID,
    decide_deployment_bakeoff,
    expected_topology_rules,
)
from academy_tractian.deployment_feasibility import (
    DeploymentFeasibilityEvidence,
    DeploymentFeasibilityPolicy,
    decide_deployment_feasibility_set,
)
from academy_tractian.managed_state_identity_feasibility import (
    HostedIdentityEvidence,
    HostedIdentityPolicy,
    ManagedPostgresEvidence,
    ManagedPostgresPolicy,
    decide_hosted_identity_set,
    decide_managed_postgres_set,
    decide_state_identity_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_DIR = ROOT / "research" / "deployment-feasibility"
STATE_IDENTITY_SCREENING = ROOT / "research" / "managed-state-identity-static-screening-2026-09-04.json"
COMPUTE_EVIDENCE_PATHS = (
    DEPLOYMENT_DIR / "oracle-oci-always-free-a1-2026-09-04.json",
    DEPLOYMENT_DIR / "google-cloud-run-request-free-tier-2026-09-04.json",
    DEPLOYMENT_DIR / "vercel-hobby-python-2026-09-04.json",
    DEPLOYMENT_DIR / "cloudflare-python-workers-free-2026-09-04.json",
    DEPLOYMENT_DIR / "railway-free-docker-2026-09-04.json",
)


def _load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected_json_object:{path}")
    return payload


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("evaluated_at_requires_timezone")
    return parsed


def _compute_feasibility(evaluated_at: datetime):
    policy = DeploymentFeasibilityPolicy.model_validate(
        _load_object(DEPLOYMENT_DIR / "backend-pilot-admission-policy-2026-09-04.json")
    )
    evidence = tuple(
        DeploymentFeasibilityEvidence.model_validate(_load_object(path))
        for path in COMPUTE_EVIDENCE_PATHS
    )
    return decide_deployment_feasibility_set(
        evidence=evidence,
        policy=policy,
        evaluated_at=evaluated_at,
    )


def _state_identity_bundle(evaluated_at: datetime):
    screening = _load_object(STATE_IDENTITY_SCREENING)
    database_policy = ManagedPostgresPolicy(
        max_evidence_age_days=screening["database_policy"]["max_evidence_age_days"],
        allowed_service_maturities=tuple(screening["database_policy"]["allowed_service_maturities"]),
        require_zero_cost_guardrail=screening["database_policy"]["require_zero_cost_guardrail"],
        min_restore_window_hours=screening["database_policy"]["min_restore_window_hours"],
        min_free_storage_mb=screening["database_policy"]["min_free_storage_mb"],
        forbid_manual_inactivity_reactivation=screening["database_policy"]["forbid_manual_inactivity_reactivation"],
    )
    identity_policy = HostedIdentityPolicy(
        max_evidence_age_days=screening["identity_policy"]["max_evidence_age_days"],
        allowed_service_maturities=tuple(screening["identity_policy"]["allowed_service_maturities"]),
        require_zero_cost_guardrail=screening["identity_policy"]["require_zero_cost_guardrail"],
        require_production_without_billing_instrument=screening["identity_policy"]["require_production_without_billing_instrument"],
        max_token_ttl_seconds=screening["identity_policy"]["max_token_ttl_seconds"],
        require_first_class_organizations=screening["identity_policy"]["require_first_class_organizations"],
        min_free_active_users=screening["identity_policy"]["min_free_active_users"],
        min_free_organizations=screening["identity_policy"]["min_free_organizations"],
        forbid_manual_inactivity_reactivation=screening["identity_policy"]["forbid_manual_inactivity_reactivation"],
    )
    database_decisions = decide_managed_postgres_set(
        evidence=tuple(
            ManagedPostgresEvidence.model_validate(item)
            for item in screening["database_candidates"]
        ),
        policy=database_policy,
        evaluated_at=evaluated_at,
    )
    identity_decisions = decide_hosted_identity_set(
        evidence=tuple(
            HostedIdentityEvidence.model_validate(item)
            for item in screening["identity_candidates"]
        ),
        policy=identity_policy,
        evaluated_at=evaluated_at,
    )
    database_by_id = {item.candidate_id: item for item in database_decisions}
    identity_by_id = {item.candidate_id: item for item in identity_decisions}
    bundle = decide_state_identity_bundle(
        bundle_id=EXPECTED_STATE_IDENTITY_BUNDLE_ID,
        database=database_by_id["neon-free"],
        identity=identity_by_id["auth0-free"],
    )
    return database_decisions, identity_decisions, bundle


def build_provider_free_no_live_decision(*, evaluated_at: datetime) -> dict[str, Any]:
    """Reproduce the current static frontier without authorizing or fabricating live evidence."""

    feasibility = _compute_feasibility(evaluated_at)
    database_decisions, identity_decisions, bundle = _state_identity_bundle(evaluated_at)
    decision = decide_deployment_bakeoff(
        manifest_sha256=EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
        topology_rules=expected_topology_rules(),
        feasibility_decisions=feasibility,
        state_identity_pilot_decisions={},
        state_identity_pilot_evidence={},
        live_attestation_decisions=(),
        live_attestation_evidence=(),
        runtime_evidence=(),
        load_reports={},
    )
    return {
        "schema_version": "cloud-deployment-bakeoff-provider-free-no-live-decision-v1",
        "evaluated_at": evaluated_at.isoformat(),
        "provider_free": True,
        "network_calls_performed": 0,
        "cloud_resources_created": 0,
        "live_evidence_supplied": False,
        "static_compute_admissible_candidate_ids": [
            item.candidate_id for item in feasibility if item.outcome == "PILOT_ADMISSIBLE"
        ],
        "static_database_admissible_candidate_ids": [
            item.candidate_id for item in database_decisions if item.outcome == "PILOT_ADMISSIBLE"
        ],
        "static_identity_admissible_candidate_ids": [
            item.candidate_id for item in identity_decisions if item.outcome == "PILOT_ADMISSIBLE"
        ],
        "required_state_identity_bundle": bundle.model_dump(mode="json"),
        "bakeoff_decision": decision.model_dump(mode="json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute the frozen provider-free cloud deployment frontier. With no explicit live "
            "artifacts this command must remain NO_SELECTION and performs no network/cloud action."
        )
    )
    parser.add_argument("--evaluated-at", type=_parse_datetime, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-promotion",
        action="store_true",
        help="Return exit code 2 unless live evidence has produced PROMOTE. No live evidence is loaded by this command.",
    )
    args = parser.parse_args()

    payload = build_provider_free_no_live_decision(evaluated_at=args.evaluated_at)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_promotion and payload["bakeoff_decision"]["outcome"] != "PROMOTE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
