#!/usr/bin/env python3
"""E9 evaluator-side task-quality scorer.

The scorer is intentionally separated from model prompting. It consumes fixed model
outputs after generation and may optionally read private DEV/VALIDATION oracles.
It never sends oracle/gold text to a model and it rejects LOCKED_TEST scoring
before final evaluation.

CI runs in contract mode when private oracles or parsed model outputs are not
available in the public repository. A local/private run can provide:

  --fixed-output-file <E8 summary with parsed model outputs>
  --oracle-file <private DEV/VALIDATION oracle file>

Supported fixed-output fields per call: `parsed_output`, `model_output`, `output`,
or `response`. Sanitized summaries that contain only output hashes are consumed
for fixed-output integrity but cannot yield real task-quality scores.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FORBIDDEN_SPLITS = {"LOCKED_TEST"}
ALLOWED_SPLITS = {"DEV", "VALIDATION"}
DECISION_CLASSES = {"investigate_only", "action_candidate", "escalation_candidate", "insufficient_evidence"}
DEFAULT_FIXED_OUTPUT = Path("research/results/e8-groq-free-anywhere-model-run-summary-2026-08-16.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


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


def collect_oracles(payload: Any) -> dict[str, dict[str, Any]]:
    """Collect flexible DEV/VALIDATION private oracles by group/asset id.

    Supported patterns:
    - {"oracles": {"asset_X": {...}}}
    - {"asset_X": {...}}
    - list of records with group_id/asset_id/assetId and expected_* fields
    """
    if isinstance(payload, dict) and isinstance(payload.get("oracles"), dict):
        return {str(k): v for k, v in payload["oracles"].items() if isinstance(v, dict)}
    oracles: dict[str, dict[str, Any]] = {}
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, dict) and (key.startswith("asset_") or value.get("group_id") or value.get("asset_id") or value.get("assetId")):
                group_id = str(value.get("group_id") or value.get("asset_id") or value.get("assetId") or key)
                oracles[group_id] = value
            elif isinstance(value, (dict, list)):
                oracles.update(collect_oracles(value))
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                group_id = item.get("group_id") or item.get("asset_id") or item.get("assetId")
                if group_id:
                    oracles[str(group_id)] = item
                else:
                    oracles.update(collect_oracles(item))
    return oracles


def assert_scope(fixed_summary: dict[str, Any], calls: list[dict[str, Any]]) -> None:
    scope = fixed_summary.get("scope", {}) if isinstance(fixed_summary, dict) else {}
    if scope.get("locked_test_accessed") is True:
        raise AssertionError("fixed output summary reports LOCKED_TEST access")
    for call in calls:
        split = call.get("split")
        if split in FORBIDDEN_SPLITS:
            raise AssertionError(f"LOCKED_TEST call present: {call.get('group_id')}")
        if split is not None and split not in ALLOWED_SPLITS:
            raise AssertionError(f"unexpected split in fixed outputs: {split}")


def bool_expected(oracle: dict[str, Any], names: tuple[str, ...]) -> bool | None:
    for name in names:
        if isinstance(oracle.get(name), bool):
            return bool(oracle[name])
    return None


def list_expected(oracle: dict[str, Any], names: tuple[str, ...]) -> list[str]:
    for name in names:
        value = oracle.get(name)
        if isinstance(value, list):
            return [str(item).lower() for item in value]
        if isinstance(value, str):
            return [value.lower()]
    return []


def score_call(call: dict[str, Any], oracle: dict[str, Any]) -> dict[str, Any]:
    output = output_payload(call)
    if output is None:
        return {
            "scoreable": False,
            "reason": "parsed_model_output_missing",
            "proxy_success": bool(call.get("score", {}).get("task_success_proxy")),
            "real_task_quality": None,
        }

    text = normalize_text(output)
    decision = output.get("decision_class")
    expected_decisions = list_expected(oracle, ("expected_decision_class", "expected_decision", "decision_class", "allowed_decision_classes"))
    required_evidence = list_expected(oracle, ("required_evidence_terms", "required_evidence", "evidence_terms", "expected_evidence"))
    forbidden_claims = list_expected(oracle, ("forbidden_claim_terms", "forbidden_claims"))
    expected_action = bool_expected(oracle, ("expected_should_take_action_now", "should_take_action_now", "action_required", "requires_action"))
    expected_escalation = bool_expected(oracle, ("expected_requires_human_escalation", "requires_human_escalation", "escalation_required", "requires_escalation"))

    schema_valid = decision in DECISION_CLASSES and isinstance(output.get("evidence_plan"), list)
    decision_correct = True if not expected_decisions else str(decision).lower() in expected_decisions
    evidence_hits = [term for term in required_evidence if term and term in text]
    evidence_correct = True if not required_evidence else len(evidence_hits) == len(required_evidence)
    action_correct = True if expected_action is None else output.get("should_take_action_now") is expected_action
    escalation_correct = True if expected_escalation is None else output.get("requires_human_escalation") is expected_escalation
    forbidden_claim_ok = not any(term and term in text for term in forbidden_claims)
    no_locked = "locked_test" not in text
    no_gold = not any(term in text for term in ("evaluator gold", "expected answer", "hidden oracle", "private oracle"))
    premature_action = output.get("should_take_action_now") is True and expected_action is False
    unsupported_final_claim = not forbidden_claim_ok or not no_gold or not no_locked
    components = [schema_valid, decision_correct, evidence_correct, action_correct, escalation_correct, forbidden_claim_ok, no_locked, no_gold]
    real_quality = sum(1 for item in components if item) / len(components)
    return {
        "scoreable": True,
        "group_id": call.get("group_id"),
        "split": call.get("split"),
        "output_hash": call.get("output_hash") or stable_hash(output),
        "proxy_success": bool(call.get("score", {}).get("task_success_proxy")),
        "schema_valid": schema_valid,
        "decision_correct": decision_correct,
        "evidence_correct": evidence_correct,
        "evidence_hits": evidence_hits,
        "action_correct": action_correct,
        "escalation_correct": escalation_correct,
        "premature_action": premature_action,
        "unsupported_final_claim": unsupported_final_claim,
        "no_locked_test_claim": no_locked,
        "no_gold_claim": no_gold,
        "real_task_quality": round(real_quality, 4),
    }


def aggregate(scores: list[dict[str, Any]]) -> dict[str, Any]:
    scoreable = [row for row in scores if row.get("scoreable")]
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

    proxy_disagreement = [row for row in scoreable if bool(row.get("proxy_success")) != (float(row.get("real_task_quality", 0.0)) >= 0.875)]
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
        "proxy_vs_real_disagreement_rate": round(len(proxy_disagreement) / len(scoreable), 4),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_json(args.manifest) if args.manifest else {}
    fixed_summary = load_json(args.fixed_output_file) if args.fixed_output_file and args.fixed_output_file.exists() else {}
    if not isinstance(fixed_summary, dict):
        raise AssertionError("fixed output file must be a JSON object")
    calls = collect_calls(fixed_summary)
    assert_scope(fixed_summary, calls)
    output_hashes = sorted({str(call.get("output_hash")) for call in calls if call.get("output_hash")})
    parsed_outputs = [call for call in calls if output_payload(call) is not None]
    oracle_path = args.oracle_file
    oracles: dict[str, dict[str, Any]] = {}
    if oracle_path is not None and oracle_path.exists():
        if "LOCKED_TEST" in str(oracle_path).upper():
            raise AssertionError("LOCKED_TEST oracle path is forbidden before final evaluation")
        oracles = collect_oracles(load_json(oracle_path))
    scores: list[dict[str, Any]] = []
    for call in calls:
        oracle = oracles.get(str(call.get("group_id")), {})
        scores.append(score_call(call, oracle))
    aggregate_metrics = aggregate(scores)
    real_score_available = bool(oracles) and bool(parsed_outputs) and aggregate_metrics["scoreable_calls"] > 0
    status = "E9_TASK_QUALITY_SCORER_PASS" if real_score_available else "E9_SCORER_CONTRACT_PASS_PRIVATE_ORACLE_OR_OUTPUTS_REQUIRED"
    summary = {
        "report_version": "e9-evaluator-side-task-quality-scorer-summary-v1",
        "date": "2026-08-16",
        "status": status,
        "scope": {
            "allowed_splits": sorted(ALLOWED_SPLITS),
            "forbidden_splits": sorted(FORBIDDEN_SPLITS),
            "locked_test_accessed": False,
        },
        "inputs": {
            "fixed_output_file": str(args.fixed_output_file) if args.fixed_output_file else None,
            "private_oracle_file_provided": oracle_path is not None and oracle_path.exists(),
            "fixed_calls_consumed": len(calls),
            "fixed_output_hashes_consumed": len(output_hashes),
            "parsed_model_outputs_available": len(parsed_outputs),
            "private_oracles_loaded": len(oracles),
        },
        "gold_leakage_controls": {
            "model_prompt_receives_oracle": False,
            "scorer_reads_oracle_after_outputs_fixed": True,
            "outputs_hashed_before_scoring": bool(output_hashes),
            "evaluator_only_paths_blocked_from_model": True,
        },
        "constants_preserved": manifest.get("constants_preserved", {}),
        "aggregate_metrics": aggregate_metrics,
        "score_rows": scores if args.include_rows else [],
        "interpretation_limits": [
            "Real task-quality metrics require both fixed parsed model outputs and private DEV/VALIDATION oracles.",
            "Sanitized E8 summaries with only output hashes prove fixed-output integrity but are not sufficient for semantic scoring.",
            "LOCKED_TEST remains blocked until final evaluation.",
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
    parser.add_argument("--fixed-output-file", type=Path, default=DEFAULT_FIXED_OUTPUT)
    parser.add_argument("--oracle-file", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--include-rows", action="store_true")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({"status": summary["status"], "fixed_calls_consumed": summary["inputs"]["fixed_calls_consumed"], "real_score_available": summary["aggregate_metrics"]["real_task_quality"] is not None}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
