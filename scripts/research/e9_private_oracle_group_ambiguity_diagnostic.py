#!/usr/bin/env python3
"""Aggregate-only ambiguity diagnostic for private expected-path supervision.

Reads private expected paths locally and maps them to frozen public split groups,
but prints no group IDs, endpoint names, oracle text, per-row results, hashes or
private paths. The goal is to determine whether group-level scoring merges
multiple independent trajectories or multiple distinct action targets.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.e2.tool_registry import TOOLS

ASSET_RE = re.compile(r"\basset_[A-Za-z0-9]+\b", re.IGNORECASE)
METHOD_RE = re.compile(r"\b(GET|POST|PATCH|PUT|DELETE)\b", re.IGNORECASE)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _template_regex(template: str) -> re.Pattern[str]:
    escaped = re.escape(template.lower())
    escaped = re.sub(r"\\\{[^{}]+\\\}", r"[a-z0-9_.:{}-]+", escaped)
    return re.compile(escaped, re.IGNORECASE)


TOOL_PATTERNS = [
    (
        f"{str(tool.method).upper()} {str(tool.path_template)}",
        str(getattr(tool.kind, "value", tool.kind)).lower(),
        str(tool.method).upper(),
        _template_regex(str(tool.path_template)),
    )
    for tool in TOOLS
]


def _canonical_step(text: str) -> tuple[str | None, str | None]:
    methods = {m.group(1).upper() for m in METHOD_RE.finditer(text)}
    lowered = text.lower()
    for signature, kind, method, path_re in TOOL_PATTERNS:
        if method in methods and path_re.search(lowered):
            return signature, kind
    return None, None


def _split_groups(split_payload: dict[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for split, body in (split_payload.get("splits") or {}).items():
        ids: set[str] = set()
        for group in body.get("groups", []):
            if isinstance(group, dict) and group.get("group_id"):
                ids.add(str(group["group_id"]))
        result[str(split)] = ids
    return result


def run(oracle_path: Path, split_path: Path) -> dict[str, Any]:
    oracle = _load(oracle_path)
    split = _load(split_path)
    if not isinstance(oracle, list) or not isinstance(split, dict):
        raise AssertionError("unexpected oracle or split shape")

    groups_by_split = _split_groups(split)
    all_groups = set().union(*groups_by_split.values()) if groups_by_split else set()
    canonical_by_lower = {g.lower(): g for g in all_groups}
    split_for_group = {g: s for s, groups in groups_by_split.items() for g in groups}

    rows_per_group: dict[str, int] = defaultdict(int)
    distinct_actions_per_group: dict[str, set[str]] = defaultdict(set)
    distinct_steps_per_group: dict[str, set[str]] = defaultdict(set)
    mapped_rows = 0
    unmapped_rows = 0

    for row in oracle:
        if not isinstance(row, dict) or not isinstance(row.get("expected_path"), list):
            continue
        blob = json.dumps(row, ensure_ascii=False, sort_keys=True).lower()
        mentions = {
            canonical_by_lower[m.lower()]
            for m in ASSET_RE.findall(blob)
            if m.lower() in canonical_by_lower
        }
        if not mentions:
            unmapped_rows += 1
            continue
        mapped_rows += 1
        step_signatures: set[str] = set()
        action_signatures: set[str] = set()
        for item in row.get("expected_path") or []:
            if not isinstance(item, dict):
                continue
            signature, kind = _canonical_step(str(item.get("step") or ""))
            if signature:
                step_signatures.add(signature)
                if kind == "action":
                    action_signatures.add(signature)
        for group in mentions:
            rows_per_group[group] += 1
            distinct_steps_per_group[group].update(step_signatures)
            distinct_actions_per_group[group].update(action_signatures)

    rows_hist = Counter(rows_per_group.values())
    action_hist = Counter(len(distinct_actions_per_group[g]) for g in rows_per_group)
    step_hist = Counter(len(distinct_steps_per_group[g]) for g in rows_per_group)

    def split_summary(name: str) -> dict[str, Any]:
        groups = [g for g in rows_per_group if split_for_group.get(g) == name]
        return {
            "groups_with_private_rows": len(groups),
            "groups_with_multiple_private_rows": sum(1 for g in groups if rows_per_group[g] > 1),
            "groups_with_multiple_distinct_action_signatures": sum(1 for g in groups if len(distinct_actions_per_group[g]) > 1),
            "groups_with_zero_action_signatures": sum(1 for g in groups if not distinct_actions_per_group[g]),
            "groups_with_one_action_signature": sum(1 for g in groups if len(distinct_actions_per_group[g]) == 1),
        }

    return {
        "status": "E9_PRIVATE_ORACLE_GROUP_AMBIGUITY_DIAGNOSTIC",
        "oracle_rows_found": sum(1 for row in oracle if isinstance(row, dict) and isinstance(row.get("expected_path"), list)),
        "mapped_rows": mapped_rows,
        "unmapped_rows": unmapped_rows,
        "groups_with_private_rows": len(rows_per_group),
        "private_rows_per_group_histogram": {str(k): v for k, v in sorted(rows_hist.items())},
        "distinct_public_tool_signatures_per_group_histogram": {str(k): v for k, v in sorted(step_hist.items())},
        "distinct_action_signatures_per_group_histogram": {str(k): v for k, v in sorted(action_hist.items())},
        "split_aggregate": {name: split_summary(name) for name in ("DEV", "VALIDATION", "LOCKED_TEST")},
        "group_level_supervision_has_multiple_rows": any(v > 1 for v in rows_per_group.values()),
        "group_level_supervision_has_multiple_action_targets": any(len(v) > 1 for v in distinct_actions_per_group.values()),
        "candidate_specific_output_used": False,
        "root_question_used_for_semantic_label": False,
        "mode_used_for_semantic_label": False,
        "prints_oracle_values": False,
        "prints_expected_path_text": False,
        "prints_group_ids": False,
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
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    args = parser.parse_args()
    print(json.dumps(run(args.oracle_file, args.split_manifest), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
