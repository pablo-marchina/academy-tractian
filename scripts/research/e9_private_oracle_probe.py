#!/usr/bin/env python3
"""Probe private DEV/VALIDATION oracle shape without leaking oracle contents.

This is a local diagnostic bridge for E9. It inspects only structural metadata:
container types, key-frequency counts, identifier-key counts and whether fixed
Groq output groups have matching identifiers anywhere in the private oracle JSON.

It intentionally does not print expected answers, paths, trajectories, labels, or
free-text values.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

FORBIDDEN_SPLITS = {"LOCKED_TEST"}
SAFE_IDENTIFIER_KEYS = {
    "asset_id",
    "assetId",
    "assetID",
    "asset",
    "group_id",
    "groupId",
    "case_id",
    "caseId",
    "scenario_id",
    "scenarioId",
    "ticket_id",
    "ticketId",
    "id",
    "split",
}
SENSITIVE_KEY_FRAGMENTS = (
    "expected",
    "answer",
    "oracle",
    "trajectory",
    "path",
    "label",
    "rationale",
    "explanation",
    "gold",
)
ASSET_RE = re.compile(r"\basset_[A-Za-z0-9]+\b")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def walk(payload: Any, *, path: str = "$", key_counter: Counter[str], id_counter: Counter[str], asset_mentions: Counter[str], max_depth: int = 12) -> None:
    if max_depth < 0:
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_counter[str(key)] += 1
            if str(key) in SAFE_IDENTIFIER_KEYS:
                id_counter[str(key)] += 1
                if isinstance(value, str):
                    for match in ASSET_RE.findall(value):
                        asset_mentions[match] += 1
            if isinstance(value, str):
                for match in ASSET_RE.findall(value):
                    asset_mentions[match] += 1
            if isinstance(value, (dict, list)):
                walk(value, path=f"{path}.{key}", key_counter=key_counter, id_counter=id_counter, asset_mentions=asset_mentions, max_depth=max_depth - 1)
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, (dict, list)):
                walk(item, path=f"{path}[]", key_counter=key_counter, id_counter=id_counter, asset_mentions=asset_mentions, max_depth=max_depth - 1)
            elif isinstance(item, str):
                for match in ASSET_RE.findall(item):
                    asset_mentions[match] += 1


def summarize_top_level(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return {
            "type": "object",
            "top_level_keys": sorted(str(key) for key in payload.keys())[:80],
            "top_level_key_count": len(payload),
        }
    if isinstance(payload, list):
        first_type = type(payload[0]).__name__ if payload else None
        first_keys = sorted(str(key) for key in payload[0].keys())[:80] if payload and isinstance(payload[0], dict) else []
        return {
            "type": "array",
            "length": len(payload),
            "first_item_type": first_type,
            "first_item_keys": first_keys,
        }
    return {"type": type(payload).__name__}


def infer_sensitive_keys(key_counter: Counter[str]) -> list[str]:
    keys: list[str] = []
    for key in key_counter:
        lowered = key.lower()
        if any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS):
            keys.append(key)
    return sorted(keys)[:120]


def run(args: argparse.Namespace) -> dict[str, Any]:
    oracle = load_json(args.oracle_file)
    fixed = load_json(args.fixed_output_file) if args.fixed_output_file and args.fixed_output_file.exists() else {}
    fixed_calls = collect_calls(fixed)
    fixed_groups = sorted({str(call.get("group_id")) for call in fixed_calls if call.get("group_id")})

    key_counter: Counter[str] = Counter()
    id_counter: Counter[str] = Counter()
    asset_mentions: Counter[str] = Counter()
    walk(oracle, key_counter=key_counter, id_counter=id_counter, asset_mentions=asset_mentions)

    locked_text_present = "LOCKED_TEST" in json.dumps(oracle, ensure_ascii=False)
    fixed_group_mentions = {group: asset_mentions.get(group, 0) for group in fixed_groups}
    matching_groups = sorted(group for group, count in fixed_group_mentions.items() if count > 0)

    summary = {
        "report_version": "e9-private-oracle-shape-probe-v1",
        "oracle_file": str(args.oracle_file),
        "top_level": summarize_top_level(oracle),
        "key_frequency_top_60": dict(key_counter.most_common(60)),
        "identifier_key_frequency": dict(id_counter.most_common()),
        "sensitive_key_names_seen_no_values_printed": infer_sensitive_keys(key_counter),
        "fixed_output_groups": fixed_groups,
        "fixed_output_group_mentions_in_oracle": fixed_group_mentions,
        "fixed_output_groups_with_direct_mentions": matching_groups,
        "locked_test_literal_seen_in_oracle_file": locked_text_present,
        "safe_next_interpretation": [
            "If fixed_output_groups_with_direct_mentions is empty, expected-paths is probably not keyed by asset_id/group_id.",
            "Use the top-level keys and identifier-key frequencies to add a format-specific adapter without exposing private gold.",
            "Do not paste expected answer values, trajectories or raw oracle rows into public logs or the repository.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "E9_PRIVATE_ORACLE_SHAPE_PROBE_PASS",
        "fixed_groups": len(fixed_groups),
        "direct_group_matches": len(matching_groups),
        "locked_test_literal_seen": locked_text_present,
        "out": str(args.out),
    }, indent=2))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle-file", type=Path, required=True)
    parser.add_argument("--fixed-output-file", type=Path, default=Path(""))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
