from __future__ import annotations

import json
import os
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from fastapi import HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from research.e2.models import BoundRequest
from research.e2.transport import RequestTransport, TransportResponse

from .cloudflare_provider_client import CloudflareWorkersAIChatCompletionsDecisionClient
from .decision_source import ProviderCallIdentity, ProviderDecisionSource
from .groq_provider_client import GroqChatCompletionsDecisionClient
from .hosted_action_authorization import (
    HostedActionAuthorizationResolver,
    HostedTractianAuthority,
)
from .hosted_config import HostedProductConfig
from .oidc_runtime_identity import OIDCClaimMapping, OIDCRuntimeContextProvider
from .postgres_product_api import create_postgres_action_capable_product_app
from .provider_clients import (
    GOOGLE_MODEL_ID,
    OPENAI_MODEL_ID,
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
    UrllibProviderJsonTransport,
)
from .runtime import canonical_tool_registry
from .tractian_authority import TenantGuardedTractianTransport, TractianAuthorityError


class HostedTractianTransport(RequestTransport):
    """One-shot HTTP adapter for the canonical TRACTIAN contract.

    The model sees only canonical ToolSpecs. Endpoint credentials stay application-owned. HTTP
    error responses are returned to the existing runner for deterministic policy handling;
    network/serialization failures fail closed and are never retried here.

    Hosted production never exposes this raw adapter directly to a model-facing runtime. It is
    wrapped by ``TenantGuardedTractianTransport`` so resource authorization happens before an
    upstream response can become model evidence.
    """

    def __init__(
        self,
        *,
        base_url: str,
        bearer_token: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._bearer_token = bearer_token
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.timeout_seconds = float(timeout_seconds)

    def __repr__(self) -> str:
        return f"HostedTractianTransport(base_url={self.base_url!r}, bearer_token=<redacted>)"

    def request(self, request: BoundRequest) -> TransportResponse:
        path = request.path if request.path.startswith("/") else f"/{request.path}"
        url = f"{self.base_url}{path}"
        if request.query:
            url = f"{url}?{urllib_parse.urlencode(request.query, doseq=True)}"
        headers = {**request.headers, "Accept": "application/json"}
        if request.body is not None:
            headers.setdefault("Content-Type", "application/json")
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        payload = None if request.body is None else json.dumps(
            request.body,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        raw_request = urllib_request.Request(
            url,
            data=payload,
            headers=headers,
            method=request.method,
        )
        try:
            with urllib_request.urlopen(raw_request, timeout=self.timeout_seconds) as response:
                status_code = int(response.status)
                response_headers = dict(response.headers)
                raw_body = response.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            status_code = int(exc.code)
            response_headers = dict(exc.headers)
            raw_body = exc.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise RuntimeError("tractian_transport_failure") from exc
        try:
            body = json.loads(raw_body) if raw_body else None
        except ValueError:
            body = raw_body
        return TransportResponse(
            status_code=status_code,
            headers=response_headers,
            body=body,
        )


def _decision_source_factory(config: HostedProductConfig):
    registry = canonical_tool_registry()

    def factory():
        transport = UrllibProviderJsonTransport()
        if config.provider == "google":
            if config.model != GOOGLE_MODEL_ID:
                raise ValueError("configured_google_model_not_implemented")
            client = GoogleInteractionsDecisionClient(
                api_key=config.provider_api_key,
                transport=transport,
                timeout_seconds=45.0,
            )
        elif config.provider == "openai":
            if config.model != OPENAI_MODEL_ID:
                raise ValueError("configured_openai_model_not_implemented")
            client = OpenAIResponsesDecisionClient(
                api_key=config.provider_api_key,
                transport=transport,
                timeout_seconds=45.0,
            )
        elif config.provider == "groq":
            client = GroqChatCompletionsDecisionClient(
                api_key=config.provider_api_key,
                model_id=config.model,
                transport=transport,
                timeout_seconds=45.0,
            )
        else:
            client = CloudflareWorkersAIChatCompletionsDecisionClient(
                api_token=config.provider_api_key,
                account_id=config.provider_account_id or "",
                model_id=config.model,
                transport=transport,
                timeout_seconds=45.0,
            )
        return ProviderDecisionSource(
            client=client,
            registry=registry,
            call_identity=ProviderCallIdentity(
                provider_id=client.provider_id,
                model_id=client.model_id,
                route_id=client.route_id,
                live_call=True,
            ),
        )

    return factory


def _raw_tractian_transport(config: HostedProductConfig) -> HostedTractianTransport:
    return HostedTractianTransport(
        base_url=config.tractian_base_url,
        bearer_token=config.tractian_bearer_token,
    )


def build_hosted_product(config: HostedProductConfig | None = None):
    active = config or HostedProductConfig.from_environment()
    oidc_context_provider = OIDCRuntimeContextProvider(
        issuer=active.oidc_issuer,
        audience=active.oidc_audience,
        jwks_url=active.oidc_jwks_url,
        algorithms=active.oidc_algorithms,
        claim_mapping=OIDCClaimMapping(
            organization_claim=active.oidc_organization_claim,
            role_claim=active.oidc_role_claim,
            permissions_claim=active.oidc_permissions_claim,
            identity_claim=active.oidc_identity_claim,
            required_claims=(active.oidc_role_claim,),
        ),
        allowed_claim_permissions=active.allowed_claim_permissions,
        allowed_privileged_permissions=(),
        authorized_parties=active.oidc_authorized_parties,
    )
    authority = HostedTractianAuthority(transport=_raw_tractian_transport(active))
    action_authorization_resolver = HostedActionAuthorizationResolver(authority=authority)

    def context_provider(request: Request):
        context = oidc_context_provider(request)
        # Bind the trusted OIDC tenant to the independent TRACTIAN user directory at the point a
        # new execution is created. Historical run reads stay available if TRACTIAN is temporarily
        # unavailable; their organization/user ownership is already durable in PostgreSQL.
        if request.method == "POST" and request.url.path == "/api/runs":
            try:
                upstream_user = authority.current_user(user_id=context.user_id)
            except TractianAuthorityError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="tractian_identity_authority_unavailable",
                ) from exc
            if upstream_user.company_id != context.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="oidc_tractian_tenant_mismatch",
                )
        return context

    def transport_factory() -> RequestTransport:
        raw = _raw_tractian_transport(active)
        return TenantGuardedTractianTransport(
            authority=authority,
            transport=raw,
        )

    app = create_postgres_action_capable_product_app(
        # The factory calls this trusted application DML connection `internal_dsn` for historical
        # reasons. Hosted serving supplies a dedicated SERVICE role here, never the migration owner.
        internal_dsn=active.postgres_service_dsn,
        scoped_dsn=active.postgres_scoped_dsn,
        decision_source_factory=_decision_source_factory(active),
        transport_factory=transport_factory,
        context_provider=context_provider,
        authorization_resolver=action_authorization_resolver,
        schema=active.postgres_schema,
        initialize_schema=False,
        max_workers=active.max_workers,
        provider_calls_enabled=True,
        # The switch is now safe to expose because the resolver is exact-target and is invoked at
        # proposal + confirmation, while the guarded transport rechecks permission/scope again
        # immediately before the external HTTP side effect.
        actions_enabled=active.actions_enabled,
        heartbeat_interval_ms=active.heartbeat_interval_ms,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(active.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Last-Event-ID"],
        expose_headers=["Content-Type"],
        max_age=600,
    )
    app.state.hosted_config = active.sanitized_summary()
    app.state.runtime_identity_backend = "oidc-jwks-v1"
    app.state.resource_authorization_backend = "tractian-authority-v1"
    app.state.hosted_local_persistent_state_required = False
    app.state.hosted_runtime_ddl_credential_present = False
    app.state.hosted_cross_tenant_tool_reads_blocked = True
    app.state.hosted_actions_qualified = True
    app.state.hosted_action_authorization_backend = "exact-target-revalidated-v1"
    app.state.hosted_unqualified_action_tools = (
        "request_retraining",
        "escalate_case",
    )
    return app


def main() -> None:
    import uvicorn

    config = HostedProductConfig.from_environment()
    uvicorn.run(
        build_hosted_product(config),
        host=config.host,
        port=config.port,
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
