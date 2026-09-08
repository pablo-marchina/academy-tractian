#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

MODEL = "openai/gpt-oss-120b"
UA = "academy-tractian-groq-rate-diagnostic/1.0"


def _summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    error = payload.get("error")
    if not isinstance(error, dict):
        return {}
    result: dict[str, Any] = {}
    for key in ("type", "code", "message"):
        value = error.get(key)
        if value is not None:
            text = str(value)
            result[key] = text[:500]
    return result


def _request(method: str, url: str, *, key: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = int(resp.status)
            headers = resp.headers
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = int(exc.code)
        headers = exc.headers
    try:
        payload: Any = json.loads(raw)
    except Exception:
        payload = {}
    rate_headers = {
        k.casefold(): v
        for k, v in headers.items()
        if k.casefold().startswith("x-ratelimit-") or k.casefold() in {"retry-after", "date"}
    }
    return {
        "status": status,
        "rate_headers": rate_headers,
        "error": _summary(payload),
    }


def main() -> int:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY missing")
    base = "https://api.groq.com/openai/v1"
    report = {
        "schema_version": "groq-rate-limit-diagnostic-v1",
        "models": _request("GET", f"{base}/models", key=key),
        "chat": _request(
            "POST",
            f"{base}/chat/completions",
            key=key,
            body={
                "model": MODEL,
                "messages": [{"role": "user", "content": "Reply OK"}],
                "temperature": 0,
                "max_completion_tokens": 8,
                "stream": False,
                "reasoning_effort": "low",
                "include_reasoning": False,
            },
        ),
    }
    print("GROQ_RATE_DIAGNOSTIC=" + json.dumps(report, sort_keys=True, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
