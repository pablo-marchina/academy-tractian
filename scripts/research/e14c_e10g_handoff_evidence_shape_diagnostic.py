#!/usr/bin/env python3
"""Sanitized E14c diagnostic for concrete-vs-template evidence resource shapes.

Reads an already-fixed private DEV capture and inspects only evidence plans from
calls whose embedded E10g reason is
`balanced_guard_handoff_without_minimum_visible_evidence`.

The historical E10e/E10g evidence counter recognizes a fixed set of public GET
resource templates by literal text. This diagnostic asks whether concrete public
paths equivalent to those same templates were present but not counted. It does
not change policy, does not read private oracle data, and never prints parsed
outputs, group IDs, resource identifiers, hashes, prompts, private paths, scorer
rows, or evaluator labels.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
E10E_SOURCE = HERE / "e10e_dev_only_premature_action_guard.py"
TOOL_REGISTRY_SOURCE = REPO_ROOT / "research" / "e2" / "tool_registry.py"
TARGET_REASON = "balanced_guard_handoff_without_minimum_visible_evidence"
_PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _literal_string(node: ast.AST) -> str:
    value = ast.literal_eval(node)
    if not isinstance(value, str):
        raise AssertionError("expected string literal")
    return value


def _e10e_public_evidence_markers() -> tuple[str, ...]:
    tree = ast.parse(E10E_SOURCE.read_text(encoding="utf-8"))
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "CONCRETE_EVIDENCE_MARKERS" for target in statement.targets):
            continue
        value = ast.literal_eval(statement.value)
        if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
            raise AssertionError("CONCRETE_EVIDENCE_MARKERS must be a literal tuple of strings")
        return tuple(str(item).lower() for item in value)
    raise AssertionError("CONCRETE_EVIDENCE_MARKERS not found in E10e source")


def _canonical_path(path_template: str, path_names: list[str]) -> str:
    matches = list(_PLACEHOLDER_RE.finditer(path_template))
    if len(matches) != len(path_names):
        raise AssertionError("public read path placeholder/parameter mismatch")
    names = iter(path_names)
    return _PLACEHOLDER_RE.sub(lambda _m: "{" + next(names) + "}", path_template).lower()


def _concrete_path_pattern(path_template: str) -> str:
    pieces: list[str] = []
    cursor = 0
    for match in _PLACEHOLDER_RE.finditer(path_template):
        pieces.append(re.escape(path_template[cursor:match.start()]))
        pieces.append(r"[^/\s?#,;:)\]\}]+")
        cursor = match.end()
    pieces.append(re.escape(path_template[cursor:]))
    return "".join(pieces)


def _public_read_route_specs() -> dict[str, re.Pattern[str]]:
    """Map canonical GET endpoint -> concrete-path regex from frozen ToolSpec source."""
    tree = ast.parse(TOOL_REGISTRY_SOURCE.read_text(encoding="utf-8"))
    tools_value: ast.AST | None = None
    for statement in tree.body:
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name) and statement.target.id == "TOOLS":
            tools_value = statement.value
            break
    if not isinstance(tools_value, ast.Tuple):
        raise AssertionError("frozen public tool registry TOOLS tuple not found")

    specs: dict[str, re.Pattern[str]] = {}
    for item in tools_value.elts:
        if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Name) or item.func.id != "read":
            continue
        if len(item.args) < 4:
            raise AssertionError("public read declaration missing required literal arguments")
        path_template = _literal_string(item.args[2])
        params_node = item.args[3]
        if not isinstance(params_node, ast.List):
            raise AssertionError("public read parameter declaration must be a literal list")
        path_names: list[str] = []
        for param in params_node.elts:
            if not isinstance(param, ast.Call) or not isinstance(param.func, ast.Name) or param.func.id != "p":
                continue
            if len(param.args) < 2:
                continue
            name = _literal_string(param.args[0])
            location = _literal_string(param.args[1]).lower()
            if location == "path":
                path_names.append(name)
        canonical = f"get {_canonical_path(path_template, path_names)}"
        path_pattern = _concrete_path_pattern(path_template)
        specs[canonical] = re.compile(
            rf"(?<![A-Za-z0-9_])get\s+{path_pattern}(?=$|[\s?#,;:.)\]\}}])",
            flags=re.IGNORECASE,
        )
    return specs


def _plan_text(output: dict[str, Any]) -> str:
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return ""
    return "\n".join(str(item) for item in plan).lower()


def _number_summary(values: list[int]) -> dict[str, int | float | None]:
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

    markers = _e10e_public_evidence_markers()
    route_specs = _public_read_route_specs()
    missing_specs = sorted(marker for marker in markers if marker not in route_specs)
    if missing_specs:
        raise AssertionError(f"E10e public evidence markers missing from frozen ToolSpec source: {len(missing_specs)}")

    payload = load_json(args.capture)
    if not isinstance(payload, dict):
        raise AssertionError("capture must be a JSON object")
    stage = payload.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []

    historical_hist: Counter[int] = Counter()
    canonicalized_hist: Counter[int] = Counter()
    shape_counts: Counter[str] = Counter()
    plan_lengths: list[int] = []
    target_calls = 0
    calls_with_concrete_equivalent = 0
    calls_reaching_threshold_after_shape_normalization = 0
    calls_still_below_threshold_after_shape_normalization = 0

    for call in calls:
        if not isinstance(call, dict):
            continue
        output = call.get("parsed_output")
        if not isinstance(output, dict):
            continue
        guard = output.get("visible_balanced_safety_action_guard")
        if not isinstance(guard, dict) or str(guard.get("reason") or "") != TARGET_REASON:
            continue

        target_calls += 1
        plan = output.get("evidence_plan")
        plan_lengths.append(len(plan) if isinstance(plan, list) else 0)
        text = _plan_text(output)

        historical_families: set[str] = set()
        canonicalized_families: set[str] = set()
        concrete_only_families: set[str] = set()

        for marker in markers:
            canonical_present = marker in text
            concrete_present = bool(route_specs[marker].search(text))
            if canonical_present:
                historical_families.add(marker)
                canonicalized_families.add(marker)
            if concrete_present:
                canonicalized_families.add(marker)
                if not canonical_present:
                    concrete_only_families.add(marker)

        historical_count = len(historical_families)
        normalized_count = len(canonicalized_families)
        historical_hist[historical_count] += 1
        canonicalized_hist[normalized_count] += 1

        if historical_families:
            shape_counts["template_marker_family_present"] += 1
        if concrete_only_families:
            shape_counts["concrete_public_read_equivalent_not_counted_historically"] += 1
            calls_with_concrete_equivalent += 1
        if normalized_count == 0:
            shape_counts["no_recognized_public_evidence_family_after_shape_normalization"] += 1
        if normalized_count >= 2:
            calls_reaching_threshold_after_shape_normalization += 1
        else:
            calls_still_below_threshold_after_shape_normalization += 1

    result = {
        "status": "E14C_SANITIZED_E10G_HANDOFF_EVIDENCE_SHAPE_DIAGNOSTIC",
        "total_calls": len(calls),
        "target_blocked_handoff_calls": target_calls,
        "historical_template_marker_count_histogram": {
            str(key): value for key, value in sorted(historical_hist.items())
        },
        "public_evidence_family_count_after_shape_normalization_histogram": {
            str(key): value for key, value in sorted(canonicalized_hist.items())
        },
        "blocked_handoff_shape_call_counts": dict(sorted(shape_counts.items())),
        "blocked_handoff_calls_with_concrete_public_read_equivalent": calls_with_concrete_equivalent,
        "blocked_handoff_calls_reaching_existing_threshold_after_shape_normalization": calls_reaching_threshold_after_shape_normalization,
        "blocked_handoff_calls_still_below_existing_threshold_after_shape_normalization": calls_still_below_threshold_after_shape_normalization,
        "blocked_handoff_plan_length": _number_summary(plan_lengths),
        "interpretation_contract": {
            "existing_e10g_handoff_threshold": 2,
            "threshold_changed": False,
            "only_existing_e10e_public_evidence_families_counted": True,
            "concrete_paths_are_matched_only_to_equivalent_frozen_public_get_routes": True,
            "query_fragment_or_longer_route_does_not_create_a_new_evidence_family": True,
            "zero_family_handoff_is_not_authorized": True,
        },
        "prints_private_outputs": False,
        "prints_group_level_rows": False,
        "prints_hashes": False,
        "prints_prompts": False,
        "prints_private_paths": False,
        "prints_oracle_data": False,
        "prints_evaluator_labels": False,
        "prints_concrete_resource_identifiers": False,
        "prints_evidence_plan_text": False,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
