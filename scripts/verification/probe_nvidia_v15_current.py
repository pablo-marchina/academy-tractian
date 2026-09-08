#!/usr/bin/env python3
"""Current two-call NVIDIA V15 compatibility probe.

This is intentionally separate from the historical P12-C4 frozen probe. It performs exactly two
synthetic requests, no retries and no fallback, and never records response bodies, reasoning text,
headers, credentials, account identifiers, benchmark inputs, or locked evaluation material.
"""
from __future__ import annotations

import json
import os
import time
from collections.abc import Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ENDPOINT = os.environ.get(
    "NVIDIA_ENDPOINT",
    "https://integrate.api.nvidia.com/v1/chat/completions",
).strip()
MODEL = os.environ.get("NVIDIA_MODEL_ID", "nvidia/nemotron-3-super-120b-a12b").strip()
TIMEOUT_SECONDS = 45.0


def _post(api_key: str, payload: dict[str, object]) -> tuple[int, Mapping[str, object] | None, float]:
    request = Request(
        ENDPOINT,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed NVIDIA HTTPS endpoint
            status = int(response.status)
            raw = response.read()
    except HTTPError as exc:
        # Deliberately do not read or retain the error response body or headers.
        return int(exc.code), None, time.monotonic() - started
    except (URLError, TimeoutError, OSError):
        return 0, None, time.monotonic() - started

    try:
        decoded = json.loads(raw.decode("utf-8")) if raw else None
    except (json.JSONDecodeError, UnicodeDecodeError):
        decoded = None
    return status, decoded if isinstance(decoded, Mapping) else None, time.monotonic() - started


def _choice(body: Mapping[str, object] | None) -> Mapping[str, object] | None:
    if body is None:
        return None
    choices = body.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], Mapping):
        return None
    return choices[0]


def _strict_semantics(body: Mapping[str, object] | None) -> bool:
    choice = _choice(body)
    if choice is None or choice.get("finish_reason") != "stop":
        return False
    message = choice.get("message")
    if not isinstance(message, Mapping):
        return False
    content = message.get("content")
    if not isinstance(content, str):
        return False
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return False
    return parsed == {"contract_marker": "V15-NVIDIA-STRICT", "ok": True}


def _tool_semantics(body: Mapping[str, object] | None) -> bool:
    choice = _choice(body)
    if choice is None:
        return False
    message = choice.get("message")
    if not isinstance(message, Mapping):
        return False
    calls = message.get("tool_calls")
    if not isinstance(calls, list) or len(calls) != 1 or not isinstance(calls[0], Mapping):
        return False
    call = calls[0]
    function = call.get("function")
    if call.get("type") != "function" or not isinstance(function, Mapping):
        return False
    if function.get("name") != "lookup_asset_status":
        return False
    arguments = function.get("arguments")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return False
    return isinstance(arguments, Mapping) and arguments.get("marker") == "V15-NVIDIA-TOOL"


def _safe_projection(
    *,
    probe: str,
    status: int,
    body: Mapping[str, object] | None,
    elapsed_seconds: float,
    semantic_pass: bool,
) -> dict[str, object]:
    choice = _choice(body)
    finish_reason = choice.get("finish_reason") if choice is not None else None
    served_model = body.get("model") if body is not None else None
    usage = body.get("usage") if body is not None else None
    usage_present = isinstance(usage, Mapping)
    return {
        "probe": probe,
        "http_status": status,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "served_model_matches": isinstance(served_model, str) and served_model == MODEL,
        "choice_present": choice is not None,
        "finish_reason": finish_reason if isinstance(finish_reason, str) else None,
        "usage_present": usage_present,
        "semantic_pass": semantic_pass,
        "response_body_recorded": False,
        "response_headers_recorded": False,
        "reasoning_content_recorded": False,
    }


def main() -> int:
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not api_key:
        print(json.dumps({"schema_version": "nvidia-v15-current-probe-v1", "status": "BLOCKED", "reason": "NVIDIA_API_KEY_MISSING"}, sort_keys=True))
        return 2

    strict_payload: dict[str, object] = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Synthetic compatibility probe only. Return exactly the requested JSON object.",
            },
            {
                "role": "user",
                "content": "Return contract_marker='V15-NVIDIA-STRICT' and ok=true.",
            },
        ],
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_tokens": 4096,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "v15_nvidia_strict_probe",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "contract_marker": {"type": "string", "const": "V15-NVIDIA-STRICT"},
                        "ok": {"type": "boolean", "const": True},
                    },
                    "required": ["contract_marker", "ok"],
                    "additionalProperties": False,
                },
            },
        },
    }
    status1, body1, elapsed1 = _post(api_key, strict_payload)
    strict_ok = 200 <= status1 < 300 and _strict_semantics(body1)
    result1 = _safe_projection(
        probe="strict_json_runtime_shape",
        status=status1,
        body=body1,
        elapsed_seconds=elapsed1,
        semantic_pass=strict_ok,
    )

    tool_payload: dict[str, object] = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Synthetic compatibility probe only. Call the requested function exactly once.",
            },
            {
                "role": "user",
                "content": "Call lookup_asset_status with marker='V15-NVIDIA-TOOL'.",
            },
        ],
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_tokens": 4096,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "lookup_asset_status",
                    "description": "Synthetic compatibility tool; performs no external action.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "marker": {"type": "string", "const": "V15-NVIDIA-TOOL"},
                        },
                        "required": ["marker"],
                        "additionalProperties": False,
                    },
                },
            }
        ],
        "tool_choice": {
            "type": "function",
            "function": {"name": "lookup_asset_status"},
        },
        "parallel_tool_calls": False,
    }
    status2, body2, elapsed2 = _post(api_key, tool_payload)
    tool_ok = 200 <= status2 < 300 and _tool_semantics(body2)
    result2 = _safe_projection(
        probe="native_tool_call_capability",
        status=status2,
        body=body2,
        elapsed_seconds=elapsed2,
        semantic_pass=tool_ok,
    )

    passed = strict_ok and tool_ok
    report = {
        "schema_version": "nvidia-v15-current-probe-v1",
        "status": "PASS" if passed else "FAIL",
        "endpoint": ENDPOINT,
        "model": MODEL,
        "provider_request_attempts": 2,
        "automatic_retries": 0,
        "provider_fallbacks": 0,
        "model_fallbacks": 0,
        "locked_eval_cases_accessed": 0,
        "raw_provider_material_recorded": False,
        "credentials_recorded": False,
        "calls": [result1, result2],
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
