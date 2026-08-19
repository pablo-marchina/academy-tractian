#!/usr/bin/env python3
"""E14n deterministic public identifier-provenance canonicalization.

Applies a preregistered, provider-free transform to an existing fixed DEV capture.
Only concrete identifiers absent from the exact runner-selected visible case are
replaced with typed public placeholders in the same free-text fields audited by
the public groundedness-surface diagnostic. Decision/action/escalation semantics
are not changed. No private oracle or scorer rows are read.

Real transformed captures contain model outputs and must remain local/uncommitted.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
GROUND_PATH = HERE / "e9_v4_1_groundedness_surface_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("e14n_ground_parent", GROUND_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load groundedness surface diagnostic")
ground = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ground)
v4 = ground.v4

MANIFEST_PATH = Path("research/experiments/e14n-public-identifier-provenance-guard-manifest.json")


def _placeholder_for(token: str) -> str:
    lowered = token.lower()
    for prefix, placeholder in (
        ("asset-", "{assetId}"),
        ("asset_", "{assetId}"),
        ("analysis-", "{analysisId}"),
        ("analysis_", "{analysisId}"),
        ("model-", "{modelId}"),
        ("model_", "{modelId}"),
        ("case-", "{caseId}"),
        ("case_", "{caseId}"),
        ("ticket-", "{ticketId}"),
        ("ticket_", "{ticketId}"),
    ):
        if lowered.startswith(prefix):
            return placeholder
    return "{id}"


def _sanitize_text(text: str, visible_blob: str) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        token = match.group(0)
        if token.lower() in visible_blob:
            return token
        replacements += 1
        return _placeholder_for(token)

    # Namespaced IDs first. UUIDs are then handled independently; the patterns
    # do not overlap for the public benchmark identifier forms.
    result = ground.NAMESPACED_ID_RE.sub(replace, text)
    result = ground.UUID_RE.sub(replace, result)
    return result, replacements


def sanitize_output(output: dict[str, Any], visible_case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    result = copy.deepcopy(output)
    visible_blob = ground._case_visible_blob(visible_case)
    replacements = 0
    changed_fields = 0

    plan = result.get("evidence_plan")
    if isinstance(plan, list):
        new_plan: list[Any] = []
        for item in plan:
            if isinstance(item, str):
                new_item, count = _sanitize_text(item, visible_blob)
                replacements += count
                changed_fields += int(new_item != item)
                new_plan.append(new_item)
            else:
                new_plan.append(item)
        result["evidence_plan"] = new_plan

    for key in ("proposed_next_step", "risk_notes"):
        value = result.get(key)
        if isinstance(value, str):
            new_value, count = _sanitize_text(value, visible_blob)
            replacements += count
            changed_fields += int(new_value != value)
            result[key] = new_value

    rubric = result.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        for key in ("calibration_reason", "action_endpoint"):
            value = rubric.get(key)
            if isinstance(value, str):
                new_value, count = _sanitize_text(value, visible_blob)
                replacements += count
                changed_fields += int(new_value != value)
                rubric[key] = new_value

    return result, {
        "unsupported_identifier_replacements": replacements,
        "changed_text_fields": changed_fields,
    }


def _decision_signature(output: dict[str, Any]) -> tuple[Any, ...]:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    return (
        output.get("decision_class"),
        output.get("should_take_action_now"),
        output.get("requires_human_escalation"),
        rubric.get("needs_more_evidence"),
        rubric.get("safe_to_act"),
        rubric.get("needs_human_escalation"),
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    fixed = json.loads(args.fixed_output_file.read_text(encoding="utf-8"))
    cases_payload = json.loads(args.agent_input_cases.read_text(encoding="utf-8"))
    split_manifest = json.loads(args.split_manifest.read_text(encoding="utf-8"))
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be JSON objects")

    transformed = copy.deepcopy(fixed)
    calls = v4.collect_calls(transformed)
    v4.assert_fixed_scope(transformed, calls, split_manifest)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected = ground._selected_case_by_group(cases_payload, fixed_groups)

    parsed = 0
    assessed = 0
    calls_changed = 0
    replacements = 0
    changed_fields = 0
    decision_semantic_changes = 0
    before_unsupported_ids = 0
    after_unsupported_ids = 0
    before_calls_with_violation = 0
    after_calls_with_violation = 0

    for call in calls:
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        parsed += 1
        group = str(call.get("group_id") or "")
        visible_case = selected.get(group)
        if not isinstance(visible_case, dict):
            continue
        assessed += 1

        before = ground.audit_output(output, visible_case)
        sanitized, stats = sanitize_output(output, visible_case)
        after = ground.audit_output(sanitized, visible_case)

        before_unsupported_ids += int(before["unsupported_id_mentions"])
        after_unsupported_ids += int(after["unsupported_id_mentions"])
        before_calls_with_violation += int(before["has_concrete_provenance_violation"] is True)
        after_calls_with_violation += int(after["has_concrete_provenance_violation"] is True)
        replacements += int(stats["unsupported_identifier_replacements"])
        changed_fields += int(stats["changed_text_fields"])
        calls_changed += int(stats["unsupported_identifier_replacements"] > 0)
        decision_semantic_changes += int(_decision_signature(output) != _decision_signature(sanitized))

        # collect_calls returns references into transformed, so replacing this
        # field mutates only the local transformed copy.
        call["parsed_output"] = sanitized

    complete = (
        bool(calls)
        and parsed == len(calls)
        and assessed == len(calls)
        and len(selected) == len(fixed_groups)
    )
    pass_guard = (
        complete
        and before_unsupported_ids == replacements
        and after_unsupported_ids == 0
        and decision_semantic_changes == 0
    )

    status = (
        "E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS"
        if pass_guard
        else "E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_NEEDS_REVIEW"
    )
    transformed["report_version"] = "e14n-public-identifier-provenance-guard-v1"
    transformed["status"] = status
    transformed["e14n_identifier_provenance_guard"] = {
        "parent_capture_status": fixed.get("status"),
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "assessed_calls": assessed,
        "complete_surface_coverage": complete,
        "calls_changed": calls_changed,
        "changed_text_fields": changed_fields,
        "unsupported_identifier_mentions_before": before_unsupported_ids,
        "unsupported_identifier_replacements": replacements,
        "unsupported_identifier_mentions_after": after_unsupported_ids,
        "calls_with_any_concrete_provenance_violation_before": before_calls_with_violation,
        "calls_with_any_concrete_provenance_violation_after": after_calls_with_violation,
        "decision_action_escalation_semantic_changes": decision_semantic_changes,
        "typed_placeholders_only": True,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "general_free_text_groundedness_claimed": False,
        "validation_gate_authorized": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(transformed, indent=2), encoding="utf-8")

    return {
        "status": status,
        **transformed["e14n_identifier_provenance_guard"],
        "raw_outputs_printed": False,
        "identifiers_printed": False,
        "private_paths_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
