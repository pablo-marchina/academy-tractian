#!/usr/bin/env python3
"""E10 DEV-only Groq quality-improvement capture runner.

This runner is a DEV-only iteration harness. It does not access VALIDATION for
tuning and never accesses LOCKED_TEST. It modifies only the model-facing policy
for a new fixed-output capture run: evidence must be explicit and API/resource
level before action/escalation decisions.

The generated file is private/local fixed model output for scorer use. Do not
commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import statistics
from pathlib import Path
from typing import Any

CAPTURE_PATH = Path(__file__).with_name("e8_capture_fixed_groq_outputs.py")
SPEC = importlib.util.spec_from_file_location("e8_capture", CAPTURE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e8_capture_fixed_groq_outputs.py")
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)
base = capture.base

STRICT_DEV_SYSTEM_PROMPT = """
You are an industrial maintenance agent candidate in a DEV-only quality-improvement iteration.
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
  }
}

Evidence policy:
- The evidence_plan must name concrete evidence resources, not generic phrases.
- Prefer these visible contract resources when relevant: GET /users/me, GET /assets/{asset_id}, GET /assets/{asset_id}/analyses, GET /analyses/{analysis_id}, GET /assets/{asset_id}/baseline, GET /assets/{asset_id}/data-quality, GET /assets/{asset_id}/rms, GET /assets/{asset_id}/spectrum, GET /knowledge/search, GET /knowledge/{doc_id}.
- Include at least four evidence steps before any action/escalation unless the visible packet is explicitly insufficient.
- If evidence is missing or ambiguous, use decision_class="insufficient_evidence" or "investigate_only" and keep should_take_action_now=false.

Action calibration:
- Set should_take_action_now=true only when the visible packet strongly supports one concrete action endpoint and no missing evidence blocks it.
- Valid action candidates include POST /analyses/{analysis_id}/reprocess, POST /analyses/{analysis_id}/request-specialist, POST /models/{model_id}/request-retraining, PATCH /assets/{asset_id}, or POST /cases/{case_id}/escalate.
- Prefer action_candidate for reprocess/retraining/patch only with direct evidence of stale, invalid, failed, low-quality, drifted, or explicitly updateable state.
- Prefer escalation_candidate or request-specialist when there is safety risk, severe fault, unclear diagnosis after evidence, missing permission, or specialist-needed uncertainty.
- Avoid premature actions. Evidence first; action second.
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

ACTION_RESOURCE_HINTS = [
    "POST /analyses/{analysis_id}/reprocess",
    "POST /analyses/{analysis_id}/request-specialist",
    "POST /models/{model_id}/request-retraining",
    "PATCH /assets/{asset_id}",
    "POST /cases/{case_id}/escalate",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def e10_observation_packet(split_name: str, group_id: str, case_by_asset: dict[str, dict[str, Any]]) -> dict[str, Any]:
    packet = base.observation_packet(split_name, group_id, case_by_asset)
    packet["e10_dev_only_quality_policy"] = {
        "iteration_scope": "DEV_ONLY",
        "validation_tuning_forbidden": True,
        "locked_test_forbidden": True,
        "required_evidence_resources": EVIDENCE_RESOURCE_HINTS,
        "supported_action_resources": ACTION_RESOURCE_HINTS,
        "decision_gate": "Do not choose action/escalation unless visible evidence supports it after explicit resource-level evidence acquisition.",
        "insufficient_evidence_rule": "If any required asset, analysis, baseline, quality, RMS, spectrum, permission, or knowledge evidence is missing, choose investigate_only or insufficient_evidence.",
    }
    return packet


def e10_build_prompt(packet: dict[str, Any], repeat_index: int) -> str:
    return (
        "DEV-only quality-improvement capture. Do not use validation feedback. Return only JSON.\n"
        f"Repeat index: {repeat_index}\n"
        f"Visible packet SHA256: {base.stable_hash(packet)}\n"
        "Visible packet JSON:\n"
        f"{json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)}\n\n"
        "Before deciding, make evidence_plan concrete: cite API/resource names and what each checks. "
        "Then set action/escalation booleans only if the visible packet makes the action safe and supported."
    )


def e10_dry_output(packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    output = {
        "decision_class": "investigate_only",
        "evidence_plan": [
            "GET /users/me to confirm permission and requester context",
            "GET /assets/{asset_id} to inspect asset identity, status, site and metadata",
            "GET /assets/{asset_id}/analyses then GET /analyses/{analysis_id} to inspect latest diagnosis evidence",
            "GET /assets/{asset_id}/baseline and GET /assets/{asset_id}/data-quality to compare expected behavior and trustworthiness",
            "GET /assets/{asset_id}/rms and GET /assets/{asset_id}/spectrum to ground vibration or signal claims",
            "GET /knowledge/search to support diagnosis or uncertainty before action",
        ],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Collect resource-level evidence first; do not execute action until evidence supports one endpoint.",
        "risk_notes": "DEV-only dry run validates E10 capture shape and evidence policy, not model quality.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "e10_policy": "dev_only_evidence_first_action_calibration",
        "repeat_index": repeat_index,
        "packet_hash": base.stable_hash(packet),
    }
    return json.dumps(output), {"model": "dry_run_e10_dev_quality", "usage": {}}


def assert_dev_only_manifest(manifest: dict[str, Any], split_manifest: dict[str, Any]) -> None:
    groups_by_split = base.split_groups(split_manifest)
    declared = manifest.get("representative_groups", {})
    if sorted(declared.keys()) != ["DEV"]:
        raise AssertionError("E10 iteration manifest must declare DEV groups only")
    locked = groups_by_split.get("LOCKED_TEST", set())
    validation = groups_by_split.get("VALIDATION", set())
    dev = groups_by_split.get("DEV", set())
    groups = set(declared.get("DEV", []))
    if groups & locked:
        raise AssertionError(f"E10 selected LOCKED_TEST groups: {sorted(groups & locked)}")
    if groups & validation:
        raise AssertionError(f"E10 selected VALIDATION groups for tuning: {sorted(groups & validation)}")
    missing = sorted(groups - dev)
    if missing:
        raise AssertionError(f"E10 DEV groups missing from split manifest: {missing}")


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    if not isinstance(manifest, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("manifest and split manifest must be JSON objects")
    assert_dev_only_manifest(manifest, split_manifest)
    capture.assert_zero_cost_or_dry_run(args.dry_run)

    original_system = base.SYSTEM_PROMPT
    original_packet = base.observation_packet
    original_build_prompt = base.build_prompt
    original_dry_output = capture.dry_output
    base.SYSTEM_PROMPT = STRICT_DEV_SYSTEM_PROMPT
    base.observation_packet = e10_observation_packet
    base.build_prompt = e10_build_prompt
    capture.dry_output = e10_dry_output
    try:
        cases = base.load_agent_visible_cases(args.agent_input_cases)
        groups = list(manifest["representative_groups"]["DEV"])
        repeats = args.dev_repeats or int(manifest.get("repeats", {}).get("DEV_QUALITY_ITERATION", 2))
        dev_stage = capture.execute_stage(
            stage="DEV_QUALITY_ITERATION",
            split_name="DEV",
            groups=groups,
            repeats=repeats,
            case_by_asset=cases,
            timeout=args.timeout_seconds,
            dry_run=args.dry_run,
        )
    finally:
        base.SYSTEM_PROMPT = original_system
        base.observation_packet = original_packet
        base.build_prompt = original_build_prompt
        capture.dry_output = original_dry_output

    all_calls = list(dev_stage["calls"])
    parsed_calls = [call for call in all_calls if isinstance(call.get("parsed_output"), dict)]
    status = "E10_DEV_ONLY_GROQ_QUALITY_CAPTURE_PASS" if dev_stage["passed"] else "E10_DEV_ONLY_GROQ_QUALITY_CAPTURE_NEEDS_REVIEW"
    latencies = [float(call.get("latency_ms", 0.0)) for call in all_calls]
    summary = {
        "report_version": "e10-dev-only-groq-quality-capture-v1",
        "date": "2026-08-16",
        "status": status,
        "provider": "groq",
        "model": os.getenv("E8_GROQ_MODEL", capture.DEFAULT_MODEL) if not args.dry_run else "dry_run_e10_dev_quality",
        "dry_run": args.dry_run,
        "purpose": "DEV-only fixed parsed outputs for quality-improvement scoring",
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
        "dev_quality_iteration": dev_stage,
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
        "e9_dev_only_next_command": "python scripts/research/e9_evaluator_side_scorer_v3.py --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json --split-manifest research/frozen/benchmark-split-v1.json --fixed-output-file <this-e10-file> --oracle-file <private-eval/expected-paths.json> --out <e10-dev-e9-summary.json> --include-rows",
        "do_not_commit_this_file": not args.dry_run,
        "validation_rerun_policy": "Only rerun VALIDATION after a DEV candidate is selected and frozen; do not tune on validation metrics.",
        "final_architecture_freeze": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10-dev-only-quality-improvement-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate DEV-only capture shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10_DEV_ONLY_GROQ_QUALITY_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
