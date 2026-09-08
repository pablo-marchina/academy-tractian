from __future__ import annotations

import ast
import inspect
import json
from typing import Any

import pytest

import academy_tractian.nvidia_provider_client as nvidia_module
from academy_tractian.decision_source import ProviderDecisionSource, build_provider_decision_request
from academy_tractian.nvidia_provider_client import (
    NVIDIA_CHAT_COMPLETIONS_ENDPOINT,
    NVIDIA_DECISION_MAX_TOKENS,
    NVIDIA_MODEL_ID,
    NVIDIA_ROUTE_ID,
    NvidiaChatCompletionsDecisionClient,
)
from academy_tractian.provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerDecisionKind


SECRET = "unit-test-nvidia-secret-never-serialize"


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


def _nvidia_response(
    text: str,
    *,
    model: str = NVIDIA_MODEL_ID,
    finish_reason: str = "stop",
    choices_count: int = 1,
    tool_calls: Any = None,
) -> ProviderHttpResponse:
    choice = {
        "index": 0,
        "finish_reason": finish_reason,
        "message": {
            "role": "assistant",
            "content": text,
            "reasoning_content": "private-provider-reasoning-must-not-surface",
            "tool_calls": tool_calls,
        },
    }
    return ProviderHttpResponse(
        status_code=200,
        body={
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "model": model,
            "choices": [dict(choice) for _ in range(choices_count)],
            "usage": {
                "prompt_tokens": 101,
                "completion_tokens": 23,
                "total_tokens": 124,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        },
    )


def test_client_imports_no_environment_or_provider_sdk_or_private_evaluator() -> None:
    source = inspect.getsource(nvidia_module)
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
    assert imported_roots.isdisjoint({"openai", "nvidia", "langgraph", "pydantic_ai"})
    assert "getenv" not in source
    assert "environ" not in source
    assert "NVIDIA_API_KEY" not in source
    assert not any(module.startswith("research.e2.evaluator") for module in imported_modules)
    assert "FRESH_BLIND" not in source
    assert "LEGACY_LOCKED_TEST" not in source


def test_builds_exact_hosted_guided_json_request_without_secret_or_private_state() -> None:
    client = NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=ScriptedJsonTransport())
    request = _provider_request()

    call = client.build_http_request(request)

    assert call.method == "POST"
    assert call.url == NVIDIA_CHAT_COMPLETIONS_ENDPOINT
    assert call.headers["Authorization"] == f"Bearer {SECRET}"
    assert call.body["model"] == NVIDIA_MODEL_ID
    assert call.body["temperature"] == 1.0
    assert call.body["top_p"] == 0.95
    assert call.body["max_tokens"] == NVIDIA_DECISION_MAX_TOKENS
    assert call.body["n"] == 1
    assert call.body["stream"] is False
    assert call.body["chat_template_kwargs"] == {"enable_thinking": False}
    assert call.body["guided_json"] == PROVIDER_DECISION_JSON_SCHEMA
    assert call.body["guided_json"] is not PROVIDER_DECISION_JSON_SCHEMA
    assert call.body["messages"][0] == {"role": "system", "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION}
    assert call.body["messages"][1]["role"] == "user"
    assert "tools" not in call.body
    assert "response_format" not in call.body

    serialized = json.dumps(call.body, sort_keys=True, separators=(",", ":"))
    assert SECRET not in serialized
    assert "x-user-id" not in serialized
    assert '"user_id"' not in serialized
    assert '"identity_id"' not in serialized
    assert "actions_enabled" not in serialized
    assert "idempotency" not in serialized
    assert "gold" not in serialized.lower()
    assert SECRET not in repr(call)
    assert SECRET not in repr(client)


def test_valid_response_integrates_with_strict_provider_decision_source() -> None:
    response = _nvidia_response(
        _decision_json(
            "TOOL",
            tool_name="get_asset",
            arguments={"asset_id": "asset-1"},
            evidence_id="ev-asset",
            message=None,
            reason_code=None,
        )
    )
    transport = ScriptedJsonTransport(response)
    client = NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())

    decision = source.decide(
        ControllerContext(user_request="Inspect asset-1", turn_index=0, tool_call_count=0)
    )

    assert decision.kind is ControllerDecisionKind.TOOL
    assert decision.proposal is not None
    assert decision.proposal.tool_name == "get_asset"
    assert decision.proposal.arguments == {"asset_id": "asset-1"}
    assert len(transport.calls) == 1


def test_private_reasoning_content_is_never_returned() -> None:
    decision = _decision_json("CLARIFY", message="Need asset id", reason_code="MISSING_ASSET")
    client = NvidiaChatCompletionsDecisionClient(
        api_key=SECRET,
        transport=ScriptedJsonTransport(_nvidia_response(decision)),
    )

    result = client.complete(_provider_request())

    assert result == decision
    assert "private-provider-reasoning" not in result


@pytest.mark.parametrize(
    ("response", "error_code"),
    [
        (_nvidia_response(_decision_json(), model="nvidia/model-drift"), "NVIDIA_MODEL_MISMATCH"),
        (_nvidia_response(_decision_json(), finish_reason="length"), "NVIDIA_FINISH_REASON_INVALID"),
        (_nvidia_response(_decision_json(), choices_count=2), "NVIDIA_CHOICES_INVALID"),
        (_nvidia_response(_decision_json(), tool_calls=[{"id": "unexpected"}]), "NVIDIA_UNEXPECTED_TOOL_CALLS"),
    ],
)
def test_provider_shape_drift_fails_closed_after_one_transport_call(response, error_code) -> None:
    transport = ScriptedJsonTransport(response)
    client = NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError, match=error_code):
        client.complete(_provider_request())

    assert len(transport.calls) == 1


def test_transport_exception_is_sanitized_and_never_retried() -> None:
    transport = ScriptedJsonTransport(RuntimeError(f"backend leaked {SECRET}"))
    client = NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())

    assert str(exc_info.value) == "TRANSPORT_FAILURE"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_non_success_http_status_is_sanitized_and_never_retried() -> None:
    transport = ScriptedJsonTransport(ProviderHttpResponse(status_code=429, body={"secret": SECRET}))
    client = NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())

    assert str(exc_info.value) == "HTTP_STATUS:429"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_usage_is_sanitized_separate_and_drainable() -> None:
    transport = ScriptedJsonTransport(_nvidia_response(_decision_json()))
    client = NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    request = _provider_request()

    client.complete(request)
    records = client.drain_usage_records()

    assert len(records) == 1
    record = records[0]
    assert record.provider_id == "nvidia"
    assert record.model_id == NVIDIA_MODEL_ID
    assert record.route_id == NVIDIA_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert (record.input_tokens, record.output_tokens, record.total_tokens, record.reasoning_tokens) == (101, 23, 124, 0)
    assert SECRET not in repr(record)
    assert client.drain_usage_records() == ()


def test_constructor_rejects_invalid_credentials_timeout_and_token_budget() -> None:
    with pytest.raises(ValueError, match="explicit non-empty api_key"):
        NvidiaChatCompletionsDecisionClient(api_key="", transport=ScriptedJsonTransport())
    with pytest.raises(ValueError, match="timeout_seconds"):
        NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=ScriptedJsonTransport(), timeout_seconds=0)
    with pytest.raises(ValueError, match="max_tokens"):
        NvidiaChatCompletionsDecisionClient(api_key=SECRET, transport=ScriptedJsonTransport(), max_tokens=0)
