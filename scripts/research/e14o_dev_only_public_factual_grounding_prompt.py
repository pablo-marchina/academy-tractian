#!/usr/bin/env python3
"""E14o DEV-only public factual-grounding prompt candidate.

E14o inherits the complete E14l generation stack and changes exactly one
intervention class: a public factual-grounding suffix is appended to the frozen
E10b system prompt. The same suffix is therefore present for the initial model
call and any already-existing E14f semantic-repair call. No private oracle,
scorer rows, VALIDATION, LOCKED_TEST, or per-claim semantic labels are available
to the model.

E14n remains a separate, unchanged deterministic post-generation safeguard and
must be applied after a complete E14o capture before quality measurement.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
E14L_PATH = HERE / "e14l_dev_only_120b_medium_reasoning_strict_4096.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14l = load_module("e14l_parent_for_e14o", E14L_PATH)
e10b = e14l.e14k.e14f.e10b

E14O_MANIFEST = Path("research/experiments/e14o-dev-only-public-factual-grounding-prompt-manifest.json")
PROMPT_MARKER = "E14O_PUBLIC_FACTUAL_GROUNDING_DISCIPLINE"
FACTUAL_GROUNDING_SUFFIX = f"""

{PROMPT_MARKER}
Factual-grounding discipline:
- State a current or past task-world fact only when it is directly present in the visible packet or is an explicit public tool-contract fact.
- Do not promote domain plausibility, diagnosis inference, severity inference, causal inference, permission inference, temporal inference, or an available tool endpoint into an observed fact.
- Evidence-plan entries describe evidence to retrieve and must not imply that the retrieval result has already been observed.
- When direct support is absent, express the content as a conditional hypothesis, a procedural recommendation, or explicit uncertainty rather than as a factual assertion.
- Keep observed facts distinct from hypotheses in proposed_next_step, risk_notes, and calibration_reason.
- Do not change decision/action/escalation merely to satisfy wording discipline; preserve the decision supported by the visible packet.
""".rstrip()

EXPECTED_GROUPS = ["G501", "C710", "S420"]
EXPECTED_REPEATS = 2


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_manifest(path: Path) -> None:
    manifest = _load(path)
    if not isinstance(manifest, dict) or manifest.get("experiment_id") != "E14o":
        raise AssertionError("E14o requires the frozen E14o manifest")
    reps = manifest.get("representative_groups")
    if not isinstance(reps, dict) or reps.get("DEV") != EXPECTED_GROUPS or sorted(reps.keys()) != ["DEV"]:
        raise AssertionError("E14o representative DEV groups changed")
    repeats = manifest.get("repeats")
    if not isinstance(repeats, dict) or repeats.get("DEV_ACTION_ESCALATION_CALIBRATION") != EXPECTED_REPEATS:
        raise AssertionError("E14o repeats changed")
    change = manifest.get("candidate_change")
    if not isinstance(change, dict) or change.get("change_class") != "public_factual_grounding_system_prompt_only":
        raise AssertionError("E14o change class changed")
    if change.get("single_intervention") is not True:
        raise AssertionError("E14o must remain a single-intervention candidate")


def effective_system_prompt() -> str:
    parent = e10b.STRICT_E10B_SYSTEM_PROMPT
    if PROMPT_MARKER in parent:
        raise AssertionError("E14o prompt marker already present in parent prompt")
    return parent.rstrip() + FACTUAL_GROUNDING_SUFFIX


def _attempt_lock_path(out: Path) -> Path:
    return Path(str(out) + ".attempt-lock.json")


def _consume_real_attempt(out: Path) -> Path:
    lock = _attempt_lock_path(out)
    if out.exists():
        raise AssertionError("E14o output already exists; real capture may not be rerun")
    if lock.exists():
        raise AssertionError("E14o real capture attempt already consumed; rerun is forbidden")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(
        json.dumps(
            {
                "experiment_id": "E14o",
                "status": "REAL_CAPTURE_ATTEMPT_CONSUMED",
                "real_capture_runs_allowed": 1,
                "rerun_allowed": False,
                "contains_raw_output": False,
                "contains_private_oracle": False,
                "contains_private_scorer_rows": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return lock


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_manifest(args.manifest)

    # Preflight every no-inference frozen check before consuming the sole real attempt.
    e14l.assert_frozen_configuration(dry_run=args.dry_run)
    e14l.schema.run_self_checks()
    effective_prompt = effective_system_prompt()

    attempt_lock: Path | None = None
    if not args.dry_run:
        attempt_lock = _consume_real_attempt(args.out)

    original_prompt = e10b.STRICT_E10B_SYSTEM_PROMPT
    e10b.STRICT_E10B_SYSTEM_PROMPT = effective_prompt
    try:
        summary = e14l.run(args)
    finally:
        e10b.STRICT_E10B_SYSTEM_PROMPT = original_prompt

    parent_status = summary.get("status")
    capture_pass = parent_status == "E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS"
    parent_config = summary.pop("e14l_reasoning_configuration", {})

    summary["report_version"] = "e14o-dev-only-public-factual-grounding-prompt-v1"
    summary["status"] = (
        "E14O_DEV_ONLY_PUBLIC_FACTUAL_GROUNDING_PROMPT_CAPTURE_PASS"
        if capture_pass
        else "E14O_DEV_ONLY_PUBLIC_FACTUAL_GROUNDING_PROMPT_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14l_capture_status"] = parent_status
    summary["e14o_configuration"] = {
        **(parent_config if isinstance(parent_config, dict) else {}),
        "change_class": "public_factual_grounding_system_prompt_only",
        "prompt_changed": True,
        "prompt_marker": PROMPT_MARKER,
        "factual_grounding_rule_count": 6,
        "initial_and_existing_e14f_repair_calls_share_effective_system_prompt": True,
        "model_changed": False,
        "reasoning_effort_changed": False,
        "response_format_changed": False,
        "schema_changed": False,
        "completion_budget_changed": False,
        "temperature_changed": False,
        "pacing_changed": False,
        "semantic_repair_trigger_policy_changed": False,
        "post_model_policy_changed": False,
        "evidence_planning_policy_changed": False,
        "action_escalation_policy_changed": False,
        "private_oracle_used_by_model": False,
        "private_scorer_rows_used_by_model": False,
        "semantic_judge_rows_used_by_model": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "e14n_guard_required_after_complete_capture": True,
        "e14n_guard_changed": False,
    }
    summary["e14o_attempt_policy"] = {
        "real_capture_runs_allowed": 1,
        "attempt_consumed": not args.dry_run,
        "rerun_allowed": False if not args.dry_run else None,
        "attempt_lock_written": attempt_lock is not None,
        "attempt_lock_contains_raw_output": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    assert_manifest(E14O_MANIFEST)
    e14l.run_self_checks()
    prompt = effective_system_prompt()
    if PROMPT_MARKER not in prompt:
        raise AssertionError("E14o prompt marker missing")
    if prompt.count(PROMPT_MARKER) != 1:
        raise AssertionError("E14o prompt marker must appear exactly once")
    required_fragments = (
        "directly present in the visible packet",
        "domain plausibility",
        "must not imply that the retrieval result has already been observed",
        "conditional hypothesis",
        "Keep observed facts distinct from hypotheses",
        "Do not change decision/action/escalation merely to satisfy wording discipline",
    )
    for fragment in required_fragments:
        if fragment not in prompt:
            raise AssertionError(f"E14o grounding rule missing: {fragment}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14O_MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dev_repeats is not None and args.dev_repeats != EXPECTED_REPEATS:
        raise AssertionError(f"E14o repeats are frozen at {EXPECTED_REPEATS}")
    if args.dry_run:
        run_self_checks()

    summary = run(args)
    completeness = summary.get("e14_completeness", {})
    config = summary.get("e14o_configuration", {})
    attempt = summary.get("e14o_attempt_policy", {})
    print(json.dumps({
        "status": summary.get("status"),
        "model": config.get("model"),
        "reasoning_effort": config.get("reasoning_effort"),
        "prompt_change_class": config.get("change_class"),
        "factual_grounding_rule_count": config.get("factual_grounding_rule_count"),
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "real_capture_attempt_consumed": attempt.get("attempt_consumed"),
        "rerun_allowed": attempt.get("rerun_allowed"),
        "e14n_guard_required_after_complete_capture": config.get("e14n_guard_required_after_complete_capture"),
        "private_oracle_used_by_model": config.get("private_oracle_used_by_model"),
        "validation_feedback_used": config.get("validation_feedback_used"),
        "locked_test_used": config.get("locked_test_used"),
    }, indent=2))
    return 0 if summary.get("status") == "E14O_DEV_ONLY_PUBLIC_FACTUAL_GROUNDING_PROMPT_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
