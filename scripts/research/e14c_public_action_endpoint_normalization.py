#!/usr/bin/env python3
"""Public-contract action-endpoint canonicalization for E14c.

This module derives the five action endpoint shapes from the frozen public
``research/e2/tool_registry.py`` source without importing the E2 runtime (and
therefore without pulling Pydantic into minimal structural CI). It canonicalizes
only the *comparison view* used by policy guards. It never rewrites model
output, never inspects private oracle data, and never exposes concrete resource
identifiers.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOL_REGISTRY_SOURCE = _REPO_ROOT / "research" / "e2" / "tool_registry.py"


@dataclass(frozen=True)
class PublicActionEndpointSpec:
    canonical_endpoint: str
    method: str
    canonical_path: str
    concrete_pattern: re.Pattern[str]


def _literal_string(node: ast.AST) -> str:
    value = ast.literal_eval(node)
    if not isinstance(value, str):
        raise AssertionError("expected string literal in frozen public tool registry")
    return value


def _action_rows_from_frozen_tool_registry_source() -> list[tuple[str, str, list[str]]]:
    """Parse only literal action(method, path, params) declarations from TOOLS."""

    tree = ast.parse(_TOOL_REGISTRY_SOURCE.read_text(encoding="utf-8"))
    tools_value: ast.AST | None = None
    for statement in tree.body:
        if not isinstance(statement, ast.AnnAssign):
            continue
        if isinstance(statement.target, ast.Name) and statement.target.id == "TOOLS":
            tools_value = statement.value
            break
    if not isinstance(tools_value, ast.Tuple):
        raise AssertionError("frozen public tool registry TOOLS tuple not found")

    rows: list[tuple[str, str, list[str]]] = []
    for item in tools_value.elts:
        if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Name) or item.func.id != "action":
            continue
        if len(item.args) < 5:
            raise AssertionError("public action declaration missing required literal arguments")
        method = _literal_string(item.args[2]).upper()
        path_template = _literal_string(item.args[3])
        params_node = item.args[4]
        if not isinstance(params_node, ast.List):
            raise AssertionError("public action parameter declaration must be a literal list")
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
        rows.append((method, path_template, path_names))

    if len(rows) != 5:
        raise AssertionError(f"expected 5 frozen public action declarations, found {len(rows)}")
    return rows


def _canonical_path(path_template: str, path_names: list[str]) -> str:
    matches = list(_PLACEHOLDER_RE.finditer(path_template))
    if len(matches) != len(path_names):
        raise AssertionError(
            f"path placeholder/parameter mismatch in frozen public tool registry: "
            f"{len(matches)} placeholders vs {len(path_names)} path parameters"
        )
    names = iter(path_names)
    return _PLACEHOLDER_RE.sub(lambda _match: "{" + next(names) + "}", path_template)


def _concrete_path_pattern(path_template: str) -> str:
    pieces: list[str] = []
    cursor = 0
    for match in _PLACEHOLDER_RE.finditer(path_template):
        pieces.append(re.escape(path_template[cursor : match.start()]))
        # One concrete path segment only; query/fragment/extra text are rejected.
        pieces.append(r"[^/\s?#]+")
        cursor = match.end()
    pieces.append(re.escape(path_template[cursor:]))
    return "".join(pieces)


def _build_specs() -> tuple[PublicActionEndpointSpec, ...]:
    specs: list[PublicActionEndpointSpec] = []
    for method, path_template, path_names in _action_rows_from_frozen_tool_registry_source():
        canonical_path = _canonical_path(path_template, path_names).lower()
        canonical_endpoint = f"{method.lower()} {canonical_path}"
        concrete_pattern = re.compile(
            rf"^\s*{re.escape(method)}\s+{_concrete_path_pattern(path_template)}\s*$",
            flags=re.IGNORECASE,
        )
        specs.append(
            PublicActionEndpointSpec(
                canonical_endpoint=canonical_endpoint,
                method=method,
                canonical_path=canonical_path,
                concrete_pattern=concrete_pattern,
            )
        )
    if len({spec.canonical_endpoint for spec in specs}) != 5:
        raise AssertionError("public action endpoint canonical forms must be unique")
    return tuple(specs)


PUBLIC_ACTION_ENDPOINT_SPECS = _build_specs()
PUBLIC_ACTION_ENDPOINTS = frozenset(spec.canonical_endpoint for spec in PUBLIC_ACTION_ENDPOINT_SPECS)


def canonicalize_public_action_endpoint(value: Any) -> str:
    """Return a guard-comparison canonical endpoint without exposing identifiers.

    Non-endpoint strings are returned with the same lowercase/trim normalization
    used by the historical guards, so this function can safely replace their
    generic ``normalize_endpoint`` helpers (which also receive decision classes).
    """

    raw = str(value or "").strip()
    normalized = raw.lower()
    if not raw:
        return ""
    if normalized in {"none", "null", "n/a", "na", "no endpoint"}:
        return normalized
    if normalized in PUBLIC_ACTION_ENDPOINTS:
        return normalized
    for spec in PUBLIC_ACTION_ENDPOINT_SPECS:
        if spec.concrete_pattern.fullmatch(raw):
            return spec.canonical_endpoint
    return normalized


def endpoint_shape(value: Any) -> str:
    """Return a sanitized endpoint-shape class; never return concrete IDs."""

    raw = str(value or "").strip()
    normalized = raw.lower()
    if not raw or normalized in {"none", "null", "n/a", "na", "no endpoint"}:
        return "none_or_empty"
    if normalized in PUBLIC_ACTION_ENDPOINTS:
        return "already_canonical_public_action_endpoint"
    for spec in PUBLIC_ACTION_ENDPOINT_SPECS:
        if spec.concrete_pattern.fullmatch(raw):
            return "concrete_public_action_endpoint"
    return "unrecognized_endpoint_shape"


def canonical_public_endpoint_or_none(value: Any) -> str | None:
    canonical = canonicalize_public_action_endpoint(value)
    return canonical if canonical in PUBLIC_ACTION_ENDPOINTS else None
