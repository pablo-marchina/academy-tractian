#!/usr/bin/env python3
"""Public-contract action-endpoint canonicalization for E14c.

This module derives the five action endpoint shapes from the frozen public
ToolSpec registry. It canonicalizes only the *comparison view* used by policy
guards. It never rewrites model output, never inspects private oracle data, and
never exposes concrete resource identifiers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from research.e2.tool_registry import TOOLS

_PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")


@dataclass(frozen=True)
class PublicActionEndpointSpec:
    canonical_endpoint: str
    method: str
    canonical_path: str
    concrete_pattern: re.Pattern[str]


def _canonical_path_for_tool(tool: Any) -> str:
    path_names = [
        str(parameter.name)
        for parameter in tool.parameters
        if str(parameter.location).lower() == "path"
    ]
    matches = list(_PLACEHOLDER_RE.finditer(str(tool.path_template)))
    if len(matches) != len(path_names):
        raise AssertionError(
            f"path placeholder/parameter mismatch for public tool {tool.name}: "
            f"{len(matches)} placeholders vs {len(path_names)} path parameters"
        )
    names = iter(path_names)
    return _PLACEHOLDER_RE.sub(lambda _match: "{" + next(names) + "}", str(tool.path_template))


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
    for tool in TOOLS:
        method = str(tool.method).upper()
        if method == "GET":
            continue
        canonical_path = _canonical_path_for_tool(tool).lower()
        canonical_endpoint = f"{method.lower()} {canonical_path}"
        concrete_pattern = re.compile(
            rf"^\s*{re.escape(method)}\s+{_concrete_path_pattern(str(tool.path_template))}\s*$",
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
    if len(specs) != 5:
        raise AssertionError(f"expected 5 public action endpoints, found {len(specs)}")
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
