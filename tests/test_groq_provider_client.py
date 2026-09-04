from __future__ import annotations

import json
from typing import Any

import pytest

from academy_tractian.decision_source import ProviderDecisionSource, build_provider_decision_request
from academy_tractian.groq_provider_client import (
    GROQ_MODEL_ID,
    GROQ_RESPONSES_ENDPOINT,
    GROQ_ROUTE_ID,
    GroqResponsesDecisionClient,
)
from academy_tractian.provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerDecisionKind


SECRET = "groq-unit-test-secret-never-serialize"


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


def _groq_response(
    text: str,
    *,
    model: str = GROQ_MODEL_ID,
    status: str = "completed",
) -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "object": "response",
            "status": status,
            "model": model,
            "output": [
                {"type": "reasoning", "status": "completed", "content": []},
                {
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": text}],
                },
            ],
            "usage": {
                "input_tokens": 111,
                "output_tokens": 23,
                "total_tokens": 134,
                "output_tokens_details": {"reasoning_tokens": 9},
            },
        },
    )


def test_groq_builds_one_stateless_structured_responses_request_without_secret_payload() -> None:
    transport = ScriptedJsonTransport(_groq_response(_decision_json()))
    client = GroqResponsesDecisionClient(api_key=SECRET, transport=transport)

    assert client.complete(_provider_request()) == _decision_json()
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.method == "POST"
    assert call.url == GROQ_RESPONSES_ENDPOINT
    assert call.headers["Authorization"] == f"Bearer {SECRET}"
    assert call.body["model"] == GROQ_MODEL_ID
    assert call.body["reasoning"] == {"effort": "medium"}
    assert call.body["text"]["format"]["type"] == "json_schema"
    assert call.body["text"]["format"]["name"] == "provider_decision_payload"
    assert "store" not in call.body
    assert "background" not in call.body
    assert "tools" not in call.body
    assert "previous_response_id" not in call.body
    assert "seed" not in call.body
    serialized = json.dumps(call.body, sort_keys=True)
    assert SECRET not in serialized
    assert "idempotency" not in serialized
    assert "actions_enabled" not in serialized
    assert "gold" not in serialized.lower()
    assert SECRET not in repr(call)
    assert SECRET not in repr(client)


def test_groq_response_integrates_with_strict_provider_decision_source() -> None:
    response = _groq_response(
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
    source = ProviderDecisionSource(
        client=GroqResponsesDecisionClient(api_key=SECRET, transport=transport),
        registry=canonical_tool_registry(),
    )

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
        _groq_response(_decision_json(), status="incomplete"),
        _groq_response(_decision_json(), model="openai/gpt-oss-120b-mutated"),
    ],
)
def test_groq_status_or_model_drift_fails_closed_without_retry(response: ProviderHttpResponse) -> None:
    transport = ScriptedJsonTransport(response)
    client = GroqResponsesDecisionClient(api_key=SECRET, transport=transport)
    with pytest.raises(ProviderHttpClientError):
        client.complete(_provider_request())
    assert len(transport.calls) == 1


def test_groq_transport_failure_is_sanitized_without_retry() -> None:
    transport = ScriptedJsonTransport(RuntimeError(f"provider leaked {SECRET}"))
    client = GroqResponsesDecisionClient(api_key=SECRET, transport=transport)
    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_provider_request())
    assert str(exc_info.value) == "TRANSPORT_FAILURE"
    assert SECRET not in str(exc_info.value)
    assert len(transport.calls) == 1


def test_groq_usage_is_sanitized_separate_and_drainable() -> None:
    transport = ScriptedJsonTransport(_groq_response(_decision_json()))
    client = GroqResponsesDecisionClient(api_key=SECRET, transport=transport)
    request = _provider_request()
    client.complete(request)
    records = client.drain_usage_records()
    assert len(records) == 1
    record = records[0]
    assert record.provider_id == "groq"
    assert record.model_id == GROQ_MODEL_ID
    assert record.route_id == GROQ_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert (record.input_tokens, record.output_tokens, record.total_tokens, record.reasoning_tokens) == (
        111,
        23,
        134,
        9,
    )
    assert SECRET not in repr(record)
    assert client.drain_usage_records() == ()


def test_groq_requires_explicit_credentials() -> None:
    with pytest.raises(ValueError, match="explicit non-empty api_key"):
        GroqResponsesDecisionClient(api_key="", transport=ScriptedJsonTransport())
