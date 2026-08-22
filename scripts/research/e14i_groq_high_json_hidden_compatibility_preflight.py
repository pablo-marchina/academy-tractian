#!/usr/bin/env python3
"""One-call non-benchmark compatibility preflight for E14i.

Uses no TRACTIAN packet, oracle, scorer row, VALIDATION or LOCKED_TEST data.
It verifies Groq can return a valid JSON object under the exact E14i provider
configuration before the six-call DEV measurement is attempted.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).parent
TRANSPORT_PATH = HERE / "e14_groq_rate_limit_transport.py"
SPEC = importlib.util.spec_from_file_location("e14i_transport", TRANSPORT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e14_groq_rate_limit_transport.py")
transport = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transport)

REQUIRED_MODEL = "openai/gpt-oss-120b"
REQUIRED_REASONING_EFFORT = "high"
REQUIRED_REASONING_FORMAT = "hidden"
REQUIRED_MAX_COMPLETION_TOKENS = 1600


def assert_configuration() -> None:
    if os.getenv("E8_GROQ_MODEL") != REQUIRED_MODEL:
        raise AssertionError(f"preflight requires E8_GROQ_MODEL={REQUIRED_MODEL}")
    if os.getenv("E14_REASONING_EFFORT") != REQUIRED_REASONING_EFFORT:
        raise AssertionError("preflight requires E14_REASONING_EFFORT=high")
    if os.getenv("E14_REASONING_FORMAT") != REQUIRED_REASONING_FORMAT:
        raise AssertionError("preflight requires E14_REASONING_FORMAT=hidden")
    if int(os.getenv("E14_MAX_COMPLETION_TOKENS", "0")) != REQUIRED_MAX_COMPLETION_TOKENS:
        raise AssertionError("preflight requires E14_MAX_COMPLETION_TOKENS=1600")
    if float(os.getenv("E8_MODEL_TEMPERATURE", "0")) != 0.0:
        raise AssertionError("preflight requires E8_MODEL_TEMPERATURE=0")
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("preflight requires E8_CONFIRM_ZERO_COST=1")
    if not os.getenv("GROQ_API_KEY"):
        raise AssertionError("GROQ_API_KEY must be present in the environment")


def main() -> int:
    assert_configuration()
    base_module = SimpleNamespace(
        SYSTEM_PROMPT=(
            "Return only one valid JSON object. Do not include markdown, prose, or reasoning."
        )
    )
    prompt = 'Return exactly a JSON object with key "compatibility" and boolean value true.'
    try:
        raw, meta = transport.call_groq(prompt, 90, base_module)
        parsed = json.loads(raw)
        valid = isinstance(parsed, dict) and parsed.get("compatibility") is True
        result = {
            "status": (
                "E14I_GROQ_HIGH_JSON_HIDDEN_COMPATIBILITY_PREFLIGHT_PASS"
                if valid
                else "E14I_GROQ_HIGH_JSON_HIDDEN_COMPATIBILITY_PREFLIGHT_FAIL"
            ),
            "model": REQUIRED_MODEL,
            "reasoning_effort": REQUIRED_REASONING_EFFORT,
            "reasoning_format": REQUIRED_REASONING_FORMAT,
            "max_completion_tokens": REQUIRED_MAX_COMPLETION_TOKENS,
            "json_object_parseable": bool(isinstance(parsed, dict)),
            "compatibility_value_true": bool(valid),
            "provider_attempts": meta.get("provider_attempts"),
            "rate_limit_events": meta.get("rate_limit_events"),
            "inference_call_made": True,
            "uses_private_task_packet": False,
            "reads_private_oracle": False,
            "reads_private_scorer_rows": False,
            "validation_used": False,
            "locked_test_used": False,
            "prints_api_key": False,
            "prints_raw_model_output": False
        }
        print(json.dumps(result, indent=2))
        return 0 if valid else 1
    except transport.E14ProviderRequestError as exc:
        print(json.dumps({
            "status": "E14I_GROQ_HIGH_JSON_HIDDEN_COMPATIBILITY_PREFLIGHT_FAIL",
            "model": REQUIRED_MODEL,
            "reasoning_effort": REQUIRED_REASONING_EFFORT,
            "reasoning_format": REQUIRED_REASONING_FORMAT,
            "max_completion_tokens": REQUIRED_MAX_COMPLETION_TOKENS,
            "provider_failure_category": exc.category,
            "provider_http_status": exc.status_code,
            "inference_call_made": True,
            "uses_private_task_packet": False,
            "reads_private_oracle": False,
            "reads_private_scorer_rows": False,
            "validation_used": False,
            "locked_test_used": False,
            "prints_api_key": False,
            "prints_raw_model_output": False
        }, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
