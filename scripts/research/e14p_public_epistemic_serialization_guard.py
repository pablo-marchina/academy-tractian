#!/usr/bin/env python3
"""E14p deterministic public epistemic serialization guard.

Transforms only free-text serialization over an already-fixed E14o-after-E14n-v1.1
DEV capture. It preserves decision/action/escalation semantics, the action endpoint,
trace self-check fields, and the exact ordered set of recognized public METHOD+path
signatures in evidence_plan. It makes no provider calls and reads no oracle,
VALIDATION, LOCKED_TEST, or semantic judge rows.

Real transformed outputs remain local/uncommitted.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
V41_PATH = HERE / "e9_evaluator_side_scorer_v4_1.py"
SPEC = importlib.util.spec_from_file_location("e14p_v41", V41_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E9 v4.1")
v41 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v41)
v4 = v41.v4

MANIFEST = Path("research/experiments/e14p-public-epistemic-serialization-guard-manifest.json")
PASS_STATUS = "E14P_PUBLIC_EPISTEMIC_SERIALIZATION_GUARD_PASS"
FAIL_STATUS = "E14P_PUBLIC_EPISTEMIC_SERIALIZATION_GUARD_NEEDS_REVIEW"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _decision_signature(output: dict[str, Any]) -> tuple[Any, ...]:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    trace = output.get("trace_quality_self_check")
    trace = trace if isinstance(trace, dict) else {}
    return (
        output.get("decision_class"),
        output.get("should_take_action_now"),
        output.get("requires_human_escalation"),
        rubric.get("needs_more_evidence"),
        rubric.get("safe_to_act"),
        rubric.get("action_endpoint"),
        rubric.get("needs_human_escalation"),
        trace.get("uses_only_visible_packet"),
        trace.get("no_locked_test"),
        trace.get("no_gold_claim"),
    )


def _evidence_signatures(output: dict[str, Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return result
    for item in plan:
        if not isinstance(item, str):
            continue
        for signature, kind in v41.canonical_tool_signatures(item, require_method=True):
            if kind != "read" or signature in seen:
                continue
            seen.add(signature)
            result.append(signature)
    return result


def _render_evidence_plan(signatures: list[str]) -> list[str]:
    if not signatures:
        return ["Continue evidence acquisition before making any task-world factual claim."]
    return [f"Retrieve {signature}; treat its result as unobserved until the tool call is actually made." for signature in signatures]


def _canonical_action_endpoint(output: dict[str, Any]) -> str | None:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = rubric.get("action_endpoint")
    if not isinstance(endpoint, str):
        return None
    signature, kind = v41.canonical_tool_signature(endpoint, require_method=True)
    return signature if kind == "action" else None


def _render_next_step(output: dict[str, Any], evidence_signatures: list[str]) -> str:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = _canonical_action_endpoint(output)
    safe = rubric.get("safe_to_act") is True
    if endpoint is not None and safe and output.get("should_take_action_now") is True:
        return f"Next procedural step: {endpoint}; execute only under the selected authorization and safety rubric."
    if evidence_signatures:
        return f"Next procedural step: retrieve {evidence_signatures[0]} before action or escalation."
    return "Next procedural step: continue evidence acquisition before action or escalation."


def _render_risk_notes(output: dict[str, Any]) -> str:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    notes: list[str] = ["Do not treat unobserved tool results as established task-world facts."]
    if rubric.get("needs_more_evidence") is True:
        notes.append("Acquire the selected evidence before making an irreversible decision.")
    if rubric.get("safe_to_act") is not True:
        notes.append("Do not execute an action endpoint unless the selected rubric marks it safe.")
    if rubric.get("needs_human_escalation") is True or output.get("requires_human_escalation") is True:
        notes.append("Route the selected workflow through human review before irreversible action.")
    return " ".join(notes)


def _render_calibration_reason(output: dict[str, Any]) -> str:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    needs_more = str(rubric.get("needs_more_evidence") is True).lower()
    safe = str(rubric.get("safe_to_act") is True).lower()
    human = str(rubric.get("needs_human_escalation") is True).lower()
    return (
        "Rubric metadata only: "
        f"needs_more_evidence={needs_more}; safe_to_act={safe}; needs_human_escalation={human}. "
        "No additional task-world fact is asserted."
    )


def serialize_output(output: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    result = copy.deepcopy(output)
    before_signatures = _evidence_signatures(output)
    changed_fields = 0

    new_plan = _render_evidence_plan(before_signatures)
    if result.get("evidence_plan") != new_plan:
        changed_fields += 1
    result["evidence_plan"] = new_plan

    new_next = _render_next_step(output, before_signatures)
    if result.get("proposed_next_step") != new_next:
        changed_fields += 1
    result["proposed_next_step"] = new_next

    new_risk = _render_risk_notes(output)
    if result.get("risk_notes") != new_risk:
        changed_fields += 1
    result["risk_notes"] = new_risk

    rubric = result.get("action_escalation_rubric")
    if not isinstance(rubric, dict):
        raise AssertionError("action_escalation_rubric must be an object")
    new_reason = _render_calibration_reason(output)
    if rubric.get("calibration_reason") != new_reason:
        changed_fields += 1
    rubric["calibration_reason"] = new_reason

    after_signatures = _evidence_signatures(result)
    losses = len([x for x in before_signatures if x not in after_signatures])
    gains = len([x for x in after_signatures if x not in before_signatures])
    order_changed = int(before_signatures != after_signatures)
    return result, {
        "changed_text_fields": changed_fields,
        "evidence_public_signature_loss": losses,
        "evidence_public_signature_gain": gains,
        "evidence_public_signature_order_changed": order_changed,
    }


def _assert_manifest(path: Path) -> None:
    manifest = _load(path)
    if not isinstance(manifest, dict) or manifest.get("experiment_id") != "E14p":
        raise AssertionError("E14p frozen manifest required")
    intervention = manifest.get("intervention")
    if not isinstance(intervention, dict) or intervention.get("change_class") != "deterministic_public_epistemic_serialization_only":
        raise AssertionError("E14p intervention class changed")
    if intervention.get("provider_calls") != 0:
        raise AssertionError("E14p must remain provider-free")


def run(args: argparse.Namespace) -> dict[str, Any]:
    _assert_manifest(args.manifest)
    fixed = _load(args.fixed_output_file)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be objects")

    transformed = copy.deepcopy(fixed)
    calls = v4.collect_calls(transformed)
    v4.assert_fixed_scope(transformed, calls, split_manifest)

    parsed = 0
    changed_calls = 0
    changed_fields = 0
    decision_changes = 0
    endpoint_changes = 0
    trace_changes = 0
    signature_loss = 0
    signature_gain = 0
    signature_order_changes = 0

    for call in calls:
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        parsed += 1
        before_decision = _decision_signature(output)
        before_rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
        before_endpoint = before_rubric.get("action_endpoint")
        before_trace = copy.deepcopy(output.get("trace_quality_self_check"))

        serialized, stats = serialize_output(output)
        after_decision = _decision_signature(serialized)
        after_rubric = serialized.get("action_escalation_rubric") if isinstance(serialized.get("action_escalation_rubric"), dict) else {}

        decision_changes += int(before_decision != after_decision)
        endpoint_changes += int(before_endpoint != after_rubric.get("action_endpoint"))
        trace_changes += int(before_trace != serialized.get("trace_quality_self_check"))
        changed_fields += int(stats["changed_text_fields"])
        changed_calls += int(stats["changed_text_fields"] > 0)
        signature_loss += int(stats["evidence_public_signature_loss"])
        signature_gain += int(stats["evidence_public_signature_gain"])
        signature_order_changes += int(stats["evidence_public_signature_order_changed"])
        call["parsed_output"] = serialized

    complete = bool(calls) and len(calls) == 6 and parsed == len(calls)
    passed = (
        complete
        and decision_changes == 0
        and endpoint_changes == 0
        and trace_changes == 0
        and signature_loss == 0
        and signature_gain == 0
        and signature_order_changes == 0
    )
    status = PASS_STATUS if passed else FAIL_STATUS

    transformed["report_version"] = "e14p-public-epistemic-serialization-guard-v1"
    transformed["status"] = status
    transformed["e14p_epistemic_serialization"] = {
        "parent_capture_status": fixed.get("status"),
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "complete_fixed_transform": complete,
        "calls_changed": changed_calls,
        "changed_text_fields": changed_fields,
        "decision_action_escalation_semantic_changes": decision_changes,
        "action_endpoint_changes": endpoint_changes,
        "trace_quality_self_check_changes": trace_changes,
        "evidence_public_signature_loss": signature_loss,
        "evidence_public_signature_gain": signature_gain,
        "evidence_public_signature_order_changes": signature_order_changes,
        "task_world_facts_added_by_serializer": False,
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
        "status": status,
        **transformed["e14p_epistemic_serialization"],
        "raw_outputs_printed": False,
        "claim_text_printed": False,
        "identifiers_printed": False,
        "private_paths_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
