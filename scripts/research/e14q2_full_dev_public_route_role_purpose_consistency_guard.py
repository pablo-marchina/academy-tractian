#!/usr/bin/env python3
"""E14q2 full-DEV public route-role and explicit-purpose consistency guard.

Incremental deterministic successor to E14q. It is provider-free and reads only
fixed public output fields plus the public tool registry. No private expected
paths, scorer rows, semantic judge rows, VALIDATION, or LOCKED_TEST are read.

The guard is fail-closed and never promotes action/escalation. It preserves the
entire evidence_plan and all E9 v4.2 free-text claim-source fields byte-for-byte.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
PARENT_PATH = HERE / "e14q_full_dev_public_action_authorization_consistency_guard.py"
SPEC = importlib.util.spec_from_file_location("e14q_parent_for_e14q2", PARENT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14q parent guard")
parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parent)

v41 = parent.v41
v4 = parent.v4
EXPECTED_CALLS = 10
PASS_STATUS = "E14Q2_FULL_DEV_PUBLIC_ROUTE_ROLE_PURPOSE_CONSISTENCY_GUARD_PASS"
FAIL_STATUS = "E14Q2_FULL_DEV_PUBLIC_ROUTE_ROLE_PURPOSE_CONSISTENCY_GUARD_NEEDS_REVIEW"

HANDOFF_ACTIONS = set(parent.HANDOFF_ACTIONS)
NON_HANDOFF_ACTIONS = set(parent.SUPPORTED_ACTIONS) - HANDOFF_ACTIONS
SUPPORTED_ACTIONS = set(parent.SUPPORTED_ACTIONS)

ACTION_INTENT_MARKERS: dict[str, tuple[str, ...]] = {
    "POST /analyses/{analysisId}/reprocess": (
        "reprocess",
        "reprocessing",
        "re-run analysis",
        "rerun analysis",
    ),
    "POST /analyses/{analysisId}/request-specialist": (
        "request-specialist",
        "specialist",
        "human review",
        "human handoff",
    ),
    "POST /models/{modelId}/request-retraining": (
        "request-retraining",
        "retrain",
        "retraining",
        "model retrain",
    ),
    "PATCH /assets/{assetId}": (
        "patch /assets",
        "patch asset",
        "update asset",
        "asset update",
    ),
    "POST /cases/{caseId}/escalate": (
        "post /cases/",
        "case escalate",
        "escalate case",
        "case escalation",
    ),
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_source_signature(output: dict[str, Any]) -> tuple[Any, ...]:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    return (
        copy.deepcopy(output.get("evidence_plan")),
        output.get("proposed_next_step"),
        output.get("risk_notes"),
        rubric.get("calibration_reason"),
        copy.deepcopy(output.get("trace_quality_self_check")),
    )


def _consistency_text(output: dict[str, Any]) -> str:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    return "\n".join(
        str(value or "")
        for value in (
            output.get("proposed_next_step"),
            output.get("risk_notes"),
            rubric.get("calibration_reason"),
        )
    )


def _explicit_free_text_actions(output: dict[str, Any]) -> set[str]:
    text = _consistency_text(output)
    found: set[str] = set()
    for signature, kind in v41.canonical_tool_signatures(text, require_method=True):
        if kind == "action":
            found.add(signature)
    return found


def _purpose_coherence_reason(output: dict[str, Any], endpoint: str | None) -> str | None:
    if endpoint is None:
        return "action_true_without_public_action_endpoint"
    if endpoint not in SUPPORTED_ACTIONS:
        return "action_endpoint_not_supported_public_action"

    explicit_actions = _explicit_free_text_actions(output)
    if explicit_actions:
        if endpoint not in explicit_actions:
            return "endpoint_conflicts_with_explicit_free_text_action_signature"
        if len(explicit_actions) > 1:
            return "multiple_explicit_action_purposes_visible"
        return None

    lowered = _consistency_text(output).lower()
    markers = ACTION_INTENT_MARKERS.get(endpoint, ())
    if not any(marker in lowered for marker in markers):
        return "endpoint_family_lacks_explicit_public_intent_marker"
    return None


def public_consistency_failure_reason(output: dict[str, Any]) -> str | None:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = parent._action_endpoint(output)
    action_now = output.get("should_take_action_now") is True
    escalation = output.get("requires_human_escalation") is True
    decision = str(output.get("decision_class") or "")

    if not action_now and endpoint is not None:
        return "non_action_output_carries_state_change_endpoint"

    if escalation:
        if not action_now:
            return "escalation_true_without_action_now"
        if decision != "escalation_candidate":
            return "escalation_true_without_escalation_candidate_decision"
        if endpoint not in HANDOFF_ACTIONS:
            return "escalation_true_without_handoff_endpoint"

    if endpoint in HANDOFF_ACTIONS:
        if not action_now:
            return "handoff_endpoint_without_action_now"
        if not escalation:
            return "handoff_endpoint_without_escalation_flag"
        if decision != "escalation_candidate":
            return "handoff_endpoint_without_escalation_candidate_decision"

    if endpoint in NON_HANDOFF_ACTIONS:
        if not action_now:
            return "state_change_endpoint_without_action_now"
        if escalation:
            return "non_handoff_action_with_escalation_flag"
        if decision != "action_candidate":
            return "non_handoff_action_without_action_candidate_decision"

    if action_now:
        purpose_reason = _purpose_coherence_reason(output, endpoint)
        if purpose_reason is not None:
            return purpose_reason

    # A candidate decision may be prospective when action_now is false, so we
    # do not promote or demote solely from candidate class without an active
    # action/escalation inconsistency.
    return None


def transform_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(output)
    result = copy.deepcopy(output)
    reason = public_consistency_failure_reason(before)
    changed = False
    endpoint_cleared = False
    action_demoted = False
    escalation_demoted = False
    decision_changed = False

    if reason is not None:
        rubric = result.get("action_escalation_rubric")
        if not isinstance(rubric, dict):
            rubric = {}
            result["action_escalation_rubric"] = rubric

        if result.get("should_take_action_now") is True:
            result["should_take_action_now"] = False
            action_demoted = True
            changed = True
        if result.get("requires_human_escalation") is True:
            result["requires_human_escalation"] = False
            escalation_demoted = True
            changed = True
        if rubric.get("action_endpoint") != "none":
            rubric["action_endpoint"] = "none"
            endpoint_cleared = True
            changed = True
        if rubric.get("safe_to_act") is not False:
            rubric["safe_to_act"] = False
            changed = True
        if rubric.get("needs_more_evidence") is not True:
            rubric["needs_more_evidence"] = True
            changed = True
        if str(result.get("decision_class") or "") in {"action_candidate", "escalation_candidate"}:
            result["decision_class"] = "investigate_only"
            decision_changed = True
            changed = True

    evidence_preserved = before.get("evidence_plan") == result.get("evidence_plan")
    free_text_preserved = _claim_source_signature(before) == _claim_source_signature(result)
    return result, {
        "failure_reason": reason,
        "changed": changed,
        "action_demoted": action_demoted,
        "escalation_demoted": escalation_demoted,
        "endpoint_cleared": endpoint_cleared,
        "decision_changed": decision_changed,
        "evidence_plan_preserved": evidence_preserved,
        "v4_2_free_text_and_trace_preserved": free_text_preserved,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    fixed = _load(args.fixed_output_file)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be objects")

    transformed = copy.deepcopy(fixed)
    calls = v4.collect_calls(transformed)
    v4.assert_fixed_scope(transformed, calls, split_manifest)
    if len(calls) != EXPECTED_CALLS:
        raise AssertionError(f"E14q2 requires exactly {EXPECTED_CALLS} fixed full-DEV calls")

    parsed = 0
    calls_changed = 0
    action_demotions = 0
    escalation_demotions = 0
    endpoint_clears = 0
    decision_changes = 0
    evidence_changes = 0
    free_text_changes = 0
    reason_counts: Counter[str] = Counter()

    for call in calls:
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        parsed += 1
        guarded, meta = transform_output(output)
        calls_changed += int(meta["changed"])
        action_demotions += int(meta["action_demoted"])
        escalation_demotions += int(meta["escalation_demoted"])
        endpoint_clears += int(meta["endpoint_cleared"])
        decision_changes += int(meta["decision_changed"])
        evidence_changes += int(not meta["evidence_plan_preserved"])
        free_text_changes += int(not meta["v4_2_free_text_and_trace_preserved"])
        if meta["failure_reason"]:
            reason_counts[str(meta["failure_reason"])] += 1
        call["parsed_output"] = guarded

    complete = parsed == EXPECTED_CALLS
    passed = complete and evidence_changes == 0 and free_text_changes == 0
    status = PASS_STATUS if passed else FAIL_STATUS

    transformed["report_version"] = "e14q2-full-dev-public-route-role-purpose-consistency-v1"
    transformed["status"] = status
    transformed["e14q2_public_route_role_purpose_consistency"] = {
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "complete_fixed_transform": complete,
        "calls_changed": calls_changed,
        "action_demotions": action_demotions,
        "escalation_demotions": escalation_demotions,
        "action_endpoints_cleared": endpoint_clears,
        "decision_class_changes": decision_changes,
        "consistency_failure_reason_counts": dict(sorted(reason_counts.items())),
        "evidence_plan_changes": evidence_changes,
        "v4_2_free_text_or_trace_changes": free_text_changes,
        "promotions_made": 0,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "semantic_judge_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "validation_gate_authorized": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(transformed, indent=2), encoding="utf-8")

    return {
        "report_version": transformed["report_version"],
        "status": status,
        **transformed["e14q2_public_route_role_purpose_consistency"],
        "raw_outputs_printed": False,
        "claim_text_printed": False,
        "identifiers_printed": False,
        "group_ids_printed": False,
        "hashes_printed": False,
        "private_paths_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
