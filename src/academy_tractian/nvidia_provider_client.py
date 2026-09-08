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


NVIDIA_PROVIDER_ID = "nvidia"
NVIDIA_MODEL_ID = "nvidia/nemotron-3-super-120b-a12b"
NVIDIA_ROUTE_ID = "nvidia.chat_completions.v1.guided_json"
NVIDIA_CHAT_COMPLETIONS_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_DECISION_MAX_TOKENS = 2048


def _canonical_request_text(request: ProviderDecisionRequest) -> str:
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


class NvidiaChatCompletionsDecisionClient:
    """One-shot NVIDIA hosted decision client with guided JSON and no provider fallback.

    This adapter deliberately owns only provider I/O. The application-owned
    ProviderDecisionSource remains authoritative for relational schema validation,
    known-tool validation, and controller policy. The client never reads credentials
    from process state and never exposes provider reasoning content.
    """

    provider_id = NVIDIA_PROVIDER_ID
    model_id = NVIDIA_MODEL_ID
    route_id = NVIDIA_ROUTE_ID

    def __init__(
        self,
        *,
        api_key: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
        max_tokens: int = NVIDIA_DECISION_MAX_TOKENS,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("provider client requires an explicit non-empty api_key")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer")
        self._api_key = api_key
        self._transport = transport
        self._timeout_seconds = float(timeout_seconds)
        self._max_tokens = max_tokens
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(provider_id={self.provider_id!r}, "
            f"model_id={self.model_id!r}, route_id={self.route_id!r}, "
            f"max_tokens={self._max_tokens!r}, api_key=<redacted>)"
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
                {"role": "user", "content": _canonical_request_text(request)},
            ],
            # NVIDIA Nemotron 3 Super model-card recommendation.
            "temperature": 1.0,
            "top_p": 0.95,
            "max_tokens": self._max_tokens,
            "n": 1,
            "stream": False,
            # Keep private reasoning disabled. The application needs only the
            # controller decision payload and must not expose chain-of-thought.
            "chat_template_kwargs": {"enable_thinking": False},
            # NVIDIA NIM recommends guided_json over json_object for reliable
            # downstream structured generation.
            "guided_json": _schema_copy(),
        }
        return ProviderHttpRequest(
            method="POST",
            url=NVIDIA_CHAT_COMPLETIONS_ENDPOINT,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        call = self.build_http_request(request)
        try:
            response = self._transport.post_json(call)
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

        text = _extract_nvidia_output(response.body)
        usage = response.body.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        completion_details = usage_map.get("completion_tokens_details")
        completion_details_map = completion_details if isinstance(completion_details, Mapping) else {}
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(usage_map.get("prompt_tokens")),
                output_tokens=_nonnegative_int_or_none(usage_map.get("completion_tokens")),
                total_tokens=_nonnegative_int_or_none(usage_map.get("total_tokens")),
                reasoning_tokens=_nonnegative_int_or_none(completion_details_map.get("reasoning_tokens")),
            )
        )
        return text


def _extract_nvidia_output(response: Mapping[str, Any]) -> str:
    if response.get("model") != NVIDIA_MODEL_ID:
        raise ProviderHttpClientError("NVIDIA_MODEL_MISMATCH")

    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ProviderHttpClientError("NVIDIA_CHOICES_INVALID")
    choice = choices[0]
    if not isinstance(choice, Mapping):
        raise ProviderHttpClientError("NVIDIA_CHOICE_INVALID")
    if choice.get("finish_reason") != "stop":
        raise ProviderHttpClientError("NVIDIA_FINISH_REASON_INVALID")

    message = choice.get("message")
    if not isinstance(message, Mapping):
        raise ProviderHttpClientError("NVIDIA_MESSAGE_INVALID")
    if message.get("role") not in (None, "assistant"):
        raise ProviderHttpClientError("NVIDIA_MESSAGE_ROLE_INVALID")
    if message.get("tool_calls") not in (None, []):
        raise ProviderHttpClientError("NVIDIA_UNEXPECTED_TOOL_CALLS")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ProviderHttpClientError("NVIDIA_CONTENT_INVALID")
    return content
