from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path

from pydantic import ValidationError
import pytest

from academy_tractian.deployment_bakeoff import (
    EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256,
    EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
    build_deployment_runtime_evidence,
    decide_deployment_bakeoff,
    expected_topology_rules,
)
from academy_tractian.deployment_feasibility import DeploymentFeasibilityDecision
from academy_tractian.hosted_state_identity_pilot import (
    HostedStateIdentityPilotPolicy,
    build_hosted_state_identity_pilot_evidence,
    decide_hosted_state_identity_pilot,
)
from academy_tractian.live_deployment_attestation import (
    LiveDeploymentPolicy,
    build_live_deployment_attestation,
    decide_live_deployment_attestation,
)
from academy_tractian.load_concurrency_benchmark import (
    LoadBenchmarkProtocol,
    LoadPressureObservation,
    LoadRequestObservation,
    analyze_load_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "experiments" / "cloud-deployment-bakeoff-preregistration-v1.json"
NOW = datetime(2026, 9, 4, 22, 0, tzinfo=UTC)
CODE_SHA = "1" * 40
ORIGIN_SHA = "2" * 64
IMAGE_DIGEST = "sha256:" + "3" * 64
EVIDENCE_SHA = "4" * 64


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _feasibility(candidate_id: str, *, admissible: bool) -> DeploymentFeasibilityDecision:
    return DeploymentFeasibilityDecision(
        candidate_id=candidate_id,
        outcome="PILOT_ADMISSIBLE" if admissible else "STATIC_REJECT",
        reason_codes=() if admissible else ("SYNTHETIC_STATIC_REJECT",),
        evidence_sha256=EVIDENCE_SHA,
    )


def _pilot(*, code_sha: str = CODE_SHA, origin_sha: str = ORIGIN_SHA):
    evidence = build_hosted_state_identity_pilot_evidence(
        bundle_id="neon-plus-auth0",
        code_sha=code_sha,
        collected_at=NOW,
        deployment_origin_sha256=origin_sha,
        database_endpoint_sha256="5" * 64,
        identity_issuer_sha256="6" * 64,
        required_local_components=0,
        observed_unexpected_cash_charge_usd=0.0,
        organization_count=2,
        user_count=2,
        clean_migration_passed=True,
        pooled_tls_postgres_passed=True,
        oidc_valid_token_accepted=True,
        oidc_jwks_rs256_verified=True,
        exact_audience_verified=True,
        exact_issuer_verified=True,
        organization_claim_verified=True,
        role_claim_verified=True,
        permission_allowlist_verified=True,
        token_ttl_verified=True,
        allowed_tenant_request_passed=True,
        cross_tenant_read_denied=True,
        cross_tenant_mutation_denied=True,
        expired_token_rejected=True,
        wrong_audience_rejected=True,
        wrong_issuer_rejected=True,
        malformed_token_rejected=True,
        unknown_organization_rejected=True,
        sse_reconnect_tenant_isolation_passed=True,
        restart_persistence_passed=True,
    )
    decision = decide_hosted_state_identity_pilot(
        evidence=evidence,
        policy=HostedStateIdentityPilotPolicy(),
    )
    assert decision.outcome == "PILOT_PASS"
    return evidence, decision


def _live(candidate_id: str, *, deployment_id: str, code_sha: str = CODE_SHA):
    evidence = build_live_deployment_attestation(
        candidate_id=candidate_id,
        deployment_id=deployment_id,
        collected_at=NOW,
        expected_source_revision=code_sha,
        observed_source_revision=code_sha,
        expected_branch="feat/cloud-production-baseline",
        observed_branch="feat/cloud-production-baseline",
        expected_build_contract="root-dockerfile",
        observed_build_contract="root-dockerfile",
        expected_python_major_minor="3.11",
        observed_python_version="3.11.16",
    )
    decision = decide_live_deployment_attestation(
        evidence=evidence,
        policy=LiveDeploymentPolicy(),
    )
    assert decision.outcome == "LIVE_ATTESTATION_PASS"
    return evidence, decision


def _report(*, max_level_throughput_rps: float = 5.0):
    protocol = LoadBenchmarkProtocol(
        protocol_id="cloud-bakeoff-load-v1",
        concurrency_levels=(1, 5, 20, 50),
        requests_per_level=20,
        warmup_requests=0,
    )
    assert protocol.sha256() == EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256

    requests = tuple(
        LoadRequestObservation(
            concurrency_level=level,
            request_index=index,
            submit_status_code=202,
            submit_latency_ms=5.0 + level / 10,
            end_to_end_latency_ms=50.0 + level,
            terminal_state="completed",
        )
        for level in protocol.concurrency_levels
        for index in range(protocol.requests_per_level)
    )
    pressure = tuple(
        LoadPressureObservation(
            concurrency_level=level,
            elapsed_ms=1.0,
            active_runs=min(level, 8),
            queued_runs=max(level - 8, 0),
            inflight_runs=level,
            max_workers=8,
            executor_utilization=min(level / 8, 1.0),
            process_cpu_time_ms=10.0,
            rss_current_bytes=10_000_000,
            rss_max_bytes=10_000_000,
            persistence_p95_ms=4.0,
        )
        for level in protocol.concurrency_levels
    )
    durations = {
        1: 20.0,
        5: 10.0,
        20: 5.0,
        50: 20.0 / max_level_throughput_rps,
    }
    return analyze_load_benchmark(
        protocol,
        requests=requests,
        pressure=pressure,
        wall_duration_seconds=durations,
    )


def _runtime(
    rule,
    report,
    *,
    deployment_id: str,
    code_sha: str = CODE_SHA,
    origin_sha: str = ORIGIN_SHA,
    api_p95_ms: float = 100.0,
    sse_first_event_p95_ms: float = 90.0,
    sse_reconnect_p95_ms: float = 80.0,
    cold_start_p95_ms: float = 500.0,
    persistence_p95_ms: float = 20.0,
    tenant_leak_count: int = 0,
    load_report_sha256: str | None = None,
):
    max_level = max(report.levels, key=lambda item: item.concurrency_level)
    return build_deployment_runtime_evidence(
        manifest_sha256=EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
        topology_id=rule.topology_id,
        compute_candidate_id=rule.compute_candidate_id,
        state_identity_bundle_id=rule.state_identity_bundle_id,
        deployment_id=deployment_id,
        deployment_origin_sha256=origin_sha,
        code_sha=code_sha,
        image_digest=IMAGE_DIGEST,
        load_protocol_sha256=EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256,
        load_report_sha256=load_report_sha256 or report.evidence_sha256,
        required_local_components=0,
        observed_cash_cost_usd=0.0,
        tenant_leak_count=tenant_leak_count,
        forbidden_data_leak_count=0,
        duplicate_action_count=0,
        sse_gap_count=0,
        sse_duplicate_event_count=0,
        unrecoverable_sse_reconnect_count=0,
        recovery_failure_count=0,
        persistence_integrity_failure_count=0,
        load_error_count=0,
        api_p95_ms=api_p95_ms,
        sse_first_event_p95_ms=sse_first_event_p95_ms,
        sse_reconnect_p95_ms=sse_reconnect_p95_ms,
        cold_start_p95_ms=cold_start_p95_ms,
        persistence_p95_ms=persistence_p95_ms,
        max_level_throughput_rps=max_level.completed_throughput_rps,
    )


def _complete_inputs(
    *,
    admissible_candidates: tuple[str, ...],
    runtime_overrides: dict[str, dict] | None = None,
    throughput: dict[str, float] | None = None,
):
    rules = expected_topology_rules()
    runtime_overrides = runtime_overrides or {}
    throughput = throughput or {}
    feasibility = tuple(
        _feasibility(
            rule.compute_candidate_id,
            admissible=rule.compute_candidate_id in admissible_candidates,
        )
        for rule in rules
    )
    pilot_decisions = {}
    pilot_evidence = {}
    live_decisions = []
    live_evidence = []
    runtime = []
    reports = {}
    for rule in rules:
        if rule.compute_candidate_id not in admissible_candidates:
            continue
        deployment_id = f"deployment-{rule.compute_candidate_id}"
        pilot_ev, pilot_dec = _pilot()
        pilot_evidence[rule.topology_id] = pilot_ev
        pilot_decisions[rule.topology_id] = pilot_dec
        live_ev, live_dec = _live(rule.compute_candidate_id, deployment_id=deployment_id)
        live_evidence.append(live_ev)
        live_decisions.append(live_dec)
        report = _report(max_level_throughput_rps=throughput.get(rule.compute_candidate_id, 5.0))
        reports[rule.topology_id] = report
        runtime.append(
            _runtime(
                rule,
                report,
                deployment_id=deployment_id,
                **runtime_overrides.get(rule.compute_candidate_id, {}),
            )
        )
    return {
        "manifest_sha256": EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
        "topology_rules": rules,
        "feasibility_decisions": feasibility,
        "state_identity_pilot_decisions": pilot_decisions,
        "state_identity_pilot_evidence": pilot_evidence,
        "live_attestation_decisions": tuple(live_decisions),
        "live_attestation_evidence": tuple(live_evidence),
        "runtime_evidence": tuple(runtime),
        "load_reports": reports,
    }


def _assessment(decision, candidate_id: str):
    return next(item for item in decision.assessments if item.compute_candidate_id == candidate_id)


def test_preregistration_hash_and_frontier_are_frozen_before_live_data() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert _canonical_sha256(payload) == EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256
    assert payload["live_cloud_actions_authorized_now"] == 0
    assert payload["cloud_resources_authorized_now"] == 0
    assert payload["production_cloud_selected"] is False
    assert payload["weighted_composite_score_forbidden"] is True
    assert tuple(payload["selection_rule"]["pareto_lower_is_better"]) == (
        "api_p95_ms",
        "sse_first_event_p95_ms",
        "sse_reconnect_p95_ms",
        "cold_start_p95_ms",
        "persistence_p95_ms",
    )
    assert tuple(item["candidate_id"] for item in payload["candidate_topologies"]) == tuple(
        rule.topology_id for rule in expected_topology_rules()
    )


def test_frontier_subset_cannot_manufacture_a_unique_survivor() -> None:
    inputs = _complete_inputs(admissible_candidates=("oracle-oci-always-free-a1",))
    inputs["topology_rules"] = inputs["topology_rules"][:1]
    decision = decide_deployment_bakeoff(**inputs)
    assert decision.outcome == "NO_SELECTION"
    assert decision.reason_codes == ("TOPOLOGY_FRONTIER_MISMATCH",)


def test_static_rejection_is_terminal_and_receives_no_live_credit() -> None:
    rules = expected_topology_rules()
    decision = decide_deployment_bakeoff(
        manifest_sha256=EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256,
        topology_rules=rules,
        feasibility_decisions=tuple(
            _feasibility(rule.compute_candidate_id, admissible=False) for rule in rules
        ),
        state_identity_pilot_decisions={},
        state_identity_pilot_evidence={},
        live_attestation_decisions=(),
        live_attestation_evidence=(),
        runtime_evidence=(),
        load_reports={},
    )
    oracle = _assessment(decision, "oracle-oci-always-free-a1")
    assert oracle.reason_codes == ("STATIC_FEASIBILITY_REJECTED",)
    assert decision.outcome == "NO_SELECTION"


def test_unique_hard_gate_survivor_can_be_promoted_only_with_complete_live_bindings() -> None:
    decision = decide_deployment_bakeoff(
        **_complete_inputs(admissible_candidates=("oracle-oci-always-free-a1",))
    )
    assert decision.outcome == "PROMOTE"
    assert decision.selected_topology_id == "oracle-oci-always-free-a1+neon-plus-auth0"
    assert decision.reason_codes == ("UNIQUE_HARD_GATE_SURVIVOR_LIVE_QUALIFIED",)


def test_nonzero_tenant_leak_is_non_compensatory() -> None:
    inputs = _complete_inputs(
        admissible_candidates=("oracle-oci-always-free-a1",),
        runtime_overrides={"oracle-oci-always-free-a1": {"tenant_leak_count": 1}},
    )
    decision = decide_deployment_bakeoff(**inputs)
    assert decision.outcome == "NO_SELECTION"
    assert "TENANT_LEAK_OBSERVED" in _assessment(
        decision, "oracle-oci-always-free-a1"
    ).reason_codes


def test_runtime_code_sha_must_match_both_live_attestation_and_state_identity_pilot() -> None:
    inputs = _complete_inputs(
        admissible_candidates=("oracle-oci-always-free-a1",),
        runtime_overrides={"oracle-oci-always-free-a1": {"code_sha": "9" * 40}},
    )
    decision = decide_deployment_bakeoff(**inputs)
    reasons = _assessment(decision, "oracle-oci-always-free-a1").reason_codes
    assert "RUNTIME_CODE_SHA_BINDING_MISMATCH" in reasons
    assert decision.outcome == "NO_SELECTION"


def test_runtime_origin_must_match_state_identity_pilot_origin() -> None:
    inputs = _complete_inputs(
        admissible_candidates=("oracle-oci-always-free-a1",),
        runtime_overrides={"oracle-oci-always-free-a1": {"origin_sha": "8" * 64}},
    )
    decision = decide_deployment_bakeoff(**inputs)
    assert "RUNTIME_DEPLOYMENT_ORIGIN_BINDING_MISMATCH" in _assessment(
        decision, "oracle-oci-always-free-a1"
    ).reason_codes


def test_load_report_hash_is_bound_to_runtime_evidence() -> None:
    inputs = _complete_inputs(
        admissible_candidates=("oracle-oci-always-free-a1",),
        runtime_overrides={"oracle-oci-always-free-a1": {"load_report_sha256": "7" * 64}},
    )
    decision = decide_deployment_bakeoff(**inputs)
    assert "LOAD_REPORT_HASH_MISMATCH" in _assessment(
        decision, "oracle-oci-always-free-a1"
    ).reason_codes


def test_unique_pareto_dominator_is_selected_without_weighted_score() -> None:
    candidates = ("oracle-oci-always-free-a1", "google-cloud-run-request-free-tier")
    inputs = _complete_inputs(
        admissible_candidates=candidates,
        throughput={
            "oracle-oci-always-free-a1": 8.0,
            "google-cloud-run-request-free-tier": 5.0,
        },
        runtime_overrides={
            "oracle-oci-always-free-a1": {
                "api_p95_ms": 80.0,
                "sse_first_event_p95_ms": 70.0,
                "sse_reconnect_p95_ms": 60.0,
                "cold_start_p95_ms": 300.0,
                "persistence_p95_ms": 15.0,
            },
            "google-cloud-run-request-free-tier": {
                "api_p95_ms": 100.0,
                "sse_first_event_p95_ms": 90.0,
                "sse_reconnect_p95_ms": 80.0,
                "cold_start_p95_ms": 500.0,
                "persistence_p95_ms": 20.0,
            },
        },
    )
    decision = decide_deployment_bakeoff(**inputs)
    assert decision.outcome == "PROMOTE"
    assert decision.selected_topology_id == "oracle-oci-always-free-a1+neon-plus-auth0"
    assert decision.reason_codes == ("UNIQUE_PARETO_DOMINANT_TOPOLOGY",)


def test_sse_first_event_tradeoff_prevents_post_hoc_promotion() -> None:
    candidates = ("oracle-oci-always-free-a1", "google-cloud-run-request-free-tier")
    inputs = _complete_inputs(
        admissible_candidates=candidates,
        throughput={
            "oracle-oci-always-free-a1": 8.0,
            "google-cloud-run-request-free-tier": 5.0,
        },
        runtime_overrides={
            "oracle-oci-always-free-a1": {
                "api_p95_ms": 80.0,
                "sse_first_event_p95_ms": 200.0,
                "sse_reconnect_p95_ms": 60.0,
                "cold_start_p95_ms": 300.0,
                "persistence_p95_ms": 15.0,
            },
            "google-cloud-run-request-free-tier": {
                "api_p95_ms": 100.0,
                "sse_first_event_p95_ms": 70.0,
                "sse_reconnect_p95_ms": 80.0,
                "cold_start_p95_ms": 500.0,
                "persistence_p95_ms": 20.0,
            },
        },
    )
    decision = decide_deployment_bakeoff(**inputs)
    assert decision.outcome == "NO_SELECTION"
    assert decision.selected_topology_id is None
    assert decision.reason_codes == ("NO_UNIQUE_PARETO_DOMINANT_TOPOLOGY",)


def test_runtime_evidence_hash_is_tamper_evident() -> None:
    inputs = _complete_inputs(admissible_candidates=("oracle-oci-always-free-a1",))
    evidence = inputs["runtime_evidence"][0]
    payload = evidence.model_dump(mode="json")
    payload["api_p95_ms"] = payload["api_p95_ms"] + 1
    with pytest.raises(ValidationError, match="deployment_runtime_evidence_hash_mismatch"):
        type(evidence).model_validate(payload)
