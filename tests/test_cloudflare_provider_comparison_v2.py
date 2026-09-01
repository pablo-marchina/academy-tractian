from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

import academy_tractian.cloudflare_provider_live_v2 as live
from academy_tractian.cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
)
from academy_tractian.cloudflare_provider_comparison_v2 import (
    CLOUDFLARE_LIVE_CANDIDATE_IDS,
    EXPECTED_PLAN_SHA256,
    GLM_CANDIDATE_ID,
    MAX_PACKET_NEURONS,
    NEMOTRON_CANDIDATE_ID,
    CloudflareComparisonStopped,
    CloudflareProviderComparisonExecutorV2,
    build_cloudflare_provider_comparison_plan_v2,
    load_frozen_cloudflare_comparison_bundle_v2,
    observed_neurons,
    worst_case_neurons_for_candidate,
)
from academy_tractian.decision_source import ProviderDecisionRequest
from academy_tractian.provider_clients import (
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderUsageRecord,
    UrllibProviderJsonTransport,
)


SECRET = "cloudflare-v2-test-secret-never-persist"
ACCOUNT_ID = "0123456789abcdef0123456789abcdef"


def _json(kind: str, **kwargs: Any) -> str:
    base: dict[str, Any] = {
        "schema_version": "provider-decision-payload-v1",
        "kind": kind,
        "tool_name": None,
        "arguments": {},
        "evidence_id": None,
        "final": None,
        "message": None,
        "reason_code": None,
    }
    base.update(kwargs)
    return json.dumps(base, sort_keys=True)


def _good_response(text: str) -> str:
    if "asset_dev_probe_001" in text:
        return _json(
            "TOOL",
            tool_name="get_asset",
            arguments={"asset_id": "asset_dev_probe_001"},
        )
    if "asset_dev_probe_002" in text:
        return _json(
            "TOOL",
            tool_name="list_analyses",
            arguments={"asset_id": "asset_dev_probe_002"},
        )
    if "asset_dev_probe_003" in text:
        return _json(
            "TOOL",
            tool_name="get_data_quality",
            arguments={"asset_id": "asset_dev_probe_003"},
        )
    if "BPFO" in text or "bpfo" in text:
        return _json(
            "TOOL",
            tool_name="search_knowledge",
            arguments={"q": "Explain BPFO", "type": "glossary"},
        )
    if "asset I mentioned" in text:
        return _json(
            "CLARIFY",
            message="Which asset should I investigate?",
            reason_code="MISSING_ASSET",
        )
    if "human specialist" in text:
        return _json(
            "ESCALATE",
            message="A human specialist should review the case.",
            reason_code="USER_REQUESTED_HUMAN",
        )
    if "asset_dev_probe_007" in text:
        return _json(
            "ABSTAIN",
            message="The requested signal evidence is unavailable.",
            reason_code="UPSTREAM_UNAVAILABLE",
        )
    if "analysis_dev_probe_008" in text:
        return _json(
            "FINAL",
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "The action remains blocked by policy.",
            },
        )
    raise AssertionError(text)


class FixtureDecisionClient:
    def __init__(self, *, usage: tuple[int | None, int | None] = (100, 20)) -> None:
        self.usage = usage
        self.records: list[ProviderUsageRecord] = []
        self.calls = 0

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls += 1
        input_tokens, output_tokens = self.usage
        self.records.append(
            ProviderUsageRecord(
                provider_id="fixture",
                model_id="fixture",
                route_id="fixture",
                request_sha256=request.request_sha256,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=(
                    None
                    if input_tokens is None or output_tokens is None
                    else input_tokens + output_tokens
                ),
            )
        )
        return _good_response(request.user_request)

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self.records)
        self.records.clear()
        return records


class NoUsageClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, request: ProviderDecisionRequest) -> str:
        self.calls += 1
        return _good_response(request.user_request)


class DynamicCloudflareTransport:
    def __init__(self) -> None:
        self.calls: list[ProviderHttpRequest] = []

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls.append(request)
        model = request.body["model"]
        user_text = request.body["messages"][1]["content"]
        decision = _good_response(user_text)
        return ProviderHttpResponse(
            status_code=200,
            body={
                "id": f"fixture-{len(self.calls)}",
                "object": "chat.completion",
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": decision},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                },
            },
        )


def _fixture_clients(*, usage: tuple[int | None, int | None] = (100, 20)):
    return {
        GLM_CANDIDATE_ID: FixtureDecisionClient(usage=usage),
        NEMOTRON_CANDIDATE_ID: FixtureDecisionClient(usage=usage),
    }


def _pre_live_evidence(neurons: float = 9000.0) -> live.CloudflarePreLiveEvidence:
    return live.CloudflarePreLiveEvidence(
        free_neurons_remaining=neurons,
        utc_day="2026-09-01",
        evidence_source="provider-free-fixture-only",
    )


def _secrets() -> live.CloudflareLiveSecrets:
    return live.CloudflareLiveSecrets(api_token=SECRET, account_id=ACCOUNT_ID)


def test_frozen_v2_bundle_and_plan_are_exact_and_distinct_from_adr010() -> None:
    bundle = load_frozen_cloudflare_comparison_bundle_v2()
    plan = build_cloudflare_provider_comparison_plan_v2(bundle)

    assert plan.plan_sha256 == EXPECTED_PLAN_SHA256
    assert plan.plan_sha256 != "69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f"
    assert len(plan.entries) == 32
    assert [item.attempt_index for item in plan.entries] == list(range(32))
    assert sum(item.candidate_id == GLM_CANDIDATE_ID for item in plan.entries) == 16
    assert sum(item.candidate_id == NEMOTRON_CANDIDATE_ID for item in plan.entries) == 16
    assert [item.candidate_id for item in plan.entries[:8]] == [
        GLM_CANDIDATE_ID,
        NEMOTRON_CANDIDATE_ID,
        NEMOTRON_CANDIDATE_ID,
        GLM_CANDIDATE_ID,
        NEMOTRON_CANDIDATE_ID,
        GLM_CANDIDATE_ID,
        GLM_CANDIDATE_ID,
        NEMOTRON_CANDIDATE_ID,
    ]


def test_frozen_neuron_math_matches_adr018_budget() -> None:
    assert worst_case_neurons_for_candidate(GLM_CANDIDATE_ID) == pytest.approx(62.6368)
    assert worst_case_neurons_for_candidate(NEMOTRON_CANDIDATE_ID) == pytest.approx(433.458368)
    assert (
        16 * worst_case_neurons_for_candidate(GLM_CANDIDATE_ID)
        + 16 * worst_case_neurons_for_candidate(NEMOTRON_CANDIDATE_ID)
    ) == pytest.approx(MAX_PACKET_NEURONS)
    assert observed_neurons(GLM_CANDIDATE_ID, input_tokens=100, output_tokens=20) > 0


def test_provider_free_fixture_executes_exact_32_and_never_selects() -> None:
    bundle = load_frozen_cloudflare_comparison_bundle_v2()
    executor = CloudflareProviderComparisonExecutorV2(
        bundle=bundle,
        clients=_fixture_clients(),
        fixture_result=True,
        available_free_neurons=9000,
        zero_cash_cost_route_proven=True,
    )
    attempts = executor.run_all_fixture()
    assert len(attempts) == 32
    assert executor.budget.consumed == 32
    assert not executor.stopped

    result = executor.finalize(
        fixed_failure_probe_passed={candidate: True for candidate in CLOUDFLARE_LIVE_CANDIDATE_IDS}
    )
    assert result.complete
    assert result.resource_accounting_complete
    assert result.actual_cash_cost_usd == 0.0
    assert result.packet_observed_neurons > 0
    assert result.packet_observed_neurons < MAX_PACKET_NEURONS
    assert result.selection == "NO_SELECTION"
    assert result.production_selection_claim is False
    for summary in result.candidates:
        assert summary.complete
        assert summary.M8_usage_complete
        assert summary.M8_total_observed_neurons is not None
        assert summary.M8_actual_cash_cost_usd == 0.0
        assert summary.hard_gate_pass


def test_missing_usage_fails_closed_after_first_attempt() -> None:
    bundle = load_frozen_cloudflare_comparison_bundle_v2()
    clients = {
        GLM_CANDIDATE_ID: NoUsageClient(),
        NEMOTRON_CANDIDATE_ID: NoUsageClient(),
    }
    executor = CloudflareProviderComparisonExecutorV2(
        bundle=bundle,
        clients=clients,
        fixture_result=True,
        available_free_neurons=9000,
        zero_cash_cost_route_proven=True,
    )
    first = executor.execute_next()
    assert first.attempt_index == 0
    assert executor.stopped
    assert executor.stop_reason == "H9_RESOURCE_ACCOUNTING_INCOMPLETE"
    assert executor.budget.consumed == 1
    with pytest.raises(CloudflareComparisonStopped):
        executor.execute_next()

    result = executor.finalize(
        fixed_failure_probe_passed={candidate: True for candidate in CLOUDFLARE_LIVE_CANDIDATE_IDS}
    )
    assert not result.complete
    assert not result.resource_accounting_complete
    assert result.selection == "NO_SELECTION"


def test_observed_prompt_and_completion_ceilings_stop_before_next_attempt() -> None:
    bundle = load_frozen_cloudflare_comparison_bundle_v2()
    prompt_executor = CloudflareProviderComparisonExecutorV2(
        bundle=bundle,
        clients=_fixture_clients(usage=(8001, 20)),
        fixture_result=True,
        available_free_neurons=9000,
        zero_cash_cost_route_proven=True,
    )
    prompt_executor.execute_next()
    assert prompt_executor.stop_reason == "H10_PROMPT_TOKEN_CEILING_EXCEEDED"
    assert prompt_executor.budget.consumed == 1

    completion_executor = CloudflareProviderComparisonExecutorV2(
        bundle=bundle,
        clients=_fixture_clients(usage=(100, 513)),
        fixture_result=True,
        available_free_neurons=9000,
        zero_cash_cost_route_proven=True,
    )
    completion_executor.execute_next()
    assert completion_executor.stop_reason == "H10_COMPLETION_TOKEN_CEILING_EXCEEDED"
    assert completion_executor.budget.consumed == 1


def test_projected_remaining_resource_guard_stops_before_claim_or_call() -> None:
    bundle = load_frozen_cloudflare_comparison_bundle_v2()
    clients = _fixture_clients()
    executor = CloudflareProviderComparisonExecutorV2(
        bundle=bundle,
        clients=clients,
        fixture_result=True,
        available_free_neurons=9000,
        zero_cash_cost_route_proven=True,
    )
    executor.packet_observed_neurons = 2000.0
    with pytest.raises(CloudflareComparisonStopped, match="H10_PROJECTED"):
        executor.assert_next_attempt_allowed()
    assert executor.budget.consumed == 0
    assert sum(client.calls for client in clients.values()) == 0


def test_pre_live_evidence_is_fail_closed_and_probe_free() -> None:
    evidence = _pre_live_evidence(9000)
    assert evidence.workers_plan == "Workers Free"
    assert evidence.workers_paid_enabled is False
    assert evidence.prepaid_ai_gateway_enabled is False
    assert evidence.actual_cash_cost_usd == 0.0
    assert evidence.inference_used_to_obtain_evidence is False
    assert evidence.credential_account_probe_used is False

    with pytest.raises(ValidationError, match="9000"):
        _pre_live_evidence(8999)
    with pytest.raises(ValidationError):
        live.CloudflarePreLiveEvidence(
            workers_paid_enabled=True,
            free_neurons_remaining=9000,
            utc_day="2026-09-01",
            evidence_source="invalid",
        )
    with pytest.raises(ValidationError):
        live.CloudflarePreLiveEvidence(
            prepaid_ai_gateway_enabled=True,
            free_neurons_remaining=9000,
            utc_day="2026-09-01",
            evidence_source="invalid",
        )


def test_exact_client_factory_and_one_shot_transport_construct_without_network() -> None:
    class NoCallTransport:
        def __init__(self) -> None:
            self.calls = 0

        def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
            self.calls += 1
            raise AssertionError("must not be called during construction")

    transport = NoCallTransport()
    clients = live.build_cloudflare_live_clients_v2(secrets=_secrets(), transport=transport)
    assert set(clients) == set(CLOUDFLARE_LIVE_CANDIDATE_IDS)
    assert clients[GLM_CANDIDATE_ID].model_id == CLOUDFLARE_GLM_MODEL_ID
    assert clients[NEMOTRON_CANDIDATE_ID].model_id == CLOUDFLARE_NEMOTRON_MODEL_ID
    assert transport.calls == 0
    assert SECRET not in repr(clients[GLM_CANDIDATE_ID])
    assert ACCOUNT_ID not in repr(clients[GLM_CANDIDATE_ID])
    assert isinstance(live.build_cloudflare_one_shot_transport_v2(), UrllibProviderJsonTransport)


def test_two_model_fixed_m5_probes_are_provider_free() -> None:
    assert live.run_cloudflare_provider_free_fixed_failure_probes_v2() == {
        GLM_CANDIDATE_ID: True,
        NEMOTRON_CANDIDATE_ID: True,
    }


def test_missing_secrets_fail_before_custody_exists(tmp_path: Path) -> None:
    root = tmp_path / "custody"
    with pytest.raises(live.MissingCloudflareSecretsError):
        live.GovernedCloudflareLiveTaskV2.prepare(
            custody_root=root,
            secrets=live.CloudflareLiveSecrets(api_token="", account_id=ACCOUNT_ID),
            pre_live_evidence=_pre_live_evidence(),
            transport=DynamicCloudflareTransport(),
            fixture_result=True,
        )
    assert not root.exists()


def test_prepare_reserves_sanitized_v2_custody_and_refuses_reset(tmp_path: Path) -> None:
    root = tmp_path / "custody"
    transport = DynamicCloudflareTransport()
    task = live.GovernedCloudflareLiveTaskV2.prepare(
        custody_root=root,
        secrets=_secrets(),
        pre_live_evidence=_pre_live_evidence(),
        transport=transport,
        fixture_result=True,
    )
    assert transport.calls == []
    marker = json.loads(task.custody_path.read_text(encoding="utf-8"))
    ledger = json.loads(
        (root / live.CANONICAL_RUN_DIRNAME / live.LEDGER_FILENAME).read_text(encoding="utf-8")
    )
    assert marker["plan_sha256"] == EXPECTED_PLAN_SHA256
    assert marker["workers_free_required"] is True
    assert marker["workers_paid_enabled"] is False
    assert marker["prepaid_ai_gateway_enabled"] is False
    assert marker["available_free_neurons_at_reservation"] == 9000
    assert marker["credentials_recorded"] is False
    assert len(ledger["entries"]) == 32
    assert all(item["state"] == "pending" for item in ledger["entries"])
    serialized = json.dumps({"marker": marker, "ledger": ledger}, sort_keys=True)
    assert SECRET not in serialized
    assert ACCOUNT_ID not in serialized

    with pytest.raises(live.ExistingCloudflareRunError, match="refusing a second run"):
        live.GovernedCloudflareLiveTaskV2.prepare(
            custody_root=root,
            secrets=_secrets(),
            pre_live_evidence=_pre_live_evidence(),
            transport=DynamicCloudflareTransport(),
            fixture_result=True,
        )


def test_governed_provider_free_fixture_completes_32_with_durable_ledger(tmp_path: Path) -> None:
    root = tmp_path / "custody"
    transport = DynamicCloudflareTransport()
    task = live.GovernedCloudflareLiveTaskV2.prepare(
        custody_root=root,
        secrets=_secrets(),
        pre_live_evidence=_pre_live_evidence(),
        transport=transport,
        fixture_result=True,
    )
    result = task.execute_all()
    assert result.state == "complete"
    assert result.completed_attempts == 32
    assert result.consumed_or_uncertain_attempts == 32
    assert result.selection == "NO_SELECTION"
    assert result.production_selection_claim is False
    assert len(transport.calls) == 32

    run_dir = root / live.CANONICAL_RUN_DIRNAME
    ledger = json.loads((run_dir / live.LEDGER_FILENAME).read_text(encoding="utf-8"))
    persisted_result = json.loads((run_dir / live.RESULT_FILENAME).read_text(encoding="utf-8"))
    assert ledger["state"] == "complete"
    assert all(item["state"] == "completed" for item in ledger["entries"])
    serialized = json.dumps({"ledger": ledger, "result": persisted_result}, sort_keys=True)
    assert SECRET not in serialized
    assert ACCOUNT_ID not in serialized
    assert persisted_result["raw_provider_material_recorded"] is False
    assert persisted_result["actual_cash_cost_usd"] == 0.0


def test_internal_failure_after_claim_is_uncertain_and_not_replayed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "custody"
    transport = DynamicCloudflareTransport()
    task = live.GovernedCloudflareLiveTaskV2.prepare(
        custody_root=root,
        secrets=_secrets(),
        pre_live_evidence=_pre_live_evidence(),
        transport=transport,
        fixture_result=True,
    )

    def explode(self):
        ledger = json.loads(
            (root / live.CANONICAL_RUN_DIRNAME / live.LEDGER_FILENAME).read_text(
                encoding="utf-8"
            )
        )
        assert ledger["entries"][0]["state"] == "claimed"
        raise RuntimeError(f"raw internal detail {SECRET}")

    monkeypatch.setattr(CloudflareProviderComparisonExecutorV2, "execute_next", explode)
    with pytest.raises(live.CloudflareLiveExecutionStopped, match="EXECUTOR_INTERNAL_FAILURE"):
        task.execute_all()

    run_dir = root / live.CANONICAL_RUN_DIRNAME
    ledger = json.loads((run_dir / live.LEDGER_FILENAME).read_text(encoding="utf-8"))
    result = json.loads((run_dir / live.RESULT_FILENAME).read_text(encoding="utf-8"))
    assert ledger["entries"][0]["state"] == "uncertain"
    assert ledger["entries"][0]["stop_code"] == "EXECUTOR_INTERNAL_FAILURE"
    assert result["consumed_or_uncertain_attempts"] == 1
    assert result["selection"] == "NO_SELECTION"
    assert SECRET not in json.dumps({"ledger": ledger, "result": result}, sort_keys=True)
    assert transport.calls == []


def test_failure_after_custody_reservation_keeps_marker_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "custody"

    def explode(**kwargs):
        raise RuntimeError("post-custody preparation failure")

    monkeypatch.setattr(live.GovernedCloudflareProviderComparisonV2, "prepare", explode)
    with pytest.raises(RuntimeError, match="post-custody"):
        live.GovernedCloudflareLiveTaskV2.prepare(
            custody_root=root,
            secrets=_secrets(),
            pre_live_evidence=_pre_live_evidence(),
            transport=DynamicCloudflareTransport(),
            fixture_result=True,
        )
    assert (root / live.CLOUDFLARE_CUSTODY_FILENAME).exists()
    with pytest.raises(live.ExistingCloudflareRunError):
        live.GovernedCloudflareLiveTaskV2.prepare(
            custody_root=root,
            secrets=_secrets(),
            pre_live_evidence=_pre_live_evidence(),
            transport=DynamicCloudflareTransport(),
            fixture_result=True,
        )
