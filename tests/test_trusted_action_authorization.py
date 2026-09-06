from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.trusted_action_authorization import (
    ActionAuthorizationResolutionError,
    OrganizationBoundActionAuthorizationResolver,
    ServerOwnedActionAuthorizationGrant,
    TrustedActionAuthorizationResolverFactory,
)
from research.e2.models import Permission


class RecordingSource:
    def __init__(self, rows=None, *, explode: bool = False, invalid_contract: bool = False) -> None:
        self.rows = dict(rows or {})
        self.explode = explode
        self.invalid_contract = invalid_contract
        self.calls: list[tuple[str, str]] = []

    def lookup(self, *, organization_id: str, user_id: str):
        self.calls.append((organization_id, user_id))
        if self.explode:
            raise RuntimeError("server-owned-source-secret-marker")
        if self.invalid_contract:
            return []
        return self.rows.get((organization_id, user_id), ())


def _context(
    *,
    organization_id: str = "org-a",
    user_id: str = "user-1",
    permissions: frozenset[str] | None = None,
) -> AuthenticatedRuntimeContext:
    return AuthenticatedRuntimeContext(
        organization_id=organization_id,
        identity_id=f"identity:{organization_id}:{user_id}",
        user_id=user_id,
        role="operator",
        permissions=(
            frozenset({"runs:create", "actions:confirm:self"})
            if permissions is None
            else permissions
        ),
    )


def _grant(
    *,
    organization_id: str = "org-a",
    user_id: str = "user-1",
    company_id: str = "company-a",
    permissions: frozenset[Permission] = frozenset({Permission.ACTION_LOW}),
    active: bool = True,
    resources: tuple[ResourceCompanyBinding, ...] | None = None,
) -> ServerOwnedActionAuthorizationGrant:
    return ServerOwnedActionAuthorizationGrant(
        organization_id=organization_id,
        user_id=user_id,
        user_company_id=company_id,
        permissions=permissions,
        resource_company_bindings=(
            (ResourceCompanyBinding(resource_id="analysis-1", company_id=company_id),)
            if resources is None
            else resources
        ),
        policy_revision="policy-rev-1",
        active=active,
    )


def test_exact_server_owned_grant_builds_canonical_action_principal() -> None:
    grant = _grant(
        permissions=frozenset({Permission.ACTION_LOW, Permission.ESCALATE})
    )
    source = RecordingSource({("org-a", "user-1"): (grant,)})
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=source,
    )

    principal = resolver(user_id="user-1")

    assert source.calls == [("org-a", "user-1")]
    assert principal.user_id == "user-1"
    assert principal.user_company_id == "company-a"
    assert principal.permissions == frozenset(
        {Permission.ACTION_LOW, Permission.ESCALATE}
    )
    assert principal.resource_company_bindings == grant.resource_company_bindings


def test_browser_or_api_capability_strings_never_become_canonical_tool_permissions() -> None:
    context = _context(
        permissions=frozenset(
            {
                "runs:create",
                "actions:confirm:self",
                "action_high",
                "escalate",
            }
        )
    )
    grant = _grant(permissions=frozenset())
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=context,
        source=RecordingSource({("org-a", "user-1"): (grant,)}),
    )

    principal = resolver(user_id="user-1")

    assert principal.permissions == frozenset()


def test_bound_user_mismatch_denies_before_source_lookup() -> None:
    source = RecordingSource({("org-a", "user-1"): (_grant(),)})
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=source,
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-2")

    assert exc_info.value.code == "BOUND_USER_MISMATCH"
    assert source.calls == []


def test_missing_grant_fails_closed() -> None:
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=RecordingSource(),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "GRANT_NOT_FOUND"


def test_duplicate_grants_are_ambiguous_and_fail_closed() -> None:
    grant = _grant()
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=RecordingSource({("org-a", "user-1"): (grant, grant)}),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "GRANT_AMBIGUOUS"


def test_source_failure_is_sanitized_and_fails_closed() -> None:
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=RecordingSource(explode=True),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "SOURCE_UNAVAILABLE"
    assert "server-owned-source-secret-marker" not in str(exc_info.value)


def test_source_must_return_tuple_to_keep_ambiguity_observable() -> None:
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=RecordingSource(invalid_contract=True),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "SOURCE_CONTRACT_INVALID"


def test_grant_user_mismatch_fails_closed() -> None:
    wrong = _grant(user_id="user-2")
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=RecordingSource({("org-a", "user-1"): (wrong,)}),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "GRANT_USER_MISMATCH"


def test_grant_organization_mismatch_fails_closed() -> None:
    wrong = _grant(organization_id="org-b")
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(organization_id="org-a"),
        source=RecordingSource({("org-a", "user-1"): (wrong,)}),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "GRANT_ORGANIZATION_MISMATCH"


def test_inactive_grant_fails_closed() -> None:
    resolver = OrganizationBoundActionAuthorizationResolver(
        context=_context(),
        source=RecordingSource({("org-a", "user-1"): (_grant(active=False),)}),
    )

    with pytest.raises(ActionAuthorizationResolutionError) as exc_info:
        resolver(user_id="user-1")

    assert exc_info.value.code == "GRANT_INACTIVE"


def test_cross_company_resource_binding_is_rejected_at_grant_boundary() -> None:
    with pytest.raises(ValidationError):
        _grant(
            company_id="company-a",
            resources=(
                ResourceCompanyBinding(
                    resource_id="analysis-cross-company",
                    company_id="company-b",
                ),
            ),
        )


def test_factory_binds_same_user_to_distinct_organizations_without_state_bleed() -> None:
    grant_a = _grant(
        organization_id="org-a",
        company_id="company-a",
        permissions=frozenset({Permission.ACTION_LOW}),
        resources=(
            ResourceCompanyBinding(resource_id="analysis-a", company_id="company-a"),
        ),
    )
    grant_b = _grant(
        organization_id="org-b",
        company_id="company-b",
        permissions=frozenset({Permission.ACTION_HIGH}),
        resources=(
            ResourceCompanyBinding(resource_id="analysis-b", company_id="company-b"),
        ),
    )
    source = RecordingSource(
        {
            ("org-a", "user-1"): (grant_a,),
            ("org-b", "user-1"): (grant_b,),
        }
    )
    factory = TrustedActionAuthorizationResolverFactory(source=source)

    resolver_a = factory.bind(context=_context(organization_id="org-a"))
    resolver_b = factory.bind(context=_context(organization_id="org-b"))
    principal_a = resolver_a(user_id="user-1")
    principal_b = resolver_b(user_id="user-1")

    assert resolver_a.organization_id == "org-a"
    assert resolver_b.organization_id == "org-b"
    assert principal_a.user_company_id == "company-a"
    assert principal_b.user_company_id == "company-b"
    assert principal_a.permissions == frozenset({Permission.ACTION_LOW})
    assert principal_b.permissions == frozenset({Permission.ACTION_HIGH})
    assert principal_a.resource_company_bindings[0].resource_id == "analysis-a"
    assert principal_b.resource_company_bindings[0].resource_id == "analysis-b"
    assert source.calls == [("org-a", "user-1"), ("org-b", "user-1")]


def test_grant_is_extra_forbid_and_cannot_accept_browser_owned_fields() -> None:
    payload = _grant().model_dump(mode="python")
    payload["actions_enabled"] = True

    with pytest.raises(ValidationError):
        ServerOwnedActionAuthorizationGrant.model_validate(payload)
