from __future__ import annotations

import pytest
from pydantic import SecretStr

import academy_tractian.remote_server as remote_server
from academy_tractian.decision_source import ProviderDecisionRequest, ProviderDecisionSource
from academy_tractian.production_config import RemoteProductionConfig
from academy_tractian.provider_clients import ProviderHttpClientError, ProviderHttpResponse
from academy_tractian.release_provider_v14 import OPENROUTER_MODEL_ID
from academy_tractian.release_provider_v15 import (
    NVIDIA_ACCOUNT_SENTINEL,
    NVIDIA_ENDPOINT,
    NVIDIA_MODEL_ID,
    NVIDIA_PROVIDER_ID,
    Release0NvidiaDecisionClientV15,
    build_release_provider_decision_source_v15,
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
    def __init__(self, error: ProviderHttpClientError) -> None:
        self.error = error
        self.requests = []

    def post_json(self, request):
        self.requests.append(request)
        raise self.error


def _request() -> ProviderDecisionRequest:
    return ProviderDecisionRequest.model_construct(
        user_request="inspect asset health",
        turn_index=0,
        tool_call_count=0,
        observations=(),
        tools=(),
        request_sha256="1" * 64,
    )


def _response(*, content: str = "{}", finish_reason: str = "stop", message_extra=None):
    message = {"role": "assistant", "content": content}
    if message_extra:
        message.update(message_extra)
    return ProviderHttpResponse(
        status_code=200,
        body={
            "model": NVIDIA_MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "finish_reason": finish_reason,
                    "message": message,
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "completion_tokens_details": {"reasoning_tokens": 2},
            },
        },
    )


def _client(response: ProviderHttpResponse | None = None, *, transport=None):
    selected_transport = transport or _StaticTransport(response or _response())
    return (
        Release0NvidiaDecisionClientV15(
            api_key="nvidia-secret-test-only",
            transport=selected_transport,
        ),
        selected_transport,
    )


def _base_config() -> RemoteProductionConfig:
    return RemoteProductionConfig.model_validate(
        {
            "environment": "production",
            "internal_dsn": "postgresql://internal:secret@db.example.net:5432/academy?sslmode=require",
            "scoped_dsn": "postgresql://scoped:secret@db.example.net:5432/academy?sslmode=require",
            "runtime_identity_secret": "runtime-identity-secret-with-more-than-32-bytes",
            "runtime_identity_issuer": "academy-production",
            "runtime_identity_audience": "academy-product",
            "public_base_url": "https://203.0.113.10",
            "release_git_sha": "c" * 40,
            "deployment_id": "deploy-v15-test",
            "cost_policy": "usd0-hard-gate",
            "paid_fallback_enabled": False,
            "local_serving_enabled": False,
            "provider_calls_enabled": False,
        }
    )


def _nvidia_config() -> RemoteProductionConfig:
    return _base_config().model_copy(
        update={
            "provider_calls_enabled": True,
            "provider_selection_state": "PROVISIONAL_RELEASE_PROVIDER",
            "provider_id": NVIDIA_PROVIDER_ID,
            "provider_model_id": NVIDIA_MODEL_ID,
            "provider_account_id": NVIDIA_ACCOUNT_SENTINEL,
            "provider_api_token": SecretStr("nvidia-secret-test-only"),
            "tractian_transport_enabled": True,
            "tractian_base_url": "https://tractian.example.net",
            "tractian_server_headers_json": SecretStr('{"x-api-key":"server-secret"}'),
        }
    )


def test_v15_nvidia_request_is_exact_direct_strict_json_without_fallback_fields() -> None:
    client, _transport = _client()

    http_request = client.build_http_request(_request())

    assert http_request.url == NVIDIA_ENDPOINT
    assert http_request.body["model"] == NVIDIA_MODEL_ID
    assert http_request.body["temperature"] == 0
    assert http_request.body["n"] == 1
    assert http_request.body["stream"] is False
    assert http_request.body["response_format"]["type"] == "json_schema"
    assert http_request.body["response_format"]["json_schema"]["strict"] is True
    assert "provider" not in http_request.body
    assert "tools" not in http_request.body
    assert http_request.headers["Authorization"] == "Bearer nvidia-secret-test-only"
    assert "nvidia-secret-test-only" not in repr(http_request)
    assert "nvidia-secret-test-only" not in repr(client)


def test_v15_nvidia_accepts_complete_structured_content_and_records_safe_usage() -> None:
    client, _transport = _client(_response(content='{"kind":"ABSTAIN"}'))

    assert client.complete(_request()) == '{"kind":"ABSTAIN"}'
    usage = client.drain_usage_records()

    assert len(usage) == 1
    assert usage[0].provider_id == NVIDIA_PROVIDER_ID
    assert usage[0].model_id == NVIDIA_MODEL_ID
    assert usage[0].input_tokens == 10
    assert usage[0].output_tokens == 5
    assert usage[0].total_tokens == 15
    assert usage[0].reasoning_tokens == 2


def test_v15_nvidia_maps_404_to_sanitized_route_diagnostic() -> None:
    transport = _ErrorTransport(ProviderHttpClientError("HTTP_STATUS", status_code=404))
    client, _transport = _client(transport=transport)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code == "NVIDIA_ROUTE_NOT_FOUND"
    assert exc_info.value.status_code == 404
    assert "nvidia-secret-test-only" not in str(exc_info.value)
    assert "response" not in str(exc_info.value).lower()


def test_v15_nvidia_rejects_native_tool_calls_at_product_decision_boundary() -> None:
    client, _transport = _client(
        _response(
            content="{}",
            message_extra={
                "tool_calls": [
                    {
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "lookup_asset_status", "arguments": "{}"},
                    }
                ]
            },
        )
    )

    with pytest.raises(ProviderHttpClientError) as exc_info:
        client.complete(_request())

    assert exc_info.value.code == "NVIDIA_TOOL_CALL_REJECTED"


def test_v15_nvidia_accepts_length_only_for_complete_json_object() -> None:
    client, _transport = _client(_response(content='{"kind":"ABSTAIN"}', finish_reason="length"))
    assert client.complete(_request()) == '{"kind":"ABSTAIN"}'

    broken, _transport = _client(_response(content="{", finish_reason="length"))
    with pytest.raises(ProviderHttpClientError) as exc_info:
        broken.complete(_request())
    assert exc_info.value.code == "NVIDIA_FINISH_REASON_INVALID"


def test_v15_validation_is_additive_and_preserves_v14_openrouter_route() -> None:
    openrouter = _nvidia_config().model_copy(
        update={
            "provider_id": "openrouter",
            "provider_model_id": OPENROUTER_MODEL_ID,
            "provider_account_id": "openrouter",
        }
    )

    validate_release_provider_config_v15(_nvidia_config())
    validate_release_provider_config_v15(openrouter)


def test_v15_builder_reuses_generic_v13_decision_source_without_provider_io() -> None:
    transport = _StaticTransport(_response())

    source = build_release_provider_decision_source_v15(
        config=_nvidia_config(),
        transport=transport,
    )

    assert isinstance(source, ProviderDecisionSource)
    assert transport.requests == []


def test_remote_server_composition_root_selects_v15(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _nvidia_config()
    sentinel = lambda: object()
    validated = []

    monkeypatch.setattr(remote_server, "validate_release_provider_config_v15", lambda value: validated.append(value))
    monkeypatch.setattr(remote_server, "build_release_provider_decision_source_factory_v15", lambda value: sentinel)

    assert remote_server._decision_source_factory(config) is sentinel
    assert validated == [config]
