#!/usr/bin/env python3
"""E14v-A corrected public synthetic transport contract.

This amendment does not change the E14v planner prompt, public route catalog,
synthetic fixture, model, temperature, reasoning effort, retry policy, pacing,
or qualification thresholds. It changes only the provider response envelope
for the corrected synthetic attempt:
- include_reasoning=false for GPT-OSS;
- strict JSON Schema output with exactly one `reads` array.

The original failed E14v synthetic attempt and its lock remain untouched.
Real DEV remains forbidden in this amendment.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
import urllib.error
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
PARENT_PATH = HERE / "e14v_isolated_public_evidence_route_planner.py"
SPEC = importlib.util.spec_from_file_location("e14v_parent_for_transport_amendment", PARENT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14v parent")
parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parent)

AMENDMENT = Path("research/experiments/e14v-a-synthetic-transport-contract-amendment.json")
PASS_STATUS = parent.PASS_SYNTHETIC
FAIL_STATUS = parent.FAIL_SYNTHETIC
LOCK_SUFFIX = ".attempt-lock.json"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_amendment(path: Path = AMENDMENT) -> dict[str, Any]:
    m = _load(path)
    if not isinstance(m, dict):
        raise AssertionError("E14v-A amendment must be an object")
    if m.get("experiment_id") != "E14v-A-public-synthetic-transport-contract-amendment":
        raise AssertionError("wrong E14v-A amendment")
    if m.get("amendment_class") != "operational_transport_contract_only":
        raise AssertionError("E14v-A amendment class changed")
    unchanged = m.get("unchanged_scientific_candidate")
    if not isinstance(unchanged, dict):
        raise AssertionError("E14v-A unchanged-candidate contract missing")
    checks = {
        "planner_model": parent.MODEL,
        "reasoning_effort": parent.REASONING_EFFORT,
        "temperature": parent.TEMPERATURE,
        "max_completion_tokens": parent.MAX_COMPLETION_TOKENS,
        "synthetic_case_count": 14,
        "max_distinct_reads": parent.MAX_READS,
    }
    for key, expected in checks.items():
        if unchanged.get(key) != expected:
            raise AssertionError(f"E14v-A changed frozen field: {key}")
    transport = m.get("transport_change")
    if not isinstance(transport, dict):
        raise AssertionError("E14v-A transport change missing")
    new = transport.get("new_response_contract")
    if not isinstance(new, dict) or new.get("type") != "json_schema" or new.get("strict") is not True:
        raise AssertionError("E14v-A must use strict JSON Schema")
    if transport.get("include_reasoning") is not False:
        raise AssertionError("E14v-A requires include_reasoning=false")
    if transport.get("reasoning_format_sent") is not False:
        raise AssertionError("E14v-A must not send reasoning_format")
    policy = m.get("corrected_synthetic_attempt_policy")
    if not isinstance(policy, dict) or policy.get("corrected_real_provider_attempts_allowed") != 1:
        raise AssertionError("E14v-A corrected attempt count changed")
    return m


def _schema_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "e14v_route_plan",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "reads": {
                        "type": "array",
                        "items": {"type": "string", "enum": list(parent.READ_ORDER)},
                    }
                },
                "required": ["reads"],
                "additionalProperties": False,
            },
        },
    }


def _consume_amended_attempt(out: Path, mode: str) -> Path:
    if mode != "synthetic":
        raise AssertionError("E14v-A authorizes synthetic mode only")
    lock = Path(str(out) + LOCK_SUFFIX)
    if out.exists():
        raise SystemExit("E14v-A corrected synthetic output already exists; rerun is forbidden")
    if lock.exists():
        raise SystemExit("E14v-A corrected synthetic attempt already consumed; rerun requires a new explicit amendment")
    parent._write(lock, {
        "report_version": "e14v-a-corrected-synthetic-attempt-lock-v1",
        "experiment_id": "E14v-A-public-synthetic-transport-contract-amendment",
        "mode": "synthetic",
        "status": "E14V_A_CORRECTED_SYNTHETIC_ATTEMPT_CONSUMED",
        "model": parent.MODEL,
        "reasoning_effort": parent.REASONING_EFFORT,
        "temperature": parent.TEMPERATURE,
        "response_format": "json_schema_strict",
        "include_reasoning": False,
        "reasoning_format_sent": False,
        "rerun_allowed": False,
        "contains_raw_output": False,
        "contains_private_oracle": False,
        "contains_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    })
    return lock


def _provider_call_amended(user_payload: dict[str, Any], timeout: int) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    payload = {
        "model": parent.MODEL,
        "messages": [
            {"role": "system", "content": parent.SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, separators=(",", ":"))},
        ],
        "temperature": parent.TEMPERATURE,
        "max_completion_tokens": parent.MAX_COMPLETION_TOKENS,
        "reasoning_effort": parent.REASONING_EFFORT,
        "include_reasoning": False,
        "response_format": _schema_response_format(),
    }
    last_error: str | None = None
    last_http_status: int | None = None
    for attempt in range(parent.MAX_RETRIES + 1):
        try:
            response = parent._request_json(payload, timeout)
            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None, {
                "transport_attempts": attempt + 1,
                "model": parent.MODEL,
                "usage": response.get("usage", {}),
                "error": None,
                "http_status": 200,
                "transport_contract": "e14v-a-json-schema-strict-include-reasoning-false",
            }
        except urllib.error.HTTPError as exc:
            last_error = type(exc).__name__
            last_http_status = int(exc.code)
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            last_error = type(exc).__name__
            last_http_status = None
        if attempt >= parent.MAX_RETRIES:
            break
        time.sleep(2.0 * (attempt + 1))
    return None, {
        "transport_attempts": parent.MAX_RETRIES + 1,
        "model": parent.MODEL,
        "usage": {},
        "error": last_error,
        "http_status": last_http_status,
        "transport_contract": "e14v-a-json-schema-strict-include-reasoning-false",
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_amendment(args.amendment)
    parent.assert_preregistration(parent.PREREG)
    if args.mode != "synthetic":
        raise AssertionError("E14v-A is synthetic-only; real DEV remains blocked")

    saved_provider = parent._provider_call
    saved_consume = parent.consume_attempt
    parent._provider_call = _provider_call_amended
    parent.consume_attempt = _consume_amended_attempt
    try:
        parent_args = argparse.Namespace(
            manifest=parent.PREREG,
            synthetic_fixture=args.synthetic_fixture,
            out=args.out,
            timeout_seconds=args.timeout_seconds,
            dry_run=args.dry_run,
        )
        result = parent.run_synthetic(parent_args)
    finally:
        parent._provider_call = saved_provider
        parent.consume_attempt = saved_consume

    result["report_version"] = "e14v-a-public-synthetic-route-planner-qualification-v1"
    result["transport_amendment"] = {
        "amendment_class": "operational_transport_contract_only",
        "response_format": "json_schema_strict",
        "include_reasoning": False,
        "reasoning_format_sent": False,
        "model_changed": False,
        "prompt_changed": False,
        "fixture_changed": False,
        "thresholds_changed": False,
        "provider_changed": False,
        "temperature_changed": False,
        "reasoning_effort_changed": False,
        "real_dev_authorized_by_this_run": False,
    }
    parent._write(args.out, result)
    return result


def run_self_checks() -> None:
    m = assert_amendment(AMENDMENT)
    parent.run_self_checks()
    response = _schema_response_format()
    schema = response["json_schema"]["schema"]
    assert response["type"] == "json_schema"
    assert response["json_schema"]["strict"] is True
    assert schema["required"] == ["reads"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["reads"]["items"]["enum"] == parent.READ_ORDER
    assert m["synthetic_gate_unchanged"]["required_cases"] == 14


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("synthetic",), default="synthetic")
    parser.add_argument("--amendment", type=Path, default=AMENDMENT)
    parser.add_argument("--synthetic-fixture", type=Path, default=parent.SYNTHETIC_FIXTURE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        run_self_checks()
        print(json.dumps({"status": "E14V_A_SYNTHETIC_TRANSPORT_AMENDMENT_SELFCHECK_PASS"}, indent=2))
        return 0

    result = run(args)
    printable = {key: value for key, value in result.items() if key != "rows"}
    print(json.dumps(printable, indent=2))
    return 0 if result.get("status") == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
