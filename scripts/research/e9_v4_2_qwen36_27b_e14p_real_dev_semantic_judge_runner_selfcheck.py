#!/usr/bin/env python3
"""Offline structural self-check for the frozen E14p E9 v4.2 judge runner."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e9_v4_2_qwen36_27b_e14p_real_dev_semantic_judge_runner.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_e14p_runner", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14p real DEV semantic judge runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def synthetic_packet() -> dict:
    # Exact frozen totals over six calls: 24/78/6/18 = 126 claims.
    calls = []
    for call_index in range(6):
        units = []
        claim_index = 0
        for _ in range(4):
            units.append({
                "claim_index": claim_index,
                "source_field": "action_escalation_rubric.calibration_reason",
                "claim_text": "Rubric metadata only; no task-world fact is asserted.",
            })
            claim_index += 1
        for _ in range(13):
            units.append({
                "claim_index": claim_index,
                "source_field": "evidence_plan[]",
                "claim_text": "Retrieve the public resource; treat its result as unobserved until called.",
            })
            claim_index += 1
        units.append({
            "claim_index": claim_index,
            "source_field": "proposed_next_step",
            "claim_text": "Next procedural step: retrieve public evidence before action.",
        })
        claim_index += 1
        for _ in range(3):
            units.append({
                "claim_index": claim_index,
                "source_field": "risk_notes",
                "claim_text": "Do not treat unobserved tool results as established facts.",
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
    assert sum(len(call["claim_units"]) for call in calls) == 126
    assert runner.EXPECTED_CLAIMS == 126
    assert runner.EXPECTED_SOURCE_COUNTS == {
        "action_escalation_rubric.calibration_reason": 24,
        "evidence_plan[]": 78,
        "proposed_next_step": 6,
        "risk_notes": 18,
    }
    assert runner.SYSTEM_PROMPT == runner.parent.SYSTEM_PROMPT
    assert runner.MODEL == runner.parent.MODEL
    assert runner.INTERCALL_SLEEP_SECONDS == runner.parent.INTERCALL_SLEEP_SECONDS == 25
    assert runner.MAX_COMPLETION_TOKENS == runner.parent.MAX_COMPLETION_TOKENS == 2048

    request_payload, case_map = runner.parent.parent.build_request_payload(calls[0])
    assert request_payload["model"] == runner.MODEL
    assert request_payload["temperature"] == 0
    assert request_payload["reasoning_effort"] == "none"
    assert request_payload["response_format"] == {"type": "json_object"}
    assert len(case_map) == len(calls[0]["claim_units"])

    # The previous E14o-sized 66-claim shape must not pass this E14p runner.
    wrong = json.loads(json.dumps(packet))
    for call in wrong["calls"]:
        call["claim_units"] = call["claim_units"][:11]
    assert sum(len(call["claim_units"]) for call in wrong["calls"]) == 66
    rejected = False
    try:
        runner.validate_packet(wrong)
    except AssertionError:
        rejected = True
    assert rejected

    # Attempt lock is single-use and E14p-specific; it stores no raw packet data.
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "e14p-labels.json"
        lock = runner.consume_real_measurement_attempt(out)
        payload = json.loads(lock.read_text(encoding="utf-8"))
        assert payload["report_version"] == runner.LOCK_VERSION
        assert payload["expected_claim_units"] == 126
        assert payload["status"] == "E14P_REAL_DEV_SEMANTIC_MEASUREMENT_ATTEMPT_CONSUMED"
        assert payload["rerun_allowed"] is False
        second_blocked = False
        try:
            runner.consume_real_measurement_attempt(out)
        except SystemExit:
            second_blocked = True
        assert second_blocked

    print(json.dumps({
        "status": "E9_V4_2_QWEN_E14P_REAL_DEV_RUNNER_STRUCTURAL_SELFCHECK_PASS",
        "expected_calls": 6,
        "expected_claims": 126,
        "prior_66_claim_shape_rejected": True,
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
