from __future__ import annotations

import json
from typing import Any, Mapping

import pytest

from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_MAX_COMPLETION_TOKENS,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_CLIENT_VERSION,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from academy_tractian.decision_source import ProviderDecisionRequest
from academy_tractian.provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext


SECRET = "cf-test-super-secret-token"
ACCOUNT_ID = "0123456789abcdef0123456789abcdef"


class ScriptedJsonTransport:
    def __init__(self, *responses: object) -> None:
        self.responses = list(responses)
        self.calls: list[ProviderHttpRequest] = []

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls.append(request)
        if not self.responses:
            raise AssertionError("transport script exhausted")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        if isinstance(item, ProviderHttpResponse):
            return item
        if isinstance(item, Mapping):
            return ProviderHttpResponse(status_code=200, body=dict(item))
        raise AssertionError("unsupported scripted response")


def _provider_request() -> ProviderDecisionRequest:
    registry = canonical_tool_registry()
    payload = {
        "schema_version": "provider-decision-request-v1",
        "adapter_version": "provider-decision-adapter-v1",
        "user_request": "Inspect asset asset_dev_probe_001.",
        "turn_index": 0,
        "tool_call_count": 0,
        "observations": [],
        "tools": [
            {
                "name": tool.name,
                "operation_id": tool.operation_id,
                "method": tool.method,
                "path_template": tool.path_template,
                "kind": tool.kind.value,
                "description": tool.description,
                "parameters": [
                    {
                        "name": parameter.name,
                        "location": parameter.location,
                        "required": parameter.required,
                        "parameter_schema": parameter.parameter_schema,
                    }
                    for parameter in tool.parameters
                ],
                "justification_required": tool.justification_required,
                "minimum_justification_length": tool.minimum_justification_length,
            }
            for tool in sorted(registry.values(), key=lambda item: item.name)
        ],
    }
    import hashlib

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    payload["request_sha256"] = hashlib.sha256(canonical).hexdigest()
    return ProviderDecisionRequest.model_validate(payload)


def _decision_json() -> str:
    return json.dumps(
        {
            "schema_version": "provider-decision-payload-v1",
            "kind": "ABSTAIN",
            "tool_name": None,
            "arguments": {},
            "evidence_id": None,
            "final": None,
            "message": "Cannot proceed safely.",
            "reason_code": "NO_SAFE_PATH",
        },
        sort_keys=True,
    )


def _cloudflare_response(
    content: str,
    *,
    model: str = CLOUDFLARE_GLM_MODEL_ID,
    finish_reason: str = "stop",
    usage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": finish_reason,
            }
        ],
        "usage": usage
        or {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
        },
    }


def _client(
    transport: ScriptedJsonTransport,
    *,
    model_id: str = CLOUDFLARE_GLM_MODEL_ID,
) -> CloudflareWorkersAIChatCompletionsDecisionClient:
    return CloudflareWorkersAIChatCompletionsDecisionClient(
        api_token=SECRET,
        account_id=ACCOUNT_ID,
        model_id=model_id,
        transport=transport,
    )


def _serialized_body(request: ProviderHttpRequest) -> str:
    return json.dumps(request.body, sort_keys=True)


def test_frozen_identity_is_explicit() -> None:
    assert CLOUDFLARE_PROVIDER_CLIENT_VERSION == "cloudflare-provider-client-v1"
    assert CLOUDFLARE_PROVIDER_ID == "cloudflare"
    assert CLOUDFLARE_ROUTE_ID == "cloudflare.workers_ai.openai_compat.chat_completions.v1"
    assert CLOUDFLARE_GLM_MODEL_ID == "@cf/zai-org/glm-4.7-flash"
    assert CLOUDFLARE_NEMOTRON_MODEL_ID == "@cf/nvidia/nemotron-3-120b-a12b"


def test_requires_explicit_credentials_and_frozen_model() -> None:
    transport = ScriptedJsonTransport()
    with pytest.raises(ValueError, match="api_token"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token="",
            account_id=ACCOUNT_ID,
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=transport,
        )
    with pytest.raises(ValueError, match="account_id"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=SECRET,
            account_id="",
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=transport,
        )
    with pytest.raises(ValueError, match="account_id"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=SECRET,
            account_id="bad/account",
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=transport,
        )
    with pytest.raises(ValueError, match="model_id"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=SECRET,
            account_id=ACCOUNT_ID,
            model_id="@cf/google/gemma-4-26b-a4b-it",
            transport=transport,
        )


@pytest.mark.parametrize("model_id", [CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID])
def test_builds_exact_direct_workers_ai_stateless_shape(model_id: str) -> None:
    transport = ScriptedJsonTransport(_cloudflare_response(_decision_json(), model=model_id))
    client = _client(transport, model_id=model_id)
    request = _provider_request()

    result = client.complete(request)

    assert result == _decision_json()
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.method == "POST"
    assert call.url == (
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1/chat/completions"
    )
    assert call.headers == {
        "Authorization": f"Bearer {SECRET}",
        "Content-Type": "application/json",
    }
    assert not any(key.lower().startswith("cf-aig") for key in call.headers)
    assert call.body["model"] == model_id
    assert call.body["temperature"] == 0
    assert call.body["n"] == 1
    assert call.body["stream"] is False
    assert call.body["max_completion_tokens"] == CLOUDFLARE_MAX_COMPLETION_TOKENS == 512
    assert call.body["store"] is False
    assert call.body["tool_choice"] == "none"
    assert call.body["parallel_tool_calls"] is False
    assert call.body["response_format"] == {
        "type": "json_schema",
        "json_schema": PROVIDER_DECISION_JSON_SCHEMA,
    }
    assert [message["role"] for message in call.body["messages"]] == ["system", "user"]
    assert "Inspect asset asset_dev_probe_001." in call.body["messages"][1]["content"]

    for forbidden_key in (
        "tools",
        "seed",
        "conversation",
        "previous_response_id",
        "gateway",
        "web_search",
    ):
        assert forbidden_key not in call.body

    serialized = _serialized_body(call)
    assert SECRET not in serialized
    assert "x-user-id" not in serialized
    assert '"user_id"' not in serialized
    assert '"identity_id"' not in serialized
    assert '"seed"' not in serialized


def test_repr_redacts_credentials() -> None:
    client = _client(ScriptedJsonTransport())
    rendered = repr(client)
    assert SECRET not in rendered
    assert ACCOUNT_ID not in rendered
    assert "<redacted>" in rendered


def test_records_usage_without_exposing_request_body() -> None:
    transport = ScriptedJsonTransport(
        _cloudflare_response(
            _decision_json(),
            usage={
                "prompt_tokens": 101,
                "completion_tokens": 21,
                "total_tokens": 122,
                "completion_tokens_details": {"reasoning_tokens": 4},
            },
        )
    )
    client = _client(transport)
    request = _provider_request()
    client.complete(request)
    records = client.drain_usage_records()
    assert len(records) == 1
    record = records[0]
    assert record.provider_id == CLOUDFLARE_PROVIDER_ID
    assert record.model_id == CLOUDFLARE_GLM_MODEL_ID
    assert record.route_id == CLOUDFLARE_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert record.input_tokens == 101
    assert record.output_tokens == 21
    assert record.total_tokens == 122
    assert record.reasoning_tokens == 4
    assert client.drain_usage_records() == ()


def test_rejects_http_non_success_without_retry() -> None:
    transport = ScriptedJsonTransport(ProviderHttpResponse(status_code=429, body={"error": "quota"}))
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "HTTP_STATUS"
    assert exc_info.value.status_code == 429
    assert len(transport.calls) == 1


def test_rejects_transport_failure_without_retry() -> None:
    transport = ScriptedJsonTransport(RuntimeError("network details"))
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "TRANSPORT_FAILURE"
    assert len(transport.calls) == 1


def test_rejects_provider_error_shape() -> None:
    transport = ScriptedJsonTransport({"success": False, "errors": [{"code": 1000}]})
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_OBJECT_INVALID"


def test_rejects_model_route_substitution() -> None:
    transport = ScriptedJsonTransport(
        _cloudflare_response(_decision_json(), model=CLOUDFLARE_NEMOTRON_MODEL_ID)
    )
    client = _client(transport, model_id=CLOUDFLARE_GLM_MODEL_ID)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_MODEL_MISMATCH"


def test_rejects_non_stop_finish_reason() -> None:
    transport = ScriptedJsonTransport(_cloudflare_response(_decision_json(), finish_reason="length"))
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_FINISH_REASON_INVALID"


def test_rejects_provider_side_tool_calls() -> None:
    response = _cloudflare_response(_decision_json())
    response["choices"][0]["message"]["tool_calls"] = [{"id": "tool-1"}]
    transport = ScriptedJsonTransport(response)
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_TOOL_CALL_REJECTED"


def test_rejects_legacy_function_call() -> None:
    response = _cloudflare_response(_decision_json())
    response["choices"][0]["message"]["function_call"] = {"name": "legacy"}
    transport = ScriptedJsonTransport(response)
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_FUNCTION_CALL_REJECTED"


def test_rejects_refusal_content() -> None:
    response = _cloudflare_response(_decision_json())
    response["choices"][0]["message"]["refusal"] = "refusal"
    transport = ScriptedJsonTransport(response)
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_REFUSAL_REJECTED"


def test_rejects_empty_output() -> None:
    transport = ScriptedJsonTransport(_cloudflare_response(""))
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "CLOUDFLARE_OUTPUT_TEXT_INVALID"


def test_rejects_non_object_http_body() -> None:
    transport = ScriptedJsonTransport(
        ProviderHttpResponse(status_code=200, body=["unexpected"])  # type: ignore[arg-type]
    )
    client = _client(transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert exc_info.value.code == "HTTP_JSON_NOT_OBJECT"
