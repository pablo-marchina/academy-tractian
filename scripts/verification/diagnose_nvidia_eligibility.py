from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"
MARKER = "ACADEMY-NVIDIA-ELIGIBILITY-20260908"


def main() -> int:
    token = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not token:
        raise RuntimeError("missing:NVIDIA_API_KEY")
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Synthetic provider eligibility probe only. Do not use external or benchmark data."},
            {"role": "user", "content": f"Reply with exactly {MARKER}"},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 64,
        "stream": False,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    status = None
    payload = None
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            status = response.status
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            payload = json.load(exc)
        except Exception:
            payload = None

    served_model = payload.get("model") if isinstance(payload, dict) else None
    choices = payload.get("choices") if isinstance(payload, dict) else None
    content = None
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        if isinstance(message, dict):
            content = message.get("content")
    semantic_ok = isinstance(content, str) and MARKER in content
    model_ok = served_model in (None, MODEL)
    result = "PASS" if status == 200 and semantic_ok and model_ok else "FAIL"
    safe = {
        "schema_version": "nvidia-eligibility-diagnostic-v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "provider_id": "nvidia",
        "route": "integrate.api.nvidia.com/v1/chat/completions",
        "requested_model": MODEL,
        "served_model": served_model,
        "http_status": status,
        "semantic_marker_observed": semantic_ok,
        "model_match": model_ok,
        "benchmark_inputs_loaded": 0,
        "credentials_recorded": False,
        "result": result,
    }
    print(json.dumps(safe, sort_keys=True), flush=True)
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
