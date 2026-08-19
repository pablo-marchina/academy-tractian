#!/usr/bin/env python3
"""Run the reliability-qualified Qwen judge on the frozen-shape local DEV claim packet.

The input packet may contain raw model claim text and runner-visible case values,
so it must remain local/uncommitted. This runner reuses the EXACT frozen system
prompt and judge settings from the synthetic reliability runner, makes one
request per fixed DEV call, performs no semantic retry/fallback/prompt repair,
and writes local prediction rows only if all calls complete successfully.

No private expected paths, private scorer rows, VALIDATION, or LOCKED_TEST are read.
Console output is aggregate/operational only and never prints claim text, visible
case values, identifiers, group IDs, hashes, raw provider responses, or judge rows.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
SYNTH_PATH = HERE / "e9_v4_2_qwen36_27b_synthetic_judge_runner.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_qwen_synth", SYNTH_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load frozen synthetic judge runner")
synth = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(synth)

MODEL = synth.MODEL
API_URL = synth.API_URL
SYSTEM_PROMPT = synth.SYSTEM_PROMPT
VALID_SUPPORT = synth.VALID_SUPPORT
VALID_TYPES = synth.VALID_TYPES

EXPECTED_PACKET_VERSION = "e9-v4.2-semantic-claim-packet-v1"
EXPECTED_CALLS = 6
EXPECTED_CLAIMS = 69
EXPECTED_SOURCE_COUNTS = {
    "action_escalation_rubric.calibration_reason": 12,
    "evidence_plan[]": 39,
    "proposed_next_step": 6,
    "risk_notes": 12,
}
EXPECTED_TOOL_SIGNATURES = 18
INTERCALL_SLEEP_SECONDS = 25
MAX_COMPLETION_TOKENS = 2048


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
        tool_signatures = contract.get("tool_signatures")
        if not isinstance(tool_signatures, list) or len(tool_signatures) != EXPECTED_TOOL_SIGNATURES:
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
        raise AssertionError("claim packet source-field counts do not match the preregistered packet")
    return calls


def build_request_payload(call: dict[str, Any]) -> dict[str, Any]:
    units = call["claim_units"]
    provider_claims = [
        {"claim_index": int(unit["claim_index"]), "claim": str(unit["claim_text"])}
        for unit in units
    ]
    user_payload = {
        "task": "Classify every supplied claim according to the frozen semantic-groundedness rubric.",
        "visible_case": call["visible_case"],
        "public_contract": call["public_contract"],
        "claims": provider_claims,
        "required_output_example": {
            "results": [
                {
                    "claim_index": 0,
                    "claim_type": "factual_assertion",
                    "support_label": "SUPPORTED",
                }
            ]
        },
    }
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, separators=(",", ":"))},
        ],
        "temperature": 0,
        "reasoning_effort": "none",
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "response_format": {"type": "json_object"},
        "stream": False,
    }


def validate_judge_payload(payload: Any, expected_claim_indices: list[int]) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or set(payload.keys()) != {"results"}:
        raise AssertionError("judge output must contain exactly one top-level results key")
    rows = payload.get("results")
    if not isinstance(rows, list) or len(rows) != len(expected_claim_indices):
        raise AssertionError("judge result count does not match call claim count")

    expected_set = set(expected_claim_indices)
    seen: set[int] = set()
    clean: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or set(row.keys()) != {"claim_index", "claim_type", "support_label"}:
            raise AssertionError("each result must contain exactly claim_index, claim_type, support_label")
        claim_index = row.get("claim_index")
        claim_type = str(row.get("claim_type") or "")
        support_label = str(row.get("support_label") or "")
        if not isinstance(claim_index, int) or claim_index not in expected_set or claim_index in seen:
            raise AssertionError("judge result claim_index is missing, duplicate, or outside the call")
        if claim_type not in VALID_TYPES or support_label not in VALID_SUPPORT:
            raise AssertionError("judge result contains invalid claim_type or support_label")
        seen.add(claim_index)
        clean.append({
            "claim_index": claim_index,
            "claim_type": claim_type,
            "support_label": support_label,
        })
    if seen != expected_set:
        raise AssertionError("judge output does not cover every claim in the call")
    return clean


def _failure_summary(status: str, completed_calls: int, http_status: int | None, category: str) -> dict[str, Any]:
    return {
        "report_version": "e9-v4.2-qwen36-27b-real-dev-semantic-judge-v1",
        "status": status,
        "judge_model": MODEL,
        "expected_calls": EXPECTED_CALLS,
        "expected_claim_units": EXPECTED_CLAIMS,
        "completed_provider_calls_before_failure": completed_calls,
        "http_status": http_status,
        "failure_category": category,
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
        "api_key_printed": False,
    }


def run(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise SystemExit("E8_CONFIRM_ZERO_COST=1 is required; paid fallback is not authorized")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is not set")

    packet = _load(args.claim_packet)
    calls = validate_packet(packet)

    all_results: list[dict[str, Any]] = []
    completed_calls = 0
    provider_attempts = 0

    for position, call in enumerate(calls):
        call_index = int(call["call_index"])
        expected_claim_indices = [int(unit["claim_index"]) for unit in call["claim_units"]]
        request_payload = build_request_payload(call)
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "academy-tractian-e9-v4-2-qwen-real-dev-judge/1.0",
            },
            method="POST",
        )
        provider_attempts += 1

        try:
            with urllib.request.urlopen(request, timeout=args.timeout_seconds) as response:
                http_status = int(response.status)
                provider_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            category = "rate_limit" if int(exc.code) == 429 else ("provider_5xx" if int(exc.code) >= 500 else "provider_http_error")
            return _failure_summary("E9_V4_2_QWEN_REAL_DEV_OPERATIONAL_FAILURE", completed_calls, int(exc.code), category), 1
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            return _failure_summary("E9_V4_2_QWEN_REAL_DEV_OPERATIONAL_FAILURE", completed_calls, None, "transport_or_provider_json_failure"), 1

        try:
            choices = provider_payload.get("choices") if isinstance(provider_payload, dict) else None
            if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
                raise AssertionError("provider response must contain exactly one choice")
            message = choices[0].get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                raise AssertionError("provider response missing message content")
            judged_payload = json.loads(message["content"])
            clean_rows = validate_judge_payload(judged_payload, expected_claim_indices)
        except (AssertionError, json.JSONDecodeError, TypeError, KeyError):
            return _failure_summary("E9_V4_2_QWEN_REAL_DEV_OUTPUT_CONTRACT_FAILURE", completed_calls, http_status, "invalid_or_incomplete_output_shape"), 1

        for row in clean_rows:
            all_results.append({
                "call_index": call_index,
                "claim_index": int(row["claim_index"]),
                "claim_type": str(row["claim_type"]),
                "support_label": str(row["support_label"]),
            })
        completed_calls += 1
        if position < len(calls) - 1:
            time.sleep(args.intercall_sleep_seconds)

    if completed_calls != EXPECTED_CALLS or len(all_results) != EXPECTED_CLAIMS:
        return _failure_summary("E9_V4_2_QWEN_REAL_DEV_OUTPUT_CONTRACT_FAILURE", completed_calls, 200, "incomplete_final_coverage"), 1

    local_results = {
        "report_version": "e9-v4.2-qwen36-27b-real-dev-semantic-judge-v1",
        "judge": {
            "provider": "Groq",
            "model": MODEL,
            "temperature": 0,
            "reasoning_effort": "none",
            "response_format": "json_object",
            "system_prompt_reused_from_synthetic_runner": True,
        },
        "scope": {
            "split": "DEV",
            "private_oracle_used": False,
            "private_scorer_rows_used": False,
            "validation_feedback_used": False,
            "locked_test_used": False,
        },
        "results": all_results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(local_results, indent=2), encoding="utf-8")

    summary = {
        "report_version": "e9-v4.2-qwen36-27b-real-dev-semantic-judge-v1",
        "status": "E9_V4_2_QWEN_REAL_DEV_SEMANTIC_JUDGE_CAPTURE_PASS",
        "judge_model": MODEL,
        "fixed_calls_consumed": EXPECTED_CALLS,
        "claim_units_consumed": EXPECTED_CLAIMS,
        "valid_prediction_rows_written": len(all_results),
        "provider_attempts_made": provider_attempts,
        "completed_provider_calls": completed_calls,
        "response_format": "json_object",
        "reasoning_effort": "none",
        "temperature": 0,
        "system_prompt_reused_without_edits": SYSTEM_PROMPT == synth.SYSTEM_PROMPT,
        "semantic_metrics_authorized": True,
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
        "api_key_printed": False,
    }
    return summary, 0


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
