#!/usr/bin/env python3
"""Oracle-free synthetic validity checks for evaluator v4 semantics."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
V4_PATH = HERE / "e9_evaluator_side_scorer_v4.py"
SPEC = importlib.util.spec_from_file_location("e9_v4", V4_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load evaluator v4")
v4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v4)


def output(*, decision: str, evidence: list[str], act: bool, escalate: bool, endpoint: str) -> dict:
    return {
        "decision_class": decision,
        "evidence_plan": evidence,
        "should_take_action_now": act,
        "requires_human_escalation": escalate,
        "proposed_next_step": "Synthetic next step.",
        "risk_notes": "Synthetic risk notes mentioning human specialist escalation action words without label effect.",
        "trace_quality_self_check": {"uses_only_visible_packet": True, "no_locked_test": True, "no_gold_claim": True},
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": act,
            "action_endpoint": endpoint,
            "needs_human_escalation": escalate,
            "calibration_reason": "Synthetic calibration.",
        },
    }


def call(group: str, payload: dict) -> dict:
    return {"group_id": group, "split": "DEV", "parsed_output": payload, "score": {"task_success_proxy": True}}


def run() -> dict:
    split = {
        "splits": {
            "DEV": {"groups": [{"group_id": "asset_X"}, {"group_id": "asset_Y"}, {"group_id": "asset_Z"}]},
            "VALIDATION": {"groups": []},
            "LOCKED_TEST": {"groups": [{"group_id": "asset_L"}]},
        }
    }
    oracle = [
        {
            "id": "asset_X-row",
            "ticket_id": "synthetic",
            "mode": "execute",
            "root_question": "Should we take action or escalate to a human specialist? This wording must not define the label.",
            "expected_path": [
                {"step": "GET /assets/asset_X", "note": "read"},
                {"step": "POST /analyses/analysis_X/reprocess", "note": "action"},
            ],
        },
        {
            "id": "asset_Y-row",
            "ticket_id": "synthetic",
            "mode": "investigate",
            "root_question": "Execute action specialist human escalation?",
            "expected_path": [
                {"step": "GET /assets/asset_Y", "note": "read only"},
            ],
        },
        {
            "id": "asset_Z-row",
            "ticket_id": "synthetic",
            "mode": "execute",
            "root_question": "Generic question",
            "expected_path": [
                {"step": "GET /analyses/analysis_Z", "note": "read"},
                {"step": "POST /analyses/analysis_Z/request-specialist", "note": "explicit specialist endpoint"},
            ],
        },
    ]

    fixed = {
        "scope": {"locked_test_accessed": False},
        "stage": {
            "calls": [
                call("asset_X", output(
                    decision="action_candidate",
                    evidence=["GET /assets/asset_X"],
                    act=True,
                    escalate=False,
                    endpoint="POST /analyses/analysis_X/reprocess",
                )),
                call("asset_Y", output(
                    decision="investigate_only",
                    evidence=["GET /assets/asset_Y"],
                    act=False,
                    escalate=False,
                    endpoint="none",
                )),
                call("asset_Z", output(
                    decision="escalation_candidate",
                    evidence=["GET /analyses/analysis_Z"],
                    act=True,
                    escalate=True,
                    endpoint="POST /analyses/analysis_Z/request-specialist",
                )),
            ]
        },
    }

    groups = {"asset_X", "asset_Y", "asset_Z"}
    adapted = v4.adapt_expected_paths(oracle, groups, split)
    rows = [v4.score_call(c, adapted.get(c["group_id"])) for c in fixed["stage"]["calls"]]
    if not all(row.get("scoreable") for row in rows):
        raise AssertionError("synthetic valid rows must be scoreable")
    if not all(row.get("decision_correct") for row in rows):
        raise AssertionError("synthetic decision-family semantics failed")
    if not all(row.get("action_correct") for row in rows):
        raise AssertionError("synthetic action semantics failed")
    if not all(row.get("escalation_correct") for row in rows):
        raise AssertionError("synthetic escalation semantics failed")
    if not all(row.get("evidence_correct") for row in rows):
        raise AssertionError("synthetic evidence-plan isolation semantics failed")

    # Whole-output text may not replace missing evidence_plan evidence.
    missing_evidence = output(
        decision="investigate_only",
        evidence=[],
        act=False,
        escalate=False,
        endpoint="none",
    )
    missing_evidence["risk_notes"] = "GET /assets/asset_Y appears here but must not earn evidence credit."
    isolated = v4.score_call(call("asset_Y", missing_evidence), adapted["asset_Y"])
    if isolated.get("evidence_correct") is not False:
        raise AssertionError("v4 must score evidence_plan only")

    # Root-question action/escalation words cannot create expected labels.
    y_oracle = adapted["asset_Y"]
    if y_oracle["expected_action_signatures"] or y_oracle["expected_escalation_signatures"]:
        raise AssertionError("root_question wording leaked into expected labels")

    # Unsupported action must be detected against expected action signatures.
    unsupported = output(
        decision="action_candidate",
        evidence=["GET /assets/asset_Y"],
        act=True,
        escalate=False,
        endpoint="POST /models/model_Y/request-retraining",
    )
    bad = v4.score_call(call("asset_Y", unsupported), y_oracle)
    if bad.get("action_correct") is not False or bad.get("unsupported_action_or_escalation") is not True:
        raise AssertionError("unsupported action detection failed")

    # End-to-end file run must remain aggregate-only and measurement-only.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        split_path = root / "split.json"
        fixed_path = root / "fixed.json"
        oracle_path = root / "oracle.json"
        out_path = root / "out.json"
        split_path.write_text(json.dumps(split), encoding="utf-8")
        fixed_path.write_text(json.dumps(fixed), encoding="utf-8")
        oracle_path.write_text(json.dumps(oracle), encoding="utf-8")
        args = type("Args", (), {
            "split_manifest": split_path,
            "fixed_output_file": fixed_path,
            "oracle_file": oracle_path,
            "out": out_path,
        })()
        summary = v4.run(args)
        if summary["aggregate_metrics"]["scoreable_calls"] != 3:
            raise AssertionError("v4 synthetic end-to-end scoreable count failed")
        if summary["validity"]["validation_gate_authorized"] is not False:
            raise AssertionError("v4 must remain measurement-only before granularity gate")
        if "rows" in summary or "calls" in summary:
            raise AssertionError("v4 summary must not persist private per-call rows")

    return {
        "status": "E9_V4_SYNTHETIC_VALIDITY_SELF_CHECK_PASS",
        "root_question_confound_blocked": True,
        "evidence_plan_isolation_pass": True,
        "deterministic_action_signature_pass": True,
        "deterministic_explicit_escalation_signature_pass": True,
        "unsupported_action_detection_pass": True,
        "private_rows_persisted": False,
        "validation_gate_authorized": False,
        "uses_validation": False,
        "uses_locked_test": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
