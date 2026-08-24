#!/usr/bin/env python3
"""Provider-free qualification for the P12-C4 Cerebras serving contract.

The check is intentionally incapable of contacting a provider. It reads only the
public serving-contract manifest and the pure request builder, then materializes
synthetic requests to verify that the frozen semantics are represented exactly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import p12_c4_cerebras_request_contract as contract


DEFAULT_MANIFEST = Path("research/experiments/p12-c4-provider-serving-contract-v1.json")
BUILDER_SOURCE = Path("scripts/research/p12_c4_cerebras_request_contract.py")


class CheckFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def validate_static_isolation() -> dict[str, bool]:
    source = BUILDER_SOURCE.read_text(encoding="utf-8")
    forbidden_fragments = [
        "CEREBRAS_API_KEY", "GROQ_API_KEY", "import requests", "from requests",
        "import httpx", "from httpx", "import urllib", "from urllib",
        "import socket", "from socket", "api.cerebras.ai", "api.groq.com",
    ]
    hits = [fragment for fragment in forbidden_fragments if fragment in source]
    require(not hits, f"pure request builder contains forbidden provider-I/O fragments: {hits}")
    return {
        "builder_has_no_credential_reference": True,
        "builder_has_no_http_client_reference": True,
        "builder_has_no_provider_endpoint_reference": True,
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, bool]:
    require(manifest.get("schema_version") == "p12-c4-provider-serving-contract-v1", "schema version mismatch")
    require(manifest.get("status") == "PROVIDER_CONTRACT_FROZEN_LIVE_NOT_AUTHORIZED", "contract status must remain live-blocked")
    require(manifest.get("decision_source") == "docs/adr/001-provider-capacity-serving-path-2026-08-24.md", "ADR binding mismatch")

    predecessor = manifest["predecessor_reuse_policy"]
    require(all(predecessor.get(key) is False for key in [
        "rerun_consumed_experiments", "reuse_partial_parent_outputs", "reuse_partial_scores", "reuse_live_seeds",
    ]), "consumed predecessor reuse must remain forbidden")

    provider = manifest["provider"]
    require(provider.get("name") == contract.PROVIDER, "provider mismatch")
    require(provider.get("tier") == "free_trial", "Cerebras tier must be recorded as Free Trial, not permanent free")
    require(provider.get("model_id") == contract.MODEL_ID, "model id mismatch")
    require(provider.get("underlying_model_family") == contract.UNDERLYING_MODEL_FAMILY, "underlying model family mismatch")
    require(provider.get("automatic_failover") is False and provider.get("fallback_provider") is None, "silent provider fallback must remain forbidden")
    require(provider.get("serving_path_change_is_explicit_confound") is True, "serving-path confound must stay explicit")
    require(provider.get("permanently_free_tier") is False, "Cerebras must not be represented as permanently free")
    require(provider.get("free_trial_requires_verified_payment_method") is True, "Free Trial payment-method prerequisite must remain explicit")
    require(provider.get("free_trial_credit_usd") == 5, "Free Trial credit boundary mismatch")
    require(provider.get("free_trial_credit_expiry_days") == 30, "Free Trial expiry boundary mismatch")
    require(provider.get("zero_cash_spend_is_conditional_on_active_trial_credit") is True, "zero-cash-spend claim must remain conditional")

    request = manifest["frozen_request_contract"]
    require(request.get("temperature") == contract.TEMPERATURE, "temperature mismatch")
    require(request.get("reasoning_effort") == contract.REASONING_EFFORT, "reasoning effort mismatch")
    require(request.get("reasoning_format") == contract.REASONING_FORMAT, "reasoning format mismatch")
    require(request.get("max_completion_tokens") == contract.MAX_COMPLETION_TOKENS, "completion budget mismatch")
    require(request.get("seed_binding") == "required_per_common_parent", "seed binding must be required")
    require(request.get("seed_determinism_guarantee") == "best_effort_only", "seed determinism must not be overstated")
    require(request["structured_output"] == {"type": "json_schema", "strict": True}, "structured-output contract mismatch")
    require(request["tool_semantics"]["support_required"] is True, "tool support must remain required")
    require(request["tool_semantics"]["tool_choice_support_required"] is True, "tool_choice support must remain required")

    packet = manifest["packet_contract"]
    require(packet.get("common_parent_generations") == 36, "expected 36 common parents")
    require(packet.get("participating_arms") == ["A00", "A10", "A01", "A11"], "factorial arm set mismatch")
    require(packet.get("fixed_arm_outputs") == 144, "expected 144 fixed arm outputs")
    require(packet.get("same_parent_for_all_four_arms") is True, "paired-parent invariant must remain enabled")
    require(packet.get("complete_packet_required_before_scoring") is True, "complete packet must precede scoring")
    require(packet.get("partial_packet_scoring_forbidden") is True, "partial scoring must remain forbidden")
    require(packet.get("arm_specific_provider_calls_forbidden") is True, "arm-specific provider calls must remain forbidden")

    isolation = manifest["isolation_contract"]
    require(isolation.get("private_oracle_accesses_during_generation") == 0, "private oracle access must remain zero")
    require(isolation.get("fresh_blind_accesses_during_generation") == 0, "fresh blind access must remain zero")
    require(isolation.get("legacy_locked_test_accesses_during_generation") == 0, "locked-test access must remain zero")
    require(isolation.get("provider_contract_self_check_must_be_provider_free") is True, "provider-free self-check invariant missing")
    require(isolation.get("provider_contract_self_check_must_not_read_credentials") is True, "credential isolation invariant missing")
    require(isolation.get("provider_contract_self_check_must_not_load_benchmark_inputs") is True, "benchmark isolation invariant missing")

    authorization = manifest["authorization"]
    require(authorization.get("provider_free_contract_checks") is True, "provider-free check must be authorized")
    require(all(authorization.get(key) is False for key in [
        "synthetic_live_provider_probe", "exposed_pool_live_generation", "private_scoring",
        "fresh_blind_measurement", "legacy_locked_test_measurement",
    ]), "all live/scoring authorization must remain false at this stage")

    capacity = manifest["published_capacity_feasibility_boundary"]
    require(capacity.get("minimum_tpm") >= 30000, "TPM feasibility boundary regressed below documented Free Trial baseline")
    require(capacity.get("minimum_tph") >= 1000000, "TPH feasibility boundary regressed")
    require(capacity.get("minimum_tpd") >= 1000000, "TPD feasibility boundary regressed")
    require(capacity.get("minimum_rpm") >= 5, "RPM feasibility boundary regressed below documented Free Trial baseline")
    expected_budget = packet["common_parent_generations"] * request["max_completion_tokens"]
    require(capacity.get("maximum_completion_token_budget") == expected_budget == 147456, "completion-token feasibility math mismatch")
    require(capacity.get("rate_limit_estimation_includes_prompt_plus_max_completion_tokens") is True, "provider token-reservation semantics must remain explicit")
    require(capacity.get("pre_live_prompt_token_estimate_required") is True, "prompt-token estimate must gate live execution")
    require(capacity.get("pacing_must_be_derived_from_verified_limits_and_measured_prompt_size") is True, "pacing cannot be hard-coded without request-size evidence")
    require(capacity.get("account_level_limits_verified") is False, "account limits cannot be marked verified without separate evidence")
    require(capacity.get("account_level_verification_required_before_any_live_probe") is True, "account-level verification must gate live probe")

    return {
        "manifest_bound_to_accepted_adr": True,
        "consumed_runs_reuse_forbidden": True,
        "serving_provider_frozen": True,
        "free_trial_semantics_explicit": True,
        "silent_failover_forbidden": True,
        "request_semantics_frozen": True,
        "seed_determinism_not_overstated": True,
        "complete_packet_invariant_frozen": True,
        "benchmark_isolation_frozen": True,
        "all_live_authorizations_blocked": True,
        "capacity_boundary_consistent": True,
        "prompt_plus_completion_reservation_accounted_for": True,
        "account_limit_verification_still_required": True,
    }


def validate_synthetic_requests() -> tuple[dict[str, bool], dict[str, str]]:
    messages = [
        {"role": "system", "content": "Synthetic P12-C4 provider contract check. No benchmark data."},
        {"role": "user", "content": "Return the contract marker only in the requested structure."},
    ]
    schema = {
        "type": "object",
        "properties": {"contract_marker": {"type": "string"}, "ok": {"type": "boolean"}},
        "required": ["contract_marker", "ok"],
        "additionalProperties": False,
    }
    structured = contract.build_structured_output_request(
        messages, seed=424242, schema_name="p12_c4_provider_contract_probe", schema=schema,
    )
    require(structured["model"] == "gpt-oss-120b", "structured request model mismatch")
    require(structured["temperature"] == 0, "structured request temperature mismatch")
    require(structured["seed"] == 424242, "structured request seed mismatch")
    require(structured["max_completion_tokens"] == 4096, "structured request completion budget mismatch")
    require(structured["reasoning_effort"] == "medium", "structured request reasoning effort mismatch")
    require(structured["reasoning_format"] == "hidden", "structured request reasoning format mismatch")
    require(structured["stream"] is False, "structured request streaming must be disabled")
    require(structured["response_format"]["type"] == "json_schema", "structured response type mismatch")
    require(structured["response_format"]["json_schema"]["strict"] is True, "strict structured output must be enabled")
    require(structured["response_format"]["json_schema"]["schema"]["additionalProperties"] is False, "strict schema must forbid additional properties")

    tools = [{
        "type": "function",
        "function": {
            "name": "synthetic_lookup",
            "description": "Returns a synthetic marker; never accesses external or benchmark data.",
            "parameters": {
                "type": "object",
                "properties": {"marker": {"type": "string"}},
                "required": ["marker"],
                "additionalProperties": False,
            },
        },
    }]
    tool_request = contract.build_tool_request(messages, seed=424243, tools=tools, tool_choice="required")
    require(tool_request["model"] == "gpt-oss-120b", "tool request model mismatch")
    require(tool_request["seed"] == 424243, "tool request seed mismatch")
    require(tool_request["tool_choice"] == "required", "tool_choice mismatch")
    require(tool_request["parallel_tool_calls"] is False, "parallel tool calls must be disabled for qualification")
    require(tool_request["tools"][0]["type"] == "function", "function-tool contract mismatch")

    snapshot = contract.contract_snapshot()
    require(snapshot["network_io_implemented"] is False, "request module unexpectedly implements network I/O")
    require(snapshot["credential_access_implemented"] is False, "request module unexpectedly implements credential access")

    return (
        {
            "structured_output_request_contract": True,
            "seed_binding_materialized": True,
            "reasoning_contract_materialized": True,
            "completion_budget_materialized": True,
            "tool_request_contract": True,
            "parallel_tool_calls_disabled_in_probe": True,
            "network_io_implemented": False,
            "credential_access_implemented": False,
        },
        {
            "structured_request_sha256": contract.canonical_request_sha256(structured),
            "tool_request_sha256": contract.canonical_request_sha256(tool_request),
        },
    )


def run(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    assertions: dict[str, bool] = {}
    assertions.update(validate_static_isolation())
    assertions.update(validate_manifest(manifest))
    synthetic_assertions, hashes = validate_synthetic_requests()
    assertions.update(synthetic_assertions)
    require(all(assertions.values()), "one or more provider-contract assertions failed")
    return {
        "schema_version": "p12-c4-provider-contract-self-check-v1",
        "status": "PASS",
        "provider": contract.PROVIDER,
        "model_id": contract.MODEL_ID,
        "provider_calls": 0,
        "credentials_read": 0,
        "benchmark_inputs_loaded": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "live_generation_authorized": False,
        "synthetic_live_probe_authorized": False,
        "assertions": assertions,
        "request_hashes": hashes,
        "next_gate": "VERIFY_ACCOUNT_LIMITS_AND_PREREGISTER_SYNTHETIC_LIVE_COMPATIBILITY_PROBE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run(args.manifest)
    except (CheckFailure, contract.ContractError, KeyError, json.JSONDecodeError) as exc:
        result = {
            "schema_version": "p12-c4-provider-contract-self-check-v1",
            "status": "FAIL",
            "provider_calls": 0,
            "credentials_read": 0,
            "benchmark_inputs_loaded": 0,
            "error": str(exc),
        }
        text = json.dumps(result, indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 1
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
