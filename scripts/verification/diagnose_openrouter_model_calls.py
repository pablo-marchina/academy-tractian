from __future__ import annotations

import http.cookiejar
import json
import os
import urllib.parse
import urllib.request


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing:{name}")
    return value


def request(opener, url: str, *, method: str = "GET", payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with opener.open(req, timeout=30) as response:
        raw = response.read()
        return response.status, json.loads(raw.decode("utf-8")) if raw else None


def main() -> int:
    product = required("TARGET_BASE_URL").rstrip("/")
    run_ids = [value.strip() for value in required("DIAGNOSTIC_RUN_IDS").split(",") if value.strip()]
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    status, _ = request(
        opener,
        f"{product}/auth/sign-in/email",
        method="POST",
        payload={
            "email": required("QA_EMAIL").lower(),
            "password": required("QA_PASSWORD"),
            "rememberMe": True,
        },
    )
    if status != 200:
        raise RuntimeError(f"signin:http_{status}")

    output = []
    allow = {
        "provider_id", "model_id", "route_id", "live_call", "outcome",
        "decision_kind", "failure_code", "latency_ms", "adapter_client_invocations",
        "adapter_retry_count", "adapter_fallback_used", "raw_request_recorded",
        "raw_response_recorded", "exception_text_recorded", "turn_index", "tool_call_count",
    }
    for run_id in run_ids:
        status, payload = request(opener, f"{product}/api/runs/{urllib.parse.quote(run_id)}/events")
        if status != 200 or not isinstance(payload, dict):
            output.append({"run_id": run_id, "status": f"http_{status}"})
            continue
        items = payload.get("items") if isinstance(payload.get("items"), list) else []
        calls = []
        for event in items:
            if not isinstance(event, dict) or event.get("event_type") != "model_call":
                continue
            metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            calls.append({key: metadata.get(key) for key in sorted(allow) if key in metadata})
        output.append({"run_id": run_id, "model_calls": calls})
    print(json.dumps({"schema_version": "openrouter-model-call-diagnostic-v1", "runs": output, "credentials_recorded": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
