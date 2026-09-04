from __future__ import annotations

from research.e2.controller import ControllerContext, ControllerDecisionKind, ControllerObservation
from research.e2.models import BoundRequest

from academy_tractian.provider_free_product import (
    ProviderFreeScenarioDecisionSource,
    ProviderFreeTransport,
)
from academy_tractian.provider_free_semantic_review import (
    provider_free_semantic_review_enabled,
    provider_free_semantic_review_permissions,
)
from academy_tractian.semantic_review_collection import SEMANTIC_REVIEW_PERMISSION


def _context(user_request: str) -> ControllerContext:
    return ControllerContext(
        user_request=user_request,
        turn_index=0,
        tool_call_count=0,
    )


def test_provider_free_investigation_uses_canonical_read_tool_then_finishes() -> None:
    source = ProviderFreeScenarioDecisionSource()
    first = source.decide(_context("scenario:investigate asset-e2e"))
    assert first.kind is ControllerDecisionKind.TOOL
    assert first.proposal is not None
    assert first.proposal.tool_name == "get_asset"
    assert first.proposal.arguments == {"asset_id": "asset-e2e"}

    second = source.decide(
        ControllerContext(
            user_request="scenario:investigate asset-e2e",
            turn_index=1,
            tool_call_count=1,
            observations=(
                ControllerObservation(
                    tool_name="get_asset",
                    status="success",
                    executed=True,
                    status_code=200,
                    body={"assetId": "asset-e2e"},
                ),
            ),
        )
    )
    assert second.kind is ControllerDecisionKind.FINAL
    assert second.final is not None
    assert second.final["reason_code"] == "E2E_EVIDENCE_CONFIRMED"


def test_provider_free_terminal_and_action_scenarios_are_explicit() -> None:
    source = ProviderFreeScenarioDecisionSource()
    assert source.decide(_context("scenario:clarify")).kind is ControllerDecisionKind.CLARIFY
    assert source.decide(_context("scenario:escalate")).kind is ControllerDecisionKind.ESCALATE
    assert source.decide(_context("scenario:abstain")).kind is ControllerDecisionKind.ABSTAIN

    pending = source.decide(_context("scenario:pending-action"))
    assert pending.kind is ControllerDecisionKind.TOOL
    assert pending.proposal is not None
    assert pending.proposal.tool_name == "reprocess_analysis"

    blocked = source.decide(_context("scenario:blocked-action"))
    assert blocked.kind is ControllerDecisionKind.TOOL
    assert blocked.proposal is not None
    assert blocked.proposal.tool_name == "update_asset_config"


def test_provider_free_transport_has_bounded_routes_and_failure_case() -> None:
    transport = ProviderFreeTransport()
    headers = {"x-user-id": "user", "x-identity-id": "identity"}

    success = transport.request(
        BoundRequest(method="GET", path="/assets/asset-e2e", query={}, headers=headers)
    )
    assert success.status_code == 200
    assert success.body["source"] == "provider-free-acceptance-profile"

    failure = transport.request(
        BoundRequest(method="GET", path="/assets/asset-error", query={}, headers=headers)
    )
    assert failure.status_code == 503

    slow = transport.request(
        BoundRequest(method="GET", path="/assets/asset-slow", query={}, headers=headers)
    )
    assert slow.status_code == 200
    assert slow.body["assetId"] == "asset-slow"

    unknown = transport.request(
        BoundRequest(method="GET", path="/unconfigured", query={}, headers=headers)
    )
    assert unknown.status_code == 404


def test_semantic_review_acceptance_permission_is_explicitly_fixture_gated(monkeypatch) -> None:
    monkeypatch.delenv("ACADEMY_E2E_SEMANTIC_REVIEW", raising=False)
    assert provider_free_semantic_review_enabled() is False
    assert provider_free_semantic_review_permissions() == frozenset()

    monkeypatch.setenv("ACADEMY_E2E_SEMANTIC_REVIEW", "1")
    assert provider_free_semantic_review_enabled() is True
    assert provider_free_semantic_review_permissions() == frozenset({SEMANTIC_REVIEW_PERMISSION})

    monkeypatch.setenv("ACADEMY_E2E_SEMANTIC_REVIEW", "0")
    assert provider_free_semantic_review_enabled() is False
    assert provider_free_semantic_review_permissions() == frozenset()