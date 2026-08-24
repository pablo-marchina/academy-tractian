#!/usr/bin/env python3
"""Fail-closed P12-C4 Cerebras synthetic compatibility probe.

Live mode is impossible unless a separate first-party effective-capacity
attestation and a separate one-shot live-probe authorization artifact both PASS.
Provider-free contract-check mode performs no SDK import, credential read, sleep,
or network I/O.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research" / "experiments" / "p12-c4-cerebras-synthetic-compatibility-probe-preregistration-v1.json"
SERVING = ROOT / "research" / "experiments" / "p12-c4-provider-serving-contract-v1.json"
PACING = ROOT / "research" / "frozen" / "p12-c4-prompt-budget-and-pacing-v1.json"
DEFAULT_ATTESTATION = ROOT / "research" / "experiments" / "p12-c4-cerebras-account-capacity-attestation-v2.json"
DEFAULT_AUTHORIZATION = ROOT / "research" / "frozen" / "p12-c4-cerebras-synthetic-probe-live-authorization-v1.json"
SDK_PACKAGE = "cerebras_cloud_sdk"
SDK_VERSION = "1.91.0"
EXPECTED_PROBE_ID = "P12-C4-CEREBRAS-SYNTHETIC-COMPATIBILITY-V1"
ATTESTATION_SCHEMA = "p12-c4-cerebras-account-capacity-attestation-v2"


class ProbeBlocked(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProbeBlocked(f"{path} must contain an object")
    return value


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_frozen_contracts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    prereg = load_json(PREREG)
    serving = load_json(SERVING)
    pacing = load_json(PACING)
    if prereg.get("probe_id") != EXPECTED_PROBE_ID:
        raise ProbeBlocked("probe preregistration id changed")
    if prereg.get("status") != "PREREGISTERED_BLOCKED_PENDING_ACCOUNT_LIMIT_VERIFICATION":
        raise ProbeBlocked("unexpected preregistration state")
    if serving.get("status") != "PROVIDER_CONTRACT_FROZEN_LIVE_NOT_AUTHORIZED":
        raise ProbeBlocked("serving contract state changed")
    transport = serving.get("transport_contract", {})
    if transport.get("sdk_package") != SDK_PACKAGE or transport.get("sdk_version") != SDK_VERSION:
        raise ProbeBlocked("SDK contract changed")
    if transport.get("client_warm_tcp_connection") is not False or transport.get("client_max_retries") != 0:
        raise ProbeBlocked("implicit SDK network behavior is not disabled")
    frozen_pacing = pacing.get("frozen_pacing", {})
    if pacing.get("status") != "FROZEN_PROVIDER_FREE_CONDITIONAL_ON_ACCOUNT_ATTESTATION":
        raise ProbeBlocked("prompt/pacing contract is not frozen")
    if frozen_pacing.get("minimum_seconds_between_any_provider_requests") != 75:
        raise ProbeBlocked("frozen pacing changed")
    if frozen_pacing.get("implicit_sdk_retries") != 0 or frozen_pacing.get("implicit_sdk_warming_requests") != 0:
        raise ProbeBlocked("pacing contract permits implicit calls")
    calls = prereg.get("frozen_probe_calls")
    if not isinstance(calls, list) or len(calls) != 2:
        raise ProbeBlocked("probe must contain exactly two calls")
    if [c.get("ordinal") for c in calls] != [1, 2]:
        raise ProbeBlocked("probe call order changed")
    if calls[0].get("probe") != "strict_structured_output" or calls[1].get("probe") != "forced_function_tool_call":
        raise ProbeBlocked("probe call identities changed")
    if calls[0]["request_contract"].get("seed") != 424242 or calls[1]["request_contract"].get("seed") != 424243:
        raise ProbeBlocked("synthetic seeds changed")
    if calls[1]["request_contract"].get("parallel_tool_calls") is not False:
        raise ProbeBlocked("parallel tool calls must remain disabled")
    return prereg, serving, pacing


def validate_account_attestation(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ProbeBlocked("actual Cerebras account attestation v2 is absent")
    x = load_json(path)
    if x.get("schema_version") != ATTESTATION_SCHEMA or x.get("status") != "PASS":
        raise ProbeBlocked("effective account/project capacity attestation has not PASSed")
    if x.get("provider") != "cerebras" or x.get("model_id") != "gpt-oss-120b":
        raise ProbeBlocked("account attestation provider/model mismatch")

    src = x.get("evidence_source", {})
    if src.get("first_party") is not True or src.get("contains_secret") is not False:
        raise ProbeBlocked("account attestation must be first-party and secret-free")
    if src.get("org_limits_observed") is not True or src.get("project_limits_observed_or_inherited") is not True:
        raise ProbeBlocked("organization/project limit context was not fully observed")

    access = x.get("account_access", {})
    if access.get("api_access_active") is not True:
        raise ProbeBlocked("Cerebras API access is not attested active")

    quota = x.get("quota_context", {})
    if quota.get("org_and_project_both_enforced") is not True:
        raise ProbeBlocked("organization/project quota enforcement not attested")
    if quota.get("api_key_scope") not in {"organization", "project"}:
        raise ProbeBlocked("API key scope is not attested")
    if quota.get("api_key_scope") == "project" and quota.get("project_quota_applies") is not True:
        raise ProbeBlocked("project-scoped API key requires project quota attestation")

    limits = x.get("effective_limits", {})
    if int(limits.get("rpm", -1)) < 5:
        raise ProbeBlocked("effective RPM below frozen boundary")
    if int(limits.get("uncached_tpm", -1)) < 30000:
        raise ProbeBlocked("effective uncached TPM below frozen boundary")
    if int(limits.get("total_tpm", -1)) < 30000:
        raise ProbeBlocked("effective total TPM below frozen boundary")

    if access.get("tier") == "free_trial":
        if int(limits.get("tph") or -1) < 1000000 or int(limits.get("tpd") or -1) < 1000000:
            raise ProbeBlocked("Free Trial TPH/TPD below frozen boundary")
        if access.get("trial_credit_active") is not True:
            raise ProbeBlocked("Free Trial credit is not attested active")

    att = x.get("attestation", {})
    required_flags = [
        "minimum_rpm_met",
        "minimum_uncached_tpm_met",
        "minimum_total_tpm_met",
        "hourly_daily_capacity_met_or_not_applicable",
        "active_access_met",
        "effective_project_and_org_context_checked",
        "secrets_excluded",
    ]
    if not all(att.get(key) is True for key in required_flags):
        raise ProbeBlocked("account attestation flags are incomplete")
    return x


def validate_live_authorization(path: Path, attestation: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        raise ProbeBlocked("synthetic live-probe authorization artifact is absent")
    x = load_json(path)
    if x.get("schema_version") != "p12-c4-cerebras-synthetic-probe-live-authorization-v1":
        raise ProbeBlocked("live authorization schema mismatch")
    if x.get("status") != "AUTHORIZED_ONE_SYNTHETIC_PROBE_ATTEMPT":
        raise ProbeBlocked("synthetic live probe is not authorized")
    if x.get("probe_id") != EXPECTED_PROBE_ID:
        raise ProbeBlocked("live authorization probe id mismatch")
    if x.get("authorized_attempts") != 1 or x.get("rerun_allowed") is not False:
        raise ProbeBlocked("live probe authorization must be one-shot")
    if x.get("exposed_pool_live_generation_authorized") is not False:
        raise ProbeBlocked("probe authorization must not authorize EXPOSED_POOL")
    if x.get("attestation_sha256") != canonical_sha256(attestation):
        raise ProbeBlocked("live authorization is not bound to the exact account attestation")
    return x


def sanitized_headers(headers: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in dict(headers).items():
        k = str(key).lower()
        if k in {"x-request-id", "request-id", "retry-after"} or k.startswith("x-ratelimit-"):
            out[k] = str(value)
    return out


def validate_structured_response(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ProbeBlocked("structured probe expected exactly one choice")
    choice = choices[0]
    if choice.get("finish_reason") != "stop":
        raise ProbeBlocked("structured probe finish_reason mismatch")
    message = choice.get("message") or {}
    content = message.get("content")
    if not isinstance(content, str):
        raise ProbeBlocked("structured probe response content missing")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ProbeBlocked("structured probe response is not valid JSON") from exc
    if parsed != {"contract_marker": "P12-C4-SYNTHETIC", "ok": True}:
        raise ProbeBlocked("structured probe marker/schema result mismatch")
    return parsed


def validate_tool_response(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ProbeBlocked("tool probe expected exactly one choice")
    choice = choices[0]
    if choice.get("finish_reason") != "tool_calls":
        raise ProbeBlocked("tool probe finish_reason mismatch")
    message = choice.get("message") or {}
    calls = message.get("tool_calls")
    if not isinstance(calls, list) or len(calls) != 1:
        raise ProbeBlocked("tool probe expected exactly one tool call")
    call = calls[0]
    if call.get("type") != "function":
        raise ProbeBlocked("tool probe type mismatch")
    fn = call.get("function") or {}
    if fn.get("name") != "synthetic_lookup":
        raise ProbeBlocked("tool probe function name mismatch")
    args = fn.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError as exc:
            raise ProbeBlocked("tool arguments are not valid JSON") from exc
    if not isinstance(args, dict) or args.get("marker") != "P12-C4-TOOL":
        raise ProbeBlocked("tool marker mismatch")
    return args


def provider_free_contract_check() -> dict[str, Any]:
    prereg, serving, pacing = validate_frozen_contracts()
    calls = prereg["frozen_probe_calls"]
    return {
        "schema_version": "p12-c4-cerebras-synthetic-probe-runner-self-check-v2",
        "status": "PASS_PROVIDER_FREE_LIVE_STILL_BLOCKED",
        "provider_calls": 0,
        "credentials_read": 0,
        "benchmark_inputs_loaded": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "exact_frozen_probe_calls": 2,
        "request_sha256": [canonical_sha256(c["request_contract"]) for c in calls],
        "sdk_contract": serving["transport_contract"],
        "attestation_schema_version": ATTESTATION_SCHEMA,
        "minimum_seconds_between_any_provider_requests": pacing["frozen_pacing"]["minimum_seconds_between_any_provider_requests"],
        "account_attestation_present": DEFAULT_ATTESTATION.exists(),
        "live_authorization_present": DEFAULT_AUTHORIZATION.exists(),
        "live_probe_authorized": False,
        "next_gate": "REAL_EFFECTIVE_CAPACITY_ATTESTATION_PASS_THEN_SEPARATE_ONE_SHOT_LIVE_PROBE_AUTHORIZATION",
    }


def execute_live(attestation_path: Path, authorization_path: Path, output: Path) -> dict[str, Any]:
    prereg, serving, pacing = validate_frozen_contracts()
    attestation = validate_account_attestation(attestation_path)
    authorization = validate_live_authorization(authorization_path, attestation)

    key = os.environ.get("CEREBRAS_API_KEY")
    if not key:
        raise ProbeBlocked("CEREBRAS_API_KEY is absent")
    installed = importlib.metadata.version(SDK_PACKAGE)
    if installed != SDK_VERSION:
        raise ProbeBlocked(f"SDK version mismatch: {installed}")
    from cerebras.cloud.sdk import Cerebras

    client = Cerebras(api_key=key, warm_tcp_connection=False, max_retries=0)
    calls = prereg["frozen_probe_calls"]
    evidence_calls: list[dict[str, Any]] = []
    previous_finished: float | None = None
    for index, call in enumerate(calls):
        if previous_finished is not None:
            elapsed = time.monotonic() - previous_finished
            remaining = float(pacing["frozen_pacing"]["minimum_seconds_between_any_provider_requests"]) - elapsed
            if remaining > 0:
                time.sleep(remaining)
        request = call["request_contract"]
        started_utc = datetime.now(timezone.utc).isoformat()
        started = time.monotonic()
        raw = client.chat.completions.with_raw_response.create(**request)
        parsed = raw.parse()
        payload = parsed.to_dict()
        elapsed_seconds = time.monotonic() - started
        previous_finished = time.monotonic()
        semantic = validate_structured_response(payload) if index == 0 else validate_tool_response(payload)
        evidence_calls.append({
            "ordinal": index + 1,
            "probe": call["probe"],
            "started_at_utc": started_utc,
            "elapsed_seconds": elapsed_seconds,
            "request": request,
            "request_sha256": canonical_sha256(request),
            "response": payload,
            "response_sha256": canonical_sha256(payload),
            "response_headers_sanitized": sanitized_headers(raw.headers),
            "semantic_validation": semantic,
            "model_identifier": payload.get("model"),
            "usage": payload.get("usage"),
        })

    evidence = {
        "schema_version": "p12-c4-cerebras-synthetic-compatibility-probe-result-v1",
        "probe_id": EXPECTED_PROBE_ID,
        "status": "PASS",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "sdk_package": SDK_PACKAGE,
        "sdk_version": installed,
        "client_warm_tcp_connection": False,
        "client_max_retries": 0,
        "provider_calls": 2,
        "benchmark_inputs_loaded": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "attestation_schema_version": ATTESTATION_SCHEMA,
        "attestation_sha256": canonical_sha256(attestation),
        "authorization_sha256": canonical_sha256(authorization),
        "calls": evidence_calls,
        "exposed_pool_live_generation_authorized_by_this_result": False,
        "next_gate": "FULL_PROVIDER_FREE_C4_ACTIVATION_AND_LIVE_MANIFEST_FREEZE",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider-free-contract-check", action="store_true")
    parser.add_argument("--attestation", type=Path, default=DEFAULT_ATTESTATION)
    parser.add_argument("--authorization", type=Path, default=DEFAULT_AUTHORIZATION)
    parser.add_argument("--output", type=Path, default=ROOT / "research" / "results" / "p12-c4-cerebras-synthetic-compatibility-probe-result.json")
    args = parser.parse_args()
    try:
        if args.provider_free_contract_check:
            result = provider_free_contract_check()
        else:
            result = execute_live(args.attestation, args.authorization, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        result = {
            "schema_version": "p12-c4-cerebras-synthetic-compatibility-probe-result-v1",
            "status": "BLOCKED_OR_FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "exposed_pool_live_generation_authorized": False,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
