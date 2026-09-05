from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import quote

from research.e2.models import BoundRequest, Permission, ToolSpec
from research.e2.transport import RequestTransport, TransportResponse

from .action_safety import ResourceCompanyBinding
from .production_actions_v2 import ProductionActionPrincipal


_KNOWN_UPSTREAM_PERMISSIONS = frozenset(permission.value for permission in Permission)
_GLOBAL_READ_PREFIXES = ("/knowledge/", "/models/")


class TractianAuthorityError(RuntimeError):
    """Fail-closed upstream authorization failure with a non-sensitive stable code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class TractianUserAuthority:
    user_id: str
    company_id: str
    permissions: frozenset[Permission]


class TractianAuthority:
    """Server-owned authorization facts derived from the TRACTIAN API.

    This boundary never consumes model text, JWT permission claims, browser-provided company
    headers, or evaluator-only data. The verified OIDC subject is used only as the x-user-id input
    to the upstream identity endpoint. Resource ownership is resolved from normal TRACTIAN read
    endpoints and is fail-closed when the upstream response is missing, degraded, malformed, or
    cannot prove a company binding.

    The challenge API exposes no company relationship for models and no public case lookup.
    Therefore model retraining and case escalation intentionally remain unqualified here.
    """

    def __init__(self, *, transport: RequestTransport) -> None:
        self._transport = transport

    def _get(
        self,
        *,
        path: str,
        user_id: str,
        query: Mapping[str, Any] | None = None,
    ) -> Any:
        response = self._transport.request(
            BoundRequest(
                method="GET",
                path=path,
                query=dict(query or {}),
                headers={"x-user-id": user_id},
                body=None,
            )
        )
        if response.status_code != 200:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_UPSTREAM_REJECTED")
        return response.body

    @staticmethod
    def _required_string(payload: Mapping[str, Any], key: str, *, code: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
            raise TractianAuthorityError(code)
        return value

    @staticmethod
    def _envelope_data(body: Any) -> Mapping[str, Any]:
        if not isinstance(body, Mapping):
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_MALFORMED_RESPONSE")
        data = body.get("data")
        if not isinstance(data, Mapping):
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE")
        return data

    def current_user(self, *, user_id: str) -> TractianUserAuthority:
        body = self._get(path="/users/me", user_id=user_id)
        if not isinstance(body, Mapping):
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_MALFORMED_USER")
        upstream_user_id = self._required_string(
            body,
            "id",
            code="TRACTIAN_AUTHORITY_MALFORMED_USER",
        )
        if upstream_user_id != user_id:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_USER_MISMATCH")
        company_id = self._required_string(
            body,
            "company_id",
            code="TRACTIAN_AUTHORITY_MALFORMED_USER",
        )
        raw_permissions = body.get("permissions")
        if not isinstance(raw_permissions, list) or not all(
            isinstance(item, str) for item in raw_permissions
        ):
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_MALFORMED_PERMISSIONS")
        if len(raw_permissions) > 64 or len(set(raw_permissions)) != len(raw_permissions):
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_MALFORMED_PERMISSIONS")
        unknown = set(raw_permissions) - _KNOWN_UPSTREAM_PERMISSIONS
        if unknown:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_UNKNOWN_PERMISSION")
        return TractianUserAuthority(
            user_id=user_id,
            company_id=company_id,
            permissions=frozenset(Permission(item) for item in raw_permissions),
        )

    def asset_company(self, *, user_id: str, asset_id: str) -> str:
        body = self._get(
            path=f"/assets/{quote(asset_id, safe='')}",
            user_id=user_id,
            query={"seed": "complete"},
        )
        data = self._envelope_data(body)
        observed_id = self._required_string(
            data,
            "id",
            code="TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE",
        )
        if observed_id != asset_id:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_RESOURCE_ID_MISMATCH")
        return self._required_string(
            data,
            "company_id",
            code="TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE",
        )

    def analysis_binding(self, *, user_id: str, analysis_id: str) -> tuple[str, str]:
        body = self._get(
            path=f"/analyses/{quote(analysis_id, safe='')}",
            user_id=user_id,
            query={"seed": "complete"},
        )
        data = self._envelope_data(body)
        observed_id = self._required_string(
            data,
            "id",
            code="TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE",
        )
        if observed_id != analysis_id:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_RESOURCE_ID_MISMATCH")
        asset_id = self._required_string(
            data,
            "asset_id",
            code="TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE",
        )
        return asset_id, self.asset_company(user_id=user_id, asset_id=asset_id)

    def action_principal(
        self,
        *,
        user_id: str,
        tool: ToolSpec,
        arguments: Mapping[str, Any],
    ) -> ProductionActionPrincipal:
        user = self.current_user(user_id=user_id)
        bindings: tuple[ResourceCompanyBinding, ...] = ()

        if tool.name == "update_asset_config":
            asset_id = arguments.get("asset_id")
            if isinstance(asset_id, str) and asset_id:
                company_id = self.asset_company(user_id=user_id, asset_id=asset_id)
                bindings = (
                    ResourceCompanyBinding(resource_id=asset_id, company_id=company_id),
                )
        elif tool.name in {"reprocess_analysis", "request_specialist_analysis"}:
            analysis_id = arguments.get("analysis_id")
            if isinstance(analysis_id, str) and analysis_id:
                _asset_id, company_id = self.analysis_binding(
                    user_id=user_id,
                    analysis_id=analysis_id,
                )
                bindings = (
                    ResourceCompanyBinding(resource_id=analysis_id, company_id=company_id),
                )
        elif tool.name in {"request_retraining", "escalate_case"}:
            # The supplied upstream contract cannot prove company ownership for these targets.
            bindings = ()
        else:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_UNSUPPORTED_ACTION")

        return ProductionActionPrincipal(
            user_id=user.user_id,
            user_company_id=user.company_id,
            permissions=user.permissions,
            resource_company_bindings=bindings,
        )

    def authorize_bound_request(self, request: BoundRequest) -> TractianUserAuthority:
        """Authorize a canonical tool HTTP request before its response may reach the model."""

        user_id = request.headers.get("x-user-id")
        if not isinstance(user_id, str) or not user_id:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_USER_REQUIRED")
        user = self.current_user(user_id=user_id)
        path = request.path
        if not path.startswith("/") or "?" in path or "#" in path:
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_INVALID_PATH")

        parts = [part for part in path.split("/") if part]
        if path == "/users/me" and request.method == "GET":
            return user

        if len(parts) >= 2 and parts[0] == "companies":
            if parts[1] != user.company_id:
                raise TractianAuthorityError("TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED")
            if request.method != "GET" or len(parts) not in {2, 3}:
                raise TractianAuthorityError("TRACTIAN_AUTHORITY_PATH_NOT_QUALIFIED")
            if len(parts) == 3 and parts[2] != "assets":
                raise TractianAuthorityError("TRACTIAN_AUTHORITY_PATH_NOT_QUALIFIED")
            return user

        if len(parts) >= 2 and parts[0] == "assets":
            company_id = self.asset_company(user_id=user_id, asset_id=parts[1])
            if company_id != user.company_id:
                raise TractianAuthorityError("TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED")
            return user

        if len(parts) >= 2 and parts[0] == "analyses":
            _asset_id, company_id = self.analysis_binding(
                user_id=user_id,
                analysis_id=parts[1],
            )
            if company_id != user.company_id:
                raise TractianAuthorityError("TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED")
            return user

        if request.method == "GET" and path.startswith(_GLOBAL_READ_PREFIXES):
            return user

        if len(parts) >= 2 and parts[0] == "models":
            # Model reads are global in the supplied contract; mutation lacks tenant ownership.
            if request.method == "GET" and len(parts) == 2:
                return user
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE")

        if len(parts) >= 2 and parts[0] == "cases":
            # No public case lookup exists to prove company ownership before escalation.
            raise TractianAuthorityError("TRACTIAN_AUTHORITY_RESOURCE_SCOPE_UNAVAILABLE")

        raise TractianAuthorityError("TRACTIAN_AUTHORITY_PATH_NOT_QUALIFIED")


class TenantGuardedTractianTransport(RequestTransport):
    """Last-mile tenant guard around the remote TRACTIAN HTTP transport."""

    def __init__(
        self,
        *,
        authority: TractianAuthority,
        transport: RequestTransport,
    ) -> None:
        self._authority = authority
        self._transport = transport

    def request(self, request: BoundRequest) -> TransportResponse:
        try:
            self._authority.authorize_bound_request(request)
        except TractianAuthorityError as exc:
            status_code = 403 if exc.code == "TRACTIAN_AUTHORITY_CROSS_TENANT_DENIED" else 503
            return TransportResponse(
                status_code=status_code,
                headers={"content-type": "application/json"},
                body={"code": exc.code, "message": "Request blocked by server-owned resource authorization."},
            )
        return self._transport.request(request)
