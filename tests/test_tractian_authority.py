from __future__ import annotations

from typing import Any

import pytest

from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.runtime import canonical_tool_registry
from academy_tractian.tractian_authority import (
    TenantGuardedTractianTransport,
    TractianAuthority,
    TractianAuthorityError,
)


class FakeUpstream:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []
        self.responses: dict[tuple[str, str], TransportResponse] = {}

    def add(self, method: str, path: str, body: Any, *, status: int = 200) -> None:
        self.responses[(method, path)] = TransportResponse(
            status_code=status,
            headers={"content-type": "application/json"},
            body=body,
        )

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return self.responses.get(
            (request.method, request.path),
            TransportResponse(
                status_code=404,
                headers={"content-type": "application/json"},
                body={"code": "NOT_FOUND"},
            ),
        )


def _user(*, user_id: str = "usr_a", company_id: str = "comp_a", permissions=None):
    return {
        "id": user_id,
        "name": "Operator",
        "role": "mechanic",
        "permissions": permissions if permissions is not None else ["read", "action_low"],
        "company_id": company_id,
    }


def _envelope(data: dict[str, Any]) -> dict[str, Any]:
    return {"mode": "complete", "notes": None, "data": data}


def _request(method: str, path: str, *, user_id: str = "usr_a") -> BoundRequest:
    return BoundRequest(
        method=method,
        path=path,
        query={},
        headers={"x-user-id": user_id},
        body=None,
    )


def test_current_user_permissions_are_derived_only_from_upstream_identity() -> None:
    upstream = FakeUpstream()
    upstream.add("GET", "/users/me", _user(permissions=["read", "action_high", "escalate"]))
    authority = TractianAuthority(transport=upstream)

    user = authority.current_user(user_id="usr_a")

    assert user.user_id == "usr_a"
    assert user.company_id == "comp_a"
    assert user.permissions == frozenset({Permission.READ, Permission.ACTION_HIGH, Permission.ESCALATE})
    assert upstream.calls[0].headers == {"x-user-id": "usr_a"}


def test_asset_action_principal_binds_exact_target_to_authoritative_company() -> None:
    upstream = FakeUpstream()
    upstream.add("GET", "/users/me", _user(permissions=["read", "action_high"]))
    upstream.add(
        "GET",
        "/assets/asset_a",
        _envelope({"id": "asset_a", "company_id": "comp_a", "name": "A"}),
    )
    authority = TractianAuthority(transport=upstream)
    tool = canonical_tool_registry()["update_asset_config"]

    principal = authority.action_principal(
        user_id="usr_a",
        tool=tool,
        arguments={"asset_id": "asset_a", "body": {"justification": "x" * 24}},
    )

    assert principal.user_company_id == "comp_a"
    assert principal.permissions == frozenset({Permission.READ, Permission.ACTION_HIGH})
    assert [(item.resource_id, item.company_id) for item in principal.resource_company_bindings] == [
        ("asset_a", "comp_a")
    ]


def test_analysis_action_principal_resolves_analysis_to_asset_to_company() -> None:
    upstream = FakeUpstream()
    upstream.add("GET", "/users/me", _user())
    upstream.add(
        "GET",
        "/analyses/an_a",
        _envelope({"id": "an_a", "asset_id": "asset_a", "status": "current"}),
    )
    upstream.add(
        "GET",
        "/assets/asset_a",
        _envelope({"id": "asset_a", "company_id": "comp_a"}),
    )
    authority = TractianAuthority(transport=upstream)

    principal = authority.action_principal(
        user_id="usr_a",
        tool=canonical_tool_registry()["reprocess_analysis"],
        arguments={"analysis_id": "an_a", "body": {"justification": "x" * 24}},
    )

    assert [(item.resource_id, item.company_id) for item in principal.resource_company_bindings] == [
        ("an_a", "comp_a")
    ]


def test_model_and_case_actions_remain_unqualified_without_public_company_binding() -> None:
    upstream = FakeUpstream()
    upstream.add(
        "GET",
        "/users/me",
        _user(permissions=["read", "action_high", "escalate"]),
    )
    authority = TractianAuthority(transport=upstream)

    model = authority.action_principal(
        user_id="usr_a",
        tool=canonical_tool_registry()["request_retraining"],
        arguments={"model_id": "mdl_1", "body": {"justification": "x" * 24}},
    )
    case = authority.action_principal(
        user_id="usr_a",
        tool=canonical_tool_registry()["escalate_case"],
        arguments={"case_id": "case_1", "body": {"justification": "x" * 24}},
    )

    assert model.resource_company_bindings == ()
    assert case.resource_company_bindings == ()


def test_cross_tenant_asset_is_denied_before_requested_resource_reaches_wrapped_transport() -> None:
    authority_upstream = FakeUpstream()
    authority_upstream.add("GET", "/users/me", _user())
    authority_upstream.add(
        "GET",
        "/assets/asset_foreign",
        _envelope({"id": "asset_foreign", "company_id": "comp_b", "secret": "never expose"}),
    )
    actual_upstream = FakeUpstream()
    actual_upstream.add(
        "GET",
        "/assets/asset_foreign",
        _envelope({"id": "asset_foreign", "company_id": "comp_b", "secret": "would leak"}),
    )
    guarded = TenantGuardedTractianTransport(
        authority=TractianAuthority(transport=authority_upstream),
        transport=actual_upstream,
    )

    response = guarded.request(_request("GET", "/assets/asset_foreign"))

    assert response.status_code == 403
    assert response.body["code"] == "TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED"
    assert "secret" not in str(response.body)
    assert actual_upstream.calls == []


def test_same_tenant_asset_read_is_forwarded_after_authority_check() -> None:
    authority_upstream = FakeUpstream()
    authority_upstream.add("GET", "/users/me", _user())
    authority_upstream.add(
        "GET",
        "/assets/asset_a",
        _envelope({"id": "asset_a", "company_id": "comp_a"}),
    )
    actual_upstream = FakeUpstream()
    actual_upstream.add("GET", "/assets/asset_a", _envelope({"id": "asset_a", "company_id": "comp_a"}))
    guarded = TenantGuardedTractianTransport(
        authority=TractianAuthority(transport=authority_upstream),
        transport=actual_upstream,
    )

    response = guarded.request(_request("GET", "/assets/asset_a"))

    assert response.status_code == 200
    assert len(actual_upstream.calls) == 1


def test_company_path_must_match_authoritative_user_company() -> None:
    upstream = FakeUpstream()
    upstream.add("GET", "/users/me", _user())
    authority = TractianAuthority(transport=upstream)

    with pytest.raises(TractianAuthorityError, match="TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED"):
        authority.authorize_bound_request(_request("GET", "/companies/comp_b/assets"))


def test_malformed_or_degraded_authority_response_fails_closed() -> None:
    upstream = FakeUpstream()
    upstream.add("GET", "/users/me", _user())
    upstream.add("GET", "/assets/asset_a", {"mode": "unavailable", "notes": "x", "data": {}})
    authority = TractianAuthority(transport=upstream)

    with pytest.raises(TractianAuthorityError, match="TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE"):
        authority.asset_company(user_id="usr_a", asset_id="asset_a")


def test_unknown_path_and_unqualified_mutations_fail_closed() -> None:
    upstream = FakeUpstream()
    upstream.add("GET", "/users/me", _user())
    authority = TractianAuthority(transport=upstream)

    for request in (
        _request("GET", "/unknown/resource"),
        _request("POST", "/models/mdl_1/request-retraining"),
        _request("POST", "/cases/case_1/escalate"),
    ):
        with pytest.raises(TractianAuthorityError):
            authority.authorize_bound_request(request)
