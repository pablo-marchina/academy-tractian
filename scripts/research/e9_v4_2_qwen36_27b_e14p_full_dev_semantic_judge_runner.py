#!/usr/bin/env python3
"""E14p full-DEV semantic judge runner for the frozen E9 v4.2 protocol.

Reuses the exact reliability-qualified Qwen judge, system prompt, provider
settings, output contract, and one-request-per-fixed-call transport used by the
targeted E14p measurement. The only changes are the preregistered full-DEV
packet cardinality: 10 calls, 206 claims, source counts 40/126/11/29, and a
distinct single-attempt lock. No oracle, VALIDATION, or LOCKED_TEST is read.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
PARENT_PATH = HERE / "e9_v4_2_qwen36_27b_e14p_real_dev_semantic_judge_runner.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_e14p_targeted_parent_for_full_dev", PARENT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load frozen targeted E14p semantic judge runner")
parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parent)

MODEL = parent.MODEL
API_URL = parent.API_URL
SYSTEM_PROMPT = parent.SYSTEM_PROMPT
VALID_SUPPORT = parent.VALID_SUPPORT
VALID_TYPES = parent.VALID_TYPES
EXPECTED_PACKET_VERSION = parent.EXPECTED_PACKET_VERSION
EXPECTED_TOOL_SIGNATURES = parent.EXPECTED_TOOL_SIGNATURES
INTERCALL_SLEEP_SECONDS = parent.INTERCALL_SLEEP_SECONDS
MAX_COMPLETION_TOKENS = parent.MAX_COMPLETION_TOKENS
ATTEMPT_LOCK_SUFFIX = parent.ATTEMPT_LOCK_SUFFIX

EXPECTED_CALLS = 10
EXPECTED_CLAIMS = 206
EXPECTED_SOURCE_COUNTS = {
    "action_escalation_rubric.calibration_reason": 40,
    "evidence_plan[]": 126,
    "proposed_next_step": 11,
    "risk_notes": 29,
}
RESULT_VERSION = "e9-v4.2-qwen36-27b-e14p-full-dev-semantic-judge-v1"
LOCK_VERSION = "e9-v4.2-e14p-full-dev-semantic-attempt-lock-v1"
PASS_STATUS = "E9_V4_2_QWEN_E14P_FULL_DEV_SEMANTIC_JUDGE_CAPTURE_PASS"
OPERATIONAL_FAILURE_STATUS = "E9_V4_2_QWEN_E14P_FULL_DEV_OPERATIONAL_FAILURE"
CONTRACT_FAILURE_STATUS = "E9_V4_2_QWEN_E14P_FULL_DEV_OUTPUT_CONTRACT_FAILURE"
CANDIDATE = "E14p-full-DEV-5-group-after-E14o-E14n-v1.1"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_packet(packet: Any) -> list[dict[str, Any]]:
    if not isinstance(packet, dict):
        raise AssertionError("claim packet must be a JSON object")
    if packet.get("report_version") != EXPECTED_PACKET_VERSION:
        raise AssertionError("claim packet report_version does not match frozen v4.2 packet")

    scope = packet.get("scope")
    if not isinstance(scope, dict) or scope.get("split") != "DEV":
        raise AssertionError("claim packet must be DEV-only")
    for key in (
        "private_oracle_included",
        "private_scorer_rows_included",
        "validation_material_included",
        "locked_test_material_included",
    ):
        if scope.get(key) is not False:
            raise AssertionError(f"claim packet scope must explicitly set {key}=false")

    calls = packet.get("calls")
    if not isinstance(calls, list) or len(calls) != EXPECTED_CALLS:
        raise AssertionError(f"claim packet must contain exactly {EXPECTED_CALLS} fixed DEV calls")

    total_claims = 0
    source_counts: Counter[str] = Counter()
    seen_call_indices: set[int] = set()
    for call in calls:
        if not isinstance(call, dict):
            raise AssertionError("each packet call must be an object")
        call_index = call.get("call_index")
        if not isinstance(call_index, int) or call_index in seen_call_indices:
            raise AssertionError("call_index must be a unique integer")
        seen_call_indices.add(call_index)
        if str(call.get("split") or "") != "DEV":
            raise AssertionError("every packet call must be DEV")
        if not isinstance(call.get("visible_case"), dict):
            raise AssertionError("every packet call must contain one visible_case object")

        contract = call.get("public_contract")
        if not isinstance(contract, dict):
            raise AssertionError("every packet call must contain public_contract")
        signatures = contract.get("tool_signatures")
        if not isinstance(signatures, list) or len(signatures) != EXPECTED_TOOL_SIGNATURES:
            raise AssertionError("public tool contract must contain the frozen 18 signatures")
        if set(contract.get("claim_support_labels") or []) != set(VALID_SUPPORT):
            raise AssertionError("claim support-label contract changed")
        if set(contract.get("claim_types") or []) != set(VALID_TYPES):
            raise AssertionError("claim-type contract changed")

        units = call.get("claim_units")
        if not isinstance(units, list) or not units:
            raise AssertionError("every packet call must contain claim units")
        seen_claim_indices: set[int] = set()
        for unit in units:
            if not isinstance(unit, dict):
                raise AssertionError("claim unit must be an object")
            claim_index = unit.get("claim_index")
            source_field = str(unit.get("source_field") or "")
            claim_text = unit.get("claim_text")
            if not isinstance(claim_index, int) or claim_index in seen_claim_indices:
                raise AssertionError("claim_index must be unique within each call")
            if source_field not in EXPECTED_SOURCE_COUNTS:
                raise AssertionError("unexpected semantic source field")
            if not isinstance(claim_text, str) or not claim_text.strip():
                raise AssertionError("claim_text must be a non-empty string")
            seen_claim_indices.add(claim_index)
            source_counts[source_field] += 1
            total_claims += 1

    if total_claims != EXPECTED_CLAIMS:
        raise AssertionError(f"claim packet must contain exactly {EXPECTED_CLAIMS} claims")
    if dict(source_counts) != EXPECTED_SOURCE_COUNTS:
        raise AssertionError("claim packet source-field counts do not match preregistered full-DEV shape")
    return calls


def attempt_lock_path(out: Path) -> Path:
    return out.with_name(out.name + ATTEMPT_LOCK_SUFFIX)


def consume_real_measurement_attempt(out: Path) -> Path:
    lock = attempt_lock_path(out)
    if out.exists():
        raise SystemExit("E14p full-DEV judge-result output already exists; rerun is forbidden")
    if lock.exists():
        raise SystemExit("E14p full-DEV semantic attempt already consumed; replacement requires an explicit amendment")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(json.dumps({
        "report_version": LOCK_VERSION,
        "status": "E14P_FULL_DEV_SEMANTIC_MEASUREMENT_ATTEMPT_CONSUMED",
        "judge_model": MODEL,
        "expected_provider_calls": EXPECTED_CALLS,
        "expected_claim_units": EXPECTED_CLAIMS,
        "rerun_allowed": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "raw_claim_text_stored": False,
        "visible_case_values_stored": False,
        "hashes_stored": False,
        "paths_stored": False
    }, indent=2), encoding="utf-8")
    return lock


def _failure_summary(status: str, completed_calls: int, http_status: int | None, category: str) -> dict[str, Any]:
    return {
        "report_version": RESULT_VERSION,
        "status": status,
        "candidate": CANDIDATE,
        "judge_model": MODEL,
        "expected_calls": EXPECTED_CALLS,
        "expected_claim_units": EXPECTED_CLAIMS,
        "completed_provider_calls_before_failure": completed_calls,
        "http_status": http_status,
        "failure_category": category,
        "real_measurement_attempt_consumed": True,
        "rerun_allowed": False,
        "local_judge_result_file_written": False,
        "semantic_metrics_authorized": False,
        "real_dev_packet_read": True,
        "validation_gate_authorized": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "raw_provider_response_printed": False,
        "claim_text_printed": False,
        "visible_case_values_printed": False,
        "judge_rows_printed": False,
        "identifiers_printed": False,
        "group_ids_printed": False,
        "hashes_printed": False,
        "api_key_printed": False
    }


def run(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    saved = {
        "EXPECTED_CALLS": parent.EXPECTED_CALLS,
        "EXPECTED_CLAIMS": parent.EXPECTED_CLAIMS,
        "EXPECTED_SOURCE_COUNTS": parent.EXPECTED_SOURCE_COUNTS,
        "RESULT_VERSION": parent.RESULT_VERSION,
        "LOCK_VERSION": parent.LOCK_VERSION,
        "PASS_STATUS": parent.PASS_STATUS,
        "OPERATIONAL_FAILURE_STATUS": parent.OPERATIONAL_FAILURE_STATUS,
        "CONTRACT_FAILURE_STATUS": parent.CONTRACT_FAILURE_STATUS,
        "CANDIDATE": parent.CANDIDATE,
        "validate_packet": parent.validate_packet,
        "consume_real_measurement_attempt": parent.consume_real_measurement_attempt,
        "_failure_summary": parent._failure_summary,
    }
    parent.EXPECTED_CALLS = EXPECTED_CALLS
    parent.EXPECTED_CLAIMS = EXPECTED_CLAIMS
    parent.EXPECTED_SOURCE_COUNTS = EXPECTED_SOURCE_COUNTS
    parent.RESULT_VERSION = RESULT_VERSION
    parent.LOCK_VERSION = LOCK_VERSION
    parent.PASS_STATUS = PASS_STATUS
    parent.OPERATIONAL_FAILURE_STATUS = OPERATIONAL_FAILURE_STATUS
    parent.CONTRACT_FAILURE_STATUS = CONTRACT_FAILURE_STATUS
    parent.CANDIDATE = CANDIDATE
    parent.validate_packet = validate_packet
    parent.consume_real_measurement_attempt = consume_real_measurement_attempt
    parent._failure_summary = _failure_summary
    try:
        summary, code = parent.run(args)
    finally:
        for key, value in saved.items():
            setattr(parent, key, value)

    summary["report_version"] = RESULT_VERSION
    summary["candidate"] = CANDIDATE
    summary["expected_source_field_claim_unit_counts"] = EXPECTED_SOURCE_COUNTS
    summary["full_dev_v4_1_gate_already_failed"] = True
    summary["semantic_pass_can_rescue_candidate"] = False
    summary["validation_gate_authorized"] = False
    return summary, code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--intercall-sleep-seconds", type=int, default=INTERCALL_SLEEP_SECONDS)
    args = parser.parse_args()
    if args.intercall_sleep_seconds != INTERCALL_SLEEP_SECONDS:
        raise AssertionError(f"intercall sleep is frozen at {INTERCALL_SLEEP_SECONDS} seconds")
    summary, code = run(args)
    print(json.dumps(summary, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
