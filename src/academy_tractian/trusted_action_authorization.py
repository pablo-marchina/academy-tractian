from __future__ import annotations

import json
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from research.e2.models import Permission

from .action_safety import ResourceCompanyBinding
from .product_api import AuthenticatedRuntimeContext
from .production_actions_v2 import ProductionActionPrincipal


TRUSTED_ACTION_AUTHORIZATION_VERSION = "trusted-action-authorization-v1"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ServerOwnedActionAuthorizationGrant(_FrozenModel):
    """Authoritative action grant loaded from a server-owned source.

    This object is never accepted from the browser, model, tool arguments, or provider output.
    API capabilities such as ``actions:confirm:self`` are intentionally a different namespace and
    are not converted into canonical ToolSpec permissions here.
    """

    schema_version: Literal["trusted-action-authorization-grant-v1"] = (
        "trusted-action-authorization-grant-v1"
    )
    user_id: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)
    user_company_id: str = Field(min_length=1)
    permissions: frozenset[Permission] = frozenset()
    resource_company_bindings: tuple[ResourceCompanyBinding, ...] = ()
    policy_revision: str = Field(min_length=1, max_length=128)
    active: bool = True
    source_owned: Literal[True] = True

    @model_validator(mode="after")
    def validate_scope(self) -> "ServerOwnedActionAuthorizationGrant":
        resource_ids = [binding.resource_id for binding in self.resource_company_bindings]
        if len(resource_ids) != len(set(resource_ids)):
            raise ValueError("action authorization grant contains duplicate resource ids")
        if any(
            binding.company_id != self.user_company_id
            for binding in self.resource_company_bindings
        ):
            raise ValueError(
                "action authorization grant resource binding crosses the granted company"
            )
        return self


class ServerOwnedActionAuthorizationSource(Protocol):
    """Lookup contract for an authoritative server-side membership/policy store.

    Returning a tuple rather than a single row makes accidental duplicate/ambiguous grants
    observable and therefore denyable instead of silently choosing one.
    """

    def lookup(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> tuple[ServerOwnedActionAuthorizationGrant, ...]: ...


class ActionAuthorizationResolutionError(RuntimeError):
    """Sanitized fail-closed authorization resolution failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"trusted action authorization denied: {code}")


def _principal_from_grant(
    grant: ServerOwnedActionAuthorizationGrant,
) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=grant.user_id,
        user_company_id=grant.user_company_id,
        permissions=grant.permissions,
        resource_company_bindings=grant.resource_company_bindings,
    )


class ConfiguredServerOwnedActionAuthorizationSource:
    """Immutable server-configured grants for governed production execution.

    The serialized grant document is accepted only by the trusted production composition layer
    (for example a secret environment variable). It is never an HTTP request field. User ids are
    required to be globally unique in this configured source because the proposal runtime resolves
    principals before tenant context reaches the action boundary. Final confirmation independently
    re-resolves the grant against the authenticated organization so a valid user grant cannot be
    replayed across organizations.
    """

    def __init__(self, grants: tuple[ServerOwnedActionAuthorizationGrant, ...]) -> None:
        if not grants:
            raise ValueError("configured action authorization requires at least one grant")
        user_ids = [grant.user_id for grant in grants]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError(
                "configured action authorization requires globally unique user ids"
            )
        self._grants = grants
        self._by_user = {grant.user_id: grant for grant in grants}

    @classmethod
    def from_json(cls, raw: str) -> "ConfiguredServerOwnedActionAuthorizationSource":
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("action authorization grants must be valid JSON") from exc
        if not isinstance(decoded, list) or not decoded:
            raise ValueError("action authorization grants must be a non-empty JSON array")
        try:
            grants = tuple(
                ServerOwnedActionAuthorizationGrant.model_validate(item)
                for item in decoded
            )
        except ValidationError as exc:
            raise ValueError("action authorization grants violate the trusted grant schema") from exc
        return cls(grants)

    def lookup(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> tuple[ServerOwnedActionAuthorizationGrant, ...]:
        grant = self._by_user.get(user_id)
        if grant is None or grant.organization_id != organization_id:
            return ()
        return (grant,)

    def __call__(self, *, user_id: str) -> ProductionActionPrincipal:
        """Remain compatible with the proposal/executor user-id resolver protocol."""

        return self.resolve_user(user_id=user_id)

    def resolve_user(self, *, user_id: str) -> ProductionActionPrincipal:
        grant = self._by_user.get(user_id)
        if grant is None:
            raise ActionAuthorizationResolutionError("GRANT_NOT_FOUND")
        if not grant.active:
            raise ActionAuthorizationResolutionError("GRANT_INACTIVE")
        return _principal_from_grant(grant)

    def authorize_context(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> ProductionActionPrincipal:
        """Resolve final execution authority against the trusted authenticated tenant context."""

        grants = self.lookup(organization_id=organization_id, user_id=user_id)
        if len(grants) == 0:
            raise ActionAuthorizationResolutionError("GRANT_NOT_FOUND")
        if len(grants) != 1:
            raise ActionAuthorizationResolutionError("GRANT_AMBIGUOUS")
        grant = grants[0]
        if grant.user_id != user_id:
            raise ActionAuthorizationResolutionError("GRANT_USER_MISMATCH")
        if grant.organization_id != organization_id:
            raise ActionAuthorizationResolutionError("GRANT_ORGANIZATION_MISMATCH")
        if not grant.active:
            raise ActionAuthorizationResolutionError("GRANT_INACTIVE")
        return _principal_from_grant(grant)

    def safe_summary(self) -> dict[str, int]:
        """Expose counts only; never emit users, organizations, resources or permissions."""

        return {
            "configured_grants": len(self._grants),
            "active_grants": sum(grant.active for grant in self._grants),
        }


class OrganizationBoundActionAuthorizationResolver:
    """Adapter compatible with the existing user-id resolver protocol, but tenant-bound.

    One instance is valid for exactly one trusted authenticated request context. The existing
    action runtime still calls the resolver with only ``user_id``; this adapter closes that gap by
    binding ``organization_id`` before the runtime is constructed. A resolver must therefore be
    created per trusted request/execution boundary and must never be shared globally across
    organizations.
    """

    def __init__(
        self,
        *,
        context: AuthenticatedRuntimeContext,
        source: ServerOwnedActionAuthorizationSource,
    ) -> None:
        if not isinstance(context, AuthenticatedRuntimeContext):
            raise TypeError("trusted action authorization requires AuthenticatedRuntimeContext")
        self._organization_id = context.organization_id
        self._user_id = context.user_id
        self._source = source

    @property
    def organization_id(self) -> str:
        return self._organization_id

    @property
    def bound_user_id(self) -> str:
        return self._user_id

    def __call__(self, *, user_id: str) -> ProductionActionPrincipal:
        if user_id != self._user_id:
            raise ActionAuthorizationResolutionError("BOUND_USER_MISMATCH")

        try:
            grants = self._source.lookup(
                organization_id=self._organization_id,
                user_id=self._user_id,
            )
        except ActionAuthorizationResolutionError:
            raise
        except Exception as exc:
            raise ActionAuthorizationResolutionError("SOURCE_UNAVAILABLE") from exc

        if not isinstance(grants, tuple):
            raise ActionAuthorizationResolutionError("SOURCE_CONTRACT_INVALID")
        if len(grants) == 0:
            raise ActionAuthorizationResolutionError("GRANT_NOT_FOUND")
        if len(grants) != 1:
            raise ActionAuthorizationResolutionError("GRANT_AMBIGUOUS")

        grant = grants[0]
        if not isinstance(grant, ServerOwnedActionAuthorizationGrant):
            raise ActionAuthorizationResolutionError("SOURCE_CONTRACT_INVALID")
        if grant.user_id != self._user_id:
            raise ActionAuthorizationResolutionError("GRANT_USER_MISMATCH")
        if grant.organization_id != self._organization_id:
            raise ActionAuthorizationResolutionError("GRANT_ORGANIZATION_MISMATCH")
        if not grant.active:
            raise ActionAuthorizationResolutionError("GRANT_INACTIVE")

        return _principal_from_grant(grant)


class TrustedActionAuthorizationResolverFactory:
    """Create a fresh organization-bound resolver from a trusted request context."""

    def __init__(self, *, source: ServerOwnedActionAuthorizationSource) -> None:
        self._source = source

    def bind(
        self,
        *,
        context: AuthenticatedRuntimeContext,
    ) -> OrganizationBoundActionAuthorizationResolver:
        return OrganizationBoundActionAuthorizationResolver(
            context=context,
            source=self._source,
        )
