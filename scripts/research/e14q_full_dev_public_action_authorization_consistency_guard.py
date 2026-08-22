#!/usr/bin/env python3
"""E14q full-DEV deterministic public action-authorization consistency guard.

Applies a single paired post-processing intervention to the fixed E14p full-DEV
outputs. It reads only the public output contract encoded in the output and the
public tool registry through E9 v4.1 canonical tool signatures. It never reads
private expected paths, scorer rows, semantic judge rows, VALIDATION, or
LOCKED_TEST.

E14q deliberately preserves evidence_plan and every v4.2 free-text source field.
Only deterministic decision/action/escalation state is changed.
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
V41_PATH = HERE / "e9_evaluator_side_scorer_v4_1.py"
SPEC = importlib.util.spec_from_file_location("e9_v41_for_e14q", V41_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load frozen E9 v4.1 public signature parser")
v41 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v41)
v4 = v41.v4

EXPECTED_CALLS = 10
PASS_STATUS = "E14Q_FULL_DEV_PUBLIC_ACTION_AUTHORIZATION_CONSISTENCY_GUARD_PASS"
FAIL_STATUS = "E14Q_FULL_DEV_PUBLIC_ACTION_AUTHORIZATION_CONSISTENCY_GUARD_NEEDS_REVIEW"

SUPPORTED_ACTIONS = {
    "POST /analyses/{analysisId}/reprocess",
    "POST /analyses/{analysisId}/request-specialist",
    "POST /models/{modelId}/request-retraining",
    "PATCH /assets/{assetId}",
    "POST /cases/{caseId}/escalate",
}
HANDOFF_ACTIONS = {
    "POST /analyses/{analysisId}/request-specialist",
    "POST /cases/{caseId}/escalate",
}
COMMON_AUTH_READ = "GET /users/me"
TARGET_READ_REQUIRED = {
    "POST /analyses/{analysisId}/reprocess": "GET /analyses/{analysisId}",
    "POST /analyses/{analysisId}/request-specialist": "GET /analyses/{analysisId}",
    "POST /models/{modelId}/request-retraining": "GET /models/{modelId}",
    "PATCH /assets/{assetId}": "GET /assets/{assetId}",
}
CASE_ESCALATION_DIAGNOSTIC_READS = {
    "GET /assets/{assetId}",
    "GET /assets/{assetId}/analyses",
    "GET /analyses/{analysisId}",
    "GET /assets/{assetId}/baseline",
    "GET /assets/{assetId}/rms",
    "GET /assets/{assetId}/spectrum",
    "GET /assets/{assetId}/data-quality",
    "GET /models/{modelId}",
    "GET /knowledge/search",
    "GET /knowledge/{docId}",
}
VISIBLE_HUMAN_REASON_MARKERS = (
    "safety",
    "severity",
    "specialist",
    "human review",
    "human approval",
    "permission",
    "approval",
    "high impact",
    "safety-critical",
    "segurança",
    "severidade",
    "especialista",
    "revisão humana",
    "aprovação",
    "permissão",
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _output_free_text_signature(output: dict[str, Any]) -> tuple[Any, ...]:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    plan = output.get("evidence_plan")
    return (
        copy.deepcopy(plan),
        output.get("proposed_next_step"),
        output.get("risk_notes"),
        rubric.get("calibration_reason"),
        copy.deepcopy(output.get("trace_quality_self_check")),
    )


def _observed_reads(output: dict[str, Any]) -> set[str]:
    reads: set[str] = set()
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return reads
    for item in plan:
        if not isinstance(item, str):
            continue
        for signature, kind in v41.canonical_tool_signatures(item, require_method=True):
            if kind == "read":
                reads.add(signature)
    return reads


def _action_endpoint(output: dict[str, Any]) -> str | None:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    raw = rubric.get("action_endpoint")
    if not isinstance(raw, str):
        return None
    signature, kind = v41.canonical_tool_signature(raw, require_method=True)
    return signature if kind == "action" else None


def _visible_human_reason(output: dict[str, Any]) -> bool:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    text = "\n".join(
        str(value or "")
        for value in (
            output.get("risk_notes"),
            rubric.get("calibration_reason"),
        )
    ).lower()
    return any(marker in text for marker in VISIBLE_HUMAN_REASON_MARKERS)


def authorization_failure_reason(output: dict[str, Any]) -> str | None:
    if output.get("should_take_action_now") is not True:
        return None

    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = _action_endpoint(output)
    reads = _observed_reads(output)

    if rubric.get("safe_to_act") is not True:
        return "safe_to_act_not_true"
    if rubric.get("needs_more_evidence") is not False:
        return "needs_more_evidence_not_false"
    if endpoint not in SUPPORTED_ACTIONS:
        return "no_supported_public_action_endpoint"
    if COMMON_AUTH_READ not in reads:
        return "missing_users_me_authorization_read"

    target_read = TARGET_READ_REQUIRED.get(endpoint)
    if target_read is not None and target_read not in reads:
        return "missing_endpoint_specific_target_read"

    if endpoint == "POST /cases/{caseId}/escalate" and not (reads & CASE_ESCALATION_DIAGNOSTIC_READS):
        return "case_escalation_missing_diagnostic_read"
    return None


def transform_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(output)
    result = copy.deepcopy(output)
    rubric = result.get("action_escalation_rubric")
    if not isinstance(rubric, dict):
        rubric = {}
        result["action_escalation_rubric"] = rubric

    original_endpoint = _action_endpoint(before)
    reason = authorization_failure_reason(before)
    endpoint_cleared = False
    action_demoted = False
    escalation_demoted = False
    decision_changed = False

    # State consistency: a non-action output must not carry a live state-change endpoint.
    if before.get("should_take_action_now") is not True and original_endpoint is not None:
        rubric["action_endpoint"] = "none"
        endpoint_cleared = True

    if reason is not None:
        if result.get("should_take_action_now") is True:
            result["should_take_action_now"] = False
            action_demoted = True
        if rubric.get("action_endpoint") != "none":
            rubric["action_endpoint"] = "none"
            endpoint_cleared = True
        rubric["safe_to_act"] = False
        rubric["needs_more_evidence"] = True
        if str(result.get("decision_class") or "") == "action_candidate":
            result["decision_class"] = "investigate_only"
            decision_changed = True

    # Human escalation must have public visible support. Once an endpoint is
    # cleared, the endpoint itself no longer authorizes the escalation flag.
    current_endpoint = _action_endpoint(result)
    human_supported = current_endpoint in HANDOFF_ACTIONS or _visible_human_reason(before)
    if result.get("requires_human_escalation") is True and not human_supported:
        result["requires_human_escalation"] = False
        escalation_demoted = True
        if str(result.get("decision_class") or "") == "escalation_candidate":
            result["decision_class"] = "action_candidate" if result.get("should_take_action_now") is True else "investigate_only"
            decision_changed = True

    # If escalation remains the decision but no escalation flag survives, keep
    # the decision state internally consistent.
    if str(result.get("decision_class") or "") == "escalation_candidate" and result.get("requires_human_escalation") is not True:
        result["decision_class"] = "action_candidate" if result.get("should_take_action_now") is True else "investigate_only"
        decision_changed = True

    free_text_unchanged = _output_free_text_signature(before) == _output_free_text_signature(result)
    return result, {
        "authorization_failure_reason": reason,
        "endpoint_cleared": endpoint_cleared,
        "action_demoted": action_demoted,
        "escalation_demoted": escalation_demoted,
        "decision_changed": decision_changed,
        "evidence_plan_preserved": before.get("evidence_plan") == result.get("evidence_plan"),
        "free_text_and_trace_preserved": free_text_unchanged,
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
        raise AssertionError(f"E14q requires exactly {EXPECTED_CALLS} fixed full-DEV calls")

    parsed = 0
    changed = 0
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
        if guarded != output:
            changed += 1
        action_demotions += int(meta["action_demoted"])
        escalation_demotions += int(meta["escalation_demoted"])
        endpoint_clears += int(meta["endpoint_cleared"])
        decision_changes += int(meta["decision_changed"])
        evidence_changes += int(not meta["evidence_plan_preserved"])
        free_text_changes += int(not meta["free_text_and_trace_preserved"])
        if meta["authorization_failure_reason"]:
            reason_counts[str(meta["authorization_failure_reason"])] += 1
        call["parsed_output"] = guarded

    complete = parsed == EXPECTED_CALLS
    passed = complete and evidence_changes == 0 and free_text_changes == 0
    status = PASS_STATUS if passed else FAIL_STATUS
    transformed["report_version"] = "e14q-full-dev-public-action-authorization-consistency-v1"
    transformed["status"] = status
    transformed["e14q_public_action_authorization_consistency"] = {
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "complete_fixed_transform": complete,
        "calls_changed": changed,
        "action_demotions": action_demotions,
        "escalation_demotions": escalation_demotions,
        "action_endpoints_cleared": endpoint_clears,
        "decision_class_changes": decision_changes,
        "authorization_failure_reason_counts": dict(sorted(reason_counts.items())),
        "evidence_plan_changes": evidence_changes,
        "v4_2_free_text_or_trace_changes": free_text_changes,
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
        **transformed["e14q_public_action_authorization_consistency"],
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
