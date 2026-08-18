#!/usr/bin/env python3
"""Evaluator v4: deterministic visible-ticket-aligned tool-signature scoring.

V4 is measurement-only. It derives supervision from the exact private
expected-path row corresponding to the public runner's actually selected visible
case: first agent-input case per asset/group, then exact ticket_id match.
Expected-path semantics come only from normalized METHOD+path signatures against
the public tool registry. Group-level oracle unions, root-question wording and
candidate outputs are never used to choose supervision.

No private oracle text, endpoint list, ticket/group label, per-row error or fixed
model output is printed. The model never receives oracle data. LOCKED_TEST fixed
outputs remain forbidden.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from research.e2.tool_registry import TOOLS

ALLOWED_SPLITS = {"DEV", "VALIDATION"}
FORBIDDEN_SPLITS = {"LOCKED_TEST"}
DECISION_CLASSES = {"investigate_only", "action_candidate", "escalation_candidate", "insufficient_evidence"}
NON_ACTION_CLASSES = {"investigate_only", "insufficient_evidence"}
ASSET_RE = re.compile(r"\basset_[A-Za-z0-9]+\b", re.IGNORECASE)
METHOD_RE = re.compile(r"\b(GET|POST|PATCH|PUT|DELETE)\b", re.IGNORECASE)
SENSITIVE_OUTPUT_TERMS = ("evaluator gold", "expected answer", "hidden oracle", "private oracle")
EXPLICIT_ESCALATION_SIGNATURES = {
    "POST /analyses/{analysisId}/request-specialist",
    "POST /cases/{caseId}/escalate",
}
ALIGNMENT_UNIQUE = "selected_ticket_matches_exactly_one_oracle_row"
ALIGNMENT_NO_MATCH = "selected_ticket_matches_no_oracle_row"
ALIGNMENT_MULTIPLE = "selected_ticket_matches_multiple_oracle_rows"
ALIGNMENT_NO_VISIBLE_CASE = "no_runner_selected_visible_case_for_group"
ALIGNMENT_NO_TICKET = "selected_visible_case_missing_ticket_id"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _kind_value(tool: Any) -> str:
    return str(getattr(tool.kind, "value", tool.kind)).lower()


def _path_regex(template: str) -> re.Pattern[str]:
    parts = template.strip("/").split("/")
    pieces: list[str] = []
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            pieces.append(r"[^/\s]+")
        else:
            pieces.append(re.escape(part))
    return re.compile(r"/" + r"/".join(pieces) + r"(?=$|[\s,.;:)\]\}])", re.IGNORECASE)


TOOL_SPECS = [
    {
        "signature": f"{str(tool.method).upper()} {str(tool.path_template)}",
        "method": str(tool.method).upper(),
        "path_re": _path_regex(str(tool.path_template)),
        "kind": _kind_value(tool),
    }
    for tool in TOOLS
]


def canonical_tool_signatures(text: str, *, require_method: bool = True) -> list[tuple[str, str]]:
    """Return every distinct public tool signature mentioned in text, in registry order."""
    methods = {m.group(1).upper() for m in METHOD_RE.finditer(text)}
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for spec in TOOL_SPECS:
        if require_method and spec["method"] not in methods:
            continue
        if spec["path_re"].search(text):
            signature = str(spec["signature"])
            if signature not in seen:
                seen.add(signature)
                result.append((signature, str(spec["kind"])))
    return result


def canonical_tool_signature(text: str, *, require_method: bool = True) -> tuple[str | None, str | None]:
    matches = canonical_tool_signatures(text, require_method=require_method)
    return matches[0] if matches else (None, None)


def collect_calls(payload: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "calls" and isinstance(value, list):
                calls.extend(item for item in value if isinstance(item, dict))
            elif isinstance(value, (dict, list)):
                calls.extend(collect_calls(value))
    elif isinstance(payload, list):
        for item in payload:
            calls.extend(collect_calls(item))
    return calls


def output_payload(call: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("parsed_output", "model_output", "output", "response"):
        value = call.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return None
            if isinstance(parsed, dict):
                return parsed
    return None


def split_groups(split_manifest: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for name, body in (split_manifest.get("splits") or {}).items():
        groups: set[str] = set()
        for item in body.get("groups", []):
            if isinstance(item, dict) and item.get("group_id"):
                groups.add(str(item["group_id"]))
        result[str(name)] = groups
    return result


def assert_fixed_scope(fixed: dict[str, Any], calls: list[dict[str, Any]], split_manifest: dict[str, Any]) -> None:
    scope = fixed.get("scope", {}) if isinstance(fixed, dict) else {}
    if scope.get("locked_test_accessed") is True:
        raise AssertionError("fixed output reports LOCKED_TEST access")
    locked = split_groups(split_manifest).get("LOCKED_TEST", set())
    for call in calls:
        group = str(call.get("group_id") or "")
        split = call.get("split")
        if split in FORBIDDEN_SPLITS or group in locked:
            raise AssertionError("LOCKED_TEST fixed output present")
        if split is not None and split not in ALLOWED_SPLITS:
            raise AssertionError("unexpected split in fixed outputs")


def expected_path_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict) and isinstance(row.get("expected_path"), list)]


def _collect_case_records(payload: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            records.extend(_collect_case_records(item))
    elif isinstance(payload, dict):
        keys = set(payload)
        if {"case_id", "asset_id"} & keys or {"ticket_id", "assetId"} & keys:
            records.append(payload)
        for value in payload.values():
            if isinstance(value, (dict, list)):
                records.extend(_collect_case_records(value))
    return records


def _asset_id(record: dict[str, Any]) -> str | None:
    for key in ("asset_id", "assetId", "asset", "assetID"):
        value = record.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for nested in ("id", "asset_id", "assetId"):
                if isinstance(value.get(nested), str):
                    return str(value[nested])
    return None


def _ticket_id(record: dict[str, Any]) -> str | None:
    for key in ("ticket_id", "ticketId", "ticket", "id"):
        value = record.get(key)
        if isinstance(value, str):
            return value
    return None


def runner_selected_ticket_by_group(cases_payload: Any, fixed_groups: set[str]) -> dict[str, str | None]:
    """Replay load_agent_visible_cases(): first encountered case per asset/group."""
    canonical_by_lower = {group.lower(): group for group in fixed_groups}
    selected: dict[str, str | None] = {}
    for record in _collect_case_records(cases_payload):
        asset = _asset_id(record)
        if not asset or asset.lower() not in canonical_by_lower:
            continue
        group = canonical_by_lower[asset.lower()]
        if group not in selected:
            selected[group] = _ticket_id(record)
    return selected


def _normalize_expected_row(row: dict[str, Any]) -> dict[str, Any]:
    reads: set[str] = set()
    actions: set[str] = set()
    escalations: set[str] = set()
    unrecognized_steps = 0
    items = row.get("expected_path") or []
    for item in items:
        if not isinstance(item, dict):
            continue
        signature, kind = canonical_tool_signature(str(item.get("step") or ""), require_method=True)
        if signature is None:
            unrecognized_steps += 1
            continue
        if kind == "read":
            reads.add(signature)
        elif kind == "action":
            actions.add(signature)
            if signature in EXPLICIT_ESCALATION_SIGNATURES:
                escalations.add(signature)
    return {
        "alignment_status": ALIGNMENT_UNIQUE,
        "private_row_count": 1,
        "private_expected_path_item_count": len(items),
        "expected_read_signatures": reads,
        "expected_action_signatures": actions,
        "expected_escalation_signatures": escalations,
        "unrecognized_expected_steps": unrecognized_steps,
    }


def adapt_expected_paths(
    payload: Any,
    fixed_groups: set[str],
    split_manifest: dict[str, Any],
    selected_tickets: dict[str, str | None],
) -> dict[str, dict[str, Any]]:
    """Align each fixed group to exactly one expected-path row by visible ticket.

    No group-level union fallback is permitted. Zero or multiple matches are
    represented explicitly and make calls for that group unscoreable.
    """
    locked = split_groups(split_manifest).get("LOCKED_TEST", set())
    canonical_by_lower = {group.lower(): group for group in fixed_groups}
    locked_lower = {group.lower() for group in locked}
    candidates: dict[str, list[dict[str, Any]]] = {group: [] for group in fixed_groups}

    for row in expected_path_rows(payload):
        ticket = row.get("ticket_id")
        if not isinstance(ticket, str):
            continue
        blob = json.dumps(row, ensure_ascii=False, sort_keys=True).lower()
        mentioned = {
            canonical_by_lower[item.lower()]
            for item in set(ASSET_RE.findall(blob))
            if item.lower() in canonical_by_lower and item.lower() not in locked_lower
        }
        for group in mentioned:
            if selected_tickets.get(group) == ticket:
                candidates[group].append(row)

    result: dict[str, dict[str, Any]] = {}
    for group in fixed_groups:
        if group not in selected_tickets:
            result[group] = {"alignment_status": ALIGNMENT_NO_VISIBLE_CASE}
            continue
        if not selected_tickets[group]:
            result[group] = {"alignment_status": ALIGNMENT_NO_TICKET}
            continue
        matches = candidates.get(group, [])
        if len(matches) == 1:
            result[group] = _normalize_expected_row(matches[0])
        elif not matches:
            result[group] = {"alignment_status": ALIGNMENT_NO_MATCH}
        else:
            result[group] = {"alignment_status": ALIGNMENT_MULTIPLE}

    if set(result) & locked:
        raise AssertionError("v4 adapter produced LOCKED_TEST supervision")
    return result


def _output_evidence_signatures(output: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return result
    for item in plan:
        if not isinstance(item, str):
            continue
        for signature, kind in canonical_tool_signatures(item, require_method=True):
            if kind == "read":
                result.add(signature)
    return result


def _output_action_signature(output: dict[str, Any]) -> str | None:
    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = rubric.get("action_endpoint")
    if not isinstance(endpoint, str):
        return None
    signature, kind = canonical_tool_signature(endpoint, require_method=True)
    return signature if kind == "action" else None


def _schema_valid(output: dict[str, Any]) -> bool:
    rubric = output.get("action_escalation_rubric")
    trace = output.get("trace_quality_self_check")
    return (
        str(output.get("decision_class") or "") in DECISION_CLASSES
        and isinstance(output.get("evidence_plan"), list)
        and isinstance(output.get("should_take_action_now"), bool)
        and isinstance(output.get("requires_human_escalation"), bool)
        and isinstance(output.get("proposed_next_step"), str)
        and isinstance(output.get("risk_notes"), str)
        and isinstance(rubric, dict)
        and isinstance(trace, dict)
    )


def _normalize_output_text(output: dict[str, Any]) -> str:
    return json.dumps(output, ensure_ascii=False, sort_keys=True).lower()


def score_call(call: dict[str, Any], oracle: dict[str, Any] | None) -> dict[str, Any]:
    output = output_payload(call)
    if output is None:
        return {"scoreable": False, "reason": "parsed_model_output_missing"}
    if not oracle:
        return {"scoreable": False, "reason": "private_oracle_alignment_missing"}
    alignment_status = str(oracle.get("alignment_status") or "")
    if alignment_status != ALIGNMENT_UNIQUE:
        return {"scoreable": False, "reason": f"private_oracle_alignment_{alignment_status or 'unknown'}"}
    if int(oracle.get("unrecognized_expected_steps") or 0) != 0:
        return {"scoreable": False, "reason": "private_expected_step_normalization_incomplete"}

    expected_reads = set(oracle.get("expected_read_signatures") or set())
    expected_actions = set(oracle.get("expected_action_signatures") or set())
    expected_escalations = set(oracle.get("expected_escalation_signatures") or set())
    expected_action = bool(expected_actions)
    expected_escalation = bool(expected_escalations)

    decision = str(output.get("decision_class") or "")
    if expected_escalation:
        decision_correct = decision == "escalation_candidate"
    elif expected_action:
        decision_correct = decision == "action_candidate"
    else:
        decision_correct = decision in NON_ACTION_CLASSES

    observed_reads = _output_evidence_signatures(output)
    covered_reads = expected_reads & observed_reads
    evidence_recall = 1.0 if not expected_reads else len(covered_reads) / len(expected_reads)
    evidence_correct = evidence_recall == 1.0
    extra_public_reads = observed_reads - expected_reads

    observed_action = output.get("should_take_action_now") is True
    observed_endpoint = _output_action_signature(output)
    if expected_action:
        action_correct = observed_action and observed_endpoint in expected_actions
    else:
        action_correct = (not observed_action) and observed_endpoint is None

    observed_escalation = output.get("requires_human_escalation") is True
    escalation_correct = observed_escalation is expected_escalation

    unsupported_action_or_escalation = (
        (observed_action and observed_endpoint not in expected_actions)
        or (observed_endpoint is not None and observed_endpoint not in expected_actions)
        or (observed_escalation and not expected_escalation)
    )
    premature_action = observed_action and not expected_action

    text = _normalize_output_text(output)
    no_locked = "locked_test" not in text
    no_gold = not any(term in text for term in SENSITIVE_OUTPUT_TERMS)
    schema_valid = _schema_valid(output)

    components = [schema_valid, decision_correct, evidence_correct, action_correct, escalation_correct, no_locked, no_gold]
    quality = sum(1 for value in components if value) / len(components)
    return {
        "scoreable": True,
        "schema_valid": schema_valid,
        "decision_correct": decision_correct,
        "evidence_correct": evidence_correct,
        "evidence_recall": round(evidence_recall, 4),
        "extra_public_read_count": len(extra_public_reads),
        "action_correct": action_correct,
        "escalation_correct": escalation_correct,
        "premature_action": premature_action,
        "unsupported_action_or_escalation": unsupported_action_or_escalation,
        "no_locked_test_claim": no_locked,
        "no_gold_claim": no_gold,
        "reference_quality": round(quality, 4),
        "private_row_count": 1,
        "private_expected_path_item_count": int(oracle.get("private_expected_path_item_count") or 0),
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scoreable = [row for row in rows if row.get("scoreable")]
    if not scoreable:
        return {
            "scoreable_calls": 0,
            "reference_quality": None,
            "decision_correctness": None,
            "evidence_correctness": None,
            "mean_expected_read_recall": None,
            "action_correctness": None,
            "escalation_correctness": None,
            "premature_action_rate": None,
            "unsupported_action_or_escalation_rate": None,
            "locked_test_or_gold_leakage_rate": None,
        }

    def rate(key: str) -> float:
        return round(sum(1 for row in scoreable if row.get(key)) / len(scoreable), 4)

    return {
        "scoreable_calls": len(scoreable),
        "reference_quality": round(sum(float(row["reference_quality"]) for row in scoreable) / len(scoreable), 4),
        "decision_correctness": rate("decision_correct"),
        "evidence_correctness": rate("evidence_correct"),
        "mean_expected_read_recall": round(sum(float(row["evidence_recall"]) for row in scoreable) / len(scoreable), 4),
        "mean_extra_public_read_count": round(sum(int(row["extra_public_read_count"]) for row in scoreable) / len(scoreable), 4),
        "action_correctness": rate("action_correct"),
        "escalation_correctness": rate("escalation_correct"),
        "premature_action_rate": rate("premature_action"),
        "unsupported_action_or_escalation_rate": rate("unsupported_action_or_escalation"),
        "locked_test_or_gold_leakage_rate": round(
            sum(1 for row in scoreable if not row.get("no_locked_test_claim") or not row.get("no_gold_claim")) / len(scoreable),
            4,
        ),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    split_manifest = _load(args.split_manifest)
    fixed = _load(args.fixed_output_file)
    oracle_payload = _load(args.oracle_file)
    cases_payload = _load(args.agent_input_cases)
    if not isinstance(split_manifest, dict) or not isinstance(fixed, dict):
        raise AssertionError("split manifest and fixed output must be JSON objects")

    calls = collect_calls(fixed)
    assert_fixed_scope(fixed, calls, split_manifest)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected_tickets = runner_selected_ticket_by_group(cases_payload, fixed_groups)
    oracles = adapt_expected_paths(oracle_payload, fixed_groups, split_manifest, selected_tickets)
    rows = [score_call(call, oracles.get(str(call.get("group_id")))) for call in calls]
    metrics = aggregate(rows)
    parsed = sum(1 for call in calls if output_payload(call) is not None)

    alignment_counts = Counter(str(value.get("alignment_status") or "unknown") for value in oracles.values())
    unique_groups = sum(1 for value in oracles.values() if value.get("alignment_status") == ALIGNMENT_UNIQUE)
    alignment_resolved = bool(fixed_groups) and unique_groups == len(fixed_groups)
    normalization_resolved = all(
        int(value.get("unrecognized_expected_steps") or 0) == 0
        for value in oracles.values()
        if value.get("alignment_status") == ALIGNMENT_UNIQUE
    )

    status = "E9_V4_MEASUREMENT_ONLY_PASS" if metrics["scoreable_calls"] else "E9_V4_MEASUREMENT_ONLY_NO_SCOREABLE_CALLS"
    return {
        "report_version": "e9-visible-ticket-aligned-tool-signature-evaluator-v4-measurement-only",
        "status": status,
        "scope": {
            "allowed_splits": sorted(ALLOWED_SPLITS),
            "locked_test_fixed_outputs_accessed": False,
            "validation_feedback_used_for_evaluator_design": False,
            "model_received_private_oracle": False,
        },
        "inputs": {
            "fixed_calls_consumed": len(calls),
            "parsed_model_outputs_available": parsed,
            "fixed_groups_found": len(fixed_groups),
            "runner_selected_visible_cases_for_fixed_groups": len(selected_tickets),
            "private_ticket_aligned_oracles_loaded": unique_groups,
            "calls_with_matching_private_oracle": sum(
                1
                for call in calls
                if oracles.get(str(call.get("group_id")), {}).get("alignment_status") == ALIGNMENT_UNIQUE
            ),
            "alignment_status_counts_for_fixed_groups": dict(sorted(alignment_counts.items())),
        },
        "aggregate_metrics": metrics,
        "validity": {
            "expected_path_step_tool_signature_coverage_required": 1.0,
            "root_question_used_for_labels": False,
            "mode_used_for_action_escalation_labels": False,
            "whole_output_text_used_for_evidence_credit": False,
            "all_public_read_signatures_per_evidence_item_extracted": True,
            "generic_human_or_specialist_words_create_escalation_label": False,
            "general_free_text_groundedness": "UNMEASURED",
            "runner_selection_rule_replayed": "first_agent_input_case_per_asset",
            "oracle_alignment_key": "group_or_asset_plus_exact_ticket_id",
            "group_union_used_for_supervision": False,
            "zero_or_multiple_ticket_match_fallback_to_group_union": False,
            "visible_case_ticket_alignment_gate_resolved_for_fixed_groups": alignment_resolved,
            "expected_step_normalization_resolved_for_aligned_rows": normalization_resolved,
            "validation_gate_authorized": False,
        },
        "privacy": {
            "private_rows_in_summary": False,
            "private_expected_path_text_in_summary": False,
            "private_endpoint_names_in_summary": False,
            "private_group_labels_in_summary": False,
            "private_ticket_ids_in_summary": False,
            "output_hashes_in_summary": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--oracle-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "fixed_calls_consumed": summary["inputs"]["fixed_calls_consumed"],
        "parsed_model_outputs_available": summary["inputs"]["parsed_model_outputs_available"],
        "fixed_groups_found": summary["inputs"]["fixed_groups_found"],
        "runner_selected_visible_cases_for_fixed_groups": summary["inputs"]["runner_selected_visible_cases_for_fixed_groups"],
        "private_ticket_aligned_oracles_loaded": summary["inputs"]["private_ticket_aligned_oracles_loaded"],
        "calls_with_matching_private_oracle": summary["inputs"]["calls_with_matching_private_oracle"],
        "scoreable_calls": summary["aggregate_metrics"]["scoreable_calls"],
        "visible_case_ticket_alignment_gate_resolved_for_fixed_groups": summary["validity"]["visible_case_ticket_alignment_gate_resolved_for_fixed_groups"],
        "validation_gate_authorized": summary["validity"]["validation_gate_authorized"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())