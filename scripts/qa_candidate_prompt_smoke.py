from __future__ import annotations

import http.cookiejar
import json
import os
import re
import time
import urllib.error
import urllib.request

AUTH_BASE = os.environ["AUTH_BASE_URL"].rstrip("/")
API_BASE = os.environ["TARGET_API_BASE_URL"].rstrip("/")
EMAIL = os.environ["QA_EMAIL"]
PASSWORD = os.environ["QA_PASSWORD"]
EXPECTED_SHA = os.environ["EXPECTED_RELEASE_SHA"].strip().lower()

CASES = [
    {
        "id": "G01",
        "prompt": "Analise o RMS do M101.",
        "required_tools": ["get_current_user", "list_assets_by_company", "get_rms"],
        "required_asset_ids": ["asset_M101"],
        "forbidden_argument_asset_ids": ["M101"],
    },
    {
        "id": "G05",
        "prompt": "Compare M101 com H110 usando RMS e espectro; busque agora e não me diga que fará depois.",
        "required_tools": ["get_current_user", "list_assets_by_company", "get_rms", "get_spectrum"],
        "required_asset_ids": ["asset_M101", "asset_H110"],
        "forbidden_argument_asset_ids": ["M101", "H110"],
        "require_each_asset_for_tools": ["get_rms", "get_spectrum"],
    },
    {
        "id": "K01",
        "prompt": "Consulte a base de conhecimento e encontre orientação sobre como interpretar vibração anormal em um ativo como o M101. Busque agora.",
        "required_tools": ["search_knowledge"],
        "required_asset_ids": [],
        "forbidden_argument_asset_ids": [],
    },
]

jar = http.cookiejar.CookieJar()
auth_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def _decode(raw: bytes):
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text) if text else None
    except Exception:
        return {"raw": text[:2000]}


def request(base, path, method="GET", payload=None, timeout=45, cookie=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "User-Agent": "academy-tractian-candidate-smoke/2",
        "Origin": AUTH_BASE,
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    opener = auth_opener if base == AUTH_BASE else urllib.request.build_opener()
    try:
        with opener.open(req, timeout=timeout) as resp:
            return int(resp.status), _decode(resp.read())
    except urllib.error.HTTPError as exc:
        return int(exc.code), _decode(exc.read())
    except Exception as exc:
        return 0, {"error": type(exc).__name__, "message": str(exc)[:1000]}


signup_status, _ = request(
    AUTH_BASE,
    "/auth/sign-up/email",
    "POST",
    {"email": EMAIL, "password": PASSWORD, "name": "QA Candidate V14"},
)
if signup_status in (200, 201):
    auth_status = signup_status
    auth_phase = "signup"
else:
    auth_status, _ = request(
        AUTH_BASE,
        "/auth/sign-in/email",
        "POST",
        {"email": EMAIL, "password": PASSWORD, "rememberMe": True},
    )
    auth_phase = "signin"
print(json.dumps({"phase": "auth", "mode": auth_phase, "status": auth_status}), flush=True)
if auth_status not in (200, 201):
    raise SystemExit(20)

session_status, session_body = request(AUTH_BASE, "/auth/get-session?disableCookieCache=true")
if session_status != 200 or not isinstance(session_body, dict) or not session_body.get("user"):
    print(json.dumps({"phase": "session", "status": session_status, "body": session_body}), flush=True)
    raise SystemExit(21)

cookie = "; ".join(f"{c.name}={c.value}" for c in jar)
if not cookie:
    raise SystemExit(22)
print(
    json.dumps(
        {"phase": "session", "status": session_status, "cookie_count": sum(1 for _ in jar)}
    ),
    flush=True,
)

cap_status, cap = request(API_BASE, "/api/release0/capabilities", cookie=cookie, timeout=30)
actual_sha = None
if isinstance(cap, dict):
    release = cap.get("release")
    if isinstance(release, dict):
        actual_sha = release.get("git_sha")
print(
    json.dumps(
        {
            "phase": "candidate_identity",
            "status": cap_status,
            "expected_sha": EXPECTED_SHA,
            "actual_sha": actual_sha,
        }
    ),
    flush=True,
)
if cap_status != 200 or actual_sha != EXPECTED_SHA:
    raise SystemExit(23)

FUTURE = re.compile(
    r"\b(vou\s+(?:buscar|consultar|verificar|analisar)|aguarde|please\s+wait|i(?:'ll| will)\s+(?:fetch|check|look))\b",
    re.I,
)
ASK_ID = re.compile(
    r"(forne[cç]a|informe|provide|send).{0,80}\b(asset_id|analysis_id|model_id|company_id)\b|\b(asset_id|analysis_id|model_id|company_id)\b.{0,80}(necess[aá]rio|required|need)",
    re.I | re.S,
)
ACTION_TOOLS = {
    "update_asset_config",
    "reprocess_analysis",
    "request_specialist_analysis",
    "request_retraining",
    "escalate_case",
}


def event_items(run_id):
    status, body = request(API_BASE, f"/api/runs/{run_id}/events", cookie=cookie, timeout=30)
    items = body.get("items") if status == 200 and isinstance(body, dict) else None
    return status, items if isinstance(items, list) else []


def tool_calls(events):
    out = []
    for event in events:
        if not isinstance(event, dict) or event.get("event_type") != "tool_call":
            continue
        out.append(
            {
                "seq": event.get("sequence"),
                "tool": event.get("tool_name"),
                "args": event.get("arguments") or {},
            }
        )
    return out


def successful_duplicate_fingerprints(events):
    successful = set()
    duplicates = []
    pending = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = event.get("event_type")
        tool = event.get("tool_name")
        if event_type == "tool_call":
            arguments = event.get("arguments") or {}
            fingerprint = json.dumps(
                [tool, arguments], sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            if fingerprint in successful:
                duplicates.append(fingerprint)
            pending[tool] = fingerprint
        elif event_type == "tool_result":
            metadata = event.get("metadata") or {}
            result = event.get("result") or {}
            status_code = metadata.get(
                "status_code",
                result.get("status_code") if isinstance(result, dict) else None,
            )
            fingerprint = pending.get(tool)
            if fingerprint and isinstance(status_code, int) and 200 <= status_code < 300:
                successful.add(fingerprint)
    return duplicates


results = []
for case in CASES:
    started = time.time()
    submit_status, accepted = request(
        API_BASE,
        "/api/runs",
        "POST",
        {"user_request": case["prompt"]},
        timeout=45,
        cookie=cookie,
    )
    run_id = accepted.get("run_id") if isinstance(accepted, dict) else None
    if submit_status != 202 or not run_id:
        item = {
            "case_id": case["id"],
            "status": "FAIL_AVAILABILITY",
            "submit_status": submit_status,
            "detail": accepted,
            "elapsed_s": round(time.time() - started, 2),
        }
        results.append(item)
        print(json.dumps({"phase": "case", **item}, ensure_ascii=False), flush=True)
        continue

    execution_state = None
    execution_http_status = 0
    auth_503_count = 0
    for _ in range(120):
        time.sleep(1)
        execution_http_status, execution_body = request(
            API_BASE,
            f"/api/runs/{run_id}/execution",
            cookie=cookie,
            timeout=25,
        )
        if execution_http_status == 503:
            auth_503_count += 1
            continue
        if execution_http_status == 200 and isinstance(execution_body, dict):
            execution_state = execution_body.get("status")
            if execution_state in {"completed", "failed"}:
                break
        elif execution_http_status in (401, 403, 404, 0):
            break

    run_status, run_body = request(API_BASE, f"/api/runs/{run_id}", cookie=cookie, timeout=30)
    run = run_body if run_status == 200 and isinstance(run_body, dict) else None
    events_status, events = event_items(run_id)
    calls = tool_calls(events)
    tool_names = [call["tool"] for call in calls if isinstance(call.get("tool"), str)]

    terminal = ""
    terminal_mode = None
    if isinstance(run, dict):
        terminal = str(run.get("terminal_message") or "")
        terminal_mode = run.get("terminal_response_mode")
    if not terminal:
        for event in events:
            if (
                isinstance(event, dict)
                and event.get("event_type") == "final_response"
                and isinstance(event.get("result"), dict)
            ):
                terminal = str(event["result"].get("message") or "")
                terminal_mode = terminal_mode or event["result"].get("response_mode")

    errors = []
    if execution_state != "completed":
        errors.append(f"execution_state:{execution_state or execution_http_status}")
    if run_status != 200:
        errors.append(f"run_status_{run_status}")
    if events_status != 200:
        errors.append(f"events_status_{events_status}")
    missing = [tool for tool in case.get("required_tools", []) if tool not in tool_names]
    if missing:
        errors.append("missing_tools:" + ",".join(missing))

    argument_asset_ids = []
    for call in calls:
        arguments = call.get("args")
        if isinstance(arguments, dict) and isinstance(arguments.get("asset_id"), str):
            argument_asset_ids.append((call["tool"], arguments["asset_id"]))

    for forbidden in case.get("forbidden_argument_asset_ids", []):
        if any(asset_id == forbidden for _, asset_id in argument_asset_ids):
            errors.append("noncanonical_asset_id:" + forbidden)
    for required in case.get("required_asset_ids", []):
        if not any(asset_id == required for _, asset_id in argument_asset_ids):
            errors.append("canonical_asset_not_used:" + required)
    for tool in case.get("require_each_asset_for_tools", []):
        for asset in case.get("required_asset_ids", []):
            if not any(t == tool and asset_id == asset for t, asset_id in argument_asset_ids):
                errors.append(f"missing_{tool}_for_{asset}")

    duplicates = successful_duplicate_fingerprints(events)
    if duplicates:
        errors.append("successful_exact_read_duplicate")
    if any(tool in ACTION_TOOLS for tool in tool_names):
        errors.append("unexpected_action_tool")
    if FUTURE.search(terminal):
        errors.append("promised_future_work")
    if ASK_ID.search(terminal):
        errors.append("asked_for_discoverable_id")

    status = (
        "PASS"
        if not errors and auth_503_count == 0
        else (
            "FAIL_AVAILABILITY"
            if auth_503_count or execution_state != "completed"
            else "FAIL_FUNCTIONAL"
        )
    )
    item = {
        "case_id": case["id"],
        "status": status,
        "run_id": run_id,
        "submit_status": submit_status,
        "execution_http_status": execution_http_status,
        "execution_state": execution_state,
        "run_status": run_status,
        "auth_503_count": auth_503_count,
        "events_status": events_status,
        "tool_sequence": tool_names,
        "tool_asset_ids": argument_asset_ids,
        "terminal_mode": terminal_mode,
        "terminal_message": terminal[:1200],
        "errors": errors,
        "elapsed_s": round(time.time() - started, 2),
    }
    results.append(item)
    print(json.dumps({"phase": "case", **item}, ensure_ascii=False), flush=True)

summary = {
    "phase": "summary",
    "total": len(results),
    "pass": sum(result["status"] == "PASS" for result in results),
    "fail_functional": sum(result["status"] == "FAIL_FUNCTIONAL" for result in results),
    "fail_availability": sum(result["status"] == "FAIL_AVAILABILITY" for result in results),
    "all_pass": all(result["status"] == "PASS" for result in results),
}
print(json.dumps(summary, ensure_ascii=False), flush=True)
raise SystemExit(0 if summary["all_pass"] else 30)
