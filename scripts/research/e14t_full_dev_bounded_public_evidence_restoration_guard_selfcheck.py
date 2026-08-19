#!/usr/bin/env python3
"""Public synthetic self-checks for E14t bounded evidence restoration."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14t_full_dev_bounded_public_evidence_restoration_guard.py"
SPEC = importlib.util.spec_from_file_location("e14t_for_selfcheck", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14t guard")
e14t = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14t)


def main() -> int:
    assert e14t.EXPECTED_CALLS == 10
    assert e14t.EXPECTED_GROUPS == 5
    assert e14t.EXPECTED_E14S_BASE_READS_TOTAL == 59
    assert e14t.MAX_ADDITIONAL_READS_TOTAL == 4
    assert e14t.MAX_ADDITIONAL_READS_PER_CALL == 1
    assert e14t.MAX_FINAL_READS_PER_CALL == 7
    assert e14t.MAX_FINAL_READS_TOTAL == 63

    original = ["GET /a", "GET /b", "GET /c"]
    selected = ["GET /a", "GET /c"]
    assert e14t._first_omitted_original(original, selected) == "GET /b"
    assert e14t._first_omitted_original(original, original) is None

    entries = [
        {
            "stable_index": 0,
            "original_candidate_count": 6,
            "candidate_pool_count": 8,
            "restoration_candidate": "GET /r0",
            "base_selected": ["GET /x"] * 6,
        },
        {
            "stable_index": 1,
            "original_candidate_count": 8,
            "candidate_pool_count": 8,
            "restoration_candidate": "GET /r1",
            "base_selected": ["GET /x"] * 6,
        },
        {
            "stable_index": 2,
            "original_candidate_count": 8,
            "candidate_pool_count": 9,
            "restoration_candidate": "GET /r2",
            "base_selected": ["GET /x"] * 6,
        },
        {
            "stable_index": 3,
            "original_candidate_count": 7,
            "candidate_pool_count": 9,
            "restoration_candidate": "GET /r3",
            "base_selected": ["GET /x"] * 6,
        },
        {
            "stable_index": 4,
            "original_candidate_count": 5,
            "candidate_pool_count": 7,
            "restoration_candidate": "GET /r4",
            "base_selected": ["GET /x"] * 6,
        },
        {
            "stable_index": 5,
            "original_candidate_count": 99,
            "candidate_pool_count": 99,
            "restoration_candidate": None,
            "base_selected": ["GET /x"] * 6,
        },
    ]

    chosen = e14t._select_restoration_indices(entries)
    assert chosen == {0, 1, 2, 3}
    assert len(chosen) == e14t.MAX_ADDITIONAL_READS_TOTAL

    tied = [
        {
            "stable_index": 2,
            "original_candidate_count": 6,
            "candidate_pool_count": 7,
            "restoration_candidate": "GET /r2",
            "base_selected": ["GET /x"] * 6,
        },
        {
            "stable_index": 1,
            "original_candidate_count": 6,
            "candidate_pool_count": 7,
            "restoration_candidate": "GET /r1",
            "base_selected": ["GET /x"] * 6,
        },
    ]
    tied_chosen = e14t._select_restoration_indices(tied)
    assert tied_chosen == {1, 2}

    already_at_hard_cap = [
        {
            "stable_index": 0,
            "original_candidate_count": 9,
            "candidate_pool_count": 9,
            "restoration_candidate": "GET /r0",
            "base_selected": [f"GET /x{i}" for i in range(7)],
        }
    ]
    assert e14t._select_restoration_indices(already_at_hard_cap) == set()

    print("E14T_PUBLIC_SYNTHETIC_SELFCHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
