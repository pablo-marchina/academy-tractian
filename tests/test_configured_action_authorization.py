from __future__ import annotations

import json

import pytest

from research.e2.models import Permission

from academy_tractian.trusted_action_authorization import (
    ActionAuthorizationResolutionError,
    ConfiguredServerOwnedActionAuthorizationSource,
)


def _grant(*, user_id: str = "user-1", organization_id: str = "org-1", active: bool = True) -> dict[str, object]:
    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "user_company_id": "company-1",
        "permissions": ["action_low", "action_high", "escalate"],
        "resource_company_bindings": [
            {"resource_id": "asset-1", "company_id": "company-1"},
            {"resource_id": "analysis-1", "company_id": "company-1"},
            {"resource_id": "analysis-2", "company_id": "company-1"},
            {"resource_id": "model-1", "company_id": "company-1"},
            {"resource_id": "case-1", "company_id": "company-1"},
        ],
        "policy_revision": "governed-execute-v1",
        "active": active,
        "source_owned": True,
    }


def test_configured_source_resolves_all_canonical_action_permissions_without_exposing_grant_material() -> None:
    source = ConfiguredServerOwnedActionAuthorizationSource.from_json(json.dumps([_grant()]))

    principal = source.resolve_user(user_id="user-1")
    tenant_principal = source.authorize_context(
        organization_id="org-1",
        user_id="user-1",
    )

    assert principal == tenant_principal
    assert source(user_id="user-1") == principal
    assert principal.permissions == frozenset(
        {Permission.ACTION_LOW, Permission.ACTION_HIGH, Permission.ESCALATE}
    )
    assert {binding.resource_id for binding in principal.resource_company_bindings} == {
        "asset-1",
        "analysis-1",
        "analysis-2",
        "model-1",
        "case-1",
    }
    assert source.lookup(organization_id="org-1", user_id="user-1")
    assert source.lookup(organization_id="org-2", user_id="user-1") == ()
    assert source.safe_summary() == {"configured_grants": 1, "active_grants": 1}
    assert "user-1" not in repr(source.safe_summary())
    assert "asset-1" not in repr(source.safe_summary())


def test_context_authorization_denies_same_user_under_wrong_organization() -> None:
    source = ConfiguredServerOwnedActionAuthorizationSource.from_json(json.dumps([_grant()]))

    with pytest.raises(ActionAuthorizationResolutionError, match="GRANT_NOT_FOUND"):
        source.authorize_context(organization_id="org-2", user_id="user-1")


def test_configured_source_rejects_ambiguous_user_identity_across_organizations() -> None:
    with pytest.raises(ValueError, match="globally unique user ids"):
        ConfiguredServerOwnedActionAuthorizationSource.from_json(
            json.dumps(
                [
                    _grant(organization_id="org-1"),
                    _grant(organization_id="org-2"),
                ]
            )
        )


def test_configured_source_rejects_cross_company_resource_binding() -> None:
    grant = _grant()
    grant["resource_company_bindings"] = [
        {"resource_id": "asset-1", "company_id": "company-2"}
    ]
    with pytest.raises(ValueError, match="trusted grant schema"):
        ConfiguredServerOwnedActionAuthorizationSource.from_json(json.dumps([grant]))


def test_inactive_or_unknown_configured_grant_fails_closed() -> None:
    source = ConfiguredServerOwnedActionAuthorizationSource.from_json(
        json.dumps([_grant(active=False)])
    )
    with pytest.raises(ActionAuthorizationResolutionError, match="GRANT_INACTIVE"):
        source.resolve_user(user_id="user-1")
    with pytest.raises(ActionAuthorizationResolutionError, match="GRANT_INACTIVE"):
        source.authorize_context(organization_id="org-1", user_id="user-1")
    with pytest.raises(ActionAuthorizationResolutionError, match="GRANT_NOT_FOUND"):
        source.resolve_user(user_id="unknown-user")


@pytest.mark.parametrize("raw", ["not-json", "{}", "[]"])
def test_configured_source_rejects_invalid_or_empty_grant_documents(raw: str) -> None:
    with pytest.raises(ValueError):
        ConfiguredServerOwnedActionAuthorizationSource.from_json(raw)
