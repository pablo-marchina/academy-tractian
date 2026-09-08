from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

MODEL = "@cf/zai-org/glm-4.7-flash"


def main() -> int:
    token = os.environ.get("TOURNAMENT_CLOUDFLARE_API_TOKEN", "").strip()
    account_id = os.environ.get("TOURNAMENT_CLOUDFLARE_ACCOUNT_ID", "").strip()
    if not token or not account_id:
        raise RuntimeError("missing:cloudflare_credentials")
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions"
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Synthetic compatibility check only. Return only the requested JSON."},
            {"role": "user", "content": "Return {\"ok\":true}."},
        ],
        "temperature": 0,
        "n": 1,
        "stream": False,
        "max_completion_tokens": 512,
        "store": False,
        "tool_choice": "none",
        "parallel_tool_calls": False,
        "reasoning_effort": None,
        "chat_template_kwargs": {"enable_thinking": False},
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
    }
    req = urllib.request.Request(
        endpoint,
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
    complete = False
    if isinstance(content, str) and content.strip():
        try:
            complete = isinstance(json.loads(content), dict)
        except Exception:
            complete = False
    result = {
        "schema_version": "cloudflare-route-safe-probe-v1",
        "http_status": status,
        "transport_error": transport_error,
        "served_model_matches": isinstance(decoded, dict) and decoded.get("model") == MODEL,
        "object": decoded.get("object") if isinstance(decoded, dict) and isinstance(decoded.get("object"), str) else None,
        "choices_count": len(decoded.get("choices")) if isinstance(decoded, dict) and isinstance(decoded.get("choices"), list) else None,
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) and isinstance(choice.get("finish_reason"), str) else None,
        "content_present": isinstance(content, str) and bool(content.strip()),
        "content_complete_object": complete,
        "credentials_recorded": False,
        "raw_request_recorded": False,
        "raw_response_recorded": False,
    }
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
