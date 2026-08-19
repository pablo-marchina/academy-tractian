#!/usr/bin/env python3
"""Full-DEV five-group generation for the frozen E14p candidate stack.

This runner reuses the exact accepted E14o generation stack and changes only
coverage/cardinality plumbing required by the preregistered full-DEV gate:
five frozen DEV groups x two repeats = ten fixed calls. It does not run
VALIDATION or LOCKED_TEST and does not change model, prompt, reasoning, schema,
completion budget, or any historical quality-policy semantics.

The generated real capture contains raw model outputs and must remain local.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).parent
E14O_PATH = HERE / "e14o_dev_only_public_factual_grounding_prompt.py"
SPEC = importlib.util.spec_from_file_location("e14o_parent_for_full_dev", E14O_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load frozen E14o runner")
e14o = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14o)

e14l = e14o.e14l
e14_core = e14l.e14k.e14f.e14e.e14d.e14c.e14
e11 = e14_core.e11

MANIFEST = Path("research/experiments/e14p-full-dev-five-group-execution-manifest.json")
EXPECTED_GROUPS = ["asset_G501", "asset_C710", "asset_S420", "asset_M208", "asset_M101"]
EXPECTED_REPEATS = 2
EXPECTED_CALLS = 10
PASS_STATUS = "E14O_FULL_DEV_FIVE_GROUP_CAPTURE_PASS"
FAIL_STATUS = "E14O_FULL_DEV_FIVE_GROUP_CAPTURE_NEEDS_REVIEW"
LOCK_SUFFIX = ".attempt-lock.json"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_manifest(path: Path) -> None:
    manifest = _load(path)
    if not isinstance(manifest, dict) or manifest.get("experiment_id") != "E14p-full-DEV-five-group":
        raise AssertionError("frozen E14p full-DEV execution manifest required")
    reps = manifest.get("representative_groups")
    if not isinstance(reps, dict) or sorted(reps.keys()) != ["DEV"] or reps.get("DEV") != EXPECTED_GROUPS:
        raise AssertionError("full-DEV group set/order changed")
    repeats = manifest.get("repeats")
    if not isinstance(repeats, dict) or repeats.get("DEV_ACTION_ESCALATION_CALIBRATION") != EXPECTED_REPEATS:
        raise AssertionError("full-DEV repeats changed")
    if manifest.get("expected_fixed_calls") != EXPECTED_CALLS:
        raise AssertionError("full-DEV expected call count changed")
    scope = manifest.get("scope")
    if not isinstance(scope, dict) or scope.get("measurement_splits") != ["DEV"]:
        raise AssertionError("full-DEV runner must remain DEV-only")
    if set(scope.get("forbidden_splits") or []) != {"VALIDATION", "LOCKED_TEST"}:
        raise AssertionError("VALIDATION and LOCKED_TEST must remain forbidden")


def _attempt_lock(out: Path) -> Path:
    return Path(str(out) + LOCK_SUFFIX)


def consume_real_attempt(out: Path) -> Path:
    lock = _attempt_lock(out)
    if out.exists():
        raise SystemExit("full-DEV capture output already exists; rerun is forbidden")
    if lock.exists():
        raise SystemExit("full-DEV generation attempt already consumed; replacement requires an explicit amendment")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(
        json.dumps(
            {
                "report_version": "e14p-full-dev-generation-attempt-lock-v1",
                "status": "FULL_DEV_GENERATION_ATTEMPT_CONSUMED",
                "expected_fixed_calls": EXPECTED_CALLS,
                "expected_dev_groups": len(EXPECTED_GROUPS),
                "repeats_per_group": EXPECTED_REPEATS,
                "rerun_allowed": False,
                "contains_raw_output": False,
                "contains_private_oracle": False,
                "contains_private_scorer_rows": False,
                "validation_used": False,
                "locked_test_used": False
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return lock


def make_full_dev_apply_to_summary(original: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]):
    """Generalize only E14's historical six-call completeness cardinality to ten."""

    def apply(summary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
        upstream_status = summary.get("status")
        stage_before = summary.get("dev_action_escalation_calibration")
        upstream_stage_pass = bool(stage_before.get("passed")) if isinstance(stage_before, dict) else False

        result = original(summary, manifest)
        stage = result.get("dev_action_escalation_calibration")
        calls = stage.get("calls", []) if isinstance(stage, dict) else []
        parsed_calls = [c for c in calls if isinstance(c.get("parsed_output"), dict)]
        successful = [c for c in calls if c.get("error") is None]
        schema_valid = [bool(c.get("score", {}).get("schema_valid")) for c in calls]
        group_counts = Counter(str(c.get("group_id") or "") for c in calls)
        expected_group_counts = {group: EXPECTED_REPEATS for group in EXPECTED_GROUPS}

        complete = (
            len(calls) == EXPECTED_CALLS
            and len(parsed_calls) == EXPECTED_CALLS
            and len(successful) == EXPECTED_CALLS
            and len(schema_valid) == EXPECTED_CALLS
            and all(schema_valid)
            and dict(group_counts) == expected_group_counts
        )

        if isinstance(stage, dict):
            stage["successful_calls"] = len(successful)
            stage["parsed_outputs"] = len(parsed_calls)
            stage["scoreable_calls"] = sum(1 for item in schema_valid if item)
            stage["completeness_pass"] = complete
            stage["passed"] = upstream_stage_pass and complete
            stage["full_dev_cardinality_generalization_only"] = True

        result["status"] = (
            "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_PASS"
            if upstream_status == "E11_DEV_ONLY_INDEPENDENT_ACTION_AUTHORIZATION_CAPTURE_PASS" and complete
            else "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_NEEDS_REVIEW"
        )
        result["full_dev_upstream_e11_status"] = upstream_status
        result.setdefault("aggregate_metrics", {})["parsed_model_outputs_available"] = len(parsed_calls)
        result["aggregate_metrics"]["scoreable_calls"] = sum(1 for item in schema_valid if item)

        old_comp = result.get("e14_completeness")
        old_comp = old_comp if isinstance(old_comp, dict) else {}
        result["e14_completeness"] = {
            **old_comp,
            "required_calls": EXPECTED_CALLS,
            "required_parsed_outputs": EXPECTED_CALLS,
            "required_scoreable_calls": EXPECTED_CALLS,
            "actual_calls": len(calls),
            "actual_parsed_outputs": len(parsed_calls),
            "actual_scoreable_calls": sum(1 for item in schema_valid if item),
            "full_dev_required_group_count": len(EXPECTED_GROUPS),
            "full_dev_each_group_repeats_required": EXPECTED_REPEATS,
            "full_dev_group_cardinality_resolved": dict(group_counts) == expected_group_counts,
            "historical_quality_policy_changed": False,
            "fail_closed": not complete,
            "passed": complete,
        }
        return result

    return apply


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_manifest(args.manifest)
    if args.dev_repeats is not None and args.dev_repeats != EXPECTED_REPEATS:
        raise AssertionError(f"full-DEV repeats are frozen at {EXPECTED_REPEATS}")

    e14l.assert_frozen_configuration(dry_run=args.dry_run)
    e14l.schema.run_self_checks()
    effective_prompt = e14o.effective_system_prompt()

    lock: Path | None = None
    if not args.dry_run:
        lock = consume_real_attempt(args.out)

    saved_manifest = e11.E10G_MANIFEST
    saved_apply = e14_core.apply_to_summary
    saved_prompt = e14o.e10b.STRICT_E10B_SYSTEM_PROMPT
    e11.E10G_MANIFEST = args.manifest
    e14_core.apply_to_summary = make_full_dev_apply_to_summary(saved_apply)
    e14o.e10b.STRICT_E10B_SYSTEM_PROMPT = effective_prompt
    try:
        summary = e14l.run(args)
    finally:
        e11.E10G_MANIFEST = saved_manifest
        e14_core.apply_to_summary = saved_apply
        e14o.e10b.STRICT_E10B_SYSTEM_PROMPT = saved_prompt

    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    group_counts = Counter(str(c.get("group_id") or "") for c in calls)
    group_cardinality_ok = dict(group_counts) == {group: EXPECTED_REPEATS for group in EXPECTED_GROUPS}
    completeness = summary.get("e14_completeness")
    completeness = completeness if isinstance(completeness, dict) else {}
    parent_pass = summary.get("status") == "E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS"
    full_pass = (
        parent_pass
        and len(calls) == EXPECTED_CALLS
        and completeness.get("passed") is True
        and group_cardinality_ok
        and summary.get("scope", {}).get("validation_ran") is False
    )

    parent_status = summary.get("status")
    status_chain = {
        "e11": summary.get("full_dev_upstream_e11_status"),
        "e14": summary.get("parent_e14_capture_status"),
        "e14c": summary.get("parent_e14c_capture_status"),
        "e14d": summary.get("parent_e14d_capture_status"),
        "e14e": summary.get("parent_e14e_capture_status"),
        "e14f": summary.get("parent_e14f_capture_status"),
        "e14l": parent_status,
    }
    summary["report_version"] = "e14o-full-dev-five-group-capture-v1"
    summary["status"] = PASS_STATUS if full_pass else FAIL_STATUS
    summary["parent_e14l_status"] = parent_status
    summary["full_dev_status_chain"] = status_chain
    summary["full_dev_generation"] = {
        "candidate": "E14p-after-E14o-generation-before-E14n-v1.1-and-E14p-serialization",
        "coverage_change_only": True,
        "expected_dev_groups": len(EXPECTED_GROUPS),
        "observed_dev_groups": len(group_counts),
        "repeats_per_group": EXPECTED_REPEATS,
        "expected_fixed_calls": EXPECTED_CALLS,
        "observed_fixed_calls": len(calls),
        "each_group_exactly_two_calls": group_cardinality_ok,
        "model_changed": False,
        "prompt_changed_from_targeted_E14o": False,
        "reasoning_changed": False,
        "schema_changed": False,
        "completion_budget_changed": False,
        "historical_quality_policy_changed": False,
        "validation_ran": False,
        "locked_test_used": False,
        "private_oracle_used_by_model": False,
        "real_generation_attempt_consumed": not args.dry_run,
        "rerun_allowed": False if not args.dry_run else None,
        "attempt_lock_written": lock is not None,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    summary = run(args)
    full = summary.get("full_dev_generation", {})
    comp = summary.get("e14_completeness", {})
    agg = summary.get("aggregate_metrics", {})
    print(json.dumps({
        "status": summary.get("status"),
        "model": "openai/gpt-oss-120b",
        "reasoning_effort": "medium",
        "required_dev_groups": len(EXPECTED_GROUPS),
        "observed_dev_groups": full.get("observed_dev_groups"),
        "repeats_per_group": EXPECTED_REPEATS,
        "total_calls": agg.get("total_calls"),
        "parsed_model_outputs_available": agg.get("parsed_model_outputs_available"),
        "scoreable_calls": agg.get("scoreable_calls"),
        "completeness_pass": comp.get("passed"),
        "each_group_exactly_two_calls": full.get("each_group_exactly_two_calls"),
        "validation_ran": full.get("validation_ran"),
        "locked_test_used": full.get("locked_test_used"),
        "dry_run": args.dry_run,
        "real_generation_attempt_consumed": full.get("real_generation_attempt_consumed"),
        "rerun_allowed": full.get("rerun_allowed"),
        "private_oracle_used_by_model": full.get("private_oracle_used_by_model"),
        "status_chain": summary.get("full_dev_status_chain"),
    }, indent=2))
    return 0 if summary.get("status") == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
