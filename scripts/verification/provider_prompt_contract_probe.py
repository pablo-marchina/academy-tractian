from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Mapping

from academy_tractian.decision_source import ProviderDecisionPayload, build_provider_decision_request
from academy_tractian.provider_clients import PROVIDER_DECISION_JSON_SCHEMA, PROVIDER_DECISION_SYSTEM_INSTRUCTION
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext

SCHEMA_VERSION = "provider-prompt-contract-probe-v3"
SYNTHETIC_ASSET_ID = "asset_prompt_probe_001"
EXPECTED_TOOL = "get_asset"
PROVIDERS = {
    "groq": {
        "token_env": "GROQ_API_KEY",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "model": "openai/gpt-oss-120b",
    },
    "nvidia": {
        "token_env": "NVIDIA_API_KEY",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "nvidia/nemotron-3-super-120b-a12b",
    },
    "openrouter": {
        "token_env": "OPENROUTER_API_KEY",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
    },
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def safe_error(payload: Any) -> dict[str, str]:
    if not isinstance(payload, Mapping) or not isinstance(payload.get("error"), Mapping):
        return {}
    error = payload["error"]
    return {
        key: str(error[key])[:500]
        for key in ("type", "code", "message")
        if error.get(key) is not None
    }


def _json_schema_response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "provider_decision_payload",
            "strict": False,
            "schema": json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA)),
        },
    }


def request_body(provider_id: str, model: str, request_text: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION},
            {"role": "user", "content": request_text},
        ],
        "temperature": 0,
        "n": 1,
        "stream": False,
    }

    if provider_id == "groq":
        body.update(
            {
                "max_completion_tokens": 512,
                "reasoning_effort": "medium",
                "response_format": _json_schema_response_format(),
            }
        )
    elif provider_id == "nvidia":
        # Live catalog discovery is authoritative for this credential. The
        # currently served Nemotron 3 Super route and NVIDIA's hosted examples
        # both use max_tokens plus chat_template_kwargs.enable_thinking.
        # Reasoning is disabled for this contract probe because the application
        # requires exactly one final JSON payload and owns all strict validation.
        body.update(
            {
                "max_tokens": 512,
                "top_p": 1,
                "chat_template_kwargs": {"enable_thinking": False},
            }
        )
    elif provider_id == "openrouter":
        # require_parameters deliberately fails closed when the selected route
        # cannot honor the exact request. Nemotron 3 Super advertises max_tokens,
        # not max_completion_tokens, through OpenRouter's route capability data.
        body.update(
            {
                "max_tokens": 512,
                "response_format": _json_schema_response_format(),
                "provider": {
                    "require_parameters": True,
                    "allow_fallbacks": False,
                },
            }
        )
    else:
        raise RuntimeError(f"unsupported_provider:{provider_id}")
    return body


def extract_response(payload: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "content": None,
        "served_model": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "choices_count": None,
        "finish_reason": None,
        "message_content_present": False,
    }
    if not isinstance(payload, Mapping):
        return result

    if isinstance(payload.get("model"), str):
        result["served_model"] = payload["model"]

    choices = payload.get("choices")
    if isinstance(choices, list):
        result["choices_count"] = len(choices)
        if len(choices) == 1 and isinstance(choices[0], Mapping):
            choice = choices[0]
            if isinstance(choice.get("finish_reason"), str):
                result["finish_reason"] = choice["finish_reason"]
            message = choice.get("message")
            if isinstance(message, Mapping) and isinstance(message.get("content"), str):
                result["content"] = message["content"]
                result["message_content_present"] = bool(message["content"].strip())

    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    for source, target in (
        ("prompt_tokens", "prompt_tokens"),
        ("completion_tokens", "completion_tokens"),
        ("total_tokens", "total_tokens"),
    ):
        value = usage.get(source)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            result[target] = value
    return result


def main() -> int:
    provider_id = os.environ.get("PROVIDER_PROMPT_PROBE_PROVIDER", "").strip().lower()
    if provider_id not in PROVIDERS:
        raise RuntimeError("PROVIDER_PROMPT_PROBE_PROVIDER must be groq, nvidia, or openrouter")

    config = PROVIDERS[provider_id]
    token = os.environ.get(config["token_env"], "").strip()
    if not token:
        raise RuntimeError(f"missing:{config['token_env']}")

    registry = canonical_tool_registry()
    if EXPECTED_TOOL not in registry:
        raise RuntimeError(f"missing_canonical_tool:{EXPECTED_TOOL}")

    context = ControllerContext(
        user_request=(
            "Synthetic provider-contract probe only; no industrial benchmark data is present. "
            f"Propose the canonical {EXPECTED_TOOL} tool with asset_id exactly "
            f"{SYNTHETIC_ASSET_ID!r}. Do not execute the tool."
        ),
        turn_index=0,
        tool_call_count=0,
    )
    decision_request = build_provider_decision_request(context=context, registry=registry)
    body = request_body(
        provider_id,
        config["model"],
        canonical_json(decision_request.model_dump(mode="json")),
    )
    request = urllib.request.Request(
        config["endpoint"],
        data=canonical_json(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "academy-tractian-provider-prompt-contract-probe/3.0",
        },
    )

    started = time.perf_counter_ns()
    raw = ""
    headers: dict[str, str] = {}
    status: int | None = None
    transport_error: str | None = None
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            status = int(response.status)
            raw = response.read().decode("utf-8", errors="replace")
            headers = {key.casefold(): value for key, value in response.headers.items()}
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8", errors="replace")
        headers = {key.casefold(): value for key, value in exc.headers.items()}
    except Exception as exc:
        transport_error = type(exc).__name__

    latency_ms = max(0, time.perf_counter_ns() - started) // 1_000_000
    try:
        payload: Any = json.loads(raw) if raw else {}
    except Exception:
        payload = {}

    extracted = extract_response(payload)
    parsed: ProviderDecisionPayload | None = None
    parse_ok = False
    semantic_ok = False
    content = extracted["content"]
    if isinstance(content, str) and content.strip():
        try:
            parsed = ProviderDecisionPayload.model_validate_json(content)
            parse_ok = True
            semantic_ok = (
                parsed.kind.value == "TOOL"
                and parsed.tool_name == EXPECTED_TOOL
                and parsed.arguments.get("asset_id") == SYNTHETIC_ASSET_ID
                and parsed.final is None
                and parsed.message is None
                and parsed.reason_code is None
            )
        except Exception:
            pass

    rate_headers = {
        key: value
        for key, value in headers.items()
        if key.startswith("x-ratelimit-") or key in {"retry-after", "date"}
    }
    result = "PASS" if status == 200 and parse_ok and semantic_ok else "FAIL"
    report = {
        "schema_version": SCHEMA_VERSION,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "provider_id": provider_id,
        "route": config["endpoint"].replace("https://", ""),
        "requested_model": config["model"],
        "served_model": extracted["served_model"],
        "http_status": status,
        "latency_ms": latency_ms,
        "choices_count": extracted["choices_count"],
        "finish_reason": extracted["finish_reason"],
        "message_content_present": extracted["message_content_present"],
        "provider_decision_parse_ok": parse_ok,
        "synthetic_semantic_contract_ok": semantic_ok,
        "decision_kind": parsed.kind.value if parsed else None,
        "decision_tool_name": parsed.tool_name if parsed else None,
        "prompt_tokens": extracted["prompt_tokens"],
        "completion_tokens": extracted["completion_tokens"],
        "total_tokens": extracted["total_tokens"],
        "rate_headers": rate_headers,
        "error": safe_error(payload),
        "transport_error_type": transport_error,
        "benchmark_inputs_loaded": 0,
        "raw_provider_material_recorded": False,
        "credentials_recorded": False,
        "result": result,
    }
    print("PROVIDER_PROMPT_CONTRACT_PROBE=" + canonical_json(report), flush=True)
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
