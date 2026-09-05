from __future__ import annotations

import json
from typing import Any

import pytest

from academy_tractian.decision_source import ProviderDecisionSource, build_provider_decision_request
from academy_tractian.groq_provider_client import (
    GROQ_ENDPOINT,
    GROQ_GPT_OSS_120B_MODEL_ID,
    GROQ_MAX_COMPLETION_TOKENS,
    GROQ_ROUTE_ID,
    GroqChatCompletionsDecisionClient,
)
from academy_tractian.provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerDecisionKind


SECRET = "groq-unit-secret-never-serialize"


class ScriptedTransport:
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


def _request():
    return build_provider_decision_request(
        context=ControllerContext(
            user_request="Inspect asset asset-demo.",
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


def _response(text: str, *, finish_reason: str = "stop") -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "id": "chatcmpl_demo",
            "object": "chat.completion",
            "model": GROQ_GPT_OSS_120B_MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "finish_reason": finish_reason,
                    "message": {
                        "role": "assistant",
                        "content": text,
                    },
                }
            ],
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 40,
                "total_tokens": 160,
                "completion_tokens_details": {"reasoning_tokens": 9},
            },
        },
    )


def test_groq_builds_one_shot_structured_output_request_without_tool_execution() -> None:
    transport = ScriptedTransport(_response(_decision_json()))
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    request = _request()

    assert client.complete(request) == _decision_json()
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.url == GROQ_ENDPOINT
    assert call.headers["Authorization"] == f"Bearer {SECRET}"
    assert call.body["model"] == GROQ_GPT_OSS_120B_MODEL_ID
    assert call.body["stream"] is False
    assert call.body["max_completion_tokens"] == GROQ_MAX_COMPLETION_TOKENS
    assert call.body["reasoning_effort"] == "medium"
    assert call.body["include_reasoning"] is False
    response_format = call.body["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is False
    assert "tools" not in call.body
    assert "tool_choice" not in call.body
    serialized = json.dumps(call.body, sort_keys=True)
    assert SECRET not in serialized
    assert "x-user-id" not in serialized
    assert '"identity_id"' not in serialized
    assert '"seed"' not in serialized
    assert "gold" not in serialized.lower()
    assert SECRET not in repr(client)
    assert SECRET not in repr(call)


def test_groq_valid_output_integrates_with_existing_strict_decision_source() -> None:
    transport = ScriptedTransport(
        _response(
            _decision_json(
                "TOOL",
                tool_name="get_asset",
                arguments={"asset_id": "asset-demo"},
                evidence_id="ev-demo",
                message=None,
                reason_code=None,
            )
        )
    )
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    source = ProviderDecisionSource(client=client, registry=canonical_tool_registry())

    decision = source.decide(
        ControllerContext(
            user_request="Inspect asset-demo",
            turn_index=0,
            tool_call_count=0,
        )
    )

    assert decision.kind is ControllerDecisionKind.TOOL
    assert decision.proposal is not None
    assert decision.proposal.tool_name == "get_asset"
    assert decision.proposal.arguments == {"asset_id": "asset-demo"}
    assert len(transport.calls) == 1


def test_groq_non_stop_output_and_model_drift_fail_closed_without_retry() -> None:
    transport = ScriptedTransport(_response(_decision_json(), finish_reason="length"))
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    with pytest.raises(ProviderHttpClientError, match="GROQ_FINISH_REASON_INVALID"):
        client.complete(_request())
    assert len(transport.calls) == 1

    drifted = _response(_decision_json())
    body = dict(drifted.body)
    body["model"] = "unexpected-model"
    transport = ScriptedTransport(ProviderHttpResponse(status_code=200, body=body))
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    with pytest.raises(ProviderHttpClientError, match="GROQ_MODEL_MISMATCH"):
        client.complete(_request())
    assert len(transport.calls) == 1


def test_groq_rejects_provider_side_tool_calls_and_sanitizes_transport_failure() -> None:
    response = _response(_decision_json())
    body = dict(response.body)
    body["choices"] = [
        {
            "index": 0,
            "finish_reason": "stop",
            "message": {
                "role": "assistant",
                "content": _decision_json(),
                "tool_calls": [{"id": "call_1"}],
            },
        }
    ]
    transport = ScriptedTransport(ProviderHttpResponse(status_code=200, body=body))
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    with pytest.raises(ProviderHttpClientError, match="GROQ_TOOL_CALL_REJECTED"):
        client.complete(_request())
    assert len(transport.calls) == 1

    transport = ScriptedTransport(RuntimeError(f"leak {SECRET}"))
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())
    assert str(exc_info.value) == "TRANSPORT_FAILURE"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_groq_usage_is_sanitized_and_drainable() -> None:
    transport = ScriptedTransport(_response(_decision_json()))
    client = GroqChatCompletionsDecisionClient(api_key=SECRET, transport=transport)
    request = _request()
    client.complete(request)

    records = client.drain_usage_records()
    assert len(records) == 1
    record = records[0]
    assert record.provider_id == "groq"
    assert record.model_id == GROQ_GPT_OSS_120B_MODEL_ID
    assert record.route_id == GROQ_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert (record.input_tokens, record.output_tokens, record.total_tokens, record.reasoning_tokens) == (
        120,
        40,
        160,
        9,
    )
    assert SECRET not in repr(record)
    assert client.drain_usage_records() == ()


def test_groq_rejects_missing_credentials_and_unregistered_model() -> None:
    with pytest.raises(ValueError, match="explicit non-empty api_key"):
        GroqChatCompletionsDecisionClient(api_key="", transport=ScriptedTransport())
    with pytest.raises(ValueError, match="not allowed"):
        GroqChatCompletionsDecisionClient(
            api_key=SECRET,
            model_id="unregistered/model",
            transport=ScriptedTransport(),
        )
