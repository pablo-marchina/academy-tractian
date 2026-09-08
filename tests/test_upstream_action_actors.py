from __future__ import annotations

import json

import pytest

from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.production_actions_v2 import ProductionActionPrincipal
from academy_tractian.upstream_action_actors import (
    ConfiguredServerOwnedUpstreamActionActorSource,
    ServerOwnedUpstreamActionActorTransport,
)
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse


LOCAL_USER = "local-user-1"
COMPANY = "comp_papel_sul"


def _actor_json() -> str:
    return json.dumps(
        [
            {
                "schema_version": "tractian-upstream-action-actor-v1",
                "company_id": COMPANY,
                "permission": "action_low",
                "upstream_user_id": "usr_marta",
                "active": True,
                "source_owned": True,
            },
            {
                "schema_version": "tractian-upstream-action-actor-v1",
                "company_id": COMPANY,
                "permission": "action_high",
                "upstream_user_id": "usr_helena",
                "active": True,
                "source_owned": True,
            },
            {
                "schema_version": "tractian-upstream-action-actor-v1",
                "company_id": COMPANY,
                "permission": "escalate",
                "upstream_user_id": "usr_helena",
                "active": True,
                "source_owned": True,
            },
        ]
    )


def _principal(*permissions: Permission) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=LOCAL_USER,
        user_company_id=COMPANY,
        permissions=frozenset(permissions),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="resource-1", company_id=COMPANY),
        ),
    )


class RecordingTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(202, {"content-type": "application/json"}, {"accepted": True})


def _request(method: str, path: str) -> BoundRequest:
    return BoundRequest(
        method=method,
        path=path,
        query={},
        headers={"x-user-id": LOCAL_USER},
        body={"justification": "Operator approved this exact governed action for production validation."},
    )


@pytest.mark.parametrize(
    ("method", "path", "permission", "expected_upstream_user"),
    [
        ("POST", "/analyses/analysis-1/reprocess", Permission.ACTION_LOW, "usr_marta"),
        (
            "POST",
            "/analyses/analysis-1/request-specialist",
            Permission.ACTION_LOW,
            "usr_marta",
        ),
        ("PATCH", "/assets/asset-1", Permission.ACTION_HIGH, "usr_helena"),
        (
            "POST",
            "/models/model-1/request-retraining",
            Permission.ACTION_HIGH,
            "usr_helena",
        ),
        ("POST", "/cases/case-1/escalate", Permission.ESCALATE, "usr_helena"),
    ],
)
def test_each_canonical_action_is_routed_by_server_owned_permission_binding(
    method: str,
    path: str,
    permission: Permission,
    expected_upstream_user: str,
) -> None:
    actor_source = ConfiguredServerOwnedUpstreamActionActorSource.from_json(_actor_json())
    principal = _principal(Permission.ACTION_LOW, Permission.ACTION_HIGH, Permission.ESCALATE)
    resolved_users: list[str] = []

    def resolver(*, user_id: str) -> ProductionActionPrincipal:
        resolved_users.append(user_id)
        return principal

    inner = RecordingTransport()
    transport = ServerOwnedUpstreamActionActorTransport(
        transport=inner,
        authorization_resolver=resolver,
        actor_source=actor_source,
    )
    original = _request(method, path)

    response = transport.request(original)

    assert response.status_code == 202
    assert response.body == {"accepted": True}
    assert resolved_users == [LOCAL_USER]
    assert original.headers == {"x-user-id": LOCAL_USER}
    assert len(inner.calls) == 1
    assert inner.calls[0].headers == {"x-user-id": expected_upstream_user}
    assert permission in principal.permissions


def test_read_request_preserves_local_identity_and_never_resolves_privileged_actor() -> None:
    actor_source = ConfiguredServerOwnedUpstreamActionActorSource.from_json(_actor_json())

    def forbidden_resolver(*, user_id: str) -> ProductionActionPrincipal:
        raise AssertionError(f"read request must not resolve action actor for {user_id}")

    inner = RecordingTransport()
    transport = ServerOwnedUpstreamActionActorTransport(
        transport=inner,
        authorization_resolver=forbidden_resolver,
        actor_source=actor_source,
    )
    request = BoundRequest(
        method="GET",
        path="/assets/asset-1",
        query={},
        headers={"x-user-id": LOCAL_USER},
        body=None,
    )

    transport.request(request)

    assert inner.calls == [request]
    assert inner.calls[0].headers == {"x-user-id": LOCAL_USER}


def test_missing_local_permission_fails_before_upstream_transport() -> None:
    actor_source = ConfiguredServerOwnedUpstreamActionActorSource.from_json(_actor_json())
    inner = RecordingTransport()
    transport = ServerOwnedUpstreamActionActorTransport(
        transport=inner,
        authorization_resolver=lambda *, user_id: _principal(Permission.ACTION_LOW),
        actor_source=actor_source,
    )

    with pytest.raises(PermissionError, match="local_action_permission_missing"):
        transport.request(_request("PATCH", "/assets/asset-1"))

    assert inner.calls == []


def test_missing_upstream_binding_fails_before_network() -> None:
    actor_source = ConfiguredServerOwnedUpstreamActionActorSource.from_json(
        json.dumps(
            [
                {
                    "schema_version": "tractian-upstream-action-actor-v1",
                    "company_id": COMPANY,
                    "permission": "action_low",
                    "upstream_user_id": "usr_marta",
                    "active": True,
                    "source_owned": True,
                }
            ]
        )
    )
    principal = _principal(Permission.ACTION_LOW, Permission.ACTION_HIGH)
    inner = RecordingTransport()
    transport = ServerOwnedUpstreamActionActorTransport(
        transport=inner,
        authorization_resolver=lambda *, user_id: principal,
        actor_source=actor_source,
    )

    with pytest.raises(PermissionError, match="upstream_action_actor_binding_missing"):
        transport.request(_request("PATCH", "/assets/asset-1"))

    assert inner.calls == []
    with pytest.raises(PermissionError, match="upstream_action_actor_binding_missing"):
        actor_source.assert_complete_for_principal(principal)


def test_actor_document_rejects_read_permission_and_non_server_owned_binding() -> None:
    bad_read = json.dumps(
        [
            {
                "schema_version": "tractian-upstream-action-actor-v1",
                "company_id": COMPANY,
                "permission": "read",
                "upstream_user_id": "usr_marta",
                "active": True,
                "source_owned": True,
            }
        ]
    )
    with pytest.raises(ValueError, match="invalid upstream action actor grant"):
        ConfiguredServerOwnedUpstreamActionActorSource.from_json(bad_read)

    bad_owner = json.dumps(
        [
            {
                "schema_version": "tractian-upstream-action-actor-v1",
                "company_id": COMPANY,
                "permission": "action_low",
                "upstream_user_id": "usr_marta",
                "active": True,
                "source_owned": False,
            }
        ]
    )
    with pytest.raises(ValueError, match="invalid upstream action actor grant"):
        ConfiguredServerOwnedUpstreamActionActorSource.from_json(bad_owner)
