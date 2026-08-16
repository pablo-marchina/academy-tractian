#!/usr/bin/env python3
"""E9 evaluator-side scorer v2 for TRACTIAN expected-paths.json.

This scorer consumes fixed parsed model outputs and maps the private
`eval/expected-paths.json` format to fixed output groups by local-only asset
mentions. It never sends oracle/gold text to a model and does not print raw
expected paths, notes, trajectories, answers, or labels.

Input oracle shape discovered locally:
[
  {"id": ..., "ticket_id": ..., "root_question": ..., "mode": ..., "expected_path": [...]},
  ...
]

The adapter builds per-asset private oracles only for fixed-output groups and
reports sanitized counts/booleans.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

ALLOWED_SPLITS = {"DEV", "VALIDATION"}
FORBIDDEN_SPLITS = {"LOCKED_TEST"}
DECISION_CLASSES = {"investigate_only", "action_candidate", "escalation_candidate", "insufficient_evidence"}
ASSET_RE = re.compile(r"\basset_[A-Za-z0-9]+\b")
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9_/-]{5,}")
STOPWORDS = {
    "asset", "assets", "analysis", "analyses", "baseline", "case", "cases", "data",
    "evidence", "expected", "gold", "oracle", "path", "private", "question", "root",
    "scenario", "step", "ticket", "using", "with", "without", "before", "after",
    "context", "current", "should", "could", "would", "there", "their", "about",
}
SENSITIVE_OUTPUT_TERMS = ("evaluator gold", "expected answer", "hidden oracle", "private oracle")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def text_values(payload: Any) -> list[str]:
    values: list[str] = []
    if isinstance(payload, str):
        values.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            values.extend(text_values(item))
    elif isinstance(payload, dict):
        for value in payload.values():
            values.extend(text_values(value))
    return values


def normalize_text(payload: Any) -> str:
    return "\n".join(text_values(payload)).lower()


def collect_calls(payload: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "calls" and isinstance(value, list):
                calls.extend(item for item in value if isinstance(item, dict))
            elif isinstance(value, (dict, list)):
                calls.extend(collect_calls(value))
    elif isinstance(payload, list):
        for item in payload:
            calls.extend(collect_calls(item))
    return calls


def output_payload(call: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("parsed_output", "model_output", "output", "response"):
        value = call.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None
    return None


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


def assert_fixed_scope(fixed_summary: dict[str, Any], calls: list[dict[str, Any]], split_manifest: dict[str, Any]) -> None:
    scope = fixed_summary.get("scope", {}) if isinstance(fixed_summary, dict) else {}
    if scope.get("locked_test_accessed") is True:
        raise AssertionError("fixed output summary reports LOCKED_TEST access")
    locked_groups = split_groups(split_manifest).get("LOCKED_TEST", set())
    for call in calls:
        split = call.get("split")
        group_id = str(call.get("group_id"))
        if split in FORBIDDEN_SPLITS or group_id in locked_groups:
            raise AssertionError(f"LOCKED_TEST fixed output present: {group_id}")
        if split is not None and split not in ALLOWED_SPLITS:
            raise AssertionError(f"unexpected split in fixed outputs: {split}")


def private_terms(payload: Any, max_terms: int = 24) -> list[str]:
    text = normalize_text(payload)
    terms: list[str] = []
    seen: set[str] = set()
    for token in TOKEN_RE.findall(text):
        token = token.lower().strip("-_/.,:;()[]{}")
        if not token or token.startswith("asset_") or token in STOPWORDS or token.isdigit():
            continue
        if token not in seen:
            seen.add(token)
            terms.append(token)
        if len(terms) >= max_terms:
            break
    return terms


def infer_flags(row: dict[str, Any]) -> dict[str, Any]:
    text = normalize_text(row)
    action_markers = (
        "patch", "post", "reprocess", "request-specialist", "request specialist",
        "request-retraining", "request retraining", "update", "executar", "execute", "action",
    )
    escalation_markers = ("escalate", "escalation", "especialista", "specialist", "human", "engenheiro")
    investigate_markers = ("investigate", "investigar", "diagnose", "diagnost", "contextualizar", "question")
    expected_action = any(marker in text for marker in action_markers)
    expected_escalation = any(marker in text for marker in escalation_markers)
    allowed: set[str] = set()
    if expected_escalation:
        allowed.add("escalation_candidate")
    if expected_action:
        allowed.add("action_candidate")
    if any(marker in text for marker in investigate_markers) or not allowed:
        allowed.add("investigate_only")
        allowed.add("insufficient_evidence")
    return {
        "expected_should_take_action_now": expected_action,
        "expected_requires_human_escalation": expected_escalation,
        "allowed_decision_classes": sorted(allowed),
    }


def expected_path_rows(payload: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict) and "expected_path" in item:
                rows.append(item)
            elif isinstance(item, (dict, list)):
                rows.extend(expected_path_rows(item))
    elif isinstance(payload, dict):
        if "expected_path" in payload:
            rows.append(payload)
        else:
            for value in payload.values():
                if isinstance(value, (dict, list)):
                    rows.extend(expected_path_rows(value))
    return rows


def adapt_expected_paths(payload: Any, fixed_groups: set[str], split_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = expected_path_rows(payload)
    locked_groups = split_groups(split_manifest).get("LOCKED_TEST", set())
    oracles: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_blob = json.dumps(row, ensure_ascii=False, sort_keys=True).lower()
        mentions = {group for group in ASSET_RE.findall(row_blob) if group in fixed_groups}
        mentions -= locked_groups
        if not mentions:
            continue
        flags = infer_flags(row)
        terms = private_terms(row.get("expected_path", row)) or private_terms(row.get("root_question", row))
        source_hash = stable_hash(row)
        for group_id in mentions:
            oracle = oracles.setdefault(
                group_id,
                {
                    "oracle_format": "expected_paths_asset_mention_adapter_v2",
                    "private_row_count": 0,
                    "private_expected_path_item_count": 0,
                    "private_source_hashes": [],
                    "allowed_decision_classes": [],
                    "required_evidence_terms": [],
                    "expected_should_take_action_now": False,
                    "expected_requires_human_escalation": False,
                },
            )
            oracle["private_row_count"] += 1
            oracle["private_source_hashes"].append(source_hash)
            expected_path = row.get("expected_path")
            oracle["private_expected_path_item_count"] += len(expected_path) if isinstance(expected_path, list) else 1
            oracle["allowed_decision_classes"] = sorted(set(oracle["allowed_decision_classes"]) | set(flags["allowed_decision_classes"]))
            oracle["required_evidence_terms"] = sorted(set(oracle["required_evidence_terms"]) | set(terms))[:24]
            oracle["expected_should_take_action_now"] = bool(oracle["expected_should_take_action_now"] or flags["expected_should_take_action_now"])
            oracle["expected_requires_human_escalation"] = bool(oracle["expected_requires_human_escalation"] or flags["expected_requires_human_escalation"])
    locked_hits = sorted(set(oracles) & locked_groups)
    if locked_hits:
        raise AssertionError(f"private oracle adapter produced LOCKED_TEST groups: {locked_hits}")
    return oracles


def score_call(call: dict[str, Any], oracle: dict[str, Any] | None) -> dict[str, Any]:
    output = output_payload(call)
    base = {
        "group_id": call.get("group_id"),
        "split": call.get("split"),
        "output_hash": call.get("output_hash") or (stable_hash(output) if output is not None else None),
        "proxy_success": bool(call.get("score", {}).get("task_success_proxy")),
    }
    if output is None:
        return {**base, "scoreable": False, "reason": "parsed_model_output_missing", "real_task_quality": None}
    if not oracle:
        return {**base, "scoreable": False, "reason": "private_oracle_missing_for_group", "real_task_quality": None}

    text = normalize_text(output)
    decision = str(output.get("decision_class", "")).lower()
    allowed = [str(item).lower() for item in oracle.get("allowed_decision_classes", [])]
    required_terms = [str(item).lower() for item in oracle.get("required_evidence_terms", [])]
    expected_action = bool(oracle.get("expected_should_take_action_now"))
    expected_escalation = bool(oracle.get("expected_requires_human_escalation"))

    schema_valid = decision in DECISION_CLASSES and isinstance(output.get("evidence_plan"), list)
    decision_correct = decision in allowed if allowed else True
    evidence_hit_count = sum(1 for term in required_terms if term and term in text)
    evidence_min_hits = 0 if not required_terms else min(3, max(1, math.ceil(len(required_terms) * 0.25)))
    evidence_correct = True if not required_terms else evidence_hit_count >= evidence_min_hits
    action_correct = output.get("should_take_action_now") is expected_action
    escalation_correct = output.get("requires_human_escalation") is expected_escalation
    no_locked = "locked_test" not in text
    no_gold = not any(term in text for term in SENSITIVE_OUTPUT_TERMS)
    premature_action = output.get("should_take_action_now") is True and expected_action is False
    unsupported_final_claim = not no_locked or not no_gold
    components = [schema_valid, decision_correct, evidence_correct, action_correct, escalation_correct, no_locked, no_gold]
    real_quality = sum(1 for item in components if item) / len(components)
    return {
        **base,
        "scoreable": True,
        "oracle_format": oracle.get("oracle_format"),
        "oracle_private_row_count": oracle.get("private_row_count"),
        "oracle_private_expected_path_item_count": oracle.get("private_expected_path_item_count"),
        "schema_valid": schema_valid,
        "decision_correct": decision_correct,
        "evidence_correct": evidence_correct,
        "evidence_required_term_count": len(required_terms),
        "evidence_hit_count": evidence_hit_count,
        "evidence_min_hits": evidence_min_hits,
        "action_correct": action_correct,
        "escalation_correct": escalation_correct,
        "premature_action": premature_action,
        "unsupported_final_claim": unsupported_final_claim,
        "no_locked_test_claim": no_locked,
        "no_gold_claim": no_gold,
        "real_task_quality": round(real_quality, 4),
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scoreable = [row for row in rows if row.get("scoreable")]
    if not scoreable:
        return {
            "scoreable_calls": 0,
            "real_task_quality": None,
            "decision_correctness": None,
            "evidence_correctness": None,
            "action_correctness": None,
            "escalation_correctness": None,
            "premature_action_rate": None,
            "unsupported_final_claim_rate": None,
            "proxy_success_rate": None,
            "proxy_vs_real_disagreement_rate": None,
        }

    def rate(key: str) -> float:
        return round(sum(1 for row in scoreable if row.get(key)) / len(scoreable), 4)

    disagreements = [row for row in scoreable if bool(row.get("proxy_success")) != (float(row.get("real_task_quality", 0.0)) >= 0.875)]
    return {
        "scoreable_calls": len(scoreable),
        "real_task_quality": round(sum(float(row["real_task_quality"]) for row in scoreable) / len(scoreable), 4),
        "decision_correctness": rate("decision_correct"),
        "evidence_correctness": rate("evidence_correct"),
        "action_correctness": rate("action_correct"),
        "escalation_correctness": rate("escalation_correct"),
        "premature_action_rate": round(sum(1 for row in scoreable if row.get("premature_action")) / len(scoreable), 4),
        "unsupported_final_claim_rate": round(sum(1 for row in scoreable if row.get("unsupported_final_claim")) / len(scoreable), 4),
        "proxy_success_rate": rate("proxy_success"),
        "proxy_vs_real_disagreement_rate": round(len(disagreements) / len(scoreable), 4),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest) if args.manifest else {}
    split_manifest = load_json(args.split_manifest)
    fixed_summary = load_json(args.fixed_output_file)
    oracle_payload = load_json(args.oracle_file)
    if not isinstance(fixed_summary, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be JSON objects")
    calls = collect_calls(fixed_summary)
    assert_fixed_scope(fixed_summary, calls, split_manifest)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    parsed = [call for call in calls if output_payload(call) is not None]
    output_hashes = sorted({str(call.get("output_hash")) for call in calls if call.get("output_hash")})
    oracles = adapt_expected_paths(oracle_payload, fixed_groups, split_manifest)
    rows = [score_call(call, oracles.get(str(call.get("group_id")))) for call in calls]
    metrics = aggregate(rows)
    status = "E9_TASK_QUALITY_SCORER_PASS" if metrics["scoreable_calls"] else "E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED"
    groups_by_split = split_groups(split_manifest)
    allowed_groups = set().union(*(groups_by_split.get(split, set()) for split in ALLOWED_SPLITS))
    summary = {
        "report_version": "e9-evaluator-side-task-quality-scorer-summary-v2",
        "date": "2026-08-16",
        "status": status,
        "scope": {
            "allowed_splits": sorted(ALLOWED_SPLITS),
            "forbidden_splits": sorted(FORBIDDEN_SPLITS),
            "locked_test_accessed": False,
            "oracle_scope": {
                "oracle_formats_detected": sorted({str(oracle.get("oracle_format")) for oracle in oracles.values()}),
                "known_allowed_oracle_groups": sorted(set(oracles) & allowed_groups),
                "locked_test_oracle_groups_detected": [],
                "outside_known_allowed_asset_groups": sorted(group for group in oracles if group.startswith("asset_") and group not in allowed_groups),
            },
        },
        "inputs": {
            "fixed_output_file": str(args.fixed_output_file),
            "private_oracle_file_argument": str(args.oracle_file),
            "private_oracle_file_provided": args.oracle_file.exists(),
            "fixed_calls_consumed": len(calls),
            "fixed_output_hashes_consumed": len(output_hashes),
            "parsed_model_outputs_available": len(parsed),
            "private_oracles_loaded": len(oracles),
            "calls_with_matching_private_oracle": sum(1 for call in calls if str(call.get("group_id")) in oracles),
        },
        "gold_leakage_controls": {
            "model_prompt_receives_oracle": False,
            "scorer_reads_oracle_after_outputs_fixed": True,
            "outputs_hashed_before_scoring": bool(output_hashes),
            "evaluator_only_paths_blocked_from_model": True,
            "locked_test_oracle_groups_rejected": True,
            "raw_expected_values_printed": False,
        },
        "constants_preserved": manifest.get("constants_preserved", {}),
        "aggregate_metrics": metrics,
        "score_rows": rows if args.include_rows else [],
        "interpretation_limits": [
            "Expected-path values are used only inside the local scorer and are not printed.",
            "This adapter maps expected-path rows to fixed model groups by asset mentions.",
            "No model/provider or final architecture is frozen by E9.",
        ],
        "final_architecture_freeze": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--oracle-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--include-rows", action="store_true")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({
        "status": summary["status"],
        "fixed_calls_consumed": summary["inputs"]["fixed_calls_consumed"],
        "parsed_model_outputs_available": summary["inputs"]["parsed_model_outputs_available"],
        "private_oracles_loaded": summary["inputs"]["private_oracles_loaded"],
        "calls_with_matching_private_oracle": summary["inputs"]["calls_with_matching_private_oracle"],
        "scoreable_calls": summary["aggregate_metrics"]["scoreable_calls"],
        "real_task_quality": summary["aggregate_metrics"]["real_task_quality"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
