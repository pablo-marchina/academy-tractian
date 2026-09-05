from __future__ import annotations

from collections.abc import Callable
import os
from typing import Mapping

from fastapi import FastAPI

from research.e2.controller import DecisionSource
from research.e2.transport import RequestTransport

from .authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from .production_actions_v2 import ActionAuthorizationResolver
from .production_config import RemoteProductionConfig


def load_remote_production_config(
    environ: Mapping[str, str] | None = None,
) -> RemoteProductionConfig:
    """Load and validate the production contract before any serving dependency is opened."""

    return RemoteProductionConfig.from_env(os.environ if environ is None else environ)


def create_remote_production_app(
    *,
    config: RemoteProductionConfig,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    authorization_resolver: ActionAuthorizationResolver,
    schema: str = "academy_operational",
    max_workers: int = 4,
    heartbeat_interval_ms: int = 1000,
) -> FastAPI:
    """Build the only production composition allowed to call itself remote-serving ready.

    Configuration validation happens before PostgreSQL pools, realtime listeners or runtime
    workers are created. Schema migration is intentionally disabled at serving boot so a remote
    deployment cannot retain an implicit DDL/bootstrap path. Provider execution remains under the
    explicit project gate represented by ``config.provider_calls_enabled``; consequential actions
    stay off at this P0 boundary until the later standards-IAM/action deployment gate is proved.
    """

    # Revalidate even when a model was created programmatically, keeping this function as a
    # defensive boot boundary rather than trusting an arbitrary object with similar attributes.
    config = RemoteProductionConfig.model_validate(config.model_dump())
    release_metadata = config.safe_metadata()

    app = create_authenticated_postgres_action_capable_product_app(
        internal_dsn=config.internal_dsn.get_secret_value(),
        scoped_dsn=config.scoped_dsn.get_secret_value(),
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        authorization_resolver=authorization_resolver,
        runtime_identity_secret=config.runtime_identity_secret.get_secret_value(),
        runtime_identity_issuer=config.runtime_identity_issuer,
        runtime_identity_audience=config.runtime_identity_audience,
        schema=schema,
        initialize_schema=False,
        max_workers=max_workers,
        provider_calls_enabled=config.provider_calls_enabled,
        actions_enabled=False,
        heartbeat_interval_ms=heartbeat_interval_ms,
    )
    app.state.remote_production = True
    app.state.release_metadata = release_metadata
    app.state.production_cost_policy = config.cost_policy
    app.state.paid_fallback_enabled = False
    app.state.local_serving_enabled = False

    @app.get("/api/meta/release")
    def release_identity() -> dict[str, object]:
        return dict(release_metadata)

    return app
