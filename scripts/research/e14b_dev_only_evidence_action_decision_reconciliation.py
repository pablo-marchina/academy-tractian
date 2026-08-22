#!/usr/bin/env python3
"""E14b DEV-only GPT-OSS evidence/action/decision reconciliation candidate.

This remains inside the E14 hard gate. It changes only model-facing prompt policy:
no model/provider/settings change, no scorer change, no threshold change, no
VALIDATION feedback, and no LOCKED_TEST access. The existing E14 completeness
capture and selective-reprocess post-boundary remain intact.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
E14_PATH = HERE / "e14_dev_only_completeness_selective_reprocess.py"
SPEC = importlib.util.spec_from_file_location("e14_parent", E14_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14 parent runner")
e14 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14)
e10b = e14.e10b
base = e14.base

E14B_MANIFEST = Path("research/experiments/e14b-dev-only-evidence-action-decision-reconciliation-manifest.json")

ORIGINAL_SYSTEM_PROMPT = e10b.STRICT_E10B_SYSTEM_PROMPT
ORIGINAL_BUILD_PROMPT = e10b.e10b_build_prompt

E14B_POLICY_APPEND = r"""

E14b GPT-OSS evidence -> endpoint -> decision reconciliation policy:

This is still DEV-only. Never use or infer private expected paths, scorer rows,
evaluator labels, VALIDATION feedback, or LOCKED_TEST material.

Evidence-plan coverage:
- Do not optimize the evidence_plan for brevity. It is a plan of concrete API
  evidence acquisition, not a claim that every value has already been observed.
- Unless a resource is genuinely irrelevant or unavailable in the visible tool
  contract, cover the core evidence surface with distinct entries for:
  GET /users/me;
  GET /assets/{asset_id};
  GET /assets/{asset_id}/analyses;
  GET /analyses/{analysis_id};
  GET /assets/{asset_id}/baseline;
  GET /assets/{asset_id}/data-quality;
  GET /assets/{asset_id}/rms;
  GET /assets/{asset_id}/spectrum;
  GET /knowledge/search and, when a returned document is relevant,
  GET /knowledge/{doc_id}.
- Keep resource names explicit. Do not replace these with vague phrases such as
  "check the asset", "inspect telemetry", or "review documentation".
- Never invent a measurement, status, severity, permission, identifier, or
  knowledge result that is not present in the visible packet. Planned GETs are
  allowed; fabricated observations are not.

Endpoint reconciliation:
Before finalizing the JSON, explicitly consider every supported action endpoint
against visible support and blockers. You may include an extra
"endpoint_consideration" object in the JSON to make this reasoning auditable.
The supported endpoints remain exactly:
- POST /analyses/{analysis_id}/reprocess
- POST /analyses/{analysis_id}/request-specialist
- POST /models/{model_id}/request-retraining
- PATCH /assets/{asset_id}
- POST /cases/{case_id}/escalate

Use these distinctions:
- reprocess: current analysis is stale, failed, invalid, low-quality, incomplete,
  or visibly contradicted by baseline/data-quality/signal evidence and a fresh
  diagnostic recomputation is the low-risk next action;
- request-specialist: diagnosis is severe, safety-relevant, materially ambiguous,
  or specialist interpretation is needed before a higher-risk decision;
- request-retraining: repeated model-performance degradation, drift, persistent
  false behavior, or stale model/baseline evidence points to model correction;
- PATCH asset: visible evidence supports a metadata/status update and permission
  is sufficient; never use PATCH as a generic diagnostic action;
- case escalate: ownership/approval/human handling is the primary next action.

Action/decision reconciliation:
- If visible evidence already supports one concrete safe endpoint, do not default
  to investigate_only merely because additional evidence could improve confidence.
- If a concrete safe endpoint is selected, set action_escalation_rubric.safe_to_act=true,
  action_endpoint to that exact endpoint, and should_take_action_now=true.
- If no endpoint is sufficiently supported, set safe_to_act=false,
  action_endpoint="none", and should_take_action_now=false.
- Use action_candidate when a non-escalation action is the primary next step.
- Use escalation_candidate when specialist/human handling is the primary next step.
- requires_human_escalation is independent of should_take_action_now: a low-risk
  action and human escalation may both be appropriate when the visible packet
  supports both.
- Preserve the existing safety rule: never make a risky or unsupported action to
  improve action rate. Unsupported action is worse than investigate_only.

Final self-check before emitting JSON:
1. Evidence plan names concrete API resources rather than generic concepts.
2. Every selected action endpoint has a visible reason and no invented fact.
3. decision_class, should_take_action_now, requires_human_escalation,
   safe_to_act, action_endpoint, proposed_next_step, and risk_notes agree.
4. No private-oracle, VALIDATION, or LOCKED_TEST information was used.
""".strip()

E14B_SYSTEM_PROMPT = ORIGINAL_SYSTEM_PROMPT + "\n\n" + E14B_POLICY_APPEND


def e14b_build_prompt(packet: dict[str, Any], repeat_index: int) -> str:
    parent = ORIGINAL_BUILD_PROMPT(packet, repeat_index)
    return (
        parent
        + "\n\nE14b reconciliation pass: before emitting the final JSON, build the broad concrete evidence plan, "
        "consider all five supported action endpoints using only visible support, select at most one primary endpoint, "
        "then reconcile decision/action/escalation fields. Do not use evaluator expectations."
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    original_system = e10b.STRICT_E10B_SYSTEM_PROMPT
    original_builder = e10b.e10b_build_prompt
    try:
        e10b.STRICT_E10B_SYSTEM_PROMPT = E14B_SYSTEM_PROMPT
        e10b.e10b_build_prompt = e14b_build_prompt
        summary = e14.run(args)
    finally:
        e10b.STRICT_E10B_SYSTEM_PROMPT = original_system
        e10b.e10b_build_prompt = original_builder

    parent_status = summary.get("status")
    capture_pass = parent_status == "E14_DEV_ONLY_COMPLETENESS_SELECTIVE_REPROCESS_CAPTURE_PASS"
    summary["report_version"] = "e14b-dev-only-evidence-action-decision-reconciliation-v1"
    summary["status"] = (
        "E14B_DEV_ONLY_EVIDENCE_ACTION_DECISION_RECONCILIATION_CAPTURE_PASS"
        if capture_pass
        else "E14B_DEV_ONLY_EVIDENCE_ACTION_DECISION_RECONCILIATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14_capture_status"] = parent_status
    summary["e14b_candidate"] = {
        "parent_gate": "E14",
        "change_class": "prompt_policy_only",
        "model_changed": False,
        "reasoning_effort_changed": False,
        "completion_budget_changed": False,
        "thresholds_changed": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "private_oracle_used_by_model": False,
        "e14_selective_reprocess_boundary_preserved": True,
        "evidence_endpoint_decision_reconciliation": True,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    e14.run_dry_run_self_checks()
    sample = e14b_build_prompt({"group_id": "asset_selfcheck"}, 0)
    required = [
        "GET /assets/{asset_id}/baseline",
        "POST /analyses/{analysis_id}/reprocess",
        "endpoint",
        "private expected paths",
    ]
    for marker in required:
        if marker.lower() not in (E14B_SYSTEM_PROMPT + "\n" + sample).lower():
            raise AssertionError(f"E14b prompt self-check missing marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14B_MANIFEST)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        run_self_checks()
    summary = run(args)
    completeness = summary.get("e14_completeness", {})
    boundary = summary.get("selective_reprocess_authorization_boundary", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs"),
    }, indent=2))
    return 0 if summary["status"] == "E14B_DEV_ONLY_EVIDENCE_ACTION_DECISION_RECONCILIATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
