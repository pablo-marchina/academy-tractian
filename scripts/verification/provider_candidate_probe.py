from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing_required_env:{name}")
    return value


def _request_config() -> tuple[str, dict[str, str], str]:
    provider = _required("PROVIDER_CANDIDATE_PROVIDER")
    model = _required("PROVIDER_CANDIDATE_MODEL")
    if provider == "cloudflare":
        account_id = _required("ACADEMY_PROVIDER_ACCOUNT_ID")
        token = _required("ACADEMY_PROVIDER_API_TOKEN")
        return (
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            model,
        )
    if provider == "groq":
        token = _required("GROQ_API_KEY")
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            model,
        )
    raise RuntimeError(f"unsupported_candidate_provider:{provider}")


def main() -> None:
    url, headers, model = _request_config()
    schema = {
        "type": "object",
        "properties": {"decision": {"type": "string", "enum": ["PASS"]}},
        "required": ["decision"],
        "additionalProperties": False,
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only data satisfying the supplied JSON schema."},
            {"role": "user", "content": "Return PASS."},
        ],
        "response_format": {"type": "json_schema", "json_schema": schema},
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_completion_tokens": 64,
        "store": False,
        "tool_choice": "none",
        "parallel_tool_calls": False,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read())
            status = response.status
            response_headers = {key.lower(): value for key, value in response.headers.items()}
    except urllib.error.HTTPError as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        error_text = exc.read().decode("utf-8", errors="replace")[:1000]
        print(json.dumps({
            "probe": "provider_candidate_contract_v1",
            "status": exc.code,
            "candidate_provider": os.environ["PROVIDER_CANDIDATE_PROVIDER"],
            "candidate_model": model,
            "latency_ms": elapsed_ms,
            "error_body": error_text,
        }, sort_keys=True))
        raise SystemExit(2)

    elapsed_ms = round((time.perf_counter() - started) * 1000)
    choices = payload.get("choices") if isinstance(payload, dict) else None
    choice = choices[0] if isinstance(choices, list) and choices else {}
    message = choice.get("message") if isinstance(choice, dict) else {}
    content = message.get("content") if isinstance(message, dict) else None
    try:
        decoded = json.loads(content) if isinstance(content, str) else None
    except json.JSONDecodeError:
        decoded = None

    rate_headers = {
        key: value
        for key, value in response_headers.items()
        if key.startswith("x-ratelimit-") or key in {"retry-after"}
    }
    result = {
        "probe": "provider_candidate_contract_v1",
        "status": status,
        "candidate_provider": os.environ["PROVIDER_CANDIDATE_PROVIDER"],
        "candidate_model": model,
        "observed_model": payload.get("model") if isinstance(payload, dict) else None,
        "object": payload.get("object") if isinstance(payload, dict) else None,
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "schema_pass": isinstance(decoded, dict) and decoded.get("decision") == "PASS" and set(decoded) == {"decision"},
        "usage": payload.get("usage") if isinstance(payload, dict) else None,
        "latency_ms": elapsed_ms,
        "rate_limit_headers": rate_headers,
    }
    print(json.dumps(result, sort_keys=True))
    if not result["schema_pass"] or status != 200:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
