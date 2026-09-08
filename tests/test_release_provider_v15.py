from __future__ import annotations

from types import SimpleNamespace

import pytest

from academy_tractian.decision_source import ProviderDecisionRequest
from academy_tractian.provider_clients import ProviderHttpClientError, ProviderHttpResponse
from academy_tractian.release_provider import PROVISIONAL_RELEASE_PROVIDER_STATE
from academy_tractian.release_provider_v15 import (
    NVIDIA_ACCOUNT_SENTINEL,
    NVIDIA_ENDPOINT,
    NVIDIA_MODEL_ID,
    NVIDIA_PROVIDER_ID,
    NvidiaV15ServingError,
    Release0NvidiaDecisionClientV15,
    validate_release_provider_config_v15,
)


class _StaticTransport:
    def __init__(self, response: ProviderHttpResponse) -> None:
        self.response = response
        self.requests = []

    def post_json(self, request):
        self.requests.append(request)
        return self.response


class _ErrorTransport:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code

    def post_json(self, _request):
        raise ProviderHttpClientError("HTTP_STATUS", status_code=self.status_code)


def _request() -> ProviderDecisionRequest:
    return ProviderDecisionRequest.model_construct(
        user_request="synthetic serving smoke only",
        turn_index=0,
        tool_call_count=0,
        observations=(),
        tools=(),
        request_sha256="0" * 64,
    )


def _response(*, content: str = "{}", model: str = NVIDIA_MODEL_ID, tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return ProviderHttpResponse(
        status_code=200,
        body={
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": message,
                }
            ],
            "usage": {},
        },
    )


def _client(transport):
    return Release0NvidiaDecisionClientV15(
        api_key="test-only-secret",
        transport=transport,
    )


def test_v15_request_is_exact_nvidia_pin_without_retry_or_fallback_fields() -> None:
    client = _client(_StaticTransport(_response()))

    request = client.build_http_request(_request())

    assert request.url == NVIDIA_ENDPOINT
    assert request.body["model"] == NVIDIA_MODEL_ID
    assert request.body["temperature"] == 0
    assert request.body["stream"] is False
    assert request.body["reasoning_effort"] == "low"
    assert "n" not in request.body
    assert "provider" not in request.body
    assert "fallback" not in request.body
    assert request.body["response_format"]["type"] == "json_schema"
    assert request.body["response_format"]["json_schema"]["strict"] is True
    assert repr(client).endswith("api_key=<redacted>)")
    assert "test-only-secret" not in repr(client)


def test_v15_accepts_one_structured_completion() -> None:
    content = '{"schema_version":"provider-decision-payload-v1","kind":"ABSTAIN","tool_name":null,"arguments":{},"evidence_id":null,"final":null,"message":"synthetic smoke","reason_code":"SYNTHETIC"}'
    client = _client(_StaticTransport(_response(content=content)))

    assert client.complete(_request()) == content


@pytest.mark.parametrize("status_code", [404, 410])
def test_v15_sanitizes_deprecated_or_missing_serving_route(status_code: int) -> None:
    client = _client(_ErrorTransport(status_code))

    with pytest.raises(NvidiaV15ServingError) as exc_info:
        client.complete(_request())

    error_text = str(exc_info.value)
    assert exc_info.value.status_code == status_code
    assert exc_info.value.category == "MODEL_OR_ROUTE_UNAVAILABLE"
    assert f"status={status_code}" in error_text
    assert NVIDIA_MODEL_ID in error_text
    assert "integrate.api.nvidia.com" in error_text
    assert "test-only-secret" not in error_text
    assert "synthetic serving smoke only" not in error_text


def test_v15_preserves_non_route_http_failure_as_generic_sanitized_provider_error() -> None:
    client = _client(_ErrorTransport(500))

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code == "HTTP_STATUS"
    assert exc_info.value.status_code == 500


def test_v15_rejects_native_tool_calls_in_application_owned_runtime() -> None:
    client = _client(
        _StaticTransport(
            _response(
                content="",
                tool_calls=[
                    {
                        "type": "function",
                        "function": {"name": "synthetic_lookup", "arguments": "{}"},
                    }
                ],
            )
        )
    )

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code == "NVIDIA_TOOL_CALL_REJECTED"


def test_v15_rejects_served_model_drift() -> None:
    client = _client(_StaticTransport(_response(model="different/model")))

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code == "NVIDIA_MODEL_MISMATCH"


def test_v15_config_accepts_only_exact_active_nvidia_route() -> None:
    config = SimpleNamespace(
        provider_calls_enabled=True,
        provider_selection_state=PROVISIONAL_RELEASE_PROVIDER_STATE,
        provider_id=NVIDIA_PROVIDER_ID,
        provider_model_id=NVIDIA_MODEL_ID,
        provider_account_id=NVIDIA_ACCOUNT_SENTINEL,
        provider_api_token=object(),
        cost_policy="usd0-hard-gate",
        paid_fallback_enabled=False,
        tractian_transport_enabled=True,
    )

    assert validate_release_provider_config_v15(config) is None

    with pytest.raises(RuntimeError, match="release_provider_model_not_supported"):
        validate_release_provider_config_v15(
            SimpleNamespace(**{**vars(config), "provider_model_id": "openai/gpt-oss-120b"})
        )
