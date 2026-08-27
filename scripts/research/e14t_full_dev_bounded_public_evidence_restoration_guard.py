#!/usr/bin/env python3
"""E14t full-DEV deterministic bounded public evidence restoration guard.

Single-class evidence-plan intervention over the same fixed E14q2 full-DEV
outputs used by E14s. E14t first recomputes the exact frozen E14s selection,
then restores at most four omitted public reads globally, at most one per call.
Restoration candidates come only from the original E14q2 evidence_plan and are
ranked using public candidate breadth plus stable fixed-call order as a tie-break.

No private expected paths, scorer rows, semantic judge rows, VALIDATION feedback,
LOCKED_TEST content, group-specific rules, ticket-specific rules, or split
coverage tags are read. Only evidence_plan may change.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
S_PATH = HERE / "e14s_full_dev_public_evidence_candidate_pool_consensus_guard.py"
S_SPEC = importlib.util.spec_from_file_location("e14s_parent_for_e14t", S_PATH)
if S_SPEC is None or S_SPEC.loader is None:
    raise RuntimeError("failed to load E14s parent")
e14s = importlib.util.module_from_spec(S_SPEC)
S_SPEC.loader.exec_module(e14s)

v41 = e14s.v41
v4 = e14s.v4
base = e14s.base

EXPECTED_CALLS = 10
EXPECTED_GROUPS = 5
EXPECTED_E14S_BASE_READS_TOTAL = 59
MAX_ADDITIONAL_READS_TOTAL = 4
MAX_ADDITIONAL_READS_PER_CALL = 1
MAX_FINAL_READS_PER_CALL = 7
MAX_FINAL_READS_TOTAL = 63

PASS_STATUS = "E14T_FULL_DEV_BOUNDED_PUBLIC_EVIDENCE_RESTORATION_GUARD_PASS"
FAIL_STATUS = "E14T_FULL_DEV_BOUNDED_PUBLIC_EVIDENCE_RESTORATION_GUARD_NEEDS_REVIEW"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _non_evidence_signature(output: dict[str, Any]) -> dict[str, Any]:
    cloned = copy.deepcopy(output)
    cloned.pop("evidence_plan", None)
    return cloned


def _original_reads(output: dict[str, Any]) -> list[str]:
    return e14s._ordered_observed_reads(output)


def _base_selection(visible_case: dict[str, Any], output: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    selected, meta = e14s.selected_read_signatures(visible_case, output)
    return list(selected), dict(meta)


def _first_omitted_original(original: list[str], selected: list[str]) -> str | None:
    selected_set = set(selected)
    for signature in original:
        if signature not in selected_set:
            return signature
    return None


def _rank_key(entry: dict[str, Any]) -> tuple[int, int, int]:
    # Higher public/model-proposed evidence breadth is restored first. Stable
    # fixed-call order is only a deterministic tie-break and is not semantic.
    return (
        -int(entry["original_candidate_count"]),
        -int(entry["candidate_pool_count"]),
        int(entry["stable_index"]),
    )


def _select_restoration_indices(entries: list[dict[str, Any]]) -> set[int]:
    eligible = [
        entry
        for entry in entries
        if entry.get("restoration_candidate") is not None
        and len(entry.get("base_selected", [])) < MAX_FINAL_READS_PER_CALL
    ]
    eligible.sort(key=_rank_key)
    chosen = eligible[:MAX_ADDITIONAL_READS_TOTAL]
    return {int(entry["stable_index"]) for entry in chosen}


def run(args: argparse.Namespace) -> dict[str, Any]:
    fixed = _load(args.fixed_output_file)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be objects")

    transformed = copy.deepcopy(fixed)
    calls = v4.collect_calls(transformed)
    v4.assert_fixed_scope(transformed, calls, split_manifest)
    if len(calls) != EXPECTED_CALLS:
        raise AssertionError(f"E14t requires exactly {EXPECTED_CALLS} fixed full-DEV calls")

    visible_cases = base.load_agent_visible_cases(args.agent_input_cases)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected_cases = {group: visible_cases.get(group) for group in fixed_groups}
    missing_visible = sorted(group for group, case in selected_cases.items() if not isinstance(case, dict))
    if missing_visible:
        raise AssertionError("E14t requires one runner-selected visible case for every fixed DEV group")

    entries: list[dict[str, Any]] = []
    parsed = 0
    base_reads_total = 0
    restoration_candidates_available = 0

    for stable_index, call in enumerate(calls):
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        group = str(call.get("group_id") or "")
        visible_case = selected_cases.get(group)
        if not isinstance(visible_case, dict):
            continue

        parsed += 1
        original = _original_reads(output)
        base_selected, base_meta = _base_selection(visible_case, output)
        restoration_candidate = _first_omitted_original(original, base_selected)
        base_reads_total += len(base_selected)
        restoration_candidates_available += int(restoration_candidate is not None)

        entries.append(
            {
                "stable_index": stable_index,
                "call": call,
                "before": copy.deepcopy(output),
                "original": original,
                "base_selected": base_selected,
                "original_candidate_count": len(set(original)),
                "candidate_pool_count": int(base_meta.get("candidate_pool_count", 0)),
                "restoration_candidate": restoration_candidate,
            }
        )

    complete = parsed == EXPECTED_CALLS and len(fixed_groups) == EXPECTED_GROUPS and not missing_visible
    if not complete:
        raise AssertionError("E14t requires complete 10-call / 5-group fixed coverage")
    if base_reads_total != EXPECTED_E14S_BASE_READS_TOTAL:
        raise AssertionError(
            f"E14t expected exact frozen E14s base total {EXPECTED_E14S_BASE_READS_TOTAL}, got {base_reads_total}"
        )

    chosen_indices = _select_restoration_indices(entries)

    calls_changed = 0
    additions_total = 0
    calls_with_restoration = 0
    final_reads_total = 0
    max_final_reads_observed = 0
    non_evidence_changes = 0
    route_contract_failures = 0
    per_call_addition_failures = 0
    candidate_pool_failures = 0
    global_budget_failures = 0

    for entry in entries:
        call = entry["call"]
        before = entry["before"]
        selected = list(entry["base_selected"])
        additions_this_call = 0

        if int(entry["stable_index"]) in chosen_indices:
            candidate = entry["restoration_candidate"]
            if candidate is None:
                raise AssertionError("chosen E14t restoration call has no public restoration candidate")
            if candidate not in set(entry["original"]):
                candidate_pool_failures += 1
            elif candidate not in selected:
                selected.append(candidate)
                additions_this_call = 1

        if additions_this_call > MAX_ADDITIONAL_READS_PER_CALL:
            per_call_addition_failures += 1

        result = copy.deepcopy(before)
        result["evidence_plan"] = e14s._evidence_items(selected)
        after_order = e14s._ordered_observed_reads(result)

        if after_order != selected:
            route_contract_failures += 1
        if len(after_order) > MAX_FINAL_READS_PER_CALL:
            per_call_addition_failures += 1
        if not set(after_order).issubset(set(entry["original"]) | set(entry["base_selected"])):
            candidate_pool_failures += 1
        if _non_evidence_signature(before) != _non_evidence_signature(result):
            non_evidence_changes += 1

        additions_total += additions_this_call
        calls_with_restoration += int(additions_this_call > 0)
        final_reads_total += len(after_order)
        max_final_reads_observed = max(max_final_reads_observed, len(after_order))
        calls_changed += int(before.get("evidence_plan") != result.get("evidence_plan"))
        call["parsed_output"] = result

    if additions_total > MAX_ADDITIONAL_READS_TOTAL:
        global_budget_failures += 1
    if final_reads_total > MAX_FINAL_READS_TOTAL:
        global_budget_failures += 1
    if final_reads_total != base_reads_total + additions_total:
        global_budget_failures += 1

    passed = (
        complete
        and base_reads_total == EXPECTED_E14S_BASE_READS_TOTAL
        and additions_total <= MAX_ADDITIONAL_READS_TOTAL
        and calls_with_restoration <= MAX_ADDITIONAL_READS_TOTAL
        and final_reads_total <= MAX_FINAL_READS_TOTAL
        and max_final_reads_observed <= MAX_FINAL_READS_PER_CALL
        and non_evidence_changes == 0
        and route_contract_failures == 0
        and per_call_addition_failures == 0
        and candidate_pool_failures == 0
        and global_budget_failures == 0
    )
    status = PASS_STATUS if passed else FAIL_STATUS

    transformed["report_version"] = "e14t-full-dev-bounded-public-evidence-restoration-v1"
    transformed["status"] = status
    transformed["e14t_bounded_public_evidence_restoration"] = {
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "fixed_groups_found": len(fixed_groups),
        "runner_selected_visible_cases_for_fixed_groups": len(selected_cases) - len(missing_visible),
        "complete_fixed_transform": complete,
        "calls_changed": calls_changed,
        "e14s_base_read_signatures_total": base_reads_total,
        "restoration_candidates_available_calls": restoration_candidates_available,
        "restoration_reads_added_total": additions_total,
        "calls_with_restoration": calls_with_restoration,
        "final_public_read_signatures_total": final_reads_total,
        "max_additional_reads_total": MAX_ADDITIONAL_READS_TOTAL,
        "max_additional_reads_per_call": MAX_ADDITIONAL_READS_PER_CALL,
        "max_final_reads_per_call": MAX_FINAL_READS_PER_CALL,
        "max_final_reads_total": MAX_FINAL_READS_TOTAL,
        "max_final_reads_observed": max_final_reads_observed,
        "non_evidence_field_changes": non_evidence_changes,
        "route_contract_failures": route_contract_failures,
        "per_call_addition_failures": per_call_addition_failures,
        "candidate_pool_failures": candidate_pool_failures,
        "global_budget_failures": global_budget_failures,
        "group_or_ticket_specific_rules_used": False,
        "split_coverage_tags_used": False,
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
        **transformed["e14t_bounded_public_evidence_restoration"],
        "raw_outputs_printed": False,
        "visible_case_values_printed": False,
        "evidence_items_printed": False,
        "identifiers_printed": False,
        "group_ids_printed": False,
        "hashes_printed": False,
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
    return 0 if summary["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
