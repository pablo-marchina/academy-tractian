#!/usr/bin/env python3
"""Oracle-free synthetic regression checks for evaluator v4.1 bugfixes."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
V41_PATH = HERE / "e9_evaluator_side_scorer_v4_1.py"
SPEC = importlib.util.spec_from_file_location("e9_v41", V41_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load evaluator v4.1")
v41 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v41)


def output(*, evidence: list[str], risk_notes: str = "Synthetic risk.") -> dict:
    return {
        "decision_class": "investigate_only",
        "evidence_plan": evidence,
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Synthetic next step.",
        "risk_notes": risk_notes,
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "action_endpoint": "none",
            "needs_human_escalation": False,
            "calibration_reason": "Synthetic calibration.",
        },
    }


def call(group: str, payload: dict) -> dict:
    return {"group_id": group, "split": "DEV", "parsed_output": payload}


def run() -> dict:
    # Segment parser must tolerate punctuation/markup and must choose the more
    # specific literal route over /knowledge/{docId} when path is /knowledge/search.
    cases = [
        ("GET `/assets/asset_X/baseline`.", "GET /assets/{assetId}/baseline"),
        ("GET: /assets/asset_X/data-quality);", "GET /assets/{assetId}/data-quality"),
        ("GET /knowledge/search?q=vibration", "GET /knowledge/search"),
        ("POST /analyses/analysis_X/request-specialist.", "POST /analyses/{analysisId}/request-specialist"),
    ]
    for text, expected in cases:
        matches = v41.canonical_tool_signatures(text)
        signatures = [sig for sig, _kind in matches]
        if expected not in signatures:
            raise AssertionError(f"expected canonical signature not found for synthetic text: {expected}")
    knowledge = [sig for sig, _kind in v41.canonical_tool_signatures("GET /knowledge/search")]
    if knowledge != ["GET /knowledge/search"]:
        raise AssertionError("literal specificity must prevent /knowledge/search from matching /knowledge/{docId}")

    multi = [sig for sig, kind in v41.canonical_tool_signatures(
        "GET /assets/asset_X then GET /assets/asset_X/baseline"
    ) if kind == "read"]
    if set(multi) != {"GET /assets/{assetId}", "GET /assets/{assetId}/baseline"}:
        raise AssertionError("multiple METHOD+path signatures in one evidence item must all be extracted")

    split = {
        "splits": {
            "DEV": {"groups": [{"group_id": "asset_X"}, {"group_id": "asset_Y"}]},
            "VALIDATION": {"groups": []},
            "LOCKED_TEST": {"groups": [{"group_id": "asset_L"}]},
        }
    }
    agent_cases = [
        {"case_id": "case-x", "ticket_id": "ticket-x", "asset_id": "asset_X"},
        {"case_id": "case-y", "ticket_id": "ticket-y", "asset_id": "asset_Y"},
    ]
    oracle = [
        {
            "id": "asset_X-row",
            "ticket_id": "ticket-x",
            "mode": "investigate",
            "root_question": "Synthetic",
            "expected_path": [
                {"step": "GET `/assets/asset_X/baseline`.", "note": "synthetic"},
            ],
        },
        {
            "id": "asset_Y-row",
            "ticket_id": "ticket-y",
            "mode": "investigate",
            "root_question": "Synthetic",
            "expected_path": [
                {"step": "GET: /assets/asset_Y/data-quality);", "note": "synthetic"},
            ],
        },
    ]
    fixed = {
        "scope": {"locked_test_accessed": False},
        "stage": {"calls": [
            call("asset_X", output(evidence=["GET /assets/asset_X/baseline"])),
            call("asset_Y", output(evidence=["GET /assets/asset_Y/data-quality"])),
        ]},
    }

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        split_path = root / "split.json"
        fixed_path = root / "fixed.json"
        oracle_path = root / "oracle.json"
        cases_path = root / "cases.json"
        out_path = root / "out.json"
        split_path.write_text(json.dumps(split), encoding="utf-8")
        fixed_path.write_text(json.dumps(fixed), encoding="utf-8")
        oracle_path.write_text(json.dumps(oracle), encoding="utf-8")
        cases_path.write_text(json.dumps(agent_cases), encoding="utf-8")
        args = type("Args", (), {
            "split_manifest": split_path,
            "fixed_output_file": fixed_path,
            "oracle_file": oracle_path,
            "agent_input_cases": cases_path,
            "out": out_path,
        })()
        summary = v41.run(args)
        if summary["status"] != "E9_V4_1_MEASUREMENT_ONLY_PASS":
            raise AssertionError("complete synthetic measurement must PASS")
        if summary["aggregate_metrics"]["scoreable_calls"] != 2:
            raise AssertionError("all complete synthetic calls must be scoreable")
        if summary["validity"]["expected_step_normalization_resolved_for_aligned_rows"] is not True:
            raise AssertionError("synthetic expected steps must normalize completely")
        if summary["aggregate_metrics"]["locked_test_or_gold_leakage_rate"] != 0.0:
            raise AssertionError("required no_locked_test key must not create leakage false positive")

        # A real string value mentioning locked_test must still be detected.
        leaking_fixed = json.loads(json.dumps(fixed))
        leaking_fixed["stage"]["calls"][0]["parsed_output"]["risk_notes"] = "I inspected locked_test data."
        fixed_path.write_text(json.dumps(leaking_fixed), encoding="utf-8")
        leaking = v41.run(args)
        if leaking["aggregate_metrics"]["locked_test_or_gold_leakage_rate"] != 0.5:
            raise AssertionError("locked_test mention in a string value must be detected")

        # Partial scoreability must never receive PASS.
        partial_oracle = [oracle[0]]
        oracle_path.write_text(json.dumps(partial_oracle), encoding="utf-8")
        fixed_path.write_text(json.dumps(fixed), encoding="utf-8")
        partial = v41.run(args)
        if partial["aggregate_metrics"]["scoreable_calls"] != 1:
            raise AssertionError("synthetic partial case must have exactly one scoreable call")
        if partial["status"] != "E9_V4_1_MEASUREMENT_ONLY_NEEDS_REVIEW":
            raise AssertionError("partial scoreability must emit NEEDS_REVIEW")
        if partial["validity"]["complete_fixed_measurement"] is not False:
            raise AssertionError("partial scoreability must not be complete")

    return {
        "status": "E9_V4_1_SYNTHETIC_STRUCTURAL_REGRESSION_PASS",
        "segment_exact_path_normalization_pass": True,
        "literal_specificity_disambiguation_pass": True,
        "multi_signature_extraction_pass": True,
        "schema_key_leakage_false_positive_blocked": True,
        "string_value_leakage_detection_preserved": True,
        "partial_scoreability_pass_blocked": True,
        "uses_private_oracle": False,
        "uses_validation": False,
        "uses_locked_test": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
