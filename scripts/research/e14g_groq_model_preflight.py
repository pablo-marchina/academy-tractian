#!/usr/bin/env python3
"""Safe no-inference preflight for the E14g Groq model-selection candidate."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

REQUIRED_MODEL = "openai/gpt-oss-120b"
MODELS_URL = "https://api.groq.com/openai/v1/models"


def main() -> int:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is not set")
    if os.getenv("E8_CONFIRM_ZERO_COST") != "1":
        raise SystemExit("E8_CONFIRM_ZERO_COST=1 is required before E14g")

    request = urllib.request.Request(
        MODELS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "academy-tractian-e14g-preflight/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            http_status = int(response.status)
    except urllib.error.HTTPError as exc:
        print(json.dumps({
            "status": "E14G_GROQ_MODEL_PREFLIGHT_FAILED",
            "requested_model": REQUIRED_MODEL,
            "http_status": int(exc.code),
            "api_key_printed": False,
        }, indent=2))
        return 1

    data = payload.get("data", []) if isinstance(payload, dict) else []
    active_ids = {str(item.get("id")) for item in data if isinstance(item, dict) and item.get("id")}
    active = REQUIRED_MODEL in active_ids
    print(json.dumps({
        "status": "E14G_GROQ_MODEL_PREFLIGHT_PASS" if active else "E14G_GROQ_MODEL_PREFLIGHT_FAILED",
        "requested_model": REQUIRED_MODEL,
        "model_active": active,
        "http_status": http_status,
        "zero_cost_operator_confirmed": True,
        "inference_call_made": False,
        "api_key_printed": False,
    }, indent=2))
    return 0 if active else 1


if __name__ == "__main__":
    raise SystemExit(main())
