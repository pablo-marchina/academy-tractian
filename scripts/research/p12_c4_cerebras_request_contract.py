#!/usr/bin/env python3
"""Pure P12-C4 Cerebras request-contract builder.

This module deliberately performs no network I/O and reads no credentials. It only
materializes the prospectively frozen OpenAI-compatible request contract selected
for P12-C4 so provider compatibility can be qualified without touching benchmark
inputs or consuming a live experiment.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping, Sequence


PROVIDER = "cerebras"
MODEL_ID = "gpt-oss-120b"
UNDERLYING_MODEL_FAMILY = "openai/gpt-oss-120b"
TEMPERATURE = 0
REASONING_EFFORT = "medium"
REASONING_FORMAT = "hidden"
MAX_COMPLETION_TOKENS = 4096


class ContractError(ValueError):
    """Raised when a request would violate the frozen P12-C4 serving contract."""


def _validate_messages(messages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(messages, Sequence) or isinstance(messages, (str, bytes)) or not messages:
        raise ContractError("messages must be a non-empty sequence")
    normalized: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        if not isinstance(message, Mapping):
            raise ContractError(f"message {index} must be an object")
        role = message.get("role")
        content = message.get("content")
        if role not in {"system", "user", "assistant", "tool"}:
            raise ContractError(f"message {index} has unsupported role: {role!r}")
        if not isinstance(content, str) or not content:
            raise ContractError(f"message {index} content must be a non-empty string")
        normalized.append(deepcopy(dict(message)))
    return normalized


def _validate_seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ContractError("seed must be an integer")
    if seed < 0:
        raise ContractError("seed must be non-negative")
    return seed


def _base_request(messages: Sequence[Mapping[str, Any]], *, seed: int) -> dict[str, Any]:
    return {
        "model": MODEL_ID,
        "messages": _validate_messages(messages),
        "temperature": TEMPERATURE,
        "seed": _validate_seed(seed),
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "reasoning_effort": REASONING_EFFORT,
        "reasoning_format": REASONING_FORMAT,
        "stream": False,
    }


def _validate_strict_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(schema, Mapping):
        raise ContractError("json schema must be an object")
    result = deepcopy(dict(schema))
    if result.get("type") != "object":
        raise ContractError("strict response schema root type must be object")
    if result.get("additionalProperties") is not False:
        raise ContractError("strict response schema must set additionalProperties=false")
    properties = result.get("properties")
    required = result.get("required")
    if not isinstance(properties, Mapping) or not properties:
        raise ContractError("strict response schema must declare properties")
    if not isinstance(required, list) or set(required) != set(properties):
        raise ContractError("strict response schema must require every root property")
    return result


def build_structured_output_request(
    messages: Sequence[Mapping[str, Any]],
    *,
    seed: int,
    schema_name: str,
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the frozen strict-JSON request without contacting Cerebras."""
    if not isinstance(schema_name, str) or not schema_name.strip():
        raise ContractError("schema_name must be non-empty")
    request = _base_request(messages, seed=seed)
    request["response_format"] = {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": True,
            "schema": _validate_strict_schema(schema),
        },
    }
    return request


def build_tool_request(
    messages: Sequence[Mapping[str, Any]],
    *,
    seed: int,
    tools: Sequence[Mapping[str, Any]],
    tool_choice: str | Mapping[str, Any] = "auto",
) -> dict[str, Any]:
    """Build the frozen tool-capable request without contacting Cerebras."""
    if not isinstance(tools, Sequence) or isinstance(tools, (str, bytes)) or not tools:
        raise ContractError("tools must be a non-empty sequence")
    normalized_tools: list[dict[str, Any]] = []
    for index, tool in enumerate(tools):
        if not isinstance(tool, Mapping) or tool.get("type") != "function":
            raise ContractError(f"tool {index} must be a function tool")
        function = tool.get("function")
        if not isinstance(function, Mapping) or not isinstance(function.get("name"), str):
            raise ContractError(f"tool {index} must declare a function name")
        normalized_tools.append(deepcopy(dict(tool)))
    if isinstance(tool_choice, str) and tool_choice not in {"none", "auto", "required"}:
        raise ContractError("tool_choice string must be none, auto, or required")
    if not isinstance(tool_choice, (str, Mapping)):
        raise ContractError("tool_choice must be a supported string or object")
    request = _base_request(messages, seed=seed)
    request["tools"] = normalized_tools
    request["tool_choice"] = deepcopy(tool_choice)
    request["parallel_tool_calls"] = False
    return request


def canonical_request_sha256(request: Mapping[str, Any]) -> str:
    """Return a stable hash for preregistration/self-check evidence."""
    if not isinstance(request, Mapping):
        raise ContractError("request must be an object")
    payload = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def contract_snapshot() -> dict[str, Any]:
    """Machine-readable frozen serving fields for provider-free qualification."""
    return {
        "provider": PROVIDER,
        "model_id": MODEL_ID,
        "underlying_model_family": UNDERLYING_MODEL_FAMILY,
        "temperature": TEMPERATURE,
        "reasoning_effort": REASONING_EFFORT,
        "reasoning_format": REASONING_FORMAT,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "stream": False,
        "network_io_implemented": False,
        "credential_access_implemented": False,
    }
