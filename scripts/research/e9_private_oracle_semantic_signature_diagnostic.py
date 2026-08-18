#!/usr/bin/env python3
"""Aggregate-only semantic-shape diagnostic for private expected paths.

The script may read private expected-path text locally, but it never prints any
oracle text, ids, asset names, hashes, paths, endpoint names, per-row labels, or
per-row results. It reports only aggregate structural signatures needed to
choose an evaluator implementation strategy before seeing a candidate result.

The public tool contract is parsed statically from research/e2/tool_registry.py
so this diagnostic has no runtime dependency on pydantic or the application.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

NEGATION_MARKERS = (
    " no ", " not ", " don't ", " do not ", " without ", " avoid ", " never ",
    " não ", " nao ", " sem ", " evitar ", " nunca ",
)
CONDITIONAL_MARKERS = (
    " if ", " when ", " unless ", " only if ", " after ", " before ",
    " se ", " quando ", " somente se ", " apenas se ", " depois ", " antes ",
)
METHOD_RE = re.compile(r"\b(GET|POST|PATCH|PUT|DELETE)\b", re.IGNORECASE)
PATH_LIKE_RE = re.compile(r"/(?:[A-Za-z0-9_{}-]+/?){1,8}")
READ_DECL_RE = re.compile(r'read\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*"([^"]+)"')
ACTION_DECL_RE = re.compile(r'action\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*"([A-Z]+)"\s*,\s*"([^"]+)"')
TOOL_REGISTRY_PATH = Path("research/e2/tool_registry.py")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict) and isinstance(row.get("expected_path"), list)]


def _template_regex(template: str) -> re.Pattern[str]:
    escaped = re.escape(template.lower())
    escaped = re.sub(r"\\\{[^{}]+\\\}", r"[a-z0-9_.:-]+", escaped)
    return re.compile(escaped, re.IGNORECASE)


def _public_tool_patterns() -> list[tuple[str, re.Pattern[str], str]]:
    source = TOOL_REGISTRY_PATH.read_text(encoding="utf-8")
    patterns: list[tuple[str, re.Pattern[str], str]] = []
    for match in READ_DECL_RE.finditer(source):
        patterns.append(("GET", _template_regex(match.group(1)), "read"))
    for match in ACTION_DECL_RE.finditer(source):
        patterns.append((match.group(1).upper(), _template_regex(match.group(2)), "action"))
    if len(patterns) != 18:
        raise AssertionError(f"expected 18 public tools, parsed {len(patterns)}")
    return patterns


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    padded = f" {text.lower()} "
    return any(marker in padded for marker in markers)


def _tool_signature(text: str, patterns: list[tuple[str, re.Pattern[str], str]]) -> tuple[bool, bool, bool, bool]:
    lowered = text.lower()
    method_tokens = {match.group(1).upper() for match in METHOD_RE.finditer(text)}
    any_path = bool(PATH_LIKE_RE.search(text))
    any_tool_path = False
    method_and_tool_path = False
    matched_any_tool = False
    for method, path_re, _kind in patterns:
        if not path_re.search(lowered):
            continue
        any_tool_path = True
        matched_any_tool = True
        if method in method_tokens:
            method_and_tool_path = True
    return any_path, any_tool_path, method_and_tool_path, matched_any_tool


def run(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    rows = _rows(payload)
    patterns = _public_tool_patterns()

    total_steps = 0
    steps_with_method = 0
    steps_with_path_like = 0
    steps_with_public_tool_path = 0
    steps_with_method_and_public_tool_path = 0
    steps_with_any_public_tool_signature = 0
    steps_with_negation = 0
    steps_with_condition = 0
    notes_with_negation = 0
    notes_with_condition = 0
    rows_with_public_tool_step = 0
    rows_with_all_steps_public_tool_recognizable = 0
    rows_with_any_negation = 0
    rows_with_any_condition = 0

    for row in rows:
        row_tool_hits = 0
        row_negation = False
        row_condition = False
        expected = row.get("expected_path") or []
        valid_steps = [item for item in expected if isinstance(item, dict)]
        total_steps += len(valid_steps)
        for item in valid_steps:
            step = str(item.get("step") or "")
            note = str(item.get("note") or "")
            if METHOD_RE.search(step):
                steps_with_method += 1
            path_like, tool_path, method_tool, any_tool = _tool_signature(step, patterns)
            if path_like:
                steps_with_path_like += 1
            if tool_path:
                steps_with_public_tool_path += 1
            if method_tool:
                steps_with_method_and_public_tool_path += 1
            if any_tool:
                steps_with_any_public_tool_signature += 1
                row_tool_hits += 1
            step_neg = _contains_marker(step, NEGATION_MARKERS)
            step_cond = _contains_marker(step, CONDITIONAL_MARKERS)
            note_neg = _contains_marker(note, NEGATION_MARKERS)
            note_cond = _contains_marker(note, CONDITIONAL_MARKERS)
            steps_with_negation += int(step_neg)
            steps_with_condition += int(step_cond)
            notes_with_negation += int(note_neg)
            notes_with_condition += int(note_cond)
            row_negation = row_negation or step_neg or note_neg
            row_condition = row_condition or step_cond or note_cond
        if row_tool_hits:
            rows_with_public_tool_step += 1
        if valid_steps and row_tool_hits == len(valid_steps):
            rows_with_all_steps_public_tool_recognizable += 1
        rows_with_any_negation += int(row_negation)
        rows_with_any_condition += int(row_condition)

    match_fraction = round(steps_with_any_public_tool_signature / total_steps, 4) if total_steps else 0.0
    strict_fraction = round(steps_with_method_and_public_tool_path / total_steps, 4) if total_steps else 0.0
    if strict_fraction >= 0.8:
        strategy = "DETERMINISTIC_PUBLIC_TOOL_SIGNATURE_EXTRACTION_IS_HIGH_COVERAGE"
    elif match_fraction >= 0.8:
        strategy = "PUBLIC_TOOL_PATH_EXTRACTION_HIGH_COVERAGE_BUT_METHOD_NORMALIZATION_NEEDED"
    else:
        strategy = "EXPECTED_STEPS_ARE_NOT_PREDOMINANTLY_EXACT_PUBLIC_TOOL_SIGNATURES;TEXT_SEMANTIC_NORMALIZATION_REQUIRED"

    return {
        "status": "E9_PRIVATE_ORACLE_SEMANTIC_SIGNATURE_DIAGNOSTIC",
        "expected_path_rows_found": len(rows),
        "expected_path_steps_found": total_steps,
        "public_tool_registry_entries_parsed": len(patterns),
        "steps_with_http_method_token": steps_with_method,
        "steps_with_path_like_token": steps_with_path_like,
        "steps_with_recognizable_public_tool_path": steps_with_public_tool_path,
        "steps_with_method_and_recognizable_public_tool_path": steps_with_method_and_public_tool_path,
        "steps_with_any_recognizable_public_tool_signature": steps_with_any_public_tool_signature,
        "public_tool_signature_step_coverage_fraction": match_fraction,
        "strict_method_plus_tool_step_coverage_fraction": strict_fraction,
        "rows_with_at_least_one_recognizable_public_tool_step": rows_with_public_tool_step,
        "rows_with_all_steps_recognizable_as_public_tools": rows_with_all_steps_public_tool_recognizable,
        "steps_with_negation_marker": steps_with_negation,
        "steps_with_conditional_marker": steps_with_condition,
        "notes_with_negation_marker": notes_with_negation,
        "notes_with_conditional_marker": notes_with_condition,
        "rows_with_any_negation_marker": rows_with_any_negation,
        "rows_with_any_conditional_marker": rows_with_any_condition,
        "recommended_evaluator_normalization_strategy": strategy,
        "root_question_excluded_from_signature_analysis": True,
        "mode_excluded_from_action_escalation_label_inference": True,
        "prints_oracle_values": False,
        "prints_expected_path_text": False,
        "prints_root_question_text": False,
        "prints_ids_or_asset_names": False,
        "prints_endpoint_names": False,
        "prints_per_row_results": False,
        "prints_hashes": False,
        "prints_private_path": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "changes_scorer": False,
        "changes_candidate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle-file", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.oracle_file), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
