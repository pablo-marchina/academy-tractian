from __future__ import annotations

from .production_actions_v2 import ProductionActionPrincipal
from .trusted_action_authorization import (
    ActionAuthorizationResolutionError,
    ConfiguredServerOwnedActionAuthorizationSource,
)


class ReadCapableConfiguredActionAuthorizationResolver:
    """Keep ordinary investigation available when consequential actions are enabled globally.

    The action-proposal runtime resolves a principal before the model selects a read or action
    tool. A user without a server-owned action grant therefore still needs a principal so read
    tools can execute. This adapter returns a zero-action principal only for missing/inactive
    grants at proposal time. Final confirmation remains strict because ``authorize_context``
    delegates directly to the trusted source and still rejects missing/inactive grants.

    No tenant, permission, resource binding, company identity, confirmation fingerprint or
    idempotency material is accepted from the browser/model by this adapter.
    """

    _READ_ONLY_COMPANY_SENTINEL = "__no_action_grant__"

    def __init__(self, source: ConfiguredServerOwnedActionAuthorizationSource) -> None:
        self._source = source

    def __call__(self, *, user_id: str) -> ProductionActionPrincipal:
        try:
            return self._source.resolve_user(user_id=user_id)
        except ActionAuthorizationResolutionError as exc:
            if exc.code not in {"GRANT_NOT_FOUND", "GRANT_INACTIVE"}:
                raise
            return ProductionActionPrincipal(
                user_id=user_id,
                user_company_id=self._READ_ONLY_COMPANY_SENTINEL,
                permissions=frozenset(),
                resource_company_bindings=(),
            )

    def authorize_context(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> ProductionActionPrincipal:
        return self._source.authorize_context(
            organization_id=organization_id,
            user_id=user_id,
        )
