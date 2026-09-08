from __future__ import annotations

import pytest

from academy_tractian.decision_source import ProviderDecisionRequest
from academy_tractian.provider_clients import ProviderHttpClientError, ProviderHttpResponse
from academy_tractian.release_provider_v14 import (
    OPENROUTER_MODEL_ID,
    Release0OpenRouterDecisionClientV14,
)


class _StaticTransport:
    def __init__(self, response: ProviderHttpResponse) -> None:
        self.response = response
        self.requests = []

    def post_json(self, request):
        self.requests.append(request)
        return self.response


def _request() -> ProviderDecisionRequest:
    return ProviderDecisionRequest.model_construct(
        user_request="inspect asset health",
        turn_index=0,
        tool_call_count=0,
        observations=(),
        tools=(),
        request_sha256="0" * 64,
    )


def _response(*, finish_reason: str, content: str) -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "model": OPENROUTER_MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "finish_reason": finish_reason,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                }
            ],
            "usage": {},
        },
    )


def _client(response: ProviderHttpResponse):
    transport = _StaticTransport(response)
    return (
        Release0OpenRouterDecisionClientV14(
            api_key="test-only",
            transport=transport,
        ),
        transport,
    )


def test_v14_request_keeps_exact_free_pin_and_disables_fallbacks() -> None:
    client, _transport = _client(_response(finish_reason="stop", content="{}"))

    http_request = client.build_http_request(_request())

    assert http_request.body["model"] == OPENROUTER_MODEL_ID
    assert OPENROUTER_MODEL_ID.endswith(":free")
    assert http_request.body["provider"] == {
        "allow_fallbacks": False,
        "require_parameters": True,
    }
    assert http_request.body["response_format"]["type"] == "json_schema"
    assert http_request.body["response_format"]["json_schema"]["strict"] is True


def test_v14_accepts_stop_with_nonempty_content() -> None:
    client, _transport = _client(_response(finish_reason="stop", content="{}"))

    assert client.complete(_request()) == "{}"


def test_v14_accepts_length_only_when_content_is_complete_json_object() -> None:
    content = '{"schema_version":"provider-decision-payload-v1","kind":"ABSTAIN","tool_name":null,"arguments":{},"evidence_id":null,"final":null,"message":"insufficient evidence","reason_code":"INSUFFICIENT_EVIDENCE"}'
    client, _transport = _client(_response(finish_reason="length", content=content))

    assert client.complete(_request()) == content


@pytest.mark.parametrize("content", ["{", "[]", '"text"', "", "   "])
def test_v14_rejects_length_when_content_is_not_complete_json_object(content: str) -> None:
    client, _transport = _client(_response(finish_reason="length", content=content))

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code in {
        "OPENROUTER_FINISH_REASON_INVALID",
        "OPENROUTER_OUTPUT_TEXT_INVALID",
    }


def test_v14_rejects_unrecognized_finish_reason() -> None:
    client, _transport = _client(_response(finish_reason="content_filter", content="{}"))

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code == "OPENROUTER_FINISH_REASON_INVALID"
