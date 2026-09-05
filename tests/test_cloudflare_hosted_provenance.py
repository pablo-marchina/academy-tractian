from __future__ import annotations

import json

from academy_tractian.decision_source import (
    ProviderCallIdentity,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    ProviderModelCallRecord,
)
from academy_tractian.runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse


CLOUDFLARE_MODEL_ID = "@cf/zai-org/glm-4.7-flash"
CLOUDFLARE_ROUTE_ID = "cloudflare.workers_ai.openai_compat.chat_completions.v1"


class _SingleResponseClient:
    def __init__(self) -> None:
        self.calls: list[ProviderDecisionRequest] = []

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls.append(request)
        return json.dumps(
            {
                "schema_version": "provider-decision-payload-v1",
                "kind": "ABSTAIN",
                "message": "No safe path",
                "reason_code": "NO_SAFE_PATH",
            },
            sort_keys=True,
        )


class _NoopTransport:
    def request(self, request: BoundRequest) -> TransportResponse:
        raise AssertionError("ABSTAIN decision must not execute a TRACTIAN transport call")


def test_cloudflare_provider_native_model_id_survives_runtime_provenance_roundtrip() -> None:
    client = _SingleResponseClient()
    runtime = ProductionRuntime(
        decision_source=ProviderDecisionSource(
            client=client,
            registry=canonical_tool_registry(),
            call_identity=ProviderCallIdentity(
                provider_id="cloudflare",
                model_id=CLOUDFLARE_MODEL_ID,
                route_id=CLOUDFLARE_ROUTE_ID,
                live_call=True,
            ),
        ),
        transport=_NoopTransport(),
    )

    trace = runtime.run(
        ProductionRequest(
            request_id="cloudflare-provenance-roundtrip",
            identity_id="identity-1",
            user_id="user-1",
            user_request="Inspect asset asset-1.",
            seed="provider-native-id-regression",
        )
    )

    model_calls = [event for event in trace.events if event.event_type == "model_call"]
    assert len(client.calls) == 1
    assert len(model_calls) == 1

    event = model_calls[0]
    record = ProviderModelCallRecord.from_trace_event(
        call_id=event.call_id,
        metadata=event.metadata,
    )

    assert record.provider_id == "cloudflare"
    assert record.model_id == CLOUDFLARE_MODEL_ID
    assert record.route_id == CLOUDFLARE_ROUTE_ID
    assert record.live_call is True
    assert record.outcome == "success"
    assert record.adapter_client_invocations == 1
    assert record.adapter_retry_count == 0
    assert record.adapter_fallback_used is False
    assert record.raw_request_recorded is False
    assert record.raw_response_recorded is False
    assert record.exception_text_recorded is False
    assert CLOUDFLARE_MODEL_ID in event.metadata.values()
