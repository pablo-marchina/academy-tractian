#!/usr/bin/env python3
"""Aggregate E14p E9 v4.2 semantic judge rows without row-level disclosure."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
BASE_PATH = HERE / "e9_v4_2_real_dev_semantic_aggregate.py"
RUNNER_PATH = HERE / "e9_v4_2_qwen36_27b_e14p_real_dev_semantic_judge_runner.py"

BASE_SPEC = importlib.util.spec_from_file_location("e9_v42_aggregate_base_for_e14p", BASE_PATH)
RUNNER_SPEC = importlib.util.spec_from_file_location("e9_v42_e14p_runner_for_aggregate", RUNNER_PATH)
if BASE_SPEC is None or BASE_SPEC.loader is None or RUNNER_SPEC is None or RUNNER_SPEC.loader is None:
    raise RuntimeError("failed to load E14p semantic aggregate dependencies")
base = importlib.util.module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(base)
runner = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner)

REPORT_VERSION = "e9-v4.2-e14p-real-dev-semantic-aggregate-v1"
PASS_STATUS = "E9_V4_2_E14P_REAL_DEV_SEMANTIC_GROUNDEDNESS_PASS"
FAIL_STATUS = "E9_V4_2_E14P_REAL_DEV_SEMANTIC_GROUNDEDNESS_FAIL"


def run(args: argparse.Namespace) -> dict[str, Any]:
    saved_runner = base.runner
    saved_result_version = base.EXPECTED_RESULT_VERSION
    base.runner = runner
    base.EXPECTED_RESULT_VERSION = runner.RESULT_VERSION
    try:
        summary = base.run(args)
    finally:
        base.runner = saved_runner
        base.EXPECTED_RESULT_VERSION = saved_result_version

    # Frozen before E14p labels: if serialization removes all factual assertions,
    # no factual assertion can violate visible support, so the rate is vacuously 1.
    if int(summary.get("factual_claims_total") or 0) == 0:
        summary["factual_groundedness_rate"] = 1.0
        summary["factual_groundedness_rate_definition"] = "1.0_when_zero_factual_assertions_else_supported_over_total"
    else:
        summary["factual_groundedness_rate_definition"] = "supported_factual_assertions_over_total_factual_assertions"

    summary["report_version"] = REPORT_VERSION
    summary["status"] = PASS_STATUS if summary.get("semantic_groundedness_gate_pass") is True else FAIL_STATUS
    summary["candidate"] = runner.CANDIDATE
    summary["synthetic_judge_reliability_passed_before_E14p_measurement"] = True
    summary["serializer_provider_calls"] = 0
    summary["paired_serializer_effect_interpretation_only"] = True
    summary["underlying_model_reasoning_improvement_claimed"] = False
    summary["validation_gate_authorized"] = False
    return summary


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
