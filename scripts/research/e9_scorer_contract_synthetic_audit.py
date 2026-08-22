#!/usr/bin/env python3
"""Synthetic, oracle-free audit of E9 v3 scorer semantics.

This script does not read private expected paths, fixed benchmark outputs,
VALIDATION, or LOCKED_TEST. It probes the frozen scorer with synthetic examples
to identify places where substring/lexical heuristics can diverge from the
semantic meaning suggested by metric names.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
V3_PATH = HERE / "e9_evaluator_side_scorer_v3.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v3 = load_module("e9_v3_for_synthetic_audit", V3_PATH)
v2 = v3.e9_v2


def _output(**overrides: Any) -> dict[str, Any]:
    base = {
        "decision_class": "investigate_only",
        "evidence_plan": [],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Investigate before acting.",
        "risk_notes": "No unsupported private references.",
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
            "calibration_reason": "More evidence is required.",
        },
    }
    base.update(overrides)
    return base


def run() -> dict[str, Any]:
    negative_escalation = v2.infer_flags({
        "root_question": "What should happen next?",
        "expected_path": ["Human escalation is not required; continue investigation."],
    })
    negative_action = v2.infer_flags({
        "root_question": "What should happen next?",
        "expected_path": ["Do not reprocess or execute an action yet; investigate first."],
    })
    question_only_action = v2.infer_flags({
        "root_question": "Should we take action now?",
        "expected_path": ["Investigate the evidence first and do not change state."],
    })
    conditional_escalation = v2.infer_flags({
        "root_question": "What should happen next?",
        "expected_path": ["Request specialist review only if later evidence shows material risk."],
    })

    lexical_oracle = {
        "oracle_format": "synthetic",
        "private_row_count": 1,
        "private_expected_path_item_count": 1,
        "allowed_decision_classes": ["investigate_only"],
        "required_evidence_terms": ["bearing", "temperature", "vibration"],
        "expected_should_take_action_now": False,
        "expected_requires_human_escalation": False,
    }
    evidence_outside_plan = _output(
        evidence_plan=[],
        risk_notes="Bearing temperature and vibration are mentioned here, outside the evidence plan.",
    )
    evidence_score = v2.score_call({"group_id": "asset_synthetic", "split": "DEV", "parsed_output": evidence_outside_plan}, lexical_oracle)

    unsupported_semantic_claim = _output(
        proposed_next_step="The machine will definitely fail tomorrow even though no visible evidence establishes that conclusion.",
    )
    claim_score = v2.score_call({"group_id": "asset_synthetic", "split": "DEV", "parsed_output": unsupported_semantic_claim}, {
        **lexical_oracle,
        "required_evidence_terms": [],
    })

    findings = {
        "negative_escalation_phrase_sets_expected_escalation_true": negative_escalation.get("expected_requires_human_escalation") is True,
        "negative_action_phrase_sets_expected_action_true": negative_action.get("expected_should_take_action_now") is True,
        "root_question_action_word_can_set_expected_action_true": question_only_action.get("expected_should_take_action_now") is True,
        "conditional_specialist_phrase_sets_expected_escalation_true": conditional_escalation.get("expected_requires_human_escalation") is True,
        "evidence_terms_outside_evidence_plan_can_satisfy_evidence_correctness": evidence_score.get("evidence_correct") is True,
        "semantic_unsupported_claim_not_detected_by_unsupported_final_claim_metric": claim_score.get("unsupported_final_claim") is False,
    }

    return {
        "status": "E9_SYNTHETIC_SCORER_CONTRACT_AUDIT_FINDINGS_PRESENT" if any(findings.values()) else "E9_SYNTHETIC_SCORER_CONTRACT_AUDIT_NO_FINDINGS",
        "scorer_under_audit": "e9_evaluator_side_scorer_v3_via_v2_semantics",
        "findings": findings,
        "finding_count": sum(1 for value in findings.values() if value),
        "interpretation": (
            "The frozen E9 v3 scorer is useful for historical DEV comparability but its action/escalation and evidence/unsupported-claim metrics rely on lexical heuristics that can diverge from ordinary semantic interpretation. Do not change E9 inside E14m-R1; require a scorer-validity review before any VALIDATION or final architecture gate."
        ),
        "changes_scorer": False,
        "reads_private_oracle": False,
        "reads_fixed_benchmark_outputs": False,
        "uses_validation": False,
        "uses_locked_test": False,
        "prints_private_values": False,
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
