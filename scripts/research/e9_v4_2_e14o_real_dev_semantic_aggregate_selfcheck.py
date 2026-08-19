#!/usr/bin/env python3
"""Offline pass/fail regression for the E14o E9 v4.2 aggregate gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
AGG_PATH = HERE / "e9_v4_2_e14o_real_dev_semantic_aggregate.py"
FIXTURE_PATH = HERE / "e9_v4_2_qwen36_27b_e14o_real_dev_semantic_judge_runner_selfcheck.py"

AGG_SPEC = importlib.util.spec_from_file_location("e9_v42_e14o_aggregate", AGG_PATH)
FIXTURE_SPEC = importlib.util.spec_from_file_location("e9_v42_e14o_fixture", FIXTURE_PATH)
if AGG_SPEC is None or AGG_SPEC.loader is None or FIXTURE_SPEC is None or FIXTURE_SPEC.loader is None:
    raise RuntimeError("failed to load E14o aggregate self-check dependencies")
agg = importlib.util.module_from_spec(AGG_SPEC)
AGG_SPEC.loader.exec_module(agg)
fixture = importlib.util.module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(fixture)
runner = agg.runner


def _judge_results(packet: dict, *, fail_one_factual: bool) -> dict:
    rows = []
    first = True
    for call in packet["calls"]:
        for unit in call["claim_units"]:
            if fail_one_factual and first:
                claim_type = "factual_assertion"
                support = "NOT_SUPPORTED"
                first = False
            else:
                claim_type = "procedural_recommendation"
                support = "NOT_APPLICABLE"
            rows.append({
                "call_index": int(call["call_index"]),
                "claim_index": int(unit["claim_index"]),
                "claim_type": claim_type,
                "support_label": support,
            })
    return {
        "report_version": runner.RESULT_VERSION,
        "candidate": "E14o-after-E14n-v1.1",
        "judge": {
            "provider": "Groq",
            "model": runner.MODEL,
            "temperature": 0,
            "reasoning_effort": "none",
            "response_format": "json_object",
            "system_prompt_reused_from_synthetic_runner": True,
            "provider_case_id_mapped_back_locally": True,
        },
        "scope": {
            "split": "DEV",
            "private_oracle_used": False,
            "private_scorer_rows_used": False,
            "validation_feedback_used": False,
            "locked_test_used": False,
        },
        "results": rows,
    }


def main() -> int:
    packet = fixture.synthetic_packet()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        packet_path = root / "packet.json"
        pass_path = root / "pass.json"
        fail_path = root / "fail.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
        pass_path.write_text(json.dumps(_judge_results(packet, fail_one_factual=False)), encoding="utf-8")
        fail_path.write_text(json.dumps(_judge_results(packet, fail_one_factual=True)), encoding="utf-8")

        passed = agg.run(argparse.Namespace(claim_packet=packet_path, judge_results=pass_path))
        failed = agg.run(argparse.Namespace(claim_packet=packet_path, judge_results=fail_path))

    assert passed["semantic_groundedness_gate_pass"] is True
    assert passed["status"] == agg.PASS_STATUS
    assert passed["claim_units_expected"] == 66
    assert passed["valid_unique_prediction_rows"] == 66
    assert passed["full_coverage"] is True
    assert failed["semantic_groundedness_gate_pass"] is False
    assert failed["status"] == agg.FAIL_STATUS
    assert failed["factual_not_supported"] == 1
    assert failed["gate_results"]["zero_not_supported_factual_claims"] is False
    assert failed["validation_gate_authorized"] is False

    print(json.dumps({
        "status": "E9_V4_2_E14O_REAL_DEV_SEMANTIC_AGGREGATE_SELFCHECK_PASS",
        "full_66_row_pass_fixture_passed": True,
        "single_not_supported_factual_claim_blocks_gate": True,
        "validation_gate_authorized": False,
        "provider_calls_made": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
