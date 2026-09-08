from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from research.e2.tool_registry import TOOLS

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
    _provider_audit_model_id,
)
from .release_provider_v13 import Release0ProviderDecisionSourceV13, _schema_for_visible_tools_v13
from .release_provider_v14 import (
    RELEASE0_V14_SYSTEM_INSTRUCTION,
    _nonnegative_int_or_none,
    _provider_request_text,
    build_release_provider_decision_source_v14,
    validate_release_provider_config_v14,
)


NVIDIA_PROVIDER_ID = "nvidia"
NVIDIA_MODEL_ID = "openai/gpt-oss-120b"
NVIDIA_ROUTE_ID = "nvidia.chat_completions.v1.gpt_oss_120b"
NVIDIA_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_ACCOUNT_SENTINEL = "nvidia"

RELEASE0_V15_PROVIDER_VERSION = "release0-provider-nvidia-v15"


def _accept_nvidia_completion_content(*, finish_reason: Any, content: Any) -> str:
    """Accept only a complete structured decision without repairing provider output.

    V15 preserves V14's bounded tolerance for ``finish_reason=length``: it is accepted only when
    the emitted content is already an independently parseable JSON object. No retry, truncation
    repair, schema relaxation, or alternate route is introduced.
    """

    if finish_reason not in ("stop", "length"):
        raise ProviderHttpClientError("NVIDIA_FINISH_REASON_INVALID")
    if not isinstance(content, str) or not content.strip():
        raise ProviderHttpClientError("NVIDIA_OUTPUT_TEXT_INVALID")
    if finish_reason == "length":
        try:
            decoded = json.loads(content)
        except Exception:
            raise ProviderHttpClientError("NVIDIA_FINISH_REASON_INVALID") from None
        if not isinstance(decoded, Mapping):
            raise ProviderHttpClientError("NVIDIA_FINISH_REASON_INVALID")
    return content


class Release0NvidiaDecisionClientV15:
    """One-shot direct NVIDIA client preserving the accepted V14 agent semantics.

    The product-facing decision contract remains strict JSON. Native NVIDIA ``tool_calls`` are
    compatibility-probed separately, but are deliberately rejected at this boundary because the
    generic Release 0 controller owns tool selection/execution. The client performs no fallback,
    retry, provider-side tool execution, output repair, or credential lookup.
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
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("NVIDIA client requires an explicit non-empty api_key")
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
        }
        return ProviderHttpRequest(
            method="POST",
            url=NVIDIA_ENDPOINT,
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
        except ProviderHttpClientError as exc:
            if exc.status_code == 404:
                raise ProviderHttpClientError("NVIDIA_ROUTE_NOT_FOUND", status_code=404) from None
            raise
        except Exception:
            raise ProviderHttpClientError("TRANSPORT_FAILURE") from None
        if not isinstance(response, ProviderHttpResponse):
            raise ProviderHttpClientError("TRANSPORT_RESPONSE_INVALID")
        if response.status_code == 404:
            raise ProviderHttpClientError("NVIDIA_ROUTE_NOT_FOUND", status_code=404)
        if response.status_code < 200 or response.status_code >= 300:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=response.status_code)
        if not isinstance(response.body, Mapping):
            raise ProviderHttpClientError("HTTP_JSON_NOT_OBJECT")
        return response.body

    def complete(self, request: ProviderDecisionRequest) -> str:
        response = self._invoke_once(self.build_http_request(request))
        served_model = response.get("model")
        if served_model is not None and served_model != self.model_id:
            raise ProviderHttpClientError("NVIDIA_MODEL_MISMATCH")

        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("NVIDIA_CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("NVIDIA_CHOICE_INVALID")
        if choice.get("index") not in (None, 0):
            raise ProviderHttpClientError("NVIDIA_CHOICE_INDEX_INVALID")

        message = choice.get("message")
        if not isinstance(message, Mapping) or message.get("role") != "assistant":
            raise ProviderHttpClientError("NVIDIA_MESSAGE_INVALID")
        if message.get("tool_calls") not in (None, []):
            raise ProviderHttpClientError("NVIDIA_TOOL_CALL_REJECTED")
        if message.get("function_call") is not None:
            raise ProviderHttpClientError("NVIDIA_FUNCTION_CALL_REJECTED")
        content = _accept_nvidia_completion_content(
            finish_reason=choice.get("finish_reason"),
            content=message.get("content"),
        )

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


def validate_release_provider_config_v15(config: RemoteProductionConfig) -> None:
    """Add the exact direct NVIDIA route while preserving every V14 provider path unchanged."""

    if not config.provider_calls_enabled:
        return
    if config.provider_id != NVIDIA_PROVIDER_ID:
        validate_release_provider_config_v14(config)
        return
    if config.provider_selection_state != PROVISIONAL_RELEASE_PROVIDER_STATE:
        raise RuntimeError("release_provider_state_not_provisional")
    if config.provider_model_id != NVIDIA_MODEL_ID:
        raise RuntimeError("release_provider_model_not_supported")
    if config.provider_account_id != NVIDIA_ACCOUNT_SENTINEL:
        raise RuntimeError("release_provider_account_id_invalid")
    if config.provider_api_token is None:
        raise RuntimeError("release_provider_api_token_missing")
    if config.cost_policy != "usd0-hard-gate" or config.paid_fallback_enabled:
        raise RuntimeError("release_provider_usd0_hard_gate_required")
    if not config.tractian_transport_enabled:
        raise RuntimeError("release_provider_requires_real_tractian_transport")


def build_release_provider_decision_source_v15(
    *,
    config: RemoteProductionConfig,
    transport: ProviderJsonTransport | None = None,
) -> ProviderDecisionSource:
    validate_release_provider_config_v15(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    assert config.provider_id is not None
    assert config.provider_model_id is not None
    assert config.provider_api_token is not None

    if config.provider_id != NVIDIA_PROVIDER_ID:
        return build_release_provider_decision_source_v14(config=config, transport=transport)

    client = Release0NvidiaDecisionClientV15(
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


def build_release_provider_decision_source_factory_v15(config: RemoteProductionConfig):
    validate_release_provider_config_v15(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v15(config=config)
