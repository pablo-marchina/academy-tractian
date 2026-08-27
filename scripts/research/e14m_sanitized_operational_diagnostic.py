#!/usr/bin/env python3
"""Sanitized operational diagnostic for an existing E14m capture.

Reads only the fixed E14m capture. Makes no provider calls and never reads
private oracle/scorer material. It reports aggregate operational telemetry only;
raw outputs, prompts, group IDs, hashes, paths, evaluator labels, and per-row
private information are never printed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_STATUS_PREFIX = "E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION_CAPTURE_"
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
        raise AssertionError("capture is not an E14m capture")

    config = summary.get("e14l_reasoning_configuration")
    if not isinstance(config, dict):
        raise AssertionError("frozen E14l configuration missing from E14m capture")
    if config.get("model") != EXPECTED_MODEL:
        raise AssertionError("unexpected E14m model")
    if config.get("reasoning_effort") != EXPECTED_REASONING:
        raise AssertionError("unexpected E14m reasoning effort")
    if int(config.get("max_completion_tokens") or 0) != EXPECTED_CAP:
        raise AssertionError("unexpected E14m completion budget")
    if config.get("response_format") != "json_schema" or config.get("strict") is not True:
        raise AssertionError("unexpected E14m response-format configuration")

    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    if not isinstance(calls, list):
        calls = []

    adjudication = summary.get("e14m_public_decision_adjudication")
    adjudication = adjudication if isinstance(adjudication, dict) else {}

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
    calls_with_e14m_provider_meta = 0
    failed_calls_without_e14m_provider_meta = 0
    initial_model_call_failed_calls = 0
    initial_output_parse_failed_calls = 0

    for call in calls:
        if not isinstance(call, dict):
            continue

        parsed = isinstance(call.get("parsed_output"), dict)
        if parsed:
            parsed_calls += 1
        score = call.get("score")
        if isinstance(score, dict) and score.get("schema_valid") is True:
            schema_valid_calls += 1

        error = str(call.get("error") or "none")
        if error not in {"none", "E14_MODEL_CALL_FAILED", "E14_PARSE_COMPLETENESS_FAILED"}:
            error = "other_sanitized_error"
        error_counts[error] += 1
        if error == "E14_MODEL_CALL_FAILED":
            initial_model_call_failed_calls += 1
        elif error == "E14_PARSE_COMPLETENESS_FAILED":
            initial_output_parse_failed_calls += 1

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
        provider_meta = provider_meta if isinstance(provider_meta, dict) else {}
        e14m_meta = provider_meta.get("e14m_public_decision_adjudication")
        if isinstance(e14m_meta, dict):
            calls_with_e14m_provider_meta += 1
        elif not parsed:
            failed_calls_without_e14m_provider_meta += 1

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

    triggered = int(adjudication.get("triggered_calls") or 0)
    additional = int(adjudication.get("additional_adjudication_calls") or 0)
    adjudication_parseable = int(adjudication.get("parseable_adjudication_responses") or 0)
    preserved = int(adjudication.get("preserved_initial_drafts") or 0)
    initial_drafts_observed = int(adjudication.get("initial_drafts_observed") or 0)

    # By E14m construction, a failed/unparseable adjudication preserves an
    # already-parseable initial draft. Therefore a missing final parsed output
    # cannot be caused solely by the optional adjudication call.
    adjudication_failure_can_explain_missing_final_output = False
    missing_final_outputs = max(0, len(calls) - parsed_calls)

    if parsed_calls == 6 and schema_valid_calls == 6:
        interpretation = "complete_capture_no_operational_failure"
    elif initial_model_call_failed_calls > 0:
        if provider_failure_counts:
            interpretation = "incomplete_due_to_initial_provider_call_failure_before_adjudication"
        else:
            interpretation = "initial_provider_call_failure_without_classified_provider_category"
    elif initial_output_parse_failed_calls > 0:
        interpretation = "incomplete_due_to_initial_output_parse_failure_before_adjudication"
    elif missing_final_outputs > 0:
        interpretation = "incomplete_before_usable_initial_draft_without_specific_sanitized_classification"
    else:
        interpretation = "no_operational_failure_pattern_detected"

    return {
        "status": "E14M_SANITIZED_OPERATIONAL_DIAGNOSTIC",
        "capture_status": status,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING,
        "response_format": config.get("response_format"),
        "strict": config.get("strict"),
        "max_completion_tokens": EXPECTED_CAP,
        "total_calls": len(calls),
        "parsed_calls": parsed_calls,
        "schema_valid_calls": schema_valid_calls,
        "missing_final_outputs": missing_final_outputs,
        "error_counts": dict(sorted(error_counts.items())),
        "attempt_count_histogram": _hist(attempt_counts),
        "retry_count_histogram": _hist(retry_counts),
        "sanitized_attempt_failure_counts": dict(sorted(attempt_failure_counts.items())),
        "sanitized_provider_failure_category_counts": dict(sorted(provider_failure_counts.items())),
        "calls_with_provider_failure_category": calls_with_provider_failure,
        "initial_model_call_failed_calls": initial_model_call_failed_calls,
        "initial_output_parse_failed_calls": initial_output_parse_failed_calls,
        "calls_with_e14m_provider_meta": calls_with_e14m_provider_meta,
        "failed_calls_without_e14m_provider_meta": failed_calls_without_e14m_provider_meta,
        "initial_drafts_observed": initial_drafts_observed,
        "adjudication_triggered_calls": triggered,
        "additional_adjudication_calls": additional,
        "parseable_adjudication_responses": adjudication_parseable,
        "preserved_initial_drafts": preserved,
        "adjudication_failure_can_explain_missing_final_output": adjudication_failure_can_explain_missing_final_output,
        "completion_token_usage_on_retained_provider_meta": _stats(completion_tokens),
        "prompt_token_usage_on_retained_provider_meta": _stats(prompt_tokens),
        "total_token_usage_on_retained_provider_meta": _stats(total_tokens),
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
