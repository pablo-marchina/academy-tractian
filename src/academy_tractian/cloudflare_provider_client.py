from __future__ import annotations

import json
import re
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


CLOUDFLARE_PROVIDER_CLIENT_VERSION = "cloudflare-provider-client-v1"
CLOUDFLARE_PROVIDER_ID = "cloudflare"
CLOUDFLARE_ROUTE_ID = "cloudflare.workers_ai.openai_compat.chat_completions.v1"
CLOUDFLARE_ENDPOINT_TEMPLATE = (
    "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions"
)
CLOUDFLARE_GLM_MODEL_ID = "@cf/zai-org/glm-4.7-flash"
CLOUDFLARE_NEMOTRON_MODEL_ID = "@cf/nvidia/nemotron-3-120b-a12b"
CLOUDFLARE_ALLOWED_MODEL_IDS = frozenset(
    {CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID}
)
CLOUDFLARE_MAX_COMPLETION_TOKENS = 512
CLOUDFLARE_MAX_ACCOUNTED_PROMPT_TOKENS = 8000

_ACCOUNT_ID_RE = re.compile(r"^[A-Za-z0-9]+$")


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


class CloudflareWorkersAIChatCompletionsDecisionClient:
    """ADR-018 Cloudflare client with explicit credentials and one-shot transport only.

    This class intentionally performs no environment lookup, retry, fallback, provider-side
    tool execution, AI Gateway routing, or automatic output repair. The transport is injected
    so provider-free tests can validate the complete request/response contract without network
    access.
    """

    provider_id = CLOUDFLARE_PROVIDER_ID
    route_id = CLOUDFLARE_ROUTE_ID

    def __init__(
        self,
        *,
        api_token: str,
        account_id: str,
        model_id: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not isinstance(api_token, str) or not api_token.strip():
            raise ValueError("Cloudflare client requires an explicit non-empty api_token")
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("Cloudflare client requires an explicit non-empty account_id")
        normalized_account_id = account_id.strip()
        if not _ACCOUNT_ID_RE.fullmatch(normalized_account_id):
            raise ValueError("Cloudflare account_id must contain only ASCII letters and digits")
        if model_id not in CLOUDFLARE_ALLOWED_MODEL_IDS:
            raise ValueError("Cloudflare model_id is not frozen by ADR-018")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._api_token = api_token
        self._account_id = normalized_account_id
        self.model_id = model_id
        self._transport = transport
        self._timeout_seconds = float(timeout_seconds)
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(provider_id={self.provider_id!r}, "
            f"model_id={self.model_id!r}, route_id={self.route_id!r}, "
            "account_id=<redacted>, api_token=<redacted>)"
        )

    @property
    def endpoint(self) -> str:
        return CLOUDFLARE_ENDPOINT_TEMPLATE.format(account_id=self._account_id)

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
                "json_schema": _schema_copy(),
            },
            "temperature": 0,
            "n": 1,
            "stream": False,
            "max_completion_tokens": CLOUDFLARE_MAX_COMPLETION_TOKENS,
            "store": False,
            "tool_choice": "none",
            "parallel_tool_calls": False,
        }
        return ProviderHttpRequest(
            method="POST",
            url=self.endpoint,
            headers={
                "Authorization": f"Bearer {self._api_token}",
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
            raise ProviderHttpClientError("CLOUDFLARE_OBJECT_INVALID")
        if response.get("model") != self.model_id:
            raise ProviderHttpClientError("CLOUDFLARE_MODEL_MISMATCH")

        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("CLOUDFLARE_CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("CLOUDFLARE_CHOICE_INVALID")
        if choice.get("index") not in (None, 0):
            raise ProviderHttpClientError("CLOUDFLARE_CHOICE_INDEX_INVALID")
        if choice.get("finish_reason") != "stop":
            raise ProviderHttpClientError("CLOUDFLARE_FINISH_REASON_INVALID")

        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ProviderHttpClientError("CLOUDFLARE_MESSAGE_INVALID")
        if message.get("role") != "assistant":
            raise ProviderHttpClientError("CLOUDFLARE_ROLE_INVALID")

        tool_calls = message.get("tool_calls")
        if tool_calls not in (None, []):
            raise ProviderHttpClientError("CLOUDFLARE_TOOL_CALL_REJECTED")
        if message.get("function_call") is not None:
            raise ProviderHttpClientError("CLOUDFLARE_FUNCTION_CALL_REJECTED")
        refusal = message.get("refusal")
        if refusal not in (None, ""):
            raise ProviderHttpClientError("CLOUDFLARE_REFUSAL_REJECTED")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderHttpClientError("CLOUDFLARE_OUTPUT_TEXT_INVALID")
        return content
