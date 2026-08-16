#!/usr/bin/env python3
"""E9 evaluator-side scorer v3 with case-safe expected-paths mapping.

The v2 expected-path adapter correctly identified the private oracle shape but
matched asset IDs case-sensitively after lowercasing the oracle row text. The
TRACTIAN IDs in fixed outputs keep canonical capitalization, for example
`asset_B204`, while lowercased oracle text contains `asset_b204`.

This wrapper patches only that mapping step. It preserves the v2 scorer contract:
private expected-path values are consumed only locally by the scorer, raw oracle
values are not printed, LOCKED_TEST stays blocked, and the model never sees
oracle/gold data.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

V2_PATH = Path(__file__).with_name("e9_evaluator_side_scorer_v2.py")
SPEC = importlib.util.spec_from_file_location("e9_v2", V2_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e9_evaluator_side_scorer_v2.py")
e9_v2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e9_v2)

ASSET_RE = re.compile(r"\basset_[A-Za-z0-9]+\b")


def adapt_expected_paths_case_safe(payload: Any, fixed_groups: set[str], split_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map expected-path rows to fixed output groups case-insensitively.

    The output keys preserve the canonical group IDs from fixed Groq outputs.
    No raw expected-path values are printed or returned beyond hashed/sanitized
    scorer summaries already produced by v2 scoring logic.
    """
    rows = e9_v2.expected_path_rows(payload)
    locked_groups = e9_v2.split_groups(split_manifest).get("LOCKED_TEST", set())
    canonical_by_lower = {group.lower(): group for group in fixed_groups}
    locked_lower = {group.lower() for group in locked_groups}
    oracles: dict[str, dict[str, Any]] = {}

    for row in rows:
        row_blob = json.dumps(row, ensure_ascii=False, sort_keys=True).lower()
        mentioned_lower = set(ASSET_RE.findall(row_blob))
        mentions = {
            canonical_by_lower[asset_lower]
            for asset_lower in mentioned_lower
            if asset_lower in canonical_by_lower and asset_lower not in locked_lower
        }
        if not mentions:
            continue

        flags = e9_v2.infer_flags(row)
        terms = e9_v2.private_terms(row.get("expected_path", row)) or e9_v2.private_terms(row.get("root_question", row))
        source_hash = e9_v2.stable_hash(row)
        for group_id in mentions:
            oracle = oracles.setdefault(
                group_id,
                {
                    "oracle_format": "expected_paths_asset_mention_adapter_v3_case_safe",
                    "private_row_count": 0,
                    "private_expected_path_item_count": 0,
                    "private_source_hashes": [],
                    "allowed_decision_classes": [],
                    "required_evidence_terms": [],
                    "expected_should_take_action_now": False,
                    "expected_requires_human_escalation": False,
                },
            )
            oracle["private_row_count"] += 1
            oracle["private_source_hashes"].append(source_hash)
            expected_path = row.get("expected_path")
            oracle["private_expected_path_item_count"] += len(expected_path) if isinstance(expected_path, list) else 1
            oracle["allowed_decision_classes"] = sorted(set(oracle["allowed_decision_classes"]) | set(flags["allowed_decision_classes"]))
            oracle["required_evidence_terms"] = sorted(set(oracle["required_evidence_terms"]) | set(terms))[:24]
            oracle["expected_should_take_action_now"] = bool(oracle["expected_should_take_action_now"] or flags["expected_should_take_action_now"])
            oracle["expected_requires_human_escalation"] = bool(oracle["expected_requires_human_escalation"] or flags["expected_requires_human_escalation"])

    locked_hits = sorted(set(oracles) & locked_groups)
    if locked_hits:
        raise AssertionError(f"private oracle adapter produced LOCKED_TEST groups: {locked_hits}")
    return oracles


def run(args: argparse.Namespace) -> dict[str, Any]:
    e9_v2.adapt_expected_paths = adapt_expected_paths_case_safe
    summary = e9_v2.run(args)
    summary["report_version"] = "e9-evaluator-side-task-quality-scorer-summary-v3"
    summary["adapter_fix"] = "case_insensitive_asset_id_mapping_preserving_fixed_output_group_ids"
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("research/experiments/e9-evaluator-side-task-quality-scorer-manifest.json"))
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--oracle-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--include-rows", action="store_true")
    args = parser.parse_args()
    summary = run(args)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "fixed_calls_consumed": summary["inputs"]["fixed_calls_consumed"],
                "parsed_model_outputs_available": summary["inputs"]["parsed_model_outputs_available"],
                "private_oracles_loaded": summary["inputs"]["private_oracles_loaded"],
                "calls_with_matching_private_oracle": summary["inputs"]["calls_with_matching_private_oracle"],
                "scoreable_calls": summary["aggregate_metrics"]["scoreable_calls"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
