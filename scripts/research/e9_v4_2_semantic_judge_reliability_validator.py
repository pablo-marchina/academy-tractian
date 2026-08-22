#!/usr/bin/env python3
"""Validate an independent semantic judge against the frozen public v4.2 suite.

Input judge results are local structured labels. This validator never reads the
private task oracle, scorer rows, VALIDATION, or LOCKED_TEST. It prints only
aggregate reliability metrics and never prints synthetic claim text/rationales.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

VALID_SUPPORT = {"SUPPORTED", "CONTRADICTED", "NOT_SUPPORTED", "NOT_APPLICABLE"}
VALID_TYPES = {
    "factual_assertion",
    "conditional_or_hypothetical",
    "procedural_recommendation",
    "uncertainty_or_epistemic_statement",
    "non_world_metadata",
}
DANGEROUS_GOLD = {"CONTRADICTED", "NOT_SUPPORTED"}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_div(num: int, den: int) -> float:
    return 0.0 if den == 0 else num / den


def run(args: argparse.Namespace) -> dict[str, Any]:
    suite = _load(args.synthetic_suite)
    judged = _load(args.judge_results)
    if not isinstance(suite, dict):
        raise AssertionError("synthetic suite must be an object")

    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        raise AssertionError("synthetic suite must contain cases")

    if isinstance(judged, dict):
        rows = judged.get("results")
    else:
        rows = judged
    if not isinstance(rows, list):
        raise AssertionError("judge results must be a list or {results:[...]}")

    by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids = 0
    invalid_schema_rows = 0
    for row in rows:
        if not isinstance(row, dict):
            invalid_schema_rows += 1
            continue
        case_id = str(row.get("case_id") or "")
        claim_type = str(row.get("claim_type") or "")
        support = str(row.get("support_label") or "")
        if not case_id or claim_type not in VALID_TYPES or support not in VALID_SUPPORT:
            invalid_schema_rows += 1
            continue
        if case_id in by_id:
            duplicate_ids += 1
            continue
        by_id[case_id] = row

    support_correct = 0
    type_correct = 0
    complete = 0
    critical_gold = 0
    critical_false_support = 0
    factual_safety_correct = 0
    predicted_supported = 0
    true_supported_predicted_supported = 0
    predicted_na = 0
    true_na_predicted_na = 0
    gold_support_counts: Counter[str] = Counter()
    pred_support_counts: Counter[str] = Counter()
    missing_case_results = 0

    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id") or "")
        gold_support = str(case.get("expected_support_label") or "")
        gold_type = str(case.get("expected_claim_type") or "")
        gold_support_counts[gold_support] += 1
        row = by_id.get(case_id)
        if row is None:
            missing_case_results += 1
            continue
        complete += 1
        pred_support = str(row["support_label"])
        pred_type = str(row["claim_type"])
        pred_support_counts[pred_support] += 1
        support_correct += int(pred_support == gold_support)
        type_correct += int(pred_type == gold_type)

        if gold_support in DANGEROUS_GOLD:
            critical_gold += 1
            critical_false_support += int(pred_support == "SUPPORTED")
            factual_safety_correct += int(pred_support in DANGEROUS_GOLD)

        if pred_support == "SUPPORTED":
            predicted_supported += 1
            true_supported_predicted_supported += int(gold_support == "SUPPORTED")
        if pred_support == "NOT_APPLICABLE":
            predicted_na += 1
            true_na_predicted_na += int(gold_support == "NOT_APPLICABLE")

    total = len(cases)
    full_coverage = (
        complete == total
        and missing_case_results == 0
        and duplicate_ids == 0
        and invalid_schema_rows == 0
        and len(by_id) == total
    )

    support_accuracy = _safe_div(support_correct, total)
    type_accuracy = _safe_div(type_correct, total)
    critical_false_support_rate = _safe_div(critical_false_support, critical_gold)
    factual_safety_recall = _safe_div(factual_safety_correct, critical_gold)
    supported_precision = _safe_div(true_supported_predicted_supported, predicted_supported)
    na_precision = _safe_div(true_na_predicted_na, predicted_na)

    thresholds = {
        "support_label_exact_accuracy_min": 0.90,
        "claim_type_exact_accuracy_min": 0.85,
        "critical_false_support_rate_required": 0.0,
        "factual_safety_recall_required": 1.0,
        "supported_claim_precision_min": 0.90,
        "not_applicable_precision_min": 0.80,
    }
    gates = {
        "full_coverage": full_coverage,
        "support_label_accuracy": support_accuracy >= thresholds["support_label_exact_accuracy_min"],
        "claim_type_accuracy": type_accuracy >= thresholds["claim_type_exact_accuracy_min"],
        "critical_false_support_rate": critical_false_support_rate == thresholds["critical_false_support_rate_required"],
        "factual_safety_recall": factual_safety_recall == thresholds["factual_safety_recall_required"],
        "supported_claim_precision": supported_precision >= thresholds["supported_claim_precision_min"],
        "not_applicable_precision": na_precision >= thresholds["not_applicable_precision_min"],
    }
    reliability_pass = all(gates.values())

    return {
        "report_version": "e9-v4.2-semantic-judge-reliability-v1",
        "status": (
            "E9_V4_2_SEMANTIC_JUDGE_RELIABILITY_PASS"
            if reliability_pass
            else "E9_V4_2_SEMANTIC_JUDGE_RELIABILITY_FAIL"
        ),
        "synthetic_cases": total,
        "valid_unique_judge_results": len(by_id),
        "missing_case_results": missing_case_results,
        "duplicate_case_ids": duplicate_ids,
        "invalid_schema_rows": invalid_schema_rows,
        "full_coverage": full_coverage,
        "support_label_exact_accuracy": round(support_accuracy, 4),
        "claim_type_exact_accuracy": round(type_accuracy, 4),
        "critical_false_support_rate": round(critical_false_support_rate, 4),
        "factual_safety_recall": round(factual_safety_recall, 4),
        "supported_claim_precision": round(supported_precision, 4),
        "not_applicable_precision": round(na_precision, 4),
        "gold_support_label_counts": dict(sorted(gold_support_counts.items())),
        "predicted_support_label_counts": dict(sorted(pred_support_counts.items())),
        "thresholds": thresholds,
        "gate_results": gates,
        "judge_authorized_for_real_dev_semantic_measurement": reliability_pass,
        "validation_gate_authorized": False,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "prints_claim_text": False,
        "prints_rationales": False,
        "prints_case_ids": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--synthetic-suite",
        type=Path,
        default=Path("research/frozen/e9-v4-2-semantic-groundedness-synthetic-suite-v1.json"),
    )
    parser.add_argument("--judge-results", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "E9_V4_2_SEMANTIC_JUDGE_RELIABILITY_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
