from __future__ import annotations

from typing import Any

from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.hosted_action_authorization import HostedTractianAuthority
from academy_tractian.tractian_authority import TenantGuardedTractianTransport


class SequencedTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []
        self.responses: dict[tuple[str, str], list[TransportResponse | Exception]] = {}

    def add(self, method: str, path: str, *responses: TransportResponse | Exception) -> None:
        self.responses[(method, path)] = list(responses)

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        queued = self.responses.get((request.method, request.path), [])
        if not queued:
            return TransportResponse(404, {"content-type": "application/json"}, {"code": "NOT_FOUND"})
        response = queued.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _ok(body: Any) -> TransportResponse:
    return TransportResponse(200, {"content-type": "application/json"}, body)


def _user(*, permissions: list[str], company_id: str = "comp_a") -> dict[str, Any]:
    return {
        "id": "usr_a",
        "name": "Operator",
        "role": "maintenance_manager",
        "permissions": permissions,
        "company_id": company_id,
    }


def _asset(*, company_id: str = "comp_a") -> dict[str, Any]:
    return {
        "mode": "complete",
        "notes": None,
        "data": {"id": "asset_a", "company_id": company_id},
    }


def _action_request(method: str = "PATCH", path: str = "/assets/asset_a") -> BoundRequest:
    return BoundRequest(
        method=method,
        path=path,
        query={},
        headers={"x-user-id": "usr_a"},
        body={"justification": "Authorized configuration change with evidence"},
    )


def test_permission_revoked_after_scope_check_never_reaches_raw_action_transport() -> None:
    authority_transport = SequencedTransport()
    authority_transport.add(
        "GET",
        "/users/me",
        _ok(_user(permissions=["read", "action_high"])),
        _ok(_user(permissions=["read"])),
    )
    authority_transport.add("GET", "/assets/asset_a", _ok(_asset()))
    raw = SequencedTransport()
    raw.add("PATCH", "/assets/asset_a", _ok({"accepted": True}))
    guarded = TenantGuardedTractianTransport(
        authority=HostedTractianAuthority(transport=authority_transport),
        transport=raw,
    )

    response = guarded.request(_action_request())

    assert response.status_code == 503
    assert response.body["code"] == "TRACTIAN_AUTHORITY_PERMISSION_DENIED"
    assert raw.calls == []


def test_company_change_during_last_mile_revalidation_never_reaches_raw_transport() -> None:
    authority_transport = SequencedTransport()
    authority_transport.add(
        "GET",
        "/users/me",
        _ok(_user(permissions=["read", "action_high"], company_id="comp_a")),
        _ok(_user(permissions=["read", "action_high"], company_id="comp_b")),
    )
    authority_transport.add("GET", "/assets/asset_a", _ok(_asset(company_id="comp_a")))
    raw = SequencedTransport()
    raw.add("PATCH", "/assets/asset_a", _ok({"accepted": True}))
    guarded = TenantGuardedTractianTransport(
        authority=HostedTractianAuthority(transport=authority_transport),
        transport=raw,
    )

    response = guarded.request(_action_request())

    assert response.status_code == 403
    assert response.body["code"] == "TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED"
    assert raw.calls == []


def test_unregistered_mutation_shape_is_rejected_without_any_raw_call() -> None:
    authority_transport = SequencedTransport()
    raw = SequencedTransport()
    guarded = TenantGuardedTractianTransport(
        authority=HostedTractianAuthority(transport=authority_transport),
        transport=raw,
    )

    response = guarded.request(_action_request(method="DELETE"))

    assert response.status_code == 503
    assert response.body["code"] == "TRACTIAN_AUTHORITY_PATH_NOT_QUALIFIED"
    assert authority_transport.calls == []
    assert raw.calls == []


def test_authority_network_failure_is_deterministic_and_never_calls_raw_transport() -> None:
    authority_transport = SequencedTransport()
    authority_transport.add("GET", "/users/me", RuntimeError("network down"))
    raw = SequencedTransport()
    raw.add("PATCH", "/assets/asset_a", _ok({"accepted": True}))
    guarded = TenantGuardedTractianTransport(
        authority=HostedTractianAuthority(transport=authority_transport),
        transport=raw,
    )

    response = guarded.request(_action_request())

    assert response.status_code == 503
    assert response.body["code"] == "TRACTIAN_AUTHORITY_UPSTREAM_UNAVAILABLE"
    assert raw.calls == []


def test_authorized_asset_action_reaches_raw_transport_exactly_once() -> None:
    authority_transport = SequencedTransport()
    authority_transport.add(
        "GET",
        "/users/me",
        _ok(_user(permissions=["read", "action_high"])),
        _ok(_user(permissions=["read", "action_high"])),
    )
    authority_transport.add("GET", "/assets/asset_a", _ok(_asset()))
    raw = SequencedTransport()
    raw.add("PATCH", "/assets/asset_a", _ok({"accepted": True, "action_id": "upstream-action"}))
    guarded = TenantGuardedTractianTransport(
        authority=HostedTractianAuthority(transport=authority_transport),
        transport=raw,
    )

    response = guarded.request(_action_request())

    assert response.status_code == 200
    assert response.body["accepted"] is True
    assert len(raw.calls) == 1
    assert raw.calls[0].headers == {"x-user-id": "usr_a"}


def test_unqualified_model_and_case_actions_remain_fail_closed_even_with_permissions() -> None:
    for request in (
        _action_request(method="POST", path="/models/mdl_vib_v3/request-retraining"),
        _action_request(method="POST", path="/cases/case_1/escalate"),
    ):
        authority_transport = SequencedTransport()
        authority_transport.add(
            "GET",
            "/users/me",
            _ok(_user(permissions=["read", "action_high", "escalate"])),
        )
        raw = SequencedTransport()
        guarded = TenantGuardedTractianTransport(
            authority=HostedTractianAuthority(transport=authority_transport),
            transport=raw,
        )

        response = guarded.request(request)

        assert response.status_code == 503
        assert response.body["code"] == "TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE"
        assert raw.calls == []
