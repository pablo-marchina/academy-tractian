#!/usr/bin/env python3
"""Oracle-free synthetic self-check for visible-case/oracle ticket alignment diagnostic."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e9_private_oracle_visible_case_alignment_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("alignment_diag", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load alignment diagnostic")
diag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diag)


def main() -> int:
    split = {
        "splits": {
            "DEV": {"groups": [{"group_id": "asset_A1"}]},
            "VALIDATION": {"groups": [{"group_id": "asset_B1"}]},
            "LOCKED_TEST": {"groups": [{"group_id": "asset_C1"}]},
        }
    }
    cases = [
        {"case_id": "case-1", "ticket_id": "ticket-1", "asset_id": "asset_A1"},
        {"case_id": "case-2", "ticket_id": "ticket-2", "asset_id": "asset_A1"},
        {"case_id": "case-3", "ticket_id": "ticket-3", "asset_id": "asset_B1"},
    ]
    oracle = [
        {
            "id": "row-1",
            "ticket_id": "ticket-1",
            "mode": "investigate",
            "root_question": "synthetic",
            "expected_path": [{"step": "GET /assets/asset_A1", "note": "synthetic"}],
        },
        {
            "id": "row-2",
            "ticket_id": "ticket-2",
            "mode": "execute",
            "root_question": "synthetic",
            "expected_path": [
                {"step": "GET /assets/asset_A1", "note": "synthetic same-asset evidence"},
                {"step": "POST /analyses/a/reprocess", "note": "synthetic action"}
            ],
        },
        {
            "id": "row-3",
            "ticket_id": "ticket-3",
            "mode": "investigate",
            "root_question": "synthetic",
            "expected_path": [{"step": "GET /assets/asset_B1", "note": "synthetic"}],
        },
    ]

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        oracle_path = root / "oracle.json"
        cases_path = root / "cases.json"
        split_path = root / "split.json"
        oracle_path.write_text(json.dumps(oracle), encoding="utf-8")
        cases_path.write_text(json.dumps(cases), encoding="utf-8")
        split_path.write_text(json.dumps(split), encoding="utf-8")
        result = diag.run(oracle_path, cases_path, split_path)

    if result.get("runner_selected_visible_cases") != 2:
        raise AssertionError("expected one selected visible case per asset/group")
    if result.get("frozen_groups_with_multiple_agent_case_records") != 1:
        raise AssertionError("synthetic multi-case asset must be detected")
    counts = result.get("selected_ticket_alignment_status_counts") or {}
    if counts.get("selected_ticket_matches_exactly_one_oracle_row") != 2:
        raise AssertionError("selected first case per asset must align to exactly one oracle row")
    if result.get("groups_where_group_union_contains_oracle_rows_beyond_selected_ticket") != 1:
        raise AssertionError("group-level union confound must be detected")
    if result.get("candidate_specific_output_used") is not False:
        raise AssertionError("diagnostic must remain candidate-output independent")

    print("E9_VISIBLE_CASE_ALIGNMENT_SYNTHETIC_SELF_CHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
