#!/usr/bin/env python3
"""Oracle-free structural self-check for the E9 v4.2 real DEV semantic measurement path."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from argparse import Namespace
from pathlib import Path

HERE = Path(__file__).parent


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = _load_module("e9_v42_real_runner_selfcheck", HERE / "e9_v4_2_qwen36_27b_real_dev_semantic_judge_runner.py")
agg = _load_module("e9_v42_real_agg_selfcheck", HERE / "e9_v4_2_real_dev_semantic_aggregate.py")


def _synthetic_packet() -> dict:
    fields = []
    for field, count in runner.EXPECTED_SOURCE_COUNTS.items():
        fields.extend([field] * count)
    assert len(fields) == runner.EXPECTED_CLAIMS

    calls = []
    cursor = 0
    sizes = [12, 12, 12, 11, 11, 11]
    for call_index, size in enumerate(sizes):
        units = []
        for claim_index in range(size):
            units.append({
                "claim_index": claim_index,
                "source_field": fields[cursor],
                "claim_text": f"Synthetic claim {cursor}",
            })
            cursor += 1
        calls.append({
            "call_index": call_index,
            "split": "DEV",
            "visible_case": {"synthetic": {"call": call_index}},
            "public_contract": {
                "tool_signatures": [f"GET /synthetic/{i}" for i in range(runner.EXPECTED_TOOL_SIGNATURES)],
                "claim_support_labels": sorted(runner.VALID_SUPPORT),
                "claim_types": sorted(runner.VALID_TYPES),
            },
            "claim_units": units,
        })
    assert cursor == runner.EXPECTED_CLAIMS
    return {
        "report_version": runner.EXPECTED_PACKET_VERSION,
        "scope": {
            "split": "DEV",
            "private_oracle_included": False,
            "private_scorer_rows_included": False,
            "validation_material_included": False,
            "locked_test_material_included": False,
            "runner_selection_rule": "first_agent_input_case_per_asset",
        },
        "calls": calls,
    }


def _prediction_payload(packet: dict, unsafe: bool = False) -> dict:
    rows = []
    first = True
    for call in packet["calls"]:
        for unit in call["claim_units"]:
            claim_type = "factual_assertion"
            support = "SUPPORTED"
            if unsafe and first:
                support = "NOT_SUPPORTED"
                first = False
            rows.append({
                "call_index": call["call_index"],
                "claim_index": unit["claim_index"],
                "claim_type": claim_type,
                "support_label": support,
            })
    return {
        "report_version": "e9-v4.2-qwen36-27b-real-dev-semantic-judge-v1",
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
    packet = _synthetic_packet()
    calls = runner.validate_packet(packet)
    assert len(calls) == runner.EXPECTED_CALLS
    assert sum(len(c["claim_units"]) for c in calls) == runner.EXPECTED_CLAIMS

    request, case_to_claim = runner.build_request_payload(calls[0])
    assert request["model"] == runner.synth.MODEL
    assert request["messages"][0]["content"] == runner.synth.SYSTEM_PROMPT
    assert request["temperature"] == 0
    assert request["reasoning_effort"] == "none"
    assert request["response_format"] == {"type": "json_object"}
    assert request["max_completion_tokens"] == 2048
    assert "expected_" not in request["messages"][1]["content"]
    assert "gold" not in request["messages"][1]["content"].lower()
    assert len(case_to_claim) == len(calls[0]["claim_units"])
    assert all(case_id.startswith("R") for case_id in case_to_claim)

    sample_output = {
        "results": [
            {"case_id": case_id, "claim_type": "factual_assertion", "support_label": "SUPPORTED"}
            for case_id in case_to_claim
        ]
    }
    validated = runner.validate_judge_payload(sample_output, case_to_claim)
    assert len(validated) == len(case_to_claim)
    assert {row["claim_index"] for row in validated} == set(case_to_claim.values())

    bad_output = {
        "results": [
            {"claim_index": idx, "claim_type": "factual_assertion", "support_label": "SUPPORTED"}
            for idx in case_to_claim.values()
        ]
    }
    try:
        runner.validate_judge_payload(bad_output, case_to_claim)
    except AssertionError:
        pass
    else:
        raise AssertionError("legacy claim_index provider contract must be rejected")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        packet_path = root / "packet.json"
        pass_path = root / "pass.json"
        fail_path = root / "fail.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
        pass_path.write_text(json.dumps(_prediction_payload(packet, unsafe=False)), encoding="utf-8")
        fail_path.write_text(json.dumps(_prediction_payload(packet, unsafe=True)), encoding="utf-8")

        passed = agg.run(Namespace(claim_packet=packet_path, judge_results=pass_path))
        assert passed["semantic_groundedness_gate_pass"] is True
        assert passed["full_coverage"] is True
        assert passed["factual_not_supported"] == 0

        failed = agg.run(Namespace(claim_packet=packet_path, judge_results=fail_path))
        assert failed["semantic_groundedness_gate_pass"] is False
        assert failed["factual_not_supported"] == 1
        assert failed["validation_gate_authorized"] is False

    print(json.dumps({
        "status": "E9_V4_2_REAL_DEV_SEMANTIC_MEASUREMENT_SELFCHECK_PASS",
        "synthetic_claim_units": runner.EXPECTED_CLAIMS,
        "system_prompt_reuse_verified": True,
        "provider_case_id_contract_verified": True,
        "provider_call_made": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
