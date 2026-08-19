#!/usr/bin/env python3
"""Locate an existing historical E14l real capture without exposing its contents.

This is a local operator utility only. It makes no provider calls, reads no
oracle/scorer files intentionally, and prints only file path plus sanitized
capture metadata needed to recover the already-consumed historical artifact.
It never prints prompts, model outputs, group IDs, ticket IDs, hashes, or
per-call rows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_STATUS_PREFIX = "E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_"
EXPECTED_REPORT_VERSION = "e14l-dev-only-120b-medium-reasoning-strict-4096-v1"
MAX_FILE_BYTES = 25 * 1024 * 1024


def _safe_meta(path: Path) -> dict[str, Any] | None:
    try:
        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None

    status = str(payload.get("status") or "")
    report_version = str(payload.get("report_version") or "")
    if not (status.startswith(EXPECTED_STATUS_PREFIX) or report_version == EXPECTED_REPORT_VERSION):
        return None

    aggregate = payload.get("aggregate_metrics")
    aggregate = aggregate if isinstance(aggregate, dict) else {}
    scope = payload.get("scope")
    scope = scope if isinstance(scope, dict) else {}
    return {
        "path": str(path.resolve()),
        "status": status or None,
        "report_version": report_version or None,
        "dry_run": payload.get("dry_run") is True,
        "total_calls": aggregate.get("total_calls"),
        "parsed_model_outputs_available": aggregate.get("parsed_model_outputs_available"),
        "scoreable_calls": aggregate.get("scoreable_calls"),
        "validation_ran": scope.get("validation_ran"),
        "locked_test_accessed": scope.get("locked_test_accessed"),
    }


def run(roots: list[Path]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    seen: set[Path] = set()
    scanned_json_files = 0

    for raw_root in roots:
        try:
            root = raw_root.expanduser().resolve()
        except Exception:
            continue
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else root.rglob("*.json")
        for path in candidates:
            try:
                resolved = path.resolve()
            except Exception:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            scanned_json_files += 1
            meta = _safe_meta(resolved)
            if meta is not None:
                matches.append(meta)

    real_complete = [
        item
        for item in matches
        if item.get("dry_run") is False
        and item.get("status") == "E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS"
        and item.get("total_calls") == 6
        and item.get("parsed_model_outputs_available") == 6
    ]
    if len(real_complete) == 1:
        recommendation = "USE_UNIQUE_REAL_COMPLETE_MATCH_AS_HISTORICAL_E14L_CAPTURE"
    elif len(real_complete) > 1:
        recommendation = "MULTIPLE_REAL_COMPLETE_MATCHES_FOUND_REVIEW_SANITIZED_METADATA_ONLY"
    elif matches:
        recommendation = "ONLY_NONCOMPLETE_OR_DRYRUN_E14L_MATCHES_FOUND_DO_NOT_RETROSCORE"
    else:
        recommendation = "NO_E14L_CAPTURE_FOUND_DO_NOT_RERUN_HISTORICAL_EXPERIMENT"

    return {
        "status": "E14L_HISTORICAL_CAPTURE_LOCATOR",
        "roots_requested": len(roots),
        "scanned_json_files": scanned_json_files,
        "matching_e14l_files": len(matches),
        "real_complete_e14l_matches": len(real_complete),
        "matches": matches,
        "recommended_action": recommendation,
        "provider_call_made": False,
        "prints_model_outputs": False,
        "prints_prompts": False,
        "prints_group_ids": False,
        "prints_ticket_ids": False,
        "prints_hashes": False,
        "prints_private_oracle_values": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, action="append", required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
