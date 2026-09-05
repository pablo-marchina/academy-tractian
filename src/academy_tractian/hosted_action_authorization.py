from __future__ import annotations

from typing import Any, Mapping

from research.e2.models import BoundRequest, Permission, ToolSpec

from .production_actions_v2 import ProductionActionPrincipal
from .tractian_authority import TractianAuthority, TractianAuthorityError


class HostedTractianAuthority(TractianAuthority):
    """TRACTIAN authority with last-mile action permission revalidation.

    Hosted serving accepts mutations only for the exact canonical action routes. Resource scope is
    resolved first and the user's permission/company are fetched again afterwards, making the final
    authority read the closest possible check before the raw HTTP side effect. The upstream action
    endpoint still receives the same server-bound ``x-user-id`` and independently checks its own
    permission at execution time.
    """

    @staticmethod
    def _required_permission(request: BoundRequest) -> Permission | None:
        parts = [part for part in request.path.split("/") if part]
        if request.method == "PATCH" and len(parts) == 2 and parts[0] == "assets":
            return Permission.ACTION_HIGH
        if (
            request.method == "POST"
            and len(parts) == 3
            and parts[0] == "analyses"
            and parts[2] in {"reprocess", "request-specialist"}
        ):
            return Permission.ACTION_LOW
        if (
            request.method == "POST"
            and len(parts) == 3
            and parts[0] == "models"
            and parts[2] == "request-retraining"
        ):
            return Permission.ACTION_HIGH
        if (
            request.method == "POST"
            and len(parts) == 3
            and parts[0] == "cases"
            and parts[2] == "escalate"
        ):
            return Permission.ESCALATE
        return None

    def authorize_bound_request(self, request: BoundRequest):
        permission = self._required_permission(request)
        if request.method != "GET" and permission is None:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_PATH_NOT_QUALIFIED")

        try:
            scoped_user = super().authorize_bound_request(request)
            if permission is None:
                return scoped_user

            # Re-read the user after target scope resolution so permission/company revocation that
            # happens between proposal/confirmation and transport is observed before the raw call.
            latest_user = self.current_user(user_id=scoped_user.user_id)
        except TractianAuthorityError:
            raise
        except Exception as exc:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_UPSTREAM_UNAVAILABLE") from exc

        if latest_user.company_id != scoped_user.company_id:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED")
        if permission not in latest_user.permissions:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_PERMISSION_DENIED")
        return latest_user


class HostedActionAuthorizationResolver:
    """Legacy-compatible principal resolver plus explicit exact-target resolution.

    ``__call__`` deliberately returns no resource bindings. It exists only for legacy API checks
    that need trusted user/company/permission facts. ``resolve_target`` is the production path used
    by the target-aware proposal and confirmation layers.
    """

    def __init__(self, *, authority: HostedTractianAuthority) -> None:
        self.authority = authority

    def __call__(self, *, user_id: str) -> ProductionActionPrincipal:
        user = self.authority.current_user(user_id=user_id)
        return ProductionActionPrincipal(
            user_id=user.user_id,
            user_company_id=user.company_id,
            permissions=user.permissions,
            resource_company_bindings=(),
        )

    def resolve_target(
        self,
        *,
        user_id: str,
        tool: ToolSpec,
        arguments: Mapping[str, Any],
    ) -> ProductionActionPrincipal:
        return self.authority.action_principal(
            user_id=user_id,
            tool=tool,
            arguments=arguments,
        )
