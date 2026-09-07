from __future__ import annotations

from collections.abc import Callable, Mapping
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from research.e2.models import BoundRequest, Permission, ToolKind
from research.e2.transport import RequestTransport, TransportResponse

from .production_actions_v2 import ProductionActionPrincipal
from .tractian_transport import _match_canonical_tool


_ACTION_PERMISSIONS = frozenset(
    {Permission.ACTION_LOW, Permission.ACTION_HIGH, Permission.ESCALATE}
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class UpstreamActionActorGrant(_FrozenModel):
    schema_version: str = Field(pattern=r"^tractian-upstream-action-actor-v1$")
    company_id: str = Field(min_length=1, max_length=256)
    permission: Permission
    upstream_user_id: str = Field(min_length=1, max_length=256)
    active: bool = True
    source_owned: bool = True

    @field_validator("permission")
    @classmethod
    def action_permission_only(cls, value: Permission) -> Permission:
        if value not in _ACTION_PERMISSIONS:
            raise ValueError("upstream action actor grants may bind only action permissions")
        return value


class ConfiguredServerOwnedUpstreamActionActorSource:
    """Server-custodied mapping from a locally authorized company/permission to TRACTIAN actor.

    The browser, model, pending-action payload and confirmation request never provide the
    upstream actor. Local product authorization remains authoritative; this source only selects
    the provider-side actor required by the supplied TRACTIAN contract after local authorization.
    """

    def __init__(self, grants: tuple[UpstreamActionActorGrant, ...]) -> None:
        if not grants:
            raise ValueError("at least one upstream action actor grant is required")
        bindings: dict[tuple[str, Permission], str] = {}
        for grant in grants:
            if not grant.active:
                continue
            if not grant.source_owned:
                raise ValueError("upstream action actor grants must be server-owned")
            key = (grant.company_id, grant.permission)
            if key in bindings:
                raise ValueError("duplicate upstream action actor binding")
            bindings[key] = grant.upstream_user_id
        if not bindings:
            raise ValueError("at least one active upstream action actor grant is required")
        self._bindings = bindings

    @classmethod
    def from_json(cls, raw: str) -> "ConfiguredServerOwnedUpstreamActionActorSource":
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("upstream action actor grants must be valid JSON") from exc
        if not isinstance(decoded, list) or not decoded:
            raise ValueError("upstream action actor grants must be a non-empty JSON list")
        try:
            grants = tuple(UpstreamActionActorGrant.model_validate(item) for item in decoded)
        except ValidationError as exc:
            raise ValueError("invalid upstream action actor grant") from exc
        return cls(grants)

    def resolve(self, *, company_id: str, permission: Permission) -> str:
        try:
            return self._bindings[(company_id, permission)]
        except KeyError as exc:
            raise PermissionError("upstream_action_actor_binding_missing") from exc

    def assert_complete_for_principal(self, principal: ProductionActionPrincipal) -> None:
        for permission in principal.permissions:
            if permission in _ACTION_PERMISSIONS:
                self.resolve(company_id=principal.user_company_id, permission=permission)

    def safe_summary(self) -> dict[str, int]:
        return {
            "configured_bindings": len(self._bindings),
            "configured_companies": len({company for company, _ in self._bindings}),
        }


class ServerOwnedUpstreamActionActorTransport(RequestTransport):
    """Rewrite only the provider-side action identity after local authorization.

    The wrapped runner keeps the authenticated local user in its ExecutionBinding, preserving
    requester ownership and observability. For ACTION calls only, this adapter re-resolves the
    local principal from the server-owned authorization source, verifies the canonical required
    permission, then replaces the network x-user-id with the matching provider-side actor.
    READ calls are passed through unchanged.
    """

    def __init__(
        self,
        *,
        transport: RequestTransport,
        authorization_resolver: Callable[..., ProductionActionPrincipal],
        actor_source: ConfiguredServerOwnedUpstreamActionActorSource,
    ) -> None:
        self._transport = transport
        self._authorization_resolver = authorization_resolver
        self._actor_source = actor_source

    def request(self, request: BoundRequest) -> TransportResponse:
        tool = _match_canonical_tool(request)
        if tool.kind is not ToolKind.ACTION:
            return self._transport.request(request)

        local_user_id = request.headers.get("x-user-id", "").strip()
        if not local_user_id:
            raise PermissionError("local_action_requester_identity_missing")
        principal = self._authorization_resolver(user_id=local_user_id)
        if principal.user_id != local_user_id:
            raise PermissionError("action_principal_user_mismatch")

        required = tuple(tool.required_permissions)
        if len(required) != 1 or required[0] not in _ACTION_PERMISSIONS:
            raise PermissionError("canonical_action_permission_contract_invalid")
        permission = required[0]
        if permission not in principal.permissions:
            raise PermissionError("local_action_permission_missing")

        upstream_user_id = self._actor_source.resolve(
            company_id=principal.user_company_id,
            permission=permission,
        )
        routed_headers: dict[str, str] = dict(request.headers)
        routed_headers["x-user-id"] = upstream_user_id
        routed = request.model_copy(update={"headers": routed_headers})
        return self._transport.request(routed)
