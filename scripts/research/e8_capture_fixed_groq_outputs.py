#!/usr/bin/env python3
"""Capture fixed Groq outputs for the E9 evaluator-side scorer.

This script is the missing bridge between E8 model execution and E9 private
semantic scoring. The public E8 result stored in the repository is sanitized and
contains hashes/aggregates, so E9 correctly reports `fixed_calls_consumed = 0`
or no real score when only that file is used.

This local/private capture runner:

- calls only Groq as the current leading zero-cost candidate;
- requires `E8_CONFIRM_ZERO_COST=1`, `E8_ENABLE_GROQ=1`, and `GROQ_API_KEY`
  unless `--dry-run` is used;
- runs DEV before VALIDATION;
- keeps LOCKED_TEST blocked;
- stores parsed model outputs under `parsed_output` for E9;
- hashes every fixed output before scorer use;
- never reads evaluator-only gold or private oracles.

Do not commit the generated fixed-output file. Pass it to
`scripts/research/e9_evaluator_side_scorer.py` together with the private
DEV/VALIDATION oracle file.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MODULE_PATH = Path(__file__).with_name("e8_free_anywhere_model_runner.py")
SPEC = importlib.util.spec_from_file_location("e8_base_runner", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load base E8 runner")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)

DEFAULT_MODEL = "llama-3.1-8b-instant"
DEFAULT_USER_AGENT = "academy-tractian-e8-fixed-groq-capture/1.0"
DECISION_CLASSES = {"investigate_only", "action_candidate", "escalation_candidate", "insufficient_evidence"}
REQUIRED_OUTPUT_KEYS = {
    "decision_class",
    "evidence_plan",
    "should_take_action_now",
    "requires_human_escalation",
    "proposed_next_step",
    "risk_notes",
    "trace_quality_self_check",
}
PAID_PROVIDER_ENVS = {
    "E8_ENABLE_OPENAI",
    "E8_ENABLE_ANTHROPIC",
    "OPENAI_API_KEY_FOR_E8",
    "ANTHROPIC_API_KEY_FOR_E8",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_zero_cost_or_dry_run(dry_run: bool) -> None:
    enabled_paid = sorted(name for name in PAID_PROVIDER_ENVS if os.getenv(name))
    if enabled_paid:
        raise AssertionError(f"Paid provider envs must stay disabled for E8/E9 free capture: {enabled_paid}")
    if dry_run:
        return
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("Groq capture requires E8_CONFIRM_ZERO_COST=1")
    if os.getenv("E8_ENABLE_GROQ") != "1":
        raise AssertionError("Groq capture requires E8_ENABLE_GROQ=1")
    if not os.getenv("GROQ_API_KEY"):
        raise AssertionError("Groq capture requires GROQ_API_KEY")


def string_values(payload: Any) -> list[str]:
    values: list[str] = []
    if isinstance(payload, str):
        values.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            values.extend(string_values(item))
    elif isinstance(payload, dict):
        for value in payload.values():
            values.extend(string_values(value))
    return values


def value_text(payload: Any) -> str:
    return "\n".join(string_values(payload)).lower()


def score_output(parsed: dict[str, Any] | None, raw_text: str) -> dict[str, Any]:
    if parsed is None:
        raw_lower = raw_text.lower()
        return {
            "json_valid": False,
            "schema_valid": False,
            "decision_class_valid": False,
            "evidence_plan_present": False,
            "no_locked_test_claim": "locked_test" not in raw_lower,
            "no_gold_claim": not any(term in raw_lower for term in ("evaluator gold", "expected answer", "scorer oracle", "hidden oracle")),
            "trace_self_check_ok": False,
            "task_success_proxy": False,
            "scoring_version": "fixed_capture_values_only",
        }
    missing = sorted(REQUIRED_OUTPUT_KEYS - set(parsed.keys()))
    decision_valid = parsed.get("decision_class") in DECISION_CLASSES
    evidence = parsed.get("evidence_plan")
    evidence_ok = isinstance(evidence, list) and bool(evidence) and all(isinstance(item, str) for item in evidence)
    trace = parsed.get("trace_quality_self_check")
    trace_ok = (
        isinstance(trace, dict)
        and trace.get("uses_only_visible_packet") is True
        and trace.get("no_locked_test") is True
        and trace.get("no_gold_claim") is True
    )
    text_values = value_text(parsed)
    no_locked = "locked_test" not in text_values
    no_gold = not any(term in text_values for term in ("evaluator gold", "expected answer", "scorer oracle", "hidden oracle"))
    schema_valid = (
        not missing
        and decision_valid
        and evidence_ok
        and isinstance(parsed.get("should_take_action_now"), bool)
        and isinstance(parsed.get("requires_human_escalation"), bool)
    )
    return {
        "json_valid": True,
        "schema_valid": schema_valid,
        "missing_keys": missing,
        "decision_class_valid": decision_valid,
        "evidence_plan_present": evidence_ok,
        "no_locked_test_claim": no_locked,
        "no_gold_claim": no_gold,
        "trace_self_check_ok": trace_ok,
        "task_success_proxy": bool(schema_valid and trace_ok and no_locked and no_gold),
        "scoring_version": "fixed_capture_values_only",
    }


def is_retryable(status_code: int | None, message: str) -> bool:
    lowered = message.lower()
    if status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
        return True
    if status_code == 403 and "1010" in lowered:
        return True
    return any(fragment in lowered for fragment in ("winerror 10054", "connection reset", "temporarily unavailable"))


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    attempts = int(os.getenv("E8_PROVIDER_MAX_ATTEMPTS", "5"))
    base_sleep = float(os.getenv("E8_PROVIDER_RETRY_BASE_SECONDS", "5"))
    data = json.dumps(payload).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": os.getenv("E8_HTTP_USER_AGENT", DEFAULT_USER_AGENT),
        **headers,
    }
    last_error = "provider request failed"
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {body[:1000]}"
            retryable = is_retryable(exc.code, last_error)
        except Exception as exc:  # noqa: BLE001 - benchmark captures provider failure text
            last_error = str(exc)
            retryable = is_retryable(None, last_error)
        if attempt >= attempts or not retryable:
            break
        time.sleep(base_sleep * attempt)
    raise RuntimeError(last_error)


def call_groq(prompt: str, timeout: int) -> tuple[str, dict[str, Any]]:
    model = os.getenv("E8_GROQ_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": base.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(os.getenv("E8_MODEL_TEMPERATURE", "0")),
        "max_tokens": int(os.getenv("E8_MAX_OUTPUT_TOKENS", "350")),
        "response_format": {"type": "json_object"},
    }
    response = post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        payload,
        timeout,
    )
    content = response["choices"][0]["message"]["content"]
    return content, {"model": model, "usage": response.get("usage", {})}


def dry_output(packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    output = {
        "decision_class": "investigate_only",
        "evidence_plan": ["inspect asset", "inspect latest analysis", "compare baseline or data quality", "search knowledge if needed"],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Collect required evidence before any action or escalation.",
        "risk_notes": "Dry-run fixed capture validates schema only and is not model-quality evidence.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "packet_hash": base.stable_hash(packet),
        "repeat_index": repeat_index,
    }
    return json.dumps(output), {"model": "dry_run_fixed_capture", "usage": {}}


def execute_stage(
    *,
    stage: str,
    split_name: str,
    groups: list[str],
    repeats: int,
    case_by_asset: dict[str, dict[str, Any]],
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    latencies: list[float] = []
    delay = float(os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0"))
    for group_id in groups:
        packet = base.observation_packet(split_name, group_id, case_by_asset)
        packet_hash = base.stable_hash(packet)
        for repeat_index in range(repeats):
            if calls and delay > 0:
                time.sleep(delay)
            prompt = base.build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            error: str | None = None
            raw_output = ""
            provider_meta: dict[str, Any] = {}
            try:
                if dry_run:
                    raw_output, provider_meta = dry_output(packet, repeat_index)
                    trace_events.append("dry_run_output_generated")
                else:
                    raw_output, provider_meta = call_groq(prompt, timeout)
                    trace_events.append("model_called")
            except Exception as exc:  # noqa: BLE001 - captured for repeatability diagnostics
                error = str(exc)
                trace_events.append("model_call_failed")
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            parsed = base.extract_json_object(raw_output) if raw_output else None
            if raw_output:
                trace_events.append("output_parsed" if parsed is not None else "output_parse_failed")
            score = score_output(parsed, raw_output or error or "")
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
        "stage": stage,
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
        "calls": calls,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    if not isinstance(manifest, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("manifest and split manifest must be JSON objects")
    base.assert_scope(manifest, split_manifest)
    assert_zero_cost_or_dry_run(args.dry_run)
    cases = base.load_agent_visible_cases(args.agent_input_cases)
    reps = manifest.get("repeats", {})
    groups = manifest["representative_groups"]
    dev_repeats = args.dev_repeats or int(reps.get("DEV_SMOKE", 2))
    validation_repeats = args.validation_repeats or int(reps.get("VALIDATION_AFTER_DEV_PASS", 3))
    dev_stage = execute_stage(
        stage="DEV_SMOKE",
        split_name="DEV",
        groups=list(groups["DEV"]),
        repeats=dev_repeats,
        case_by_asset=cases,
        timeout=args.timeout_seconds,
        dry_run=args.dry_run,
    )
    validation_stage = None
    if dev_stage["passed"]:
        validation_stage = execute_stage(
            stage="VALIDATION_AFTER_DEV_PASS",
            split_name="VALIDATION",
            groups=list(groups["VALIDATION"]),
            repeats=validation_repeats,
            case_by_asset=cases,
            timeout=args.timeout_seconds,
            dry_run=args.dry_run,
        )
    stages = [dev_stage] + ([validation_stage] if validation_stage else [])
    status = "E8_FIXED_GROQ_OUTPUT_CAPTURE_PASS" if validation_stage and all(stage["passed"] for stage in stages if stage) else "E8_FIXED_GROQ_OUTPUT_CAPTURE_NEEDS_REVIEW"
    all_calls = [call for stage in stages if stage for call in stage["calls"]]
    parsed_calls = [call for call in all_calls if isinstance(call.get("parsed_output"), dict)]
    summary = {
        "report_version": "e8-fixed-groq-output-capture-v1",
        "date": "2026-08-16",
        "status": status,
        "provider": "groq",
        "model": os.getenv("E8_GROQ_MODEL", DEFAULT_MODEL) if not args.dry_run else "dry_run_fixed_capture",
        "dry_run": args.dry_run,
        "purpose": "fixed_parsed_outputs_for_e9_private_scorer",
        "external_model_calls_made": not args.dry_run,
        "cost_usd": 0.0,
        "project_cost_limit_usd": 0,
        "zero_cost_confirmed_by_env": os.getenv("E8_CONFIRM_ZERO_COST") == "1" if not args.dry_run else False,
        "paid_models_enabled": False,
        "agent_input_cases_used": args.agent_input_cases is not None,
        "agent_input_cases_matched_assets": sorted(cases.keys()),
        "scope": {
            "allowed_splits": ["DEV", "VALIDATION"],
            "forbidden_splits": ["LOCKED_TEST"],
            "locked_test_accessed": False,
            "dev_smoke_ran_before_validation": validation_stage is not None,
        },
        "gold_leakage_controls": {
            "model_prompt_receives_oracle": False,
            "scorer_reads_oracle_after_outputs_fixed": True,
            "outputs_hashed_before_scoring": all(call.get("output_hash") for call in parsed_calls),
            "evaluator_only_paths_blocked_from_model": True,
            "locked_test_forbidden_before_final": True,
        },
        "constants_preserved": manifest.get("constants_preserved", {}),
        "dev_smoke": dev_stage,
        "validation": validation_stage,
        "aggregate_metrics": {
            "total_calls": len(all_calls),
            "parsed_model_outputs_available": len(parsed_calls),
            "task_success_proxy": min(stage["task_success_proxy"] for stage in stages if stage),
            "schema_valid_rate": min(stage["schema_valid_rate"] for stage in stages if stage),
            "trace_completeness": all(stage["trace_completeness"] for stage in stages if stage),
            "latency_avg_ms": round(statistics.mean(stage["latency_avg_ms"] for stage in stages if stage), 3),
            "latency_p95_ms": max(stage["latency_p95_ms"] for stage in stages if stage),
            "cost_usd": 0.0,
        },
        "e9_next_command": "python scripts/research/e9_evaluator_side_scorer.py --manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json --fixed-output-file <this-file> --oracle-file <private-dev-validation-oracle.json> --out <e9-private-task-quality-summary.json> --include-rows",
        "do_not_commit_this_file": not args.dry_run,
        "final_architecture_freeze": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e8-free-anywhere-real-candidate-run-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--validation-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate capture shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({"status": summary["status"], "total_calls": summary["aggregate_metrics"]["total_calls"], "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"], "dry_run": summary["dry_run"]}, indent=2))
    return 0 if args.dry_run or summary["status"] == "E8_FIXED_GROQ_OUTPUT_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
