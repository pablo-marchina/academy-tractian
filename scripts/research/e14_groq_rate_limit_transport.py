#!/usr/bin/env python3
"""Rate-limit-aware Groq transport used only by recovered E14 DEV capture.

This module changes transport behavior only. It does not change prompts, model
instructions, DEV groups, scorer logic, private-oracle isolation, E14 policy, or
acceptance thresholds.

It honors Groq's documented `retry-after` / token-reset headers for 429 responses,
classifies provider failures without persisting raw error text, and falls back to
bounded exponential backoff for transient 5xx/network failures.

For the GPT-OSS replacement-model recovery, reasoning effort is explicitly frozen
at `medium` (the provider default) and E14 gets its own completion-token budget so
we can remove the prior 800-token harness bottleneck without changing reasoning
behavior or decision semantics.
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
DEFAULT_USER_AGENT = "academy-tractian-e14-rate-limit-aware/1.2"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_E14_MAX_COMPLETION_TOKENS = 1600


class E14ProviderRequestError(RuntimeError):
    def __init__(self, category: str, status_code: int | None = None):
        super().__init__(f"E14_PROVIDER_REQUEST_FAILED:{category}")
        self.category = category
        self.status_code = status_code


def error_fields(body: str) -> tuple[str, str, str]:
    """Return only provider error code/type/message for in-memory classification."""
    try:
        payload = json.loads(body)
    except Exception:
        return "", "", body
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        return "", "", body
    code = str(error.get("code") or "")
    error_type = str(error.get("type") or "")
    message = str(error.get("message") or "")
    failed_generation = error.get("failed_generation")
    if failed_generation is not None:
        message = f"{message} failed_generation"
    return code, error_type, message


def classify_failure(status_code: int | None, body: str) -> str:
    code, error_type, message = error_fields(body)
    lowered = f"{code} {error_type} {message}".lower()

    if status_code == 429:
        if "tokens per day" in lowered or "tpd" in lowered:
            return "rate_limit_tpd"
        if "tokens per minute" in lowered or "tpm" in lowered:
            return "rate_limit_tpm"
        if "requests per minute" in lowered or "rpm" in lowered:
            return "rate_limit_rpm"
        if "requests per day" in lowered or "rpd" in lowered:
            return "rate_limit_rpd"
        return "rate_limit"
    if status_code in {500, 502, 503, 504}:
        return "provider_server_failure"
    if status_code in {401, 403}:
        return "authentication_or_authorization_failure"
    if status_code == 404:
        return "model_or_endpoint_unavailable"
    if status_code in {400, 422} and (
        code == "json_validate_failed"
        or "failed_generation" in lowered
        or "valid json" in lowered
        or "json validation" in lowered
        or "generated json" in lowered
    ):
        return "json_generation_validation_failure"
    if status_code == 413:
        return "request_too_large"
    if status_code in {400, 422}:
        return "invalid_request_failure"
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


def documented_retry_wait(exc: urllib.error.HTTPError) -> float | None:
    retry_after = parse_seconds(exc.headers.get("retry-after"))
    token_reset = parse_reset_duration(exc.headers.get("x-ratelimit-reset-tokens"))
    waits = [x for x in (retry_after, token_reset) if x is not None]
    if not waits:
        return None
    return max(waits) + 0.75 + random.uniform(0.0, 0.5)


def post_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    attempts = int(os.getenv("E8_PROVIDER_MAX_ATTEMPTS", "5"))
    base_sleep = float(os.getenv("E8_PROVIDER_RETRY_BASE_SECONDS", "5"))
    max_sleep = float(os.getenv("E14_PROVIDER_MAX_RETRY_SLEEP_SECONDS", "75"))
    max_documented_wait = float(os.getenv("E14_PROVIDER_MAX_DOCUMENTED_RETRY_SECONDS", "180"))
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
    provider_attempts = 0
    rate_limit_events = 0
    wait_seconds_total = 0.0

    for attempt in range(1, attempts + 1):
        provider_attempts += 1
        req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body), {
                    "provider_attempts": provider_attempts,
                    "rate_limit_events": rate_limit_events,
                    "provider_retry_wait_seconds_total": round(wait_seconds_total, 3),
                }
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_status = int(exc.code)
            last_category = classify_failure(last_status, body)
            retryable = last_status in {408, 409, 425, 429, 500, 502, 503, 504}
            if attempt >= attempts or not retryable:
                break

            if last_status == 429:
                rate_limit_events += 1
                documented_wait = documented_retry_wait(exc)
                if documented_wait is not None:
                    if documented_wait > max_documented_wait:
                        raise E14ProviderRequestError("rate_limit_long_window", last_status)
                    wait = documented_wait
                else:
                    wait = min(max_sleep, base_sleep * (2 ** (attempt - 1)) + random.uniform(0.0, 0.5))
            else:
                wait = min(max_sleep, base_sleep * (2 ** (attempt - 1)) + random.uniform(0.0, 0.5))

            wait_seconds_total += wait
            time.sleep(wait)
        except Exception as exc:  # noqa: BLE001 - classified without leaking raw provider text
            last_status = None
            last_category = classify_failure(None, str(exc))
            retryable = last_category == "network_or_transient_failure"
            if attempt >= attempts or not retryable:
                break
            wait = min(max_sleep, base_sleep * (2 ** (attempt - 1)) + random.uniform(0.0, 0.5))
            wait_seconds_total += wait
            time.sleep(wait)

    raise E14ProviderRequestError(last_category, last_status)


def call_groq(prompt: str, timeout: int, base_module: Any) -> tuple[str, dict[str, Any]]:
    model = os.getenv("E8_GROQ_MODEL", DEFAULT_MODEL)
    reasoning_effort = os.getenv("E14_REASONING_EFFORT", DEFAULT_REASONING_EFFORT).strip().lower()
    if reasoning_effort not in {"low", "medium", "high"}:
        raise AssertionError("E14_REASONING_EFFORT must be one of: low, medium, high")
    max_completion_tokens = int(
        os.getenv(
            "E14_MAX_COMPLETION_TOKENS",
            str(DEFAULT_E14_MAX_COMPLETION_TOKENS),
        )
    )
    if max_completion_tokens < 1:
        raise AssertionError("E14_MAX_COMPLETION_TOKENS must be >= 1")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": base_module.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(os.getenv("E8_MODEL_TEMPERATURE", "0")),
        "reasoning_effort": reasoning_effort,
        "max_completion_tokens": max_completion_tokens,
        "response_format": {"type": "json_object"},
    }
    response, transport_meta = post_json(
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
        "reasoning_effort": reasoning_effort,
        "max_completion_tokens": max_completion_tokens,
        **transport_meta,
    }
