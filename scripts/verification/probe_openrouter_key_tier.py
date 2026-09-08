from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def main() -> int:
    token = os.environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("missing:ACADEMY_PROVIDER_API_TOKEN")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    status = None
    payload = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = int(response.status)
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
    data = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else {}
    is_free_tier = data.get("is_free_tier") if isinstance(data.get("is_free_tier"), bool) else None
    print(json.dumps({
        "schema_version": "openrouter-key-tier-probe-v1",
        "request_succeeded": status == 200,
        "http_status": status,
        "is_free_tier": is_free_tier,
        "credentials_recorded": False,
        "credit_balance_recorded": False,
        "usage_amount_recorded": False,
    }, sort_keys=True), flush=True)
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
