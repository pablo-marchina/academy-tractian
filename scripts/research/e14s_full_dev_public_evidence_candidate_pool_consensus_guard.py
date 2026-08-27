#!/usr/bin/env python3
"""E14s full-DEV deterministic public evidence candidate-pool consensus guard.

Single-class evidence-plan intervention over the fixed E14q2 full-DEV outputs.
It combines two public candidate sources: the fixed model-proposed evidence_plan
ordering and the preregistered E14r deterministic visible-case route selector.
No private expected paths, scorer rows, semantic judge rows, VALIDATION feedback,
LOCKED_TEST content, group-specific rules, ticket-specific rules, or split
coverage tags are read.

Only evidence_plan may change. All decision/action/escalation and free-text fields
remain byte-for-byte unchanged.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
R_PATH = HERE / "e14r_full_dev_public_visible_case_evidence_route_selection_guard.py"
R_SPEC = importlib.util.spec_from_file_location("e14r_parent_for_e14s", R_PATH)
if R_SPEC is None or R_SPEC.loader is None:
    raise RuntimeError("failed to load E14r parent")
e14r = importlib.util.module_from_spec(R_SPEC)
R_SPEC.loader.exec_module(e14r)

v41 = e14r.v41
v4 = e14r.v4
base = e14r.base
EXPECTED_CALLS = 10
MAX_SELECTED_READS = 6
PASS_STATUS = "E14S_FULL_DEV_PUBLIC_EVIDENCE_CANDIDATE_POOL_CONSENSUS_GUARD_PASS"
FAIL_STATUS = "E14S_FULL_DEV_PUBLIC_EVIDENCE_CANDIDATE_POOL_CONSENSUS_GUARD_NEEDS_REVIEW"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _non_evidence_signature(output: dict[str, Any]) -> dict[str, Any]:
    cloned = copy.deepcopy(output)
    cloned.pop("evidence_plan", None)
    return cloned


def _ordered_observed_reads(output: dict[str, Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return result
    for item in plan:
        if not isinstance(item, str):
            continue
        for signature, kind in v41.canonical_tool_signatures(item, require_method=True):
            if kind == "read" and signature not in seen:
                seen.add(signature)
                result.append(signature)
    return result


def _active_dependency_reads(output: dict[str, Any]) -> list[str]:
    endpoint = e14r._active_action_endpoint(output)
    if endpoint is None:
        return []
    wanted = {"GET /users/me", *e14r.ACTION_DEPENDENCY_READS.get(endpoint, ())}
    # Stable public order; only public reads already defined by E14r's frozen
    # action-dependency contract are eligible for the highest-priority tier.
    return [signature for signature in e14r.READ_ORDER if signature in wanted]


def _append_unique(target: list[str], candidates: list[str], *, cap: int) -> None:
    for signature in candidates:
        if signature in target:
            continue
        target.append(signature)
        if len(target) >= cap:
            return


def selected_read_signatures(
    visible_case: dict[str, Any],
    output: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    original = _ordered_observed_reads(output)
    e14r_selected, _ = e14r.selected_read_signatures(visible_case, output)
    original_set = set(original)
    e14r_set = set(e14r_selected)
    candidate_pool = original_set | e14r_set

    active = _active_dependency_reads(output)
    consensus = [signature for signature in original if signature in e14r_set]
    remaining_e14r = [signature for signature in e14r_selected if signature not in original_set]
    remaining_original = [signature for signature in original if signature not in e14r_set]

    selected: list[str] = []
    for tier in (active, consensus, remaining_e14r, remaining_original):
        _append_unique(selected, tier, cap=MAX_SELECTED_READS)
        if len(selected) >= MAX_SELECTED_READS:
            break

    # Fail-closed: every selected route must come from one of the two frozen
    # public candidate sources. No route synthesis occurs here.
    if not set(selected).issubset(candidate_pool):
        raise AssertionError("E14s selected a route outside the public candidate pool")

    return selected, {
        "original_candidate_count": len(original_set),
        "e14r_candidate_count": len(e14r_set),
        "candidate_pool_count": len(candidate_pool),
        "active_dependency_candidate_count": len(set(active)),
        "consensus_candidate_count": len(set(consensus)),
        "e14r_only_candidate_count": len(e14r_set - original_set),
        "original_only_candidate_count": len(original_set - e14r_set),
        "selected_count": len(selected),
    }


def _evidence_items(signatures: list[str]) -> list[str]:
    return [
        f"{signature} to collect the public evidence selected by the frozen candidate-pool policy before any conclusion or state-changing step."
        for signature in signatures
    ]


def transform_output(
    output: dict[str, Any],
    visible_case: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(output)
    result = copy.deepcopy(output)
    before_reads = set(_ordered_observed_reads(before))
    selected, selection_meta = selected_read_signatures(visible_case, before)
    result["evidence_plan"] = _evidence_items(selected)
    after_order = _ordered_observed_reads(result)
    after_reads = set(after_order)

    non_evidence_preserved = _non_evidence_signature(before) == _non_evidence_signature(result)
    exact_selected_routes = after_order == selected
    each_item_exactly_one_read = all(
        len([pair for pair in v41.canonical_tool_signatures(item, require_method=True) if pair[1] == "read"]) == 1
        and not any(pair[1] == "action" for pair in v41.canonical_tool_signatures(item, require_method=True))
        for item in result.get("evidence_plan", [])
        if isinstance(item, str)
    )

    return result, {
        **selection_meta,
        "changed": before.get("evidence_plan") != result.get("evidence_plan"),
        "before_read_count": len(before_reads),
        "after_read_count": len(after_reads),
        "added_read_count": len(after_reads - before_reads),
        "removed_read_count": len(before_reads - after_reads),
        "retained_read_count": len(after_reads & before_reads),
        "non_evidence_preserved": non_evidence_preserved,
        "exact_selected_routes": exact_selected_routes,
        "each_item_exactly_one_read": each_item_exactly_one_read,
        "selected_read_count_within_cap": len(after_reads) <= MAX_SELECTED_READS,
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
        raise AssertionError(f"E14s requires exactly {EXPECTED_CALLS} fixed full-DEV calls")

    visible_cases = base.load_agent_visible_cases(args.agent_input_cases)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected_cases = {group: visible_cases.get(group) for group in fixed_groups}
    missing_visible = sorted(group for group, case in selected_cases.items() if not isinstance(case, dict))
    if missing_visible:
        raise AssertionError("E14s requires one runner-selected visible case for every fixed DEV group")

    parsed = 0
    calls_changed = 0
    before_reads_total = 0
    after_reads_total = 0
    added_reads_total = 0
    removed_reads_total = 0
    retained_reads_total = 0
    candidate_pool_total = 0
    consensus_candidates_total = 0
    e14r_only_candidates_total = 0
    original_only_candidates_total = 0
    active_dependency_candidates_total = 0
    non_evidence_changes = 0
    route_contract_failures = 0
    cap_failures = 0

    for call in calls:
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        group = str(call.get("group_id") or "")
        visible_case = selected_cases.get(group)
        if not isinstance(visible_case, dict):
            continue
        parsed += 1
        guarded, meta = transform_output(output, visible_case)
        calls_changed += int(meta["changed"])
        before_reads_total += int(meta["before_read_count"])
        after_reads_total += int(meta["after_read_count"])
        added_reads_total += int(meta["added_read_count"])
        removed_reads_total += int(meta["removed_read_count"])
        retained_reads_total += int(meta["retained_read_count"])
        candidate_pool_total += int(meta["candidate_pool_count"])
        consensus_candidates_total += int(meta["consensus_candidate_count"])
        e14r_only_candidates_total += int(meta["e14r_only_candidate_count"])
        original_only_candidates_total += int(meta["original_only_candidate_count"])
        active_dependency_candidates_total += int(meta["active_dependency_candidate_count"])
        non_evidence_changes += int(not meta["non_evidence_preserved"])
        route_contract_failures += int(not (meta["exact_selected_routes"] and meta["each_item_exactly_one_read"]))
        cap_failures += int(not meta["selected_read_count_within_cap"])
        call["parsed_output"] = guarded

    complete = parsed == EXPECTED_CALLS and len(fixed_groups) == 5 and not missing_visible
    passed = complete and non_evidence_changes == 0 and route_contract_failures == 0 and cap_failures == 0
    status = PASS_STATUS if passed else FAIL_STATUS

    transformed["report_version"] = "e14s-full-dev-public-evidence-candidate-pool-consensus-v1"
    transformed["status"] = status
    transformed["e14s_public_evidence_candidate_pool_consensus"] = {
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "fixed_groups_found": len(fixed_groups),
        "runner_selected_visible_cases_for_fixed_groups": len(selected_cases) - len(missing_visible),
        "complete_fixed_transform": complete,
        "calls_changed": calls_changed,
        "public_read_signatures_before_total": before_reads_total,
        "public_read_signatures_after_total": after_reads_total,
        "public_read_signatures_added_total": added_reads_total,
        "public_read_signatures_removed_total": removed_reads_total,
        "public_read_signatures_retained_total": retained_reads_total,
        "public_candidate_pool_total": candidate_pool_total,
        "consensus_candidates_total": consensus_candidates_total,
        "e14r_only_candidates_total": e14r_only_candidates_total,
        "original_only_candidates_total": original_only_candidates_total,
        "active_dependency_candidates_total": active_dependency_candidates_total,
        "max_selected_reads_per_call": MAX_SELECTED_READS,
        "non_evidence_field_changes": non_evidence_changes,
        "route_contract_failures": route_contract_failures,
        "selected_read_cap_failures": cap_failures,
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
        **transformed["e14s_public_evidence_candidate_pool_consensus"],
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
