#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "research/experiments/p12-c4-nvidia-one-shot-live-manifest-v1.json"


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
        item: dict[str, Any] = {"name": name, "passed": bool(condition)}
        if detail:
            item["detail"] = detail
        checks.append(item)
        if not condition:
            raise AssertionError(f"P12-C4 NVIDIA one-shot manifest failed: {name}: {detail}")

    check("provider_free_no_nvidia_secret_in_environment", not os.getenv("NVIDIA_API_KEY"))
    manifest = load(MANIFEST)
    check("schema", manifest.get("schema_version") == "p12-c4-nvidia-one-shot-live-manifest-v1")
    check("manifest_id", manifest.get("manifest_id") == "P12-C4-NVIDIA-ONE-SHOT-LIVE-V1")
    check("experiment_id", manifest.get("experiment_id") == "P12-C4-PROSPECTIVE-EXPOSED-POOL")
    check("status_pending_live", manifest.get("status") == "FROZEN_PROVIDER_FREE_PENDING_LIVE_EXECUTION")

    pins = manifest.get("source_pins") or {}
    check("source_pins_exact_count", isinstance(pins, dict) and len(pins) == 7)
    loaded: dict[str, dict[str, Any]] = {}
    for key, pin in sorted(pins.items()):
        check(f"pin_shape:{key}", isinstance(pin, dict) and bool(pin.get("path")) and bool(pin.get("git_blob_sha")))
        path = ROOT / str(pin["path"])
        check(f"pin_exists:{key}", path.is_file(), str(path))
        check(f"pin_blob:{key}", git_blob_sha(path) == pin["git_blob_sha"], str(path))
        if path.suffix == ".json":
            loaded[key] = load(path)

    activation_spec = loaded["activation_gate_spec"]
    activation_result = loaded["activation_gate_evidence"]
    activation_closure = loaded["activation_gate_closure"]

    check("activation_gate_spec_exact", activation_spec.get("gate_id") == "P12-C4-NVIDIA-FULL-PACKET-ACTIVATION-CAPACITY-V1")
    check(
        "activation_result_pass_73_of_73",
        activation_result.get("status") == "PASS"
        and activation_result.get("all_passed") is True
        and activation_result.get("checks_passed") == 73
        and activation_result.get("checks_total") == 73,
    )
    check(
        "activation_result_provider_free",
        activation_result.get("provider_calls") == 0
        and activation_result.get("credentials_read") == 0
        and activation_result.get("benchmark_inputs_loaded") == 0,
    )
    check("activation_result_next_gate", activation_result.get("next_gate") == "FREEZE_ONE_SHOT_C4_LIVE_MANIFEST")
    check("activation_result_manifest_not_pre_frozen", activation_result.get("live_manifest_frozen_by_this_gate") is False)

    boundary = activation_closure.get("authorization_boundary") or {}
    check("activation_closure_pass", activation_closure.get("status") == "PASS_PROVIDER_FREE_ACTIVATION_CAPACITY")
    check("activation_closure_one_manifest", boundary.get("one_live_manifest_may_be_frozen") is True)
    check(
        "activation_closure_36_by_1",
        boundary.get("maximum_provider_request_attempts_under_that_manifest") == 36
        and boundary.get("maximum_attempts_per_parent") == 1,
    )
    check("activation_closure_pacing", boundary.get("minimum_seconds_between_request_starts") >= 75)
    check(
        "activation_closure_zero_retry_fallback",
        boundary.get("automatic_retries") == 0
        and boundary.get("provider_fallbacks") == 0
        and boundary.get("model_fallbacks") == 0,
    )
    check(
        "activation_closure_no_resume_rerun_scoring",
        boundary.get("resume_after_incomplete_packet") is False
        and boundary.get("workflow_rerun_allowed") is False
        and boundary.get("private_scoring_authorized") is False,
    )
    check("activation_closure_next_gate", activation_closure.get("next_gate") == "FREEZE_ONE_SHOT_C4_LIVE_MANIFEST")

    serving = loaded["serving_contract"]
    provider = manifest.get("provider") or {}
    serving_provider = serving.get("provider") or {}
    check(
        "provider_exactly_pinned",
        provider.get("name") == "NVIDIA"
        and provider.get("hosting_path") == serving_provider.get("hosting_path") == "nvidia_hosted_nim"
        and provider.get("endpoint") == serving_provider.get("endpoint") == "https://integrate.api.nvidia.com/v1/chat/completions"
        and provider.get("model_id") == serving_provider.get("model_id") == "openai/gpt-oss-120b"
        and provider.get("credential_env") == serving_provider.get("credential_env") == "NVIDIA_API_KEY",
    )
    check(
        "provider_no_fallback",
        provider.get("fallback_provider") is None
        and provider.get("model_fallbacks") == []
        and provider.get("automatic_failover") is False,
    )

    semantics = manifest.get("request_semantics") or {}
    frozen_semantics = serving.get("frozen_request_semantics") or {}
    check(
        "request_semantics_core_match_serving",
        semantics.get("temperature") == frozen_semantics.get("temperature") == 0
        and semantics.get("max_tokens") == frozen_semantics.get("max_tokens") == 4096
        and semantics.get("reasoning_effort") == frozen_semantics.get("reasoning_effort") == "medium"
        and semantics.get("stream") is frozen_semantics.get("stream") is False,
    )
    check(
        "request_semantics_seed_and_structure",
        semantics.get("seed_required_per_request") is True
        and semantics.get("response_format") == "json_schema_strict"
        and semantics.get("parallel_tool_calls") is False
        and semantics.get("drop_reasoning_content_before_persistence") is True,
    )

    transport = manifest.get("transport") or {}
    serving_transport = serving.get("transport_contract") or {}
    check(
        "transport_exact",
        all(transport.get(k) == serving_transport.get(k) for k in (
            "client", "version", "connect_timeout_seconds", "read_timeout_seconds",
            "write_timeout_seconds", "pool_timeout_seconds", "follow_redirects",
            "application_retries", "implicit_retries_allowed",
        )),
    )

    pacing = loaded["request_budget_and_pacing"].get("frozen_pacing") or {}
    execution = manifest.get("one_shot_execution") or {}
    check("one_shot_36", execution.get("common_parent_count") == 36 and execution.get("maximum_provider_request_attempts") == 36)
    check("one_shot_one_per_parent", execution.get("maximum_attempts_per_parent") == 1)
    check(
        "one_shot_75_seconds",
        execution.get("minimum_seconds_between_request_starts") >= 75
        and pacing.get("minimum_seconds_between_any_provider_requests") >= 75,
    )
    check(
        "one_shot_zero_retry_warm_fallback",
        execution.get("automatic_retries") == 0
        and execution.get("warming_requests") == 0
        and execution.get("provider_fallbacks") == 0
        and execution.get("model_fallbacks") == 0,
    )
    check(
        "one_shot_no_resume_rerun_regeneration",
        execution.get("resume_after_incomplete_packet") is False
        and execution.get("workflow_rerun_allowed") is False
        and execution.get("completed_parent_regeneration_allowed") is False,
    )
    check("one_shot_bursting_forbidden", execution.get("bursting_forbidden") is True)
    failure_policy = execution.get("failure_policy") or {}
    check(
        "one_shot_fail_closed_all_failure_modes",
        set(failure_policy) == {
            "non_2xx", "invalid_or_unparseable_parent", "missing_parent",
            "duplicate_parent", "seed_or_parent_mismatch",
        }
        and all(v == "ABORT_PACKET_INCOMPLETE_NO_SCORING" for v in failure_policy.values()),
    )

    seed_map = loaded["fresh_seed_map"]
    seed_parents = seed_map.get("common_parents") or []
    ordered = manifest.get("ordered_requests") or []
    expected_ids = [f"P{i:02d}" for i in range(1, 37)]
    check("seed_map_frozen", seed_map.get("status") == "FROZEN_PROVIDER_FREE_SEED_PLAN")
    check("manifest_exactly_36_ordered_requests", len(ordered) == 36)
    check("manifest_parent_order_exact", [x.get("parent_id") for x in ordered] == expected_ids)
    check("manifest_ordinals_exact", [x.get("ordinal") for x in ordered] == list(range(1, 37)))
    check("manifest_seeds_unique", len({x.get("seed") for x in ordered}) == 36)
    check(
        "manifest_requests_equal_frozen_seed_map",
        [(x.get("ordinal"), x.get("parent_id"), x.get("seed")) for x in ordered]
        == [(x.get("ordinal"), x.get("parent_id"), x.get("seed")) for x in seed_parents],
    )
    check("manifest_each_parent_max_one_attempt", all(x.get("maximum_attempts") == 1 for x in ordered))

    live = manifest.get("live_output_contract") or {}
    check(
        "live_output_common_parents_only",
        live.get("provider_calls_write_only_common_parents") is True
        and live.get("required_valid_common_parents") == "36/36",
    )
    check("live_partial_packet_terminal", live.get("partial_live_packet_is_terminal_incomplete") is True)
    check(
        "live_namespace_frozen",
        live.get("namespace") == "research/live/p12-c4-nvidia-one-shot-v1"
        and live.get("common_parent_output") == "research/live/p12-c4-nvidia-one-shot-v1/common-parents.jsonl"
        and live.get("request_ledger") == "research/live/p12-c4-nvidia-one-shot-v1/request-ledger.jsonl",
    )

    local = manifest.get("local_arm_expansion") or {}
    check("local_expansion_only_after_36", local.get("authorized_only_after_valid_common_parents") == "36/36")
    check("local_expansion_zero_provider_calls", local.get("provider_calls") == 0)
    check("local_expansion_four_arms", local.get("arms") == ["A00", "A10", "A01", "A11"] and local.get("expected_outputs_per_parent") == 4)
    check("local_expansion_same_parent", local.get("same_common_parent_for_all_four_arms") is True)
    check("local_expansion_requires_144", local.get("required_fixed_arm_outputs") == "144/144" and local.get("partial_expansion_blocks_packet_freeze") is True)

    scoring = manifest.get("packet_freeze_and_scoring_boundary") or {}
    check("packet_freeze_requires_144", scoring.get("complete_packet_freeze_requires") == "144/144")
    check(
        "scoring_forbidden_before_freeze",
        scoring.get("deterministic_private_scoring_before_packet_freeze") == "FORBIDDEN"
        and scoring.get("partial_packet_scoring") == "FORBIDDEN"
        and scoring.get("bootstrap_before_deterministic_scoring") == "FORBIDDEN",
    )
    check(
        "transition_chain_exact",
        scoring.get("next_gate_after_manifest_freeze") == "C4_36_OF_36_FRESH_COMMON_PARENTS"
        and scoring.get("next_gate_after_36_of_36") == "C4_144_OF_144_LOCAL_ARM_OUTPUTS"
        and scoring.get("next_gate_after_144_of_144") == "FREEZE_COMPLETE_C4_PACKET"
        and scoring.get("next_gate_after_packet_freeze") == "DETERMINISTIC_SCORING",
    )

    scientific = manifest.get("scientific_boundary") or {}
    check(
        "single_manifest_single_attempt",
        scientific.get("manifest_count_authorized") == 1
        and scientific.get("live_execution_attempts_authorized") == 1,
    )
    check("quota_not_claimed", scientific.get("provider_quota_guarantee") == "UNKNOWN_NOT_CLAIMED")
    check(
        "no_post_outcome_mutation",
        scientific.get("no_post_outcome_manifest_mutation") is True
        and scientific.get("no_partial_packet_reinterpretation") is True,
    )

    restricted = manifest.get("restricted_access") or {}
    check(
        "selfcheck_provider_free_by_contract",
        restricted.get("provider_free_self_check_reads_credentials") is False
        and restricted.get("provider_free_self_check_network_calls") == 0
        and restricted.get("provider_free_self_check_loads_benchmark_inputs") is False,
    )
    check(
        "restricted_access_zero",
        restricted.get("private_oracle_accesses") == 0
        and restricted.get("fresh_blind_accesses") == 0
        and restricted.get("legacy_locked_test_accesses") == 0,
    )

    auth = manifest.get("authorization") or {}
    check("manifest_freeze_authorized", auth.get("manifest_freeze_authorized_by_activation_gate") is True)
    check("live_execution_exact_manifest_only", auth.get("live_provider_execution_permitted_only_under_this_exact_manifest") is True)
    check("scoring_and_blind_still_denied", auth.get("private_scoring") is False and auth.get("fresh_blind") is False and auth.get("legacy_locked_test") is False)

    passed = sum(1 for c in checks if c["passed"])
    all_passed = passed == len(checks)
    result = {
        "schema_version": "p12-c4-nvidia-one-shot-live-manifest-self-check-v1",
        "manifest_id": manifest["manifest_id"],
        "status": "PASS" if all_passed else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": all_passed,
        "provider_calls": 0,
        "credentials_read": 0,
        "benchmark_inputs_loaded": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "manifest_git_blob_sha": git_blob_sha(MANIFEST),
        "manifest_sha256": sha256(MANIFEST),
        "live_execution_attempts_authorized_if_pass": 1 if all_passed else 0,
        "maximum_provider_request_attempts_if_pass": 36 if all_passed else 0,
        "maximum_attempts_per_parent_if_pass": 1 if all_passed else 0,
        "minimum_seconds_between_request_starts": 75,
        "expected_fresh_common_parents": 36,
        "expected_local_arm_outputs_after_complete_live_packet": 144,
        "live_execution_performed_by_this_check": False,
        "common_parents_generated_by_this_check": 0,
        "local_arm_outputs_generated_by_this_check": 0,
        "private_scoring_authorized_by_this_check": False,
        "next_gate": "C4_36_OF_36_FRESH_COMMON_PARENTS" if all_passed else "STOP_C4_NO_LIVE_EXECUTION",
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
            "schema_version": "p12-c4-nvidia-one-shot-live-manifest-self-check-v1",
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "provider_calls": 0,
            "credentials_read": 0,
            "live_execution_performed_by_this_check": False,
            "private_scoring_authorized_by_this_check": False,
            "next_gate": "STOP_C4_NO_LIVE_EXECUTION",
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        k: result[k] for k in (
            "status", "checks_passed", "checks_total", "provider_calls",
            "live_execution_attempts_authorized_if_pass", "next_gate",
        )
    }, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
