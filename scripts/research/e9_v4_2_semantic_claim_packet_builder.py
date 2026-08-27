#!/usr/bin/env python3
"""Build local public-only semantic-groundedness claim packets for E9 v4.2.

The packet builder is deterministic and does not judge claims. It pairs free-text
claim units from a fixed DEV output with the exact runner-selected visible case
and public-contract metadata. The resulting packet may contain raw model text and
visible case values and therefore MUST remain local/uncommitted.

Console output is aggregate-only and never prints claim text, case values,
identifiers, group IDs, hashes, or private paths.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
GROUND_PATH = HERE / "e9_v4_1_groundedness_surface_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_ground_parent", GROUND_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load groundedness surface diagnostic")
ground = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ground)
v41 = ground.v41
v4 = ground.v4

SOURCE_FIELDS = (
    "evidence_plan[]",
    "proposed_next_step",
    "risk_notes",
    "action_escalation_rubric.calibration_reason",
)

# Split on terminal punctuation, semicolons, or explicit line breaks while
# avoiding destructive tokenization of API paths/placeholders.
CLAUSE_SPLIT_RE = re.compile(r"(?:\r?\n)+|(?<=[.!?;])\s+")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def segment_claim_units(text: str) -> list[str]:
    normalized = _normalize_space(text)
    if not normalized:
        return []
    parts = [_normalize_space(part) for part in CLAUSE_SPLIT_RE.split(normalized)]
    return [part for part in parts if part]


def _source_texts(output: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    plan = output.get("evidence_plan")
    if isinstance(plan, list):
        for item in plan:
            if isinstance(item, str):
                rows.append(("evidence_plan[]", item))

    for key in ("proposed_next_step", "risk_notes"):
        value = output.get(key)
        if isinstance(value, str):
            rows.append((key, value))

    rubric = output.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        value = rubric.get("calibration_reason")
        if isinstance(value, str):
            rows.append(("action_escalation_rubric.calibration_reason", value))
    return rows


def build_claim_units(output: dict[str, Any]) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    index = 0
    for field, text in _source_texts(output):
        for claim in segment_claim_units(text):
            units.append({
                "claim_index": index,
                "source_field": field,
                "claim_text": claim,
            })
            index += 1
    return units


def _selected_case_by_group(cases_payload: Any, fixed_groups: set[str]) -> dict[str, dict[str, Any]]:
    return ground._selected_case_by_group(cases_payload, fixed_groups)


def run(args: argparse.Namespace) -> dict[str, Any]:
    fixed = _load(args.fixed_output_file)
    cases_payload = _load(args.agent_input_cases)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be JSON objects")

    calls = v4.collect_calls(fixed)
    v4.assert_fixed_scope(fixed, calls, split_manifest)
    fixed_groups = {str(call.get("group_id")) for call in calls if call.get("group_id")}
    selected = _selected_case_by_group(cases_payload, fixed_groups)

    packet_calls: list[dict[str, Any]] = []
    parsed_outputs = 0
    calls_with_visible_case = 0
    source_field_counts: Counter[str] = Counter()
    claim_units_total = 0
    calls_with_zero_claim_units = 0

    tool_signatures = [str(spec["signature"]) for spec in v41.PUBLIC_TOOL_SPECS]

    for call_index, call in enumerate(calls):
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        parsed_outputs += 1
        group = str(call.get("group_id") or "")
        visible_case = selected.get(group)
        if not isinstance(visible_case, dict):
            continue
        calls_with_visible_case += 1

        units = build_claim_units(output)
        calls_with_zero_claim_units += int(not units)
        claim_units_total += len(units)
        for unit in units:
            source_field_counts[str(unit["source_field"])] += 1

        packet_calls.append({
            "call_index": call_index,
            "split": str(call.get("split") or "DEV"),
            "visible_case": visible_case,
            "public_contract": {
                "tool_signatures": tool_signatures,
                "claim_support_labels": ["SUPPORTED", "CONTRADICTED", "NOT_SUPPORTED", "NOT_APPLICABLE"],
                "claim_types": [
                    "factual_assertion",
                    "conditional_or_hypothetical",
                    "procedural_recommendation",
                    "uncertainty_or_epistemic_statement",
                    "non_world_metadata"
                ]
            },
            "claim_units": units,
        })

    complete = (
        bool(calls)
        and parsed_outputs == len(calls)
        and calls_with_visible_case == len(calls)
        and len(selected) == len(fixed_groups)
        and calls_with_zero_claim_units == 0
    )

    packet = {
        "report_version": "e9-v4.2-semantic-claim-packet-v1",
        "scope": {
            "split": "DEV",
            "private_oracle_included": False,
            "private_scorer_rows_included": False,
            "validation_material_included": False,
            "locked_test_material_included": False,
            "runner_selection_rule": "first_agent_input_case_per_asset",
        },
        "calls": packet_calls,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    status = (
        "E9_V4_2_SEMANTIC_CLAIM_PACKET_BUILD_PASS"
        if complete
        else "E9_V4_2_SEMANTIC_CLAIM_PACKET_BUILD_NEEDS_REVIEW"
    )
    return {
        "status": status,
        "fixed_calls_consumed": len(calls),
        "parsed_model_outputs_available": parsed_outputs,
        "fixed_groups_found": len(fixed_groups),
        "runner_selected_visible_cases_for_fixed_groups": len(selected),
        "calls_with_visible_case": calls_with_visible_case,
        "claim_units_total": claim_units_total,
        "calls_with_zero_claim_units": calls_with_zero_claim_units,
        "source_field_claim_unit_counts": dict(sorted(source_field_counts.items())),
        "complete_claim_packet_coverage": complete,
        "judge_called": False,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "prints_claim_text": False,
        "prints_visible_case_values": False,
        "prints_identifiers": False,
        "prints_group_ids": False,
        "prints_hashes": False,
        "prints_private_paths": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "E9_V4_2_SEMANTIC_CLAIM_PACKET_BUILD_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
