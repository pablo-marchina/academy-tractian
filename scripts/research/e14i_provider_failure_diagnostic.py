#!/usr/bin/env python3
"""Sanitized fixed-capture diagnostic for E14i operational failure.

Reads an existing E14i DEV capture only. Makes no provider calls, reads no
private oracle/scorer data, and does not modify the capture. Reports aggregate
completeness/provider failure metadata only; never prints model outputs, prompts,
group IDs, hashes, private paths, or evaluator labels.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_STATUS_PREFIX = "E14I_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_HIDDEN_FORMAT_CAPTURE_"
EXPECTED_MODEL = "openai/gpt-oss-120b"
EXPECTED_REASONING = "high"
EXPECTED_REASONING_FORMAT = "hidden"
EXPECTED_CAP = 1600


def _hist(values: list[int]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(values).items())}


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    return None


def run(path: Path) -> dict[str, Any]:
    summary = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise AssertionError("capture must be a JSON object")

    status = str(summary.get("status") or "")
    cfg = summary.get("e14i_provider_compatibility_configuration")
    if not status.startswith(EXPECTED_STATUS_PREFIX):
        raise AssertionError("capture is not an E14i capture")
    if not isinstance(cfg, dict):
        raise AssertionError("E14i provider configuration missing")
    if cfg.get("model") != EXPECTED_MODEL:
        raise AssertionError("unexpected model")
    if cfg.get("reasoning_effort") != EXPECTED_REASONING:
        raise AssertionError("unexpected reasoning effort")
    if cfg.get("reasoning_format") != EXPECTED_REASONING_FORMAT:
        raise AssertionError("unexpected reasoning format")
    if int(cfg.get("max_completion_tokens") or 0) != EXPECTED_CAP:
        raise AssertionError("unexpected completion cap")

    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    if not isinstance(calls, list):
        calls = []

    errors: Counter[str] = Counter()
    failures: Counter[str] = Counter()
    provider: Counter[str] = Counter()
    attempts: list[int] = []
    retries: list[int] = []
    parsed = 0
    schema_valid = 0
    calls_with_provider_failure = 0
    usage_calls = 0

    allowed_provider = {
        "rate_limit_tpd", "rate_limit_tpm", "rate_limit_rpm", "rate_limit_rpd",
        "rate_limit", "rate_limit_long_window", "provider_server_failure",
        "authentication_or_authorization_failure", "model_or_endpoint_unavailable",
        "json_generation_validation_failure", "request_too_large",
        "invalid_request_failure", "network_or_transient_failure",
        "unknown_provider_failure", "unclassified_provider_failure",
    }

    for call in calls:
        if not isinstance(call, dict):
            continue
        if isinstance(call.get("parsed_output"), dict):
            parsed += 1
        score = call.get("score")
        if isinstance(score, dict) and score.get("schema_valid") is True:
            schema_valid += 1

        err = str(call.get("error") or "none")
        if err not in {"none", "E14_MODEL_CALL_FAILED", "E14_PARSE_COMPLETENESS_FAILED"}:
            err = "other_sanitized_error"
        errors[err] += 1

        comp = call.get("e14_completeness")
        if isinstance(comp, dict):
            a = _int(comp.get("attempt_count"))
            r = _int(comp.get("retry_count"))
            if a is not None:
                attempts.append(a)
            if r is not None:
                retries.append(r)
            for item in comp.get("sanitized_attempt_failures") or []:
                text = str(item)
                failures[text if text in {"model_call_failed", "output_parse_failed"} else "other_sanitized_failure"] += 1
            cats = comp.get("sanitized_provider_failure_categories") or []
            if cats:
                calls_with_provider_failure += 1
            for item in cats:
                text = str(item)
                provider[text if text in allowed_provider else "other_sanitized_provider_failure"] += 1

        meta = call.get("provider_meta")
        usage = meta.get("usage") if isinstance(meta, dict) else None
        if isinstance(usage, dict) and usage:
            usage_calls += 1

    provider_attempts_total = sum(provider.values())
    all_provider_json_validation = bool(
        len(calls) == 6
        and parsed == 0
        and provider_attempts_total > 0
        and provider_attempts_total == provider.get("json_generation_validation_failure", 0)
    )

    if all_provider_json_validation:
        interpretation = "all_recorded_provider_failures_are_json_generation_validation_failures"
    elif provider:
        interpretation = "mixed_or_other_provider_failure_pattern"
    elif parsed == 0:
        interpretation = "zero_parsed_without_recorded_provider_failure_category"
    else:
        interpretation = "no_complete_e14i_operational_failure_pattern"

    return {
        "status": "E14I_SANITIZED_PROVIDER_FAILURE_DIAGNOSTIC",
        "capture_status": status,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING,
        "reasoning_format_recorded": EXPECTED_REASONING_FORMAT,
        "max_completion_tokens": EXPECTED_CAP,
        "total_calls": len(calls),
        "parsed_calls": parsed,
        "schema_valid_calls": schema_valid,
        "error_counts": dict(sorted(errors.items())),
        "attempt_count_histogram": _hist(attempts),
        "retry_count_histogram": _hist(retries),
        "sanitized_attempt_failure_counts": dict(sorted(failures.items())),
        "sanitized_provider_failure_category_counts": dict(sorted(provider.items())),
        "calls_with_provider_failure_category": calls_with_provider_failure,
        "provider_failure_attempts_total": provider_attempts_total,
        "provider_usage_observed_calls": usage_calls,
        "all_recorded_provider_failures_are_json_generation_validation_failures": all_provider_json_validation,
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
