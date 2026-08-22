#!/usr/bin/env python3
"""Safe Groq availability preflight for real E14 DEV-only measurement.

This script performs no model inference and never prints the API key. It checks
that the zero-cost guard is enabled and that the configured Groq model is
currently present in the provider Models API before the six fixed E14 DEV calls
are attempted.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_MODEL = "openai/gpt-oss-20b"
MODELS_URL = "https://api.groq.com/openai/v1/models"


def classify_failure(status: int | None, body: str) -> str:
    lowered = body.lower()
    if status in {401, 403}:
        return "authentication_or_authorization_failure"
    if status == 404 or any(term in lowered for term in ("decommission", "deprecated", "model_not_found", "model not found")):
        return "model_unavailable_or_deprecated"
    if status == 429:
        return "provider_rate_limit"
    if status is not None and status >= 500:
        return "provider_server_failure"
    if any(term in lowered for term in ("connection reset", "winerror 10054", "timed out", "temporarily unavailable")):
        return "network_or_transient_provider_failure"
    return "unknown_provider_failure"


def main() -> int:
    model = os.getenv("E8_GROQ_MODEL", DEFAULT_MODEL)
    result = {
        "status": "E14_GROQ_PROVIDER_PREFLIGHT_NEEDS_REVIEW",
        "provider": "groq",
        "model": model,
        "external_model_inference_made": False,
        "api_key_present": bool(os.getenv("GROQ_API_KEY")),
        "zero_cost_confirmed_by_env": os.getenv("E8_CONFIRM_ZERO_COST") == "1",
        "groq_enabled_by_env": os.getenv("E8_ENABLE_GROQ") == "1",
        "http_status": None,
        "failure_category": None,
    }

    if not result["api_key_present"]:
        result["failure_category"] = "missing_groq_api_key"
        print(json.dumps(result, indent=2))
        return 1
    if not result["zero_cost_confirmed_by_env"]:
        result["failure_category"] = "zero_cost_guard_not_confirmed"
        print(json.dumps(result, indent=2))
        return 1
    if not result["groq_enabled_by_env"]:
        result["failure_category"] = "groq_not_enabled"
        print(json.dumps(result, indent=2))
        return 1

    req = urllib.request.Request(
        MODELS_URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "User-Agent": os.getenv("E8_HTTP_USER_AGENT", "academy-tractian-e14-provider-preflight/1.0"),
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            result["http_status"] = int(resp.status)
            models = payload.get("data", []) if isinstance(payload, dict) else []
            match = next((item for item in models if isinstance(item, dict) and item.get("id") == model), None)
            if match is None:
                result["model_active"] = False
                result["failure_category"] = "model_unavailable_or_deprecated"
            else:
                active = match.get("active")
                result["model_active"] = True if active is None else bool(active)
                result["provider_model_id"] = match.get("id", model)
                if result["model_active"]:
                    result["status"] = "E14_GROQ_PROVIDER_PREFLIGHT_PASS"
                    print(json.dumps(result, indent=2))
                    return 0
                result["failure_category"] = "model_inactive"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        result["http_status"] = int(exc.code)
        result["failure_category"] = classify_failure(exc.code, body)
    except Exception as exc:  # safe classification only; raw exception is not printed
        result["failure_category"] = classify_failure(None, str(exc))

    print(json.dumps(result, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
