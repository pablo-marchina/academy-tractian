from __future__ import annotations

from collections import deque

import pytest
from pydantic import ValidationError

from academy_tractian.tractian_transport_campaign import (
    TractianTransportCampaignManifest,
    TransportProbeFixture,
    run_tractian_transport_campaign,
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


def _manifest(*fixtures: TransportProbeFixture) -> TractianTransportCampaignManifest:
    return TractianTransportCampaignManifest(
        identity_id="identity-campaign",
        user_id="user-campaign",
        seed="seed-campaign",
        fixtures=fixtures,
    )


def test_fixture_rejects_unknown_operation_as_controlled_contract_error() -> None:
    with pytest.raises(ValidationError, match="unknown_transport_probe_operation"):
        TransportProbeFixture(
            operation="invented_operation",
            valid_arguments={},
        )


def test_manifest_rejects_missing_required_valid_arguments_before_network() -> None:
    fixture = TransportProbeFixture(
        operation="get_asset",
        valid_arguments={},
    )
    with pytest.raises(ValidationError, match="invalid_valid_probe_arguments:get_asset"):
        _manifest(fixture)


def test_read_fixture_cannot_smuggle_action_approval_metadata() -> None:
    with pytest.raises(ValidationError, match="read_fixture_cannot_carry_action_approval"):
        TransportProbeFixture(
            operation="get_asset",
            valid_arguments={"asset_id": "asset-1"},
            action_execution_approved=True,
            action_approval_ref="approval-read-1",
        )


def test_read_campaign_records_real_success_and_http_error_without_raw_payloads() -> None:
    manifest = _manifest(
        TransportProbeFixture(
            operation="get_asset",
            valid_arguments={"asset_id": "asset-sensitive-valid"},
            error_arguments={"asset_id": "asset-sensitive-missing"},
        )
    )
    transport = _FakeTransport(
        TransportResponse(200, {}, {"private": "response-body"}),
        TransportResponse(404, {}, {"private": "missing-body"}),
    )

    run, ledger = run_tractian_transport_campaign(manifest=manifest, transport=transport)

    assert len(transport.requests) == 2
    assert run.configured_operations == 1
    assert run.executed_operations == 1
    assert run.successful_valid_probes == 1
    assert run.observed_http_error_probes == 1
    assert run.results[0].valid_probe == "success"
    assert run.results[0].error_probe == "http_error_observed"
    assert ledger.unique_success_operations("hosted_live") == {"get_asset"}
    assert ledger.unique_outcome_operations("hosted_live", "http_error_observed") == {"get_asset"}
    safe_output = run.model_dump_json()
    assert "asset-sensitive-valid" not in safe_output
    assert "asset-sensitive-missing" not in safe_output
    assert "response-body" not in safe_output
    assert "missing-body" not in safe_output


def test_action_without_manifest_approval_is_safety_blocked_with_zero_network_calls() -> None:
    manifest = _manifest(
        TransportProbeFixture(
            operation="update_asset_config",
            valid_arguments={
                "asset_id": "asset-action",
                "body": {"reason": "controlled campaign fixture only"},
            },
        )
    )
    transport = _FakeTransport()

    run, ledger = run_tractian_transport_campaign(
        manifest=manifest,
        transport=transport,
        allow_actions=True,
    )

    assert transport.requests == []
    assert run.executed_operations == 0
    assert run.safety_blocked_actions == 1
    assert run.results[0].valid_probe == "blocked_by_safety"
    assert run.results[0].action_live_execution_enabled is False
    assert ledger.unique_outcome_operations("hosted_live", "blocked_by_safety") == {
        "update_asset_config"
    }
    assert ledger.unique_success_operations("hosted_live") == set()


def test_action_manifest_approval_still_requires_invocation_level_allow_actions() -> None:
    manifest = _manifest(
        TransportProbeFixture(
            operation="update_asset_config",
            valid_arguments={
                "asset_id": "asset-action",
                "body": {"reason": "approved campaign fixture with explicit justification"},
            },
            action_execution_approved=True,
            action_approval_ref="approval-ticket-123",
        )
    )
    transport = _FakeTransport()

    run, ledger = run_tractian_transport_campaign(
        manifest=manifest,
        transport=transport,
        allow_actions=False,
    )

    assert transport.requests == []
    assert run.safety_blocked_actions == 1
    assert run.results[0].action_live_execution_enabled is False
    assert ledger.unique_outcome_operations("hosted_live", "blocked_by_safety") == {
        "update_asset_config"
    }


def test_action_reaches_transport_only_when_both_approval_gates_are_explicit() -> None:
    manifest = _manifest(
        TransportProbeFixture(
            operation="update_asset_config",
            valid_arguments={
                "asset_id": "asset-action-approved",
                "body": {"reason": "approved controlled live integration campaign"},
            },
            action_execution_approved=True,
            action_approval_ref="approval-ticket-456",
        )
    )
    transport = _FakeTransport(TransportResponse(202, {}, {"accepted": True}))

    run, ledger = run_tractian_transport_campaign(
        manifest=manifest,
        transport=transport,
        allow_actions=True,
    )

    assert len(transport.requests) == 1
    assert run.executed_operations == 1
    assert run.safety_blocked_actions == 0
    assert run.successful_valid_probes == 1
    assert run.results[0].action_live_execution_enabled is True
    assert ledger.unique_success_operations("hosted_live") == {"update_asset_config"}


def test_transport_failure_is_recorded_without_exposing_exception_text() -> None:
    manifest = _manifest(
        TransportProbeFixture(
            operation="get_asset",
            valid_arguments={"asset_id": "asset-failure"},
        )
    )
    transport = _FakeTransport(RuntimeError("SECRET-UPSTREAM-FAILURE"))

    run, ledger = run_tractian_transport_campaign(manifest=manifest, transport=transport)

    assert run.results[0].valid_probe == "transport_failure"
    assert "SECRET-UPSTREAM-FAILURE" not in run.model_dump_json()
    assert ledger.unique_outcome_operations("hosted_live", "transport_failure") == {"get_asset"}
