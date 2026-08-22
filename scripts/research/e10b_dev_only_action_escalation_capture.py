#!/usr/bin/env python3
"""E10b DEV-only action/escalation calibration capture runner.

E10 improved evidence correctness on DEV, but action/escalation correctness
remained 0.0. This runner keeps the evidence-first policy and adds explicit
action/escalation calibration guidance without using VALIDATION or LOCKED_TEST.

The generated non-dry-run file contains fixed parsed model outputs for private
scorer use. Do not commit real non-dry-run outputs.
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

CAPTURE_PATH = Path(__file__).with_name("e8_capture_fixed_groq_outputs.py")
SPEC = importlib.util.spec_from_file_location("e8_capture", CAPTURE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e8_capture_fixed_groq_outputs.py")
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)
base = capture.base

STRICT_E10B_SYSTEM_PROMPT = """
You are an industrial maintenance agent candidate in a DEV-only action/escalation calibration iteration.
Use only the visible case packet and general API/tool contract knowledge already visible in the repository harness.
Do not claim access to hidden expected answers, evaluator gold, LOCKED_TEST, private trajectories, expected-path rows, or scorer oracles.

Return exactly one JSON object, with no Markdown, using this schema:
{
  "decision_class": "investigate_only|action_candidate|escalation_candidate|insufficient_evidence",
  "evidence_plan": ["explicit API/resource-level evidence references"],
  "should_take_action_now": true|false,
  "requires_human_escalation": true|false,
  "proposed_next_step": "concise next step with the next concrete tool/API action",
  "risk_notes": "concise safety/uncertainty notes",
  "trace_quality_self_check": {
    "uses_only_visible_packet": true,
    "no_locked_test": true,
    "no_gold_claim": true
  },
  "action_escalation_rubric": {
    "needs_more_evidence": true|false,
    "safe_to_act": true|false,
    "action_endpoint": "endpoint or none",
    "needs_human_escalation": true|false,
    "calibration_reason": "brief visible-evidence reason"
  }
}

Evidence policy:
- Preserve E10's evidence gain: evidence_plan must name concrete API/resource-level evidence, not generic phrases.
- Prefer: GET /users/me, GET /assets/{asset_id}, GET /assets/{asset_id}/analyses, GET /analyses/{analysis_id}, GET /assets/{asset_id}/baseline, GET /assets/{asset_id}/data-quality, GET /assets/{asset_id}/rms, GET /assets/{asset_id}/spectrum, GET /knowledge/search, GET /knowledge/{doc_id}.
- Include enough evidence steps to ground asset state, latest analysis, baseline/data quality, signal data, permissions and knowledge support.

Action calibration:
- Do not leave should_take_action_now=false merely because more evidence would be nice; if the visible packet already supports a concrete safe endpoint, choose action_candidate and set should_take_action_now=true.
- Set should_take_action_now=true only when action_escalation_rubric.safe_to_act=true and action_endpoint is one of: POST /analyses/{analysis_id}/reprocess, POST /analyses/{analysis_id}/request-specialist, POST /models/{model_id}/request-retraining, PATCH /assets/{asset_id}, POST /cases/{case_id}/escalate.
- Choose POST /analyses/{analysis_id}/reprocess when visible evidence indicates stale, failed, invalid, low-quality or incomplete analysis that can be reprocessed.
- Choose POST /models/{model_id}/request-retraining when visible evidence indicates model drift, stale baseline, repeated false positives/negatives or model-performance degradation.
- Choose PATCH /assets/{asset_id} only when visible evidence supports a metadata/status update and permission is sufficient.

Escalation calibration:
- Set requires_human_escalation=true when visible evidence indicates safety risk, severe fault, specialist-needed diagnosis, ambiguous but high-impact condition, missing permission for a needed action, or when the best endpoint is request-specialist/escalate.
- Use escalation_candidate when human/specialist handling is the primary next step.
- Do not escalate for generic uncertainty alone; escalate when uncertainty blocks safe action or impact/risk is material.

Consistency rules:
- If should_take_action_now=true, proposed_next_step must name the action endpoint and why visible evidence supports it.
- If requires_human_escalation=true, risk_notes must state the visible safety/severity/uncertainty/permission/specialist reason.
- If neither action nor escalation is supported, use investigate_only or insufficient_evidence and explain the missing evidence.
- Keep premature actions at zero: do not invent facts, ids, permissions, severity or hidden labels.
""".strip()

EVIDENCE_RESOURCE_HINTS = [
    "GET /users/me",
    "GET /assets/{asset_id}",
    "GET /assets/{asset_id}/analyses",
    "GET /analyses/{analysis_id}",
    "GET /assets/{asset_id}/baseline",
    "GET /assets/{asset_id}/data-quality",
    "GET /assets/{asset_id}/rms",
    "GET /assets/{asset_id}/spectrum",
    "GET /knowledge/search",
    "GET /knowledge/{doc_id}",
]

ACTION_ENDPOINTS = [
    "POST /analyses/{analysis_id}/reprocess",
    "POST /analyses/{analysis_id}/request-specialist",
    "POST /models/{model_id}/request-retraining",
    "PATCH /assets/{asset_id}",
    "POST /cases/{case_id}/escalate",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_dev_only_manifest(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    groups_by_split = base.split_groups(split_manifest)
    declared = manifest.get("representative_groups", {})
    if sorted(declared.keys()) != ["DEV"]:
        raise AssertionError("E10b manifest must declare DEV groups only")
    groups = set(declared.get("DEV", []))
    dev = groups_by_split.get("DEV", set())
    validation = groups_by_split.get("VALIDATION", set())
    locked = groups_by_split.get("LOCKED_TEST", set())
    if groups & validation:
        raise AssertionError(f"E10b selected VALIDATION groups for tuning: {sorted(groups & validation)}")
    if groups & locked:
        raise AssertionError(f"E10b selected LOCKED_TEST groups: {sorted(groups & locked)}")
    missing = sorted(groups - dev)
    if missing:
        raise AssertionError(f"E10b DEV groups missing from split manifest: {missing}")


def e10b_observation_packet(split_name: str, group_id: str, case_by_asset: dict[str, dict[str, Any]]) -> dict[str, Any]:
    packet = base.observation_packet(split_name, group_id, case_by_asset)
    packet["e10b_dev_only_calibration_policy"] = {
        "iteration_scope": "DEV_ONLY_ACTION_ESCALATION_CALIBRATION",
        "validation_tuning_forbidden": True,
        "validation_ran": False,
        "locked_test_forbidden": True,
        "required_evidence_resources": EVIDENCE_RESOURCE_HINTS,
        "supported_action_endpoints": ACTION_ENDPOINTS,
        "decision_checks_before_final_json": [
            "needs_more_evidence",
            "safe_to_act",
            "action_endpoint",
            "needs_human_escalation",
        ],
        "action_rule": "Choose action_candidate and should_take_action_now=true when visible evidence already supports a concrete safe endpoint.",
        "escalation_rule": "Choose escalation_candidate or requires_human_escalation=true when visible risk/severity/specialist uncertainty/permission blocking makes human handling necessary.",
        "negative_rule": "Use investigate_only or insufficient_evidence only when evidence is genuinely insufficient for a safe endpoint or escalation decision.",
    }
    return packet


def e10b_build_prompt(packet: dict[str, Any], repeat_index: int) -> str:
    return (
        "DEV-only action/escalation calibration capture. Do not use validation feedback. Return only JSON.\n"
        f"Repeat index: {repeat_index}\n"
        f"Visible packet SHA256: {base.stable_hash(packet)}\n"
        "Visible packet JSON:\n"
        f"{json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)}\n\n"
        "First build concrete evidence_plan entries. Then fill action_escalation_rubric. "
        "Finally set decision_class, should_take_action_now and requires_human_escalation consistently with that rubric. "
        "Do not use private expected paths, validation results or locked-test material."
    )


def e10b_dry_output(packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    output = {
        "decision_class": "escalation_candidate",
        "evidence_plan": [
            "GET /users/me to confirm permission and requester context",
            "GET /assets/{asset_id} to inspect asset identity, status, site and metadata",
            "GET /assets/{asset_id}/analyses then GET /analyses/{analysis_id} to inspect latest diagnosis evidence",
            "GET /assets/{asset_id}/baseline and GET /assets/{asset_id}/data-quality to compare expected behavior and data trustworthiness",
            "GET /assets/{asset_id}/rms and GET /assets/{asset_id}/spectrum to ground signal severity before action",
            "GET /knowledge/search to support diagnosis and specialist/escalation rationale",
        ],
        "should_take_action_now": True,
        "requires_human_escalation": True,
        "proposed_next_step": "If visible evidence supports it, use POST /analyses/{analysis_id}/request-specialist or POST /cases/{case_id}/escalate; otherwise continue evidence acquisition.",
        "risk_notes": "DEV-only dry run validates action/escalation rubric shape and benchmark boundary, not model quality.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": True,
            "action_endpoint": "POST /analyses/{analysis_id}/request-specialist",
            "needs_human_escalation": True,
            "calibration_reason": "Dry-run rubric example; not private-oracle-derived.",
        },
        "e10b_policy": "dev_only_action_escalation_calibration",
        "repeat_index": repeat_index,
        "packet_hash": base.stable_hash(packet),
    }
    return json.dumps(output), {"model": "dry_run_e10b_action_escalation", "usage": {}}


def call_model(prompt: str, timeout: int, dry_run: bool, packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    if dry_run:
        return e10b_dry_output(packet, repeat_index)
    original_system = base.SYSTEM_PROMPT
    try:
        base.SYSTEM_PROMPT = STRICT_E10B_SYSTEM_PROMPT
        return capture.call_groq(prompt, timeout)
    finally:
        base.SYSTEM_PROMPT = original_system


def execute_stage(*, groups: list[str], repeats: int, case_by_asset: dict[str, dict[str, Any]], timeout: int, dry_run: bool) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    latencies: list[float] = []
    delay = float(os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0"))
    for group_id in groups:
        packet = e10b_observation_packet("DEV", group_id, case_by_asset)
        packet_hash = base.stable_hash(packet)
        for repeat_index in range(repeats):
            if calls and delay > 0:
                time.sleep(delay)
            prompt = e10b_build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            error: str | None = None
            raw_output = ""
            provider_meta: dict[str, Any] = {}
            try:
                raw_output, provider_meta = call_model(prompt, timeout, dry_run, packet, repeat_index)
                trace_events.append("dry_run_output_generated" if dry_run else "model_called")
            except Exception as exc:  # noqa: BLE001 - captured for repeatability diagnostics
                error = str(exc)
                trace_events.append("model_call_failed")
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            parsed = base.extract_json_object(raw_output) if raw_output else None
            if raw_output:
                trace_events.append("output_parsed" if parsed is not None else "output_parse_failed")
            score = capture.score_output(parsed, raw_output or error or "")
            trace_events.append("output_scored")
            calls.append(
                {
                    "group_id": group_id,
                    "split": "DEV",
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
        "stage": "DEV_ACTION_ESCALATION_CALIBRATION",
        "split": "DEV",
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
        "calls": calls,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    if not isinstance(manifest, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("manifest and split manifest must be JSON objects")
    assert_dev_only_manifest(manifest, split_manifest)
    capture.assert_zero_cost_or_dry_run(args.dry_run)
    cases = base.load_agent_visible_cases(args.agent_input_cases)
    groups = list(manifest["representative_groups"]["DEV"])
    repeats = args.dev_repeats or int(manifest.get("repeats", {}).get("DEV_ACTION_ESCALATION_CALIBRATION", 2))
    dev_stage = execute_stage(groups=groups, repeats=repeats, case_by_asset=cases, timeout=args.timeout_seconds, dry_run=args.dry_run)
    all_calls = list(dev_stage["calls"])
    parsed_calls = [call for call in all_calls if isinstance(call.get("parsed_output"), dict)]
    status = "E10B_DEV_ONLY_ACTION_ESCALATION_CAPTURE_PASS" if dev_stage["passed"] else "E10B_DEV_ONLY_ACTION_ESCALATION_CAPTURE_NEEDS_REVIEW"
    latencies = [float(call.get("latency_ms", 0.0)) for call in all_calls]
    summary = {
        "report_version": "e10b-dev-only-action-escalation-capture-v1",
        "date": "2026-08-16",
        "status": status,
        "provider": "groq",
        "model": os.getenv("E8_GROQ_MODEL", capture.DEFAULT_MODEL) if not args.dry_run else "dry_run_e10b_action_escalation",
        "dry_run": args.dry_run,
        "purpose": "DEV-only fixed parsed outputs for action/escalation calibration scoring",
        "external_model_calls_made": not args.dry_run,
        "cost_usd": 0.0,
        "project_cost_limit_usd": 0,
        "zero_cost_confirmed_by_env": os.getenv("E8_CONFIRM_ZERO_COST") == "1" if not args.dry_run else False,
        "paid_models_enabled": False,
        "scope": {
            "allowed_training_splits": ["DEV"],
            "protected_splits": ["VALIDATION", "LOCKED_TEST"],
            "locked_test_accessed": False,
            "validation_used_for_tuning": False,
            "validation_ran": False,
        },
        "quality_policy_changes": manifest.get("candidate_policy_changes", {}),
        "gold_leakage_controls": {
            "model_prompt_receives_oracle": False,
            "private_expected_paths_in_prompt": False,
            "validation_feedback_in_prompt": False,
            "locked_test_forbidden_before_final": True,
            "outputs_hashed_before_scoring": all(call.get("output_hash") for call in parsed_calls),
        },
        "constants_preserved": manifest.get("constants_preserved", {}),
        "dev_action_escalation_calibration": dev_stage,
        "aggregate_metrics": {
            "total_calls": len(all_calls),
            "parsed_model_outputs_available": len(parsed_calls),
            "task_success_proxy": dev_stage["task_success_proxy"],
            "schema_valid_rate": dev_stage["schema_valid_rate"],
            "trace_completeness": dev_stage["trace_completeness"],
            "latency_avg_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
            "latency_p95_ms": max(latencies) if latencies else 0.0,
            "cost_usd": 0.0,
        },
        "e9_dev_only_next_command": "python scripts/research/e9_evaluator_side_scorer_v3.py --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json --split-manifest research/frozen/benchmark-split-v1.json --fixed-output-file <this-e10b-file> --oracle-file <private-eval/expected-paths.json> --out <e10b-dev-e9-summary.json> --include-rows",
        "do_not_commit_this_file": not args.dry_run,
        "full_remeasurement_policy": "Only rerun DEV+VALIDATION after this DEV-only candidate improves action/escalation without safety regressions.",
        "final_architecture_freeze": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10b-dev-only-action-escalation-calibration-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10b DEV-only capture shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10B_DEV_ONLY_ACTION_ESCALATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
