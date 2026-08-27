#!/usr/bin/env python3
from __future__ import annotations

"""Deterministically derive the P12-C1 exact-ticket scorer from the frozen base.

This is evaluator-only plumbing. It changes oracle row selection from the
historical v4.1 asset-mention+ticket adapter to exact unique public ticket_id
selection. v4.1 normalization, score_call, metrics, gates and candidate outputs
remain unchanged. Zero/multiple exact matches fail closed; no group-union or
fuzzy fallback is introduced.
"""

import argparse
import hashlib
from pathlib import Path

BASE_SHA256 = "4ffc93ff73acad5c96cc099205390f544b6e6cff712f44c8431db83306bc7a73"
DERIVED_SHA256 = "e12d603edd14b00edd76b65fdbe54b0f0534b3478a9c94c192a82b67080fd233"

HELPER = '''def exact_unique_ticket_oracle(payload: Any, ticket_id: str) -> dict[str, Any]:\n    """Resolve one private oracle row by exact public ticket_id only.\n\n    P12-C1 scores every activated ticket, while historical v4.1's adapter also\n    required an asset identifier to be embedded in the private row. That\n    redundant precondition is not part of candidate supervision here. No\n    group-union or fuzzy fallback is permitted: zero/multiple exact matches\n    fail closed, and normalization remains the pinned v4.1 implementation.\n    """\n    matches = [\n        row for row in v4.expected_path_rows(payload)\n        if isinstance(row, dict) and row.get("ticket_id") == ticket_id\n    ]\n    if len(matches) != 1:\n        raise AssertionError(\n            f"exact ticket oracle alignment requires one row for {ticket_id}; got {len(matches)}"\n        )\n    oracle = v4._normalize_expected_row(matches[0])\n    if oracle.get("alignment_status") != v4.ALIGNMENT_UNIQUE:\n        raise AssertionError(f"exact ticket oracle normalization failed for {ticket_id}")\n    if int(oracle.get("unrecognized_expected_steps") or 0) != 0:\n        raise AssertionError(f"expected-step normalization incomplete for {ticket_id}")\n    return oracle\n\n\n'''

OLD = '''        # Exact selected-ticket adaptation. No group-union fallback is introduced.\n        oracles = v4.adapt_expected_paths(\n            oracle_payload,\n            {group},\n            split_manifest,\n            {group: ticket},\n        )\n        oracle = oracles.get(group)\n        score = v41.score_call({"group_id": group, "parsed_output": call.get("parsed_output")}, oracle)\n'''

NEW = '''        # Exact public-ticket adaptation for the full P12-C1 12-ticket corpus.\n        # Group consistency is enforced against the frozen activation mapping\n        # above; private oracle selection itself is exact ticket_id only.\n        oracle = exact_unique_ticket_oracle(oracle_payload, ticket)\n        score = v41.score_call({"group_id": group, "parsed_output": call.get("parsed_output")}, oracle)\n'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive(text: str) -> str:
    if sha256(text.encode()) != BASE_SHA256:
        raise AssertionError("base scorer hash changed")
    anchor = "def run(args: argparse.Namespace) -> int:\n"
    if text.count(anchor) != 1 or text.count(OLD) != 1:
        raise AssertionError("frozen patch anchors changed")
    out = text.replace(anchor, HELPER + anchor).replace(OLD, NEW)
    if sha256(out.encode()) != DERIVED_SHA256:
        raise AssertionError("derived scorer hash mismatch")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = derive(args.base.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(out, encoding="utf-8")
    print(DERIVED_SHA256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
