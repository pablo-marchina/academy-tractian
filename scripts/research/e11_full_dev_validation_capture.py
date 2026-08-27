#!/usr/bin/env python3
"""E11 full DEV+VALIDATION fixed capture runner.

This runner remeasures the E11 independent action-authorization policy after
DEV-only acceptance. It runs DEV and VALIDATION as measurement splits only,
keeps LOCKED_TEST blocked, and never gives private expected paths, evaluator
labels, validation feedback, or LOCKED_TEST material to the model or policy.

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

E10G_FULL_PATH = Path(__file__).with_name("e10g_full_dev_validation_capture.py")
E11_PATH = Path(__file__).with_name("e11_dev_only_independent_action_authorization.py")

SPEC_G_FULL = importlib.util.spec_from_file_location("e10g_full_capture", E10G_FULL_PATH)
if SPEC_G_FULL is None or SPEC_G_FULL.loader is None:
    raise RuntimeError("failed to load e10g_full_dev_validation_capture.py")
e10g_full = importlib.util.module_from_spec(SPEC_G_FULL)
SPEC_G_FULL.loader.exec_module(e10g_full)

SPEC_11 = importlib.util.spec_from_file_location("e11_policy", E11_PATH)
if SPEC_11 is None or SPEC_11.loader is None:
    raise RuntimeError("failed to load e11_dev_only_independent_action_authorization.py")
e11 = importlib.util.module_from_spec(SPEC_11)
SPEC_11.loader.exec_module(e11)
base = e11.base


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_e11_policy_to_stage(stage: dict[str, Any]) -> dict[str, Any]:
    calls = stage.get("calls", []) if isinstance(stage.get("calls", []), list) else []
    policy_rows: list[dict[str, Any]] = []
    for call in calls:
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guarded, policy_meta = e11.apply_authorization_to_output(call)
        call["parsed_output"] = guarded
        call["output_hash"] = base.stable_hash(guarded)
        call["score"] = e11.e10g.e10e.e10d.e10b.capture.score_output(guarded, json.dumps(guarded, ensure_ascii=False))
        call.setdefault("trace_events", []).append(
            "independent_action_authorization_blocked" if policy_meta["applied"] else "independent_action_authorization_checked"
        )
        policy_rows.append(
            {
                "group_id": call.get("group_id"),
                "split": call.get("split"),
                "repeat_index": call.get("repeat_index"),
                "authorized": policy_meta.get("authorized"),
                "applied": policy_meta.get("applied"),
                "reason": policy_meta.get("reason"),
                "action_class": policy_meta.get("action_class"),
                "endpoint": policy_meta.get("endpoint"),
                "evidence_families": policy_meta.get("evidence_families"),
                "output_hash_after_policy": call.get("output_hash"),
            }
        )
    schema_valid = [call.get("score", {}).get("schema_valid", False) for call in calls]
    task_success = [call.get("score", {}).get("task_success_proxy", False) for call in calls]
    no_locked = [call.get("score", {}).get("no_locked_test_claim", False) for call in calls]
    trace_complete = [bool(call.get("trace_complete")) for call in calls]
    successful = [call for call in calls if call.get("error") is None]
    split_name = str(stage.get("split", "UNKNOWN"))
    stage["stage"] = f"{split_name}_E11_FULL_REMEASUREMENT"
    stage["successful_calls"] = len(successful)
    stage["passed"] = bool(calls) and len(successful) == len(calls) and all(schema_valid) and all(no_locked) and all(trace_complete)
    stage["task_success_proxy"] = round(sum(1 for item in task_success if item) / len(task_success), 4) if task_success else 0.0
    stage["schema_valid_rate"] = round(sum(1 for item in schema_valid if item) / len(schema_valid), 4) if schema_valid else 0.0
    stage["no_locked_test_claim_rate"] = round(sum(1 for item in no_locked if item) / len(no_locked), 4) if no_locked else 0.0
    stage["trace_completeness"] = all(trace_complete) if trace_complete else False
    stage["independent_action_authorization_policy"] = {
        "enabled": True,
        "uses_model_safe_to_act_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(policy_rows),
        "outputs_changed": sum(1 for row in policy_rows if row["applied"]),
        "rows": policy_rows,
    }
    return stage


def all_calls_from_summary(summary: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for key in ("dev_e11_full_remeasurement", "validation_e11_full_remeasurement"):
        stage = summary.get(key)
        if isinstance(stage, dict) and isinstance(stage.get("calls"), list):
            calls.extend(stage["calls"])
    return calls


def apply_e11_full_policy(summary: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    dev_stage = summary.pop("dev_e10g_full_remeasurement")
    validation_stage = summary.pop("validation_e10g_full_remeasurement")
    summary["dev_e11_full_remeasurement"] = apply_e11_policy_to_stage(dev_stage)
    summary["validation_e11_full_remeasurement"] = apply_e11_policy_to_stage(validation_stage)

    all_calls = all_calls_from_summary(summary)
    parsed_calls = [call for call in all_calls if isinstance(call.get("parsed_output"), dict)]
    latencies = [float(call.get("latency_ms", 0.0)) for call in all_calls]
    policy_rows = (
        summary["dev_e11_full_remeasurement"]["independent_action_authorization_policy"]["rows"]
        + summary["validation_e11_full_remeasurement"]["independent_action_authorization_policy"]["rows"]
    )
    status = (
        "E11_FULL_DEV_VALIDATION_CAPTURE_PASS"
        if summary["dev_e11_full_remeasurement"]["passed"] and summary["validation_e11_full_remeasurement"]["passed"]
        else "E11_FULL_DEV_VALIDATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["report_version"] = "e11-full-dev-validation-capture-v1"
    summary["status"] = status
    summary["purpose"] = "Full DEV+VALIDATION fixed parsed outputs for E11 private remeasurement"
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
        "balanced_safety_action_guard_receives_oracle": False,
        "independent_action_authorization_receives_oracle": False,
        "validation_feedback_in_prompt_or_policy": False,
        "locked_test_forbidden_before_final": True,
        "outputs_hashed_before_scoring": all(call.get("output_hash") for call in parsed_calls),
    }
    summary["independent_action_authorization_policy"] = {
        "enabled": True,
        "uses_model_safe_to_act_as_sufficient": False,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "total_outputs_checked": len(policy_rows),
        "outputs_changed": sum(1 for row in policy_rows if row["applied"]),
        "rows": policy_rows,
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
        "--fixed-output-file <this-e11-full-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e11-full-e9-summary.json> --include-rows"
    )
    summary["do_not_commit_this_file"] = not bool(summary.get("dry_run"))
    summary["final_architecture_freeze"] = False
    return summary


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise AssertionError("manifest must be a JSON object")
    summary = e10g_full.run(args)
    summary = apply_e11_full_policy(summary, manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e11-full-dev-validation-remeasurement-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--validation-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E11 full remeasurement shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    policy = summary.get("independent_action_authorization_policy", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "policy_outputs_checked": policy.get("total_outputs_checked"),
        "policy_outputs_changed": policy.get("outputs_changed"),
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E11_FULL_DEV_VALIDATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
