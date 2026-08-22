#!/usr/bin/env python3
"""Deterministic fail-closed access guard for BIG-B4 evaluation protocol.

This module is intentionally provider-free. It validates protocol/freeze/authorization
artifacts and makes explicit allow/deny decisions for benchmark partitions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROTOCOL_PATH = Path("research/frozen/big-b4-evaluation-protocol-v1.json")
REGISTRY_PATH = Path("research/frozen/big-b4-blind-source-registry-v1.json")
FREEZE_TEMPLATE_PATH = Path("research/frozen/big-b4-candidate-freeze-template-v1.json")
AUTH_TEMPLATE_PATH = Path("research/frozen/big-b4-final-access-authorization-template-v1.json")


class ProtocolError(RuntimeError):
    """Raised when a frozen protocol artifact is invalid or inconsistent."""


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ProtocolError(f"{path} must contain a JSON object")
    return payload


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProtocolError(message)


def validate_protocol(root: Path = Path(".")) -> dict[str, Any]:
    protocol = load_json(root / PROTOCOL_PATH)
    _require(protocol.get("schema_version") == "big-b4-evaluation-protocol-v1", "unexpected protocol schema")
    _require(protocol.get("status") == "FROZEN", "protocol is not frozen")
    _require(protocol.get("protocol_id") == "P12_FRESH_BLIND_HYBRID_EXTERNAL_FIRST", "unexpected protocol id")
    _require((protocol.get("access_policy") or {}).get("default") == "DENY", "access policy must default deny")

    pins = protocol.get("source_pins") or {}
    for path_key, sha_key in (
        ("benchmark_split_path", "benchmark_split_git_blob_sha"),
        ("big_b3_selection_path", "big_b3_selection_git_blob_sha"),
        ("big_b2_preregistration_path", "big_b2_preregistration_git_blob_sha"),
    ):
        source = root / str(pins.get(path_key, ""))
        expected = str(pins.get(sha_key, ""))
        _require(source.is_file(), f"pinned source missing: {source}")
        _require(git_blob_sha(source) == expected, f"pinned source hash mismatch: {source}")

    benchmark = load_json(root / str(pins["benchmark_split_path"]))
    splits = benchmark.get("splits") or {}
    dev_ids = {str(g["group_id"]) for g in (splits.get("DEV") or {}).get("groups", [])}
    validation_ids = {str(g["group_id"]) for g in (splits.get("VALIDATION") or {}).get("groups", [])}
    locked_ids = {str(g["group_id"]) for g in (splits.get("LOCKED_TEST") or {}).get("groups", [])}

    partitions = protocol.get("partitions") or {}
    exposed_ids = set((partitions.get("EXPOSED_POOL") or {}).get("group_ids", []))
    protocol_locked_ids = set((partitions.get("LEGACY_LOCKED_TEST") or {}).get("group_ids", []))
    _require(exposed_ids == dev_ids | validation_ids, "EXPOSED_POOL must equal historical DEV + VALIDATION")
    _require(protocol_locked_ids == locked_ids, "LEGACY_LOCKED_TEST must equal historical LOCKED_TEST")
    _require(not exposed_ids & protocol_locked_ids, "exposed and legacy locked groups overlap")
    _require(len(exposed_ids) == 7, "EXPOSED_POOL must contain seven independent groups")
    _require(len(protocol_locked_ids) == 3, "LEGACY_LOCKED_TEST must contain three independent groups")

    _require((partitions.get("FRESH_BLIND") or {}).get("group_ids_in_repository") == [], "fresh blind semantics must not be committed in protocol")
    _require((protocol.get("final_authorization") or {}).get("default_authorized") is False, "final authorization must default false")
    _require((protocol.get("candidate_generation_freeze") or {}).get("required_before_any_blind_or_legacy_final_measurement") is True, "candidate freeze must be mandatory")
    _require((protocol.get("repeated_run_protocol") or {}).get("stochastic_candidate_minimum_repetitions_per_scenario") == 3, "stochastic repeat minimum must remain three")
    _require((protocol.get("regression_policy") or {}).get("provider_free_protocol_self_check_required_in_ci") is True, "provider-free self-check must be required")
    return protocol


def validate_blind_registry(root: Path = Path(".")) -> dict[str, Any]:
    registry = load_json(root / REGISTRY_PATH)
    _require(registry.get("schema_version") == "big-b4-blind-source-registry-v1", "unexpected blind registry schema")
    _require(registry.get("default_fail_closed") is True, "blind registry must fail closed")
    state = registry.get("authorization_state")
    sources = registry.get("authorized_sources") or []
    if state == "NO_BLIND_SOURCE_AUTHORIZED":
        _require(sources == [], "no-source authorization state must have empty authorized_sources")
    return registry


def validate_candidate_freeze(freeze: dict[str, Any]) -> tuple[bool, list[str]]:
    required = [
        "generation_id",
        "candidate_code_hash",
        "candidate_config_hash",
        "prompt_hash",
        "model_provider_runtime_identity",
        "stochastic_candidate",
        "retrieval_policy_hash",
        "guard_policy_hash",
        "evaluator_version_hash",
        "semantic_judge_manifest_hash_or_not_applicable",
        "seed_policy",
        "primary_outcomes",
        "hard_safety_constraints",
        "repetitions_per_scenario",
        "uncertainty_method",
        "frozen_at",
    ]
    missing = [key for key in required if freeze.get(key) in (None, "", [], {})]
    if freeze.get("status") != "FROZEN_GENERATION":
        missing.append("status=FROZEN_GENERATION")
    if freeze.get("ready_for_final_authorization") is not True:
        missing.append("ready_for_final_authorization=true")
    reps = freeze.get("repetitions_per_scenario")
    if isinstance(reps, int) and reps < 1:
        missing.append("repetitions_per_scenario>=1")
    if freeze.get("stochastic_candidate") is True and (not isinstance(reps, int) or reps < 3):
        missing.append("stochastic_repetitions_per_scenario>=3")
    return (not missing, missing)


def final_authorization_ready(
    authorization: dict[str, Any],
    *,
    source_breached: bool = False,
) -> tuple[bool, list[str]]:
    required_true = [
        "candidate_generation_frozen",
        "evaluator_qualified_and_hash_frozen",
        "semantic_judge_qualified_and_hash_frozen_or_not_applicable",
        "seed_and_repetition_policy_frozen",
        "primary_outcomes_and_hard_safety_constraints_frozen",
        "blind_source_registered_and_unbreached_or_not_applicable",
        "no_adaptive_partial_feedback",
    ]
    failures = [key for key in required_true if authorization.get(key) is not True]
    if authorization.get("authorized") is not True:
        failures.append("authorized=true")
    if authorization.get("authorization_previously_consumed") is True:
        failures.append("authorization_not_previously_consumed")
    if source_breached:
        failures.append("source_unbreached")
    for key in ("authorization_id", "generation_id", "partition", "candidate_freeze_hash", "measurement_cycle_id"):
        if authorization.get(key) in (None, ""):
            failures.append(key)
    if authorization.get("partition") not in ("FRESH_BLIND", "LEGACY_LOCKED_TEST"):
        failures.append("partition_is_final_partition")
    return (not failures, failures)


def access_decision(
    protocol: dict[str, Any],
    *,
    partition: str,
    actor: str,
    purpose: str,
    private_oracle: bool = False,
    outputs_fixed: bool = False,
    generation_frozen: bool = False,
    evaluator_qualified: bool = False,
    judge_gate_satisfied: bool = False,
    final_authorized: bool = False,
    source_registered: bool = False,
    source_breached: bool = False,
    authorization_consumed: bool = False,
) -> tuple[bool, str]:
    """Return an explicit allow/deny decision. Any unknown state is denied."""

    known_partitions = set((protocol.get("partitions") or {}).keys())
    if partition not in known_partitions:
        return False, "DENY_UNKNOWN_PARTITION"

    if private_oracle and actor == "candidate":
        return False, "DENY_CANDIDATE_PRIVATE_ORACLE"

    if partition == "EXPOSED_POOL":
        if private_oracle:
            if actor == "evaluator" and purpose == "scoring" and outputs_fixed:
                return True, "ALLOW_EXPOSED_POOL_EVALUATOR_SCORING_AFTER_OUTPUTS_FIXED"
            return False, "DENY_EXPOSED_POOL_PRIVATE_ORACLE_OUTSIDE_FIXED_OUTPUT_SCORING"
        if actor in {"candidate", "developer"} and purpose in {"development", "selection", "ablation", "failure_analysis", "regression"}:
            return True, "ALLOW_EXPOSED_POOL_ADAPTIVE_USE"
        if actor == "evaluator" and purpose in {"development", "qualification", "scoring", "regression"}:
            return True, "ALLOW_EXPOSED_POOL_EVALUATOR_USE"
        return False, "DENY_EXPOSED_POOL_UNDECLARED_USE"

    if partition == "SYNTHETIC_ADVERSARIAL":
        if actor in {"candidate", "developer", "evaluator", "judge"} and purpose in {"development", "qualification", "robustness", "regression"}:
            return True, "ALLOW_SYNTHETIC_SUPPLEMENTARY_USE"
        return False, "DENY_SYNTHETIC_UNDECLARED_USE"

    if partition == "LEGACY_LOCKED_TEST":
        if actor == "developer":
            return False, "DENY_DEVELOPER_LEGACY_LOCKED_SEMANTIC_ACCESS"
        if purpose in {"development", "selection", "ablation", "failure_analysis"}:
            return False, "DENY_LEGACY_LOCKED_ADAPTIVE_USE"
        prerequisites = generation_frozen and evaluator_qualified and judge_gate_satisfied and final_authorized and not authorization_consumed
        if not prerequisites:
            return False, "DENY_LEGACY_LOCKED_FINAL_PREREQUISITES_INCOMPLETE"
        if actor == "custodian_runner" and purpose == "final_measurement" and not private_oracle:
            return True, "ALLOW_LEGACY_LOCKED_ONE_SHOT_CANDIDATE_EXECUTION"
        if actor == "evaluator" and purpose == "scoring" and private_oracle and outputs_fixed:
            return True, "ALLOW_LEGACY_LOCKED_PRIVATE_SCORING_AFTER_FIXED_OUTPUTS"
        return False, "DENY_LEGACY_LOCKED_UNDECLARED_FINAL_USE"

    if partition == "FRESH_BLIND":
        if actor == "developer":
            return False, "DENY_DEVELOPER_FRESH_BLIND_SEMANTIC_ACCESS"
        if source_breached:
            return False, "DENY_FRESH_BLIND_BREACHED_SOURCE"
        prerequisites = (
            source_registered
            and generation_frozen
            and evaluator_qualified
            and judge_gate_satisfied
            and final_authorized
            and not authorization_consumed
        )
        if not prerequisites:
            return False, "DENY_FRESH_BLIND_FINAL_PREREQUISITES_INCOMPLETE"
        if actor == "custodian_runner" and purpose == "final_measurement" and not private_oracle:
            return True, "ALLOW_FRESH_BLIND_CUSTODIAN_EXECUTION"
        if actor == "evaluator" and purpose == "scoring" and private_oracle and outputs_fixed:
            return True, "ALLOW_FRESH_BLIND_PRIVATE_SCORING_AFTER_FIXED_OUTPUTS"
        return False, "DENY_FRESH_BLIND_UNDECLARED_FINAL_USE"

    return False, "DENY_DEFAULT"


def main() -> int:
    protocol = validate_protocol()
    registry = validate_blind_registry()
    print(json.dumps({
        "status": "BIG_B4_PROTOCOL_GUARD_VALID",
        "protocol_id": protocol["protocol_id"],
        "blind_authorization_state": registry["authorization_state"],
        "default_access": "DENY",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
