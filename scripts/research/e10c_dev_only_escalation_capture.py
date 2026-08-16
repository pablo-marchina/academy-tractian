#!/usr/bin/env python3
"""E10c DEV-only escalation calibration capture runner.

E10b improved decision/evidence/action on DEV but escalation correctness stayed
0.0. E10c keeps the E10b action rubric and tightens the human-escalation rule:
human escalation is not mutually exclusive with action. It is required when a
visible endpoint or risk profile needs specialist/human handling.

The generated non-dry-run file contains fixed parsed model outputs for private
scorer use. Do not commit real non-dry-run outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

E10B_PATH = Path(__file__).with_name("e10b_dev_only_action_escalation_capture.py")
SPEC = importlib.util.spec_from_file_location("e10b_capture", E10B_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10b_dev_only_action_escalation_capture.py")
e10b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10b)

STRICT_E10C_SYSTEM_PROMPT = """
You are an industrial maintenance agent candidate in a DEV-only escalation-calibration iteration.
Use only the visible case packet and general API/tool contract knowledge already visible in the repository harness.
Do not claim access to hidden expected answers, evaluator gold, LOCKED_TEST, private trajectories, expected-path rows, or scorer oracles.

Return exactly one JSON object, with no Markdown, using this schema:
{
  "decision_class": "investigate_only|action_candidate|escalation_candidate|insufficient_evidence",
  "evidence_plan": ["explicit API/resource-level evidence references"],
  "should_take_action_now": true|false,
  "requires_human_escalation": true|false,
  "proposed_next_step": "concise next step with the next concrete tool/API action",
  "risk_notes": "concise safety/uncertainty notes",
  "trace_quality_self_check": {
    "uses_only_visible_packet": true,
    "no_locked_test": true,
    "no_gold_claim": true
  },
  "action_escalation_rubric": {
    "needs_more_evidence": true|false,
    "safe_to_act": true|false,
    "action_endpoint": "endpoint or none",
    "needs_human_escalation": true|false,
    "calibration_reason": "brief visible-evidence reason"
  }
}

Preserve E10b gains:
- Keep evidence_plan concrete and API/resource-level.
- Keep action correctness: if visible evidence supports a concrete safe endpoint, choose action_candidate and set should_take_action_now=true.
- Keep premature actions at zero: do not invent ids, permissions, severity, hidden labels or private expected-path facts.

Escalation calibration focus:
- Human escalation is not mutually exclusive with action. Many industrial maintenance next steps are both an action and a human/specialist escalation.
- Set requires_human_escalation=true whenever the chosen action_endpoint is POST /analyses/{analysis_id}/request-specialist or POST /cases/{case_id}/escalate.
- Set requires_human_escalation=true when the next step requires specialist review, engineering/human approval, safety/severity judgment, permission-sensitive execution, high operational impact, or a human-in-the-loop before changing asset/model/case state.
- For POST /models/{model_id}/request-retraining, PATCH /assets/{asset_id}, and reprocess actions, set requires_human_escalation=true if the visible packet suggests operations/engineering approval, high-impact maintenance context, ambiguous severity, or specialist confirmation is needed.
- Do not escalate for generic uncertainty alone. Escalate when uncertainty blocks safe autonomous action or when visible risk/impact/permission/specialist handling is material.

Consistency rules:
- If action_escalation_rubric.needs_human_escalation=true, then requires_human_escalation must be true.
- If requires_human_escalation=true, risk_notes must explicitly name the visible reason: safety, severity, specialist review, permission, high impact or human approval.
- If should_take_action_now=true and requires_human_escalation=true, proposed_next_step should name the concrete endpoint and state that it should proceed with human/specialist handling.
- Use escalation_candidate only when human/specialist handling is the primary decision; otherwise action_candidate can still have requires_human_escalation=true.
""".strip()


def e10c_dry_output(packet: dict[str, Any], repeat_index: int) -> tuple[str, dict[str, Any]]:
    output = {
        "decision_class": "action_candidate",
        "evidence_plan": [
            "GET /users/me to confirm permission and requester context",
            "GET /assets/{asset_id} to inspect asset identity, status, site and metadata",
            "GET /assets/{asset_id}/analyses then GET /analyses/{analysis_id} to inspect latest diagnosis evidence",
            "GET /assets/{asset_id}/baseline and GET /assets/{asset_id}/data-quality to compare expected behavior and data trustworthiness",
            "GET /assets/{asset_id}/rms and GET /assets/{asset_id}/spectrum to ground signal severity before action",
            "GET /knowledge/search to support diagnosis and specialist/escalation rationale",
        ],
        "should_take_action_now": True,
        "requires_human_escalation": True,
        "proposed_next_step": "Proceed with the supported action endpoint under human/specialist handling if visible evidence confirms the need.",
        "risk_notes": "DEV-only dry run validates escalation-as-human-in-loop shape; it is not model-quality evidence.",
        "trace_quality_self_check": {
            "uses_only_visible_packet": True,
            "no_locked_test": True,
            "no_gold_claim": True,
        },
        "action_escalation_rubric": {
            "needs_more_evidence": False,
            "safe_to_act": True,
            "action_endpoint": "POST /analyses/{analysis_id}/request-specialist",
            "needs_human_escalation": True,
            "calibration_reason": "Dry-run rubric example; not private-oracle-derived.",
        },
        "e10c_policy": "dev_only_escalation_calibration",
        "repeat_index": repeat_index,
        "packet_hash": e10b.base.stable_hash(packet),
    }
    return json.dumps(output), {"model": "dry_run_e10c_escalation", "usage": {}}


def run(args: argparse.Namespace) -> dict[str, Any]:
    original_prompt = e10b.STRICT_E10B_SYSTEM_PROMPT
    original_dry_output = e10b.e10b_dry_output
    e10b.STRICT_E10B_SYSTEM_PROMPT = STRICT_E10C_SYSTEM_PROMPT
    e10b.e10b_dry_output = e10c_dry_output
    try:
        summary = e10b.run(args)
    finally:
        e10b.STRICT_E10B_SYSTEM_PROMPT = original_prompt
        e10b.e10b_dry_output = original_dry_output

    old_status = summary["status"]
    summary["report_version"] = "e10c-dev-only-escalation-capture-v1"
    summary["status"] = (
        "E10C_DEV_ONLY_ESCALATION_CAPTURE_PASS"
        if old_status == "E10B_DEV_ONLY_ACTION_ESCALATION_CAPTURE_PASS"
        else "E10C_DEV_ONLY_ESCALATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["purpose"] = "DEV-only fixed parsed outputs for escalation calibration scoring"
    summary["quality_policy_changes"] = {
        **summary.get("quality_policy_changes", {}),
        "human_in_loop_not_mutually_exclusive_with_action": True,
        "tighten_escalation_gate": True,
    }
    summary["e9_dev_only_next_command"] = (
        "python scripts/research/e9_evaluator_side_scorer_v3.py "
        "--manifest research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json "
        "--split-manifest research/frozen/benchmark-split-v1.json "
        "--fixed-output-file <this-e10c-file> "
        "--oracle-file <private-eval/expected-paths.json> "
        "--out <e10c-dev-e9-summary.json> --include-rows"
    )
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e10c-dev-only-escalation-calibration-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate E10c DEV-only capture shape without external model calls")
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary["aggregate_metrics"]["total_calls"],
        "parsed_model_outputs_available": summary["aggregate_metrics"]["parsed_model_outputs_available"],
        "validation_ran": summary["scope"]["validation_ran"],
        "dry_run": summary["dry_run"],
    }, indent=2))
    return 0 if args.dry_run or summary["status"] == "E10C_DEV_ONLY_ESCALATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
