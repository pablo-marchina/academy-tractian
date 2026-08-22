#!/usr/bin/env python3
"""Provider-free structural/self-check for the frozen BIG-B4 protocol."""

from __future__ import annotations

import json
from typing import Any

from scripts.research.big_b4_protocol_guard import (
    AUTH_TEMPLATE_PATH,
    FREEZE_TEMPLATE_PATH,
    access_decision,
    final_authorization_ready,
    load_json,
    validate_blind_registry,
    validate_candidate_freeze,
    validate_protocol,
)


def _record(results: list[dict[str, Any]], name: str, condition: bool, detail: str) -> None:
    results.append({"check": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def _decision(
    results: list[dict[str, Any]],
    protocol: dict[str, Any],
    name: str,
    expected_allow: bool,
    **kwargs: Any,
) -> None:
    allowed, reason = access_decision(protocol, **kwargs)
    _record(results, name, allowed is expected_allow, f"allowed={allowed}; reason={reason}")


def main() -> int:
    results: list[dict[str, Any]] = []
    protocol = validate_protocol()
    registry = validate_blind_registry()
    _record(results, "protocol_manifest_valid", True, protocol["protocol_id"])
    _record(results, "blind_registry_fail_closed", registry["authorization_state"] == "NO_BLIND_SOURCE_AUTHORIZED", registry["authorization_state"])

    freeze_template = load_json(FREEZE_TEMPLATE_PATH)
    freeze_ok, freeze_missing = validate_candidate_freeze(freeze_template)
    _record(results, "unfrozen_candidate_template_cannot_authorize", not freeze_ok, f"missing={freeze_missing}")

    auth_template = load_json(AUTH_TEMPLATE_PATH)
    auth_ok, auth_missing = final_authorization_ready(auth_template)
    _record(results, "authorization_template_defaults_denied", not auth_ok and auth_template.get("authorized") is False, f"missing={auth_missing}")

    valid_freeze = dict(freeze_template)
    valid_freeze.update({
        "status": "FROZEN_GENERATION",
        "generation_id": "SELF_CHECK_GENERATION",
        "candidate_code_hash": "sha256:self-check-code",
        "candidate_config_hash": "sha256:self-check-config",
        "prompt_hash": "sha256:self-check-prompt",
        "model_provider_runtime_identity": "self-check-model-provider-runtime",
        "retrieval_policy_hash": "sha256:self-check-retrieval",
        "guard_policy_hash": "sha256:self-check-guard",
        "evaluator_version_hash": "sha256:self-check-evaluator",
        "semantic_judge_manifest_hash_or_not_applicable": "NOT_APPLICABLE",
        "seed_policy": {"paired": True, "seeds": [1, 2, 3]},
        "primary_outcomes": ["task_quality_or_task_success", "evidence_correctness"],
        "hard_safety_constraints": ["unauthorized_side_effect"],
        "repetitions_per_scenario": 3,
        "uncertainty_method": "GROUP_CLUSTER_PERCENTILE_BOOTSTRAP",
        "frozen_at": "SELF_CHECK_ONLY",
        "ready_for_final_authorization": True,
    })
    freeze_ok, freeze_missing = validate_candidate_freeze(valid_freeze)
    _record(results, "complete_candidate_generation_can_pass_freeze_schema", freeze_ok, f"missing={freeze_missing}")

    valid_auth = dict(auth_template)
    valid_auth.update({
        "status": "AUTHORIZED_SELF_CHECK_ONLY",
        "authorization_id": "SELF_CHECK_AUTH",
        "generation_id": "SELF_CHECK_GENERATION",
        "partition": "FRESH_BLIND",
        "blind_source_id_or_legacy_locked_test": "SELF_CHECK_SOURCE",
        "candidate_freeze_hash": "sha256:self-check-freeze",
        "candidate_generation_frozen": True,
        "evaluator_qualified_and_hash_frozen": True,
        "semantic_judge_qualified_and_hash_frozen_or_not_applicable": True,
        "seed_and_repetition_policy_frozen": True,
        "primary_outcomes_and_hard_safety_constraints_frozen": True,
        "blind_source_registered_and_unbreached_or_not_applicable": True,
        "no_adaptive_partial_feedback": True,
        "authorization_previously_consumed": False,
        "authorized": True,
        "measurement_cycle_id": "SELF_CHECK_CYCLE",
    })
    auth_ok, auth_missing = final_authorization_ready(valid_auth)
    _record(results, "complete_final_authorization_schema_can_pass", auth_ok, f"missing={auth_missing}")

    _decision(results, protocol, "exposed_pool_candidate_development_allowed", True,
              partition="EXPOSED_POOL", actor="candidate", purpose="development")
    _decision(results, protocol, "candidate_private_oracle_denied_even_on_exposed_pool", False,
              partition="EXPOSED_POOL", actor="candidate", purpose="development", private_oracle=True)
    _decision(results, protocol, "exposed_private_scoring_denied_before_outputs_fixed", False,
              partition="EXPOSED_POOL", actor="evaluator", purpose="scoring", private_oracle=True, outputs_fixed=False)
    _decision(results, protocol, "exposed_private_scoring_allowed_after_outputs_fixed", True,
              partition="EXPOSED_POOL", actor="evaluator", purpose="scoring", private_oracle=True, outputs_fixed=True)

    _decision(results, protocol, "legacy_locked_candidate_development_denied", False,
              partition="LEGACY_LOCKED_TEST", actor="candidate", purpose="development")
    _decision(results, protocol, "legacy_locked_developer_semantic_access_denied", False,
              partition="LEGACY_LOCKED_TEST", actor="developer", purpose="final_measurement")
    _decision(results, protocol, "legacy_locked_final_without_authorization_denied", False,
              partition="LEGACY_LOCKED_TEST", actor="custodian_runner", purpose="final_measurement",
              generation_frozen=True, evaluator_qualified=True, judge_gate_satisfied=True, final_authorized=False)
    _decision(results, protocol, "legacy_locked_final_with_full_prerequisites_allowed", True,
              partition="LEGACY_LOCKED_TEST", actor="custodian_runner", purpose="final_measurement",
              generation_frozen=True, evaluator_qualified=True, judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "legacy_locked_private_scoring_before_outputs_fixed_denied", False,
              partition="LEGACY_LOCKED_TEST", actor="evaluator", purpose="scoring", private_oracle=True,
              outputs_fixed=False, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "legacy_locked_private_scoring_after_outputs_fixed_allowed", True,
              partition="LEGACY_LOCKED_TEST", actor="evaluator", purpose="scoring", private_oracle=True,
              outputs_fixed=True, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True)

    _decision(results, protocol, "fresh_blind_without_registered_source_denied", False,
              partition="FRESH_BLIND", actor="custodian_runner", purpose="final_measurement",
              source_registered=False, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "fresh_blind_with_unqualified_evaluator_denied", False,
              partition="FRESH_BLIND", actor="custodian_runner", purpose="final_measurement",
              source_registered=True, generation_frozen=True, evaluator_qualified=False,
              judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "fresh_blind_with_unsatisfied_judge_gate_denied", False,
              partition="FRESH_BLIND", actor="custodian_runner", purpose="final_measurement",
              source_registered=True, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=False, final_authorized=True)
    _decision(results, protocol, "fresh_blind_breached_source_denied", False,
              partition="FRESH_BLIND", actor="custodian_runner", purpose="final_measurement",
              source_registered=True, source_breached=True, generation_frozen=True,
              evaluator_qualified=True, judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "fresh_blind_consumed_authorization_denied", False,
              partition="FRESH_BLIND", actor="custodian_runner", purpose="final_measurement",
              source_registered=True, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True, authorization_consumed=True)
    _decision(results, protocol, "fresh_blind_full_prerequisites_custodian_execution_allowed", True,
              partition="FRESH_BLIND", actor="custodian_runner", purpose="final_measurement",
              source_registered=True, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "fresh_blind_developer_access_denied_even_when_authorized", False,
              partition="FRESH_BLIND", actor="developer", purpose="final_measurement",
              source_registered=True, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "fresh_blind_candidate_private_oracle_denied", False,
              partition="FRESH_BLIND", actor="candidate", purpose="scoring", private_oracle=True,
              source_registered=True, generation_frozen=True, evaluator_qualified=True,
              judge_gate_satisfied=True, final_authorized=True)
    _decision(results, protocol, "unknown_partition_fails_closed", False,
              partition="UNKNOWN", actor="candidate", purpose="development")

    protocol_json = json.dumps(protocol, sort_keys=True).lower()
    _record(results, "frozen_protocol_contains_no_raw_expected_path_payload", "expected_path\"" not in protocol_json and "expected_paths\"" not in protocol_json,
            "protocol does not embed expected_path keys")

    passed = sum(1 for item in results if item["passed"])
    output = {
        "status": "BIG_B4_PROTOCOL_SELF_CHECK_PASS",
        "protocol_id": protocol["protocol_id"],
        "provider_inference_calls": 0,
        "private_benchmark_semantics_read": False,
        "checks_passed": passed,
        "checks_total": len(results),
        "all_passed": passed == len(results),
        "checks": results,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
