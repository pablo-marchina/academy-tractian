#!/usr/bin/env python3
"""Aggregate-only alignment diagnostic between runner-visible cases and private expected paths.

The public runner selects the first agent-input case per asset. This diagnostic
replays only that selection rule locally and checks whether the selected visible
case can be matched to exactly one private expected-path row by ticket_id.

It prints aggregate counts only: no asset/group IDs, ticket IDs, oracle text,
expected paths, prompts, hashes, private paths, or per-row results.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _split_groups(payload: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for split, body in (payload.get("splits") or {}).items():
        groups: set[str] = set()
        for item in body.get("groups", []):
            if isinstance(item, dict) and item.get("group_id"):
                groups.add(str(item["group_id"]))
        result[str(split)] = groups
    return result


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


def run(oracle_path: Path, cases_path: Path, split_path: Path) -> dict[str, Any]:
    oracle = _load(oracle_path)
    cases = _load(cases_path)
    split = _load(split_path)
    if not isinstance(oracle, list) or not isinstance(split, dict):
        raise AssertionError("unexpected oracle or split shape")

    groups_by_split = _split_groups(split)
    all_groups = set().union(*groups_by_split.values()) if groups_by_split else set()
    canonical_by_lower = {group.lower(): group for group in all_groups}
    split_for_group = {group: name for name, groups in groups_by_split.items() for group in groups}

    case_records = _collect_case_records(cases)
    records_per_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    selected_visible_case: dict[str, dict[str, Any]] = {}
    for record in case_records:
        asset = _asset_id(record)
        if not asset or asset.lower() not in canonical_by_lower:
            continue
        group = canonical_by_lower[asset.lower()]
        records_per_group[group].append(record)
        if group not in selected_visible_case:
            # Exactly mirrors load_agent_visible_cases(): first record per asset.
            selected_visible_case[group] = record

    oracle_rows_by_group_ticket: dict[tuple[str, str], int] = defaultdict(int)
    oracle_rows_per_group: Counter[str] = Counter()
    oracle_rows_without_group = 0
    for row in oracle:
        if not isinstance(row, dict) or not isinstance(row.get("expected_path"), list):
            continue
        ticket = row.get("ticket_id")
        ticket = str(ticket) if isinstance(ticket, str) else None
        # Prefer explicit asset-like tokens in the serialized row only for group mapping;
        # values are never printed.
        blob = json.dumps(row, ensure_ascii=False, sort_keys=True).lower()
        mentioned = [group for group in all_groups if group.lower() in blob]
        if not mentioned:
            oracle_rows_without_group += 1
            continue
        for group in set(mentioned):
            oracle_rows_per_group[group] += 1
            if ticket:
                oracle_rows_by_group_ticket[(group, ticket)] += 1

    status_hist: Counter[str] = Counter()
    split_status: dict[str, Counter[str]] = {name: Counter() for name in ("DEV", "VALIDATION", "LOCKED_TEST")}
    groups_with_extra_group_rows_beyond_selected_ticket = 0
    selected_cases_without_ticket = 0

    for group, selected in selected_visible_case.items():
        split_name = split_for_group.get(group, "OTHER")
        ticket = _ticket_id(selected)
        if not ticket:
            selected_cases_without_ticket += 1
            status = "selected_visible_case_missing_ticket_id"
        else:
            matches = oracle_rows_by_group_ticket.get((group, ticket), 0)
            if matches == 1:
                status = "selected_ticket_matches_exactly_one_oracle_row"
            elif matches == 0:
                status = "selected_ticket_matches_no_oracle_row"
            else:
                status = "selected_ticket_matches_multiple_oracle_rows"
            if matches >= 1 and oracle_rows_per_group.get(group, 0) > matches:
                groups_with_extra_group_rows_beyond_selected_ticket += 1
        status_hist[status] += 1
        if split_name in split_status:
            split_status[split_name][status] += 1

    multi_case_groups = sum(1 for rows in records_per_group.values() if len(rows) > 1)
    selected_match_exact = status_hist["selected_ticket_matches_exactly_one_oracle_row"]
    selected_total = len(selected_visible_case)
    exact_fraction = round(selected_match_exact / selected_total, 4) if selected_total else 0.0

    return {
        "status": "E9_PRIVATE_ORACLE_VISIBLE_CASE_ALIGNMENT_DIAGNOSTIC",
        "agent_case_records_found": len(case_records),
        "frozen_groups_with_agent_case_records": len(records_per_group),
        "frozen_groups_with_multiple_agent_case_records": multi_case_groups,
        "runner_selected_visible_cases": selected_total,
        "selected_visible_cases_without_ticket_id": selected_cases_without_ticket,
        "selected_ticket_alignment_status_counts": dict(sorted(status_hist.items())),
        "selected_ticket_exact_single_oracle_row_fraction": exact_fraction,
        "groups_where_group_union_contains_oracle_rows_beyond_selected_ticket": groups_with_extra_group_rows_beyond_selected_ticket,
        "oracle_rows_without_frozen_group_mapping": oracle_rows_without_group,
        "split_aggregate": {
            name: {
                "runner_selected_visible_cases": sum(split_status[name].values()),
                "selected_ticket_alignment_status_counts": dict(sorted(split_status[name].items())),
            }
            for name in ("DEV", "VALIDATION", "LOCKED_TEST")
        },
        "runner_selection_rule_replayed": "first_agent_input_case_per_asset",
        "candidate_specific_output_used": False,
        "root_question_used_for_semantic_label": False,
        "mode_used_for_semantic_label": False,
        "prints_oracle_values": False,
        "prints_expected_path_text": False,
        "prints_group_ids": False,
        "prints_ticket_ids": False,
        "prints_endpoint_names": False,
        "prints_per_row_results": False,
        "prints_hashes": False,
        "prints_private_path": False,
        "uses_validation_feedback": False,
        "uses_locked_test_feedback": False,
        "changes_scorer": False,
        "changes_candidate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    args = parser.parse_args()
    print(json.dumps(run(args.oracle_file, args.agent_input_cases, args.split_manifest), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
