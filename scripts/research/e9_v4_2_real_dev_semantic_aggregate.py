#!/usr/bin/env python3
"""Aggregate local E9 v4.2 real-DEV semantic judge rows without printing row-level labels.

This scorer uses only the already-built public-only DEV claim packet and local
judge predictions. It does not read private expected paths, private scorer rows,
VALIDATION, or LOCKED_TEST. It prints aggregate counts/rates only and never
prints claim text, visible-case values, identifiers, group IDs, hashes, paths,
or per-claim judge labels.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
RUNNER_PATH = HERE / "e9_v4_2_qwen36_27b_real_dev_semantic_judge_runner.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_real_runner", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load real DEV semantic judge runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

EXPECTED_RESULT_VERSION = "e9-v4.2-qwen36-27b-real-dev-semantic-judge-v1"
FACTUAL = "factual_assertion"
NA = "NOT_APPLICABLE"
SUPPORTED = "SUPPORTED"
CONTRADICTED = "CONTRADICTED"
NOT_SUPPORTED = "NOT_SUPPORTED"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_div(num: int, den: int) -> float:
    return 0.0 if den == 0 else num / den


def run(args: argparse.Namespace) -> dict[str, Any]:
    packet = _load(args.claim_packet)
    calls = runner.validate_packet(packet)
    expected_keys = {
        (int(call["call_index"]), int(unit["claim_index"]))
        for call in calls
        for unit in call["claim_units"]
    }
    if len(expected_keys) != runner.EXPECTED_CLAIMS:
        raise AssertionError("claim packet keys are not uniquely complete")

    judged = _load(args.judge_results)
    if not isinstance(judged, dict) or judged.get("report_version") != EXPECTED_RESULT_VERSION:
        raise AssertionError("judge result report_version does not match frozen real DEV runner")
    judge_meta = judged.get("judge")
    scope = judged.get("scope")
    rows = judged.get("results")
    if not isinstance(judge_meta, dict) or judge_meta.get("model") != runner.MODEL:
        raise AssertionError("judge model does not match reliability-qualified frozen judge")
    if judge_meta.get("temperature") != 0 or judge_meta.get("reasoning_effort") != "none":
        raise AssertionError("judge settings changed")
    if judge_meta.get("system_prompt_reused_from_synthetic_runner") is not True:
        raise AssertionError("frozen synthetic system prompt was not reused")
    if not isinstance(scope, dict) or scope.get("split") != "DEV":
        raise AssertionError("judge results must be DEV-only")
    for key in ("private_oracle_used", "private_scorer_rows_used", "validation_feedback_used", "locked_test_used"):
        if scope.get(key) is not False:
            raise AssertionError(f"judge scope must explicitly set {key}=false")
    if not isinstance(rows, list):
        raise AssertionError("judge results must contain a results list")

    seen: set[tuple[int, int]] = set()
    duplicate_rows = 0
    invalid_schema_rows = 0
    extra_rows = 0
    type_counts: Counter[str] = Counter()
    support_counts: Counter[str] = Counter()

    factual_total = 0
    factual_supported = 0
    factual_contradicted = 0
    factual_not_supported = 0
    factual_not_applicable = 0
    nonfactual_total = 0
    nonfactual_not_applicable = 0
    nonfactual_non_not_applicable = 0

    for row in rows:
        if not isinstance(row, dict) or set(row.keys()) != {"call_index", "claim_index", "claim_type", "support_label"}:
            invalid_schema_rows += 1
            continue
        call_index = row.get("call_index")
        claim_index = row.get("claim_index")
        claim_type = str(row.get("claim_type") or "")
        support_label = str(row.get("support_label") or "")
        if not isinstance(call_index, int) or not isinstance(claim_index, int):
            invalid_schema_rows += 1
            continue
        if claim_type not in runner.VALID_TYPES or support_label not in runner.VALID_SUPPORT:
            invalid_schema_rows += 1
            continue
        key = (call_index, claim_index)
        if key not in expected_keys:
            extra_rows += 1
            continue
        if key in seen:
            duplicate_rows += 1
            continue
        seen.add(key)
        type_counts[claim_type] += 1
        support_counts[support_label] += 1

        if claim_type == FACTUAL:
            factual_total += 1
            factual_supported += int(support_label == SUPPORTED)
            factual_contradicted += int(support_label == CONTRADICTED)
            factual_not_supported += int(support_label == NOT_SUPPORTED)
            factual_not_applicable += int(support_label == NA)
        else:
            nonfactual_total += 1
            nonfactual_not_applicable += int(support_label == NA)
            nonfactual_non_not_applicable += int(support_label != NA)

    missing_rows = len(expected_keys - seen)
    full_coverage = (
        len(seen) == runner.EXPECTED_CLAIMS
        and missing_rows == 0
        and duplicate_rows == 0
        and invalid_schema_rows == 0
        and extra_rows == 0
        and len(rows) == runner.EXPECTED_CLAIMS
    )

    factual_groundedness_rate = _safe_div(factual_supported, factual_total)
    type_support_consistency_rate = _safe_div(
        factual_supported + factual_contradicted + factual_not_supported + nonfactual_not_applicable,
        factual_total + nonfactual_total,
    )

    gates = {
        "full_coverage": full_coverage,
        "zero_contradicted_factual_claims": factual_contradicted == 0,
        "zero_not_supported_factual_claims": factual_not_supported == 0,
        "zero_factual_not_applicable_pairs": factual_not_applicable == 0,
        "zero_nonfactual_non_not_applicable_pairs": nonfactual_non_not_applicable == 0,
    }
    semantic_pass = all(gates.values())

    return {
        "report_version": "e9-v4.2-real-dev-semantic-aggregate-v1",
        "status": (
            "E9_V4_2_REAL_DEV_SEMANTIC_GROUNDEDNESS_PASS"
            if semantic_pass
            else "E9_V4_2_REAL_DEV_SEMANTIC_GROUNDEDNESS_FAIL"
        ),
        "judge_model": runner.MODEL,
        "claim_units_expected": runner.EXPECTED_CLAIMS,
        "valid_unique_prediction_rows": len(seen),
        "missing_prediction_rows": missing_rows,
        "duplicate_prediction_rows": duplicate_rows,
        "invalid_schema_rows": invalid_schema_rows,
        "extra_prediction_rows": extra_rows,
        "full_coverage": full_coverage,
        "claim_type_counts": dict(sorted(type_counts.items())),
        "support_label_counts": dict(sorted(support_counts.items())),
        "factual_claims_total": factual_total,
        "factual_supported": factual_supported,
        "factual_contradicted": factual_contradicted,
        "factual_not_supported": factual_not_supported,
        "factual_not_applicable": factual_not_applicable,
        "nonfactual_claims_total": nonfactual_total,
        "nonfactual_not_applicable": nonfactual_not_applicable,
        "nonfactual_non_not_applicable": nonfactual_non_not_applicable,
        "factual_groundedness_rate": round(factual_groundedness_rate, 4),
        "type_support_consistency_rate": round(type_support_consistency_rate, 4),
        "gate_results": gates,
        "semantic_groundedness_gate_pass": semantic_pass,
        "synthetic_judge_reliability_passed_before_real_measurement": True,
        "validation_gate_authorized": False,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "prints_claim_text": False,
        "prints_visible_case_values": False,
        "prints_prediction_rows": False,
        "prints_identifiers": False,
        "prints_group_ids": False,
        "prints_hashes": False,
        "prints_private_paths": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-packet", type=Path, required=True)
    parser.add_argument("--judge-results", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["semantic_groundedness_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
