#!/usr/bin/env python3
"""E14h DEV-only GPT-OSS 120B high-reasoning candidate.

E14h inherits the complete E14f stack and preserves the E14g model selection.
Relative to E14g it changes exactly one real-call configuration variable:
`E14_REASONING_EFFORT` must be `high` instead of `medium`.

Provider, model, prompts, conditional semantic repair, temperature, completion
budget, JSON Object Mode, post-model guards, scorer and acceptance thresholds
remain unchanged. No VALIDATION tuning or LOCKED_TEST access is allowed.
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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14f = load_module("e14f_parent_for_e14h", E14F_PATH)

E14H_MANIFEST = Path("research/experiments/e14h-dev-only-gpt-oss-120b-high-reasoning-manifest.json")
REQUIRED_MODEL = "openai/gpt-oss-120b"
REQUIRED_REASONING_EFFORT = "high"
PARENT_REASONING_EFFORT = "medium"
REQUIRED_MAX_COMPLETION_TOKENS = 1600
REQUIRED_TEMPERATURE = 0.0


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None else float(value)


def assert_frozen_real_configuration(*, dry_run: bool) -> None:
    model = os.getenv("E8_GROQ_MODEL", REQUIRED_MODEL if dry_run else "")
    if model != REQUIRED_MODEL:
        raise AssertionError(f"E14h requires E8_GROQ_MODEL={REQUIRED_MODEL}")

    reasoning = os.getenv("E14_REASONING_EFFORT", REQUIRED_REASONING_EFFORT if dry_run else "")
    if reasoning != REQUIRED_REASONING_EFFORT:
        raise AssertionError("E14h requires E14_REASONING_EFFORT=high")

    max_tokens = int(os.getenv("E14_MAX_COMPLETION_TOKENS", str(REQUIRED_MAX_COMPLETION_TOKENS)))
    if max_tokens != REQUIRED_MAX_COMPLETION_TOKENS:
        raise AssertionError("E14h requires unchanged E14_MAX_COMPLETION_TOKENS=1600")

    temperature = _float_env("E8_MODEL_TEMPERATURE", REQUIRED_TEMPERATURE)
    if temperature != REQUIRED_TEMPERATURE:
        raise AssertionError("E14h requires unchanged E8_MODEL_TEMPERATURE=0")

    if not dry_run and os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("E14h real measurement requires E8_CONFIRM_ZERO_COST=1")


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_frozen_real_configuration(dry_run=args.dry_run)
    summary = e14f.run(args)
    parent_status = summary.get("status")
    capture_pass = parent_status == "E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS"
    summary["report_version"] = "e14h-dev-only-gpt-oss-120b-high-reasoning-v1"
    summary["status"] = (
        "E14H_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_CAPTURE_PASS"
        if capture_pass
        else "E14H_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14f_capture_status"] = parent_status
    summary["e14h_reasoning_configuration"] = {
        "change_class": "reasoning_effort_only",
        "provider": "groq",
        "model": REQUIRED_MODEL,
        "model_changed_from_e14g": False,
        "parent_reasoning_effort": PARENT_REASONING_EFFORT,
        "reasoning_effort": REQUIRED_REASONING_EFFORT,
        "reasoning_effort_changed": True,
        "prompt_changed": False,
        "semantic_repair_changed": False,
        "temperature": REQUIRED_TEMPERATURE,
        "temperature_changed": False,
        "max_completion_tokens": REQUIRED_MAX_COMPLETION_TOKENS,
        "completion_budget_changed": False,
        "response_format_changed": False,
        "post_model_policy_changed": False,
        "scorer_changed": False,
        "acceptance_thresholds_changed": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "private_oracle_used_by_model_or_repair": False,
        "zero_cost_operator_confirmation_required": not args.dry_run,
        "completion_budget_rescue_allowed_inside_candidate": False,
        "causal_interpretation": "single configuration intervention, but separate model generations are not deterministic paired observations; use absolute gate",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    e14f.run_self_checks()
    assert_frozen_real_configuration(dry_run=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14H_MANIFEST)
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
    config = summary.get("e14h_reasoning_configuration", {})
    print(json.dumps({
        "status": summary["status"],
        "model": config.get("model"),
        "reasoning_effort": config.get("reasoning_effort"),
        "max_completion_tokens": config.get("max_completion_tokens"),
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
    return 0 if summary["status"] == "E14H_DEV_ONLY_GPT_OSS_120B_HIGH_REASONING_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
