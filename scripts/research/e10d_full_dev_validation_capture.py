#!/usr/bin/env python3
"""E10d full DEV+VALIDATION fixed capture runner.

This runner remeasures the E10d candidate after the DEV-only gate passed. It
runs DEV and VALIDATION as measurement splits only, keeps LOCKED_TEST blocked,
and applies the same visible-output escalation consistency guard used in E10d.

The generated non-dry-run file contains fixed parsed outputs for private scorer
use. Do not commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any

E10D_PATH = Path(__file__).with_name("e10d_dev_only_escalation_consistency_guard.py")
SPEC = importlib.util.spec_from_file_location("e10d_guard", E10D_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10d_dev_only_escalation_consistency_guard.py")
e10d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10d)
e10c = e10d.e10c
e10b = e10d.e10b
base = e10d.base


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def split_groups(split_manifest: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for split_name, split_payload in (split_manifest.get("splits") or {}).items():
        groups: set[str] = set()
        for group in split_payload.get("groups", []):
            if isinstance(group, dict) and group.get("group_id"):
                groups.add(str(group["group_id"]))
            elif isinstance(group, str):
                groups.add(group)
        result[str(split_name)] = groups
    return result


def assert_full_measurement_scope(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    declared = manifest.get("representative_groups", {})
    if sorted(declared.keys()) != ["DEV", "VALIDATION"]:
        raise AssertionError("E10d full manifest must declare exactly DEV and VALIDATION groups")
    groups_by_split = split_groups(split_manifest)
    locked = groups_by_split.get("LOCKED_TEST", set())
    for split_name in ("DEV", "VALIDATION"):
        declared_groups = set(map(str, declared.get(split_name, [])))
        expected_split_groups = groups_by_split.get(split_name, set())
        if not declared_groups:
            raise AssertionError(f"E10d full manifest has no {split_name} groups")
        missing = sorted(declared_groups - expected_split_groups)
        if missing:
            raise AssertionError(f"E10d {split_name} groups missing from split manifest: {missing}")
        locked_hits = sorted(declared_groups & locked)
        if locked_hits:
            raise AssertionError(f"E10d full manifest selected LOCKED_TEST groups: {locked_hits}")
    scope = manifest.get("scope", {})
    if scope.get("validation_used_for_tuning") is not False:
        raise AssertionError("E10d full remeasurement must keep validation_used_for_tuning=false")
    if scope.get("locked_test_accessed") is not False:
        raise AssertionError("E10d full remeasurement must keep locked_test_accessed=false")


def e10d_full_observation_packet(split_name: str, group_id: str, case_by_asset: dict[str, dict[str, Any]]) -> dict[str, Any]:
    packet = e10b.e10b_observation_packet(split_name, group_id, case_by_asset)
    packet["e10d_full_remeasurement_policy"] = {
        "iteration_scope": "FULL_DEV_VALIDATION_REMEASUREMENT",
        "split": split_name,
        "validation_is_measurement_only": split_name == "VALIDATION",
        "validation_tuning_forbidden": True,
        "locked_test_forbidden": True,
        "visible_output_guard_enabled_after_generation": True,
        "guard_uses_private_oracle": False,
        "guard_uses_validation_feedback": False,
        "guard_uses_locked_test": False,
    }
    return packet


def call_model(prompt: str, timeout: int, dry_run: bool, packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    original_prompt = e10b.STRICT_E10B_SYSTEM_PROMPT
    original_dry = e10b.e10b_dry_output
    try:
        e10b.STRICT_E10B_SYSTEM_PROMPT = e10c.STRICT_E10C_SYSTEM_PROMPT
        e10b.e10b_dry_output = e10c.e10c_dry_output
        return e10b.call_model(prompt, timeout, dry_run, packet, repeat_index)
    finally:
        e10b.STRICT_E10B_SYSTEM_PROMPT = original_prompt
        e10b.e10b_dry_output = original_dry


def execute_split(
    *,
    split_name: str,
    groups: list[str],
    repeats: int,
    case_by_asset: dict[str, dict[str, Any]],
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    latencies: list[float] = []
    guard_rows: list[dict[str, Any]] = []
    delay = float(os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0"))
    for group_id in groups:
        packet = e10d_full_observation_packet(split_name, group_id, case_by_asset)
        packet_hash = base.stable_hash(packet)
        for repeat_index in range(repeats):
            if calls and delay > 0:
                time.sleep(delay)
            prompt = e10b.e10b_build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            error: str | None = None
            raw_output = ""
            provider_meta: dict[str, Any] = {}
            try:
                raw_output, provider_meta = call_model(prompt, timeout, dry_run, packet, repeat_index)
                trace_events.append("dry_run_output_generated" if dry_run else "model_called")
            except Exception as exc:  # noqa: BLE001 - preserved for repeatability diagnostics
                error = str(exc)
                trace_events.append("model_call_failed")
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            parsed = base.extract_json_object(raw_output) if raw_output else None
            if raw_output:
                trace_events.append("output_parsed" if parsed is not None else "output_parse_failed")
            if isinstance(parsed, dict):
                guarded, guard_meta = e10d.apply_visible_escalation_guard_to_output(parsed)
                parsed = guarded
                trace_events.append("visible_escalation_consistency_guard_applied" if guard_meta["applied"] else "visible_escalation_consistency_guard_checked")
                guard_rows.append(
                    {
                        "group_id": group_id,
                        "split": split_name,
                        "repeat_index": repeat_index,
                        "applied": guard_meta["applied"],
                        "reason": guard_meta["reason"],
                        "output_hash_after_guard": base.stable_hash(parsed),
                    }
                )
            score = e10b.capture.score_output(parsed, raw_output or error or "")
            trace_events.append("output_scored")
            calls.append(
                {
                    "group_id": group_id,
                    "split": split_name,
                    "repeat_index": repeat_index,
                    "fixed_observation_packet_hash": packet_hash,
                    "prompt_hash": base.stable_hash(prompt),
                    "provider_meta": provider_meta,
                    "latency_ms": round(elapsed, 3),
                    "error": error,
                    "score": score,
                    "trace_events": trace_events,
                    "trace_complete": all(event in trace_events for event in ("prompt_built", "output_scored"))
                    and ("model_called" in trace_events or "dry_run_output_generated" in trace_events),
                    "parsed_output": parsed,
                    "output_hash": base.stable_hash(parsed) if parsed is not None else None,
                }
            )
    successful = [call for call in calls if call["error"] is None]
    schema_valid = [call["score"].get("schema_valid", False) for call in calls]
    task_success = [call["score"].get("task_success_proxy", False) for call in calls]
    no_locked = [call["score"].get("no_locked_test_claim", False) for call in calls]
    trace_complete = [call["trace_complete"] for call in calls]
    latency_p95 = max(latencies) if len(latencies) < 20 else statistics.quantiles(latencies, n=20)[18]
    passed = bool(calls) and len(successful) == len(calls) and all(schema_valid) and all(no_locked) and all(trace_complete)
    return {
        "stage": f"{split_name}_E10D_FULL_REMEASUREMENT",
        "split": split_name,
        "groups": groups,
        "repeats_per_group": repeats,
        "total_calls": len(calls),
        "successful_calls": len(successful),
        "passed": passed,
        "task_success_proxy": round(sum(1 for item in task_success if item) / len(task_success), 4) if task_success else 0.0,
        "schema_valid_rate": round(sum(1 for item in schema_valid if item) / len(schema_valid), 4) if schema_valid else 0.0,
        "no_locked_test_claim_rate": round(sum(1 for item in no_locked if item) / len(no_locked), 4) if no_locked else 0.0,
        "trace_completeness": all(trace_complete) if trace_complete else False,
        "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
        "latency_p95_ms": round(latency_p95, 3) if latencies else 0.0,
        "cost_usd": 0.0,
        "visible_escalation_consistency_guard": {
            "enabled": True,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
            "total_outputs_checked": len(guard_rows),
            "outputs_changed": sum(1 for row in guard_rows if row["applied"]),
            "rows": guard_rows,
        },
        "calls": calls,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    if not isinstance(manifest, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("manifest and split manifest must be JSON objects")
    assert_full_measurement_scope(manifest, split_manifest)
    e10b.capture.assert_zero_cost_or_dry_run(args.dry_run)
    cases = base.load_agent_visible_cases(args.agent_input_cases)

    groups_by_split = manifest["representative_groups"]
    repeats_by_split = manifest.get("repeats", {})
    dev_stage = execute_split(
        split_name="DEV",
        groups=list(groups_by_split["DEV"]),
        repeats=args.dev_repeats or int(repeats_by_split.get("DEV", 2)),
        case_by_asset=cases,
        timeout=args.timeout_seconds,
        dry_run=args.dry_run,
    )
    validation_stage = execute_split(
        split_name="VALIDATION",
        groups=list(groups_by_split["VALIDATION"]),
        repeats=args.validation_repeats or int(repeats_by_split.get("VALIDATION", 3)),
        case_by_asset=cases,
        timeout=args.timeout_seconds,
        dry_run=args.dry_run,
    )
    all_calls = list(dev_stage["calls"]) + list(validation_stage["calls"])
    parsed_calls = [call for call in all_calls if isinstance(call.get("parsed_output"), dict)]
    latencies = [float(call.get("latency_ms", 0.0)) for call in all_calls]
    status = (
        "E10D_FULL_DEV_VALIDATION_CAPTURE_PASS"
        if dev_stage["passed"] and validation_stage["passed"]
        else "E10D_FULL_DEV_VALIDATION_CAPTURE_NEEDS_REVIEW"
    )
    guard_rows = dev_stage["visible_escalation_consistency_guard"]["rows"] + validation_stage["visible_escalation_consistency_guard"]["rows"]
    summary = {
        "report_version": "e10d-full-dev-validation-capture-v1",
        "date": "2026-08-16",
        "status": status,
        "provider": "groq",
        "model": os.getenv("E8_GROQ_MODEL", e10b.capture.DEFAULT_MODEL) if not args.dry_run else "dry_run_e10d_full_dev_validation",
        "dry_run": args.dry_run,
        "purpose": "Full DEV+VALIDATION fixed parsed outputs for E10d private remeasurement",
        "external_model_calls_made": not args.dry_run,
        "cost_usd": 0.0,
        "project_cost_limit_usd": 0,
        "zero_cost_confirmed_by_env": os.getenv("E8_CONFIRM_ZERO_COST") == "1" if not args.dry_run else False,
        "paid_models_enabled": False,
        "scope": {
            "measurement_splits": ["DEV", "VALIDATION"],
            "validation_used_for_tuning": False,
            "validation_ran": True,
            "locked_test_accessed": False,
            "forbidden_splits": ["LOCKED_TEST"],
        },
        "quality_policy_changes": manifest.get("candidate_policy_changes_under_remeasurement", {}),
        "gold_leakage_controls": {
            "model_prompt_receives_oracle": False,
            "guard_receives_oracle": False,
            "private_expected_paths_in_prompt": False,
            "validation_feedback_in_prompt": False,
            "locked_test_forbidden_before_final": True,
            "outputs_hashed_before_scoring": all(call.get("output_hash") for call in parsed_calls),
        },
        "constants_preserved": manifest.get("constants_preserved", {}),
        "dev_e10d_full_remeasurement": dev_stage,
        "validation_e10d_full_remeasurement": validation_stage,
        "visible_escalation_consistency_guard": {
            "enabled": True,
            "uses_private_oracle": False,
            "uses_validation_feedback": False,
            "uses_locked_test": False,
            "total_outputs_checked": len(guard_rows),
            "outputs_changed": sum(1 for row in guard_rows if row["applied"]),
            "rows": guard_rows,
        },
        "aggregate_metrics": {
            "total_calls": len(all_calls),
            "parsed_model_outputs_available": len(parsed_calls),
            "task_success_proxy": round(sum(1 for call in all_calls if call.get("score", {}).get("task_success_proxy")) / len(all_calls), 4) if all_calls else 0.0,
            "schema_valid_rate": round(sum(1 for call in all_calls if call.get("score", {}).get("schema_valid")) / len(all_calls), 4) if all_calls else 0.0,
            "trace_completeness": all(call.get("trace_complete") for call in all_calls) if all_calls else False,
            "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
            "latency_p95_ms": max(latencies) if latencies else 0.0,
            "cost_usd": 0.0,
        },
        "e9_full_next_command": "python scripts/research/e9_evaluator_side_scorer_v3.py --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json --split-manifest research/frozen/benchmark-split-v1.json --fixed-output-file <this-e10d-full-file> --oracle-file <private-eval/expected-paths.json> --out <e10d-full-e9-summary.json> --include-rows",
        "do_not_commit_this_file": not args.dry_run,
        "final_architecture_freeze": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10d-full-dev-validation-remeasurement-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--validation-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate full DEV+VALIDATION E10d capture shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
        "guard_outputs_checked": summary["visible_escalation_consistency_guard"]["total_outputs_checked"],
        "guard_outputs_changed": summary["visible_escalation_consistency_guard"]["outputs_changed"],
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10D_FULL_DEV_VALIDATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
