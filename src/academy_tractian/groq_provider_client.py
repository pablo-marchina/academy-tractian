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


GROQ_PROVIDER_CLIENT_VERSION = "groq-provider-client-v1"
GROQ_PROVIDER_ID = "groq"
GROQ_ROUTE_ID = "groq.openai_compat.chat_completions.v1"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_GPT_OSS_120B_MODEL_ID = "openai/gpt-oss-120b"
GROQ_ALLOWED_MODEL_IDS = frozenset({GROQ_GPT_OSS_120B_MODEL_ID})
GROQ_MAX_COMPLETION_TOKENS = 2048


def _provider_request_text(request: ProviderDecisionRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _schema_copy() -> dict[str, Any]:
    return json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


class GroqChatCompletionsDecisionClient:
    """One-shot Groq decision client for the hosted live-demo challenger.

    The application keeps tool execution and relational validation. Provider-side tool use,
    retries and output repair are intentionally disabled. Structured output is requested in
    best-effort mode because the canonical ProviderDecision schema deliberately leaves nested
    tool arguments/final payloads open for downstream validation.
    """

    provider_id = GROQ_PROVIDER_ID
    route_id = GROQ_ROUTE_ID

    def __init__(
        self,
        *,
        api_key: str,
        transport: ProviderJsonTransport,
        model_id: str = GROQ_GPT_OSS_120B_MODEL_ID,
        timeout_seconds: float = 45.0,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("Groq client requires an explicit non-empty api_key")
        if model_id not in GROQ_ALLOWED_MODEL_IDS:
            raise ValueError("Groq model_id is not allowed by LIVE-DEMO-PROVIDER-001")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._transport = transport
        self.model_id = model_id
        self._timeout_seconds = float(timeout_seconds)
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(provider_id={self.provider_id!r}, "
            f"model_id={self.model_id!r}, route_id={self.route_id!r}, api_key=<redacted>)"
        )

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage_records)
        self._usage_records.clear()
        return records

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": _provider_request_text(request)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "provider_decision_payload",
                    "strict": False,
                    "schema": _schema_copy(),
                },
            },
            "reasoning_effort": "medium",
            "include_reasoning": False,
            "stream": False,
            "max_completion_tokens": GROQ_MAX_COMPLETION_TOKENS,
        }
        return ProviderHttpRequest(
            method="POST",
            url=GROQ_ENDPOINT,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        response = self._invoke_once(self.build_http_request(request))
        usage = response.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        completion_details = usage_map.get("completion_tokens_details")
        completion_details_map = (
            completion_details if isinstance(completion_details, Mapping) else {}
        )
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(usage_map.get("prompt_tokens")),
                output_tokens=_nonnegative_int_or_none(usage_map.get("completion_tokens")),
                total_tokens=_nonnegative_int_or_none(usage_map.get("total_tokens")),
                reasoning_tokens=_nonnegative_int_or_none(
                    completion_details_map.get("reasoning_tokens")
                ),
            )
        )
        return self._extract_output(response)

    def _invoke_once(self, request: ProviderHttpRequest) -> Mapping[str, Any]:
        try:
            response = self._transport.post_json(request)
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
        return response.body

    def _extract_output(self, response: Mapping[str, Any]) -> str:
        if response.get("object") != "chat.completion":
            raise ProviderHttpClientError("GROQ_OBJECT_INVALID")
        if response.get("model") != self.model_id:
            raise ProviderHttpClientError("GROQ_MODEL_MISMATCH")
        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("GROQ_CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("GROQ_CHOICE_INVALID")
        if choice.get("index") not in (None, 0):
            raise ProviderHttpClientError("GROQ_CHOICE_INDEX_INVALID")
        if choice.get("finish_reason") != "stop":
            raise ProviderHttpClientError("GROQ_FINISH_REASON_INVALID")
        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ProviderHttpClientError("GROQ_MESSAGE_INVALID")
        if message.get("role") != "assistant":
            raise ProviderHttpClientError("GROQ_ROLE_INVALID")
        if message.get("tool_calls") not in (None, []):
            raise ProviderHttpClientError("GROQ_TOOL_CALL_REJECTED")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderHttpClientError("GROQ_OUTPUT_TEXT_INVALID")
        return content
