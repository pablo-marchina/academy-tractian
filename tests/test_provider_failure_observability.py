from __future__ import annotations

import pytest

from academy_tractian.decision_source import (
    ProviderCallIdentity,
    ProviderDecisionSource,
    _classify_client_failure,
)
from academy_tractian.provider_clients import ProviderHttpClientError
from research.e2.controller import ControllerContext
from research.e2.models import ToolKind, ToolSpec


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (ProviderHttpClientError("HTTP_STATUS", status_code=429), "PROVIDER_RATE_LIMITED"),
        (ProviderHttpClientError("HTTP_STATUS", status_code=400), "PROVIDER_HTTP_CLIENT_ERROR"),
        (ProviderHttpClientError("HTTP_STATUS", status_code=503), "PROVIDER_HTTP_SERVER_ERROR"),
        (ProviderHttpClientError("TRANSPORT_FAILURE"), "PROVIDER_TRANSPORT_FAILURE"),
        (ProviderHttpClientError("OPENROUTER_FINISH_REASON_INVALID"), "PROVIDER_RESPONSE_PROTOCOL_INVALID"),
        (RuntimeError("opaque failure"), "CLIENT_FAILURE"),
    ],
)
def test_provider_failure_classifier_is_sanitized(error: Exception, expected: str) -> None:
    assert _classify_client_failure(error) == expected


class _FailingClient:
    def complete(self, request):
        raise ProviderHttpClientError("HTTP_STATUS", status_code=429)


def test_model_call_persists_sanitized_rate_limit_without_exception_text() -> None:
    tool = ToolSpec(
        name="dummy.read",
        operation_id="dummy_read",
        method="GET",
        path_template="/dummy",
        kind=ToolKind.READ,
    )
    source = ProviderDecisionSource(
        client=_FailingClient(),
        registry={tool.name: tool},
        call_identity=ProviderCallIdentity(
            provider_id="openrouter",
            model_id="nvidia/nemotron-3-super-120b-a12b:free",
            route_id="openrouter.chat_completions.v1.fixed_free",
            live_call=True,
        ),
    )

    with pytest.raises(ProviderHttpClientError):
        source.decide(
            ControllerContext(
                user_request="inspect asset health",
                turn_index=0,
                tool_call_count=0,
            )
        )

    records = source.drain_audit_records()
    assert len(records) == 1
    metadata = records[0].metadata
    assert metadata["failure_code"] == "PROVIDER_RATE_LIMITED"
    assert metadata["provider_id"] == "openrouter"
    assert metadata["raw_request_recorded"] is False
    assert metadata["raw_response_recorded"] is False
    assert metadata["exception_text_recorded"] is False
    assert "429" not in str(metadata)
