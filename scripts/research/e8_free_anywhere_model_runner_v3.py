#!/usr/bin/env python3
"""E8 free-anywhere real model candidate runner v3.

V3 extends the v2 Groq/Gemini runner with an OpenRouter zero-cost comparator.
It preserves the v2 scoring and retry behavior, keeps Groq as the leading
free-provider candidate, and allows OpenRouter only when the selected model is
explicitly zero-cost: either `openrouter/free` or a specific `:free` model.

It still requires explicit zero-cost opt-in and never uses LOCKED_TEST.
"""

from __future__ import annotations

import importlib.util
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any

MODULE_PATH = Path(__file__).with_name("e8_free_anywhere_model_runner_v2.py")
SPEC = importlib.util.spec_from_file_location("e8_v2_runner", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E8 v2 runner")
v2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v2)
base = v2.base

OPENROUTER_PROVIDER = "openrouter"
DEFAULT_OPENROUTER_MODEL = "openrouter/free"
BLOCKED_OPENROUTER_MODELS = {"openrouter/auto", "openrouter/auto:free", "auto", "auto:free"}

base.ALLOWED_PROVIDERS.add(OPENROUTER_PROVIDER)


def selected_openrouter_model() -> str:
    return os.getenv("E8_OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL).strip()


def assert_openrouter_zero_cost_model(model: str) -> None:
    if model in BLOCKED_OPENROUTER_MODELS:
        raise AssertionError(
            "OpenRouter auto routing is blocked for E8 zero-cost benchmarking; use openrouter/free or a specific :free model"
        )
    if model == "openrouter/free" or model.endswith(":free"):
        return
    raise AssertionError("OpenRouter E8 model must be openrouter/free or a specific model id ending in :free")


def assert_zero_cost_guard_v3(provider: str, dry_run: bool) -> None:
    enabled_paid = sorted(name for name in base.PAID_PROVIDER_ENVS if os.getenv(name))
    if enabled_paid:
        raise AssertionError(f"Paid provider envs must stay disabled for E8: {enabled_paid}")
    if dry_run:
        return
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("Remote candidate execution requires E8_CONFIRM_ZERO_COST=1")
    if provider == OPENROUTER_PROVIDER:
        if os.getenv("E8_ENABLE_OPENROUTER_FREE") != "1" or not os.getenv("OPENROUTER_API_KEY"):
            raise AssertionError("OpenRouter free run requires OPENROUTER_API_KEY and E8_ENABLE_OPENROUTER_FREE=1")
        assert_openrouter_zero_cost_model(selected_openrouter_model())
        return
    v2.base.assert_zero_cost_guard(provider, dry_run)


def call_openrouter(prompt: str, timeout: int) -> tuple[str, dict[str, Any]]:
    model = selected_openrouter_model()
    assert_openrouter_zero_cost_model(model)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": base.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(os.getenv("E8_MODEL_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("E8_MAX_OUTPUT_TOKENS", "700")),
        "response_format": {"type": "json_object"},
    }
    response = base.post_json(
        "https://openrouter.ai/api/v1/chat/completions",
        {
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "HTTP-Referer": os.getenv("E8_OPENROUTER_SITE_URL", "https://github.com/pablo-marchina/academy-tractian"),
            "X-Title": os.getenv("E8_OPENROUTER_APP_TITLE", "academy-tractian-e8-free-comparator"),
        },
        payload,
        timeout,
    )
    content = response["choices"][0]["message"]["content"]
    return content, {"model": model, "usage": response.get("usage", {}), "raw_id": response.get("id")}


def call_candidate_v3(
    provider: str,
    prompt: str,
    timeout: int,
    dry_run: bool,
    packet: dict[str, Any],
    repeat_index: int,
) -> tuple[str, dict[str, Any]]:
    if dry_run:
        return base.dry_run_model_output(packet, repeat_index)
    if provider == OPENROUTER_PROVIDER:
        return call_openrouter(prompt, timeout)
    return v2.base.call_candidate(provider, prompt, timeout, dry_run, packet, repeat_index)


def execute_stage_v3(**kwargs: Any) -> dict[str, Any]:
    provider = kwargs["provider"]
    stage = kwargs["stage"]
    split_name = kwargs["split_name"]
    groups = kwargs["groups"]
    repeats = kwargs["repeats"]
    case_by_asset = kwargs["case_by_asset"]
    timeout = kwargs["timeout"]
    dry_run = kwargs["dry_run"]
    delay = float(os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0"))

    latencies: list[float] = []
    calls: list[dict[str, Any]] = []
    for group_id in groups:
        packet = base.observation_packet(split_name, group_id, case_by_asset)
        packet_hash = base.stable_hash(packet)
        for repeat_index in range(repeats):
            if calls and delay > 0:
                time.sleep(delay)
            prompt = base.build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            error: str | None = None
            raw_output = ""
            provider_meta: dict[str, Any] = {}
            try:
                raw_output, provider_meta = call_candidate_v3(provider, prompt, timeout, dry_run, packet, repeat_index)
                trace_events.append("model_called" if not dry_run else "dry_run_output_generated")
            except Exception as exc:  # noqa: BLE001 - benchmark captures provider failure text
                error = str(exc)
                trace_events.append("model_call_failed")
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            parsed = base.extract_json_object(raw_output) if raw_output else None
            if raw_output:
                trace_events.append("output_parsed" if parsed is not None else "output_parse_failed")
            score = v2.score_output_v2(parsed, raw_output or error or "")
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


base.assert_zero_cost_guard = assert_zero_cost_guard_v3
base.call_candidate = call_candidate_v3
base.execute_stage = execute_stage_v3

if __name__ == "__main__":
    raise SystemExit(base.main())
