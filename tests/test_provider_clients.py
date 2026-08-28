from __future__ import annotations

import ast
import inspect
import json
from typing import Any

import pytest

import academy_tractian.provider_clients as provider_clients_module
from academy_tractian.decision_source import ProviderDecisionSource, build_provider_decision_request
from academy_tractian.provider_clients import (
    GOOGLE_INTERACTIONS_ENDPOINT,
    GOOGLE_MODEL_ID,
    GOOGLE_ROUTE_ID,
    OPENAI_MODEL_ID,
    OPENAI_RESPONSES_ENDPOINT,
    OPENAI_ROUTE_ID,
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerDecisionKind


SECRET = "unit-test-secret-never-serialize"


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


def _openai_response(text: str, *, model: str = OPENAI_MODEL_ID, status: str = "completed") -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "object": "response",
            "status": status,
            "model": model,
            "output": [
                {"type": "reasoning", "id": "rs_1"},
                {
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": text}],
                },
            ],
            "usage": {
                "input_tokens": 101,
                "output_tokens": 17,
                "total_tokens": 118,
                "output_tokens_details": {"reasoning_tokens": 7},
            },
        },
    )


def _google_response(text: str, *, model: str = GOOGLE_MODEL_ID, status: str = "completed") -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "object": "interaction",
            "status": status,
            "model": model,
            "steps": [
                {"type": "thought", "signature": "opaque-provider-signature"},
                {"type": "model_output", "content": [{"type": "text", "text": text}]},
            ],
            "usage": {
                "total_input_tokens": 93,
                "total_output_tokens": 15,
                "total_thought_tokens": 11,
                "total_tokens": 119,
            },
        },
    )


def _serialized_body(call: ProviderHttpRequest) -> str:
    return json.dumps(call.body, sort_keys=True, separators=(",", ":"))


@pytest.mark.parametrize(
    "client_factory",
    [
        lambda transport: OpenAIResponsesDecisionClient(api_key=SECRET, transport=transport),
        lambda transport: GoogleInteractionsDecisionClient(api_key=SECRET, transport=transport),
    ],
)
def test_provider_clients_require_explicit_constructor_credentials_and_never_lookup_environment(client_factory) -> None:
    source = inspect.getsource(provider_clients_module)
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert "os" not in imported_roots
    assert "getenv" not in source
    assert "environ" not in source
    assert "OPENAI_API_KEY" not in source
    assert "GEMINI_API_KEY" not in source
    assert "GOOGLE_API_KEY" not in source
    assert client_factory(ScriptedJsonTransport()) is not None


def test_provider_clients_import_no_provider_sdk_or_private_evaluator_stack() -> None:
    source = inspect.getsource(provider_clients_module)
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

    assert imported_roots.isdisjoint({"openai", "google", "google_genai", "langgraph", "pydantic_ai"})
    assert not any(module.startswith("research.e2.evaluator") for module in imported_modules)
    assert "FRESH_BLIND" not in source
    assert "LEGACY_LOCKED_TEST" not in source


def test_openai_builds_exact_stateless_responses_shape_without_secret_or_private_runtime_state() -> None:
    transport = ScriptedJsonTransport(_openai_response(_decision_json()))
    client = OpenAIResponsesDecisionClient(api_key=SECRET, transport=transport)
    request = _provider_request()

    result = client.complete(request)

    assert result == _decision_json()
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.method == "POST"
    assert call.url == OPENAI_RESPONSES_ENDPOINT
    assert call.headers["Authorization"] == f"Bearer {SECRET}"
    assert call.body["model"] == OPENAI_MODEL_ID
    assert call.body["store"] is False
    assert call.body["background"] is False
    assert call.body["reasoning"] == {"effort": "medium"}
    assert call.body["text"]["format"]["type"] == "json_schema"
    assert call.body["text"]["format"]["name"] == "provider_decision_payload"
    assert call.body["text"]["format"]["strict"] is False
    assert "tools" not in call.body
    assert "conversation" not in call.body
    assert "previous_response_id" not in call.body
    assert "seed" not in call.body
    assert "user" not in call.body
    assert "safety_identifier" not in call.body

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


def test_google_builds_exact_stateless_interactions_shape_without_secret_or_private_runtime_state() -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json()))
    client = GoogleInteractionsDecisionClient(api_key=SECRET, transport=transport)
    request = _provider_request()

    result = client.complete(request)

    assert result == _decision_json()
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.method == "POST"
    assert call.url == GOOGLE_INTERACTIONS_ENDPOINT
    assert call.headers["x-goog-api-key"] == SECRET
    assert call.body["model"] == GOOGLE_MODEL_ID
    assert call.body["store"] is False
    assert call.body["background"] is False
    assert call.body["generation_config"] == {
        "thinking_level": "medium",
        "thinking_summaries": "none",
        "tool_choice": "none",
    }
    assert call.body["response_format"]["type"] == "text"
    assert call.body["response_format"]["mime_type"] == "application/json"
    assert "tools" not in call.body
    assert "previous_interaction_id" not in call.body
    assert "seed" not in call.body["generation_config"]

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


def test_openai_valid_response_integrates_with_strict_provider_decision_source() -> None:
    transport = ScriptedJsonTransport(
        _openai_response(
            _decision_json(
                "TOOL",
                tool_name="get_asset",
                arguments={"asset_id": "asset-1"},
                evidence_id="ev-asset",
                message=None,
                reason_code=None,
            )
        )
    )
    client = OpenAIResponsesDecisionClient(api_key=SECRET, transport=transport)
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())

    decision = source.decide(ControllerContext(user_request="Inspect asset-1", turn_index=0, tool_call_count=0))

    assert decision.kind is ControllerDecisionKind.TOOL
    assert decision.proposal is not None
    assert decision.proposal.tool_name == "get_asset"
    assert decision.proposal.arguments == {"asset_id": "asset-1"}
    assert len(transport.calls) == 1


def test_google_valid_response_integrates_with_strict_provider_decision_source() -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json("CLARIFY", message="Need asset id", reason_code="MISSING_ASSET")))
    client = GoogleInteractionsDecisionClient(api_key=SECRET, transport=transport)
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())

    decision = source.decide(ControllerContext(user_request="Inspect it", turn_index=0, tool_call_count=0))

    assert decision.kind is ControllerDecisionKind.CLARIFY
    assert decision.message == "Need asset id"
    assert decision.reason_code == "MISSING_ASSET"
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    ("client_class", "response"),
    [
        (OpenAIResponsesDecisionClient, _openai_response(_decision_json(), status="incomplete")),
        (OpenAIResponsesDecisionClient, _openai_response(_decision_json(), model="gpt-5.6-sol-mutated")),
        (GoogleInteractionsDecisionClient, _google_response(_decision_json(), status="failed")),
        (GoogleInteractionsDecisionClient, _google_response(_decision_json(), model="gemini-3.7-flash-mutated")),
    ],
)
def test_status_or_model_drift_fails_closed_after_exactly_one_transport_call(client_class, response) -> None:
    transport = ScriptedJsonTransport(response)
    client = client_class(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError):
        client.complete(_provider_request())

    assert len(transport.calls) == 1


def test_openai_refusal_or_tool_output_shape_is_rejected() -> None:
    response = _openai_response(_decision_json())
    body = dict(response.body)
    body["output"] = [{"type": "function_call", "name": "get_asset", "arguments": "{}"}]
    transport = ScriptedJsonTransport(ProviderHttpResponse(status_code=200, body=body))
    client = OpenAIResponsesDecisionClient(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError, match="OPENAI_UNEXPECTED_OUTPUT_ITEM"):
        client.complete(_provider_request())
    assert len(transport.calls) == 1


def test_google_server_or_function_step_is_rejected() -> None:
    response = _google_response(_decision_json())
    body = dict(response.body)
    body["steps"] = [{"type": "function_call", "name": "get_asset", "arguments": {}}]
    transport = ScriptedJsonTransport(ProviderHttpResponse(status_code=200, body=body))
    client = GoogleInteractionsDecisionClient(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError, match="GOOGLE_UNEXPECTED_STEP"):
        client.complete(_provider_request())
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "client_class",
    [OpenAIResponsesDecisionClient, GoogleInteractionsDecisionClient],
)
def test_transport_exception_is_sanitized_and_never_retried(client_class) -> None:
    transport = ScriptedJsonTransport(RuntimeError(f"backend leaked {SECRET}"))
    client = client_class(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())

    assert str(exc_info.value) == "TRANSPORT_FAILURE"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


@pytest.mark.parametrize(
    "client_class",
    [OpenAIResponsesDecisionClient, GoogleInteractionsDecisionClient],
)
def test_non_success_http_status_is_sanitized_and_never_retried(client_class) -> None:
    transport = ScriptedJsonTransport(ProviderHttpResponse(status_code=429, body={"secret": SECRET}))
    client = client_class(api_key=SECRET, transport=transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())

    assert str(exc_info.value) == "HTTP_STATUS:429"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_openai_usage_is_sanitized_separate_and_drainable() -> None:
    transport = ScriptedJsonTransport(_openai_response(_decision_json()))
    client = OpenAIResponsesDecisionClient(api_key=SECRET, transport=transport)
    request = _provider_request()
    client.complete(request)

    records = client.drain_usage_records()
    assert len(records) == 1
    record = records[0]
    assert record.provider_id == "openai"
    assert record.model_id == OPENAI_MODEL_ID
    assert record.route_id == OPENAI_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert (record.input_tokens, record.output_tokens, record.total_tokens, record.reasoning_tokens) == (101, 17, 118, 7)
    assert SECRET not in repr(record)
    assert client.drain_usage_records() == ()


def test_google_usage_is_sanitized_separate_and_drainable() -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json()))
    client = GoogleInteractionsDecisionClient(api_key=SECRET, transport=transport)
    request = _provider_request()
    client.complete(request)

    records = client.drain_usage_records()
    assert len(records) == 1
    record = records[0]
    assert record.provider_id == "google"
    assert record.model_id == GOOGLE_MODEL_ID
    assert record.route_id == GOOGLE_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert (record.input_tokens, record.output_tokens, record.total_tokens, record.reasoning_tokens) == (93, 15, 119, 11)
    assert SECRET not in repr(record)
    assert client.drain_usage_records() == ()


def test_invalid_credentials_are_rejected_without_transport() -> None:
    with pytest.raises(ValueError, match="explicit non-empty api_key"):
        OpenAIResponsesDecisionClient(api_key="", transport=ScriptedJsonTransport())
    with pytest.raises(ValueError, match="explicit non-empty api_key"):
        GoogleInteractionsDecisionClient(api_key="   ", transport=ScriptedJsonTransport())


def test_json_schema_keeps_provider_decision_top_level_closed() -> None:
    schema = provider_clients_module.PROVIDER_DECISION_JSON_SCHEMA
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "schema_version",
        "kind",
        "tool_name",
        "arguments",
        "evidence_id",
        "final",
        "message",
        "reason_code",
    }
    assert schema["properties"]["kind"]["enum"] == ["TOOL", "FINAL", "CLARIFY", "ESCALATE", "ABSTAIN"]
