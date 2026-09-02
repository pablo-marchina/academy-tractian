from __future__ import annotations

import json
from pathlib import Path

import pytest

from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
)
from academy_tractian.cloudflare_provider_comparison_v2 import (
    GLM_CANDIDATE_ID,
    NEMOTRON_CANDIDATE_ID,
    load_frozen_cloudflare_comparison_bundle_v2,
)
from academy_tractian.cloudflare_provider_d02 import (
    CLOUDFLARE_D02_MAX_PACKET_NEURONS,
    CloudflareD02PreLiveEvidence,
    build_cloudflare_d02_plan,
)
from academy_tractian.cloudflare_provider_d02_executor import (
    CLOUDFLARE_D02_CUSTODY_FILENAME,
    CLOUDFLARE_D02_LEDGER_FILENAME,
    CLOUDFLARE_D02_RESULT_FILENAME,
    CLOUDFLARE_D02_RUN_DIRNAME,
    CloudflareD02ComparisonExecutor,
    CloudflareD02InvariantError,
    DurableCloudflareD02Ledger,
    GovernedCloudflareD02Task,
    build_d02_clients,
    run_d02_provider_free_fixed_failure_probes,
)
from academy_tractian.provider_clients import ProviderHttpRequest, ProviderHttpResponse


class ScriptedTransport:
    def __init__(self, responses: list[ProviderHttpResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[ProviderHttpRequest] = []

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls.append(request)
        if not self.responses:
            raise AssertionError("scripted D02 transport exhausted")
        return self.responses.pop(0)


def _decision_json(kind: str = "ABSTAIN") -> str:
    return json.dumps(
        {
            "schema_version": "provider-decision-payload-v1",
            "kind": kind,
            "tool_name": None,
            "arguments": {},
            "evidence_id": None,
            "final": None,
            "message": "Provider-free D02 fixture decision.",
            "reason_code": "PROVIDER_FREE_FIXTURE",
        },
        sort_keys=True,
    )


def _response(
    model_id: str,
    *,
    finish_reason: str = "stop",
    output_tokens: int = 20,
) -> ProviderHttpResponse:
    return ProviderHttpResponse(
        status_code=200,
        body={
            "id": "provider-free-d02",
            "object": "chat.completion",
            "created": 1,
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": _decision_json()},
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": output_tokens,
                "total_tokens": 100 + output_tokens,
            },
        },
    )


def _clients(*, glm_responses: list[ProviderHttpResponse], nemotron_responses: list[ProviderHttpResponse]):
    transports = {
        GLM_CANDIDATE_ID: ScriptedTransport(glm_responses),
        NEMOTRON_CANDIDATE_ID: ScriptedTransport(nemotron_responses),
    }
    clients = build_d02_clients(
        api_token="provider-free-d02-test-token",
        account_id="0123456789abcdef0123456789abcdef",
        transports=transports,
    )
    return clients, transports


def _evidence(free_neurons: float = 10000.0) -> CloudflareD02PreLiveEvidence:
    return CloudflareD02PreLiveEvidence(
        free_neurons_remaining=free_neurons,
        evidence_source="provider-free-d02-test",
    )


def test_d02_fixed_failure_probes_are_one_shot_and_sanitized() -> None:
    assert run_d02_provider_free_fixed_failure_probes() == {
        GLM_CANDIDATE_ID: True,
        NEMOTRON_CANDIDATE_ID: True,
    }


def test_d02_executor_records_finish_reason_subtype_at_1024_without_stopping() -> None:
    clients, transports = _clients(
        glm_responses=[
            _response(CLOUDFLARE_GLM_MODEL_ID, finish_reason="length", output_tokens=1024)
        ],
        nemotron_responses=[],
    )
    executor = CloudflareD02ComparisonExecutor(
        bundle=load_frozen_cloudflare_comparison_bundle_v2(),
        plan=build_cloudflare_d02_plan(),
        clients=clients,
        fixture_result=True,
        available_free_neurons=10000.0,
        zero_cash_cost_route_proven=True,
    )

    attempt = executor.execute_next()

    assert attempt.attempt_index == 0
    assert attempt.candidate_id == GLM_CANDIDATE_ID
    assert attempt.outcome == "failure"
    assert attempt.failure_code == "CLIENT_FAILURE"
    assert attempt.failure_subtype == "CLOUDFLARE_FINISH_REASON_INVALID"
    assert attempt.output_tokens == 1024
    assert attempt.trace_integrity is True
    assert attempt.raw_material_recorded is False
    assert executor.stopped is False
    assert len(transports[GLM_CANDIDATE_ID].calls) == 1
    assert transports[GLM_CANDIDATE_ID].calls[0].body["max_completion_tokens"] == 1024


def test_d02_executor_rejects_old_9000_start_gate() -> None:
    clients, _ = _clients(glm_responses=[], nemotron_responses=[])
    with pytest.raises(ValueError, match="9352.805376"):
        CloudflareD02ComparisonExecutor(
            bundle=load_frozen_cloudflare_comparison_bundle_v2(),
            plan=build_cloudflare_d02_plan(),
            clients=clients,
            fixture_result=True,
            available_free_neurons=9000.0,
            zero_cash_cost_route_proven=True,
        )
    assert CLOUDFLARE_D02_MAX_PACKET_NEURONS == pytest.approx(9352.805376)


def test_d02_ledger_write_ahead_claim_and_uncertain_state_forbid_replay(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    ledger = DurableCloudflareD02Ledger.create(
        run_dir=run_dir,
        plan=build_cloudflare_d02_plan(),
        pre_live_evidence=_evidence(),
    )

    ledger.claim(0)
    persisted = json.loads((run_dir / CLOUDFLARE_D02_LEDGER_FILENAME).read_text())
    assert persisted["entries"][0]["state"] == "claimed"
    assert persisted["entries"][1]["state"] == "pending"

    with pytest.raises(CloudflareD02InvariantError, match="claimed/uncertain"):
        ledger.claim(1)

    ledger.mark_uncertain(0, "NETWORK_OUTCOME_UNCERTAIN")
    persisted = json.loads((run_dir / CLOUDFLARE_D02_LEDGER_FILENAME).read_text())
    assert persisted["state"] == "stopped"
    assert persisted["entries"][0]["state"] == "uncertain"
    assert persisted["entries"][0]["attempt"] is None

    with pytest.raises(CloudflareD02InvariantError, match="claimed/uncertain"):
        ledger.claim(1)


def test_governed_d02_provider_free_packet_completes_32_with_distinct_custody(tmp_path: Path) -> None:
    glm_responses = [_response(CLOUDFLARE_GLM_MODEL_ID) for _ in range(16)]
    nemotron_responses = [_response(CLOUDFLARE_NEMOTRON_MODEL_ID) for _ in range(16)]
    clients, transports = _clients(
        glm_responses=glm_responses,
        nemotron_responses=nemotron_responses,
    )

    task = GovernedCloudflareD02Task.prepare_provider_free(
        custody_root=tmp_path / "custody-d02",
        clients=clients,
        pre_live_evidence=_evidence(),
    )
    result = task.execute_all()

    assert result.state == "complete"
    assert result.completed_attempts == 32
    assert result.consumed_or_uncertain_attempts == 32
    assert result.selection == "NO_SELECTION"
    assert result.production_selection_claim is False
    assert result.raw_provider_material_recorded is False
    assert result.actual_cash_cost_usd == 0.0
    assert result.provider_result is not None
    assert result.provider_result["attempted_calls"] == 32
    assert result.provider_result["resource_accounting_complete"] is True
    assert result.provider_result["actual_cash_cost_usd"] == 0.0
    assert len(transports[GLM_CANDIDATE_ID].calls) == 16
    assert len(transports[NEMOTRON_CANDIDATE_ID].calls) == 16

    custody_root = tmp_path / "custody-d02"
    assert (custody_root / CLOUDFLARE_D02_CUSTODY_FILENAME).is_file()
    run_dir = custody_root / CLOUDFLARE_D02_RUN_DIRNAME
    assert (run_dir / CLOUDFLARE_D02_LEDGER_FILENAME).is_file()
    assert (run_dir / CLOUDFLARE_D02_RESULT_FILENAME).is_file()

    ledger = json.loads((run_dir / CLOUDFLARE_D02_LEDGER_FILENAME).read_text())
    assert ledger["state"] == "complete"
    assert all(item["state"] == "completed" for item in ledger["entries"])
    assert all(item["attempt"]["raw_material_recorded"] is False for item in ledger["entries"])
    serialized = json.dumps(ledger, sort_keys=True)
    assert "provider-free-d02-test-token" not in serialized
    assert "0123456789abcdef0123456789abcdef" not in serialized


def test_d02_custody_is_exclusive_create(tmp_path: Path) -> None:
    clients, _ = _clients(
        glm_responses=[_response(CLOUDFLARE_GLM_MODEL_ID) for _ in range(16)],
        nemotron_responses=[_response(CLOUDFLARE_NEMOTRON_MODEL_ID) for _ in range(16)],
    )
    root = tmp_path / "same-custody"
    GovernedCloudflareD02Task.prepare_provider_free(
        custody_root=root,
        clients=clients,
        pre_live_evidence=_evidence(),
    )

    from academy_tractian.cloudflare_provider_d02_executor import CloudflareD02ExistingRunError

    with pytest.raises(CloudflareD02ExistingRunError, match="custody already exists"):
        GovernedCloudflareD02Task.prepare_provider_free(
            custody_root=root,
            clients=clients,
            pre_live_evidence=_evidence(),
        )
