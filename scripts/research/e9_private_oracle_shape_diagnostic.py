#!/usr/bin/env python3
"""Shape-only diagnostic for the private E9 expected-path oracle.

Runs locally. It prints only container types, counts, length buckets, and field
names. It never prints field values, text, IDs, asset/group names, hashes,
private paths, expected-path contents, or evaluator labels.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
V2_PATH = HERE / "e9_evaluator_side_scorer_v2.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v2 = load_module("e9_v2_for_oracle_shape", V2_PATH)


def _type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, (int, float)):
        return "number"
    return type(value).__name__


def _length_bucket(value: str) -> str:
    n = len(value)
    if n == 0:
        return "0"
    if n <= 40:
        return "1-40"
    if n <= 120:
        return "41-120"
    if n <= 300:
        return "121-300"
    return "301+"


def _sorted(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def run(oracle_file: Path) -> dict[str, Any]:
    payload = json.loads(oracle_file.read_text(encoding="utf-8"))
    rows = v2.expected_path_rows(payload)

    row_key_counts: Counter[str] = Counter()
    row_value_types: Counter[str] = Counter()
    expected_path_types: Counter[str] = Counter()
    expected_path_length_hist: Counter[str] = Counter()
    expected_item_types: Counter[str] = Counter()
    expected_item_object_key_counts: Counter[str] = Counter()
    expected_item_object_value_types: Counter[str] = Counter()
    expected_item_string_length_buckets: Counter[str] = Counter()
    root_question_types: Counter[str] = Counter()
    root_question_length_buckets: Counter[str] = Counter()
    mode_types: Counter[str] = Counter()

    for row in rows:
        if not isinstance(row, dict):
            continue
        for key, value in row.items():
            row_key_counts[str(key)] += 1
            row_value_types[f"{key}:{_type(value)}"] += 1

        root = row.get("root_question")
        root_question_types[_type(root)] += 1
        if isinstance(root, str):
            root_question_length_buckets[_length_bucket(root)] += 1
        mode_types[_type(row.get("mode"))] += 1

        expected = row.get("expected_path")
        expected_path_types[_type(expected)] += 1
        if isinstance(expected, list):
            expected_path_length_hist[str(len(expected))] += 1
            for item in expected:
                item_type = _type(item)
                expected_item_types[item_type] += 1
                if isinstance(item, str):
                    expected_item_string_length_buckets[_length_bucket(item)] += 1
                elif isinstance(item, dict):
                    for key, value in item.items():
                        expected_item_object_key_counts[str(key)] += 1
                        expected_item_object_value_types[f"{key}:{_type(value)}"] += 1
        else:
            expected_path_length_hist["not_list"] += 1

    structured_item_fields_present = bool(expected_item_object_key_counts)
    return {
        "status": "E9_PRIVATE_ORACLE_SHAPE_DIAGNOSTIC",
        "top_level_type": _type(payload),
        "expected_path_rows_found": len(rows),
        "row_key_presence_counts": _sorted(row_key_counts),
        "row_field_type_counts": _sorted(row_value_types),
        "expected_path_container_types": _sorted(expected_path_types),
        "expected_path_item_count_histogram": _sorted(expected_path_length_hist),
        "expected_path_item_types": _sorted(expected_item_types),
        "expected_path_item_object_key_presence_counts": _sorted(expected_item_object_key_counts),
        "expected_path_item_object_field_type_counts": _sorted(expected_item_object_value_types),
        "expected_path_item_string_length_buckets": _sorted(expected_item_string_length_buckets),
        "root_question_types": _sorted(root_question_types),
        "root_question_length_buckets": _sorted(root_question_length_buckets),
        "mode_types": _sorted(mode_types),
        "structured_expected_path_item_fields_present": structured_item_fields_present,
        "diagnostic_reads_private_oracle": True,
        "prints_oracle_values": False,
        "prints_expected_path_text": False,
        "prints_root_question_text": False,
        "prints_ids_or_asset_names": False,
        "prints_hashes": False,
        "prints_private_path": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "changes_scorer": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle-file", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.oracle_file), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
