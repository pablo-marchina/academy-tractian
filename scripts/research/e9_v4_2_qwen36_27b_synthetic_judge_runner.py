#!/usr/bin/env python3
"""Run the preregistered independent Qwen judge on the frozen PUBLIC synthetic suite only.

This runner is deliberately incapable of reading a real E14l/E14n claim packet.
It strips synthetic gold labels before the provider call, makes exactly one
batched inference request, validates the returned shape locally, and writes the
local prediction rows for the separate preregistered reliability validator.

No private task oracle, scorer rows, VALIDATION, or LOCKED_TEST are read.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MODEL = "qwen/qwen3.6-27b"
API_URL = "https://api.groq.com/openai/v1/chat/completions"
FROZEN_SUITE = Path("research/frozen/e9-v4-2-semantic-groundedness-synthetic-suite-v1.json")
EXPECTED_SUITE_VERSION = "e9-v4.2-semantic-groundedness-synthetic-v1"
EXPECTED_CASES = 24
VALID_SUPPORT = {"SUPPORTED", "CONTRADICTED", "NOT_SUPPORTED", "NOT_APPLICABLE"}
VALID_TYPES = {
    "factual_assertion",
    "conditional_or_hypothetical",
    "procedural_recommendation",
    "uncertainty_or_epistemic_statement",
    "non_world_metadata",
}

SYSTEM_PROMPT = """You are an independent semantic-groundedness judge.
Classify each supplied synthetic claim using ONLY its visible_case and optional explicit public_contract_fact.
Do not use outside domain knowledge as evidence.

Claim types:
- factual_assertion: asserts a current/past world fact.
- conditional_or_hypothetical: explicitly conditional, hypothetical, or future-contingent.
- procedural_recommendation: recommends a read/action/process rather than asserting its result occurred.
- uncertainty_or_epistemic_statement: states uncertainty, lack of knowledge, or an epistemic limitation.
- non_world_metadata: metadata about formatting/evaluation rather than the task world.

Support labels:
- SUPPORTED: visible_case or explicit public_contract_fact directly supports the factual assertion.
- CONTRADICTED: visible_case directly conflicts with the factual assertion.
- NOT_SUPPORTED: a factual assertion is neither directly supported nor directly contradicted.
- NOT_APPLICABLE: support is not the applicable judgment for conditional/hypothetical, procedural recommendation, uncertainty/epistemic, or non-world-metadata units.

Rules:
- Generic plausibility is NOT support.
- Tool availability does NOT imply a tool result was observed.
- Severity, diagnosis, permissions, causal facts, and temporal facts require visible support.
- Do not turn conditional/future wording into a current fact.
- Return JSON only. No explanations or rationales.
- Output exactly one top-level key named results.
- results must contain exactly one item per input case.
- Each item must contain exactly: case_id, claim_type, support_label.
"""


def _load_suite(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("synthetic suite must be a JSON object")
    if payload.get("suite_version") != EXPECTED_SUITE_VERSION:
        raise AssertionError("synthetic suite version does not match frozen v1")
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASES:
        raise AssertionError(f"frozen suite must contain exactly {EXPECTED_CASES} cases")
    return payload


def build_provider_cases(suite: dict[str, Any]) -> list[dict[str, Any]]:
    provider_cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in suite["cases"]:
        if not isinstance(row, dict):
            raise AssertionError("synthetic suite case must be an object")
        case_id = str(row.get("case_id") or "")
        if not case_id or case_id in seen:
            raise AssertionError("synthetic suite case_id must be non-empty and unique")
        seen.add(case_id)
        visible_case = row.get("visible_case")
        claim = row.get("claim")
        if not isinstance(visible_case, dict) or not isinstance(claim, str) or not claim.strip():
            raise AssertionError("synthetic case must contain visible_case object and claim string")
        clean: dict[str, Any] = {
            "case_id": case_id,
            "visible_case": visible_case,
            "claim": claim,
        }
        contract_fact = row.get("public_contract_fact")
        if isinstance(contract_fact, str) and contract_fact.strip():
            clean["public_contract_fact"] = contract_fact
        # expected_claim_type / expected_support_label are intentionally NOT copied.
        provider_cases.append(clean)
    return provider_cases


def build_request_payload(provider_cases: list[dict[str, Any]]) -> dict[str, Any]:
    user_payload = {
        "task": "Classify every synthetic case according to the frozen semantic-groundedness rubric.",
        "cases": provider_cases,
        "required_output_example": {
            "results": [
                {
                    "case_id": "S01",
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
        "max_completion_tokens": 2048,
        "response_format": {"type": "json_object"},
        "stream": False,
    }


def validate_judge_payload(payload: Any, expected_case_ids: list[str]) -> list[dict[str, str]]:
    if not isinstance(payload, dict) or set(payload.keys()) != {"results"}:
        raise AssertionError("judge output must contain exactly one top-level results key")
    results = payload.get("results")
    if not isinstance(results, list) or len(results) != len(expected_case_ids):
        raise AssertionError("judge output result count does not match frozen suite")

    expected_set = set(expected_case_ids)
    seen: set[str] = set()
    clean: list[dict[str, str]] = []
    for row in results:
        if not isinstance(row, dict) or set(row.keys()) != {"case_id", "claim_type", "support_label"}:
            raise AssertionError("each judge result must contain exactly case_id, claim_type, support_label")
        case_id = str(row.get("case_id") or "")
        claim_type = str(row.get("claim_type") or "")
        support_label = str(row.get("support_label") or "")
        if case_id not in expected_set or case_id in seen:
            raise AssertionError("judge result case_id is missing, duplicate, or outside frozen suite")
        if claim_type not in VALID_TYPES or support_label not in VALID_SUPPORT:
            raise AssertionError("judge result contains invalid claim_type or support_label")
        seen.add(case_id)
        clean.append({
            "case_id": case_id,
            "claim_type": claim_type,
            "support_label": support_label,
        })
    if seen != expected_set:
        raise AssertionError("judge output does not cover all frozen case IDs")
    return clean


def _operational_summary(status: str, http_status: int | None, category: str) -> dict[str, Any]:
    return {
        "report_version": "e9-v4.2-qwen36-27b-synthetic-judge-v1",
        "status": status,
        "judge_model": MODEL,
        "synthetic_cases_expected": EXPECTED_CASES,
        "provider_attempts_made": 1,
        "http_status": http_status,
        "failure_category": category,
        "reliability_metrics_authorized": False,
        "real_dev_packet_read": False,
        "real_dev_semantic_measurement_authorized": False,
        "validation_gate_authorized": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "raw_provider_response_printed": False,
        "synthetic_claims_printed": False,
        "prediction_rows_printed": False,
        "api_key_printed": False,
    }


def run(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if args.synthetic_suite.resolve() != FROZEN_SUITE.resolve():
        raise AssertionError("runner is frozen to the public v4.2 synthetic suite and cannot accept another input")
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise SystemExit("E8_CONFIRM_ZERO_COST=1 is required; paid fallback is not authorized")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is not set")

    suite = _load_suite(args.synthetic_suite)
    provider_cases = build_provider_cases(suite)
    expected_ids = [str(row["case_id"]) for row in provider_cases]
    request_payload = build_request_payload(provider_cases)

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "academy-tractian-e9-v4-2-qwen-judge/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout_seconds) as response:
            http_status = int(response.status)
            provider_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        category = "rate_limit" if int(exc.code) == 429 else ("provider_5xx" if int(exc.code) >= 500 else "provider_http_error")
        return _operational_summary("E9_V4_2_QWEN_SYNTHETIC_JUDGE_OPERATIONAL_FAILURE", int(exc.code), category), 1
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return _operational_summary("E9_V4_2_QWEN_SYNTHETIC_JUDGE_OPERATIONAL_FAILURE", None, "transport_or_provider_json_failure"), 1

    try:
        choices = provider_payload.get("choices") if isinstance(provider_payload, dict) else None
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise AssertionError("provider response must contain exactly one choice")
        message = choices[0].get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise AssertionError("provider response missing message content")
        judged_payload = json.loads(message["content"])
        clean_results = validate_judge_payload(judged_payload, expected_ids)
    except (AssertionError, json.JSONDecodeError, TypeError, KeyError):
        return _operational_summary("E9_V4_2_QWEN_SYNTHETIC_JUDGE_OUTPUT_CONTRACT_FAILURE", http_status, "invalid_or_incomplete_output_shape"), 1

    local_results = {
        "report_version": "e9-v4.2-qwen36-27b-synthetic-judge-v1",
        "judge": {
            "provider": "Groq",
            "model": MODEL,
            "temperature": 0,
            "reasoning_effort": "none",
            "response_format": "json_object",
            "provider_attempts": 1,
        },
        "results": clean_results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(local_results, indent=2), encoding="utf-8")

    summary = {
        "report_version": "e9-v4.2-qwen36-27b-synthetic-judge-v1",
        "status": "E9_V4_2_QWEN_SYNTHETIC_JUDGE_CAPTURE_PASS",
        "judge_model": MODEL,
        "synthetic_cases_expected": EXPECTED_CASES,
        "valid_prediction_rows_written": len(clean_results),
        "provider_attempts_made": 1,
        "http_status": http_status,
        "response_format": "json_object",
        "reasoning_effort": "none",
        "temperature": 0,
        "reliability_metrics_authorized": True,
        "real_dev_packet_read": False,
        "real_dev_semantic_measurement_authorized": False,
        "validation_gate_authorized": False,
        "gold_labels_sent_to_judge": False,
        "candidate_quality_metrics_sent_to_judge": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "raw_provider_response_printed": False,
        "synthetic_claims_printed": False,
        "prediction_rows_printed": False,
        "api_key_printed": False,
    }
    return summary, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-suite", type=Path, default=FROZEN_SUITE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    args = parser.parse_args()
    summary, code = run(args)
    print(json.dumps(summary, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
