from __future__ import annotations

from dataclasses import dataclass
import http.cookiejar
import json
import os
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener
from uuid import uuid4


BASE_URL = os.environ.get(
    "ACADEMY_PRODUCTION_WEB_BASE_URL",
    "https://production-web-production-c9d1.up.railway.app",
).rstrip("/")
EXPECTED_SHA = os.environ.get("ACADEMY_EXPECTED_RELEASE_GIT_SHA", os.environ.get("GITHUB_SHA", "")).strip()
TIMEOUT_SECONDS = 25
DEPLOY_WAIT_SECONDS = 300
RUN_WAIT_SECONDS = 150


@dataclass
class HttpResult:
    status: int
    body: bytes
    headers: Any

    def json_object(self) -> dict[str, Any]:
        payload = json.loads(self.body.decode("utf-8")) if self.body else {}
        if not isinstance(payload, dict):
            raise RuntimeError("expected JSON object")
        return payload


class BrowserSession:
    def __init__(self) -> None:
        self.cookies = http.cookiejar.CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookies))

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResult:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{BASE_URL}{path}",
            data=body,
            headers={
                "Accept": "application/json",
                "User-Agent": "academy-tractian-release0-agent-smoke/1",
                **({"Content-Type": "application/json"} if body is not None else {}),
                **(headers or {}),
            },
            method=method,
        )
        try:
            with self.opener.open(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed HTTPS production origin
                return HttpResult(int(response.status), response.read(), response.headers)
        except HTTPError as exc:
            return HttpResult(int(exc.code), exc.read(), exc.headers)
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"remote request unavailable for {path}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def wait_for_exact_release() -> dict[str, Any]:
    require(len(EXPECTED_SHA) == 40, "expected release SHA is missing")
    deadline = time.monotonic() + DEPLOY_WAIT_SECONDS
    anonymous = BrowserSession()
    last: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        result = anonymous.request("/api/meta/release")
        if result.status == 200:
            last = result.json_object()
            if last.get("artifact_git_sha") == EXPECTED_SHA and last.get("artifact_identity_verified") is True:
                return last
        time.sleep(5)
    seen = None if last is None else last.get("artifact_git_sha")
    raise RuntimeError(f"production did not converge to expected release identity; observed={seen}")


def require_release0_capabilities() -> dict[str, Any]:
    result = BrowserSession().request("/api/release0/capabilities")
    require(result.status == 200, f"capability manifest returned HTTP {result.status}")
    manifest = result.json_object()
    require(manifest.get("schema_version") == "release0-capabilities-v1", "capability schema drift")
    summary = manifest.get("tool_summary")
    require(isinstance(summary, dict), "tool summary missing")
    require(summary.get("total") == 18, "canonical operation count drift")
    require(summary.get("reads") == 13, "canonical read count drift")
    require(summary.get("actions") == 5, "canonical action count drift")
    release = manifest.get("release")
    provider = manifest.get("provider")
    tractian = manifest.get("tractian")
    action_execution = manifest.get("action_execution")
    require(isinstance(release, dict) and release.get("read_only_user_path_enabled") is True, "read-only user path not ready")
    require(isinstance(provider, dict) and provider.get("calls_enabled") is True, "provider calls not enabled")
    require(provider.get("provider_id") == "cloudflare", "unexpected Release 0 provider")
    require(isinstance(tractian, dict) and tractian.get("read_path_enabled") is True, "TRACTIAN read path not enabled")
    require(isinstance(action_execution, dict) and action_execution.get("enabled") is False, "action execution unexpectedly enabled")
    require(action_execution.get("external_side_effects_allowed") is False, "external side effects unexpectedly allowed")
    return manifest


def sign_up() -> BrowserSession:
    browser = BrowserSession()
    result = browser.request(
        "/auth/sign-up/email",
        method="POST",
        payload={
            "email": f"academy-release0-{uuid4().hex}@example.com",
            "password": f"Release0-{uuid4().hex}-Secure!",
            "name": "Release 0 acceptance",
        },
        headers={"Origin": BASE_URL},
    )
    require(result.status in {200, 201}, f"Release 0 sign-up failed with HTTP {result.status}")
    context = browser.request("/api/session/context")
    require(context.status == 200, "server-owned session context unavailable")
    require(context.json_object().get("server_owned") is True, "session context is not server-owned")
    return browser


def wait_for_execution(browser: BrowserSession, execution_path: str) -> str:
    deadline = time.monotonic() + RUN_WAIT_SECONDS
    while time.monotonic() < deadline:
        result = browser.request(execution_path)
        require(result.status == 200, f"execution status returned HTTP {result.status}")
        status = result.json_object().get("status")
        if status in {"completed", "failed"}:
            return str(status)
        time.sleep(1.5)
    raise RuntimeError("Release 0 run did not reach a terminal execution state")


def safe_items(browser: BrowserSession, path: str) -> list[dict[str, Any]]:
    result = browser.request(path)
    require(result.status == 200, f"{path} returned HTTP {result.status}")
    payload = result.json_object()
    items = payload.get("items")
    require(isinstance(items, list), f"{path} did not return an items array")
    require(all(isinstance(item, dict) for item in items), f"{path} returned a non-object item")
    return items


def assert_no_secret_projection(payloads: list[object]) -> None:
    serialized = json.dumps(payloads, sort_keys=True).lower()
    for marker in (
        "provider_api_token",
        "provider_account_id",
        "tractian_server_headers",
        "authorization: bearer",
        "postgres_internal_dsn",
        "postgres_scoped_dsn",
    ):
        require(marker not in serialized, f"forbidden secret marker leaked: {marker}")


def sign_out(browser: BrowserSession) -> None:
    result = browser.request("/auth/sign-out", method="POST", payload={}, headers={"Origin": BASE_URL})
    require(result.status in {200, 204}, f"sign-out failed with HTTP {result.status}")


def main() -> None:
    release = wait_for_exact_release()
    manifest = require_release0_capabilities()
    browser = sign_up()

    prompt = (
        "Investigate the recommended diagnostic procedure for an industrial vibration alert using live TRACTIAN evidence. "
        "You must use the search_knowledge read tool with a relevant vibration diagnostic query before concluding; if a "
        "relevant knowledge document is returned and its identifier is available, inspect it with get_knowledge_doc. "
        "Do not propose or execute any action. Return a customer-safe conclusion and preserve partial, inconclusive, "
        "conflicting, or unavailable evidence semantics instead of guessing."
    )
    accepted_result = browser.request("/api/runs", method="POST", payload={"user_request": prompt})
    require(accepted_result.status == 202, f"live Release 0 run was not accepted: HTTP {accepted_result.status}")
    accepted = accepted_result.json_object()
    run_id = accepted.get("run_id")
    execution_path = accepted.get("execution_path")
    require(isinstance(run_id, str) and run_id, "accepted run_id missing")
    require(isinstance(execution_path, str) and execution_path, "execution_path missing")

    execution_status = wait_for_execution(browser, execution_path)
    require(execution_status == "completed", "live Release 0 agent execution failed")

    run_result = browser.request(f"/api/runs/{run_id}")
    require(run_result.status == 200, "completed run is not retrievable")
    run = run_result.json_object()
    events = safe_items(browser, f"/api/runs/{run_id}/events")
    evidence = safe_items(browser, f"/api/runs/{run_id}/evidence")
    evaluation = safe_items(browser, f"/api/runs/{run_id}/evaluation")
    actions = safe_items(browser, f"/api/runs/{run_id}/actions")
    lineage_result = browser.request(f"/api/runs/{run_id}/lineage")
    require(lineage_result.status == 200, "output lineage unavailable")
    lineage = lineage_result.json_object()

    model_calls = [event for event in events if event.get("event_type") == "model_call"]
    require(model_calls, "no model_call event persisted")
    require(any(event.get("provider_id") == "cloudflare" and event.get("live_call") is True for event in model_calls), "no live Cloudflare provider provenance persisted")

    read_tool_names = {tool["name"] for tool in manifest["tools"] if tool.get("kind") == "read"}
    action_tool_names = {tool["name"] for tool in manifest["tools"] if tool.get("kind") == "action"}
    read_calls = [event for event in events if event.get("event_type") == "tool_call" and event.get("tool_name") in read_tool_names]
    read_results = [event for event in events if event.get("event_type") == "tool_result" and event.get("tool_name") in read_tool_names]
    require(read_calls, "agent completed without a canonical live read tool call")
    require(any(isinstance(event.get("status_code"), int) and 200 <= event["status_code"] < 300 for event in read_results), "no successful live TRACTIAN read result persisted")
    require(any(event.get("tool_name") == "search_knowledge" for event in read_calls), "required search_knowledge acceptance read was not used")

    action_calls = [event for event in events if event.get("event_type") == "tool_call" and event.get("tool_name") in action_tool_names]
    require(not action_calls, "read-only acceptance run reached an action transport call")
    require(actions == [], "read-only acceptance run unexpectedly persisted an actionable confirmation")

    require(run.get("completed") is True, "run projection not marked completed")
    require(isinstance(run.get("terminal_message"), str) and bool(run["terminal_message"].strip()), "customer-safe terminal message missing")
    require(run.get("terminal_response_mode") in {"complete", "partial", "inconclusive", "conflict", "unavailable"}, "terminal response semantics missing or invalid")
    require(evidence, "no evidence reference persisted for the real read path")
    require(evaluation, "post-runtime evaluation rows missing")
    blocking = [item for item in evaluation if item.get("blocking") is True]
    require(blocking, "no blocking evaluation checks persisted")
    require(all(item.get("passed") is True for item in blocking), "a blocking post-runtime evaluation check failed")
    require(lineage.get("runtime_card_count", 0) > 0, "output lineage has no runtime cards")

    assert_no_secret_projection([release, manifest, run, events, evidence, evaluation, actions, lineage])
    sign_out(browser)

    report = {
        "schema_version": "hosted-release0-agent-acceptance-v1",
        "status": "PASS",
        "release_git_sha": EXPECTED_SHA,
        "provider": "cloudflare",
        "live_model_call": True,
        "live_tractian_read": True,
        "canonical_tool_count": 18,
        "read_tool_count": 13,
        "proposal_only_action_count": 5,
        "search_knowledge_observed": True,
        "evidence_persisted": True,
        "terminal_output_persisted": True,
        "post_runtime_evaluation_persisted": True,
        "output_lineage_persisted": True,
        "blocking_checks_passed": True,
        "external_action_calls": 0,
        "raw_secrets_printed": False,
    }
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
