from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.request

AUTH_BASE = os.environ["AUTH_BASE_URL"].rstrip("/")
API_BASE = os.environ["TARGET_API_BASE_URL"].rstrip("/")
EMAIL = os.environ["QA_EMAIL"]
PASSWORD = os.environ["QA_PASSWORD"]
EXPECTED_SHA = os.environ["EXPECTED_RELEASE_SHA"].strip().lower()

jar = http.cookiejar.CookieJar()
auth_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def _decode(raw: bytes):
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text) if text else None
    except Exception:
        return {"raw": text[:1000]}


def request(base, path, method="GET", payload=None, timeout=30, cookie=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "User-Agent": "academy-tractian-auth-ladder/1",
        "Origin": AUTH_BASE,
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    if cookie:
        headers["Cookie"] = cookie
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    opener = auth_opener if base == AUTH_BASE else urllib.request.build_opener()
    started = time.perf_counter()
    try:
        with opener.open(req, timeout=timeout) as response:
            return int(response.status), _decode(response.read()), (time.perf_counter() - started) * 1000
    except urllib.error.HTTPError as exc:
        return int(exc.code), _decode(exc.read()), (time.perf_counter() - started) * 1000
    except Exception as exc:
        return 0, {"error": type(exc).__name__}, (time.perf_counter() - started) * 1000


def detail(body) -> str:
    return str(body.get("detail") or "") if isinstance(body, dict) else ""


def authenticate() -> str:
    status, _, _ = request(
        AUTH_BASE,
        "/auth/sign-up/email",
        "POST",
        {"email": EMAIL, "password": PASSWORD, "name": "QA Auth Ladder"},
    )
    if status not in {200, 201}:
        status, body, _ = request(
            AUTH_BASE,
            "/auth/sign-in/email",
            "POST",
            {"email": EMAIL, "password": PASSWORD, "rememberMe": True},
        )
        if status not in {200, 201}:
            raise RuntimeError(f"auth_failed:{status}:{detail(body)}")
    status, body, _ = request(AUTH_BASE, "/auth/get-session?disableCookieCache=true")
    if status != 200 or not isinstance(body, dict) or not body.get("user"):
        raise RuntimeError(f"session_failed:{status}:{detail(body)}")
    cookie = "; ".join(f"{item.name}={item.value}" for item in jar)
    if not cookie:
        raise RuntimeError("session_cookie_missing")
    return cookie


def assert_identity(cookie: str) -> None:
    status, body, _ = request(API_BASE, "/api/release0/capabilities", cookie=cookie)
    release = body.get("release") if status == 200 and isinstance(body, dict) else None
    actual = release.get("git_sha") if isinstance(release, dict) else None
    if status != 200 or actual != EXPECTED_SHA:
        raise RuntimeError(f"candidate_identity_mismatch:{status}:{actual}")


def submit(cookie: str, label: str):
    prompt = f"Auth reliability probe {label}: liste os ativos acessíveis sem inventar recursos."
    status, body, elapsed = request(
        API_BASE,
        "/api/runs",
        "POST",
        {"user_request": prompt},
        timeout=30,
        cookie=cookie,
    )
    run_id = body.get("run_id") if status == 202 and isinstance(body, dict) else None
    return {
        "operation": "POST /api/runs",
        "status": status,
        "detail": detail(body),
        "run_id": run_id,
        "elapsed_ms": round(elapsed, 2),
    }


def poll_frontend_pattern(cookie: str, run_id: str):
    results = []
    for path in (
        f"/api/runs/{run_id}/execution",
        f"/api/runs/{run_id}",
        f"/api/runs/{run_id}/execution",
    ):
        status, body, elapsed = request(API_BASE, path, cookie=cookie, timeout=20)
        results.append(
            {
                "operation": "GET " + path.split(run_id)[-1].replace(run_id, ""),
                "path": path,
                "status": status,
                "detail": detail(body),
                "elapsed_ms": round(elapsed, 2),
            }
        )
        time.sleep(0.15)
    return results


def serial_stage(cookie: str, count: int):
    observations = []
    for index in range(count):
        item = submit(cookie, f"serial-{count}-{index}")
        observations.append(item)
        if item["run_id"]:
            observations.extend(poll_frontend_pattern(cookie, str(item["run_id"])))
        time.sleep(0.2)
    return observations


def concurrent_stage(cookie: str, count: int):
    observations = []
    with ThreadPoolExecutor(max_workers=count) as pool:
        futures = [pool.submit(submit, cookie, f"concurrent-{count}-{index}") for index in range(count)]
        accepted = []
        for future in as_completed(futures):
            item = future.result()
            observations.append(item)
            if item["run_id"]:
                accepted.append(str(item["run_id"]))
    with ThreadPoolExecutor(max_workers=max(1, min(count, len(accepted)))) as pool:
        futures = [pool.submit(poll_frontend_pattern, cookie, run_id) for run_id in accepted]
        for future in as_completed(futures):
            observations.extend(future.result())
    return observations


def stage_summary(name: str, observations):
    statuses = Counter(int(item["status"]) for item in observations)
    auth_503 = sum(
        item["status"] == 503 and item.get("detail") == "managed_session_unavailable"
        for item in observations
    )
    post_items = [item for item in observations if item["operation"] == "POST /api/runs"]
    return {
        "stage": name,
        "request_count": len(observations),
        "post_count": len(post_items),
        "post_accepted": sum(item["status"] == 202 for item in post_items),
        "managed_session_unavailable": auth_503,
        "status_counts": dict(statuses),
        "max_elapsed_ms": max((item["elapsed_ms"] for item in observations), default=0),
        "observations": observations,
    }


def main() -> None:
    if len(EXPECTED_SHA) != 40:
        raise SystemExit("EXPECTED_RELEASE_SHA must be a 40-character SHA")
    cookie = authenticate()
    assert_identity(cookie)

    reports = []
    for count in (1, 5, 10):
        observations = serial_stage(cookie, count)
        report = stage_summary(f"serial-{count}", observations)
        reports.append(report)
        print(json.dumps({key: value for key, value in report.items() if key != "observations"}), flush=True)

    for count in (2, 5, 10):
        observations = concurrent_stage(cookie, count)
        report = stage_summary(f"concurrent-{count}", observations)
        reports.append(report)
        print(json.dumps({key: value for key, value in report.items() if key != "observations"}), flush=True)

    summary = {
        "schema_version": "auth-reliability-ladder-v1",
        "release_sha": EXPECTED_SHA,
        "retry_policy": "none",
        "total_requests": sum(report["request_count"] for report in reports),
        "total_posts": sum(report["post_count"] for report in reports),
        "total_post_accepted": sum(report["post_accepted"] for report in reports),
        "managed_session_unavailable": sum(report["managed_session_unavailable"] for report in reports),
        "stages": reports,
    }
    print(json.dumps(summary), flush=True)
    raise SystemExit(0 if summary["managed_session_unavailable"] == 0 else 31)


if __name__ == "__main__":
    main()
