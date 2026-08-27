#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Mapping

SAFETY_MARGIN_SECONDS = 30
MIN_INTER_REQUEST_DELAY_SECONDS = 30
MAX_PRE_OUTPUT_TRANSPORT_ATTEMPTS_PER_CELL = 3
MAX_COLLECTION_HOURS = 72

DURATION_RE = re.compile(r"^(?:(?P<h>\d+(?:\.\d+)?)h)?(?:(?P<m>\d+(?:\.\d+)?)m)?(?:(?P<s>\d+(?:\.\d+)?)s)?$")


def parse_duration_seconds(value: str) -> float:
    text = value.strip().lower()
    if text.isdigit() or re.fullmatch(r"\d+(?:\.\d+)?", text):
        return float(text)
    m = DURATION_RE.fullmatch(text)
    if not m or not any(m.groupdict().values()):
        raise ValueError(f"unsupported duration: {value}")
    return 3600 * float(m.group("h") or 0) + 60 * float(m.group("m") or 0) + float(m.group("s") or 0)


def _retry_after_deadline(value: str, now: datetime) -> datetime:
    text = value.strip()
    try:
        return now + timedelta(seconds=float(text))
    except ValueError:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)


def _reset_deadline(value: str, now: datetime) -> datetime:
    return now + timedelta(seconds=parse_duration_seconds(value))


def normalized_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {str(k).strip().lower(): str(v).strip() for k, v in headers.items()}


def provider_wait_deadline(headers: Mapping[str, str], now: datetime) -> datetime | None:
    h = normalized_headers(headers)
    candidates: list[datetime] = []
    if h.get("retry-after"):
        candidates.append(_retry_after_deadline(h["retry-after"], now))
    for key in ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"):
        if h.get(key):
            candidates.append(_reset_deadline(h[key], now))
    if not candidates:
        return None
    return max(candidates) + timedelta(seconds=SAFETY_MARGIN_SECONDS)


def proactive_capacity_decision(headers: Mapping[str, str], estimated_next_tokens: int, now: datetime) -> dict[str, Any]:
    h = normalized_headers(headers)
    rem_req = int(h["x-ratelimit-remaining-requests"]) if h.get("x-ratelimit-remaining-requests", "").isdigit() else None
    rem_tok = int(h["x-ratelimit-remaining-tokens"]) if h.get("x-ratelimit-remaining-tokens", "").isdigit() else None
    insufficient = (rem_req is not None and rem_req < 1) or (rem_tok is not None and rem_tok < int(estimated_next_tokens))
    if not insufficient:
        return {"send": True, "reason": "HEADROOM_OK", "resume_at": None}
    deadline = provider_wait_deadline(h, now)
    if deadline is None:
        return {"send": False, "reason": "INSUFFICIENT_HEADROOM_NO_RESET_METADATA", "resume_at": None}
    return {"send": False, "reason": "INSUFFICIENT_HEADROOM_WAIT_FOR_RESET", "resume_at": deadline.isoformat()}


def rate_limit_decision(status_code: int, headers: Mapping[str, str], model_output_received: bool, now: datetime) -> dict[str, Any]:
    if status_code != 429:
        return {"cell_pending": False, "abort_batch": False, "resume_at": None, "candidate_outcome": bool(model_output_received)}
    if model_output_received:
        return {"cell_pending": False, "abort_batch": False, "resume_at": None, "candidate_outcome": True}
    deadline = provider_wait_deadline(headers, now)
    if deadline is None:
        return {"cell_pending": True, "abort_batch": True, "resume_at": None, "candidate_outcome": False}
    return {"cell_pending": True, "abort_batch": False, "resume_at": deadline.isoformat(), "candidate_outcome": False}


def horizon_deadline(first_live_call_at: datetime) -> datetime:
    return first_live_call_at + timedelta(hours=MAX_COLLECTION_HOURS)


def within_horizon(first_live_call_at: datetime, now: datetime) -> bool:
    return now <= horizon_deadline(first_live_call_at)


def checkpoint_hash(checkpoint: Mapping[str, Any]) -> str:
    payload = json.dumps(checkpoint, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_checkpoint(checkpoint: Mapping[str, Any], declared_cell_ids: set[str]) -> None:
    completed = checkpoint.get("completed", {})
    pending = checkpoint.get("pending", [])
    if not isinstance(completed, dict) or not isinstance(pending, list):
        raise AssertionError("invalid checkpoint shape")
    if not set(completed).issubset(declared_cell_ids) or not set(pending).issubset(declared_cell_ids):
        raise AssertionError("checkpoint contains undeclared cell")
    if set(completed) & set(pending):
        raise AssertionError("completed cell cannot be pending")
    if set(completed) | set(pending) != declared_cell_ids:
        raise AssertionError("checkpoint must cover every declared cell")
    for cell_id, row in completed.items():
        if not isinstance(row, dict) or not row.get("parent_hash"):
            raise AssertionError(f"completed cell missing parent hash: {cell_id}")


def accept_parent(checkpoint: dict[str, Any], cell_id: str, parent_hash: str, raw_parent: Any) -> dict[str, Any]:
    completed = checkpoint.setdefault("completed", {})
    pending = checkpoint.setdefault("pending", [])
    if cell_id in completed:
        raise AssertionError("completed parent may never be regenerated")
    if cell_id not in pending:
        raise AssertionError("only pending predeclared cells may be accepted")
    completed[cell_id] = {"parent_hash": parent_hash, "raw_parent": raw_parent}
    checkpoint["pending"] = [x for x in pending if x != cell_id]
    return checkpoint


def public_checkpoint_record(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    completed = checkpoint.get("completed", {})
    pending = checkpoint.get("pending", [])
    return {
        "completed_cell_count": len(completed),
        "pending_cell_count": len(pending),
        "transport_failure_count": int(checkpoint.get("transport_failure_count", 0)),
        "rate_limit_event_count": int(checkpoint.get("rate_limit_event_count", 0)),
        "provider_reset_timestamp_or_duration": checkpoint.get("provider_reset_timestamp_or_duration"),
        "checkpoint_hash": checkpoint_hash(checkpoint),
    }
