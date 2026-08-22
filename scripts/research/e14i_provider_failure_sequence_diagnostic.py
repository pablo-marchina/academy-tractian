#!/usr/bin/env python3
"""Sanitized sequence diagnostic for E14i provider failures.

Reads an existing E14i DEV capture only. Makes no provider calls, reads no
private oracle/scorer rows, and prints no raw model outputs, prompts, group IDs,
hashes, private paths, or evaluator labels.

The goal is to determine whether the small number of unknown provider failures
occur only inside calls otherwise dominated by JSON-generation validation
failures, or whether any call exhibits an independent unknown-only failure
pattern.
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
EXPECTED_CAP = 1600

ALLOW = {
    "json_generation_validation_failure",
    "unknown_provider_failure",
    "rate_limit_tpd",
    "rate_limit_tpm",
    "rate_limit_rpm",
    "rate_limit_rpd",
    "rate_limit",
    "rate_limit_long_window",
    "provider_server_failure",
    "authentication_or_authorization_failure",
    "model_or_endpoint_unavailable",
    "request_too_large",
    "invalid_request_failure",
    "network_or_transient_failure",
    "unclassified_provider_failure",
}


def _safe_category(value: Any) -> str:
    text = str(value or "")
    return text if text in ALLOW else "other_sanitized_provider_failure"


def _pattern(categories: list[str]) -> str:
    counts = Counter(categories)
    if not counts:
        return "no_recorded_provider_failure"
    return "+".join(f"{name}*{count}" for name, count in sorted(counts.items()))


def run(path: Path) -> dict[str, Any]:
    summary = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(summary, dict):
        raise AssertionError("capture must be a JSON object")

    status = str(summary.get("status") or "")
    cfg = summary.get("e14i_provider_compatibility_configuration")
    if not status.startswith(EXPECTED_STATUS_PREFIX):
        raise AssertionError("capture is not an E14i capture")
    if not isinstance(cfg, dict):
        raise AssertionError("E14i configuration missing")
    if cfg.get("model") != EXPECTED_MODEL:
        raise AssertionError("unexpected E14i model")
    if cfg.get("reasoning_effort") != EXPECTED_REASONING:
        raise AssertionError("unexpected E14i reasoning effort")
    if int(cfg.get("max_completion_tokens") or 0) != EXPECTED_CAP:
        raise AssertionError("unexpected E14i completion cap")

    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    if not isinstance(calls, list):
        calls = []

    attempt_position_counts: dict[int, Counter[str]] = {}
    call_pattern_counts: Counter[str] = Counter()
    calls_with_any_json = 0
    calls_with_any_unknown = 0
    calls_with_only_json = 0
    calls_with_mixed_json_unknown = 0
    calls_without_json = 0
    total_categories = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        completeness = call.get("e14_completeness")
        raw_categories = completeness.get("sanitized_provider_failure_categories") if isinstance(completeness, dict) else []
        categories = [_safe_category(x) for x in (raw_categories or [])]
        total_categories += len(categories)
        call_pattern_counts[_pattern(categories)] += 1

        for idx, category in enumerate(categories, start=1):
            attempt_position_counts.setdefault(idx, Counter())[category] += 1

        has_json = "json_generation_validation_failure" in categories
        has_unknown = "unknown_provider_failure" in categories
        if has_json:
            calls_with_any_json += 1
        else:
            calls_without_json += 1
        if has_unknown:
            calls_with_any_unknown += 1
        if categories and all(x == "json_generation_validation_failure" for x in categories):
            calls_with_only_json += 1
        if has_json and has_unknown:
            calls_with_mixed_json_unknown += 1

    unknown_isolated_from_json = calls_with_any_unknown > 0 and calls_with_mixed_json_unknown < calls_with_any_unknown
    dominant_json_validation_pattern = bool(
        len(calls) == 6
        and calls_with_any_json == 6
        and calls_without_json == 0
        and not unknown_isolated_from_json
    )

    return {
        "status": "E14I_SANITIZED_PROVIDER_FAILURE_SEQUENCE_DIAGNOSTIC",
        "capture_status": status,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING,
        "max_completion_tokens": EXPECTED_CAP,
        "total_calls": len(calls),
        "provider_failure_attempts_total": total_categories,
        "attempt_position_category_counts": {
            str(idx): dict(sorted(counter.items()))
            for idx, counter in sorted(attempt_position_counts.items())
        },
        "per_call_failure_pattern_counts": dict(sorted(call_pattern_counts.items())),
        "calls_with_any_json_generation_validation_failure": calls_with_any_json,
        "calls_with_any_unknown_provider_failure": calls_with_any_unknown,
        "calls_with_only_json_generation_validation_failures": calls_with_only_json,
        "calls_with_mixed_json_and_unknown_failures": calls_with_mixed_json_unknown,
        "calls_without_json_generation_validation_failure": calls_without_json,
        "unknown_failure_isolated_from_json_validation": unknown_isolated_from_json,
        "dominant_json_validation_failure_pattern": dominant_json_validation_pattern,
        "interpretation": (
            "json_validation_dominates_every_failed_call_unknowns_are_not_independent"
            if dominant_json_validation_pattern
            else "mixed_failure_mechanism_not_yet_isolated"
        ),
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
