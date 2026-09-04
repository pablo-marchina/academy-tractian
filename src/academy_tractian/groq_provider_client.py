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


GROQ_PROVIDER_ID = "groq"
GROQ_MODEL_ID = "openai/gpt-oss-120b"
GROQ_ROUTE_ID = "groq.responses.beta.stateless"
GROQ_RESPONSES_ENDPOINT = "https://api.groq.com/openai/v1/responses"


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


class GroqResponsesDecisionClient:
    """One-shot Groq Responses client for the governed hosted provider challenger.

    The client deliberately uses the provider-neutral application decision schema rather than
    Groq-hosted tools. Tool execution remains exclusively application-owned. There are no retries,
    fallbacks, environment credential lookups, response persistence, or hidden provider SDKs.
    """

    provider_id = GROQ_PROVIDER_ID
    model_id = GROQ_MODEL_ID
    route_id = GROQ_ROUTE_ID

    def __init__(
        self,
        *,
        api_key: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("provider client requires an explicit non-empty api_key")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
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
            "reasoning": {"effort": "medium"},
            "instructions": PROVIDER_DECISION_SYSTEM_INSTRUCTION,
            "input": _provider_request_text(request),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "provider_decision_payload",
                    "schema": _schema_copy(),
                }
            },
        }
        return ProviderHttpRequest(
            method="POST",
            url=GROQ_RESPONSES_ENDPOINT,
            headers={
                "Authorization": f"Bearer {self._api_key}",
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
        output_details = usage_map.get("output_tokens_details")
        output_details_map = output_details if isinstance(output_details, Mapping) else {}
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(usage_map.get("input_tokens")),
                output_tokens=_nonnegative_int_or_none(usage_map.get("output_tokens")),
                total_tokens=_nonnegative_int_or_none(usage_map.get("total_tokens")),
                reasoning_tokens=_nonnegative_int_or_none(output_details_map.get("reasoning_tokens")),
            )
        )
        return _extract_groq_output(response.body)

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage_records)
        self._usage_records.clear()
        return records


def _extract_groq_output(response: Mapping[str, Any]) -> str:
    if response.get("object") != "response":
        raise ProviderHttpClientError("GROQ_OBJECT_INVALID")
    if response.get("status") != "completed":
        raise ProviderHttpClientError("GROQ_STATUS_NOT_COMPLETED")
    if response.get("model") != GROQ_MODEL_ID:
        raise ProviderHttpClientError("GROQ_MODEL_MISMATCH")
    output = response.get("output")
    if not isinstance(output, list):
        raise ProviderHttpClientError("GROQ_OUTPUT_INVALID")

    texts: list[str] = []
    for item in output:
        if not isinstance(item, Mapping):
            raise ProviderHttpClientError("GROQ_OUTPUT_ITEM_INVALID")
        item_type = item.get("type")
        if item_type == "reasoning":
            continue
        if item_type != "message":
            raise ProviderHttpClientError("GROQ_UNEXPECTED_OUTPUT_ITEM")
        if item.get("status") not in (None, "completed"):
            raise ProviderHttpClientError("GROQ_MESSAGE_NOT_COMPLETED")
        content = item.get("content")
        if not isinstance(content, list):
            raise ProviderHttpClientError("GROQ_CONTENT_INVALID")
        for part in content:
            if not isinstance(part, Mapping) or part.get("type") != "output_text":
                raise ProviderHttpClientError("GROQ_UNEXPECTED_CONTENT")
            text = part.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ProviderHttpClientError("GROQ_OUTPUT_TEXT_INVALID")
            texts.append(text)

    if len(texts) != 1:
        raise ProviderHttpClientError("GROQ_OUTPUT_TEXT_COUNT")
    return texts[0]
