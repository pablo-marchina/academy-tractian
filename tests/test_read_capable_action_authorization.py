from __future__ import annotations

import json

import pytest

from research.e2.controller import ControllerContext, ControllerDecision, ControllerDecisionKind, DecisionSource
from research.e2.models import BoundRequest, Permission
from research.e2.transport import RequestTransport, TransportResponse

from academy_tractian.production_actions_v2 import (
    ActionProposalRealtimeProductionRuntime,
    PendingActionCustody,
)
from academy_tractian.read_capable_action_authorization import (
    ReadCapableConfiguredActionAuthorizationResolver,
)
from academy_tractian.runtime import ProductionRequest
from academy_tractian.trusted_action_authorization import (
    ActionAuthorizationResolutionError,
    ConfiguredServerOwnedActionAuthorizationSource,
)


class _NeverCalledSource(DecisionSource):
    def decide(self, _context: ControllerContext) -> ControllerDecision:
        return ControllerDecision(
            kind=ControllerDecisionKind.ABSTAIN,
            reason_code="TEST_ONLY",
            message="test",
        )


class _NoIoTransport(RequestTransport):
    def request(self, _request: BoundRequest) -> TransportResponse:
        raise AssertionError("prepare must not perform transport I/O")


class _Sink:
    def publish(self, _event) -> None:
        return None


def _source() -> ConfiguredServerOwnedActionAuthorizationSource:
    return ConfiguredServerOwnedActionAuthorizationSource.from_json(
        json.dumps(
            [
                {
                    "schema_version": "trusted-action-authorization-grant-v1",
                    "user_id": "action-user",
                    "organization_id": "org-1",
                    "user_company_id": "company-1",
                    "permissions": [Permission.ACTION_LOW.value],
                    "resource_company_bindings": [],
                    "policy_revision": "test-v1",
                    "active": True,
                    "source_owned": True,
                }
            ]
        )
    )


def test_missing_action_grant_gets_zero_action_proposal_principal() -> None:
    resolver = ReadCapableConfiguredActionAuthorizationResolver(_source())

    principal = resolver(user_id="ordinary-read-user")

    assert principal.user_id == "ordinary-read-user"
    assert principal.permissions == frozenset()
    assert principal.resource_company_bindings == ()
    assert principal.user_company_id == "__no_action_grant__"


def test_strict_confirmation_still_rejects_missing_grant() -> None:
    resolver = ReadCapableConfiguredActionAuthorizationResolver(_source())

    with pytest.raises(ActionAuthorizationResolutionError, match="GRANT_NOT_FOUND"):
        resolver.authorize_context(
            organization_id="org-1",
            user_id="ordinary-read-user",
        )


def test_existing_action_grant_is_preserved() -> None:
    resolver = ReadCapableConfiguredActionAuthorizationResolver(_source())

    principal = resolver(user_id="action-user")

    assert principal.user_id == "action-user"
    assert principal.user_company_id == "company-1"
    assert principal.permissions == frozenset({Permission.ACTION_LOW})


def test_action_enabled_runtime_can_prepare_read_run_for_ungranted_user(tmp_path) -> None:
    resolver = ReadCapableConfiguredActionAuthorizationResolver(_source())
    runtime = ActionProposalRealtimeProductionRuntime(
        decision_source=_NeverCalledSource(),
        transport=_NoIoTransport(),
        observability_sink=_Sink(),
        authorization_resolver=resolver,
        custody=PendingActionCustody(tmp_path / "custody.duckdb"),
    )

    prepared = runtime.prepare(
        ProductionRequest(
            request_id="ordinary-read-request",
            identity_id="identity-ordinary-read-user",
            user_id="ordinary-read-user",
            user_request="Inspect the current condition of asset R310.",
        )
    )

    assert prepared is not None
