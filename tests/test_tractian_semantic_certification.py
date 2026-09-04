from __future__ import annotations

from collections import deque
from datetime import UTC, datetime, timedelta

from academy_tractian.tractian_semantic_certification import run_tractian_semantic_certification
from academy_tractian.tractian_transport_campaign import (
    TractianTransportCampaignManifest,
    TransportProbeFixture,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse


class _FakeTransport:
    def __init__(self, *responses: TransportResponse | Exception) -> None:
        self.responses = deque(responses)
        self.requests: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.requests.append(request)
        response = self.responses.popleft()
        if isinstance(response, Exception):
            raise response
        return response


class _Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 9, 4, 15, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        current = self.value
        self.value += timedelta(microseconds=1)
        return current


def _manifest(*fixtures: TransportProbeFixture) -> TractianTransportCampaignManifest:
    return TractianTransportCampaignManifest(
        identity_id="semantic-identity",
        user_id="semantic-user",
        seed="semantic-seed",
        fixtures=fixtures,
    )


def _states(ledger, operation: str) -> dict[str, bool]:
    return {
        record.dimension: record.passed
        for record in ledger.records
        if record.operation == operation
    }


def test_read_live_response_is_certified_without_a_second_network_call() -> None:
    transport = _FakeTransport(
        TransportResponse(200, {"x-safe": "header"}, {"private": "SECRET-RESPONSE-BODY"})
    )
    manifest = _manifest(
        TransportProbeFixture(
            operation="get_asset",
            valid_arguments={"asset_id": "asset-live"},
        )
    )

    run, transport_ledger, semantic_ledger, summary = run_tractian_semantic_certification(
        manifest=manifest,
        transport=transport,
        now=_Clock(),
    )

    assert len(transport.requests) == 1
    assert run.results[0].valid_probe == "success"
    assert transport_ledger.unique_success_operations("hosted_live") == {"get_asset"}
    assert _states(semantic_ledger, "get_asset") == {
        "invalid_parameters_rejected": True,
        "response_normalization_verified": True,
        "agent_evaluator_behavior_verified": True,
    }
    assert summary.invalid_parameter_passes == 1
    assert summary.response_normalization_passes == 1
    assert summary.agent_evaluator_passes == 1
    safe_semantic_output = "".join(record.model_dump_json() for record in semantic_ledger.records)
    assert "SECRET-RESPONSE-BODY" not in safe_semantic_output
    assert "asset-live" not in safe_semantic_output


def test_http_error_response_can_still_certify_runtime_failure_normalization() -> None:
    transport = _FakeTransport(TransportResponse(404, {}, {"error": "not found"}))
    manifest = _manifest(
        TransportProbeFixture(
            operation="get_asset",
            valid_arguments={"asset_id": "missing-asset"},
        )
    )

    run, _, semantic_ledger, summary = run_tractian_semantic_certification(
        manifest=manifest,
        transport=transport,
        now=_Clock(),
    )

    assert len(transport.requests) == 1
    assert run.results[0].valid_probe == "http_error_observed"
    assert _states(semantic_ledger, "get_asset") == {
        "invalid_parameters_rejected": True,
        "response_normalization_verified": True,
        "agent_evaluator_behavior_verified": True,
    }
    assert summary.semantic_record_count == 3


def test_blocked_action_certifies_parameter_rejection_but_does_not_invent_live_semantics() -> None:
    transport = _FakeTransport()
    manifest = _manifest(
        TransportProbeFixture(
            operation="update_asset_config",
            valid_arguments={
                "asset_id": "asset-action",
                "body": {
                    "justification": "Controlled semantic certification justification.",
                    "changes": {"criticality": "high"},
                },
            },
        )
    )

    run, _, semantic_ledger, summary = run_tractian_semantic_certification(
        manifest=manifest,
        transport=transport,
        allow_actions=False,
        now=_Clock(),
    )

    assert transport.requests == []
    assert run.results[0].valid_probe == "blocked_by_safety"
    assert _states(semantic_ledger, "update_asset_config") == {
        "invalid_parameters_rejected": True,
    }
    assert summary.invalid_parameter_passes == 1
    assert summary.response_normalization_passes == 0
    assert summary.agent_evaluator_passes == 0


def test_approved_action_live_response_is_replayed_semantically_without_second_mutation() -> None:
    transport = _FakeTransport(TransportResponse(202, {}, {"accepted": True}))
    manifest = _manifest(
        TransportProbeFixture(
            operation="update_asset_config",
            valid_arguments={
                "asset_id": "asset-action-approved",
                "body": {
                    "justification": "Approved controlled live semantic certification action.",
                    "changes": {"criticality": "medium"},
                },
            },
            action_execution_approved=True,
            action_approval_ref="approval-semantic-action-001",
        )
    )

    run, _, semantic_ledger, summary = run_tractian_semantic_certification(
        manifest=manifest,
        transport=transport,
        allow_actions=True,
        now=_Clock(),
    )

    assert len(transport.requests) == 1
    assert run.results[0].valid_probe == "success"
    assert run.results[0].action_live_execution_enabled is True
    assert _states(semantic_ledger, "update_asset_config") == {
        "invalid_parameters_rejected": True,
        "response_normalization_verified": True,
        "agent_evaluator_behavior_verified": True,
    }
    assert summary.semantic_record_count == 3


def test_b0_valid_but_runtime_invalid_action_fails_agent_evaluator_certification() -> None:
    transport = _FakeTransport(TransportResponse(202, {}, {"accepted": True}))
    manifest = _manifest(
        TransportProbeFixture(
            operation="update_asset_config",
            valid_arguments={
                "asset_id": "asset-action-invalid-runtime",
                "body": {"changes": {"criticality": "high"}},
            },
            action_execution_approved=True,
            action_approval_ref="approval-semantic-action-002",
        )
    )

    _, _, semantic_ledger, summary = run_tractian_semantic_certification(
        manifest=manifest,
        transport=transport,
        allow_actions=True,
        now=_Clock(),
    )

    assert len(transport.requests) == 1
    states = _states(semantic_ledger, "update_asset_config")
    assert states["invalid_parameters_rejected"] is True
    assert states["response_normalization_verified"] is False
    assert states["agent_evaluator_behavior_verified"] is False
    assert summary.agent_evaluator_passes == 0
