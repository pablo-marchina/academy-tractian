from __future__ import annotations

import json
from pathlib import Path

from academy_tractian.decision_source import build_provider_decision_request
from academy_tractian.provider_clients import ProviderHttpResponse
from academy_tractian.provider_tournament_cross_provider_v2 import (
    NVIDIA_CANDIDATE,
    OPENROUTER_CANDIDATE,
    HostedOpenAICompatibleDecisionClientV2,
    groq_candidate,
    run_synthetic_eligibility_probe,
)
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext


class _Transport:
    def __init__(self, candidate) -> None:
        self.candidate = candidate
        self.requests = []

    def post_json(self, request):
        self.requests.append(request)
        payload = {
            "schema_version": "provider-decision-payload-v1",
            "kind": "CLARIFY",
            "tool_name": None,
            "arguments": {},
            "evidence_id": None,
            "final": None,
            "message": "Please identify the equipment or asset.",
            "reason_code": "ASSET_REQUIRED",
        }
        response_model = self.candidate.acceptable_response_model_ids[0] if self.candidate.acceptable_response_model_ids else self.candidate.model_id
        return ProviderHttpResponse(
            status_code=200,
            body={
                "object": "chat.completion",
                "model": response_model,
                "choices": [{
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": json.dumps(payload)},
                }],
                "usage": {"prompt_tokens": 200, "completion_tokens": 30, "total_tokens": 230},
            },
        )


def _request():
    context = ControllerContext(
        user_request="Help with maintenance but the asset is not identified.",
        turn_index=0,
        tool_call_count=0,
        observations=(),
    )
    return build_provider_decision_request(context=context, registry=canonical_tool_registry())


def test_dp006_manifest_preserves_v3_geometry_and_contract() -> None:
    manifest = json.loads(Path("research/experiments/provider-tournament-cross-provider-v2-manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "PREREGISTERED_BEFORE_ANY_DP006_INFERENCE_CALL"
    assert manifest["source_contract"]["contract_mutation_allowed"] is False
    assert manifest["source_contract"]["population_sha256"] == "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9"
    assert manifest["experimental_design"]["attempts_per_candidate"] == 85
    assert manifest["experimental_design"]["total_live_evaluated_attempts"] == 255
    assert manifest["request_contract"]["automatic_retries"] == 0
    assert manifest["request_contract"]["automatic_fallbacks"] == 0
    assert manifest["request_contract"]["automatic_json_repair"] is False
    assert manifest["eligibility_protocol"]["probes_count_toward_tournament_denominator"] is False


def test_v2_route_request_matches_frozen_semantics() -> None:
    candidates = [
        groq_candidate("openai/gpt-oss-20b"),
        NVIDIA_CANDIDATE,
        OPENROUTER_CANDIDATE,
    ]
    for candidate in candidates:
        transport = _Transport(candidate)
        client = HostedOpenAICompatibleDecisionClientV2(
            candidate=candidate,
            api_key="provider-free-placeholder",
            transport=transport,
        )
        raw = client.complete(_request())
        assert json.loads(raw)["schema_version"] == "provider-decision-payload-v1"
        assert len(transport.requests) == 1
        sent = transport.requests[0]
        assert sent.body["temperature"] == 0
        assert sent.body["n"] == 1
        assert sent.body["stream"] is False
        assert sent.body["response_format"]["type"] == "json_schema"
        assert sent.body["response_format"]["json_schema"]["strict"] is False
        assert sent.body["response_format"]["json_schema"]["schema"]["additionalProperties"] is False
        assert "tools" not in sent.body
        if candidate.provider_id == "openrouter":
            assert sent.body["provider"] == {"allow_fallbacks": False, "require_parameters": True}
        else:
            assert "provider" not in sent.body


def test_synthetic_eligibility_must_parse_through_provider_decision_source() -> None:
    for candidate in [groq_candidate("openai/gpt-oss-20b"), NVIDIA_CANDIDATE, OPENROUTER_CANDIDATE]:
        result = run_synthetic_eligibility_probe(
            candidate=candidate,
            api_key="provider-free-placeholder",
            transport=_Transport(candidate),
        )
        assert result["passed"] is True
        assert result["decision_kind"] == "CLARIFY"
        assert result["audit_integrity"] is True
        assert result["usage_accounted_and_within_ceiling"] is True
        assert result["automatic_retry_count"] == 0
        assert result["automatic_fallback_count"] == 0
        assert result["raw_provider_material_recorded"] is False
