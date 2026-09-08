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
    try:
        with opener.open(req, timeout=30) as response:
            raw = response.read()
            decoded = json.loads(raw.decode("utf-8")) if raw else None
            return response.status, decoded
    except urllib.error.HTTPError as exc:
        return int(exc.code), None


def scalar(value):
    return value if isinstance(value, (str, int, float, bool)) or value is None else None


def safe_projection(payload):
    if not isinstance(payload, dict):
        return {"payload_type": type(payload).__name__}
    out = {"top_level_keys": sorted(str(key) for key in payload)}
    safe_exact = {
        "run_id",
        "status",
        "state",
        "phase",
        "outcome",
        "terminal",
        "completed",
        "done",
        "error_code",
        "failure_code",
        "reason_code",
        "error_type",
        "decision_kind",
        "finish_reason",
        "evaluation_status",
        "execution_status",
        "worker_state",
    }
    for key, value in payload.items():
        if key in safe_exact and isinstance(value, (str, int, float, bool, type(None))):
            out[key] = scalar(value)
    for key in ("result", "final", "response", "answer", "assistant_response", "message", "error"):
        if key in payload:
            value = payload[key]
            out[f"has_{key}"] = value not in (None, "", [], {})
            out[f"{key}_type"] = type(value).__name__
            if key == "error" and isinstance(value, dict):
                out["error_fields"] = sorted(str(k) for k in value)
                for nested_key in ("code", "type", "status", "reason_code", "failure_code"):
                    nested = value.get(nested_key)
                    if isinstance(nested, (str, int, float, bool, type(None))):
                        out[f"error_{nested_key}"] = nested
    for key in ("items", "events", "messages", "steps", "turns", "tool_calls"):
        value = payload.get(key)
        if isinstance(value, list):
            out[f"{key}_count"] = len(value)
    return out


def main() -> int:
    product = required("TARGET_BASE_URL").rstrip("/")
    run_id = required("DIAGNOSTIC_RUN_IDS").split(",", 1)[0].strip()
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

    endpoints = {
        "run": f"/api/runs/{urllib.parse.quote(run_id)}",
        "execution": f"/api/runs/{urllib.parse.quote(run_id)}/execution",
        "evaluation": f"/api/runs/{urllib.parse.quote(run_id)}/evaluation",
    }
    output = {"schema_version": "safe-run-state-diagnostic-v1", "run_id": run_id, "credentials_recorded": False}
    for name, path in endpoints.items():
        http_status, payload = request(opener, product + path)
        output[name] = {"http_status": http_status, **safe_projection(payload)}
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
