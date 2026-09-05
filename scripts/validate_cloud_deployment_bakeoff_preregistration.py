from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from academy_tractian.deployment_bakeoff import (
    EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256,
    EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
    EXPECTED_STATE_IDENTITY_BUNDLE_ID,
    expected_topology_rules,
)
from academy_tractian.load_concurrency_benchmark import LoadBenchmarkProtocol


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT / "research" / "experiments" / "cloud-deployment-bakeoff-preregistration-v1.json"
)
EXPECTED_DEPLOYMENT_FEASIBILITY_MANIFEST_SHA256 = (
    "305b98b8ba65d3f495199fb58953603d063b6fa45eb09315fe253fdbc2dd0c4b"
)
EXPECTED_STATE_IDENTITY_SOURCE_MANIFEST_SHA256 = (
    "3449bcd5ba596c44e72b43314ee69cd368402f19aa51b949aff855346fb82def"
)
FORBIDDEN_KEY_MARKERS = (
    "api_key",
    "bearer",
    "credential",
    "dsn",
    "password",
    "private_key",
    "raw_token",
    "secret",
)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _walk_keys(value: object) -> tuple[str, ...]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return tuple(keys)


def validate_manifest(payload: dict[str, object]) -> tuple[str, ...]:
    failures: list[str] = []

    if _canonical_sha256(payload) != EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256:
        failures.append("MANIFEST_HASH_MISMATCH")
    if payload.get("schema_version") != "cloud-deployment-bakeoff-preregistration-v1":
        failures.append("SCHEMA_VERSION_MISMATCH")
    if payload.get("status") != "PREREGISTERED_PROVIDER_FREE_DESIGN":
        failures.append("STATUS_NOT_PROVIDER_FREE_DESIGN")
    if payload.get("live_cloud_actions_authorized_now") != 0:
        failures.append("LIVE_CLOUD_ACTION_AUTHORIZATION_FORBIDDEN")
    if payload.get("cloud_resources_authorized_now") != 0:
        failures.append("CLOUD_RESOURCE_AUTHORIZATION_FORBIDDEN")
    if payload.get("production_cloud_selected") is not False:
        failures.append("PRODUCTION_CLOUD_SELECTION_FORBIDDEN")
    if payload.get("weighted_composite_score_forbidden") is not True:
        failures.append("WEIGHTED_SCORE_MUST_REMAIN_FORBIDDEN")

    expected_candidates = [
        {
            "candidate_id": rule.topology_id,
            "compute_candidate_id": rule.compute_candidate_id,
            "state_identity_bundle_id": rule.state_identity_bundle_id,
        }
        for rule in expected_topology_rules()
    ]
    if payload.get("candidate_topologies") != expected_candidates:
        failures.append("CANDIDATE_FRONTIER_MISMATCH")

    static_inputs = payload.get("static_inputs")
    if not isinstance(static_inputs, dict):
        failures.append("STATIC_INPUTS_MISSING")
    else:
        if (
            static_inputs.get("deployment_feasibility_manifest_sha256")
            != EXPECTED_DEPLOYMENT_FEASIBILITY_MANIFEST_SHA256
        ):
            failures.append("DEPLOYMENT_FEASIBILITY_MANIFEST_BINDING_MISMATCH")
        if (
            static_inputs.get("state_identity_source_manifest_sha256")
            != EXPECTED_STATE_IDENTITY_SOURCE_MANIFEST_SHA256
        ):
            failures.append("STATE_IDENTITY_MANIFEST_BINDING_MISMATCH")
        if static_inputs.get("required_state_identity_bundle") != EXPECTED_STATE_IDENTITY_BUNDLE_ID:
            failures.append("STATE_IDENTITY_BUNDLE_MISMATCH")

    live = payload.get("live_protocol")
    if not isinstance(live, dict):
        failures.append("LIVE_PROTOCOL_MISSING")
    else:
        expected_scalars = {
            "required_source_branch": "feat/cloud-production-baseline",
            "required_python_major_minor": "3.11",
            "required_local_components": 0,
            "observed_cash_cost_usd": 0.0,
            "concurrency_levels": [1, 5, 20, 50],
            "requests_per_level": 20,
            "warmup_requests": 0,
            "load_protocol_id": "cloud-bakeoff-load-v1",
            "load_protocol_sha256": EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256,
            "candidate_frontier_exact_match_required": True,
            "exact_code_sha_binding_required": True,
            "deployment_origin_binding_required": True,
            "image_digest_required": True,
            "live_attestation_evidence_hash_binding_required": True,
            "state_identity_evidence_hash_binding_required": True,
            "load_report_protocol_must_match": True,
            "state_identity_pilot_must_pass": True,
            "live_deployment_attestation_must_pass": True,
        }
        for key, expected in expected_scalars.items():
            if live.get(key) != expected:
                failures.append(f"LIVE_PROTOCOL_{key.upper()}_MISMATCH")
        if live.get("approved_build_contracts") != ["root-dockerfile"]:
            failures.append("LIVE_PROTOCOL_BUILD_CONTRACT_MISMATCH")

        protocol = LoadBenchmarkProtocol(
            protocol_id="cloud-bakeoff-load-v1",
            concurrency_levels=(1, 5, 20, 50),
            requests_per_level=20,
            warmup_requests=0,
        )
        if protocol.sha256() != EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256:
            failures.append("LOAD_PROTOCOL_IMPLEMENTATION_HASH_MISMATCH")

    selection = payload.get("selection_rule")
    if not isinstance(selection, dict):
        failures.append("SELECTION_RULE_MISSING")
    else:
        expected_lower = [
            "api_p95_ms",
            "sse_first_event_p95_ms",
            "sse_reconnect_p95_ms",
            "cold_start_p95_ms",
            "persistence_p95_ms",
        ]
        expected_higher = ["max_level_throughput_rps"]
        if selection.get("hard_gates_first") is not True:
            failures.append("HARD_GATES_FIRST_REQUIRED")
        if selection.get("static_reject_never_receives_live_evidence_credit") is not True:
            failures.append("STATIC_REJECT_COMPENSATION_FORBIDDEN")
        if selection.get("unique_live_qualified_survivor_may_be_selected") is not True:
            failures.append("UNIQUE_SURVIVOR_RULE_MISSING")
        if selection.get("multiple_survivors_require_unique_pareto_dominance") is not True:
            failures.append("PARETO_RULE_MISSING")
        if selection.get("pareto_lower_is_better") != expected_lower:
            failures.append("PARETO_LOWER_AXES_MISMATCH")
        if selection.get("pareto_higher_is_better") != expected_higher:
            failures.append("PARETO_HIGHER_AXES_MISMATCH")
        if selection.get("ties_or_tradeoffs") != "NO_SELECTION":
            failures.append("PARETO_TRADEOFF_FAIL_CLOSED_MISSING")
        if selection.get("allowed_outcomes") != ["PROMOTE", "NO_SELECTION"]:
            failures.append("ALLOWED_OUTCOMES_MISMATCH")

    lowered_keys = tuple(key.lower() for key in _walk_keys(payload))
    for marker in FORBIDDEN_KEY_MARKERS:
        if any(marker in key for key in lowered_keys):
            failures.append(f"FORBIDDEN_SECRET_FIELD_{marker.upper()}")

    return tuple(dict.fromkeys(failures))


def validate_workflow_provider_free(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8").lower()
    markers = (
        "se" + "crets.",
        "terr" + "aform",
        "pul" + "umi",
        "kub" + "ectl",
        "gcl" + "oud ",
        "wran" + "gler",
        "vercel " + "deploy",
        "railway " + "up",
        "railway " + "deploy",
        "curl " + "http",
    )
    return tuple(
        f"FORBIDDEN_LIVE_CLOUD_SURFACE_{index}"
        for index, marker in enumerate(markers)
        if marker in text
    )


def main() -> int:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("cloud bakeoff preregistration must be a JSON object")
    failures = list(validate_manifest(payload))
    workflow_path = (
        ROOT
        / ".github"
        / "workflows"
        / "cloud-deployment-bakeoff-preregistration-provider-free.yml"
    )
    failures.extend(validate_workflow_provider_free(workflow_path))
    failures = list(dict.fromkeys(failures))
    summary = {
        "schema_version": "cloud-deployment-bakeoff-preregistration-validation-v1",
        "manifest_sha256": _canonical_sha256(payload),
        "expected_manifest_sha256": EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
        "provider_free": True,
        "live_cloud_actions_authorized": 0,
        "cloud_resources_authorized": 0,
        "outcome": "PASS" if not failures else "FAIL",
        "reason_codes": failures,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
