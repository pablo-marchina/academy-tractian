from __future__ import annotations

import http.cookiejar
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Case:
    case_id: str
    prompt: str
    required_tools: tuple[str, ...] = ()
    required_any: tuple[str, ...] = ()
    forbidden_terminal_fragments: tuple[str, ...] = ()
    allowed_response_modes: tuple[str, ...] = ("complete", "partial", "inconclusive", "conflict", "unavailable")


def _validated_asset_label(value: str) -> str:
    label = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", label):
        raise RuntimeError("invalid QA_ASSET_LABEL")
    return label


def _cases(asset_label: str) -> tuple[Case, ...]:
    return (
        Case(
            case_id="F01_EXPLICIT_ASSET_CONDITION",
            prompt=f"For asset {asset_label}, explain its current condition and what evidence supports that conclusion. Do not ask me for internal IDs that the system can discover.",
            required_tools=("get_current_user", "list_assets_by_company"),
            required_any=("get_analysis", "get_rms", "get_spectrum"),
            forbidden_terminal_fragments=("company_id", "asset_id"),
        ),
        Case(
            case_id="F02_EXPLICIT_ASSET_CAUSAL",
            prompt=f"Why is {asset_label} vibrating more than usual? Identify the most likely mechanism only if the available evidence supports it, and state what remains uncertain.",
            required_tools=("get_current_user", "list_assets_by_company"),
            required_any=("get_rms", "get_spectrum", "get_analysis"),
            forbidden_terminal_fragments=("company_id", "asset_id"),
        ),
        Case(
            case_id="F03_DATA_QUALITY",
            prompt=f"Check the data quality for {asset_label} and tell me whether the available measurements are reliable enough to use for a maintenance decision.",
            required_tools=("get_current_user", "list_assets_by_company", "get_data_quality"),
            forbidden_terminal_fragments=("company_id", "asset_id"),
        ),
    )


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _origin(value: str) -> str:
    return value.rstrip("/")


def _json_request(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> tuple[int, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
            decoded = json.loads(raw.decode("utf-8")) if raw else None
            return int(response.status), decoded
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            decoded = json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            decoded = None
        return int(exc.code), decoded


def _signin(opener: urllib.request.OpenerDirector, product_origin: str) -> None:
    status, _ = _json_request(
        opener,
        f"{product_origin}/auth/sign-in/email",
        method="POST",
        payload={
            "email": _required("QA_EMAIL").strip().lower(),
            "password": _required("QA_PASSWORD"),
            "rememberMe": True,
        },
    )
    if status != 200:
        raise RuntimeError(f"qa sign-in failed: http_{status}")
    status, session = _json_request(
        opener,
        f"{product_origin}/auth/get-session?disableCookieCache=true",
    )
    if status != 200 or not isinstance(session, dict) or not isinstance(session.get("user"), dict):
        raise RuntimeError(f"qa session validation failed: http_{status}")


def _assert_release(opener: urllib.request.OpenerDirector, api_origin: str) -> str:
    expected = _required("EXPECTED_RELEASE_SHA")
    status, payload = _json_request(opener, f"{api_origin}/api/release0/capabilities")
    if status != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"release identity unavailable: http_{status}")
    release = payload.get("release")
    actual = release.get("git_sha") if isinstance(release, dict) else None
    if actual != expected:
        raise RuntimeError("release identity mismatch")
    return expected


def _wait_for_run(
    opener: urllib.request.OpenerDirector,
    product_origin: str,
    accepted: dict[str, Any],
    *,
    deadline_s: float = 120.0,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    execution_path = str(accepted["execution_path"])
    run_path = str(accepted["run_path"])
    deadline = time.monotonic() + deadline_s
    last_execution_status = "accepted"
    while time.monotonic() < deadline:
        status, execution = _json_request(opener, f"{product_origin}{execution_path}")
        if status != 200 or not isinstance(execution, dict):
            raise RuntimeError(f"execution polling failed: http_{status}")
        last_execution_status = str(execution.get("status"))
        if last_execution_status in {"completed", "failed"}:
            break
        time.sleep(1.0)
    else:
        raise RuntimeError("execution polling timed out")

    status, run = _json_request(opener, f"{product_origin}{run_path}")
    if status != 200 or not isinstance(run, dict):
        raise RuntimeError(f"run fetch failed: http_{status}")
    status, event_payload = _json_request(
        opener,
        f"{product_origin}/api/runs/{urllib.parse.quote(str(accepted['run_id']))}/events",
    )
    if status != 200 or not isinstance(event_payload, dict) or not isinstance(event_payload.get("items"), list):
        raise RuntimeError(f"event fetch failed: http_{status}")
    run["_execution_status"] = last_execution_status
    return run, [item for item in event_payload["items"] if isinstance(item, dict)]


def _evaluate(case: Case, run: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    tools = [
        str(event.get("tool_name"))
        for event in events
        if event.get("event_type") == "tool_call" and event.get("tool_name")
    ]
    failures: list[str] = []
    if run.get("_execution_status") != "completed":
        failures.append(f"execution:{run.get('_execution_status')}")
    if run.get("completed") is not True:
        failures.append("run_not_completed")
    for required_tool in case.required_tools:
        if required_tool not in tools:
            failures.append(f"missing_tool:{required_tool}")
    if case.required_any and not any(tool in tools for tool in case.required_any):
        failures.append("missing_required_evidence_tool")
    response_mode = run.get("terminal_response_mode")
    if response_mode not in case.allowed_response_modes:
        failures.append(f"unexpected_response_mode:{response_mode}")
    terminal = str(run.get("terminal_message") or "").lower()
    for fragment in case.forbidden_terminal_fragments:
        if fragment.lower() in terminal:
            failures.append(f"forbidden_terminal_fragment:{fragment}")
    reason = run.get("terminal_reason_code")
    if reason in {"DECISION_SOURCE_FAILURE", "TOOL_BOUNDARY_FAILURE", "TOOL_CALL_BUDGET_EXHAUSTED", "TURN_BUDGET_EXHAUSTED"}:
        failures.append(f"runtime_failure:{reason}")

    seen: dict[tuple[str, str, int | None], int] = {}
    for event in events:
        if event.get("event_type") != "tool_result" or not event.get("tool_name"):
            continue
        key = (str(event.get("tool_name")), str(event.get("argument_names") or ""), event.get("status_code"))
        seen[key] = seen.get(key, 0) + 1
    repeated_failures = [key for key, count in seen.items() if count >= 2 and isinstance(key[2], int) and key[2] >= 400]
    if repeated_failures:
        failures.append("non_progress_repeated_failed_call")

    return {
        "case_id": case.case_id,
        "run_id": run.get("run_id"),
        "status": "PASS" if not failures else "FAIL",
        "tool_sequence": tools,
        "response_mode": response_mode,
        "reason_code": reason,
        "failures": failures,
    }


def main() -> int:
    product_origin = _origin(_required("TARGET_BASE_URL"))
    api_origin = _origin(os.environ.get("TARGET_API_BASE_URL", "").strip() or product_origin)
    asset_label = _validated_asset_label(_required("QA_ASSET_LABEL"))
    cases = _cases(asset_label)
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    try:
        release_sha = _assert_release(opener, api_origin)
        _signin(opener, product_origin)
    except Exception as exc:
        print(json.dumps({"schema_version": "live-functional-campaign-v2", "status": "BLOCKED", "reason": type(exc).__name__}, sort_keys=True))
        return 2

    results: list[dict[str, Any]] = []
    for case in cases:
        try:
            status, accepted = _json_request(
                opener,
                f"{product_origin}/api/runs",
                method="POST",
                payload={"user_request": case.prompt},
            )
            if status != 202 or not isinstance(accepted, dict) or not accepted.get("run_id"):
                results.append({"case_id": case.case_id, "status": "FAIL", "failures": [f"submit_http_{status}"]})
                continue
            run, events = _wait_for_run(opener, product_origin, accepted)
            results.append(_evaluate(case, run, events))
        except Exception as exc:
            results.append({"case_id": case.case_id, "status": "FAIL", "failures": [type(exc).__name__]})

    passed = sum(item.get("status") == "PASS" for item in results)
    summary = {
        "schema_version": "live-functional-campaign-v2",
        "campaign": os.environ.get("QA_RUN_REV", "FINAL-V1-2026-09-08"),
        "release_sha": release_sha,
        "asset_label": asset_label,
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "all_pass": passed == len(results),
        "results": results,
        "credentials_recorded": False,
        "raw_provider_material_recorded": False,
        "raw_tool_bodies_recorded": False,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
