#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "research/experiments/p12-c4-nvidia-full-activation-and-capacity-gate-v1.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        item = {"name": name, "passed": bool(condition)}
        if detail:
            item["detail"] = detail
        checks.append(item)
        if not condition:
            raise AssertionError(f"P12-C4 NVIDIA activation gate failed: {name}: {detail}")

    check("provider_free_no_nvidia_secret_in_environment", not os.getenv("NVIDIA_API_KEY"))
    spec = load(SPEC)
    check("schema", spec.get("schema_version") == "p12-c4-nvidia-full-activation-and-capacity-gate-v1")
    check("gate_id", spec.get("gate_id") == "P12-C4-NVIDIA-FULL-PACKET-ACTIVATION-CAPACITY-V1")
    check("experiment_id", spec.get("experiment_id") == "P12-C4-PROSPECTIVE-EXPOSED-POOL")
    check("frozen_gate", spec.get("decision_state") == "FROZEN_PROVIDER_FREE_GATE" and spec.get("status") == "READY_FOR_PROVIDER_FREE_SELF_CHECK")

    pins = spec.get("source_pins") or {}
    check("source_pins_present", isinstance(pins, dict) and len(pins) == 7)
    loaded: dict[str, dict[str, Any]] = {}
    for key, pin in sorted(pins.items()):
        check(f"pin_shape:{key}", isinstance(pin, dict) and bool(pin.get("path")) and bool(pin.get("git_blob_sha")))
        path = ROOT / str(pin["path"])
        check(f"pin_exists:{key}", path.is_file(), str(path))
        check(f"pin_blob:{key}", git_blob_sha(path) == pin["git_blob_sha"], str(path))
        if path.suffix == ".json":
            loaded[key] = load(path)

    pass_artifact = loaded["synthetic_pass_artifact"]
    check("synthetic_pass_sha256", sha256(ROOT / pins["synthetic_pass_artifact"]["path"]) == spec["synthetic_prerequisite"]["canonical_pass_artifact_sha256"])
    check("synthetic_status_pass", pass_artifact.get("status") == "PASS")
    check("synthetic_exact_two_calls", pass_artifact.get("provider_calls") == 2 and pass_artifact.get("provider_request_attempts") == 2)
    check("synthetic_two_outputs", pass_artifact.get("successful_http_responses") == 2 and pass_artifact.get("model_outputs_observed") == 2)
    check("synthetic_no_retries_fallbacks", pass_artifact.get("automatic_retries") == 0 and pass_artifact.get("provider_fallbacks") == 0 and pass_artifact.get("model_fallbacks") == 0)
    check("synthetic_spacing", float(pass_artifact.get("minimum_seconds_between_any_provider_requests", 0)) >= 75)
    check("synthetic_restricted_access_zero", pass_artifact.get("benchmark_inputs_loaded") == 0 and pass_artifact.get("private_oracle_accesses") == 0 and pass_artifact.get("fresh_blind_accesses") == 0 and pass_artifact.get("legacy_locked_test_accesses") == 0)
    check("synthetic_does_not_authorize_full_packet", pass_artifact.get("full_packet_capacity_authorized_by_this_result") is False and pass_artifact.get("exposed_pool_live_generation_authorized_by_this_result") is False)
    check("synthetic_next_gate_exact", pass_artifact.get("next_gate") == "FULL_PROVIDER_FREE_C4_ACTIVATION_AND_CAPACITY_GATE")

    closure = loaded["synthetic_closure"]
    check("closure_status", closure.get("status") == "PASS_SYNTHETIC_COMPATIBILITY_2_OF_2")
    auth = closure.get("authorization") or {}
    check("synthetic_authorization_consumed", auth.get("consumed") is True and auth.get("rerun_allowed") is False)
    execution = closure.get("execution") or {}
    check("closure_exact_two", execution.get("provider_request_attempts") == 2 and execution.get("successful_http_responses") == 2 and execution.get("model_outputs_observed") == 2)
    check("closure_spacing", float(execution.get("observed_start_spacing_seconds", 0)) >= 75)
    restricted = closure.get("restricted_access_audit") or {}
    check("closure_restricted_zero", all(restricted.get(k) == 0 for k in ("benchmark_inputs_loaded", "private_oracle_accesses", "fresh_blind_accesses", "legacy_locked_test_accesses")))

    serving = loaded["serving_contract"]
    provider = serving.get("provider") or {}
    check("serving_contract_frozen", serving.get("schema_version") == "p12-c4-nvidia-provider-serving-contract-v1")
    check("provider_exact", provider.get("hosting_path") == "nvidia_hosted_nim" and provider.get("endpoint") == "https://integrate.api.nvidia.com/v1/chat/completions" and provider.get("model_id") == "openai/gpt-oss-120b" and provider.get("credential_env") == "NVIDIA_API_KEY")
    transport = serving.get("transport_contract") or {}
    check("transport_no_retries", transport.get("application_retries") == 0 and transport.get("implicit_retry_requests_allowed") is False and transport.get("follow_redirects") is False)
    packet = serving.get("packet_contract") or {}
    check("serving_geometry", packet.get("common_parent_generations") == 36 and packet.get("fixed_arm_outputs") == 144 and packet.get("participating_arms") == ["A00", "A10", "A01", "A11"])
    check("serving_complete_before_scoring", packet.get("complete_packet_required_before_scoring") is True and packet.get("partial_packet_scoring_forbidden") is True and packet.get("arm_specific_provider_calls_forbidden") is True)

    pacing = loaded["nvidia_pacing"]
    fp = pacing.get("frozen_pacing") or {}
    check("nvidia_pacing_geometry", fp.get("full_packet_common_parent_calls") == 36)
    check("nvidia_pacing_75_seconds", fp.get("minimum_seconds_between_any_provider_requests") >= 75)
    check("nvidia_pacing_zero_retry_warm_fallback", fp.get("automatic_retries") == 0 and fp.get("warming_requests") == 0 and fp.get("automatic_fallbacks") is False and fp.get("bursting_forbidden") is True)
    check("nvidia_pacing_historical_capacity_false", fp.get("full_packet_capacity_authorized") is False)

    seeds = loaded["fresh_seed_map"]
    parents = seeds.get("common_parents") or []
    parent_ids = [p.get("parent_id") for p in parents]
    seed_values = [p.get("seed") for p in parents]
    check("fresh_seed_map_frozen", seeds.get("status") == "FROZEN_PROVIDER_FREE_SEED_PLAN")
    check("fresh_36_parents", len(parents) == 36 and parent_ids == [f"P{i:02d}" for i in range(1, 37)])
    check("fresh_36_unique_seeds", len(seed_values) == 36 and len(set(seed_values)) == 36)
    invariants = seeds.get("invariants") or {}
    check("fresh_seed_invariants", invariants.get("common_parent_count") == 36 and invariants.get("no_seed_reuse_from_p12_c1_c2_c3_required") is True and invariants.get("partial_parent_reuse_forbidden") is True and invariants.get("arm_specific_seed_variation_forbidden") is True)
    seed_auth = seeds.get("authorization") or {}
    check("seed_plan_not_live_authorization", seed_auth.get("provider_calls") is False and seed_auth.get("exposed_pool_generation") is False and seed_auth.get("private_scoring") is False)

    prompt = loaded["prompt_budget_measurement"]
    measurement = prompt.get("provider_free_measurement") or {}
    frozen_pacing = prompt.get("frozen_pacing") or {}
    scope = prompt.get("scientific_scope") or {}
    check("prompt_measurement_36_provider_free", measurement.get("parents_materialized") == 36 and measurement.get("provider_calls") == 0 and measurement.get("credentials_read") == 0)
    check("prompt_bound_positive", 0 < measurement.get("max_conservative_prompt_upper_bound_tokens", 0) <= measurement.get("max_reserved_admission_tokens_including_completion", 0))
    check("prompt_pacing_75", frozen_pacing.get("minimum_seconds_between_any_provider_requests") >= 75 and frozen_pacing.get("implicit_sdk_retries") == 0 and frozen_pacing.get("implicit_sdk_warming_requests") == 0 and frozen_pacing.get("automatic_failover") is False)
    check("prompt_scope_fresh", scope.get("uses_c1_c2_c3_candidate_outputs") is False and scope.get("uses_c1_c2_c3_scores") is False and scope.get("uses_c2_c3_partial_parents") is False and scope.get("uses_c2_c3_live_seeds") is False)

    basis = spec.get("capacity_basis") or {}
    check("bounded_mode", basis.get("mode") == "BOUNDED_EXECUTION_PLAN_WITHOUT_QUOTA_GUARANTEE")
    check("quota_not_claimed", basis.get("provider_quota_guarantee") == "UNKNOWN_NOT_CLAIMED" and basis.get("published_free_endpoint_is_capacity_proof") is False and basis.get("synthetic_success_is_capacity_proof_for_36_calls") is False)
    bounded = spec.get("bounded_execution") or {}
    check("bounded_exact_36_attempts", bounded.get("common_parent_count") == 36 and bounded.get("maximum_provider_request_attempts") == 36 and bounded.get("maximum_provider_request_attempts_per_parent") == 1)
    check("bounded_pacing", bounded.get("minimum_seconds_between_provider_request_starts") >= 75 and bounded.get("bursting_forbidden") is True)
    check("bounded_zero_retry_fallback", bounded.get("automatic_retries") == 0 and bounded.get("implicit_retries_allowed") is False and bounded.get("warming_requests") == 0 and bounded.get("provider_fallbacks") == 0 and bounded.get("model_fallbacks") == 0)
    check("bounded_no_resume_or_rerun", bounded.get("resume_after_incomplete_packet") is False and bounded.get("github_workflow_rerun_allowed") is False and bounded.get("completed_parent_regeneration_allowed") is False)
    check("bounded_fail_closed", all(bounded.get(k) == "ABORT_PACKET_INCOMPLETE_NO_SCORING" for k in ("on_any_non_2xx", "on_any_invalid_or_unparseable_parent", "on_any_missing_parent")))

    boundary = spec.get("packet_and_scoring_boundary") or {}
    check("activation_36_then_144", boundary.get("required_common_parents_before_local_expansion") == "36/36" and boundary.get("required_fixed_arm_outputs_before_packet_freeze") == "144/144" and boundary.get("local_expansion_provider_calls") == 0)
    check("activation_scoring_denied_until_freeze", boundary.get("private_deterministic_scoring_before_complete_packet_freeze") == "FORBIDDEN" and boundary.get("partial_packet_scoring") == "FORBIDDEN" and boundary.get("complete_case_only_reinterpretation") == "FORBIDDEN")

    restricted_spec = spec.get("restricted_access") or {}
    check("gate_itself_provider_free", restricted_spec.get("provider_free_gate_loads_benchmark_inputs") is False and restricted_spec.get("provider_free_gate_reads_nvidia_api_key") is False and restricted_spec.get("provider_free_gate_network_calls_to_provider") == 0)
    check("gate_restricted_zero", restricted_spec.get("private_oracle_accesses") == 0 and restricted_spec.get("fresh_blind_accesses") == 0 and restricted_spec.get("legacy_locked_test_accesses") == 0)

    authorization = spec.get("authorization") or {}
    check("pre_selfcheck_not_live", authorization.get("full_packet_execution_authorized_before_self_check_pass") is False)
    check("one_manifest_only_if_pass", authorization.get("full_packet_execution_authorized_if_self_check_passes_and_live_manifest_is_frozen") is True and authorization.get("authorized_live_manifests_if_passed") == 1)
    check("scoring_and_blind_still_denied", authorization.get("private_scoring") is False and authorization.get("fresh_blind") is False and authorization.get("legacy_locked_test") is False)

    passed = sum(1 for c in checks if c["passed"])
    result = {
        "schema_version": "p12-c4-nvidia-full-activation-and-capacity-self-check-v1",
        "gate_id": spec["gate_id"],
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "provider_calls": 0,
        "credentials_read": 0,
        "benchmark_inputs_loaded": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "capacity_basis": basis,
        "bounded_execution": bounded,
        "common_parents_authorized_if_live_manifest_frozen": 36,
        "maximum_provider_request_attempts_if_live_manifest_frozen": 36,
        "fixed_arm_outputs_required_before_scoring": 144,
        "execution_authorized_by_this_gate": passed == len(checks),
        "live_manifest_frozen_by_this_gate": False,
        "private_scoring_authorized_by_this_gate": False,
        "next_gate": "FREEZE_ONE_SHOT_C4_LIVE_MANIFEST" if passed == len(checks) else "STOP_C4_NO_LIVE_MANIFEST",
        "checks": checks,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run()
    except Exception as exc:
        result = {
            "schema_version": "p12-c4-nvidia-full-activation-and-capacity-self-check-v1",
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "provider_calls": 0,
            "credentials_read": 0,
            "execution_authorized_by_this_gate": False,
            "live_manifest_frozen_by_this_gate": False,
            "private_scoring_authorized_by_this_gate": False,
            "next_gate": "STOP_C4_NO_LIVE_MANIFEST",
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks_passed", "checks_total", "provider_calls", "execution_authorized_by_this_gate", "next_gate")}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
