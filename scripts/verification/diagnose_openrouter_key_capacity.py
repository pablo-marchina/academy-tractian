from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone

OPENROUTER_KEY_URL = "https://openrouter.ai/api/v1/key"
REQUIRED_CAPACITY = 85
FREE_TIER_DAILY_CAPACITY = 50
CREDIT_BACKED_FREE_MODEL_DAILY_CAPACITY = 1000


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing:{name}")
    return value


def main() -> int:
    token = required("ACADEMY_PROVIDER_API_TOKEN")
    req = urllib.request.Request(
        OPENROUTER_KEY_URL,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise RuntimeError("openrouter_key_payload_invalid")

    is_free_tier = data.get("is_free_tier")
    if not isinstance(is_free_tier, bool):
        raise RuntimeError("openrouter_key_missing_is_free_tier")

    published_daily_capacity = (
        FREE_TIER_DAILY_CAPACITY if is_free_tier else CREDIT_BACKED_FREE_MODEL_DAILY_CAPACITY
    )
    result = "PASS" if published_daily_capacity >= REQUIRED_CAPACITY else "FAIL"

    safe = {
        "schema_version": "openrouter-key-capacity-diagnostic-v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "provider_id": "openrouter",
        "required_capacity": REQUIRED_CAPACITY,
        "is_free_tier": is_free_tier,
        "published_free_model_daily_capacity": published_daily_capacity,
        "capacity_basis": (
            "OpenRouter published free-model account limit: 50 requests/day on free tier; "
            "1000 requests/day after >=10 purchased credits."
        ),
        "key_limit_present": data.get("limit") is not None,
        "key_limit_remaining": data.get("limit_remaining"),
        "key_limit_reset": data.get("limit_reset"),
        "usage_daily": data.get("usage_daily"),
        "rate_limit_metadata": data.get("rate_limit"),
        "result": result,
        "credentials_recorded": False,
        "key_label_recorded": False,
        "creator_identity_recorded": False,
    }
    print(json.dumps(safe, sort_keys=True), flush=True)
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
