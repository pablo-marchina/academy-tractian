#!/usr/bin/env python3
"""Synthetic NVIDIA serving probe for V15. Never loads benchmark inputs or persists raw bodies."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any
import urllib.error
import urllib.request

ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
HISTORICAL_MODEL = "openai/gpt-oss-120b"
CANDIDATE_MODEL = "openai/gpt-oss-20b"


@dataclass(frozen=True)
class ProbeResult:
    probe: str
    model: str
    status: str
    http_status: int | None
    semantic_pass: bool
    request_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "probe": self.probe,
            "model": self.model,
            "status": self.status,
            "http_status": self.http_status,
            "semantic_pass": self.semantic_pass,
            "request_id": self.request_id,
        }


def _request_id(headers: Any) -> str | None:
    for name in ("x-request-id", "request-id"):
        value = headers.get(name) if headers is not None else None
        if isinstance(value, str) and value.strip():
            return value.strip()[:160]
    return None


def _post(key: str, body: dict[str, Any]) -> tuple[int, dict[str, Any], str | None]:
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "academy-tractian-v15-serving-probe/1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            status = int(response.status)
            request_id = _request_id(response.headers)
            raw = response.read()
    except urllib.error.HTTPError as exc:
        # Intentionally do not read or persist the provider error body.
        return int(exc.code), {}, _request_id(exc.headers)
    except Exception:
        return 0, {}, None
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except Exception:
        return status, {}, request_id
    return status, decoded if isinstance(decoded, dict) else {}, request_id


def _strict_json_body(model: str) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only the requested structured object."},
            {"role": "user", "content": "Return marker V15-NVIDIA-JSON and ok=true."},
        ],
        "temperature": 0,
        "max_tokens": 256,
        "reasoning_effort": "low",
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "v15_nvidia_probe",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "marker": {"type": "string", "enum": ["V15-NVIDIA-JSON"]},
                        "ok": {"type": "boolean", "const": True},
                    },
                    "required": ["marker", "ok"],
                },
            },
        },
    }


def _tool_body(model: str) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Call synthetic_lookup exactly once with marker V15-NVIDIA-TOOL. Do not answer directly.",
            }
        ],
        "temperature": 0,
        "max_tokens": 256,
        "reasoning_effort": "low",
        "stream": False,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "synthetic_lookup",
                    "description": "Synthetic compatibility probe only.",
                    "parameters": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "marker": {"type": "string", "enum": ["V15-NVIDIA-TOOL"]}
                        },
                        "required": ["marker"],
                    },
                },
            }
        ],
        "tool_choice": {"type": "function", "function": {"name": "synthetic_lookup"}},
        "parallel_tool_calls": False,
    }


def _choice(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
        return {}
    return choices[0]


def _json_semantic(payload: dict[str, Any]) -> bool:
    message = _choice(payload).get("message")
    if not isinstance(message, dict):
        return False
    content = message.get("content")
    if not isinstance(content, str):
        return False
    try:
        decoded = json.loads(content)
    except Exception:
        return False
    return decoded == {"marker": "V15-NVIDIA-JSON", "ok": True}


def _tool_semantic(payload: dict[str, Any]) -> bool:
    message = _choice(payload).get("message")
    if not isinstance(message, dict):
        return False
    calls = message.get("tool_calls")
    if not isinstance(calls, list) or len(calls) != 1 or not isinstance(calls[0], dict):
        return False
    function = calls[0].get("function")
    if not isinstance(function, dict) or function.get("name") != "synthetic_lookup":
        return False
    arguments = function.get("arguments")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except Exception:
            return False
    return isinstance(arguments, dict) and arguments.get("marker") == "V15-NVIDIA-TOOL"


def run() -> dict[str, Any]:
    key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not key:
        raise SystemExit("NVIDIA_API_KEY missing")

    results: list[ProbeResult] = []

    status, payload, request_id = _post(key, _strict_json_body(HISTORICAL_MODEL))
    historical_semantic = 200 <= status < 300 and _json_semantic(payload)
    if status == 404:
        historical_state = "DEPRECATED_OR_ROUTE_UNAVAILABLE"
    elif historical_semantic:
        historical_state = "SERVING_COMPATIBLE"
    elif 200 <= status < 300:
        historical_state = "SERVED_BUT_CONTRACT_INCOMPATIBLE"
    else:
        historical_state = "HTTP_FAILURE"
    results.append(
        ProbeResult(
            "historical_strict_json",
            HISTORICAL_MODEL,
            historical_state,
            status or None,
            historical_semantic,
            request_id,
        )
    )

    status, payload, request_id = _post(key, _strict_json_body(CANDIDATE_MODEL))
    candidate_json = 200 <= status < 300 and _json_semantic(payload)
    results.append(
        ProbeResult(
            "candidate_strict_json",
            CANDIDATE_MODEL,
            "PASS" if candidate_json else "FAIL",
            status or None,
            candidate_json,
            request_id,
        )
    )

    status, payload, request_id = _post(key, _tool_body(CANDIDATE_MODEL))
    candidate_tool = 200 <= status < 300 and _tool_semantic(payload)
    results.append(
        ProbeResult(
            "candidate_native_tool_call",
            CANDIDATE_MODEL,
            "PASS" if candidate_tool else "FAIL",
            status or None,
            candidate_tool,
            request_id,
        )
    )

    candidate_pass = candidate_json and candidate_tool
    summary = {
        "schema_version": "nvidia-v15-serving-probe-v1",
        "endpoint": ENDPOINT,
        "historical_model": HISTORICAL_MODEL,
        "candidate_model": CANDIDATE_MODEL,
        "candidate_pass": candidate_pass,
        "results": [item.as_dict() for item in results],
        "provider_calls": 3,
        "official_cases_loaded": 0,
        "official_cases_consumed": 0,
        "raw_response_body_persisted": False,
        "credential_persisted": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-candidate-pass", action="store_true")
    args = parser.parse_args()
    summary = run()
    if args.require_candidate_pass and not summary["candidate_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
