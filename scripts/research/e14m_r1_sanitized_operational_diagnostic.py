#!/usr/bin/env python3
"""Sanitized operational diagnostic for the single E14m-R1 replacement capture.

Reads only an existing local R1 capture. Makes no provider calls and does not
read any private oracle or scorer output. It reports aggregate operational
telemetry only; raw model outputs, prompts, group IDs, hashes and private paths
are never printed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_STATUS_PREFIX = "E14M_R1_OPERATIONAL_REPLACEMENT_CAPTURE_"
EXPECTED_MODEL = "openai/gpt-oss-120b"
EXPECTED_REASONING = "medium"
EXPECTED_CAP = 4096

ALLOWED_PROVIDER_CATEGORIES = {
    "rate_limit_tpd",
    "rate_limit_tpm",
    "rate_limit_rpm",
    "rate_limit_rpd",
    "rate_limit",
    "rate_limit_long_window",
    "provider_server_failure",
    "authentication_or_authorization_failure",
    "model_or_endpoint_unavailable",
    "json_generation_validation_failure",
    "completion_or_length_generation_failure",
    "generation_failure_other",
    "request_too_large",
    "invalid_request_failure",
    "network_or_transient_failure",
    "unknown_provider_failure",
    "unclassified_provider_failure",
}


def _num(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    return None


def _hist(values: list[int]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(values).items())}


def _stats(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"observed_calls": 0, "min": None, "max": None, "avg": None, "histogram": {}}
    return {
        "observed_calls": len(values),
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 3),
        "histogram": _hist(values),
    }


def run(path: Path) -> dict[str, Any]:
    summary = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise AssertionError("capture must be a JSON object")

    status = str(summary.get("status") or "")
    if not status.startswith(EXPECTED_STATUS_PREFIX):
        raise AssertionError("capture is not an E14m-R1 replacement capture")

    # The R1 runner writes this metadata under the explicit operational name.
    # Keep the old short alias as a read-only fallback so diagnostics remain
    # tolerant of any local artifact produced while the helper was being built.
    replacement = summary.get("e14m_r1_operational_replacement")
    if not isinstance(replacement, dict):
        replacement = summary.get("e14m_r1_replacement")
    replacement = replacement if isinstance(replacement, dict) else {}
    amendment_id = summary.get("replacement_amendment_id") or replacement.get("amendment_id")
    capture_index = summary.get("replacement_capture_index") or replacement.get("replacement_capture_index")
    captures_allowed = summary.get("replacement_captures_allowed") or replacement.get("replacement_captures_allowed")
    if amendment_id != "E14m-R1" or int(capture_index or 0) != 1 or int(captures_allowed or 0) != 1:
        raise AssertionError("R1 replacement metadata does not match the preregistered single replacement")

    config = summary.get("e14l_reasoning_configuration")
    if not isinstance(config, dict):
        raise AssertionError("frozen E14l configuration missing from R1 capture")
    if config.get("model") != EXPECTED_MODEL or config.get("reasoning_effort") != EXPECTED_REASONING:
        raise AssertionError("unexpected R1 model/reasoning configuration")
    if int(config.get("max_completion_tokens") or 0) != EXPECTED_CAP:
        raise AssertionError("unexpected R1 completion budget")
    if config.get("response_format") != "json_schema" or config.get("strict") is not True:
        raise AssertionError("unexpected R1 response-format configuration")

    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    if not isinstance(calls, list):
        calls = []

    error_counts: Counter[str] = Counter()
    attempt_failure_counts: Counter[str] = Counter()
    provider_failure_counts: Counter[str] = Counter()
    attempt_counts: list[int] = []
    retry_counts: list[int] = []
    completion_tokens: list[int] = []
    prompt_tokens: list[int] = []
    total_tokens: list[int] = []
    reasoning_tokens: list[int] = []
    parsed_calls = 0
    schema_valid_calls = 0
    initial_model_call_failed_calls = 0
    initial_output_parse_failed_calls = 0
    calls_with_provider_failure = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        parsed = isinstance(call.get("parsed_output"), dict)
        parsed_calls += int(parsed)
        score = call.get("score")
        schema_valid_calls += int(isinstance(score, dict) and score.get("schema_valid") is True)

        error = str(call.get("error") or "none")
        if error not in {"none", "E14_MODEL_CALL_FAILED", "E14_PARSE_COMPLETENESS_FAILED"}:
            error = "other_sanitized_error"
        error_counts[error] += 1
        initial_model_call_failed_calls += int(error == "E14_MODEL_CALL_FAILED")
        initial_output_parse_failed_calls += int(error == "E14_PARSE_COMPLETENESS_FAILED")

        comp = call.get("e14_completeness")
        if isinstance(comp, dict):
            attempt = _num(comp.get("attempt_count"))
            retry = _num(comp.get("retry_count"))
            if attempt is not None:
                attempt_counts.append(attempt)
            if retry is not None:
                retry_counts.append(retry)
            for item in comp.get("sanitized_attempt_failures") or []:
                value = str(item)
                attempt_failure_counts[value if value in {"model_call_failed", "output_parse_failed"} else "other_sanitized_failure"] += 1
            categories = comp.get("sanitized_provider_failure_categories") or []
            calls_with_provider_failure += int(bool(categories))
            for item in categories:
                value = str(item)
                provider_failure_counts[value if value in ALLOWED_PROVIDER_CATEGORIES else "other_sanitized_provider_failure"] += 1

        provider_meta = call.get("provider_meta")
        provider_meta = provider_meta if isinstance(provider_meta, dict) else {}
        usage = provider_meta.get("usage")
        if isinstance(usage, dict):
            ct = _num(usage.get("completion_tokens"))
            pt = _num(usage.get("prompt_tokens"))
            tt = _num(usage.get("total_tokens"))
            if ct is not None:
                completion_tokens.append(ct)
            if pt is not None:
                prompt_tokens.append(pt)
            if tt is not None:
                total_tokens.append(tt)
            details = usage.get("completion_tokens_details")
            if isinstance(details, dict):
                rt = _num(details.get("reasoning_tokens"))
                if rt is not None:
                    reasoning_tokens.append(rt)

    missing = max(0, len(calls) - parsed_calls)
    if parsed_calls == len(calls) and schema_valid_calls == len(calls) and calls:
        interpretation = "complete_replacement_capture"
    elif initial_model_call_failed_calls > 0 and provider_failure_counts:
        interpretation = "incomplete_replacement_due_to_provider_failure_before_usable_output"
    elif initial_model_call_failed_calls > 0:
        interpretation = "incomplete_replacement_due_to_unclassified_initial_model_call_failure"
    elif initial_output_parse_failed_calls > 0:
        interpretation = "incomplete_replacement_due_to_initial_output_parse_failure"
    else:
        interpretation = "incomplete_replacement_without_specific_sanitized_classification"

    return {
        "status": "E14M_R1_SANITIZED_OPERATIONAL_DIAGNOSTIC",
        "capture_status": status,
        "replacement_amendment_id": amendment_id,
        "replacement_capture_index": 1,
        "replacement_captures_allowed": 1,
        "third_real_capture_allowed": False,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING,
        "response_format": "json_schema",
        "strict": True,
        "max_completion_tokens": EXPECTED_CAP,
        "total_calls": len(calls),
        "parsed_calls": parsed_calls,
        "schema_valid_calls": schema_valid_calls,
        "missing_final_outputs": missing,
        "error_counts": dict(sorted(error_counts.items())),
        "attempt_count_histogram": _hist(attempt_counts),
        "retry_count_histogram": _hist(retry_counts),
        "sanitized_attempt_failure_counts": dict(sorted(attempt_failure_counts.items())),
        "sanitized_provider_failure_category_counts": dict(sorted(provider_failure_counts.items())),
        "calls_with_provider_failure_category": calls_with_provider_failure,
        "initial_model_call_failed_calls": initial_model_call_failed_calls,
        "initial_output_parse_failed_calls": initial_output_parse_failed_calls,
        "completion_token_usage_on_retained_provider_meta": _stats(completion_tokens),
        "prompt_token_usage_on_retained_provider_meta": _stats(prompt_tokens),
        "total_token_usage_on_retained_provider_meta": _stats(total_tokens),
        "reasoning_token_usage_if_provider_exposed": _stats(reasoning_tokens),
        "calls_with_observed_completion_tokens_at_or_above_cap": sum(1 for x in completion_tokens if x >= EXPECTED_CAP),
        "interpretation": interpretation,
        "quality_scoring_allowed": False,
        "rerun_allowed": False,
        "diagnostic_makes_provider_call": False,
        "diagnostic_reads_private_oracle": False,
        "diagnostic_reads_private_scorer_rows": False,
        "diagnostic_writes_capture": False,
        "prints_raw_model_outputs": False,
        "prints_prompts": False,
        "prints_group_ids": False,
        "prints_hashes": False,
        "prints_private_paths": False,
        "prints_evaluator_labels": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.capture), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
