#!/usr/bin/env python3
"""E8 free-anywhere real model candidate runner.

This runner can call zero-cost remote providers only with explicit opt-in. It is
safe for CI because --dry-run makes no external calls and only validates scope,
configuration, prompt construction and summary shape.

It intentionally never reads evaluator-only gold and never uses LOCKED_TEST.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ALLOWED_PROVIDERS = {"groq", "gemini"}
PAID_PROVIDER_ENVS = {
    "E8_ENABLE_OPENAI",
    "E8_ENABLE_ANTHROPIC",
    "OPENAI_API_KEY_FOR_E8",
    "ANTHROPIC_API_KEY_FOR_E8",
}
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
DEFAULT_USER_AGENT = "academy-tractian-e8-free-anywhere-runner/1.1"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are an industrial maintenance agent candidate in a benchmark pilot.
Use only the visible case packet. Do not claim access to hidden expected answers,
evaluator gold, LOCKED_TEST, private trajectories or scorer oracles.
Return exactly one JSON object, with no Markdown, using this schema:
{
  "decision_class": "investigate_only|action_candidate|escalation_candidate|insufficient_evidence",
  "evidence_plan": ["short evidence/tool intent strings"],
  "should_take_action_now": true|false,
  "requires_human_escalation": true|false,
  "proposed_next_step": "concise next step",
  "risk_notes": "concise safety/uncertainty notes",
  "trace_quality_self_check": {
    "uses_only_visible_packet": true,
    "no_locked_test": true,
    "no_gold_claim": true
  }
}
Prefer evidence acquisition before actions. Only suggest action/escalation when the visible packet supports it.
""".strip()


def load_json(path: Path) -> dict[str, Any] | list[Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def split_groups(split_manifest: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for split_name, split_payload in (split_manifest.get("splits") or {}).items():
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
    forbidden = set(manifest["scope"]["forbidden_splits"])
    if "LOCKED_TEST" not in forbidden:
        raise AssertionError("LOCKED_TEST must be explicitly forbidden")
    declared = manifest["representative_groups"]
    for split_name in declared:
        if split_name not in {"DEV", "VALIDATION"}:
            raise AssertionError(f"Unexpected split: {split_name}")
    locked = groups_by_split.get("LOCKED_TEST", set())
    used = set(declared.get("DEV", [])) | set(declared.get("VALIDATION", []))
    leaked = sorted(used & locked)
    if leaked:
        raise AssertionError(f"LOCKED_TEST groups selected: {leaked}")
    for split_name, group_ids in declared.items():
        available = groups_by_split.get(split_name, set())
        missing = sorted(set(group_ids) - available)
        if missing:
            raise AssertionError(f"Representative groups missing from {split_name}: {missing}")


def assert_zero_cost_guard(provider: str, dry_run: bool) -> None:
    enabled_paid = sorted(name for name in PAID_PROVIDER_ENVS if os.getenv(name))
    if enabled_paid:
        raise AssertionError(f"Paid provider envs must stay disabled for E8: {enabled_paid}")
    if dry_run:
        return
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise AssertionError("Remote candidate execution requires E8_CONFIRM_ZERO_COST=1")
    if provider == "groq":
        if os.getenv("E8_ENABLE_GROQ") != "1" or not os.getenv("GROQ_API_KEY"):
            raise AssertionError("Groq run requires GROQ_API_KEY and E8_ENABLE_GROQ=1")
    elif provider == "gemini":
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if os.getenv("E8_ENABLE_GEMINI") != "1" or not key:
            raise AssertionError("Gemini run requires GEMINI_API_KEY or GOOGLE_API_KEY and E8_ENABLE_GEMINI=1")
    else:
        raise AssertionError(f"Unsupported provider: {provider}")


def collect_case_records(payload: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            records.extend(collect_case_records(item))
    elif isinstance(payload, dict):
        keys = set(payload.keys())
        if {"case_id", "asset_id"} & keys or {"ticket_id", "assetId"} & keys:
            records.append(payload)
        for value in payload.values():
            if isinstance(value, (dict, list)):
                records.extend(collect_case_records(value))
    return records


def find_asset_id(record: dict[str, Any]) -> str | None:
    for key in ("asset_id", "assetId", "asset", "assetID"):
        value = record.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for nested in ("id", "asset_id", "assetId"):
                if isinstance(value.get(nested), str):
                    return str(value[nested])
    return None


def trim_payload(payload: Any, limit: int = 10000) -> Any:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    if len(text) <= limit:
        return payload
    return {
        "truncated": True,
        "sha256": stable_hash(payload),
        "preview": text[:limit],
        "note": "payload preview truncated for provider prompt budget; no evaluator gold is included by this runner",
    }


def load_agent_visible_cases(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    raw = load_json(path)
    by_asset: dict[str, dict[str, Any]] = {}
    for record in collect_case_records(raw):
        asset_id = find_asset_id(record)
        if asset_id and asset_id not in by_asset:
            by_asset[asset_id] = record
    return by_asset


def observation_packet(split_name: str, group_id: str, case_by_asset: dict[str, dict[str, Any]]) -> dict[str, Any]:
    visible_case = case_by_asset.get(group_id)
    if visible_case:
        return {
            "split": split_name,
            "group_id": group_id,
            "visible_context_class": "agent_input_case_json_no_gold",
            "visible_case": trim_payload(visible_case),
            "forbidden": ["LOCKED_TEST", "eval/expected-paths.json", "docs/test-scenarios.md", "data/cases.parquet"],
            "required_behavior": "Plan evidence first; do not use evaluator-only gold; suggest action/escalation only if supported.",
        }
    return {
        "split": split_name,
        "group_id": group_id,
        "visible_context_class": "proxy_packet_no_agent_input_file_available",
        "required_evidence": ["asset", "analysis", "baseline_or_quality", "knowledge_if_needed"],
        "forbidden": ["LOCKED_TEST", "eval/expected-paths.json", "docs/test-scenarios.md", "data/cases.parquet"],
        "required_behavior": "Plan evidence first; do not use evaluator-only gold; suggest action/escalation only if supported.",
    }


def build_prompt(packet: dict[str, Any], repeat_index: int) -> str:
    return (
        "Evaluate the visible case packet below. Return only the requested JSON object.\n"
        f"Repeat index: {repeat_index}\n"
        f"Visible packet SHA256: {stable_hash(packet)}\n"
        "Visible packet JSON:\n"
        f"{json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True)}"
    )


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": os.getenv("E8_HTTP_USER_AGENT", DEFAULT_USER_AGENT),
        **headers,
    }
    req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:1000]}") from exc


def call_groq(prompt: str, timeout: int) -> tuple[str, dict[str, Any]]:
    model = os.getenv("E8_GROQ_MODEL", DEFAULT_GROQ_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(os.getenv("E8_MODEL_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("E8_MAX_OUTPUT_TOKENS", "700")),
        "response_format": {"type": "json_object"},
    }
    response = post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        payload,
        timeout,
    )
    content = response["choices"][0]["message"]["content"]
    return content, {"model": model, "usage": response.get("usage", {}), "raw_id": response.get("id")}


def call_gemini(prompt: str, timeout: int) -> tuple[str, dict[str, Any]]:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("Gemini key missing")
    model = os.getenv("E8_GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": float(os.getenv("E8_MODEL_TEMPERATURE", "0.2")),
            "maxOutputTokens": int(os.getenv("E8_MAX_OUTPUT_TOKENS", "700")),
            "responseMimeType": "application/json",
        },
    }
    response = post_json(url, {"x-goog-api-key": key}, payload, timeout)
    candidates = response.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    content = "".join(str(part.get("text", "")) for part in parts)
    return content, {"model": model, "usage": response.get("usageMetadata", {}), "raw_id": response.get("responseId")}


def dry_run_model_output(packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    output = {
        "decision_class": "investigate_only",
        "evidence_plan": ["inspect asset", "inspect latest analysis", "compare baseline or data quality", "search knowledge if needed"],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Collect required evidence before any action or escalation.",
        "risk_notes": "Dry-run output validates schema only and is not model-quality evidence.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "packet_hash": stable_hash(packet),
        "repeat_index": repeat_index,
    }
    return json.dumps(output), {"model": "dry_run_schema_validator", "usage": {}, "raw_id": None}


def extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def score_output(parsed: dict[str, Any] | None, raw_text: str) -> dict[str, Any]:
    if parsed is None:
        return {
            "json_valid": False,
            "schema_valid": False,
            "decision_class_valid": False,
            "evidence_plan_present": False,
            "no_locked_test_claim": "LOCKED_TEST" not in raw_text,
            "no_gold_claim": not any(term in raw_text.lower() for term in ("gold", "expected answer", "oracle")),
            "trace_self_check_ok": False,
            "task_success_proxy": False,
        }
    missing = sorted(REQUIRED_OUTPUT_KEYS - set(parsed.keys()))
    decision_valid = parsed.get("decision_class") in DECISION_CLASSES
    evidence = parsed.get("evidence_plan")
    evidence_ok = isinstance(evidence, list) and bool(evidence) and all(isinstance(item, str) for item in evidence)
    trace = parsed.get("trace_quality_self_check")
    trace_ok = isinstance(trace, dict) and trace.get("uses_only_visible_packet") is True and trace.get("no_locked_test") is True and trace.get("no_gold_claim") is True
    no_locked = "LOCKED_TEST" not in json.dumps(parsed, ensure_ascii=False)
    no_gold = not any(term in json.dumps(parsed, ensure_ascii=False).lower() for term in ("gold", "expected answer", "oracle"))
    schema_valid = not missing and decision_valid and evidence_ok and isinstance(parsed.get("should_take_action_now"), bool) and isinstance(parsed.get("requires_human_escalation"), bool)
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
    }


def call_candidate(provider: str, prompt: str, timeout: int, dry_run: bool, packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    if dry_run:
        return dry_run_model_output(packet, repeat_index)
    if provider == "groq":
        return call_groq(prompt, timeout)
    if provider == "gemini":
        return call_gemini(prompt, timeout)
    raise ValueError(f"unsupported provider: {provider}")


def execute_stage(
    *,
    provider: str,
    stage: str,
    split_name: str,
    groups: list[str],
    repeats: int,
    case_by_asset: dict[str, dict[str, Any]],
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    latencies: list[float] = []
    calls: list[dict[str, Any]] = []
    for group_id in groups:
        packet = observation_packet(split_name, group_id, case_by_asset)
        packet_hash = stable_hash(packet)
        for repeat_index in range(repeats):
            prompt = build_prompt(packet, repeat_index)
            trace_events = ["prompt_built"]
            start = time.perf_counter()
            error: str | None = None
            raw_output = ""
            provider_meta: dict[str, Any] = {}
            try:
                raw_output, provider_meta = call_candidate(provider, prompt, timeout, dry_run, packet, repeat_index)
                trace_events.append("model_called" if not dry_run else "dry_run_output_generated")
            except Exception as exc:  # noqa: BLE001 - recorded for benchmark summary
                error = str(exc)
                trace_events.append("model_call_failed")
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed)
            parsed = extract_json_object(raw_output) if raw_output else None
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
                    "prompt_hash": stable_hash(prompt),
                    "provider_meta": provider_meta,
                    "latency_ms": round(elapsed, 3),
                    "error": error,
                    "score": score,
                    "trace_events": trace_events,
                    "trace_complete": all(event in trace_events for event in ("prompt_built", "output_scored")) and ("model_called" in trace_events or "dry_run_output_generated" in trace_events),
                    "output_hash": stable_hash(parsed) if parsed is not None else None,
                }
            )
    successful = [call for call in calls if call["error"] is None]
    task_success = [call["score"]["task_success_proxy"] for call in calls]
    schema_valid = [call["score"].get("schema_valid", False) for call in calls]
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
    provider = args.provider
    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(f"provider must be one of {sorted(ALLOWED_PROVIDERS)}")
    manifest = load_json(args.manifest)
    split_manifest = load_json(args.split_manifest)
    assert isinstance(manifest, dict)
    assert isinstance(split_manifest, dict)
    assert_scope(manifest, split_manifest)
    assert_zero_cost_guard(provider, args.dry_run)
    cases = load_agent_visible_cases(args.agent_input_cases)
    reps = manifest["repeats"]
    groups = manifest["representative_groups"]
    dev_stage = execute_stage(
        provider=provider,
        stage="DEV_SMOKE",
        split_name="DEV",
        groups=list(groups["DEV"]),
        repeats=int(reps["DEV_SMOKE"]),
        case_by_asset=cases,
        timeout=args.timeout_seconds,
        dry_run=args.dry_run,
    )
    validation_stage = None
    if dev_stage["passed"]:
        validation_stage = execute_stage(
            provider=provider,
            stage="VALIDATION_AFTER_DEV_PASS",
            split_name="VALIDATION",
            groups=list(groups["VALIDATION"]),
            repeats=int(reps["VALIDATION_AFTER_DEV_PASS"]),
            case_by_asset=cases,
            timeout=args.timeout_seconds,
            dry_run=args.dry_run,
        )
    stages = [dev_stage] + ([validation_stage] if validation_stage else [])
    status = "E8_FREE_ANYWHERE_MODEL_RUN_PASS" if validation_stage and all(stage["passed"] for stage in stages if stage) else "E8_FREE_ANYWHERE_MODEL_RUN_NEEDS_REVIEW"
    summary = {
        "report_version": "e8-free-anywhere-real-model-run-summary-v1",
        "date": "2026-08-16",
        "status": status,
        "provider": provider,
        "dry_run": args.dry_run,
        "external_model_calls_made": not args.dry_run,
        "free_anywhere_scope": True,
        "project_cost_limit_usd": 0,
        "cost_usd": 0.0,
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
        "constants_preserved": manifest["constants_preserved"],
        "dev_smoke": dev_stage,
        "validation": validation_stage,
        "aggregate_metrics": {
            "task_success_proxy": min(stage["task_success_proxy"] for stage in stages if stage),
            "schema_valid_rate": min(stage["schema_valid_rate"] for stage in stages if stage),
            "trace_completeness": all(stage["trace_completeness"] for stage in stages if stage),
            "latency_avg_ms": round(statistics.mean(stage["latency_avg_ms"] for stage in stages if stage), 3),
            "latency_p95_ms": max(stage["latency_p95_ms"] for stage in stages if stage),
            "cost_usd": 0.0,
        },
        "interpretation_limits": [
            "This run scores model-output structure and safety/trace proxy metrics without leaking evaluator-only gold.",
            "Task-success remains a proxy until a scorer maps outputs to private oracles outside the model prompt.",
            "No model/provider or final architecture is frozen by this run.",
        ],
        "final_architecture_freeze": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--provider", choices=sorted(ALLOWED_PROVIDERS), required=True)
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--dry-run", action="store_true", help="Validate runner without external model calls")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({"status": summary["status"], "provider": summary["provider"], "dry_run": summary["dry_run"]}, indent=2))
    return 0 if summary["status"] == "E8_FREE_ANYWHERE_MODEL_RUN_PASS" or args.dry_run else 1


if __name__ == "__main__":
    raise SystemExit(main())
