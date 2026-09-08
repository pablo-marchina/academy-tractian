#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Mapping

USER_AGENT = "academy-tractian-provider-tournament/1.0"
RATE_HEADERS = (
    "x-ratelimit-limit-requests",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-reset-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-tokens",
    "retry-after",
)


def _redact(text: str) -> str:
    for key in (
        "GROQ_API_KEY",
        "TOURNAMENT_CLOUDFLARE_API_TOKEN",
        "TOURNAMENT_CLOUDFLARE_ACCOUNT_ID",
        "ACADEMY_PROVIDER_API_TOKEN",
        "ACADEMY_PROVIDER_ACCOUNT_ID",
    ):
        value = os.environ.get(key, "").strip()
        if value:
            text = text.replace(value, "<redacted>")
    return text[:400]


def _selected_headers(headers: Mapping[str, str]) -> dict[str, str]:
    lower = {str(k).lower(): str(v) for k, v in headers.items()}
    return {name: lower[name] for name in RATE_HEADERS if name in lower}


def _request(method: str, url: str, headers: dict[str, str], body: dict[str, Any] | None = None) -> tuple[int, Any, dict[str, str]]:
    data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json", **headers}
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status = int(response.status)
            response_headers = _selected_headers(response.headers)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8", errors="replace")
        response_headers = _selected_headers(exc.headers)
    except Exception as exc:
        return 0, {"transport_error": type(exc).__name__}, {}
    try:
        payload: Any = json.loads(raw)
    except Exception:
        payload = {"non_json": _redact(raw)}
    return status, payload, response_headers


def _error_summary(payload: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(payload, dict):
        if payload.get("non_json") is not None:
            result["non_json"] = _redact(str(payload.get("non_json")))
        if payload.get("transport_error") is not None:
            result["transport_error"] = str(payload.get("transport_error"))
        error = payload.get("error")
        if isinstance(error, dict):
            if error.get("type") is not None:
                result["type"] = error.get("type")
            if error.get("code") is not None:
                result["code"] = error.get("code")
            if error.get("message") is not None:
                result["message"] = _redact(str(error.get("message")))
        errors = payload.get("errors")
        if isinstance(errors, list):
            compact = []
            for item in errors[:3]:
                if isinstance(item, dict):
                    compact.append({
                        "code": item.get("code"),
                        "message": _redact(str(item.get("message", ""))),
                    })
            if compact:
                result["errors"] = compact
    return result


def main() -> int:
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    cf_account = (
        os.environ.get("TOURNAMENT_CLOUDFLARE_ACCOUNT_ID", "").strip()
        or os.environ.get("ACADEMY_PROVIDER_ACCOUNT_ID", "").strip()
    )
    cf_token = (
        os.environ.get("TOURNAMENT_CLOUDFLARE_API_TOKEN", "").strip()
        or os.environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
    )

    report: dict[str, Any] = {"schema_version": "provider-access-diagnostic-v4", "user_agent": USER_AGENT}

    if groq_key:
        headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
        status, payload, rate_headers = _request("GET", "https://api.groq.com/openai/v1/models", headers)
        model_visible = False
        if status == 200 and isinstance(payload, dict) and isinstance(payload.get("data"), list):
            model_visible = any(
                isinstance(item, dict) and item.get("id") == "openai/gpt-oss-120b"
                for item in payload["data"]
            )
        report["groq_models"] = {"status": status, "model_visible": model_visible, "rate_headers": rate_headers, **_error_summary(payload)}

        status, payload, rate_headers = _request(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            headers,
            {
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
                "temperature": 0,
                "max_completion_tokens": 8,
                "stream": False,
            },
        )
        report["groq_chat"] = {"status": status, "rate_headers": rate_headers, **_error_summary(payload)}
    else:
        report["groq"] = {"status": "missing_credentials"}

    if cf_account and cf_token:
        headers = {"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
        status, payload, rate_headers = _request(
            "POST",
            f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/v1/chat/completions",
            headers,
            {
                "model": "@cf/openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
                "temperature": 0,
                "max_completion_tokens": 8,
                "stream": False,
            },
        )
        report["cloudflare_chat"] = {"status": status, "rate_headers": rate_headers, **_error_summary(payload)}
    else:
        report["cloudflare"] = {"status": "missing_credentials"}

    print("PROVIDER_ACCESS_DIAGNOSTIC=" + json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
