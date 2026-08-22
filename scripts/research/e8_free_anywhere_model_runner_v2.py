#!/usr/bin/env python3
"""E8 free-anywhere real model candidate runner v2.

V2 wraps the original runner and fixes two post-run issues without changing the
benchmark scope:

1. `no_gold_claim` scoring now checks only model-produced string values, not JSON
   field names such as `trace_quality_self_check.no_gold_claim`.
2. Provider calls use retries/backoff for transient connection resets and free-tier
   rate limits.

It still requires explicit zero-cost opt-in and never uses LOCKED_TEST.
"""

from __future__ import annotations

import importlib.util
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MODULE_PATH = Path(__file__).with_name("e8_free_anywhere_model_runner.py")
SPEC = importlib.util.spec_from_file_location("e8_base_runner", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load base E8 runner")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)


def string_values(payload: Any) -> list[str]:
    """Return only string values produced by the model; dictionary keys are ignored."""
    values: list[str] = []
    if isinstance(payload, str):
        values.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            values.extend(string_values(item))
    elif isinstance(payload, dict):
        for value in payload.values():
            values.extend(string_values(value))
    return values


def value_text(payload: Any) -> str:
    return "\n".join(string_values(payload)).lower()


def score_output_v2(parsed: dict[str, Any] | None, raw_text: str) -> dict[str, Any]:
    if parsed is None:
        raw_lower = raw_text.lower()
        return {
            "json_valid": False,
            "schema_valid": False,
            "decision_class_valid": False,
            "evidence_plan_present": False,
            "no_locked_test_claim": "locked_test" not in raw_lower,
            "no_gold_claim": not any(term in raw_lower for term in ("evaluator gold", "expected answer", "scorer oracle", "hidden oracle")),
            "trace_self_check_ok": False,
            "task_success_proxy": False,
            "scoring_version": "v2_values_only",
        }
    missing = sorted(base.REQUIRED_OUTPUT_KEYS - set(parsed.keys()))
    decision_valid = parsed.get("decision_class") in base.DECISION_CLASSES
    evidence = parsed.get("evidence_plan")
    evidence_ok = isinstance(evidence, list) and bool(evidence) and all(isinstance(item, str) for item in evidence)
    trace = parsed.get("trace_quality_self_check")
    trace_ok = (
        isinstance(trace, dict)
        and trace.get("uses_only_visible_packet") is True
        and trace.get("no_locked_test") is True
        and trace.get("no_gold_claim") is True
    )
    text_values = value_text(parsed)
    no_locked = "locked_test" not in text_values
    no_gold = not any(term in text_values for term in ("evaluator gold", "expected answer", "scorer oracle", "hidden oracle"))
    schema_valid = (
        not missing
        and decision_valid
        and evidence_ok
        and isinstance(parsed.get("should_take_action_now"), bool)
        and isinstance(parsed.get("requires_human_escalation"), bool)
    )
    return {
        "json_valid": True,
        "schema_valid": schema_valid,
        "missing_keys": missing,
        "decision_class_valid": decision_valid,
        "evidence_plan_present": evidence_ok,
        "no_locked_test_claim": no_locked,
        "no_gold_claim": no_gold,
        "trace_self_check_ok": trace_ok,
        "task_success_proxy": bool(schema_valid and trace_ok and no_locked and no_gold),
        "scoring_version": "v2_values_only",
    }


def is_retryable_error(status_code: int | None, message: str) -> bool:
    lowered = message.lower()
    if status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
        return True
    if status_code == 403 and "1010" in lowered:
        return True
    return any(fragment in lowered for fragment in ("winerror 10054", "connection reset", "temporarily unavailable"))


def post_json_v2(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    attempts = int(os.getenv("E8_PROVIDER_MAX_ATTEMPTS", "4"))
    base_sleep = float(os.getenv("E8_PROVIDER_RETRY_BASE_SECONDS", "4"))
    data = json.dumps(payload).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": os.getenv("E8_HTTP_USER_AGENT", base.DEFAULT_USER_AGENT),
        **headers,
    }
    last_error: str | None = None
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {body[:1000]}"
            retryable = is_retryable_error(exc.code, last_error)
        except Exception as exc:  # noqa: BLE001 - benchmark captures provider failure text
            last_error = str(exc)
            retryable = is_retryable_error(None, last_error)
        if attempt >= attempts or not retryable:
            break
        sleep_seconds = base_sleep * attempt
        time.sleep(sleep_seconds)
    raise RuntimeError(last_error or "provider request failed")


def execute_stage_v2(**kwargs: Any) -> dict[str, Any]:
    """Run the base stage, then recompute metrics with the v2 scorer already patched."""
    delay = float(os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0"))
    if delay <= 0:
        return base.execute_stage(**kwargs)

    # Copy of the base loop with an inter-call delay to respect tight free-tier TPM limits.
    provider = kwargs["provider"]
    stage = kwargs["stage"]
    split_name = kwargs["split_name"]
    groups = kwargs["groups"]
    repeats = kwargs["repeats"]
    case_by_asset = kwargs["case_by_asset"]
    timeout = kwargs["timeout"]
    dry_run = kwargs["dry_run"]

    latencies: list[float] = []
    calls: list[dict[str, Any]] = []
    for group_id in groups:
        packet = base.observation_packet(split_name, group_id, case_by_asset)
        packet_hash = base.stable_hash(packet)
        for repeat_index in range(repeats):
            if calls:
                time.sleep(delay)
            prompt = base.build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            error: str | None = None
            raw_output = ""
            provider_meta: dict[str, Any] = {}
            try:
                raw_output, provider_meta = base.call_candidate(provider, prompt, timeout, dry_run, packet, repeat_index)
                trace_events.append("model_called" if not dry_run else "dry_run_output_generated")
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
                trace_events.append("model_call_failed")
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            parsed = base.extract_json_object(raw_output) if raw_output else None
            if raw_output:
                trace_events.append("output_parsed" if parsed is not None else "output_parse_failed")
            score = score_output_v2(parsed, raw_output or error or "")
            trace_events.append("output_scored")
            calls.append(
                {
                    "group_id": group_id,
                    "split": split_name,
                    "repeat_index": repeat_index,
                    "fixed_observation_packet_hash": packet_hash,
                    "prompt_hash": base.stable_hash(prompt),
                    "provider_meta": provider_meta,
                    "latency_ms": round(elapsed, 3),
                    "error": error,
                    "score": score,
                    "trace_events": trace_events,
                    "trace_complete": all(event in trace_events for event in ("prompt_built", "output_scored"))
                    and ("model_called" in trace_events or "dry_run_output_generated" in trace_events),
                    "output_hash": base.stable_hash(parsed) if parsed is not None else None,
                }
            )
    successful = [call for call in calls if call["error"] is None]
    task_success = [call["score"]["task_success_proxy"] for call in calls]
    schema_valid = [call["score"].get("schema_valid", False) for call in calls]
    no_locked = [call["score"].get("no_locked_test_claim", False) for call in calls]
    trace_complete = [call["trace_complete"] for call in calls]
    latency_p95 = max(latencies) if len(latencies) < 20 else statistics.quantiles(latencies, n=20)[18]
    passed = bool(calls) and len(successful) == len(calls) and all(schema_valid) and all(no_locked) and all(trace_complete)
    return {
        "stage": stage,
        "split": split_name,
        "groups": groups,
        "repeats_per_group": repeats,
        "total_calls": len(calls),
        "successful_calls": len(successful),
        "passed": passed,
        "task_success_proxy": round(sum(1 for item in task_success if item) / len(task_success), 4) if task_success else 0.0,
        "schema_valid_rate": round(sum(1 for item in schema_valid if item) / len(schema_valid), 4) if schema_valid else 0.0,
        "no_locked_test_claim_rate": round(sum(1 for item in no_locked if item) / len(no_locked), 4) if no_locked else 0.0,
        "trace_completeness": all(trace_complete) if trace_complete else False,
        "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
        "latency_p95_ms": round(latency_p95, 3) if latencies else 0.0,
        "cost_usd": 0.0,
        "calls": calls,
    }


base.score_output = score_output_v2
base.post_json = post_json_v2
base.execute_stage = execute_stage_v2

if __name__ == "__main__":
    raise SystemExit(base.main())
