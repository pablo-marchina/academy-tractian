#!/usr/bin/env python3
"""E10e full DEV+VALIDATION fixed capture runner.

This runner remeasures the E10e candidate after the DEV-only safety gate passed.
It runs DEV and VALIDATION as measurement splits only, keeps LOCKED_TEST blocked,
and applies the E10d visible escalation guard plus the E10e visible premature-
action safety guard.

The generated non-dry-run file contains fixed parsed outputs for private scorer
use. Do not commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from pathlib import Path
from typing import Any

E10D_FULL_PATH = Path(__file__).with_name("e10d_full_dev_validation_capture.py")
E10E_PATH = Path(__file__).with_name("e10e_dev_only_premature_action_guard.py")

SPEC_D_FULL = importlib.util.spec_from_file_location("e10d_full_capture", E10D_FULL_PATH)
if SPEC_D_FULL is None or SPEC_D_FULL.loader is None:
    raise RuntimeError("failed to load e10d_full_dev_validation_capture.py")
e10d_full = importlib.util.module_from_spec(SPEC_D_FULL)
SPEC_D_FULL.loader.exec_module(e10d_full)

SPEC_E = importlib.util.spec_from_file_location("e10e_guard", E10E_PATH)
if SPEC_E is None or SPEC_E.loader is None:
    raise RuntimeError("failed to load e10e_dev_only_premature_action_guard.py")
e10e = importlib.util.module_from_spec(SPEC_E)
SPEC_E.loader.exec_module(e10e)
base = e10e.base


def apply_e10e_guard_to_stage(stage: dict[str, Any]) -> dict[str, Any]:
    calls = stage.get("calls", []) if isinstance(stage.get("calls", []), list) else []
    guard_rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded, guard_meta = e10e.apply_premature_action_guard_to_output(output)
        call["parsed_output"] = guarded
        call["output_hash"] = base.stable_hash(guarded)
        call["score"] = e10e.e10d.e10b.capture.score_output(guarded, json.dumps(guarded, ensure_ascii=False))
        call.setdefault("trace_events", []).append(
            "visible_premature_action_safety_guard_applied" if guard_meta["applied"] else "visible_premature_action_safety_guard_checked"
        )
        guard_rows.append(
            {
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "applied": guard_meta["applied"],
                "reason": guard_meta["reason"],
                "output_hash_after_guard": call.get("output_hash"),
            }
        )
    schema_valid = [call.get("score", {}).get("schema_valid", False) for call in calls]
    task_success = [call.get("score", {}).get("task_success_proxy", False) for call in calls]
    no_locked = [call.get("score", {}).get("no_locked_test_claim", False) for call in calls]
    trace_complete = [bool(call.get("trace_complete")) for call in calls]
    successful = [call for call in calls if call.get("error") is None]
    split_name = str(stage.get("split", "UNKNOWN"))
    stage["stage"] = f"{split_name}_E10E_FULL_REMEASUREMENT"
    stage["successful_calls"] = len(successful)
    stage["passed"] = bool(calls) and len(successful) == len(calls) and all(schema_valid) and all(no_locked) and all(trace_complete)
    stage["task_success_proxy"] = round(sum(1 for item in task_success if item) / len(task_success), 4) if task_success else 0.0
    stage["schema_valid_rate"] = round(sum(1 for item in schema_valid if item) / len(schema_valid), 4) if schema_valid else 0.0
    stage["no_locked_test_claim_rate"] = round(sum(1 for item in no_locked if item) / len(no_locked), 4) if no_locked else 0.0
    stage["trace_completeness"] = all(trace_complete) if trace_complete else False
    stage["visible_premature_action_safety_guard"] = {
        "enabled": True,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(guard_rows),
        "outputs_changed": sum(1 for row in guard_rows if row["applied"]),
        "rows": guard_rows,
    }
    return stage


def all_calls_from_summary(summary: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for key in ("dev_e10e_full_remeasurement", "validation_e10e_full_remeasurement"):
        stage = summary.get(key)
        if isinstance(stage, dict) and isinstance(stage.get("calls"), list):
            calls.extend(stage["calls"])
    return calls


def apply_e10e_full_guard(summary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    dev_stage = summary.pop("dev_e10d_full_remeasurement")
    validation_stage = summary.pop("validation_e10d_full_remeasurement")
    summary["dev_e10e_full_remeasurement"] = apply_e10e_guard_to_stage(dev_stage)
    summary["validation_e10e_full_remeasurement"] = apply_e10e_guard_to_stage(validation_stage)

    all_calls = all_calls_from_summary(summary)
    parsed_calls = [call for call in all_calls if isinstance(call.get("parsed_output"), dict)]
    latencies = [float(call.get("latency_ms", 0.0)) for call in all_calls]
    safety_rows = (
        summary["dev_e10e_full_remeasurement"]["visible_premature_action_safety_guard"]["rows"]
        + summary["validation_e10e_full_remeasurement"]["visible_premature_action_safety_guard"]["rows"]
    )
    status = (
        "E10E_FULL_DEV_VALIDATION_CAPTURE_PASS"
        if summary["dev_e10e_full_remeasurement"]["passed"] and summary["validation_e10e_full_remeasurement"]["passed"]
        else "E10E_FULL_DEV_VALIDATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["report_version"] = "e10e-full-dev-validation-capture-v1"
    summary["status"] = status
    summary["purpose"] = "Full DEV+VALIDATION fixed parsed outputs for E10e private remeasurement"
    summary["quality_policy_changes"] = manifest.get("candidate_policy_changes_under_remeasurement", {})
    summary["scope"] = {
        "measurement_splits": ["DEV", "VALIDATION"],
        "validation_used_for_tuning": False,
        "validation_ran": True,
        "locked_test_accessed": False,
        "forbidden_splits": ["LOCKED_TEST"],
    }
    summary["gold_leakage_controls"] = {
        **summary.get("gold_leakage_controls", {}),
        "model_prompt_receives_oracle": False,
        "escalation_guard_receives_oracle": False,
        "premature_action_guard_receives_oracle": False,
        "validation_feedback_in_prompt_or_guard": False,
        "locked_test_forbidden_before_final": True,
        "outputs_hashed_before_scoring": all(call.get("output_hash") for call in parsed_calls),
    }
    summary["visible_premature_action_safety_guard"] = {
        "enabled": True,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(safety_rows),
        "outputs_changed": sum(1 for row in safety_rows if row["applied"]),
        "rows": safety_rows,
    }
    summary["aggregate_metrics"] = {
        "total_calls": len(all_calls),
        "parsed_model_outputs_available": len(parsed_calls),
        "task_success_proxy": round(sum(1 for call in all_calls if call.get("score", {}).get("task_success_proxy")) / len(all_calls), 4) if all_calls else 0.0,
        "schema_valid_rate": round(sum(1 for call in all_calls if call.get("score", {}).get("schema_valid")) / len(all_calls), 4) if all_calls else 0.0,
        "trace_completeness": all(call.get("trace_complete") for call in all_calls) if all_calls else False,
        "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
        "latency_p95_ms": max(latencies) if latencies else 0.0,
        "cost_usd": 0.0,
    }
    summary["e9_full_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e10e-full-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e10e-full-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise AssertionError("manifest must be a JSON object")
    summary = e10d_full.run(args)
    summary = apply_e10e_full_guard(summary, manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10e-full-dev-validation-remeasurement-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--validation-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10e full remeasurement shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    guard = summary.get("visible_premature_action_safety_guard", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "guard_outputs_checked": guard.get("total_outputs_checked"),
        "guard_outputs_changed": guard.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10E_FULL_DEV_VALIDATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
