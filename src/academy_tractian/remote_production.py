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
from .neon_authenticated_postgres_product_api import (
    create_neon_authenticated_postgres_action_capable_product_app,
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
    workers are created. Schema migration is intentionally disabled at serving boot. Provider
    execution remains under the explicit provider-selection gate and consequential actions stay
    disabled at this infrastructure/IAM boundary.
    """

    config = RemoteProductionConfig.model_validate(config.model_dump())
    release_metadata = config.safe_metadata()

    common = dict(
        internal_dsn=config.internal_dsn.get_secret_value(),
        scoped_dsn=config.scoped_dsn.get_secret_value(),
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        authorization_resolver=authorization_resolver,
        schema=schema,
        initialize_schema=False,
        max_workers=max_workers,
        provider_calls_enabled=config.provider_calls_enabled,
        actions_enabled=False,
        heartbeat_interval_ms=heartbeat_interval_ms,
    )

    if config.browser_iam_mode == "neon-auth":
        if config.neon_auth_base_url is None:
            raise RuntimeError("validated neon-auth configuration is missing its base URL")
        app = create_neon_authenticated_postgres_action_capable_product_app(
            **common,
            neon_auth_base_url=config.neon_auth_base_url,
        )
    else:
        if (
            config.runtime_identity_secret is None
            or config.runtime_identity_issuer is None
            or config.runtime_identity_audience is None
        ):
            raise RuntimeError("validated signed-bearer configuration is incomplete")
        app = create_authenticated_postgres_action_capable_product_app(
            **common,
            runtime_identity_secret=config.runtime_identity_secret.get_secret_value(),
            runtime_identity_issuer=config.runtime_identity_issuer,
            runtime_identity_audience=config.runtime_identity_audience,
        )

    app.state.remote_production = True
    app.state.release_metadata = release_metadata
    app.state.production_cost_policy = config.cost_policy
    app.state.paid_fallback_enabled = False
    app.state.local_serving_enabled = False
    app.state.browser_iam_mode = config.browser_iam_mode

    @app.get("/api/meta/release")
    def release_identity() -> dict[str, object]:
        return dict(release_metadata)

    return app
