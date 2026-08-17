#!/usr/bin/env python3
"""Rate-limit-aware Groq transport used only by recovered E14 DEV capture.

This module changes transport behavior only. It does not change prompts, model
instructions, DEV groups, scorer logic, private-oracle isolation, E14 policy, or
acceptance thresholds.

It honors Groq's documented `retry-after` header for 429 responses and falls
back to bounded exponential backoff for transient 5xx/network failures.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from typing import Any

API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"
DEFAULT_USER_AGENT = "academy-tractian-e14-rate-limit-aware/1.0"


class E14ProviderRequestError(RuntimeError):
    def __init__(self, category: str, status_code: int | None = None):
        super().__init__(f"E14_PROVIDER_REQUEST_FAILED:{category}")
        self.category = category
        self.status_code = status_code


def classify_failure(status_code: int | None, message: str) -> str:
    lowered = message.lower()
    if status_code == 429:
        return "rate_limit"
    if status_code in {500, 502, 503, 504}:
        return "provider_server_failure"
    if status_code in {401, 403}:
        return "authentication_or_authorization_failure"
    if status_code == 404:
        return "model_or_endpoint_unavailable"
    if status_code in {400, 413, 422}:
        return "non_retryable_request_failure"
    if any(fragment in lowered for fragment in (
        "timed out",
        "timeout",
        "connection reset",
        "winerror 10054",
        "temporarily unavailable",
        "remote end closed",
    )):
        return "network_or_transient_failure"
    return "unknown_provider_failure"


def parse_seconds(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value.strip()))
    except ValueError:
        return None


def parse_reset_duration(value: str | None) -> float | None:
    """Parse Groq-style durations such as `7.66s`, `2m59.56s`, or `1m`."""
    if not value:
        return None
    text = value.strip().lower()
    match = re.fullmatch(r"(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?", text)
    if not match:
        return None
    minutes = float(match.group(1) or 0.0)
    seconds = float(match.group(2) or 0.0)
    return max(0.0, minutes * 60.0 + seconds)


def retry_wait_seconds(exc: urllib.error.HTTPError, attempt: int, base_sleep: float, max_sleep: float) -> float:
    retry_after = parse_seconds(exc.headers.get("retry-after"))
    token_reset = parse_reset_duration(exc.headers.get("x-ratelimit-reset-tokens"))
    documented_waits = [x for x in (retry_after, token_reset) if x is not None]
    if documented_waits:
        wait = max(documented_waits) + 0.75
    else:
        wait = base_sleep * (2 ** (attempt - 1))
    jitter = random.uniform(0.0, 0.5)
    return min(max_sleep, wait + jitter)


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    attempts = int(os.getenv("E8_PROVIDER_MAX_ATTEMPTS", "5"))
    base_sleep = float(os.getenv("E8_PROVIDER_RETRY_BASE_SECONDS", "5"))
    max_sleep = float(os.getenv("E14_PROVIDER_MAX_RETRY_SLEEP_SECONDS", "75"))
    if attempts < 1:
        raise AssertionError("E8_PROVIDER_MAX_ATTEMPTS must be >= 1")

    data = json.dumps(payload).encode("utf-8")
    request_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": os.getenv("E8_HTTP_USER_AGENT", DEFAULT_USER_AGENT),
        **headers,
    }

    last_category = "unknown_provider_failure"
    last_status: int | None = None

    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_status = int(exc.code)
            last_category = classify_failure(last_status, body)
            retryable = last_status in {408, 409, 425, 429, 500, 502, 503, 504}
            if attempt >= attempts or not retryable:
                break
            time.sleep(retry_wait_seconds(exc, attempt, base_sleep, max_sleep))
        except Exception as exc:  # noqa: BLE001 - classified without leaking raw provider text
            last_status = None
            last_category = classify_failure(None, str(exc))
            retryable = last_category == "network_or_transient_failure"
            if attempt >= attempts or not retryable:
                break
            wait = min(max_sleep, base_sleep * (2 ** (attempt - 1)) + random.uniform(0.0, 0.5))
            time.sleep(wait)

    raise E14ProviderRequestError(last_category, last_status)


def call_groq(prompt: str, timeout: int, base_module: Any) -> tuple[str, dict[str, Any]]:
    model = os.getenv("E8_GROQ_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": base_module.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(os.getenv("E8_MODEL_TEMPERATURE", "0")),
        "max_completion_tokens": int(os.getenv("E8_MAX_OUTPUT_TOKENS", "800")),
        "response_format": {"type": "json_object"},
    }
    response = post_json(
        API_URL,
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        payload,
        timeout,
    )
    content = response["choices"][0]["message"]["content"]
    return content, {
        "model": model,
        "usage": response.get("usage", {}),
        "transport": "e14_rate_limit_aware",
    }
