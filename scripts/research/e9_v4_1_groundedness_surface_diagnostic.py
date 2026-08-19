#!/usr/bin/env python3
"""Public-only, one-sided concrete-claim groundedness surface diagnostic.

This diagnostic does NOT claim to measure general semantic groundedness. It can
only surface concrete provenance problems in fixed DEV outputs using the exact
runner-selected visible case and the public tool registry. It never reads the
private oracle or scorer rows and never prints raw claims, identifiers, values,
group labels, hashes, or per-call results.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).parent
V41_PATH = HERE / "e9_evaluator_side_scorer_v4_1.py"
SPEC = importlib.util.spec_from_file_location("e9_v41_grounding_parent", V41_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E9 v4.1 evaluator")
v41 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v41)
v4 = v41.v4

PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")
NAMESPACED_ID_RE = re.compile(
    r"\b(?:asset|analysis|model|case|ticket)[-_][A-Za-z0-9][A-Za-z0-9._:-]*\b",
    re.IGNORECASE,
)
UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_.])-?\d+(?:\.\d+)?")
UNIT_NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_.])(-?\d+(?:\.\d+)?)\s*(kHz|Hz|rpm|mm/s|m/s|dB|°C|C|g|%)(?=$|[\s,.;:)\]])",
    re.IGNORECASE,
)
UNIT_CANON = {
    "khz": "khz",
    "hz": "hz",
    "rpm": "rpm",
    "mm/s": "mm/s",
    "m/s": "m/s",
    "db": "db",
    "°c": "c",
    "c": "c",
    "g": "g",
    "%": "%",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _string_values(child)


def _selected_case_by_group(cases_payload: Any, fixed_groups: set[str]) -> dict[str, dict[str, Any]]:
    canonical = {group.lower(): group for group in fixed_groups}
    selected: dict[str, dict[str, Any]] = {}
    for record in v4._collect_case_records(cases_payload):
        asset = v4._asset_id(record)
        if not asset or asset.lower() not in canonical:
            continue
        group = canonical[asset.lower()]
        if group not in selected:
            selected[group] = record
    return selected


def _output_free_text(output: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    plan = output.get("evidence_plan")
    if isinstance(plan, list):
        texts.extend(str(item) for item in plan if isinstance(item, str))
    for key in ("proposed_next_step", "risk_notes"):
        value = output.get(key)
        if isinstance(value, str):
            texts.append(value)
    rubric = output.get("action_escalation_rubric")
    if isinstance(rubric, dict):
        for key in ("calibration_reason", "action_endpoint"):
            value = rubric.get(key)
            if isinstance(value, str):
                texts.append(value)
    return texts


def _case_visible_blob(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True).lower()


def _visible_numbers(record: dict[str, Any]) -> set[float]:
    values: set[float] = set()

    def walk(value: Any) -> None:
        if isinstance(value, bool) or value is None:
            return
        if isinstance(value, (int, float)):
            if math.isfinite(float(value)):
                values.add(float(value))
            return
        if isinstance(value, str):
            for match in NUMBER_RE.finditer(value):
                try:
                    values.add(float(match.group(0)))
                except ValueError:
                    pass
            return
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(record)
    return values


def _unit_visible(record: dict[str, Any], unit: str) -> bool:
    canonical = UNIT_CANON[unit.lower()]
    strings = "\n".join(_string_values(record)).lower()
    if canonical == "c":
        return bool(re.search(r"(?:°c|\bcelsius\b|\btemperature\b|\btemp\b)", strings))
    if canonical == "%":
        return "%" in strings or "percent" in strings or "percentage" in strings
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(canonical)}(?![a-z0-9])", strings))


def _numeric_supported(number: float, unit: str, visible_numbers: set[float]) -> bool:
    def close(a: float, b: float) -> bool:
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)

    if any(close(number, visible) for visible in visible_numbers):
        return True
    if UNIT_CANON[unit.lower()] == "%" and any(close(number / 100.0, visible) for visible in visible_numbers):
        return True
    return False


def _id_mentions(text: str) -> set[str]:
    scrubbed = PLACEHOLDER_RE.sub("", text)
    found = {match.group(0).lower() for match in NAMESPACED_ID_RE.finditer(scrubbed)}
    found.update(match.group(0).lower() for match in UUID_RE.finditer(scrubbed))
    return found


def _endpoint_pair_counts(text: str) -> tuple[int, int]:
    total = 0
    unsupported = 0
    for method, path in v41._method_path_pairs(text):
        total += 1
        if not v41.canonical_tool_signatures(f"{method} {path}", require_method=True):
            unsupported += 1
    return total, unsupported


def audit_output(output: dict[str, Any], visible_case: dict[str, Any]) -> dict[str, int | bool]:
    visible_blob = _case_visible_blob(visible_case)
    numbers = _visible_numbers(visible_case)
    id_mentions = 0
    unsupported_ids = 0
    endpoint_mentions = 0
    unsupported_endpoints = 0
    unit_numeric_mentions = 0
    unsupported_unit_numeric = 0

    for text in _output_free_text(output):
        ids = _id_mentions(text)
        id_mentions += len(ids)
        unsupported_ids += sum(1 for token in ids if token not in visible_blob)

        endpoint_total, endpoint_bad = _endpoint_pair_counts(text)
        endpoint_mentions += endpoint_total
        unsupported_endpoints += endpoint_bad

        scrubbed = PLACEHOLDER_RE.sub("", text)
        for match in UNIT_NUMBER_RE.finditer(scrubbed):
            unit_numeric_mentions += 1
            number = float(match.group(1))
            unit = match.group(2)
            if not _numeric_supported(number, unit, numbers) or not _unit_visible(visible_case, unit):
                unsupported_unit_numeric += 1

    trace = output.get("trace_quality_self_check")
    trace = trace if isinstance(trace, dict) else {}
    false_trace_flags = sum(
        1
        for key in ("uses_only_visible_packet", "no_locked_test", "no_gold_claim")
        if trace.get(key) is False
    )

    has_violation = any((unsupported_ids, unsupported_endpoints, unsupported_unit_numeric, false_trace_flags))
    return {
        "id_mentions": id_mentions,
        "unsupported_id_mentions": unsupported_ids,
        "public_endpoint_mentions": endpoint_mentions,
        "unrecognized_method_path_mentions": unsupported_endpoints,
        "unit_numeric_mentions": unit_numeric_mentions,
        "unsupported_unit_numeric_mentions": unsupported_unit_numeric,
        "false_trace_self_check_flags": false_trace_flags,
        "has_concrete_provenance_violation": has_violation,
    }


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

    parsed_outputs = 0
    assessed_calls = 0
    calls_with_violation = 0
    totals = {
        "id_mentions": 0,
        "unsupported_id_mentions": 0,
        "public_endpoint_mentions": 0,
        "unrecognized_method_path_mentions": 0,
        "unit_numeric_mentions": 0,
        "unsupported_unit_numeric_mentions": 0,
        "false_trace_self_check_flags": 0,
    }

    for call in calls:
        output = v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        parsed_outputs += 1
        group = str(call.get("group_id") or "")
        visible_case = selected.get(group)
        if not isinstance(visible_case, dict):
            continue
        assessed_calls += 1
        row = audit_output(output, visible_case)
        calls_with_violation += int(row["has_concrete_provenance_violation"] is True)
        for key in totals:
            totals[key] += int(row[key])

    complete_surface_coverage = (
        bool(calls)
        and parsed_outputs == len(calls)
        and assessed_calls == len(calls)
        and len(selected) == len(fixed_groups)
    )
    status = (
        "E9_V4_1_GROUNDEDNESS_SURFACE_AUDIT_COMPLETE"
        if complete_surface_coverage
        else "E9_V4_1_GROUNDEDNESS_SURFACE_AUDIT_NEEDS_REVIEW"
    )
    violations = sum(
        totals[key]
        for key in (
            "unsupported_id_mentions",
            "unrecognized_method_path_mentions",
            "unsupported_unit_numeric_mentions",
            "false_trace_self_check_flags",
        )
    )
    interpretation = (
        "CONCRETE_PROVENANCE_VIOLATIONS_FOUND_GENERAL_GROUNDEDNESS_BLOCKED"
        if violations
        else "NO_CONCRETE_PROVENANCE_VIOLATIONS_FOUND_GENERAL_GROUNDEDNESS_STILL_UNMEASURED"
    )

    return {
        "report_version": "e9-v4.1-public-groundedness-surface-v1",
        "status": status,
        "fixed_calls_consumed": len(calls),
        "parsed_model_outputs_available": parsed_outputs,
        "fixed_groups_found": len(fixed_groups),
        "runner_selected_visible_cases_for_fixed_groups": len(selected),
        "assessed_calls": assessed_calls,
        "complete_surface_coverage": complete_surface_coverage,
        "calls_with_any_concrete_provenance_violation": calls_with_violation,
        **totals,
        "concrete_provenance_violation_count": violations,
        "interpretation": interpretation,
        "general_free_text_groundedness": "UNRESOLVED_BY_ONE_SIDED_SURFACE_AUDIT",
        "one_sided_only": True,
        "can_authorize_validation": False,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "prints_raw_model_outputs": False,
        "prints_visible_case_values": False,
        "prints_identifiers": False,
        "prints_numeric_claim_values": False,
        "prints_group_ids": False,
        "prints_per_call_results": False,
        "prints_hashes": False,
        "prints_private_paths": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--agent-input-cases", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
