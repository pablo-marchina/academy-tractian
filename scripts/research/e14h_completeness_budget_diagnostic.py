#!/usr/bin/env python3
"""Sanitized fixed-capture diagnostic for E14h completeness failure.

This diagnostic reads an existing E14h DEV capture only. It makes no provider
calls, does not read the private oracle/scorer, and does not modify the capture.
It reports only aggregate completeness/failure/token-usage metadata needed to
distinguish completion-budget exhaustion from provider or unrelated failures.

It never prints raw model outputs, prompts, group IDs, hashes, private paths,
or evaluator labels.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_STATUS_PREFIX = "E14H_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_CAPTURE_"
EXPECTED_MODEL = "openai/gpt-oss-120b"
EXPECTED_REASONING = "high"
EXPECTED_CAP = 1600


def _safe_error(value: Any) -> str:
    text = str(value or "none")
    if text in {"none", "E14_MODEL_CALL_FAILED", "E14_PARSE_COMPLETENESS_FAILED"}:
        return text
    return "other_sanitized_error"


def _numeric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    return None


def _hist(values: list[int]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(values).items())}


def run(capture_path: Path) -> dict[str, Any]:
    summary = json.loads(capture_path.read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise AssertionError("capture must be a JSON object")

    status = str(summary.get("status") or "")
    config = summary.get("e14h_reasoning_configuration")
    if not status.startswith(EXPECTED_STATUS_PREFIX):
        raise AssertionError("capture is not an E14h capture")
    if not isinstance(config, dict):
        raise AssertionError("E14h reasoning configuration missing")
    if config.get("model") != EXPECTED_MODEL:
        raise AssertionError("unexpected E14h model")
    if config.get("reasoning_effort") != EXPECTED_REASONING:
        raise AssertionError("unexpected E14h reasoning effort")
    if int(config.get("max_completion_tokens") or 0) != EXPECTED_CAP:
        raise AssertionError("unexpected E14h completion cap")

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
    parse_failed_calls = 0
    parsed_calls = 0
    schema_valid_calls = 0
    calls_with_provider_failure = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        parsed = call.get("parsed_output")
        if isinstance(parsed, dict):
            parsed_calls += 1
        score = call.get("score")
        if isinstance(score, dict) and score.get("schema_valid") is True:
            schema_valid_calls += 1

        err = _safe_error(call.get("error"))
        error_counts[err] += 1
        if err == "E14_PARSE_COMPLETENESS_FAILED":
            parse_failed_calls += 1

        completeness = call.get("e14_completeness")
        if isinstance(completeness, dict):
            attempt = _numeric(completeness.get("attempt_count"))
            retry = _numeric(completeness.get("retry_count"))
            if attempt is not None:
                attempt_counts.append(attempt)
            if retry is not None:
                retry_counts.append(retry)
            for item in completeness.get("sanitized_attempt_failures") or []:
                text = str(item)
                if text in {"model_call_failed", "output_parse_failed"}:
                    attempt_failure_counts[text] += 1
                else:
                    attempt_failure_counts["other_sanitized_failure"] += 1
            categories = completeness.get("sanitized_provider_failure_categories") or []
            if categories:
                calls_with_provider_failure += 1
            for item in categories:
                text = str(item)
                allow = {
                    "rate_limit_tpd", "rate_limit_tpm", "rate_limit_rpm", "rate_limit_rpd",
                    "rate_limit", "rate_limit_long_window", "provider_server_failure",
                    "authentication_or_authorization_failure", "model_or_endpoint_unavailable",
                    "json_generation_validation_failure", "request_too_large",
                    "invalid_request_failure", "network_or_transient_failure",
                    "unknown_provider_failure", "unclassified_provider_failure",
                }
                provider_failure_counts[text if text in allow else "other_sanitized_provider_failure"] += 1

        provider_meta = call.get("provider_meta")
        usage = provider_meta.get("usage") if isinstance(provider_meta, dict) else None
        if isinstance(usage, dict):
            ct = _numeric(usage.get("completion_tokens"))
            pt = _numeric(usage.get("prompt_tokens"))
            tt = _numeric(usage.get("total_tokens"))
            if ct is not None:
                completion_tokens.append(ct)
            if pt is not None:
                prompt_tokens.append(pt)
            if tt is not None:
                total_tokens.append(tt)
            details = usage.get("completion_tokens_details")
            if isinstance(details, dict):
                rt = _numeric(details.get("reasoning_tokens"))
                if rt is not None:
                    reasoning_tokens.append(rt)

    observed_completion_calls = len(completion_tokens)
    calls_at_cap = sum(1 for x in completion_tokens if x >= EXPECTED_CAP)
    all_observed_hit_cap = observed_completion_calls > 0 and calls_at_cap == observed_completion_calls
    no_provider_failures = calls_with_provider_failure == 0 and not provider_failure_counts
    all_calls_parse_failed = len(calls) > 0 and parse_failed_calls == len(calls) and parsed_calls == 0

    budget_exhaustion_supported = bool(
        len(calls) == 6
        and all_calls_parse_failed
        and no_provider_failures
        and observed_completion_calls == 6
        and all_observed_hit_cap
    )

    if budget_exhaustion_supported:
        interpretation = "completion_budget_exhaustion_supported"
    elif provider_failure_counts or calls_with_provider_failure:
        interpretation = "provider_failure_present_budget_exhaustion_not_isolated"
    elif parsed_calls == 0 and parse_failed_calls > 0:
        interpretation = "parse_failure_present_budget_exhaustion_not_proven"
    else:
        interpretation = "no_e14h_completeness_failure_pattern_detected"

    def stats(values: list[int]) -> dict[str, Any]:
        if not values:
            return {"observed_calls": 0, "min": None, "max": None, "avg": None, "histogram": {}}
        return {
            "observed_calls": len(values),
            "min": min(values),
            "max": max(values),
            "avg": round(sum(values) / len(values), 3),
            "histogram": _hist(values),
        }

    return {
        "status": "E14H_SANITIZED_COMPLETENESS_BUDGET_DIAGNOSTIC",
        "capture_status": status,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING,
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
        "completion_token_usage": stats(completion_tokens),
        "prompt_token_usage": stats(prompt_tokens),
        "total_token_usage": stats(total_tokens),
        "reasoning_token_usage_if_provider_exposed": stats(reasoning_tokens),
        "calls_with_observed_completion_tokens_at_or_above_cap": calls_at_cap,
        "all_observed_completion_token_counts_hit_cap": all_observed_hit_cap,
        "completion_budget_exhaustion_supported": budget_exhaustion_supported,
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
