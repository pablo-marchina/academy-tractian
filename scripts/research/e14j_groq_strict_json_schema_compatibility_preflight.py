#!/usr/bin/env python3
"""Synthetic provider preflight for E14j strict JSON Schema compatibility.

This makes exactly one non-benchmark Groq inference using the exact E14j output
schema. It uses no TRACTIAN case packet, private oracle, scorer rows, VALIDATION,
or LOCKED_TEST material and never prints raw model output or API keys.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
TRANSPORT_PATH = HERE / "e14_groq_rate_limit_transport.py"
SCHEMA_PATH = HERE / "e14j_strict_output_schema.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


transport = load_module("e14j_transport_preflight", TRANSPORT_PATH)
schema = load_module("e14j_schema_preflight", SCHEMA_PATH)

REQUIRED_MODEL = "openai/gpt-oss-120b"
REQUIRED_REASONING = "high"
REQUIRED_REASONING_FORMAT_ENV = "hidden"
REQUIRED_RESPONSE_MODE = "json_schema_strict"
REQUIRED_CAP = 1600
REQUIRED_TEMPERATURE = 0.0


class PublicSyntheticBase:
    SYSTEM_PROMPT = (
        "Return exactly one JSON object matching the provider-supplied schema. "
        "Use only the synthetic instructions in this request."
    )


def assert_config() -> None:
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("E14j preflight requires E8_CONFIRM_ZERO_COST=1")
    if os.getenv("E8_GROQ_MODEL") != REQUIRED_MODEL:
        raise AssertionError(f"E14j preflight requires E8_GROQ_MODEL={REQUIRED_MODEL}")
    if os.getenv("E14_REASONING_EFFORT") != REQUIRED_REASONING:
        raise AssertionError("E14j preflight requires E14_REASONING_EFFORT=high")
    if os.getenv("E14_REASONING_FORMAT") != REQUIRED_REASONING_FORMAT_ENV:
        raise AssertionError("E14j preflight preserves E14_REASONING_FORMAT=hidden")
    if os.getenv("E14_RESPONSE_FORMAT_MODE") != REQUIRED_RESPONSE_MODE:
        raise AssertionError("E14j preflight requires E14_RESPONSE_FORMAT_MODE=json_schema_strict")
    if int(os.getenv("E14_MAX_COMPLETION_TOKENS", "0")) != REQUIRED_CAP:
        raise AssertionError("E14j preflight requires E14_MAX_COMPLETION_TOKENS=1600")
    if float(os.getenv("E8_MODEL_TEMPERATURE", "nan")) != REQUIRED_TEMPERATURE:
        raise AssertionError("E14j preflight requires E8_MODEL_TEMPERATURE=0")


def exact_public_schema_shape(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required_root = set(schema.OUTPUT_SCHEMA["required"])
    if set(value) != required_root:
        return False
    if value.get("decision_class") not in {
        "investigate_only", "action_candidate", "escalation_candidate", "insufficient_evidence"
    }:
        return False
    if not isinstance(value.get("evidence_plan"), list) or not all(isinstance(x, str) for x in value["evidence_plan"]):
        return False
    if not isinstance(value.get("should_take_action_now"), bool):
        return False
    if not isinstance(value.get("requires_human_escalation"), bool):
        return False
    if not isinstance(value.get("proposed_next_step"), str) or not isinstance(value.get("risk_notes"), str):
        return False

    trace = value.get("trace_quality_self_check")
    if not isinstance(trace, dict) or set(trace) != {"uses_only_visible_packet", "no_locked_test", "no_gold_claim"}:
        return False
    if not all(isinstance(trace[k], bool) for k in trace):
        return False

    rubric = value.get("action_escalation_rubric")
    rubric_keys = {
        "needs_more_evidence", "safe_to_act", "action_endpoint",
        "needs_human_escalation", "calibration_reason"
    }
    if not isinstance(rubric, dict) or set(rubric) != rubric_keys:
        return False
    if not isinstance(rubric.get("needs_more_evidence"), bool):
        return False
    if not isinstance(rubric.get("safe_to_act"), bool):
        return False
    if not isinstance(rubric.get("needs_human_escalation"), bool):
        return False
    if not isinstance(rubric.get("action_endpoint"), str) or not isinstance(rubric.get("calibration_reason"), str):
        return False
    return True


def main() -> int:
    assert_config()
    schema.run_self_checks()
    prompt = (
        "Synthetic compatibility check only. Return an internally consistent harmless example: "
        "decision_class investigate_only; evidence_plan with one generic public check; no immediate action; "
        "no human escalation; concise next step and risk note; all trace self-check booleans true; "
        "rubric needs_more_evidence true, safe_to_act false, action_endpoint 'none', "
        "needs_human_escalation false, with a short synthetic calibration reason."
    )

    raw, meta = transport.call_groq(prompt, 90, PublicSyntheticBase)
    parseable = False
    exact_shape = False
    try:
        parsed = json.loads(raw)
        parseable = isinstance(parsed, dict)
        exact_shape = exact_public_schema_shape(parsed)
    except Exception:
        parsed = None

    status = (
        "E14J_GROQ_STRICT_JSON_SCHEMA_COMPATIBILITY_PREFLIGHT_PASS"
        if parseable and exact_shape
        else "E14J_GROQ_STRICT_JSON_SCHEMA_COMPATIBILITY_PREFLIGHT_FAIL"
    )
    transport_meta = meta if isinstance(meta, dict) else {}
    print(json.dumps({
        "status": status,
        "model": REQUIRED_MODEL,
        "reasoning_effort": REQUIRED_REASONING,
        "reasoning_format_environment_value": REQUIRED_REASONING_FORMAT_ENV,
        "reasoning_format_effect_claimed": False,
        "response_format": "json_schema",
        "strict": True,
        "max_completion_tokens": REQUIRED_CAP,
        "json_parseable": parseable,
        "exact_public_schema_shape": exact_shape,
        "provider_attempts": transport_meta.get("provider_attempts"),
        "rate_limit_events": transport_meta.get("rate_limit_events"),
        "response_format_mode": transport_meta.get("response_format_mode"),
        "inference_call_made": True,
        "uses_private_task_packet": False,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "validation_used": False,
        "locked_test_used": False,
        "prints_api_key": False,
        "prints_raw_model_output": False,
    }, indent=2))
    return 0 if status.endswith("_PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
