#!/usr/bin/env python3
"""E9 evaluator v4.1: structural bugfixes over v4, measurement-only.

Changes are preregistered in e9-v4-1-structural-bugfix-amendment.json:
1) deterministic METHOD+path token parsing with exact path-segment matching;
2) leakage scanning over string values only, never JSON key names;
3) PASS requires complete scoreability of every fixed call.

All v4 supervision semantics remain frozen: visible-ticket alignment, no group
union fallback, evidence_plan-only evidence credit, no root_question/mode labels,
no VALIDATION authorization, and no LOCKED_TEST fixed outputs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).parent
V4_PATH = HERE / "e9_evaluator_side_scorer_v4.py"
SPEC = importlib.util.spec_from_file_location("e9_v4_parent", V4_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load evaluator v4")
v4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v4)

METHOD_RE = re.compile(r"\b(GET|POST|PATCH|PUT|DELETE)\b", re.IGNORECASE)
PATH_TOKEN_RE = re.compile(r"/[A-Za-z0-9_.:{}-]+(?:/[A-Za-z0-9_.:{}-]+)*")
LOCKED_VALUE_TERMS = ("locked_test", "locked test")
TERMINAL_SENTENCE_PUNCTUATION = ".,;:"


def _kind_value(tool: Any) -> str:
    return str(getattr(tool.kind, "value", tool.kind)).lower()


def _segments(path: str) -> list[str]:
    return [part for part in path.strip().split("/") if part]


def _template_matches_path(template: str, observed_path: str) -> bool:
    template_parts = _segments(template)
    observed_parts = _segments(observed_path)
    if len(template_parts) != len(observed_parts):
        return False
    for expected, observed in zip(template_parts, observed_parts):
        if expected.startswith("{") and expected.endswith("}"):
            if not observed:
                return False
            continue
        if expected.lower() != observed.lower():
            return False
    return True


def _literal_specificity(template: str) -> int:
    return sum(1 for part in _segments(template) if not (part.startswith("{") and part.endswith("}")))


PUBLIC_TOOL_SPECS = [
    {
        "signature": f"{str(tool.method).upper()} {str(tool.path_template)}",
        "method": str(tool.method).upper(),
        "template": str(tool.path_template),
        "kind": _kind_value(tool),
        "specificity": _literal_specificity(str(tool.path_template)),
    }
    for tool in v4.TOOLS
]


def _method_path_pairs(text: str) -> list[tuple[str, str]]:
    """Pair each HTTP method token with the first path token before the next method."""
    methods = list(METHOD_RE.finditer(text))
    pairs: list[tuple[str, str]] = []
    for index, match in enumerate(methods):
        start = match.end()
        end = methods[index + 1].start() if index + 1 < len(methods) else len(text)
        path_match = PATH_TOKEN_RE.search(text[start:end])
        if path_match:
            pairs.append((match.group(1).upper(), path_match.group(0)))
    return pairs


def _matching_specs(method: str, observed_path: str) -> list[dict[str, Any]]:
    # Try the exact token and a terminal-sentence-punctuation-stripped variant.
    # We consider both before specificity ranking so e.g. /knowledge/search.
    # resolves to the literal /knowledge/search route rather than the generic
    # /knowledge/{docId} placeholder route.
    candidates = [observed_path]
    trimmed = observed_path.rstrip(TERMINAL_SENTENCE_PUNCTUATION)
    if trimmed and trimmed != observed_path:
        candidates.append(trimmed)
    found: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        for spec in PUBLIC_TOOL_SPECS:
            if spec["method"] != method:
                continue
            if _template_matches_path(str(spec["template"]), candidate):
                found[str(spec["signature"])] = spec
    return list(found.values())


def canonical_tool_signatures(text: str, *, require_method: bool = True) -> list[tuple[str, str]]:
    if not require_method:
        raise AssertionError("v4.1 requires explicit METHOD+path signatures")
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for method, observed_path in _method_path_pairs(text):
        matches = _matching_specs(method, observed_path)
        if not matches:
            continue
        max_specificity = max(int(spec["specificity"]) for spec in matches)
        winners = [spec for spec in matches if int(spec["specificity"]) == max_specificity]
        for spec in winners:
            signature = str(spec["signature"])
            if signature not in seen:
                seen.add(signature)
                result.append((signature, str(spec["kind"])))
    return result


def canonical_tool_signature(text: str, *, require_method: bool = True) -> tuple[str | None, str | None]:
    matches = canonical_tool_signatures(text, require_method=require_method)
    return matches[0] if matches else (None, None)


# Freeze v4 supervision/alignment behavior while replacing only the preregistered
# METHOD+path normalization primitive used by expected-path adaptation.
v4.canonical_tool_signatures = canonical_tool_signatures
v4.canonical_tool_signature = canonical_tool_signature


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _string_values(child)


def _value_text(output: dict[str, Any]) -> str:
    return "\n".join(_string_values(output)).lower()


def score_call(call: dict[str, Any], oracle: dict[str, Any] | None) -> dict[str, Any]:
    output = v4.output_payload(call)
    if output is None:
        return {"scoreable": False, "reason": "parsed_model_output_missing"}
    if not oracle:
        return {"scoreable": False, "reason": "private_oracle_alignment_missing"}
    alignment_status = str(oracle.get("alignment_status") or "")
    if alignment_status != v4.ALIGNMENT_UNIQUE:
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
        decision_correct = decision in v4.NON_ACTION_CLASSES

    observed_reads: set[str] = set()
    plan = output.get("evidence_plan")
    if isinstance(plan, list):
        for item in plan:
            if not isinstance(item, str):
                continue
            for signature, kind in canonical_tool_signatures(item, require_method=True):
                if kind == "read":
                    observed_reads.add(signature)
    covered_reads = expected_reads & observed_reads
    evidence_recall = 1.0 if not expected_reads else len(covered_reads) / len(expected_reads)
    evidence_correct = evidence_recall == 1.0
    extra_public_reads = observed_reads - expected_reads

    rubric = output.get("action_escalation_rubric")
    rubric = rubric if isinstance(rubric, dict) else {}
    endpoint = rubric.get("action_endpoint")
    endpoint_signature, endpoint_kind = canonical_tool_signature(str(endpoint), require_method=True) if isinstance(endpoint, str) else (None, None)
    observed_endpoint = endpoint_signature if endpoint_kind == "action" else None

    observed_action = output.get("should_take_action_now") is True
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

    # Search values only. Required public schema keys such as no_locked_test must
    # never count as leakage merely because their key names contain the term.
    value_text = _value_text(output)
    no_locked = not any(term in value_text for term in LOCKED_VALUE_TERMS)
    no_gold = not any(term in value_text for term in v4.SENSITIVE_OUTPUT_TERMS)
    schema_valid = v4._schema_valid(output)

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


def run(args: argparse.Namespace) -> dict[str, Any]:
    split_manifest = v4._load(args.split_manifest)
    fixed = v4._load(args.fixed_output_file)
    oracle_payload = v4._load(args.oracle_file)
    cases_payload = v4._load(args.agent_input_cases)
    if not isinstance(split_manifest, dict) or not isinstance(fixed, dict):
        raise AssertionError("split manifest and fixed output must be JSON objects")

    calls = v4.collect_calls(fixed)
    v4.assert_fixed_scope(fixed, calls, split_manifest)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected_tickets = v4.runner_selected_ticket_by_group(cases_payload, fixed_groups)
    oracles = v4.adapt_expected_paths(oracle_payload, fixed_groups, split_manifest, selected_tickets)
    rows = [score_call(call, oracles.get(str(call.get("group_id")))) for call in calls]
    metrics = v4.aggregate(rows)
    parsed = sum(1 for call in calls if v4.output_payload(call) is not None)

    alignment_counts = Counter(str(value.get("alignment_status") or "unknown") for value in oracles.values())
    unique_groups = sum(1 for value in oracles.values() if value.get("alignment_status") == v4.ALIGNMENT_UNIQUE)
    alignment_resolved = bool(fixed_groups) and unique_groups == len(fixed_groups)
    normalization_resolved = all(
        int(value.get("unrecognized_expected_steps") or 0) == 0
        for value in oracles.values()
        if value.get("alignment_status") == v4.ALIGNMENT_UNIQUE
    )
    complete_scoreability = (
        bool(calls)
        and parsed == len(calls)
        and alignment_resolved
        and normalization_resolved
        and int(metrics.get("scoreable_calls") or 0) == len(calls)
    )
    if complete_scoreability:
        status = "E9_V4_1_MEASUREMENT_ONLY_PASS"
    elif int(metrics.get("scoreable_calls") or 0) == 0:
        status = "E9_V4_1_MEASUREMENT_ONLY_NO_SCOREABLE_CALLS"
    else:
        status = "E9_V4_1_MEASUREMENT_ONLY_NEEDS_REVIEW"

    return {
        "report_version": "e9-visible-ticket-aligned-tool-signature-evaluator-v4.1-measurement-only",
        "status": status,
        "scope": {
            "allowed_splits": sorted(v4.ALLOWED_SPLITS),
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
                1 for call in calls
                if oracles.get(str(call.get("group_id")), {}).get("alignment_status") == v4.ALIGNMENT_UNIQUE
            ),
            "alignment_status_counts_for_fixed_groups": dict(sorted(alignment_counts.items())),
        },
        "aggregate_metrics": metrics,
        "validity": {
            "expected_path_step_tool_signature_coverage_required": 1.0,
            "path_normalizer": "method_plus_path_segment_exact_match_with_literal_specificity",
            "leakage_scan_scope": "string_values_only_not_object_keys",
            "pass_requires_every_fixed_call_scoreable": True,
            "complete_fixed_measurement": complete_scoreability,
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
        "normalization_resolved": summary["validity"]["expected_step_normalization_resolved_for_aligned_rows"],
        "complete_fixed_measurement": summary["validity"]["complete_fixed_measurement"],
        "validation_gate_authorized": summary["validity"]["validation_gate_authorized"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
