from __future__ import annotations

import json
from typing import Any, Mapping

from .decision_source import ProviderDecisionRequest
from .provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    ProviderUsageRecord,
)


GOOGLE_HOSTED_PROVIDER_ID = "google"
GOOGLE_37_MODEL_ID = "gemini-3.7-flash"
GOOGLE_38_MODEL_ID = "gemini-3.8-flash"
GOOGLE_INTERACTIONS_SUPPORTED_MODELS = frozenset({GOOGLE_37_MODEL_ID, GOOGLE_38_MODEL_ID})
# The Interactions product is GA as of June 2026, while the current public REST path remains
# versioned v1beta. Keep product maturity and transport version distinct in evidence/provenance.
GOOGLE_INTERACTIONS_ROUTE_ID = "google.interactions.ga.v1beta.stateless"
GOOGLE_INTERACTIONS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _provider_request_text(request: ProviderDecisionRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _schema_copy() -> dict[str, Any]:
    return json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))


class GoogleHostedInteractionsDecisionClient:
    """One-shot stateless Gemini Interactions client for controlled hosted candidates.

    The Interactions product is GA, but Google currently exposes its REST resource at the v1beta
    path. Model identity is explicit so upgrades cannot inherit prior evidence silently. Requests
    disable server-side storage, background execution, provider tools and thought summaries; the
    application remains the only owner of the agent loop, tool execution and safety decisions.
    """

    provider_id = GOOGLE_HOSTED_PROVIDER_ID
    route_id = GOOGLE_INTERACTIONS_ROUTE_ID

    def __init__(
        self,
        *,
        api_key: str,
        model_id: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("provider client requires an explicit non-empty api_key")
        normalized_model = model_id.strip()
        if normalized_model not in GOOGLE_INTERACTIONS_SUPPORTED_MODELS:
            raise ValueError("unsupported_google_interactions_model")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.model_id = normalized_model
        self._api_key = api_key
        self._transport = transport
        self._timeout_seconds = float(timeout_seconds)
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(provider_id={self.provider_id!r}, "
            f"model_id={self.model_id!r}, route_id={self.route_id!r}, api_key=<redacted>)"
        )

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.model_id,
            "store": False,
            "background": False,
            "system_instruction": PROVIDER_DECISION_SYSTEM_INSTRUCTION,
            "input": _provider_request_text(request),
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": _schema_copy(),
            },
            "generation_config": {
                "thinking_level": "medium",
                "thinking_summaries": "none",
                "tool_choice": "none",
            },
        }
        return ProviderHttpRequest(
            method="POST",
            url=GOOGLE_INTERACTIONS_ENDPOINT,
            headers={
                "x-goog-api-key": self._api_key,
                "Content-Type": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        try:
            response = self._transport.post_json(self.build_http_request(request))
        except ProviderHttpClientError:
            raise
        except Exception:
            raise ProviderHttpClientError("TRANSPORT_FAILURE") from None

        if not isinstance(response, ProviderHttpResponse):
            raise ProviderHttpClientError("TRANSPORT_RESPONSE_INVALID")
        if response.status_code < 200 or response.status_code >= 300:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=response.status_code)
        if not isinstance(response.body, Mapping):
            raise ProviderHttpClientError("HTTP_JSON_NOT_OBJECT")

        usage = response.body.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(usage_map.get("total_input_tokens")),
                output_tokens=_nonnegative_int_or_none(usage_map.get("total_output_tokens")),
                total_tokens=_nonnegative_int_or_none(usage_map.get("total_tokens")),
                reasoning_tokens=_nonnegative_int_or_none(usage_map.get("total_thought_tokens")),
            )
        )
        return _extract_google_output(response.body, expected_model=self.model_id)

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage_records)
        self._usage_records.clear()
        return records


def _extract_google_output(response: Mapping[str, Any], *, expected_model: str) -> str:
    if response.get("object") not in (None, "interaction"):
        raise ProviderHttpClientError("GOOGLE_OBJECT_INVALID")
    if response.get("status") != "completed":
        raise ProviderHttpClientError("GOOGLE_STATUS_NOT_COMPLETED")
    if response.get("model") != expected_model:
        raise ProviderHttpClientError("GOOGLE_MODEL_MISMATCH")
    steps = response.get("steps")
    if not isinstance(steps, list):
        raise ProviderHttpClientError("GOOGLE_STEPS_INVALID")

    texts: list[str] = []
    for step in steps:
        if not isinstance(step, Mapping):
            raise ProviderHttpClientError("GOOGLE_STEP_INVALID")
        step_type = step.get("type")
        if step_type == "thought":
            continue
        if step_type != "model_output":
            raise ProviderHttpClientError("GOOGLE_UNEXPECTED_STEP")
        if step.get("status") not in (None, "done", "completed"):
            raise ProviderHttpClientError("GOOGLE_MODEL_OUTPUT_NOT_DONE")
        content = step.get("content")
        if not isinstance(content, list):
            raise ProviderHttpClientError("GOOGLE_CONTENT_INVALID")
        for part in content:
            if not isinstance(part, Mapping) or part.get("type") != "text":
                raise ProviderHttpClientError("GOOGLE_UNEXPECTED_CONTENT")
            text = part.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ProviderHttpClientError("GOOGLE_OUTPUT_TEXT_INVALID")
            texts.append(text)

    if len(texts) != 1:
        raise ProviderHttpClientError("GOOGLE_OUTPUT_TEXT_COUNT")
    return texts[0]
