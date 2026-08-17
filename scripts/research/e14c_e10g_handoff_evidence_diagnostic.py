#!/usr/bin/env python3
"""Sanitized E14c diagnostic for E10g human-handoff evidence blocking.

Reads an already-fixed private DEV capture and reports only aggregate counts for
calls whose embedded E10g reason is
`balanced_guard_handoff_without_minimum_visible_evidence`.

It does not read private oracle data and never prints parsed outputs, group IDs,
resource identifiers, hashes, prompts, private paths, scorer rows, or evaluator
labels. The evidence-plan fields inspected here are model-visible/public-contract
material already preserved by E10g.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

PUBLIC_EVIDENCE_MARKERS = (
    "get /users/me",
    "get /assets/{asset_id}",
    "get /assets/{asset_id}/analyses",
    "get /analyses/{analysis_id}",
    "get /assets/{asset_id}/baseline",
    "get /assets/{asset_id}/data-quality",
    "get /assets/{asset_id}/rms",
    "get /assets/{asset_id}/spectrum",
    "get /knowledge/search",
    "get /knowledge/{doc_id}",
)

TARGET_REASON = "balanced_guard_handoff_without_minimum_visible_evidence"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def public_marker_count(output: dict[str, Any]) -> int:
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return 0
    text = "\n".join(str(item) for item in plan).lower()
    return sum(1 for marker in PUBLIC_EVIDENCE_MARKERS if marker in text)


def plan_length(output: dict[str, Any]) -> int:
    plan = output.get("evidence_plan")
    return len(plan) if isinstance(plan, list) else 0


def number_summary(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    payload = load_json(args.capture)
    if not isinstance(payload, dict):
        raise AssertionError("capture must be a JSON object")
    stage = payload.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []

    marker_histogram: Counter[int] = Counter()
    plan_lengths: list[int] = []
    target_calls = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guard = output.get("visible_balanced_safety_action_guard")
        if not isinstance(guard, dict):
            continue
        if str(guard.get("reason") or "") != TARGET_REASON:
            continue
        target_calls += 1
        marker_histogram[public_marker_count(output)] += 1
        plan_lengths.append(plan_length(output))

    result = {
        "status": "E14C_SANITIZED_E10G_HANDOFF_EVIDENCE_DIAGNOSTIC",
        "total_calls": len(calls),
        "e10g_handoff_without_minimum_visible_evidence_calls": target_calls,
        "blocked_handoff_public_marker_count_histogram": {
            str(key): value for key, value in sorted(marker_histogram.items())
        },
        "blocked_handoff_plan_length": number_summary(plan_lengths),
        "interpretation_contract": {
            "e10g_handoff_threshold": 2,
            "histogram_counts_distinct_public_evidence_markers_only": True,
            "zero_marker_handoff_is_not_automatically_authorized": True,
        },
        "prints_private_outputs": False,
        "prints_group_level_rows": False,
        "prints_hashes": False,
        "prints_prompts": False,
        "prints_private_paths": False,
        "prints_oracle_data": False,
        "prints_evaluator_labels": False,
        "prints_concrete_resource_identifiers": False,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
