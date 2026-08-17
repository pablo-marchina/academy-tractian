#!/usr/bin/env python3
"""Public GET evidence-family canonicalization for E14d.

E10e/E10g historically count a fixed tuple of canonical public GET route
markers by literal substring. E14d preserves exactly that accepted family set
and threshold semantics, but recognizes concrete public paths equivalent to the
same frozen ToolSpec routes.

This module is stdlib-only, reads only public repository source, never rewrites
model output, and never inspects private oracle, scorer, VALIDATION, or
LOCKED_TEST material.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
E10E_SOURCE = HERE / "e10e_dev_only_premature_action_guard.py"
TOOL_REGISTRY_SOURCE = REPO_ROOT / "research" / "e2" / "tool_registry.py"
_PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")


def _literal_string(node: ast.AST) -> str:
    value = ast.literal_eval(node)
    if not isinstance(value, str):
        raise AssertionError("expected string literal in public contract source")
    return value


def accepted_evidence_markers() -> tuple[str, ...]:
    """Read the historical accepted family set directly from E10e source."""
    tree = ast.parse(E10E_SOURCE.read_text(encoding="utf-8"))
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "CONCRETE_EVIDENCE_MARKERS"
            for target in statement.targets
        ):
            continue
        value = ast.literal_eval(statement.value)
        if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
            raise AssertionError("CONCRETE_EVIDENCE_MARKERS must remain a literal tuple of strings")
        markers = tuple(str(item).strip().lower() for item in value)
        if len(markers) != 10 or len(set(markers)) != 10:
            raise AssertionError("expected exactly 10 distinct historical public evidence families")
        return markers
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
        # One path segment only. Query/fragment text may follow the route but
        # cannot become a new family; longer route suffixes do not match.
        pieces.append(r"[^/\s?#,;:)\]\}]+")
        cursor = match.end()
    pieces.append(re.escape(path_template[cursor:]))
    return "".join(pieces)


def frozen_public_read_patterns() -> dict[str, re.Pattern[str]]:
    """Return patterns only for the already-accepted E10e evidence families."""
    markers = set(accepted_evidence_markers())
    tree = ast.parse(TOOL_REGISTRY_SOURCE.read_text(encoding="utf-8"))
    tools_value: ast.AST | None = None
    for statement in tree.body:
        if (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == "TOOLS"
        ):
            tools_value = statement.value
            break
    if not isinstance(tools_value, ast.Tuple):
        raise AssertionError("frozen public tool registry TOOLS tuple not found")

    patterns: dict[str, re.Pattern[str]] = {}
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
        if canonical not in markers:
            continue
        concrete_route = _concrete_path_pattern(path_template)
        patterns[canonical] = re.compile(
            rf"(?<![A-Za-z0-9_])get\s+{concrete_route}(?=$|[\s?#,;:.)\]\}}])",
            flags=re.IGNORECASE,
        )

    if set(patterns) != markers:
        missing = sorted(markers - set(patterns))
        raise AssertionError(f"historical evidence families missing from frozen public read routes: {len(missing)}")
    return patterns


ACCEPTED_EVIDENCE_MARKERS = accepted_evidence_markers()
PUBLIC_READ_PATTERNS = frozen_public_read_patterns()


def evidence_plan_text(output: dict[str, Any]) -> str:
    plan = output.get("evidence_plan")
    if not isinstance(plan, list):
        return ""
    return "\n".join(str(item) for item in plan).lower()


def matched_public_evidence_families(output: dict[str, Any]) -> frozenset[str]:
    """Return distinct historical evidence families visible in template or concrete form."""
    text = evidence_plan_text(output)
    if not text:
        return frozenset()
    matched: set[str] = set()
    for marker in ACCEPTED_EVIDENCE_MARKERS:
        if marker in text or PUBLIC_READ_PATTERNS[marker].search(text):
            matched.add(marker)
    return frozenset(matched)


def public_evidence_family_count(output: dict[str, Any]) -> int:
    return len(matched_public_evidence_families(output))


def historical_template_marker_count(output: dict[str, Any]) -> int:
    text = evidence_plan_text(output)
    return sum(1 for marker in ACCEPTED_EVIDENCE_MARKERS if marker in text)


def concrete_equivalent_family_count(output: dict[str, Any]) -> int:
    text = evidence_plan_text(output)
    count = 0
    for marker in ACCEPTED_EVIDENCE_MARKERS:
        if marker not in text and PUBLIC_READ_PATTERNS[marker].search(text):
            count += 1
    return count
