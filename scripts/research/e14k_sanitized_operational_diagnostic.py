#!/usr/bin/env python3
"""Sanitized operational diagnostic for an existing E14k capture.

No provider calls. No private oracle/scorer access. No raw model outputs, prompts,
group IDs, hashes, private paths or evaluator labels are printed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_STATUS_PREFIX = "E14K_DEV_ONLY_HIGH_REASONING_4096_COMPLETION_BUDGET_CAPTURE_"
EXPECTED_MODEL = "openai/gpt-oss-120b"
EXPECTED_REASONING = "high"
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
    config = summary.get("e14k_completion_budget_configuration")
    if not status.startswith(EXPECTED_STATUS_PREFIX):
        raise AssertionError("capture is not an E14k capture")
    if not isinstance(config, dict):
        raise AssertionError("E14k configuration missing")
    if config.get("model") != EXPECTED_MODEL:
        raise AssertionError("unexpected E14k model")
    if config.get("reasoning_effort") != EXPECTED_REASONING:
        raise AssertionError("unexpected E14k reasoning effort")
    if int(config.get("max_completion_tokens") or 0) != EXPECTED_CAP:
        raise AssertionError("unexpected E14k completion budget")

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
    calls_with_provider_failure = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        if isinstance(call.get("parsed_output"), dict):
            parsed_calls += 1
        score = call.get("score")
        if isinstance(score, dict) and score.get("schema_valid") is True:
            schema_valid_calls += 1

        error = str(call.get("error") or "none")
        if error not in {"none", "E14_MODEL_CALL_FAILED", "E14_PARSE_COMPLETENESS_FAILED"}:
            error = "other_sanitized_error"
        error_counts[error] += 1

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
                attempt_failure_counts[
                    value if value in {"model_call_failed", "output_parse_failed"} else "other_sanitized_failure"
                ] += 1

            categories = comp.get("sanitized_provider_failure_categories") or []
            if categories:
                calls_with_provider_failure += 1
            for item in categories:
                value = str(item)
                provider_failure_counts[
                    value if value in ALLOWED_PROVIDER_CATEGORIES else "other_sanitized_provider_failure"
                ] += 1

        provider_meta = call.get("provider_meta")
        usage = provider_meta.get("usage") if isinstance(provider_meta, dict) else None
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

    if parsed_calls == 6 and schema_valid_calls == 6:
        interpretation = "complete_capture_no_operational_failure"
    elif provider_failure_counts.get("completion_or_length_generation_failure", 0) > 0:
        interpretation = "explicit_completion_or_length_signal_present"
    elif provider_failure_counts.get("rate_limit_tpm", 0) > 0 or provider_failure_counts.get("rate_limit", 0) > 0:
        interpretation = "rate_limit_signal_present"
    elif provider_failure_counts.get("json_generation_validation_failure", 0) > 0:
        interpretation = "explicit_json_or_schema_signal_present"
    elif provider_failure_counts.get("generation_failure_other", 0) > 0:
        interpretation = "generic_failed_generation_signal_present"
    elif provider_failure_counts:
        interpretation = "other_provider_failure_signal_present"
    elif parsed_calls < 6:
        interpretation = "incomplete_without_classified_provider_failure"
    else:
        interpretation = "no_operational_failure_pattern_detected"

    return {
        "status": "E14K_SANITIZED_OPERATIONAL_DIAGNOSTIC",
        "capture_status": status,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING,
        "response_format": config.get("response_format"),
        "strict": config.get("strict"),
        "max_completion_tokens": EXPECTED_CAP,
        "total_calls": len(calls),
        "parsed_calls": parsed_calls,
        "schema_valid_calls": schema_valid_calls,
        "error_counts": dict(sorted(error_counts.items())),
        "attempt_count_histogram": _hist(attempt_counts),
        "retry_count_histogram": _hist(retry_counts),
        "sanitized_attempt_failure_counts": dict(sorted(attempt_failure_counts.items())),
        "sanitized_provider_failure_category_counts": dict(sorted(provider_failure_counts.items())),
        "calls_with_provider_failure_category": calls_with_provider_failure,
        "completion_token_usage": _stats(completion_tokens),
        "prompt_token_usage": _stats(prompt_tokens),
        "total_token_usage": _stats(total_tokens),
        "reasoning_token_usage_if_provider_exposed": _stats(reasoning_tokens),
        "calls_with_observed_completion_tokens_at_or_above_cap": sum(1 for x in completion_tokens if x >= EXPECTED_CAP),
        "interpretation": interpretation,
        "diagnostic_changes_candidate": False,
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
