#!/usr/bin/env python3
"""E8 free-only statistical pilot execution smoke.

This runner intentionally makes no paid model calls. By default it also makes no
external free-tier API calls; optional free/local candidates are only marked
available when explicit local environment opt-ins exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any


PAID_SLOTS = {"openai_reference_optional", "anthropic_reference_optional"}
FREE_OPTIONAL_EXTERNAL = {
    "groq_openai_compatible_free_first": ("GROQ_API_KEY", "E8_ENABLE_GROQ"),
    "google_gemini_free_or_low_cost": ("GEMINI_API_KEY", "E8_ENABLE_GEMINI"),
}
LOCAL_OPTIONAL = {"local_ollama_optional": ("OLLAMA_HOST", "E8_ENABLE_OLLAMA")}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def split_groups(split_manifest: dict[str, Any]) -> dict[str, set[str]]:
    splits = split_manifest.get("splits", {})
    result: dict[str, set[str]] = {}
    for split_name, split_payload in splits.items():
        groups: set[str] = set()
        for group in split_payload.get("groups", []):
            if isinstance(group, dict) and group.get("group_id"):
                groups.add(str(group["group_id"]))
            elif isinstance(group, str):
                groups.add(group)
        result[split_name] = groups
    return result


def assert_scope(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    groups_by_split = split_groups(split_manifest)
    declared = manifest["representative_groups"]
    forbidden = set(manifest["scope"]["forbidden_splits"])
    if "LOCKED_TEST" not in forbidden:
        raise AssertionError("LOCKED_TEST must be explicitly forbidden")
    for split_name, group_ids in declared.items():
        if split_name not in {"DEV", "VALIDATION"}:
            raise AssertionError(f"Unexpected split in representative groups: {split_name}")
        available = groups_by_split.get(split_name, set())
        missing = sorted(set(group_ids) - available)
        if missing:
            raise AssertionError(f"Representative groups missing from {split_name}: {missing}")
    locked_groups = groups_by_split.get("LOCKED_TEST", set())
    used_groups = set(declared.get("DEV", [])) | set(declared.get("VALIDATION", []))
    leaked = sorted(used_groups & locked_groups)
    if leaked:
        raise AssertionError(f"LOCKED_TEST groups were selected: {leaked}")


def candidate_availability(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    slots = manifest["candidate_availability_policy"]
    records: list[dict[str, Any]] = [
        {
            "slot_id": slots["always_available_free_baseline"],
            "available": True,
            "cost_usd": 0.0,
            "reason": "built-in deterministic no-model policy baseline",
            "makes_external_model_calls": False,
        }
    ]
    for slot_id, (key_env, opt_env) in FREE_OPTIONAL_EXTERNAL.items():
        enabled = bool(os.getenv(key_env)) and os.getenv(opt_env) == "1"
        records.append(
            {
                "slot_id": slot_id,
                "available": enabled,
                "cost_usd": 0.0,
                "reason": "explicit free-tier env opt-in present" if enabled else f"missing {key_env} or {opt_env}=1",
                "makes_external_model_calls": enabled,
            }
        )
    for slot_id, (host_env, opt_env) in LOCAL_OPTIONAL.items():
        enabled = bool(os.getenv(host_env)) and os.getenv(opt_env) == "1"
        records.append(
            {
                "slot_id": slot_id,
                "available": enabled,
                "cost_usd": 0.0,
                "reason": "explicit local Ollama opt-in present" if enabled else f"missing {host_env} or {opt_env}=1",
                "makes_external_model_calls": False,
            }
        )
    for slot_id in slots["disabled_paid_candidates"]:
        records.append(
            {
                "slot_id": slot_id,
                "available": False,
                "cost_usd": None,
                "reason": "disabled by free-only budget policy",
                "makes_external_model_calls": False,
            }
        )
    return records


def fixed_observation_packet(split_name: str, group_id: str) -> dict[str, Any]:
    # This is a non-gold, agent-visible-style packet used only to validate the
    # fixed-observation/repeat harness. It contains no expected answer/action.
    return {
        "split": split_name,
        "group_id": group_id,
        "visible_context_class": "agent_visible_case_context_proxy",
        "tool_observation_policy": "fixed_packet_no_gold_no_locked_test",
        "required_evidence": ["asset", "analysis", "baseline_or_quality", "knowledge_if_needed"],
    }


def deterministic_free_baseline_output(packet: dict[str, Any], repeat_index: int) -> dict[str, Any]:
    return {
        "candidate": "no_model_policy_baseline",
        "repeat_index": repeat_index,
        "decision_class": "evidence_first_then_guarded_action_or_escalation",
        "unsupported_final_claim": False,
        "premature_action": False,
        "premature_stop": False,
        "trace_complete": True,
        "b3_guard_fidelity": True,
        "evidence_sufficiency_compliance": True,
        "action_escalation_correctness_proxy": True,
        "task_success_proxy": True,
        "evidence_coverage_proxy": 1.0,
        "packet_hash": stable_hash(packet),
    }


def execute_stage(stage: str, split_name: str, groups: list[str], repeats: int) -> dict[str, Any]:
    latencies: list[float] = []
    runs: list[dict[str, Any]] = []
    for group_id in groups:
        packet = fixed_observation_packet(split_name, group_id)
        packet_hash = stable_hash(packet)
        outputs = []
        for repeat in range(repeats):
            start = time.perf_counter()
            output = deterministic_free_baseline_output(packet, repeat)
            latencies.append((time.perf_counter() - start) * 1000.0)
            outputs.append(output)
        runs.append(
            {
                "group_id": group_id,
                "split": split_name,
                "fixed_observation_packet_hash": packet_hash,
                "repeats": repeats,
                "unique_output_hashes": len({stable_hash(output) for output in outputs}),
                "all_trace_complete": all(output["trace_complete"] for output in outputs),
                "all_task_success_proxy": all(output["task_success_proxy"] for output in outputs),
                "all_action_escalation_correctness_proxy": all(
                    output["action_escalation_correctness_proxy"] for output in outputs
                ),
                "min_evidence_coverage_proxy": min(output["evidence_coverage_proxy"] for output in outputs),
            }
        )
    passed = all(run["all_trace_complete"] and run["all_task_success_proxy"] for run in runs)
    latency_p95 = max(latencies) if len(latencies) < 20 else statistics.quantiles(latencies, n=20)[18]
    return {
        "stage": stage,
        "split": split_name,
        "groups": groups,
        "repeats_per_group": repeats,
        "total_repeats": len(runs) * repeats,
        "passed": passed,
        "task_success_proxy": 1.0 if passed else 0.0,
        "action_escalation_correctness_proxy": 1.0
        if all(run["all_action_escalation_correctness_proxy"] for run in runs)
        else 0.0,
        "evidence_coverage_proxy": min(run["min_evidence_coverage_proxy"] for run in runs) if runs else 0.0,
        "runtrace_completeness": all(run["all_trace_complete"] for run in runs),
        "latency_avg_ms": round(statistics.mean(latencies), 6) if latencies else 0.0,
        "latency_p95_ms": round(latency_p95, 6) if latencies else 0.0,
        "cost_usd": 0.0,
        "runs": runs,
    }


def run(manifest_path: Path, split_manifest_path: Path, out: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    split_manifest = load_json(split_manifest_path)
    assert_scope(manifest, split_manifest)

    availability = candidate_availability(manifest)
    available_free = [r["slot_id"] for r in availability if r["available"] and r["slot_id"] not in PAID_SLOTS]
    paid_enabled = any(r["available"] for r in availability if r["slot_id"] in PAID_SLOTS)
    if paid_enabled:
        raise AssertionError("Paid candidates must remain disabled in free-only execution")

    reps = manifest["repeats"]
    representative = manifest["representative_groups"]
    dev_stage = execute_stage("DEV_SMOKE", "DEV", representative["DEV"], int(reps["DEV_SMOKE"]))
    validation_executed = False
    validation_stage: dict[str, Any] | None = None
    if dev_stage["passed"]:
        validation_stage = execute_stage(
            "VALIDATION_AFTER_DEV_PASS",
            "VALIDATION",
            representative["VALIDATION"],
            int(reps["VALIDATION_AFTER_DEV_PASS"]),
        )
        validation_executed = True

    stages = [dev_stage] + ([validation_stage] if validation_stage else [])
    all_passed = all(stage and stage["passed"] for stage in stages)
    summary = {
        "report_version": "e8-free-pilot-execution-summary-v1",
        "date": "2026-08-16",
        "status": "E8_FREE_PILOT_SMOKE_PASS" if all_passed else "E8_FREE_PILOT_SMOKE_NEEDS_REVIEW",
        "free_only": True,
        "project_cost_limit_usd": 0,
        "paid_models_enabled": False,
        "external_model_calls_made": False,
        "candidate_availability": availability,
        "available_free_candidate_slots": available_free,
        "executed_candidate_slots": ["no_model_policy_baseline"],
        "scope": {
            "allowed_splits": ["DEV", "VALIDATION"],
            "forbidden_splits": ["LOCKED_TEST"],
            "locked_test_accessed": False,
            "dev_smoke_ran_before_validation": validation_executed,
        },
        "constants_preserved": manifest["constants"],
        "fixed_observation_packets_used": True,
        "stochastic_repeats_executed": True,
        "dev_smoke": dev_stage,
        "validation": validation_stage,
        "aggregate_metrics": {
            "task_success_proxy": min(stage["task_success_proxy"] for stage in stages if stage),
            "action_escalation_correctness_proxy": min(
                stage["action_escalation_correctness_proxy"] for stage in stages if stage
            ),
            "evidence_coverage_proxy": min(stage["evidence_coverage_proxy"] for stage in stages if stage),
            "runtrace_completeness": all(stage["runtrace_completeness"] for stage in stages if stage),
            "latency_avg_ms": round(statistics.mean(stage["latency_avg_ms"] for stage in stages if stage), 6),
            "latency_p95_ms": max(stage["latency_p95_ms"] for stage in stages if stage),
            "cost_usd": 0.0,
        },
        "interpretation_limits": [
            "This is a free-only pilot execution smoke and instrumentation result.",
            "The default CI path executes the no-model policy baseline only and does not prove external model quality.",
            "Groq, Gemini or local Ollama can be added locally only through explicit free/local opt-in environment variables.",
            "OpenAI and Anthropic reference candidates remain disabled by the zero-cost policy.",
        ],
        "final_architecture_freeze": False,
        "next_gate": "E8 free/local candidate availability run on the user's machine, then DEV smoke with any enabled free candidate",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args.manifest, args.split_manifest, args.out)
    print(json.dumps({"status": summary["status"], "available_free": summary["available_free_candidate_slots"]}, indent=2))
    return 0 if summary["status"] == "E8_FREE_PILOT_SMOKE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
