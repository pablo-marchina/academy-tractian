from __future__ import annotations

import json
from typing import Any

import pytest

from academy_tractian.decision_source import ProviderDecisionSource, build_provider_decision_request
from academy_tractian.google_v1_provider_client import (
    GOOGLE_37_MODEL_ID,
    GOOGLE_38_MODEL_ID,
    GOOGLE_V1_INTERACTIONS_ENDPOINT,
    GOOGLE_V1_ROUTE_ID,
    GoogleV1InteractionsDecisionClient,
)
from academy_tractian.provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, ControllerDecisionKind


SECRET = "google-v1-unit-test-secret-never-serialize"


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


def _google_response(text: str, *, model: str = GOOGLE_38_MODEL_ID) -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "id": "int_test",
            "object": "interaction",
            "status": "completed",
            "model": model,
            "steps": [
                {
                    "type": "model_output",
                    "status": "done",
                    "content": [{"type": "text", "text": text}],
                }
            ],
            "usage": {
                "total_input_tokens": 120,
                "total_output_tokens": 30,
                "total_thought_tokens": 12,
                "total_tokens": 162,
            },
        },
    )


def test_google_v1_uses_stable_interactions_route_and_explicit_model() -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json()))
    client = GoogleV1InteractionsDecisionClient(
        api_key=SECRET,
        model_id=GOOGLE_38_MODEL_ID,
        transport=transport,
    )

    assert client.complete(_provider_request()) == _decision_json()
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call.url == GOOGLE_V1_INTERACTIONS_ENDPOINT
    assert call.headers["x-goog-api-key"] == SECRET
    assert call.body["model"] == GOOGLE_38_MODEL_ID
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
    assert SECRET not in json.dumps(call.body, sort_keys=True)
    assert SECRET not in repr(call)
    assert SECRET not in repr(client)


@pytest.mark.parametrize("model_id", [GOOGLE_37_MODEL_ID, GOOGLE_38_MODEL_ID])
def test_google_v1_supports_both_frozen_baseline_and_latest_candidate(model_id: str) -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json(), model=model_id))
    client = GoogleV1InteractionsDecisionClient(
        api_key=SECRET,
        model_id=model_id,
        transport=transport,
    )
    assert client.complete(_provider_request()) == _decision_json()
    assert client.model_id == model_id
    assert client.route_id == GOOGLE_V1_ROUTE_ID


def test_google_v1_integrates_with_provider_decision_source() -> None:
    transport = ScriptedJsonTransport(
        _google_response(
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
    source = ProviderDecisionSource(
        client=GoogleV1InteractionsDecisionClient(
            api_key=SECRET,
            model_id=GOOGLE_38_MODEL_ID,
            transport=transport,
        ),
        registry=canonical_tool_registry(),
    )
    decision = source.decide(
        ControllerContext(user_request="Inspect asset-1", turn_index=0, tool_call_count=0)
    )
    assert decision.kind is ControllerDecisionKind.TOOL
    assert decision.proposal is not None
    assert decision.proposal.tool_name == "get_asset"


def test_google_v1_model_drift_fails_closed_without_retry() -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json(), model=GOOGLE_37_MODEL_ID))
    client = GoogleV1InteractionsDecisionClient(
        api_key=SECRET,
        model_id=GOOGLE_38_MODEL_ID,
        transport=transport,
    )
    with pytest.raises(ProviderHttpClientError, match="GOOGLE_MODEL_MISMATCH"):
        client.complete(_provider_request())
    assert len(transport.calls) == 1


def test_google_v1_usage_is_sanitized_and_drainable() -> None:
    transport = ScriptedJsonTransport(_google_response(_decision_json()))
    client = GoogleV1InteractionsDecisionClient(
        api_key=SECRET,
        model_id=GOOGLE_38_MODEL_ID,
        transport=transport,
    )
    request = _provider_request()
    client.complete(request)
    record = client.drain_usage_records()[0]
    assert record.provider_id == "google"
    assert record.model_id == GOOGLE_38_MODEL_ID
    assert record.route_id == GOOGLE_V1_ROUTE_ID
    assert record.request_sha256 == request.request_sha256
    assert (record.input_tokens, record.output_tokens, record.reasoning_tokens, record.total_tokens) == (
        120,
        30,
        12,
        162,
    )
    assert SECRET not in repr(record)


def test_google_v1_rejects_unknown_model_before_transport() -> None:
    with pytest.raises(ValueError, match="unsupported_google_v1_model"):
        GoogleV1InteractionsDecisionClient(
            api_key=SECRET,
            model_id="gemini-unknown",
            transport=ScriptedJsonTransport(),
        )
