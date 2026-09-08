from __future__ import annotations

import json
from pathlib import Path

from academy_tractian.decision_source import build_provider_decision_request
from academy_tractian.provider_clients import ProviderHttpResponse
from academy_tractian.provider_tournament_cross_provider_v1 import (
    ATTEMPTS_PER_CANDIDATE,
    ATTEMPTS_PER_PACKET,
    BASE_MODEL_ID,
    CANDIDATES,
    CANDIDATE_IDS,
    REPETITIONS,
    TOTAL_ATTEMPTS,
    CrossProviderChatCompletionsDecisionClient,
    analyze_tournament,
    build_packet_plan,
    load_dp005_manifest,
)
from academy_tractian.provider_tournament_v3 import context_for_unit, load_frozen_tournament_v3
from academy_tractian.runtime import canonical_tool_registry


class _Transport:
    def __init__(self) -> None:
        self.requests = []

    def post_json(self, request):
        self.requests.append(request)
        body = request.body
        requested_model = body["model"]
        response_model = BASE_MODEL_ID if requested_model.endswith(":free") else requested_model
        payload = {
            "schema_version": "provider-decision-payload-v1",
            "kind": "CLARIFY",
            "tool_name": None,
            "arguments": {},
            "evidence_id": None,
            "final": None,
            "message": "Need one more detail.",
            "reason_code": "INSUFFICIENT_CONTEXT",
        }
        return ProviderHttpResponse(
            status_code=200,
            body={
                "object": "chat.completion",
                "model": response_model,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": json.dumps(payload)},
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                    "completion_tokens_details": {"reasoning_tokens": 5},
                },
            },
        )


def test_manifest_reuses_frozen_v3_contract() -> None:
    manifest = load_dp005_manifest(Path("."))
    assert manifest["source_contract"]["contract_mutation_allowed"] is False
    assert manifest["source_contract"]["population_sha256"] == "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9"
    assert manifest["experimental_design"]["total_live_attempts"] == 255
    assert manifest["request_contract"]["automatic_retries"] == 0
    assert manifest["request_contract"]["automatic_fallbacks"] == 0
    assert manifest["request_contract"]["automatic_json_repair"] is False


def test_balanced_geometry_has_85_attempts_per_candidate() -> None:
    bundle = load_frozen_tournament_v3(Path("."))
    counts = {candidate_id: 0 for candidate_id in CANDIDATE_IDS}
    total = 0
    for repetition_index in range(REPETITIONS):
        plan = build_packet_plan(bundle, repetition_index)
        assert len(plan) == ATTEMPTS_PER_PACKET
        for entry in plan:
            counts[entry.candidate_id] += 1
            total += 1
    assert total == TOTAL_ATTEMPTS
    assert set(counts.values()) == {ATTEMPTS_PER_CANDIDATE}


def test_all_clients_preserve_one_shot_structured_contract() -> None:
    bundle = load_frozen_tournament_v3(Path("."))
    context = context_for_unit(bundle, bundle.population["units"][0]["unit_id"])
    request = build_provider_decision_request(context=context, registry=canonical_tool_registry())
    for candidate in CANDIDATES:
        transport = _Transport()
        client = CrossProviderChatCompletionsDecisionClient(
            candidate=candidate,
            api_key="test-secret-not-real",
            transport=transport,
        )
        raw = client.complete(request)
        assert json.loads(raw)["schema_version"] == "provider-decision-payload-v1"
        assert len(transport.requests) == 1
        sent = transport.requests[0]
        assert sent.url == candidate.endpoint
        assert sent.body["temperature"] == 0
        assert sent.body["n"] == 1
        assert sent.body["stream"] is False
        assert sent.body["response_format"]["type"] == "json_schema"
        assert "tools" not in sent.body
        usage = client.drain_usage_records()
        assert len(usage) == 1
        assert usage[0].input_tokens == 100
        assert usage[0].output_tokens == 20
        if candidate.provider_id == "openrouter":
            assert sent.body["provider"] == {"allow_fallbacks": False, "require_parameters": True}
        else:
            assert "provider" not in sent.body


def _synthetic_attempt(candidate_id: str, unit_index: int, repetition_index: int, rubric_pass: bool) -> dict:
    return {
        "candidate_id": candidate_id,
        "unit_index": unit_index,
        "repetition_index": repetition_index,
        "outcome": "success",
        "failure_code": None,
        "decision_kind": "CLARIFY",
        "tool_name": None,
        "trace_integrity": True,
        "latency_ms": 10,
        "input_tokens": 100,
        "output_tokens": 20,
        "usage_accounted": True,
        "token_ceiling_violation": False,
        "known_tool_selection_valid": None,
        "b1_valid": None,
        "identity_seed_attempt": False,
        "private_key_attempt": False,
        "rubric_pass": rubric_pass,
        "raw_provider_material_recorded": False,
        "automatic_retry_count": 0,
        "automatic_fallback_count": 0,
    }


def test_preregistered_selection_requires_primary_quality_advantage(tmp_path: Path) -> None:
    packet_paths = []
    champion = CANDIDATE_IDS[0]
    for repetition_index in range(REPETITIONS):
        attempts = []
        for unit_index in range(17):
            for candidate_id in CANDIDATE_IDS:
                attempts.append(
                    _synthetic_attempt(
                        candidate_id,
                        unit_index,
                        repetition_index,
                        rubric_pass=candidate_id == champion,
                    )
                )
        path = tmp_path / f"packet-{repetition_index}.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": "provider-tournament-cross-provider-v1-packet",
                    "decision_id": "DP-005",
                    "repetition_index": repetition_index,
                    "population_sha256": "4205d00931150d83c510c7c6e58ad48bbd88da55654bac69ec35819af41299b9",
                    "attempt_count": ATTEMPTS_PER_PACKET,
                    "attempts": attempts,
                    "complete": True,
                }
            ),
            encoding="utf-8",
        )
        packet_paths.append(path)
    analysis = analyze_tournament(packet_paths)
    assert analysis["selection"] == f"PROMOTE:{champion}"
    assert analysis["candidate_summaries"][champion]["operational_outcome_accuracy"] == 1.0
    for candidate_id in CANDIDATE_IDS[1:]:
        assert analysis["candidate_summaries"][candidate_id]["operational_outcome_accuracy"] == 0.0
