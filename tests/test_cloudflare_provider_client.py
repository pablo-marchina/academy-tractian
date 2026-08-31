from __future__ import annotations

import ast
import inspect
import json
from typing import Any

import pytest

import academy_tractian.cloudflare_provider_client as cloudflare_module
from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_ALLOWED_MODEL_IDS,
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_MAX_COMPLETION_TOKENS,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from academy_tractian.decision_source import ProviderDecisionSource, build_provider_decision_request
from academy_tractian.provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerDecisionKind


SECRET = "cloudflare-unit-test-token-never-serialize"
ACCOUNT_ID = "0123456789abcdef0123456789abcdef"


class ScriptedJsonTransport:
    def __init__(self, *responses: ProviderHttpResponse | Exception) -> None:
        self.responses = list(responses)
        self.calls: list[ProviderHttpRequest] = []

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls.append(request)
        if not self.responses:
            raise AssertionError("transport script exhausted")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _provider_request():
    return build_provider_decision_request(
        context=ControllerContext(
            user_request="Inspect asset asset_dev_probe_001.",
            turn_index=0,
            tool_call_count=0,
        ),
        registry=canonical_tool_registry(),
    )


def _decision_json(kind: str = "ABSTAIN", **overrides: Any) -> str:
    payload: dict[str, Any] = {
        "schema_version": "provider-decision-payload-v1",
        "kind": kind,
        "tool_name": None,
        "arguments": {},
        "evidence_id": None,
        "final": None,
        "message": "Cannot safely continue.",
        "reason_code": "NO_SAFE_PATH",
    }
    payload.update(overrides)
    return json.dumps(payload, sort_keys=True)


def _cloudflare_response(
    text: str,
    *,
    model: str = CLOUDFLARE_GLM_MODEL_ID,
    finish_reason: str = "stop",
    message_overrides: dict[str, Any] | None = None,
    usage: dict[str, Any] | None = None,
) -> ProviderHttpResponse:
    message: dict[str, Any] = {
        "role": "assistant",
        "content": text,
    }
    if message_overrides:
        message.update(message_overrides)
    return ProviderHttpResponse(
        status_code=200,
        body={
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": message,
                    "finish_reason": finish_reason,
                }
            ],
            "usage": usage
            if usage is not None
            else {
                "prompt_tokens": 103,
                "completion_tokens": 19,
                "total_tokens": 122,
                "completion_tokens_details": {"reasoning_tokens": 7},
            },
        },
    )


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


def _serialized_body(call: ProviderHttpRequest) -> str:
    return json.dumps(call.body, sort_keys=True, separators=(",", ":"))


def test_cloudflare_module_has_no_environment_lookup_sdk_or_network_transport() -> None:
    source = inspect.getsource(cloudflare_module)
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
            imported_modules.add(node.module)

    assert "os" not in imported_roots
    assert "urllib" not in imported_roots
    assert "requests" not in imported_roots
    assert imported_roots.isdisjoint({"cloudflare", "openai", "httpx", "aiohttp"})
    assert "getenv" not in source
    assert "environ" not in source
    assert "CLOUDFLARE_API_TOKEN" not in source
    assert "CLOUDFLARE_ACCOUNT_ID" not in source
    assert not any(module.startswith("research.e2.evaluator") for module in imported_modules)


def test_constructor_accepts_only_adr018_models_and_explicit_values() -> None:
    for model_id in CLOUDFLARE_ALLOWED_MODEL_IDS:
        assert _client(ScriptedJsonTransport(), model_id=model_id).model_id == model_id

    with pytest.raises(ValueError, match="explicit non-empty api_token"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token="",
            account_id=ACCOUNT_ID,
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=ScriptedJsonTransport(),
        )
    with pytest.raises(ValueError, match="explicit non-empty account_id"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=SECRET,
            account_id=" ",
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=ScriptedJsonTransport(),
        )
    with pytest.raises(ValueError, match="ASCII letters and digits"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=SECRET,
            account_id="abc/../def",
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=ScriptedJsonTransport(),
        )
    with pytest.raises(ValueError, match="not frozen by ADR-018"):
        CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=SECRET,
            account_id=ACCOUNT_ID,
            model_id="@cf/google/gemma-4-26b-a4b-it",
            transport=ScriptedJsonTransport(),
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
    assert "actions_enabled" not in serialized
    assert "idempotency" not in serialized
    assert "gold" not in serialized.lower()
    assert SECRET not in repr(call)
    assert SECRET not in repr(client)
    assert ACCOUNT_ID not in repr(client)


def test_valid_cloudflare_response_integrates_with_strict_provider_decision_source() -> None:
    text = _decision_json(
        "TOOL",
        tool_name="get_asset",
        arguments={"asset_id": "asset-1"},
        evidence_id="ev-asset",
        message=None,
        reason_code=None,
    )
    transport = ScriptedJsonTransport(_cloudflare_response(text))
    client = _client(transport)
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())

    decision = source.decide(
        ControllerContext(user_request="Inspect asset-1", turn_index=0, tool_call_count=0)
    )

    assert decision.kind is ControllerDecisionKind.TOOL
    assert decision.proposal is not None
    assert decision.proposal.tool_name == "get_asset"
    assert decision.proposal.arguments == {"asset_id": "asset-1"}
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "response",
    [
        _cloudflare_response(_decision_json(), model=CLOUDFLARE_NEMOTRON_MODEL_ID),
        _cloudflare_response(_decision_json(), finish_reason="length"),
        ProviderHttpResponse(
            status_code=200,
            body={
                "object": "response",
                "model": CLOUDFLARE_GLM_MODEL_ID,
                "choices": [],
            },
        ),
    ],
)
def test_route_model_or_completion_shape_drift_fails_closed_after_one_call(
    response: ProviderHttpResponse,
) -> None:
    transport = ScriptedJsonTransport(response)
    client = _client(transport)

    with pytest.raises(ProviderHttpClientError):
        client.complete(_provider_request())

    assert len(transport.calls) == 1


def test_provider_native_tool_call_is_rejected() -> None:
    response = _cloudflare_response(
        _decision_json(),
        message_overrides={
            "content": None,
            "tool_calls": [
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "get_asset", "arguments": "{}"},
                }
            ],
        },
    )
    transport = ScriptedJsonTransport(response)
    client = _client(transport)

    with pytest.raises(ProviderHttpClientError, match="CLOUDFLARE_TOOL_CALL_REJECTED"):
        client.complete(_provider_request())
    assert len(transport.calls) == 1


def test_provider_function_call_and_refusal_are_rejected() -> None:
    function_transport = ScriptedJsonTransport(
        _cloudflare_response(
            _decision_json(),
            message_overrides={"function_call": {"name": "get_asset", "arguments": "{}"}},
        )
    )
    with pytest.raises(ProviderHttpClientError, match="CLOUDFLARE_FUNCTION_CALL_REJECTED"):
        _client(function_transport).complete(_provider_request())

    refusal_transport = ScriptedJsonTransport(
        _cloudflare_response(_decision_json(), message_overrides={"refusal": "blocked"})
    )
    with pytest.raises(ProviderHttpClientError, match="CLOUDFLARE_REFUSAL_REJECTED"):
        _client(refusal_transport).complete(_provider_request())


def test_transport_exception_is_sanitized_and_never_retried() -> None:
    transport = ScriptedJsonTransport(RuntimeError(f"backend leaked {SECRET}"))
    client = _client(transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())

    assert str(exc_info.value) == "TRANSPORT_FAILURE"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_http_failure_is_sanitized_and_never_retried() -> None:
    transport = ScriptedJsonTransport(
        ProviderHttpResponse(status_code=429, body={"secret": SECRET})
    )
    client = _client(transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())

    assert str(exc_info.value) == "HTTP_STATUS:429"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_usage_is_sanitized_exact_and_drainable() -> None:
    transport = ScriptedJsonTransport(_cloudflare_response(_decision_json()))
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
    assert (record.input_tokens, record.output_tokens, record.total_tokens, record.reasoning_tokens) == (
        103,
        19,
        122,
        7,
    )
    assert SECRET not in repr(record)
    assert client.drain_usage_records() == ()


def test_missing_or_invalid_usage_is_not_fabricated() -> None:
    transport = ScriptedJsonTransport(
        _cloudflare_response(
            _decision_json(),
            usage={
                "prompt_tokens": None,
                "completion_tokens": -1,
                "total_tokens": "122",
            },
        )
    )
    client = _client(transport)
    client.complete(_provider_request())

    record = client.drain_usage_records()[0]
    assert record.input_tokens is None
    assert record.output_tokens is None
    assert record.total_tokens is None
    assert record.reasoning_tokens is None


def test_schema_is_copied_per_request_and_top_level_remains_closed() -> None:
    transport = ScriptedJsonTransport()
    client = _client(transport)
    request = _provider_request()

    first = client.build_http_request(request)
    second = client.build_http_request(request)
    first_schema = first.body["response_format"]["json_schema"]
    second_schema = second.body["response_format"]["json_schema"]

    assert first_schema == PROVIDER_DECISION_JSON_SCHEMA
    assert first_schema is not PROVIDER_DECISION_JSON_SCHEMA
    assert second_schema is not first_schema
    assert first_schema["additionalProperties"] is False
    assert set(first_schema["required"]) == set(first_schema["properties"])
