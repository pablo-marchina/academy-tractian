#!/usr/bin/env python3
"""Public-metadata-only audit of benchmark split and representative DEV coverage."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError("input must be a JSON object")
    return value


def _groups(split: dict[str, Any], name: str) -> list[dict[str, Any]]:
    payload = (split.get("splits") or {}).get(name, {})
    groups = payload.get("groups", []) if isinstance(payload, dict) else []
    return [g for g in groups if isinstance(g, dict)]


def _flat(groups: list[dict[str, Any]], key: str) -> list[str]:
    out: list[str] = []
    for group in groups:
        values = group.get(key, [])
        if isinstance(values, list):
            out.extend(str(x) for x in values)
    return out


def run(split_path: Path, representative_manifest_path: Path) -> dict[str, Any]:
    split = _load(split_path)
    rep = _load(representative_manifest_path)
    names = ("DEV", "VALIDATION", "LOCKED_TEST")
    groups_by_split = {name: _groups(split, name) for name in names}
    ids_by_split = {name: {str(g.get("group_id")) for g in groups_by_split[name]} for name in names}
    scenarios_by_split = {name: set(_flat(groups_by_split[name], "scenarios")) for name in names}
    tickets_by_split = {name: set(_flat(groups_by_split[name], "tickets")) for name in names}

    overlaps: dict[str, Any] = {}
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            overlaps[f"{left}__{right}"] = {
                "group_overlap_count": len(ids_by_split[left] & ids_by_split[right]),
                "scenario_overlap_count": len(scenarios_by_split[left] & scenarios_by_split[right]),
                "ticket_overlap_count": len(tickets_by_split[left] & tickets_by_split[right]),
            }

    dev_groups = groups_by_split["DEV"]
    dev_ids = ids_by_split["DEV"]
    representative = set((rep.get("representative_groups") or {}).get("DEV", []))
    omitted = sorted(dev_ids - representative)
    included = sorted(dev_ids & representative)

    dev_scenarios = set(_flat(dev_groups, "scenarios"))
    dev_tickets = set(_flat(dev_groups, "tickets"))
    selected_groups = [g for g in dev_groups if str(g.get("group_id")) in representative]
    selected_scenarios = set(_flat(selected_groups, "scenarios"))
    selected_tickets = set(_flat(selected_groups, "tickets"))
    dev_modalities = set(_flat(dev_groups, "modalities"))
    selected_modalities = set(_flat(selected_groups, "modalities"))
    omitted_modalities = sorted(dev_modalities - selected_modalities)

    omitted_group_metadata = []
    for g in dev_groups:
        gid = str(g.get("group_id"))
        if gid in omitted:
            omitted_group_metadata.append({
                "group_id": gid,
                "scenarios": g.get("scenarios", []),
                "tickets": g.get("tickets", []),
                "modalities": g.get("modalities", []),
                "coverage_tags": g.get("coverage_tags", []),
            })

    aggregate_declared = split.get("aggregate_counts", {})
    aggregate_match = all(
        isinstance(aggregate_declared.get(name), dict)
        and aggregate_declared[name].get("groups") == len(groups_by_split[name])
        and aggregate_declared[name].get("scenarios") == len(scenarios_by_split[name])
        for name in names
    )

    source_group_count = split.get("source_group_count")
    actual_source_groups = sum(len(ids_by_split[name]) for name in names)
    no_cross_split_overlap = all(
        item["group_overlap_count"] == 0
        and item["scenario_overlap_count"] == 0
        and item["ticket_overlap_count"] == 0
        for item in overlaps.values()
    )

    return {
        "status": "BENCHMARK_SPLIT_PUBLIC_COVERAGE_AUDIT",
        "split_schema_version": split.get("schema_version"),
        "split_status": split.get("status"),
        "source_group_count_declared": source_group_count,
        "source_group_count_actual": actual_source_groups,
        "source_group_count_matches": source_group_count == actual_source_groups,
        "aggregate_counts_match": aggregate_match,
        "cross_split_overlap": overlaps,
        "cross_split_group_scenario_ticket_disjoint": no_cross_split_overlap,
        "split_counts": {
            name: {
                "groups": len(ids_by_split[name]),
                "scenarios": len(scenarios_by_split[name]),
                "tickets": len(tickets_by_split[name]),
                "modalities": sorted(set(_flat(groups_by_split[name], "modalities"))),
            }
            for name in names
        },
        "representative_dev_gate": {
            "declared_group_count": len(representative),
            "full_dev_group_count": len(dev_ids),
            "group_coverage_fraction": round(len(representative & dev_ids) / len(dev_ids), 4) if dev_ids else None,
            "included_groups": included,
            "omitted_groups": omitted,
            "full_dev_scenario_count": len(dev_scenarios),
            "representative_scenario_count": len(selected_scenarios),
            "scenario_coverage_fraction": round(len(selected_scenarios) / len(dev_scenarios), 4) if dev_scenarios else None,
            "full_dev_ticket_count": len(dev_tickets),
            "representative_ticket_count": len(selected_tickets),
            "ticket_coverage_fraction": round(len(selected_tickets) / len(dev_tickets), 4) if dev_tickets else None,
            "full_dev_modalities": sorted(dev_modalities),
            "representative_modalities": sorted(selected_modalities),
            "omitted_modalities": omitted_modalities,
            "omitted_group_public_metadata": omitted_group_metadata,
        },
        "representative_gate_is_full_dev": representative == dev_ids,
        "validation_group_count": len(ids_by_split["VALIDATION"]),
        "locked_test_group_count": len(ids_by_split["LOCKED_TEST"]),
        "reads_private_oracle": False,
        "reads_model_outputs": False,
        "uses_validation_feedback": False,
        "uses_locked_test_only_public_frozen_metadata": True,
        "changes_split": False,
        "changes_candidate": False,
        "changes_scorer": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument(
        "--representative-manifest",
        type=Path,
        default=Path("research/experiments/e10b-dev-only-action-escalation-calibration-manifest.json"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.split, args.representative_manifest), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
