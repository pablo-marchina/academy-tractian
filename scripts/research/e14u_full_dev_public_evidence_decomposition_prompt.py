#!/usr/bin/env python3
"""E14u full-DEV public evidence-decomposition prompt candidate.

Single intervention over the frozen E14o full-DEV generation stack: append one
public evidence-decomposition suffix to the exact E14o effective system prompt.
Model, reasoning, temperature, strict JSON schema, 4096 completion budget,
retry/repair behavior, group coverage and action/escalation semantics remain
unchanged.

Real outputs contain model generations and must remain local/uncommitted.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
PARENT_PATH = HERE / "e14o_full_dev_five_group_capture.py"
SPEC = importlib.util.spec_from_file_location("e14o_full_parent_for_e14u", PARENT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14o full-DEV parent")
parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parent)

E14U_MANIFEST = Path("research/experiments/e14u-full-dev-public-evidence-decomposition-prompt-preregistration.json")
PROMPT_MARKER = "E14U_PUBLIC_EVIDENCE_DECOMPOSITION_DISCIPLINE"
PASS_STATUS = "E14U_FULL_DEV_PUBLIC_EVIDENCE_DECOMPOSITION_PROMPT_CAPTURE_PASS"
FAIL_STATUS = "E14U_FULL_DEV_PUBLIC_EVIDENCE_DECOMPOSITION_PROMPT_CAPTURE_NEEDS_REVIEW"
LOCK_SUFFIX = ".attempt-lock.json"

BASE_E14O_EFFECTIVE_SYSTEM_PROMPT = parent.e14o.effective_system_prompt

EVIDENCE_DECOMPOSITION_SUFFIX = f"""

{PROMPT_MARKER}
Evidence-decomposition discipline:
- Before final JSON, privately decompose the visible task into concrete unknowns and choose the smallest complete set of public GET routes needed to resolve those unknowns.
- Every evidence_plan item must contain exactly one canonical public GET METHOD+path signature. Do not combine multiple GET routes into one evidence item.
- Do not add a route merely because it exists or as a generic checklist item.
- Use GET /users/me only when current-user authorization is materially required for a contemplated state-changing action.
- Use GET /assets/{{assetId}}, GET /assets/{{assetId}}/analyses, and GET /analyses/{{analysisId}} when asset or analysis state is needed by the visible task; preserve that public resource dependency chain when a specific analysis must be inspected.
- Use GET /assets/{{assetId}}/baseline only when baseline, threshold, or reference-state evidence is material.
- Use GET /assets/{{assetId}}/data-quality only when completeness, reliability, or quality of input data is material.
- Use GET /assets/{{assetId}}/rms only when amplitude, time-domain, or trend evidence is material.
- Use GET /assets/{{assetId}}/spectrum only when frequency-domain, harmonic, or fault-signature evidence is material.
- Use GET /models/{{modelId}} whenever model state, drift, model performance, coverage, or retraining is materially implicated.
- Use GET /knowledge/search followed by GET /knowledge/{{docId}} only when procedural, domain, or source-grounding knowledge is materially required.
- If a state-changing endpoint is selected, include the public target-state read and authorization read required by the existing frozen action policy before action.
- Prefer 4-6 distinct public reads when that is complete; allow a seventh only for a distinct public dependency; never emit more than 7 distinct public reads.
- Do not change the existing decision/action/escalation calibration rules; this suffix changes evidence decomposition guidance only.
- Never use private expected paths, evaluator labels, VALIDATION feedback, or LOCKED_TEST material.
""".rstrip()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_e14u_manifest(path: Path) -> None:
    manifest = _load(path)
    if not isinstance(manifest, dict):
        raise AssertionError("E14u manifest must be an object")
    if manifest.get("experiment_id") != "E14u-full-DEV-public-evidence-decomposition-prompt":
        raise AssertionError("wrong E14u manifest")
    if manifest.get("intervention_class") != "public_evidence_decomposition_system_prompt_only":
        raise AssertionError("E14u intervention class changed")
    if manifest.get("single_intervention") is not True:
        raise AssertionError("E14u must remain a single intervention")

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        raise AssertionError("E14u scope missing")
    if scope.get("measurement_splits") != ["DEV"]:
        raise AssertionError("E14u must remain DEV-only")
    if set(scope.get("forbidden_splits") or []) != {"VALIDATION", "LOCKED_TEST"}:
        raise AssertionError("E14u must forbid VALIDATION and LOCKED_TEST")
    if scope.get("dev_groups") != parent.EXPECTED_GROUPS:
        raise AssertionError("E14u full-DEV group set/order changed")
    if int(scope.get("repeats_per_group") or 0) != parent.EXPECTED_REPEATS:
        raise AssertionError("E14u repeats changed")
    if int(scope.get("expected_fixed_calls") or 0) != parent.EXPECTED_CALLS:
        raise AssertionError("E14u expected fixed-call count changed")

    config = manifest.get("frozen_generation_configuration")
    if not isinstance(config, dict):
        raise AssertionError("E14u generation config missing")
    if config.get("model") != "openai/gpt-oss-120b":
        raise AssertionError("E14u model changed")
    if config.get("reasoning_effort") != "medium":
        raise AssertionError("E14u reasoning changed")
    if config.get("temperature") != 0:
        raise AssertionError("E14u temperature changed")
    if config.get("strict_json") is not True or int(config.get("max_completion_tokens") or 0) != 4096:
        raise AssertionError("E14u output contract or completion budget changed")

    change = manifest.get("prompt_change")
    if not isinstance(change, dict) or change.get("marker") != PROMPT_MARKER:
        raise AssertionError("E14u prompt marker changed")
    if change.get("change_class") != "append_public_evidence_decomposition_suffix_only":
        raise AssertionError("E14u prompt change class changed")

    attempt = manifest.get("real_attempt_policy")
    if not isinstance(attempt, dict) or int(attempt.get("real_generation_runner_invocations_allowed") or 0) != 1:
        raise AssertionError("E14u real-attempt policy changed")
    if attempt.get("attempt_lock_before_first_provider_call") is not True or attempt.get("rerun_after_attempt_consumption") is not False:
        raise AssertionError("E14u attempt lock/no-rerun policy changed")


def effective_system_prompt() -> str:
    base_prompt = BASE_E14O_EFFECTIVE_SYSTEM_PROMPT()
    if PROMPT_MARKER in base_prompt:
        raise AssertionError("E14u marker already present in parent prompt")
    return base_prompt.rstrip() + EVIDENCE_DECOMPOSITION_SUFFIX


def _attempt_lock(out: Path) -> Path:
    return Path(str(out) + LOCK_SUFFIX)


def consume_real_attempt(out: Path) -> Path:
    lock = _attempt_lock(out)
    if out.exists():
        raise SystemExit("E14u output already exists; rerun is forbidden")
    if lock.exists():
        raise SystemExit("E14u generation attempt already consumed; replacement requires an explicit amendment")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(
        json.dumps(
            {
                "report_version": "e14u-full-dev-generation-attempt-lock-v1",
                "experiment_id": "E14u-full-DEV-public-evidence-decomposition-prompt",
                "status": "E14U_FULL_DEV_GENERATION_ATTEMPT_CONSUMED",
                "expected_fixed_calls": parent.EXPECTED_CALLS,
                "expected_dev_groups": len(parent.EXPECTED_GROUPS),
                "repeats_per_group": parent.EXPECTED_REPEATS,
                "model": "openai/gpt-oss-120b",
                "reasoning_effort": "medium",
                "rerun_allowed": False,
                "contains_raw_output": False,
                "contains_private_oracle": False,
                "contains_private_scorer_rows": False,
                "uses_validation_feedback": False,
                "uses_locked_test": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return lock


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_e14u_manifest(args.manifest)
    if args.dev_repeats is not None and args.dev_repeats != parent.EXPECTED_REPEATS:
        raise AssertionError(f"E14u repeats are frozen at {parent.EXPECTED_REPEATS}")

    # Parent run requires its own frozen execution manifest. E14u's manifest is
    # asserted separately above and changes only the effective system prompt.
    parent_args = copy.copy(args)
    parent_args.manifest = parent.MANIFEST

    saved_effective = parent.e14o.effective_system_prompt
    saved_consume = parent.consume_real_attempt
    parent.e14o.effective_system_prompt = effective_system_prompt
    parent.consume_real_attempt = consume_real_attempt
    try:
        summary = parent.run(parent_args)
    finally:
        parent.e14o.effective_system_prompt = saved_effective
        parent.consume_real_attempt = saved_consume

    parent_status = summary.get("status")
    capture_pass = parent_status == parent.PASS_STATUS
    full = summary.get("full_dev_generation")
    full = full if isinstance(full, dict) else {}
    comp = summary.get("e14_completeness")
    comp = comp if isinstance(comp, dict) else {}
    agg = summary.get("aggregate_metrics")
    agg = agg if isinstance(agg, dict) else {}

    structural_complete = (
        capture_pass
        and int(agg.get("total_calls") or 0) == parent.EXPECTED_CALLS
        and int(agg.get("parsed_model_outputs_available") or 0) == parent.EXPECTED_CALLS
        and int(agg.get("scoreable_calls") or 0) == parent.EXPECTED_CALLS
        and comp.get("passed") is True
        and full.get("each_group_exactly_two_calls") is True
        and full.get("validation_ran") is False
        and full.get("locked_test_used") is False
    )

    summary["report_version"] = "e14u-full-dev-public-evidence-decomposition-prompt-v1"
    summary["status"] = PASS_STATUS if structural_complete else FAIL_STATUS
    summary["parent_e14o_full_dev_capture_status"] = parent_status
    full["candidate"] = "E14u-after-public-evidence-decomposition-prompt-before-fixed-E14n-E14p-E14q-E14q2-stack"
    full["prompt_changed_from_targeted_E14o"] = True
    summary["full_dev_generation"] = full
    summary["e14u_configuration"] = {
        "change_class": "public_evidence_decomposition_system_prompt_only",
        "single_intervention": True,
        "prompt_marker": PROMPT_MARKER,
        "model": "openai/gpt-oss-120b",
        "reasoning_effort": "medium",
        "temperature": 0,
        "strict_json": True,
        "max_completion_tokens": 4096,
        "model_changed": False,
        "reasoning_effort_changed": False,
        "temperature_changed": False,
        "response_format_changed": False,
        "completion_budget_changed": False,
        "retry_policy_changed": False,
        "semantic_repair_policy_changed": False,
        "action_escalation_policy_changed": False,
        "evidence_decomposition_prompt_changed": True,
        "max_distinct_public_reads_in_prompt": 7,
        "fixed_post_generation_stack_required": ["E14n-v1.1", "E14p", "E14q", "E14q2"],
        "private_oracle_used_by_model": False,
        "private_scorer_rows_used_by_model": False,
        "semantic_judge_rows_used_by_model": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
    }
    summary["e14u_attempt_policy"] = {
        "real_generation_runner_invocations_allowed": 1,
        "attempt_consumed": not args.dry_run,
        "rerun_allowed": False if not args.dry_run else None,
        "attempt_lock_written": not args.dry_run,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    assert_e14u_manifest(E14U_MANIFEST)
    prompt = effective_system_prompt()
    if prompt.count(PROMPT_MARKER) != 1:
        raise AssertionError("E14u prompt marker must occur exactly once")
    required = (
        "smallest complete set of public GET routes",
        "exactly one canonical public GET METHOD+path signature",
        "GET /models/{modelId}",
        "never emit more than 7 distinct public reads",
        "Do not change the existing decision/action/escalation calibration rules",
    )
    for fragment in required:
        if fragment not in prompt:
            raise AssertionError(f"E14u prompt rule missing: {fragment}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14U_MANIFEST)
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
    full = summary.get("full_dev_generation", {})
    comp = summary.get("e14_completeness", {})
    agg = summary.get("aggregate_metrics", {})
    config = summary.get("e14u_configuration", {})
    attempt = summary.get("e14u_attempt_policy", {})
    print(json.dumps({
        "status": summary.get("status"),
        "model": config.get("model"),
        "reasoning_effort": config.get("reasoning_effort"),
        "prompt_change_class": config.get("change_class"),
        "required_dev_groups": len(parent.EXPECTED_GROUPS),
        "observed_dev_groups": full.get("observed_dev_groups"),
        "repeats_per_group": parent.EXPECTED_REPEATS,
        "total_calls": agg.get("total_calls"),
        "parsed_model_outputs_available": agg.get("parsed_model_outputs_available"),
        "scoreable_calls": agg.get("scoreable_calls"),
        "completeness_pass": comp.get("passed"),
        "each_group_exactly_two_calls": full.get("each_group_exactly_two_calls"),
        "validation_ran": full.get("validation_ran"),
        "locked_test_used": full.get("locked_test_used"),
        "dry_run": args.dry_run,
        "real_generation_attempt_consumed": attempt.get("attempt_consumed"),
        "rerun_allowed": attempt.get("rerun_allowed"),
        "private_oracle_used_by_model": config.get("private_oracle_used_by_model"),
        "validation_feedback_used": config.get("validation_feedback_used"),
    }, indent=2))
    return 0 if summary.get("status") == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
