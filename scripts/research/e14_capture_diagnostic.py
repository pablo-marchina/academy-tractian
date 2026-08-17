#!/usr/bin/env python3
"""Print only aggregate, non-private diagnostics from an E14 capture.

This helper never prints parsed outputs, raw provider errors, prompts, hashes,
asset-level rows, oracle data, or private file contents. It is intended to
classify completeness failures before deciding whether a real DEV-only rerun is
methodologically justified.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

SAFE_PROVIDER_CATEGORIES = {
    "rate_limit",
    "provider_server_failure",
    "authentication_or_authorization_failure",
    "model_or_endpoint_unavailable",
    "non_retryable_request_failure",
    "network_or_transient_failure",
    "unknown_provider_failure",
    "unclassified_provider_failure",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    payload = load_json(args.capture)
    stage = payload.get("dev_action_escalation_calibration") if isinstance(payload, dict) else None
    calls = stage.get("calls", []) if isinstance(stage, dict) else []

    attempt_failures: Counter[str] = Counter()
    provider_categories: Counter[str] = Counter()
    calls_with_model_failure = 0
    calls_with_parse_failure = 0
    calls_with_parsed_output = 0
    calls_with_final_error = 0
    retry_count = 0
    repair_count = 0
    models: set[str] = set()

    for call in calls:
        if not isinstance(call, dict):
            continue
        comp = call.get("e14_completeness") or {}
        failures = comp.get("sanitized_attempt_failures") or []
        if isinstance(failures, list):
            safe_failures = [str(x) for x in failures if x in {"model_call_failed", "output_parse_failed"}]
            attempt_failures.update(safe_failures)
            if "model_call_failed" in safe_failures:
                calls_with_model_failure += 1
            if "output_parse_failed" in safe_failures:
                calls_with_parse_failure += 1
        categories = comp.get("sanitized_provider_failure_categories") or []
        if isinstance(categories, list):
            provider_categories.update(
                str(x) if str(x) in SAFE_PROVIDER_CATEGORIES else "unclassified_provider_failure"
                for x in categories
            )
        retry_count += int(comp.get("retry_count") or 0)
        repair_count += int(comp.get("repair_count") or 0)
        if isinstance(call.get("parsed_output"), dict):
            calls_with_parsed_output += 1
        if call.get("error") is not None:
            calls_with_final_error += 1
        provider_meta = call.get("provider_meta") or {}
        model = provider_meta.get("model") if isinstance(provider_meta, dict) else None
        if isinstance(model, str) and model:
            models.add(model)

    result = {
        "status": "E14_SANITIZED_CAPTURE_DIAGNOSTIC",
        "total_calls": len(calls),
        "parsed_calls": calls_with_parsed_output,
        "calls_with_final_error": calls_with_final_error,
        "retry_count": retry_count,
        "repair_count": repair_count,
        "attempt_failure_counts": {
            "model_call_failed": attempt_failures.get("model_call_failed", 0),
            "output_parse_failed": attempt_failures.get("output_parse_failed", 0),
        },
        "provider_failure_category_counts": dict(sorted(provider_categories.items())),
        "calls_with_any_model_call_failure": calls_with_model_failure,
        "calls_with_any_parse_failure": calls_with_parse_failure,
        "provider_models_observed_on_successful_calls": sorted(models),
        "prints_private_outputs": False,
        "prints_raw_provider_errors": False,
        "prints_oracle_data": False,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
