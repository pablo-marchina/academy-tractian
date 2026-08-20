#!/usr/bin/env python3
"""E14v-B public synthetic attempt after external provider-permission remediation.

Scientific candidate and transport are unchanged from E14v-A. This wrapper only
creates a distinct experiment/attempt lock after manual remediation of Groq
model permissions. Real DEV remains forbidden here.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
E14V_A_PATH = HERE / "e14v_a_synthetic_transport_contract_amendment.py"
SPEC = importlib.util.spec_from_file_location("e14v_a_for_permission_remediation", E14V_A_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14v-A")
e14va = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14va)
parent = e14va.parent

AMENDMENT = Path("research/experiments/e14v-b-provider-permission-remediation-amendment.json")
PASS_STATUS = parent.PASS_SYNTHETIC
LOCK_SUFFIX = ".attempt-lock.json"
ACTIVE_STATUS = "ACTIVE_PERMISSION_REMEDIATED_SYNTHETIC_ATTEMPT_AUTHORIZED"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_amendment(path: Path = AMENDMENT) -> dict[str, Any]:
    m = _load(path)
    if not isinstance(m, dict):
        raise AssertionError("E14v-B amendment must be an object")
    if m.get("experiment_id") != "E14v-B-public-synthetic-provider-permission-remediation-amendment":
        raise AssertionError("wrong E14v-B amendment")
    if m.get("status") != ACTIVE_STATUS:
        raise AssertionError("E14v-B is not in the active authorized synthetic-attempt state")
    if m.get("amendment_class") != "external_provider_permission_remediation_only":
        raise AssertionError("E14v-B amendment class changed")

    unchanged = m.get("unchanged_scientific_candidate")
    if not isinstance(unchanged, dict):
        raise AssertionError("E14v-B unchanged-candidate contract missing")
    checks = {
        "planner_model": parent.MODEL,
        "reasoning_effort": parent.REASONING_EFFORT,
        "temperature": parent.TEMPERATURE,
        "max_completion_tokens": parent.MAX_COMPLETION_TOKENS,
        "synthetic_case_count": 14,
        "max_distinct_reads": parent.MAX_READS,
        "response_format": "json_schema_strict",
        "include_reasoning": False,
        "reasoning_format_sent": False,
        "transport_contract_changed_from_e14v_a": False,
    }
    for key, expected in checks.items():
        if unchanged.get(key) != expected:
            raise AssertionError(f"E14v-B changed frozen field: {key}")

    remediation = m.get("external_remediation_precondition")
    if not isinstance(remediation, dict) or remediation.get("manual_confirmation_received") is not True:
        raise AssertionError("E14v-B provider-permission remediation is not confirmed")
    if remediation.get("required_model") != parent.MODEL:
        raise AssertionError("E14v-B required model changed")

    policy = m.get("corrected_attempt_policy")
    if not isinstance(policy, dict) or policy.get("corrected_real_provider_attempts_allowed") != 1:
        raise AssertionError("E14v-B corrected attempt count changed")

    auth = m.get("authorization_boundary")
    if not isinstance(auth, dict) or auth.get("activation_condition_satisfied") is not True:
        raise AssertionError("E14v-B activation condition not satisfied")
    if auth.get("corrected_synthetic_attempt_authorized_now") is not True:
        raise AssertionError("E14v-B corrected synthetic attempt is not authorized")
    if auth.get("structural_ci_requirement_satisfied") is not True:
        raise AssertionError("E14v-B structural CI requirement is not satisfied")
    if auth.get("real_dev_authorized") is not False or auth.get("validation_authorized") is not False or auth.get("locked_test_authorized") is not False:
        raise AssertionError("E14v-B cannot authorize DEV/VALIDATION/LOCKED_TEST")
    return m


def _consume_e14v_b_attempt(out: Path, mode: str) -> Path:
    if mode != "synthetic":
        raise AssertionError("E14v-B authorizes synthetic mode only")
    lock = Path(str(out) + LOCK_SUFFIX)
    if out.exists():
        raise SystemExit("E14v-B synthetic output already exists; rerun is forbidden")
    if lock.exists():
        raise SystemExit("E14v-B attempt already consumed; rerun requires a new explicit amendment")
    parent._write(lock, {
        "report_version": "e14v-b-permission-remediated-synthetic-attempt-lock-v1",
        "experiment_id": "E14v-B-public-synthetic-provider-permission-remediation-amendment",
        "mode": "synthetic",
        "status": "E14V_B_PERMISSION_REMEDIATED_SYNTHETIC_ATTEMPT_CONSUMED",
        "model": parent.MODEL,
        "reasoning_effort": parent.REASONING_EFFORT,
        "temperature": parent.TEMPERATURE,
        "response_format": "json_schema_strict",
        "include_reasoning": False,
        "reasoning_format_sent": False,
        "provider_permission_remediation_confirmed": True,
        "rerun_allowed": False,
        "contains_raw_output": False,
        "contains_private_oracle": False,
        "contains_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    })
    return lock


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_amendment(args.amendment)
    parent.assert_preregistration(parent.PREREG)
    e14va.assert_amendment(e14va.AMENDMENT)
    if args.mode != "synthetic":
        raise AssertionError("E14v-B is synthetic-only; real DEV remains blocked")

    saved_provider = parent._provider_call
    saved_consume = parent.consume_attempt
    parent._provider_call = e14va._provider_call_amended
    parent.consume_attempt = _consume_e14v_b_attempt
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

    result["report_version"] = "e14v-b-public-synthetic-route-planner-qualification-v1"
    result["provider_permission_remediation"] = {
        "amendment_class": "external_provider_permission_remediation_only",
        "manual_permission_confirmation_received": True,
        "transport_reused_from_e14v_a_without_edits": True,
        "model_changed": False,
        "prompt_changed": False,
        "fixture_changed": False,
        "thresholds_changed": False,
        "provider_changed": False,
        "response_contract_changed": False,
        "temperature_changed": False,
        "reasoning_effort_changed": False,
        "real_dev_authorized_by_this_run": False,
    }
    parent._write(args.out, result)
    return result


def run_self_checks() -> None:
    m = assert_amendment(AMENDMENT)
    parent.run_self_checks()
    e14va.run_self_checks()
    assert e14va._schema_response_format()["type"] == "json_schema"
    assert m["synthetic_gate_unchanged"]["required_cases"] == 14
    assert m["external_remediation_precondition"]["manual_confirmation_received"] is True


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
        print(json.dumps({"status": "E14V_B_PROVIDER_PERMISSION_REMEDIATION_SELFCHECK_PASS"}, indent=2))
        return 0

    result = run(args)
    printable = {key: value for key, value in result.items() if key != "rows"}
    print(json.dumps(printable, indent=2))
    return 0 if result.get("status") == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
