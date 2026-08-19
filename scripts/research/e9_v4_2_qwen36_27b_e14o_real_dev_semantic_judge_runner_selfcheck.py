#!/usr/bin/env python3
"""Offline structural self-check for the frozen E14o E9 v4.2 judge runner."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e9_v4_2_qwen36_27b_e14o_real_dev_semantic_judge_runner.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_e14o_runner", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14o real DEV semantic judge runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def synthetic_packet() -> dict:
    # Distribute the frozen 66 claims over six calls while preserving exact
    # preregistered source-field totals: 12/39/6/9.
    per_call_evidence = [7, 7, 7, 6, 6, 6]
    per_call_risk = [2, 2, 2, 1, 1, 1]
    calls = []
    for call_index in range(6):
        units = []
        claim_index = 0
        for _ in range(2):
            units.append({
                "claim_index": claim_index,
                "source_field": "action_escalation_rubric.calibration_reason",
                "claim_text": "Visible evidence is insufficient; retain uncertainty.",
            })
            claim_index += 1
        for _ in range(per_call_evidence[call_index]):
            units.append({
                "claim_index": claim_index,
                "source_field": "evidence_plan[]",
                "claim_text": "Retrieve a public read before drawing a factual conclusion.",
            })
            claim_index += 1
        units.append({
            "claim_index": claim_index,
            "source_field": "proposed_next_step",
            "claim_text": "Inspect the next public resource before acting.",
        })
        claim_index += 1
        for _ in range(per_call_risk[call_index]):
            units.append({
                "claim_index": claim_index,
                "source_field": "risk_notes",
                "claim_text": "Do not promote an unobserved inference into a current fact.",
            })
            claim_index += 1

        calls.append({
            "call_index": call_index,
            "split": "DEV",
            "visible_case": {"asset_id": f"asset-visible-{call_index}"},
            "public_contract": {
                "tool_signatures": [f"GET /synthetic-tool-{i}" for i in range(runner.EXPECTED_TOOL_SIGNATURES)],
                "claim_support_labels": sorted(runner.VALID_SUPPORT),
                "claim_types": sorted(runner.VALID_TYPES),
            },
            "claim_units": units,
        })

    return {
        "report_version": runner.EXPECTED_PACKET_VERSION,
        "scope": {
            "split": "DEV",
            "private_oracle_included": False,
            "private_scorer_rows_included": False,
            "validation_material_included": False,
            "locked_test_material_included": False,
        },
        "calls": calls,
    }


def main() -> int:
    packet = synthetic_packet()
    calls = runner.validate_packet(packet)
    assert len(calls) == 6
    assert sum(len(call["claim_units"]) for call in calls) == 66
    assert runner.EXPECTED_CLAIMS == 66
    assert runner.EXPECTED_SOURCE_COUNTS == {
        "action_escalation_rubric.calibration_reason": 12,
        "evidence_plan[]": 39,
        "proposed_next_step": 6,
        "risk_notes": 9,
    }
    assert runner.SYSTEM_PROMPT == runner.parent.SYSTEM_PROMPT
    assert runner.MODEL == runner.parent.MODEL
    assert runner.INTERCALL_SLEEP_SECONDS == runner.parent.INTERCALL_SLEEP_SECONDS == 25
    assert runner.MAX_COMPLETION_TOKENS == runner.parent.MAX_COMPLETION_TOKENS == 2048

    request_payload, case_map = runner.parent.build_request_payload(calls[0])
    assert request_payload["model"] == runner.MODEL
    assert request_payload["temperature"] == 0
    assert request_payload["reasoning_effort"] == "none"
    assert request_payload["response_format"] == {"type": "json_object"}
    assert len(case_map) == len(calls[0]["claim_units"])

    # Historical 69-claim shape must not silently pass this E14o runner.
    wrong = json.loads(json.dumps(packet))
    first = wrong["calls"][0]["claim_units"]
    start = max(unit["claim_index"] for unit in first) + 1
    for offset in range(3):
        first.append({
            "claim_index": start + offset,
            "source_field": "risk_notes",
            "claim_text": "Extra historical-shape claim must be rejected.",
        })
    rejected = False
    try:
        runner.validate_packet(wrong)
    except AssertionError:
        rejected = True
    assert rejected

    # Attempt lock is single-use and contains no raw packet material.
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "e14o-labels.json"
        lock = runner.consume_real_measurement_attempt(out)
        payload = json.loads(lock.read_text(encoding="utf-8"))
        assert payload["report_version"] == runner.LOCK_VERSION
        assert payload["expected_claim_units"] == 66
        assert payload["rerun_allowed"] is False
        second_blocked = False
        try:
            runner.consume_real_measurement_attempt(out)
        except SystemExit:
            second_blocked = True
        assert second_blocked

    print(json.dumps({
        "status": "E9_V4_2_QWEN_E14O_REAL_DEV_RUNNER_STRUCTURAL_SELFCHECK_PASS",
        "expected_calls": 6,
        "expected_claims": 66,
        "historical_69_claim_shape_rejected": True,
        "frozen_judge_prompt_reused": True,
        "single_attempt_lock_pass": True,
        "provider_calls_made": 0,
        "uses_private_oracle": False,
        "uses_validation": False,
        "uses_locked_test": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
