#!/usr/bin/env python3
"""E14k DEV-only high-reasoning 4096 completion-budget candidate.

E14k inherits the E14j effective stack and changes exactly one model request
parameter: max_completion_tokens 1600 -> 4096. Model, reasoning effort,
response-format enforcement, strict public schema, temperature, prompts,
semantic repair, post-model policies, scorer and acceptance gate stay frozen.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
E14F_PATH = HERE / "e14f_dev_only_public_semantic_repair.py"
SCHEMA_PATH = HERE / "e14j_strict_output_schema.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14f = load_module("e14f_parent_for_e14k", E14F_PATH)
schema = load_module("e14j_schema_for_e14k", SCHEMA_PATH)

E14K_MANIFEST = Path("research/experiments/e14k-dev-only-high-reasoning-4096-completion-budget-manifest.json")
REQUIRED_MODEL = "openai/gpt-oss-120b"
REQUIRED_REASONING_EFFORT = "high"
REQUIRED_REASONING_FORMAT_ENV = "hidden"
REQUIRED_RESPONSE_FORMAT_MODE = "json_schema_strict"
REQUIRED_MAX_COMPLETION_TOKENS = 4096
PARENT_MAX_COMPLETION_TOKENS = 1600
REQUIRED_TEMPERATURE = 0.0
REQUIRED_BETWEEN_CALL_DELAY_SECONDS = 25.0
REQUIRED_REPAIR_DELAY_SECONDS = 25.0
REQUIRED_MAX_RETRIES = 2


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None else int(value)


def assert_frozen_configuration(*, dry_run: bool) -> None:
    model = os.getenv("E8_GROQ_MODEL", REQUIRED_MODEL if dry_run else "")
    if model != REQUIRED_MODEL:
        raise AssertionError(f"E14k requires E8_GROQ_MODEL={REQUIRED_MODEL}")

    reasoning = os.getenv("E14_REASONING_EFFORT", REQUIRED_REASONING_EFFORT if dry_run else "")
    if reasoning != REQUIRED_REASONING_EFFORT:
        raise AssertionError("E14k requires E14_REASONING_EFFORT=high")

    reasoning_format = os.getenv(
        "E14_REASONING_FORMAT",
        REQUIRED_REASONING_FORMAT_ENV if dry_run else "",
    )
    if reasoning_format != REQUIRED_REASONING_FORMAT_ENV:
        raise AssertionError("E14k preserves E14_REASONING_FORMAT=hidden as an environment value only")

    response_mode = os.getenv(
        "E14_RESPONSE_FORMAT_MODE",
        REQUIRED_RESPONSE_FORMAT_MODE if dry_run else "",
    )
    if response_mode != REQUIRED_RESPONSE_FORMAT_MODE:
        raise AssertionError("E14k requires E14_RESPONSE_FORMAT_MODE=json_schema_strict")

    max_tokens = _int_env("E14_MAX_COMPLETION_TOKENS", REQUIRED_MAX_COMPLETION_TOKENS)
    if max_tokens != REQUIRED_MAX_COMPLETION_TOKENS:
        raise AssertionError("E14k requires E14_MAX_COMPLETION_TOKENS=4096")

    temperature = _float_env("E8_MODEL_TEMPERATURE", REQUIRED_TEMPERATURE)
    if temperature != REQUIRED_TEMPERATURE:
        raise AssertionError("E14k requires unchanged E8_MODEL_TEMPERATURE=0")

    between_delay = _float_env("E8_BETWEEN_CALL_DELAY_SECONDS", REQUIRED_BETWEEN_CALL_DELAY_SECONDS)
    if between_delay != REQUIRED_BETWEEN_CALL_DELAY_SECONDS:
        raise AssertionError("E14k requires unchanged E8_BETWEEN_CALL_DELAY_SECONDS=25")

    repair_delay = _float_env("E14F_REPAIR_DELAY_SECONDS", REQUIRED_REPAIR_DELAY_SECONDS)
    if repair_delay != REQUIRED_REPAIR_DELAY_SECONDS:
        raise AssertionError("E14k requires unchanged E14F_REPAIR_DELAY_SECONDS=25")

    max_retries = _int_env("E14_MAX_RETRIES", REQUIRED_MAX_RETRIES)
    if max_retries != REQUIRED_MAX_RETRIES:
        raise AssertionError("E14k requires unchanged E14_MAX_RETRIES=2")

    if not dry_run and os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("E14k real measurement requires E8_CONFIRM_ZERO_COST=1")


def _run_parent_without_structural_sleep(args: argparse.Namespace) -> dict[str, Any]:
    """Skip pacing sleeps only for a no-provider structural dry-run.

    The frozen real-run values are asserted before this helper is called. The
    temporary zero values never apply to a real provider call and are restored
    immediately after the dry-run parent stack returns.
    """
    if not args.dry_run:
        return e14f.run(args)

    names = ("E8_BETWEEN_CALL_DELAY_SECONDS", "E14F_REPAIR_DELAY_SECONDS")
    saved = {name: os.environ.get(name) for name in names}
    try:
        os.environ["E8_BETWEEN_CALL_DELAY_SECONDS"] = "0"
        os.environ["E14F_REPAIR_DELAY_SECONDS"] = "0"
        return e14f.run(args)
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_frozen_configuration(dry_run=args.dry_run)
    schema.run_self_checks()
    summary = _run_parent_without_structural_sleep(args)
    parent_status = summary.get("status")
    capture_pass = parent_status == "E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS"

    summary["report_version"] = "e14k-dev-only-high-reasoning-4096-completion-budget-v1"
    summary["status"] = (
        "E14K_DEV_ONLY_HIGH_REASONING_4096_COMPLETION_BUDGET_CAPTURE_PASS"
        if capture_pass
        else "E14K_DEV_ONLY_HIGH_REASONING_4096_COMPLETION_BUDGET_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14f_capture_status"] = parent_status
    summary["e14k_completion_budget_configuration"] = {
        "change_class": "completion_budget_only",
        "provider": "groq",
        "model": REQUIRED_MODEL,
        "reasoning_effort": REQUIRED_REASONING_EFFORT,
        "reasoning_format_environment_value": REQUIRED_REASONING_FORMAT_ENV,
        "reasoning_format_effect_not_claimed_for_gpt_oss": True,
        "response_format": "json_schema",
        "response_format_mode": REQUIRED_RESPONSE_FORMAT_MODE,
        "strict": True,
        "schema_name": schema.SCHEMA_NAME,
        "schema_source": "existing_public_e10b_output_contract_only",
        "parent_max_completion_tokens": PARENT_MAX_COMPLETION_TOKENS,
        "max_completion_tokens": REQUIRED_MAX_COMPLETION_TOKENS,
        "temperature": REQUIRED_TEMPERATURE,
        "between_call_delay_seconds": REQUIRED_BETWEEN_CALL_DELAY_SECONDS,
        "semantic_repair_delay_seconds": REQUIRED_REPAIR_DELAY_SECONDS,
        "max_retries": REQUIRED_MAX_RETRIES,
        "completion_budget_changed": True,
        "model_changed": False,
        "reasoning_effort_changed": False,
        "reasoning_format_environment_value_changed": False,
        "response_format_changed": False,
        "schema_changed": False,
        "temperature_changed": False,
        "pacing_changed": False,
        "prompt_changed": False,
        "semantic_repair_changed": False,
        "post_model_policy_changed": False,
        "scorer_changed": False,
        "acceptance_thresholds_changed": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "private_oracle_used_by_model_or_schema": False,
        "budget_rescue_allowed_inside_candidate": False,
        "structural_dry_run_sleep_skipped": bool(args.dry_run),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    e14f.run_self_checks()
    schema.run_self_checks()
    assert_frozen_configuration(dry_run=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14K_MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        run_self_checks()
    summary = run(args)
    completeness = summary.get("e14_completeness", {})
    repair = summary.get("e14f_public_semantic_repair", {})
    boundary = summary.get("selective_reprocess_authorization_boundary", {})
    config = summary.get("e14k_completion_budget_configuration", {})
    print(json.dumps({
        "status": summary["status"],
        "model": config.get("model"),
        "reasoning_effort": config.get("reasoning_effort"),
        "response_format": config.get("response_format"),
        "strict": config.get("strict"),
        "parent_max_completion_tokens": config.get("parent_max_completion_tokens"),
        "max_completion_tokens": config.get("max_completion_tokens"),
        "between_call_delay_seconds": config.get("between_call_delay_seconds"),
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "semantic_repair_triggered_calls": repair.get("triggered_calls"),
        "semantic_repair_calls": repair.get("repair_calls"),
        "semantic_repair_residual_violation_calls": repair.get("calls_with_residual_public_violations"),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs"),
    }, indent=2))
    return 0 if summary["status"] == "E14K_DEV_ONLY_HIGH_REASONING_4096_COMPLETION_BUDGET_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
