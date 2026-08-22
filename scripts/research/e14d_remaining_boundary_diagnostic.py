#!/usr/bin/env python3
"""Sanitized diagnostic for remaining E14d E10d/E10e boundary effects.

This is a zero-provider-call, zero-oracle diagnostic over an already-fixed E14d
DEV capture. It reports only aggregate public-policy facts:

1. which frozen E10d human-escalation marker strings remain visible for calls
   changed specifically by `visible_human_escalation_marker`, after removing
   deterministic guard-added text; and
2. for calls changed by E10e's generic state-change evidence minimum, the
   canonical public action endpoint, normalized E14d evidence-family count, and
   whether the already-preregistered E14 selective reprocess boundary would
   authorize that same visible proposal if `should_take_action_now` were restored
   to its known pre-E10e value of true.

It never reads private oracle/scorer data and never prints parsed outputs, group
IDs, concrete resource identifiers, prompts, hashes, private paths, evaluator
labels, or evidence-plan text.
"""

from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
E10D_SOURCE = HERE / "e10d_dev_only_escalation_consistency_guard.py"
E14D_EVIDENCE_PATH = HERE / "e14d_public_evidence_resource_normalization.py"
E14C_ENDPOINT_PATH = HERE / "e14c_public_action_endpoint_normalization.py"
E14_SELECTIVE_PATH = HERE / "e14_selective_reprocess.py"

TARGET_E10D_REASON = "visible_human_escalation_marker"
TARGET_E10E_REASON = "too_few_concrete_evidence_resources_for_state_change"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence_norm = load_module("e14d_remaining_evidence_norm", E14D_EVIDENCE_PATH)
endpoint_norm = load_module("e14d_remaining_endpoint_norm", E14C_ENDPOINT_PATH)
e14_selective = load_module("e14d_remaining_e14_selective", E14_SELECTIVE_PATH)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def e10d_markers() -> tuple[str, ...]:
    tree = ast.parse(E10D_SOURCE.read_text(encoding="utf-8"))
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "HUMAN_ESCALATION_MARKERS" for target in statement.targets):
            continue
        value = ast.literal_eval(statement.value)
        if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
            raise AssertionError("HUMAN_ESCALATION_MARKERS must be a literal tuple")
        return tuple(str(item).lower() for item in value)
    raise AssertionError("HUMAN_ESCALATION_MARKERS not found")


def text_values(payload: Any) -> list[str]:
    values: list[str] = []
    if isinstance(payload, str):
        values.append(payload)
    elif isinstance(payload, list):
        for item in payload:
            values.extend(text_values(item))
    elif isinstance(payload, dict):
        for key, value in payload.items():
            lowered = str(key).lower()
            if "guard" in lowered or "authorization" in lowered or "boundary" in lowered:
                continue
            values.extend(text_values(value))
    return values


def strip_guard_added_text(output: dict[str, Any]) -> dict[str, Any]:
    """Remove deterministic suffixes added after the original model output.

    This is used only for marker diagnosis. It does not attempt to reconstruct or
    print the original output.
    """
    cleaned = copy.deepcopy(output)
    for key in list(cleaned):
        lowered = str(key).lower()
        if "guard" in lowered or "authorization" in lowered or "boundary" in lowered:
            cleaned.pop(key, None)

    risk = str(cleaned.get("risk_notes", "") or "")
    for token in (
        " Visible-output escalation consistency guard applied:",
        " Visible-output premature-action safety guard applied:",
        " E10g balanced visible-output safety guard applied:",
        " E14 blocked autonomous reprocess:",
    ):
        if token in risk:
            risk = risk.split(token, 1)[0]
    cleaned["risk_notes"] = risk

    proposed = str(cleaned.get("proposed_next_step", "") or "")
    for token in (
        " Do not execute a state-changing maintenance action yet; collect the missing visible evidence or obtain human review before action.",
        " Do not execute the state-changing maintenance action yet; collect stronger concrete evidence or route to human review before action.",
        " E14 selective reprocess authorization did not approve immediate reprocess;",
    ):
        if token in proposed:
            proposed = proposed.split(token, 1)[0]
    cleaned["proposed_next_step"] = proposed

    rubric = cleaned.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        calibration = str(rubric.get("calibration_reason", "") or "")
        for token in (
            " Visible guard reason:",
            " Safety guard reason:",
            " Balanced safety guard reason:",
            " E14 selective reprocess reason:",
        ):
            if token in calibration:
                calibration = calibration.split(token, 1)[0]
        rubric["calibration_reason"] = calibration
    return cleaned


def safe_e14_reason(value: Any) -> str:
    reason = str(value or "none")
    allow = {
        "no_immediate_action_requested",
        "not_reprocess_endpoint_boundary_target",
        "missing_visible_analysis_resource_reference",
        "missing_visible_asset_or_case_reference",
        "reprocess_action_not_limited_to_reprocess",
        "missing_human_readable_evidence_to_reprocess_reason",
        "fewer_than_two_concrete_reprocess_support_anchors",
        "authorized_reprocess_with_selective_visible_support",
    }
    return reason if reason in allow else "other_public_reason"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    payload = load_json(args.capture)
    if not isinstance(payload, dict):
        raise AssertionError("capture must be a JSON object")
    stage = payload.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []

    markers = e10d_markers()
    e10d_target_calls = 0
    marker_hits: Counter[str] = Counter()
    e10d_endpoint_counts: Counter[str] = Counter()

    e10e_target_calls = 0
    e10e_endpoint_counts: Counter[str] = Counter()
    e10e_evidence_hist: Counter[int] = Counter()
    e14_counterfactual_authorized = 0
    e14_counterfactual_reasons: Counter[str] = Counter()
    e14_support_anchor_hist: Counter[int] = Counter()

    for call in calls:
        if not isinstance(call, dict):
            continue
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue

        rubric = output.get("action_escalation_rubric")
        endpoint_value = rubric.get("action_endpoint") if isinstance(rubric, dict) else None
        canonical_endpoint = endpoint_norm.canonical_public_endpoint_or_none(endpoint_value) or "none_or_unrecognized"

        e10d_guard = output.get("visible_escalation_consistency_guard")
        if isinstance(e10d_guard, dict) and str(e10d_guard.get("reason") or "") == TARGET_E10D_REASON:
            e10d_target_calls += 1
            e10d_endpoint_counts[canonical_endpoint] += 1
            cleaned = strip_guard_added_text(output)
            text = "\n".join(text_values(cleaned)).lower()
            for marker in markers:
                if marker in text:
                    marker_hits[marker] += 1

        e10e_guard = output.get("visible_premature_action_safety_guard")
        if isinstance(e10e_guard, dict) and str(e10e_guard.get("reason") or "") == TARGET_E10E_REASON:
            e10e_target_calls += 1
            e10e_endpoint_counts[canonical_endpoint] += 1
            family_count = evidence_norm.public_evidence_family_count(output)
            e10e_evidence_hist[family_count] += 1

            # E10e only emits TARGET_E10E_REASON when should_take_action_now was
            # true before its downgrade. Restore only that known precondition and
            # ask the already-existing E14 selective public policy what it would
            # decide. E14 does not use the private oracle.
            cf_output = copy.deepcopy(output)
            cf_output["should_take_action_now"] = True
            decision = e14_selective.authorize({**call, "parsed_output": cf_output})
            authorized = decision.get("authorized") is True and decision.get("is_target_reprocess_action") is True
            e14_counterfactual_authorized += int(authorized)
            e14_counterfactual_reasons[safe_e14_reason(decision.get("reason"))] += 1
            e14_support_anchor_hist[int(decision.get("support_anchor_count") or 0)] += 1

    result = {
        "status": "E14D_SANITIZED_REMAINING_BOUNDARY_DIAGNOSTIC",
        "total_calls": len(calls),
        "e10d_visible_human_marker": {
            "target_calls": e10d_target_calls,
            "canonical_public_endpoint_counts": dict(sorted(e10d_endpoint_counts.items())),
            "public_marker_hit_call_counts": dict(sorted(marker_hits.items())),
            "marker_match_semantics": "same literal substring semantics as historical E10d after deterministic guard-added text is removed",
        },
        "e10e_too_few_state_change": {
            "target_calls": e10e_target_calls,
            "canonical_public_endpoint_counts": dict(sorted(e10e_endpoint_counts.items())),
            "normalized_public_evidence_family_count_histogram": {
                str(key): value for key, value in sorted(e10e_evidence_hist.items())
            },
            "existing_e10e_state_change_threshold": 3,
        },
        "e14_selective_reprocess_counterfactual_for_e10e_too_few": {
            "target_calls_checked": e10e_target_calls,
            "authorized_target_reprocess_calls": e14_counterfactual_authorized,
            "public_reason_counts": dict(sorted(e14_counterfactual_reasons.items())),
            "support_anchor_count_histogram": {
                str(key): value for key, value in sorted(e14_support_anchor_hist.items())
            },
            "existing_e14_required_anchor_count": 2,
            "restores_only_known_pre_e10e_should_take_action_now_true_for_policy_check": True,
            "does_not_change_or_write_capture": True,
        },
        "prints_private_outputs": False,
        "prints_group_level_rows": False,
        "prints_hashes": False,
        "prints_prompts": False,
        "prints_private_paths": False,
        "prints_oracle_data": False,
        "prints_evaluator_labels": False,
        "prints_concrete_resource_identifiers": False,
        "prints_evidence_plan_text": False,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
