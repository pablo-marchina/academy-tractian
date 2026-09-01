from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
)
from academy_tractian.cloudflare_provider_provenance_v2 import (
    CloudflareProviderCallIdentityV2,
    CloudflareProviderDecisionSourceV2,
    CloudflareProviderModelCallRecordV2,
    validate_cloudflare_audit_record_v2,
)
from academy_tractian.provider_clients import ProviderUsageRecord
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext


class LocalDecisionClient:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.records: list[ProviderUsageRecord] = []

    def complete(self, request):
        self.records.append(
            ProviderUsageRecord(
                provider_id="cloudflare",
                model_id=self.model_id,
                route_id="cloudflare.workers_ai.openai_compat.chat_completions.v1",
                request_sha256=request.request_sha256,
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
            )
        )
        return json.dumps(
            {
                "schema_version": "provider-decision-payload-v1",
                "kind": "ABSTAIN",
                "tool_name": None,
                "arguments": {},
                "evidence_id": None,
                "final": None,
                "message": "No safe path.",
                "reason_code": "NO_SAFE_PATH",
            },
            sort_keys=True,
        )


@pytest.mark.parametrize("model_id", [CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID])
def test_exact_official_at_cf_model_ids_are_preserved_in_v1_event_shape(model_id: str) -> None:
    source = CloudflareProviderDecisionSourceV2(
        client=LocalDecisionClient(model_id),
        registry=canonical_tool_registry(),
        call_identity=CloudflareProviderCallIdentityV2(model_id=model_id, live_call=False),
        clock_ns=iter([1_000_000, 2_000_000]).__next__,
    )
    context = ControllerContext(user_request="Inspect the public test asset.", turn_index=0, tool_call_count=0)
    request = source.build_request(context)
    source.decide(context)
    records = source.drain_audit_records()

    record, valid, issues = validate_cloudflare_audit_record_v2(
        provider_id="cloudflare",
        model_id=model_id,
        route_id="cloudflare.workers_ai.openai_compat.chat_completions.v1",
        request_sha256=request.request_sha256,
        audit_records=records,
        live_call=False,
    )
    assert valid
    assert issues == ()
    assert record is not None
    assert record.schema_version == "provider-model-call-v1"
    assert record.adapter_version == "provider-decision-adapter-v1"
    assert record.model_id == model_id
    assert record.provider_id == "cloudflare"
    assert record.route_id == "cloudflare.workers_ai.openai_compat.chat_completions.v1"
    assert record.adapter_client_invocations == 1
    assert record.adapter_retry_count == 0
    assert record.adapter_fallback_used is False
    assert record.raw_request_recorded is False
    assert record.raw_response_recorded is False
    assert record.exception_text_recorded is False

    reparsed = CloudflareProviderModelCallRecordV2.model_validate(
        {"call_id": records[0].call_id, **dict(records[0].metadata)}
    )
    assert reparsed.call_id == record.call_id


def test_provenance_extension_rejects_any_non_adr018_model() -> None:
    with pytest.raises(ValidationError):
        CloudflareProviderCallIdentityV2(model_id="@cf/google/gemma-4-26b-a4b-it")
    with pytest.raises(ValidationError):
        CloudflareProviderCallIdentityV2(model_id="cf/zai-org/glm-4.7-flash")
