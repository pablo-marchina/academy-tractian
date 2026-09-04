from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Literal

from fastapi import FastAPI

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .postgres_product_api import create_postgres_action_capable_product_app
from .production_actions_v2 import ActionAuthorizationResolver
from .runtime_identity import SignedBearerRuntimeContextProvider


def create_authenticated_postgres_action_capable_product_app(
    *,
    db_path: str | Path,
    internal_dsn: str,
    scoped_dsn: str,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    authorization_resolver: ActionAuthorizationResolver,
    runtime_identity_secret: bytes | str,
    runtime_identity_issuer: str,
    runtime_identity_audience: str,
    runtime_identity_max_ttl_seconds: int = 3600,
    runtime_identity_clock_skew_seconds: int = 30,
    runtime_identity_allowed_privileged_permissions: Iterable[str] = (),
    schema: str = "academy_operational",
    observability_schema: str = "academy_observability",
    observability_backend: Literal["duckdb", "postgresql"] = "duckdb",
    initialize_schema: bool = False,
    max_workers: int = 4,
    provider_calls_enabled: bool = True,
    actions_enabled: bool = False,
    heartbeat_interval_ms: int = 1000,
) -> FastAPI:
    """Create the authenticated Postgres topology with a selectable safe read-model backend.

    The hosted-only path uses ``observability_backend='postgresql'``. Historical provider-free
    reproduction may retain DuckDB without changing runtime or API semantics.
    """

    context_provider = SignedBearerRuntimeContextProvider(
        secret=runtime_identity_secret,
        issuer=runtime_identity_issuer,
        audience=runtime_identity_audience,
        max_ttl_seconds=runtime_identity_max_ttl_seconds,
        clock_skew_seconds=runtime_identity_clock_skew_seconds,
        allowed_privileged_permissions=runtime_identity_allowed_privileged_permissions,
    )
    app = create_postgres_action_capable_product_app(
        db_path=db_path,
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        context_provider=context_provider,
        authorization_resolver=authorization_resolver,
        schema=schema,
        observability_schema=observability_schema,
        observability_backend=observability_backend,
        initialize_schema=initialize_schema,
        max_workers=max_workers,
        provider_calls_enabled=provider_calls_enabled,
        actions_enabled=actions_enabled,
        heartbeat_interval_ms=heartbeat_interval_ms,
    )
    app.state.runtime_identity_backend = "signed-bearer-hmac-sha256-v1"
    app.state.runtime_identity_issuer = runtime_identity_issuer
    app.state.runtime_identity_audience = runtime_identity_audience
    return app
