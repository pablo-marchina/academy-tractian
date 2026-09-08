#!/usr/bin/env python3
from __future__ import annotations

"""Sanitized one-shot Groq rate diagnostic using the frozen T3-01 request shape.

This is not benchmark evidence and never records raw prompt/response/provider credentials.
It exists only to explain request-admission behavior before re-freezing a causal matrix.
"""

from hashlib import sha256
import json
import os
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.error
import urllib.request

from academy_tractian.decision_source import build_provider_decision_request
from academy_tractian.provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
)
from academy_tractian.provider_tournament_v3 import (
    POPULATION_SHA256,
    context_for_unit,
    load_frozen_tournament_v3,
)
from academy_tractian.runtime import canonical_tool_registry

SCHEMA_VERSION = "groq-benchmark-rate-diagnostic-v2"
MODEL_ID = "openai/gpt-oss-120b"
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
UNIT_ID = "T3-01-COMPANY-CONTEXT"
MAX_COMPLETION_TOKENS = 2048
EXPECTED_POPULATION_SHA256 = "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def safe_error(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {}
    error = payload.get("error")
    if not isinstance(error, Mapping):
        return {}
    result: dict[str, Any] = {}
    for key in ("type", "code", "message"):
        value = error.get(key)
        if value is not None:
            result[key] = str(value)[:1000]
    return result


def main() -> int:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY missing")

    root = Path(__file__).resolve().parents[2]
    bundle = load_frozen_tournament_v3(root)
    if POPULATION_SHA256 != EXPECTED_POPULATION_SHA256:
        raise RuntimeError("population hash drift")
    registry = canonical_tool_registry()
    context = context_for_unit(bundle, UNIT_ID)
    decision_request = build_provider_decision_request(context=context, registry=registry)

    body: dict[str, Any] = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": f"Reasoning: medium\n\n{PROVIDER_DECISION_SYSTEM_INSTRUCTION}",
            },
            {
                "role": "user",
                "content": canonical_json(decision_request.model_dump(mode="json")),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "provider_decision_payload",
                "strict": False,
                "schema": json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA)),
            },
        },
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "tool_choice": "none",
        "parallel_tool_calls": False,
        "include_reasoning": False,
    }

    encoded = canonical_json(body).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=encoded,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "academy-tractian-groq-benchmark-rate-diagnostic/2.0",
        },
    )

    started = time.perf_counter_ns()
    raw = ""
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status = int(response.status)
            headers = {k.casefold(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        status = int(exc.code)
        headers = {k.casefold(): v for k, v in exc.headers.items()}
    latency_ms = max(0, time.perf_counter_ns() - started) // 1_000_000

    try:
        payload: Any = json.loads(raw)
    except Exception:
        payload = {}

    usage = payload.get("usage") if isinstance(payload, Mapping) and isinstance(payload.get("usage"), Mapping) else {}
    rate_headers = {
        key: value
        for key, value in headers.items()
        if key.startswith("x-ratelimit-") or key in {"retry-after", "date"}
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "provider_id": "groq",
        "model_id": MODEL_ID,
        "unit_id": UNIT_ID,
        "population_sha256": POPULATION_SHA256,
        "request_sha256": decision_request.request_sha256,
        "request_body_sha256": digest(body),
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "http_status": status,
        "latency_ms": latency_ms,
        "rate_headers": rate_headers,
        "error": safe_error(payload),
        "prompt_tokens": usage.get("prompt_tokens") if isinstance(usage.get("prompt_tokens"), int) else None,
        "completion_tokens": usage.get("completion_tokens") if isinstance(usage.get("completion_tokens"), int) else None,
        "total_tokens": usage.get("total_tokens") if isinstance(usage.get("total_tokens"), int) else None,
        "raw_provider_material_recorded": False,
        "credentials_recorded": False,
        "promotion_authorized": False,
    }
    report["evidence_sha256"] = digest(report)
    print("GROQ_BENCHMARK_RATE_DIAGNOSTIC=" + canonical_json(report), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
