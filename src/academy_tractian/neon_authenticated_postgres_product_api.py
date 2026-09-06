from __future__ import annotations

from collections.abc import Callable
from hashlib import sha256

from fastapi import FastAPI, Request

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .neon_auth_identity import NeonAuthRuntimeContextProvider
from .postgres_product_api import create_postgres_action_capable_product_app
from .product_api import AuthenticatedRuntimeContext, trusted_runtime_context
from .production_actions_v2 import ActionAuthorizationResolver


_SESSION_CONTEXT_SCHEMA_VERSION = "production-session-context-v1"


def _fingerprint(value: str) -> str:
    """Return a stable non-reversible browser-safe identity fingerprint."""

    return sha256(f"academy-tractian-session-context:{value}".encode("utf-8")).hexdigest()[:24]


def public_session_context(context: AuthenticatedRuntimeContext) -> dict[str, object]:
    """Project trusted identity into a browser-safe diagnostic/acceptance surface.

    Raw managed user, identity and organization identifiers stay server-side. The endpoint exists
    so production IAM/tenant behavior can be inspected and regression-tested without making
    browser headers or payloads authoritative.
    """

    organization_kind = "personal" if context.organization_id.startswith("user:") else "managed"
    return {
        "schema_version": _SESSION_CONTEXT_SCHEMA_VERSION,
        "identity_fingerprint": _fingerprint(context.identity_id),
        "user_fingerprint": _fingerprint(context.user_id),
        "organization_fingerprint": _fingerprint(context.organization_id),
        "organization_kind": organization_kind,
        "role": context.role,
        "permissions": sorted(context.permissions),
        "server_owned": True,
    }


def create_neon_authenticated_postgres_action_capable_product_app(
    *,
    internal_dsn: str,
    scoped_dsn: str,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    authorization_resolver: ActionAuthorizationResolver,
    neon_auth_base_url: str,
    neon_auth_timeout_seconds: float = 5.0,
    schema: str = "academy_operational",
    initialize_schema: bool = False,
    max_workers: int = 4,
    provider_calls_enabled: bool = True,
    actions_enabled: bool = False,
    heartbeat_interval_ms: int = 1000,
) -> FastAPI:
    """Create the promoted PostgreSQL topology with managed browser-session identity."""

    context_provider = NeonAuthRuntimeContextProvider(
        base_url=neon_auth_base_url,
        timeout_seconds=neon_auth_timeout_seconds,
    )
    app = create_postgres_action_capable_product_app(
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        context_provider=context_provider,
        authorization_resolver=authorization_resolver,
        schema=schema,
        initialize_schema=initialize_schema,
        max_workers=max_workers,
        provider_calls_enabled=provider_calls_enabled,
        actions_enabled=actions_enabled,
        heartbeat_interval_ms=heartbeat_interval_ms,
    )

    @app.get("/api/session/context")
    def session_context(request: Request) -> dict[str, object]:
        context = trusted_runtime_context(context_provider, request)
        return public_session_context(context)

    app.state.runtime_identity_backend = "neon-auth-managed-session-v1"
    app.state.neon_auth_base_url_configured = True
    return app
