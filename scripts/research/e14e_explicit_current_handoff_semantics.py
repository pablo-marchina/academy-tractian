#!/usr/bin/env python3
"""Deterministic explicit current-handoff semantics for E14e.

Historical E10d escalates on any marker substring such as "risk", "safety",
"severity", or "escalation" anywhere in visible model text. E14e keeps every
strong structured E10d condition unchanged and narrows only that final textual
fallback: a current handoff must be stated explicitly and positively.

Negated, conditional/contingent, or bare marker context is not by itself a
current handoff instruction. This module is stdlib-only and uses no oracle,
scorer, VALIDATION, or LOCKED_TEST data.
"""

from __future__ import annotations

import re
from typing import Any

SEMANTIC_FIELDS = (
    "proposed_next_step",
    "risk_notes",
    "evidence_plan",
    "action_escalation_rubric.calibration_reason",
)

POSITIVE_CURRENT_HANDOFF_PATTERNS = (
    r"\brequires?\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bneeds?\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\b(?:human|specialist|engineering)\s+review\s+(?:is\s+)?required\b",
    r"\bescalation\s+(?:is\s+)?required\b",
    r"\bapproval\s+(?:is\s+)?required\b",
    r"\bmust\s+escalate\b",
    r"\bshould\s+escalate\b",
    r"^\s*escalate\b",
    r"\bescalate\s+(?:this|the|to)\b",
    r"\broute\s+(?:this\s+|the\s+)?(?:case\s+)?to\s+(?:a\s+)?(?:human|specialist|engineer)\b",
    r"\brefer\s+(?:this\s+|the\s+)?(?:case\s+)?to\s+(?:a\s+)?(?:human|specialist|engineer)\b",
    r"\bobtain\s+(?:human\s+)?approval\b",
    r"\brequest\s+(?:a\s+)?specialist\b",
    r"\brequer\s+(?:um\s+)?(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
    r"\bnecessita\s+(?:de\s+)?(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
    r"\brevis[aã]o\s+humana\s+(?:é\s+)?necess[aá]ria\b",
    r"\bescalonamento\s+(?:é\s+)?necess[aá]rio\b",
    r"\bdeve\s+escalar\b",
    r"^\s*escalar\b",
    r"\bescalar\s+para\b",
    r"\bencaminhar\s+(?:o\s+caso\s+)?para\s+(?:um\s+)?(?:humano|especialista|engenheiro)\b",
)

NEGATIVE_HANDOFF_PATTERNS = (
    r"\bno\s+(?:human\s+)?escalation\b",
    r"\bwithout\s+(?:human\s+)?escalation\b",
    r"\bdoes\s+not\s+require\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bdoesn't\s+require\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bescalation\s+(?:is\s+)?not\s+required\b",
    r"\b(?:human|specialist|engineering)\s+review\s+(?:is\s+)?not\s+required\b",
    r"\bapproval\s+(?:is\s+)?not\s+required\b",
    r"\bdo\s+not\s+escalate\b",
    r"\bshould\s+not\s+escalate\b",
    r"\bdo\s+not\s+request\s+(?:a\s+)?specialist\b",
    r"\bn[aã]o\s+(?:requer|necessita\s+de)\s+(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
    r"\bsem\s+necessidade\s+de\s+(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
    r"\bescalonamento\s+n[aã]o\s+(?:é\s+)?necess[aá]rio\b",
    r"\bn[aã]o\s+deve\s+escalar\b",
)

CONDITIONAL_HANDOFF_PATTERNS = (
    r"\bif\b[^\n]{0,140}\bescalat(?:e|ion)\b",
    r"\bescalat(?:e|ion)\b[^\n]{0,140}\bif\b",
    r"\bunless\b[^\n]{0,140}\bescalat(?:e|ion)\b",
    r"\bescalat(?:e|ion)\b[^\n]{0,140}\bunless\b",
    r"\bconsider\s+(?:human\s+)?escalation\b",
    r"\bmay\s+require\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bmight\s+require\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bcould\s+require\s+(?:a\s+)?(?:human\s+)?(?:escalation|review|approval)\b",
    r"\bse\b[^\n]{0,140}\b(?:escalar|escalonamento)\b",
    r"\bconsiderar\s+escalonamento\b",
    r"\bpode\s+requerer\s+(?:escalonamento|revis[aã]o\s+humana|aprova[cç][aã]o)\b",
)

_SEGMENT_SPLIT_RE = re.compile(r"(?:[.!?;]+|\n+)")


def _field_value(output: dict[str, Any], field: str) -> Any:
    if field == "action_escalation_rubric.calibration_reason":
        rubric = output.get("action_escalation_rubric")
        return rubric.get("calibration_reason") if isinstance(rubric, dict) else ""
    return output.get(field)


def field_text(output: dict[str, Any], field: str) -> str:
    value = _field_value(output, field)
    if isinstance(value, list):
        return "\n".join(str(item) for item in value).lower()
    return str(value or "").lower()


def _matches(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def segment_has_explicit_positive_current_handoff(segment: str) -> bool:
    """True only for an unambiguous positive current-handoff segment."""
    text = str(segment or "").strip().lower()
    if not text:
        return False
    if _matches(NEGATIVE_HANDOFF_PATTERNS, text):
        return False
    if _matches(CONDITIONAL_HANDOFF_PATTERNS, text):
        return False
    return _matches(POSITIVE_CURRENT_HANDOFF_PATTERNS, text)


def field_has_explicit_positive_current_handoff(text: str) -> bool:
    for segment in _SEGMENT_SPLIT_RE.split(str(text or "")):
        if segment_has_explicit_positive_current_handoff(segment):
            return True
    return False


def explicit_current_handoff_fields(output: dict[str, Any]) -> tuple[str, ...]:
    matched: list[str] = []
    for field in SEMANTIC_FIELDS:
        if field_has_explicit_positive_current_handoff(field_text(output, field)):
            matched.append(field)
    return tuple(matched)


def has_explicit_current_handoff(output: dict[str, Any]) -> bool:
    return bool(explicit_current_handoff_fields(output))
