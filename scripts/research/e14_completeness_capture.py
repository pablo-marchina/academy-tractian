from __future__ import annotations

import importlib.util
import json
import os
import re
import statistics
import time
from pathlib import Path
from typing import Any

E13_PATH = Path(__file__).with_name("e13_dev_only_reprocess_authorization_boundary.py")
SPEC = importlib.util.spec_from_file_location("e13_policy", E13_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e13_dev_only_reprocess_authorization_boundary.py")
e13 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e13)
e11 = e13.e11
base = e13.base
e10b = e11.e10g.e10e.e10d.e10c.e10b
capture = e10b.capture

TRANSPORT_PATH = Path(__file__).with_name("e14_groq_rate_limit_transport.py")
TRANSPORT_SPEC = importlib.util.spec_from_file_location("e14_groq_transport", TRANSPORT_PATH)
if TRANSPORT_SPEC is None or TRANSPORT_SPEC.loader is None:
    raise RuntimeError("failed to load e14_groq_rate_limit_transport.py")
transport = importlib.util.module_from_spec(TRANSPORT_SPEC)
TRANSPORT_SPEC.loader.exec_module(transport)


def _e14_rate_limit_aware_call_groq(prompt: str, timeout: int) -> tuple[str, dict[str, Any]]:
    return transport.call_groq(prompt, timeout, capture.base)


# E14-only transport override. e10b.call_model still owns the strict system prompt
# and temporarily mutates capture.base.SYSTEM_PROMPT before invoking this function.
capture.call_groq = _e14_rate_limit_aware_call_groq
DEFAULT_MAX_RETRIES = 2


def syntax_only_json_repair(raw_output: str) -> tuple[dict[str, Any] | None, str | None]:
    text = raw_output.strip().lstrip("\ufeff")
    if not text:
        return None, None
    candidates: list[tuple[str, str]] = []
    fenced = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    fenced = re.sub(r"\s*```$", "", fenced).strip()
    if fenced != text:
        candidates.append(("strip_markdown_fence", fenced))
    first, last = text.find("{"), text.rfind("}")
    if first >= 0 and last > first:
        outer = text[first : last + 1]
        if outer != text:
            candidates.append(("extract_outer_object", outer))
        no_trailing = re.sub(r",\s*([}\]])", r"\1", outer)
        if no_trailing != outer:
            candidates.append(("remove_trailing_commas", no_trailing))
    seen: set[str] = set()
    for method, candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed, method
    return None, None


def parse_with_repair(raw_output: str) -> tuple[dict[str, Any] | None, str | None]:
    parsed = base.extract_json_object(raw_output)
    if isinstance(parsed, dict):
        return parsed, None
    return syntax_only_json_repair(raw_output)


def execute_stage(*, groups: list[str], repeats: int, case_by_asset: dict[str, dict[str, Any]], timeout: int, dry_run: bool) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    latencies: list[float] = []
    delay = float(os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0"))
    max_retries = int(os.getenv("E14_MAX_RETRIES", str(DEFAULT_MAX_RETRIES)))
    if max_retries < 0:
        raise AssertionError("E14_MAX_RETRIES must be >= 0")

    for group_id in groups:
        packet = e10b.e10b_observation_packet("DEV", group_id, case_by_asset)
        packet_hash = base.stable_hash(packet)
        for repeat_index in range(repeats):
            if calls and delay > 0:
                time.sleep(delay)
            prompt = e10b.e10b_build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            parsed: dict[str, Any] | None = None
            error: str | None = None
            provider_meta: dict[str, Any] = {}
            retry_count = 0
            repair_count = 0
            repair_method: str | None = None
            failures: list[str] = []
            provider_failure_categories: list[str] = []

            for attempt in range(max_retries + 1):
                if attempt > 0:
                    retry_count += 1
                    trace_events.append("e14_retry_started")
                    if delay > 0:
                        time.sleep(delay)
                try:
                    raw_output, provider_meta = e10b.call_model(prompt, timeout, dry_run, packet, repeat_index)
                    trace_events.append("dry_run_output_generated" if dry_run else "model_called")
                    error = None
                except Exception as exc:
                    error = "E14_MODEL_CALL_FAILED"
                    failures.append("model_call_failed")
                    category = getattr(exc, "category", None)
                    if isinstance(category, str) and category:
                        provider_failure_categories.append(category)
                    else:
                        provider_failure_categories.append("unclassified_provider_failure")
                    trace_events.append("model_call_failed")
                    if attempt < max_retries:
                        continue
                    break

                parsed, repair_method = parse_with_repair(raw_output)
                if parsed is not None:
                    trace_events.append("output_repaired" if repair_method else "output_parsed")
                    if repair_method:
                        repair_count += 1
                    break
                failures.append("output_parse_failed")
                trace_events.append("output_parse_failed")
                error = "E14_PARSE_COMPLETENESS_FAILED"
                if attempt >= max_retries:
                    break

            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            score = capture.score_output(parsed, error or "")
            trace_events.append("output_scored")
            trace_complete = all(x in trace_events for x in ("prompt_built", "output_scored")) and (
                "model_called" in trace_events or "dry_run_output_generated" in trace_events
            )
            calls.append({
                "group_id": group_id,
                "split": "DEV",
                "repeat_index": repeat_index,
                "fixed_observation_packet_hash": packet_hash,
                "prompt_hash": base.stable_hash(prompt),
                "provider_meta": provider_meta,
                "latency_ms": round(elapsed, 3),
                "error": error,
                "score": score,
                "trace_events": trace_events,
                "trace_complete": trace_complete,
                "parsed_output": parsed,
                "output_hash": base.stable_hash(parsed) if parsed is not None else None,
                "e14_completeness": {
                    "attempt_count": retry_count + 1,
                    "retry_count": retry_count,
                    "repair_count": repair_count,
                    "repair_method": repair_method,
                    "sanitized_attempt_failures": failures,
                    "sanitized_provider_failure_categories": provider_failure_categories,
                    "semantic_fields_invented_by_repair": False
                }
            })

    successful = [c for c in calls if c.get("error") is None]
    parsed_calls = [c for c in calls if isinstance(c.get("parsed_output"), dict)]
    schema_valid = [bool(c.get("score", {}).get("schema_valid")) for c in calls]
    task_success = [bool(c.get("score", {}).get("task_success_proxy")) for c in calls]
    no_locked = [bool(c.get("score", {}).get("no_locked_test_claim")) for c in calls]
    trace_complete = [bool(c.get("trace_complete")) for c in calls]
    p95 = max(latencies) if len(latencies) < 20 else statistics.quantiles(latencies, n=20)[18]
    completeness_pass = len(calls) == 6 and len(parsed_calls) == 6
    passed = completeness_pass and len(successful) == 6 and all(schema_valid) and all(no_locked) and all(trace_complete)
    return {
        "stage": "DEV_E14_COMPLETENESS_CAPTURE",
        "split": "DEV",
        "groups": groups,
        "repeats_per_group": repeats,
        "total_calls": len(calls),
        "successful_calls": len(successful),
        "parsed_outputs": len(parsed_calls),
        "scoreable_calls": sum(1 for x in schema_valid if x),
        "passed": passed,
        "completeness_pass": completeness_pass,
        "task_success_proxy": round(sum(1 for x in task_success if x) / len(task_success), 4) if task_success else 0.0,
        "schema_valid_rate": round(sum(1 for x in schema_valid if x) / len(schema_valid), 4) if schema_valid else 0.0,
        "no_locked_test_claim_rate": round(sum(1 for x in no_locked if x) / len(no_locked), 4) if no_locked else 0.0,
        "trace_completeness": all(trace_complete) if trace_complete else False,
        "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
        "latency_p95_ms": round(p95, 3) if latencies else 0.0,
        "cost_usd": 0.0,
        "retry_count": sum(c["e14_completeness"]["retry_count"] for c in calls),
        "repair_count": sum(c["e14_completeness"]["repair_count"] for c in calls),
        "calls": calls
    }
