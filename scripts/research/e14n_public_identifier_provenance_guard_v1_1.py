#!/usr/bin/env python3
"""E14n v1.1 deterministic identifier-provenance guard.

Bugfix-only successor to E14n v1. Existing {...} public placeholders are
preserved byte-for-byte and concrete-ID matching is applied only outside brace
placeholders. No provider calls, private oracle, VALIDATION, or LOCKED_TEST.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
PARENT_PATH = HERE / "e14n_public_identifier_provenance_guard.py"
SPEC = importlib.util.spec_from_file_location("e14n_v1_parent", PARENT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14n v1 parent guard")
parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parent)


def _sanitize_text_v1_1(text: str, visible_blob: str) -> tuple[str, int, int]:
    """Sanitize concrete IDs outside {...} placeholders only.

    Distinct unsupported mentions are deduplicated across the full text item,
    matching the surface auditor's per-text set semantics. Raw replacement
    occurrences remain separately counted.
    """
    unsupported_tokens: set[str] = set()
    replacement_occurrences = 0

    def sanitize_segment(segment: str) -> str:
        nonlocal replacement_occurrences

        def replace(match: re.Match[str]) -> str:
            nonlocal replacement_occurrences
            token = match.group(0)
            lowered = token.lower()
            if lowered in visible_blob:
                return token
            unsupported_tokens.add(lowered)
            replacement_occurrences += 1
            return parent._placeholder_for(token)

        result = parent.ground.NAMESPACED_ID_RE.sub(replace, segment)
        return parent.ground.UUID_RE.sub(replace, result)

    chunks: list[str] = []
    cursor = 0
    for match in parent.ground.PLACEHOLDER_RE.finditer(text):
        chunks.append(sanitize_segment(text[cursor:match.start()]))
        chunks.append(match.group(0))
        cursor = match.end()
    chunks.append(sanitize_segment(text[cursor:]))
    return "".join(chunks), len(unsupported_tokens), replacement_occurrences


def run(args: argparse.Namespace) -> dict[str, Any]:
    original = parent._sanitize_text
    parent._sanitize_text = _sanitize_text_v1_1
    try:
        summary = parent.run(args)
    finally:
        parent._sanitize_text = original

    transformed = json.loads(args.out.read_text(encoding="utf-8"))
    transformed["report_version"] = "e14n-public-identifier-provenance-guard-v1.1"
    meta = transformed.get("e14n_identifier_provenance_guard")
    if not isinstance(meta, dict):
        raise AssertionError("E14n guard metadata missing")
    meta["guard_version"] = "v1.1-placeholder-preservation"
    meta["brace_placeholders_preserved_byte_for_byte"] = True
    meta["matching_applied_only_outside_brace_placeholders"] = True
    meta["bugfix_change_only"] = True
    args.out.write_text(json.dumps(transformed, indent=2), encoding="utf-8")

    return {
        **summary,
        "report_version": transformed["report_version"],
        "guard_version": meta["guard_version"],
        "brace_placeholders_preserved_byte_for_byte": True,
        "matching_applied_only_outside_brace_placeholders": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument(
        "--split-manifest",
        type=Path,
        default=Path("research/frozen/benchmark-split-v1.json"),
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "E14N_PUBLIC_IDENTIFIER_PROVENANCE_GUARD_TRANSFORM_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
