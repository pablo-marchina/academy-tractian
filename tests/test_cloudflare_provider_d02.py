from __future__ import annotations

import json
from typing import Any

import pytest

from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
)
from academy_tractian.cloudflare_provider_d02 import (
    CLOUDFLARE_D02_EXPECTED_PLAN_SHA256,
    CLOUDFLARE_D02_MAX_COMPLETION_TOKENS,
    CLOUDFLARE_D02_MAX_MODELED_HEADROOM,
    CLOUDFLARE_D02_MAX_PACKET_NEURONS,
    CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
    CloudflareD02PreLiveEvidence,
    CloudflareProviderCallIdentityV2,
    CloudflareProviderDecisionSourceD02,
    CloudflareWorkersAIChatCompletionsDecisionClientD02,
    build_cloudflare_d02_plan,
    validate_cloudflare_audit_record_d02,
    validate_cloudflare_failure_diagnostic_d02,
    worst_case_neurons_per_candidate_d02,
)
from academy_tractian.decision_source import build_provider_decision_request
from academy_tractian.provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext, DecisionSourceAuditRecord


SECRET = "d02-provider-free-test-token"
ACCOUNT_ID = "0123456789abcdef0123456789abcdef"
GLM_CANDIDATE_ID = "cloudflare_glm_4_7_flash_workers_free"
NEMOTRON_CANDIDATE_ID = "cloudflare_nemotron_3_120b_a12b_workers_free"


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


def _decision_json() -> str:
    return json.dumps(
        {
            "schema_version": "provider-decision-payload-v1",
            "kind": "ABSTAIN",
            "tool_name": None,
            "arguments": {},
            "evidence_id": None,
            "final": None,
            "message": "Cannot safely continue.",
            "reason_code": "NO_SAFE_PATH",
        },
        sort_keys=True,
    )


def _response(
    *,
    model: str,
    finish_reason: str = "stop",
    completion_tokens: int = 19,
    content: str | None = None,
) -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "id": "chatcmpl-d02-provider-free",
            "object": "chat.completion",
            "created": 1,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": _decision_json() if content is None else content,
                    },
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": completion_tokens,
                "total_tokens": 100 + completion_tokens,
            },
        },
    )


def _client(transport: ScriptedJsonTransport, model_id: str = CLOUDFLARE_GLM_MODEL_ID):
    return CloudflareWorkersAIChatCompletionsDecisionClientD02(
        api_token=SECRET,
        account_id=ACCOUNT_ID,
        model_id=model_id,
        transport=transport,
    )


def test_d02_changes_only_completion_cap_in_inherited_http_contract() -> None:
    transport = ScriptedJsonTransport(_response(model=CLOUDFLARE_GLM_MODEL_ID))
    client = _client(transport)
    request = _provider_request()

    assert client.complete(request) == _decision_json()
    call = transport.calls[0]
    assert call.body["max_completion_tokens"] == CLOUDFLARE_D02_MAX_COMPLETION_TOKENS == 1024
    assert call.body["temperature"] == 0
    assert call.body["n"] == 1
    assert call.body["stream"] is False
    assert call.body["store"] is False
    assert call.body["tool_choice"] == "none"
    assert call.body["parallel_tool_calls"] is False
    assert "tools" not in call.body
    assert "seed" not in call.body
    assert SECRET not in json.dumps(call.body, sort_keys=True)
    assert ACCOUNT_ID not in repr(client)
    assert SECRET not in repr(client)


def test_d02_finish_reason_failure_preserves_trace_contract_and_emits_ledger_diagnostic() -> None:
    transport = ScriptedJsonTransport(
        _response(
            model=CLOUDFLARE_GLM_MODEL_ID,
            finish_reason="length",
            completion_tokens=1024,
        )
    )
    client = _client(transport)
    source = CloudflareProviderDecisionSourceD02(
        client=client,
        registry=canonical_tool_registry(),
        call_identity=CloudflareProviderCallIdentityV2(
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            live_call=False,
        ),
    )
    context = ControllerContext(
        user_request="Inspect asset asset_dev_probe_001.",
        turn_index=0,
        tool_call_count=0,
    )
    request = source.build_request(context)

    with pytest.raises(ProviderHttpClientError) as exc_info:
        source.decide(context)
    assert exc_info.value.code == "CLOUDFLARE_FINISH_REASON_INVALID"

    audit_records = source.drain_audit_records()
    assert len(audit_records) == 1
    assert isinstance(audit_records[0], DecisionSourceAuditRecord)
    assert "failure_subtype" not in audit_records[0].metadata
    audit, valid, issues = validate_cloudflare_audit_record_d02(
        provider_id="cloudflare",
        model_id=CLOUDFLARE_GLM_MODEL_ID,
        route_id="cloudflare.workers_ai.openai_compat.chat_completions.v1",
        request_sha256=request.request_sha256,
        audit_records=audit_records,
        live_call=False,
    )
    assert valid is True
    assert issues == ()
    assert audit is not None
    assert audit.failure_code == "CLIENT_FAILURE"
    assert audit.raw_request_recorded is False
    assert audit.raw_response_recorded is False
    assert audit.exception_text_recorded is False

    diagnostics = source.drain_failure_diagnostics()
    diagnostic, diagnostic_valid, diagnostic_issues = validate_cloudflare_failure_diagnostic_d02(
        diagnostic_records=diagnostics,
        expected_call_id=audit.call_id,
    )
    assert diagnostic_valid is True
    assert diagnostic_issues == ()
    assert diagnostic is not None
    assert diagnostic.failure_subtype == "CLOUDFLARE_FINISH_REASON_INVALID"
    assert diagnostic.raw_request_recorded is False
    assert diagnostic.raw_response_recorded is False
    assert diagnostic.exception_text_recorded is False

    usage = client.drain_usage_records()
    assert len(usage) == 1
    assert usage[0].output_tokens == 1024
    assert usage[0].input_tokens == 100

    serialized_audit = json.dumps(audit_records[0].metadata, sort_keys=True)
    serialized_diagnostic = json.dumps(diagnostic.model_dump(mode="json"), sort_keys=True)
    assert _decision_json() not in serialized_audit
    assert _decision_json() not in serialized_diagnostic
    assert SECRET not in serialized_audit + serialized_diagnostic
    assert ACCOUNT_ID not in serialized_audit + serialized_diagnostic


def test_d02_transport_failure_keeps_only_sanitized_ledger_code() -> None:
    transport = ScriptedJsonTransport(ProviderHttpClientError("TRANSPORT_FAILURE"))
    client = _client(transport, CLOUDFLARE_NEMOTRON_MODEL_ID)
    source = CloudflareProviderDecisionSourceD02(
        client=client,
        registry=canonical_tool_registry(),
        call_identity=CloudflareProviderCallIdentityV2(
            model_id=CLOUDFLARE_NEMOTRON_MODEL_ID,
            live_call=False,
        ),
    )
    context = ControllerContext(
        user_request="Investigate asset asset_dev_probe_002.",
        turn_index=0,
        tool_call_count=0,
    )

    with pytest.raises(ProviderHttpClientError):
        source.decide(context)

    audit = source.drain_audit_records()[0]
    diagnostics = source.drain_failure_diagnostics()
    assert audit.metadata["failure_code"] == "CLIENT_FAILURE"
    assert len(diagnostics) == 1
    assert diagnostics[0].failure_subtype == "TRANSPORT_FAILURE"
    assert diagnostics[0].exception_text_recorded is False


def test_d02_resource_bound_is_derived_and_old_9000_gate_is_insufficient() -> None:
    assert worst_case_neurons_per_candidate_d02(GLM_CANDIDATE_ID) == pytest.approx(1300.3776)
    assert worst_case_neurons_per_candidate_d02(NEMOTRON_CANDIDATE_ID) == pytest.approx(8052.427776)
    assert CLOUDFLARE_D02_MAX_PACKET_NEURONS == pytest.approx(9352.805376)
    assert CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1 == pytest.approx(9352.805376)
    assert CLOUDFLARE_D02_MAX_MODELED_HEADROOM == pytest.approx(647.194624)
    assert 9000.0 < CLOUDFLARE_D02_MAX_PACKET_NEURONS < 10000.0

    with pytest.raises(ValueError, match="9352.805376"):
        CloudflareD02PreLiveEvidence(
            free_neurons_remaining=9000.0,
            evidence_source="provider-free-test",
        )

    accepted = CloudflareD02PreLiveEvidence(
        free_neurons_remaining=9352.805376,
        evidence_source="provider-free-test",
    )
    assert accepted.actual_cash_cost_usd == 0.0
    assert accepted.workers_paid_enabled is False


def test_d02_plan_is_same_geometry_as_d01_but_has_distinct_frozen_identity() -> None:
    plan = build_cloudflare_d02_plan()
    assert plan.plan_sha256 == CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    assert len(plan.entries) == 32
    assert [entry.attempt_index for entry in plan.entries] == list(range(32))
    assert {entry.candidate_id for entry in plan.entries} == {
        GLM_CANDIDATE_ID,
        NEMOTRON_CANDIDATE_ID,
    }
    assert all(entry.repeat_index in (0, 1) for entry in plan.entries)
