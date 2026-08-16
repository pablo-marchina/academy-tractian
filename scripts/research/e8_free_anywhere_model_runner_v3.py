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
BLOCKED_OPENROUTER_MODELS = {"openrouter/auto", "openrouter/auto:free"}

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


base.assert_zero_cost_guard = assert_zero_cost_guard_v3
base.call_candidate = call_candidate_v3

if __name__ == "__main__":
    raise SystemExit(base.main())
