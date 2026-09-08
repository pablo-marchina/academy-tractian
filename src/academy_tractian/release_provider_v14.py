from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import CLOUDFLARE_PROVIDER_ID
from .decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    ProviderUsageRecord,
    UrllibProviderJsonTransport,
)
from .release_provider import (
    PROVISIONAL_RELEASE_PROVIDER_STATE,
    RELEASE0_MAX_COMPLETION_TOKENS,
    RELEASE0_PROVIDER_SYSTEM_INSTRUCTION,
    _provider_audit_model_id,
    validate_release_provider_config,
)
from .release_provider_v11 import RELEASE0_V11_RESPONSE_MODE_INSTRUCTION
from .release_provider_v12 import RELEASE0_V12_GROUNDING_INSTRUCTION
from .release_provider_v13 import (
    RELEASE0_V13_GROUNDING_INSTRUCTION,
    Release0ProviderDecisionSourceV13,
    _schema_for_visible_tools_v13,
    build_release_provider_decision_source_v13,
)


OPENROUTER_PROVIDER_ID = "openrouter"
OPENROUTER_MODEL_ID = "nvidia/nemotron-3-super-120b-a12b:free"
OPENROUTER_ROUTE_ID = "openrouter.chat_completions.v1.fixed_free"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_ACCOUNT_SENTINEL = "openrouter"

RELEASE0_V14_PROVIDER_VERSION = "release0-provider-failover-v14"
RELEASE0_V14_SYSTEM_INSTRUCTION = "\n\n".join(
    (
        RELEASE0_PROVIDER_SYSTEM_INSTRUCTION,
        RELEASE0_V11_RESPONSE_MODE_INSTRUCTION,
        RELEASE0_V12_GROUNDING_INSTRUCTION,
        RELEASE0_V13_GROUNDING_INSTRUCTION,
    )
)


def _provider_request_text(request: ProviderDecisionRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


class Release0OpenRouterDecisionClientV14:
    """One-shot fixed-free OpenRouter client preserving the accepted V13 agent semantics.

    The model is pinned to a ``:free`` route proven to support the production JSON schema. The
    request explicitly disables model/provider fallback and requires parameter support so the USD0
    hard gate cannot silently degrade into another model or a paid route. The client performs no
    retry, output repair, credential lookup, or provider-side tool execution.
    """

    provider_id = OPENROUTER_PROVIDER_ID
    model_id = OPENROUTER_MODEL_ID
    route_id = OPENROUTER_ROUTE_ID

    def __init__(
        self,
        *,
        api_key: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("OpenRouter client requires an explicit non-empty api_key")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key.strip()
        self._transport = transport
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
                {"role": "system", "content": RELEASE0_V14_SYSTEM_INSTRUCTION},
                {"role": "user", "content": _provider_request_text(request)},
            ],
            "temperature": 0,
            "n": 1,
            "stream": False,
            "max_tokens": RELEASE0_MAX_COMPLETION_TOKENS,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "release0_decision",
                    "strict": True,
                    "schema": _schema_for_visible_tools_v13(request),
                },
            },
            "provider": {
                "allow_fallbacks": False,
                "require_parameters": True,
            },
        }
        return ProviderHttpRequest(
            method="POST",
            url=OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

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

    def complete(self, request: ProviderDecisionRequest) -> str:
        response = self._invoke_once(self.build_http_request(request))
        served_model = response.get("model")
        # OpenRouter's structured-output path may omit model; when present it must remain pinned.
        if served_model is not None and served_model != self.model_id:
            raise ProviderHttpClientError("OPENROUTER_MODEL_MISMATCH")

        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("OPENROUTER_CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("OPENROUTER_CHOICE_INVALID")
        if choice.get("index") not in (None, 0):
            raise ProviderHttpClientError("OPENROUTER_CHOICE_INDEX_INVALID")
        if choice.get("finish_reason") != "stop":
            raise ProviderHttpClientError("OPENROUTER_FINISH_REASON_INVALID")

        message = choice.get("message")
        if not isinstance(message, Mapping) or message.get("role") != "assistant":
            raise ProviderHttpClientError("OPENROUTER_MESSAGE_INVALID")
        if message.get("tool_calls") not in (None, []):
            raise ProviderHttpClientError("OPENROUTER_TOOL_CALL_REJECTED")
        if message.get("function_call") is not None:
            raise ProviderHttpClientError("OPENROUTER_FUNCTION_CALL_REJECTED")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderHttpClientError("OPENROUTER_OUTPUT_TEXT_INVALID")

        usage = response.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        completion_details = usage_map.get("completion_tokens_details")
        completion_map = completion_details if isinstance(completion_details, Mapping) else {}
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(usage_map.get("prompt_tokens")),
                output_tokens=_nonnegative_int_or_none(usage_map.get("completion_tokens")),
                total_tokens=_nonnegative_int_or_none(usage_map.get("total_tokens")),
                reasoning_tokens=_nonnegative_int_or_none(completion_map.get("reasoning_tokens")),
            )
        )
        return content


def validate_release_provider_config_v14(config: RemoteProductionConfig) -> None:
    """Accept the historical Cloudflare route or the exact tested OpenRouter USD0 route only."""

    if not config.provider_calls_enabled:
        return
    if config.provider_id == CLOUDFLARE_PROVIDER_ID:
        validate_release_provider_config(config)
        return
    if config.provider_selection_state != PROVISIONAL_RELEASE_PROVIDER_STATE:
        raise RuntimeError("release_provider_state_not_provisional")
    if config.provider_id != OPENROUTER_PROVIDER_ID:
        raise RuntimeError("release_provider_not_supported")
    if config.provider_model_id != OPENROUTER_MODEL_ID:
        raise RuntimeError("release_provider_model_not_supported")
    if config.provider_account_id != OPENROUTER_ACCOUNT_SENTINEL:
        raise RuntimeError("release_provider_account_id_invalid")
    if config.provider_api_token is None:
        raise RuntimeError("release_provider_api_token_missing")
    if config.cost_policy != "usd0-hard-gate" or config.paid_fallback_enabled:
        raise RuntimeError("release_provider_usd0_hard_gate_required")
    if not config.tractian_transport_enabled:
        raise RuntimeError("release_provider_requires_real_tractian_transport")


def build_release_provider_decision_source_v14(
    *,
    config: RemoteProductionConfig,
    transport: ProviderJsonTransport | None = None,
) -> ProviderDecisionSource:
    validate_release_provider_config_v14(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    assert config.provider_id is not None
    assert config.provider_model_id is not None
    assert config.provider_api_token is not None

    if config.provider_id == CLOUDFLARE_PROVIDER_ID:
        if transport is not None:
            raise RuntimeError("release_cloudflare_v13_custom_transport_not_supported")
        return build_release_provider_decision_source_v13(config=config)

    client = Release0OpenRouterDecisionClientV14(
        api_key=config.provider_api_token.get_secret_value(),
        transport=transport or UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSourceV13(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory_v14(config: RemoteProductionConfig):
    validate_release_provider_config_v14(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v14(config=config)
