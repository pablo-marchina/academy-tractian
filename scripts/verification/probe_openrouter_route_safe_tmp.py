from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def main() -> int:
    token = os.environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("missing:ACADEMY_PROVIDER_API_TOKEN")
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Synthetic compatibility check only. Return only the requested JSON."},
            {"role": "user", "content": "Return {\"ok\":true}."},
        ],
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_tokens": 1024,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "safe_probe",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"ok": {"type": "boolean", "const": True}},
                    "required": ["ok"],
                    "additionalProperties": False,
                },
            },
        },
        "provider": {"allow_fallbacks": False, "require_parameters": True},
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    status = None
    decoded = None
    transport_error = None
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            status = int(response.status)
            raw = response.read()
            try:
                decoded = json.loads(raw.decode("utf-8"))
            except Exception:
                decoded = None
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        transport_error = "HTTP_ERROR"
    except Exception as exc:
        transport_error = type(exc).__name__

    choice = None
    if isinstance(decoded, dict):
        choices = decoded.get("choices")
        if isinstance(choices, list) and len(choices) == 1 and isinstance(choices[0], dict):
            choice = choices[0]
    message = choice.get("message") if isinstance(choice, dict) and isinstance(choice.get("message"), dict) else {}
    content = message.get("content") if isinstance(message, dict) else None
    content_complete_object = False
    if isinstance(content, str) and content.strip():
        try:
            content_complete_object = isinstance(json.loads(content), dict)
        except Exception:
            content_complete_object = False
    usage = decoded.get("usage") if isinstance(decoded, dict) and isinstance(decoded.get("usage"), dict) else {}
    details = usage.get("completion_tokens_details") if isinstance(usage.get("completion_tokens_details"), dict) else {}
    result = {
        "schema_version": "openrouter-route-safe-probe-v1",
        "http_status": status,
        "transport_error": transport_error,
        "served_model_matches": isinstance(decoded, dict) and decoded.get("model") == MODEL,
        "choices_count": len(decoded.get("choices")) if isinstance(decoded, dict) and isinstance(decoded.get("choices"), list) else None,
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) and isinstance(choice.get("finish_reason"), str) else None,
        "content_present": isinstance(content, str) and bool(content.strip()),
        "content_complete_object": content_complete_object,
        "prompt_tokens": usage.get("prompt_tokens") if isinstance(usage.get("prompt_tokens"), int) else None,
        "completion_tokens": usage.get("completion_tokens") if isinstance(usage.get("completion_tokens"), int) else None,
        "reasoning_tokens": details.get("reasoning_tokens") if isinstance(details.get("reasoning_tokens"), int) else None,
        "error_object_present": isinstance(decoded, dict) and decoded.get("error") is not None,
        "credentials_recorded": False,
        "raw_request_recorded": False,
        "raw_response_recorded": False,
    }
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
