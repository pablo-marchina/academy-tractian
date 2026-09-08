from __future__ import annotations

import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.request


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing:{name}")
    return value


def call(opener, url: str, *, method: str = "GET", payload: dict | None = None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(req, timeout=30) as response:
            raw = response.read()
            decoded = json.loads(raw.decode("utf-8")) if raw else None
            return int(response.status), decoded
    except urllib.error.HTTPError as exc:
        return int(exc.code), None


def main() -> int:
    base = required("TARGET_BASE_URL").rstrip("/")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    signin_status, _ = call(
        opener,
        base + "/auth/sign-in/email",
        method="POST",
        payload={
            "email": required("QA_EMAIL").lower(),
            "password": required("QA_PASSWORD"),
            "rememberMe": True,
        },
    )
    if signin_status != 200:
        print(json.dumps({"schema_version":"production-chat-recovery-probe-v1","status":"FAIL","stage":"signin","http_status":signin_status,"credentials_recorded":False}, sort_keys=True))
        return 1

    submit_status, accepted = call(
        opener,
        base + "/api/runs",
        method="POST",
        payload={
            "user_request": "Do not use tools. Briefly explain that an asset condition cannot be assessed without supporting evidence.",
        },
    )
    if submit_status != 202 or not isinstance(accepted, dict) or not isinstance(accepted.get("run_id"), str):
        print(json.dumps({"schema_version":"production-chat-recovery-probe-v1","status":"FAIL","stage":"submit","http_status":submit_status,"credentials_recorded":False}, sort_keys=True))
        return 1

    run_id = accepted["run_id"]
    execution_status = None
    for _ in range(60):
        status, execution = call(opener, base + f"/api/runs/{run_id}/execution")
        if status == 200 and isinstance(execution, dict):
            execution_status = execution.get("status")
            if execution_status in {"completed", "failed", "interrupted", "uncertain"}:
                break
        time.sleep(0.5)

    detail_status, detail = call(opener, base + f"/api/runs/{run_id}")
    events_status, events_payload = call(opener, base + f"/api/runs/{run_id}/events")
    events = events_payload.get("items") if isinstance(events_payload, dict) and isinstance(events_payload.get("items"), list) else []
    model_events = [item for item in events if isinstance(item, dict) and item.get("event_type") == "model_call"]
    final_events = [item for item in events if isinstance(item, dict) and item.get("event_type") == "final_response"]
    model_event = model_events[-1] if model_events else {}
    final_event = final_events[-1] if final_events else {}

    completed = isinstance(detail, dict) and detail.get("completed") is True
    terminal_message = detail.get("terminal_message") if isinstance(detail, dict) and isinstance(detail.get("terminal_message"), str) else None
    result = {
        "schema_version": "production-chat-recovery-probe-v1",
        "status": "PASS" if execution_status == "completed" and completed and bool(terminal_message) and model_event.get("outcome") == "success" else "FAIL",
        "run_id": run_id,
        "submit_http_status": submit_status,
        "execution_status": execution_status,
        "detail_http_status": detail_status,
        "events_http_status": events_status,
        "completed": completed,
        "terminal_decision": detail.get("terminal_decision") if isinstance(detail, dict) else None,
        "terminal_response_mode": detail.get("terminal_response_mode") if isinstance(detail, dict) else None,
        "terminal_reason_code": detail.get("terminal_reason_code") if isinstance(detail, dict) else None,
        "terminal_message_present": bool(terminal_message),
        "terminal_message": terminal_message,
        "provider_id": model_event.get("provider_id"),
        "model_id": model_event.get("model_id"),
        "model_outcome": model_event.get("outcome"),
        "model_failure_code": model_event.get("failure_code"),
        "final_response_mode": final_event.get("response_mode"),
        "final_reason_code": final_event.get("reason_code"),
        "credentials_recorded": False,
        "raw_provider_material_recorded": False,
    }
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
