#!/usr/bin/env python3
"""Classify an existing E14m-R1 capture file without exposing model outputs.

This diagnostic makes no provider call, does not read private oracle files, and
prints no prompts, output text, group ids, hashes, API keys, or local paths.
It exists only to decide whether an occupied R1 output path is a harmless dry-run
artifact, a real R1 capture that must not be rerun, or an unrelated/stale file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _collect_calls(payload: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "calls" and isinstance(value, list):
                calls.extend(item for item in value if isinstance(item, dict))
            elif isinstance(value, (dict, list)):
                calls.extend(_collect_calls(value))
    elif isinstance(payload, list):
        for item in payload:
            calls.extend(_collect_calls(item))
    return calls


def _provider_usage_present(call: dict[str, Any]) -> bool:
    meta = call.get("provider_meta")
    if not isinstance(meta, dict):
        return False
    usage = meta.get("usage")
    if isinstance(usage, dict) and any(value not in (None, 0, "", {}) for value in usage.values()):
        return True
    return bool(meta.get("inference_call_made") is True)


def run(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "status": "E14M_R1_EXISTING_CAPTURE_DIAGNOSTIC",
            "capture_file_exists": False,
            "classification": "PATH_AVAILABLE_NO_EXISTING_CAPTURE",
            "safe_to_reuse_same_path_without_deleting": True,
            "provider_call_made_by_diagnostic": False,
            "prints_raw_model_outputs": False,
            "prints_private_paths": False,
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "status": "E14M_R1_EXISTING_CAPTURE_DIAGNOSTIC",
            "capture_file_exists": True,
            "json_valid": False,
            "classification": "EXISTING_FILE_NOT_VALID_CAPTURE_JSON",
            "safe_to_reuse_same_path_without_deleting": False,
            "provider_call_made_by_diagnostic": False,
            "prints_raw_model_outputs": False,
            "prints_private_paths": False,
        }

    if not isinstance(payload, dict):
        return {
            "status": "E14M_R1_EXISTING_CAPTURE_DIAGNOSTIC",
            "capture_file_exists": True,
            "json_valid": True,
            "top_level_object": False,
            "classification": "EXISTING_JSON_NOT_CAPTURE_OBJECT",
            "safe_to_reuse_same_path_without_deleting": False,
            "provider_call_made_by_diagnostic": False,
            "prints_raw_model_outputs": False,
            "prints_private_paths": False,
        }

    replacement = payload.get("e14m_r1_operational_replacement")
    replacement = replacement if isinstance(replacement, dict) else {}
    aggregate = payload.get("aggregate_metrics")
    aggregate = aggregate if isinstance(aggregate, dict) else {}
    scope = payload.get("scope")
    scope = scope if isinstance(scope, dict) else {}
    calls = _collect_calls(payload)

    dry_run = payload.get("dry_run") is True
    status = str(payload.get("status") or "")
    is_r1 = (
        replacement.get("amendment_id") == "E14m-R1"
        or str(payload.get("report_version") or "").startswith("e14m-r1-operational-replacement")
        or status.startswith("E14M_R1_OPERATIONAL_REPLACEMENT")
    )
    provider_usage_calls = sum(1 for call in calls if _provider_usage_present(call))

    if is_r1 and dry_run:
        classification = "R1_DRY_RUN_ARTIFACT_EXISTS"
        action = "USE_A_DIFFERENT_FRESH_PATH_OR_REMOVE_ONLY_IF_OPERATOR_CONFIRMS_THIS_IS_DRY_RUN"
    elif is_r1 and not dry_run:
        classification = "REAL_R1_CAPTURE_ALREADY_EXISTS_DO_NOT_RUN_R1_AGAIN"
        action = "STOP_AND_INSPECT_SANITIZED_CAPTURE_STATUS_ONLY"
    elif status.startswith("E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION"):
        classification = "PARENT_E14M_CAPTURE_OCCUPIES_R1_PATH"
        action = "USE_A_FRESH_R1_PATH;DO_NOT_OVERWRITE_PARENT_CAPTURE"
    else:
        classification = "UNRELATED_OR_STALE_FILE_OCCUPIES_R1_PATH"
        action = "USE_A_FRESH_UNIQUE_R1_PATH_UNLESS_OPERATOR_IDENTIFIES_FILE_PROVENANCE"

    return {
        "status": "E14M_R1_EXISTING_CAPTURE_DIAGNOSTIC",
        "capture_file_exists": True,
        "json_valid": True,
        "top_level_object": True,
        "classification": classification,
        "recommended_action": action,
        "capture_status": status or None,
        "report_version": payload.get("report_version"),
        "dry_run": dry_run,
        "is_e14m_r1": is_r1,
        "replacement_amendment_id": replacement.get("amendment_id"),
        "replacement_capture_index": replacement.get("replacement_capture_index"),
        "replacement_captures_allowed": replacement.get("replacement_captures_allowed"),
        "same_candidate": replacement.get("same_candidate"),
        "total_calls": aggregate.get("total_calls"),
        "parsed_model_outputs_available": aggregate.get("parsed_model_outputs_available"),
        "scoreable_calls": aggregate.get("scoreable_calls"),
        "validation_ran": scope.get("validation_ran"),
        "locked_test_accessed": scope.get("locked_test_accessed"),
        "provider_usage_metadata_present_calls": provider_usage_calls,
        "safe_to_reuse_same_path_without_deleting": False,
        "provider_call_made_by_diagnostic": False,
        "reads_private_oracle": False,
        "prints_raw_model_outputs": False,
        "prints_prompts": False,
        "prints_group_ids": False,
        "prints_hashes": False,
        "prints_private_paths": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.capture), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
