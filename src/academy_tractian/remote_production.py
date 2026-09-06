from __future__ import annotations

from collections.abc import Callable
import logging
import os
from typing import Literal, Mapping

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
from .release_identity import ArtifactReleaseIdentity, build_verified_release_metadata


_LOGGER = logging.getLogger(__name__)
TractianTransportState = Literal["UNCONFIGURED", "CONFIGURED_UNVERIFIED"]


def load_remote_production_config(
    environ: Mapping[str, str] | None = None,
) -> RemoteProductionConfig:
    """Load and validate the production contract before any serving dependency is opened."""

    return RemoteProductionConfig.from_env(os.environ if environ is None else environ)


def create_remote_production_app(
    *,
    config: RemoteProductionConfig,
    artifact_release_identity: ArtifactReleaseIdentity,
    decision_source_factory: Callable[[], DecisionSource],
    transport_factory: Callable[[], RequestTransport],
    authorization_resolver: ActionAuthorizationResolver,
    railway_runtime_git_sha: str | None = None,
    tractian_transport_state: TractianTransportState = "UNCONFIGURED",
    schema: str = "academy_operational",
    max_workers: int = 4,
    heartbeat_interval_ms: int = 1000,
) -> FastAPI:
    """Build the only production composition allowed to call itself remote-serving ready.

    Configuration and baked-artifact identity validation happen before PostgreSQL pools,
    realtime listeners or runtime workers are created. Schema migration is intentionally
    disabled at serving boot. Model/provider execution remains under its explicit selection
    gate, TRACTIAN API composition has an independent state, and consequential actions stay
    disabled at this infrastructure/IAM boundary.
    """

    config = RemoteProductionConfig.model_validate(config.model_dump())
    expected_tractian_state: TractianTransportState = (
        "CONFIGURED_UNVERIFIED" if config.tractian_transport_enabled else "UNCONFIGURED"
    )
    if tractian_transport_state != expected_tractian_state:
        raise RuntimeError("production_tractian_transport_state_config_mismatch")

    release_metadata = build_verified_release_metadata(
        configured_metadata=config.safe_metadata(),
        artifact_identity=artifact_release_identity,
        railway_runtime_git_sha=railway_runtime_git_sha,
    )
    release_metadata = {
        **release_metadata,
        "tractian_transport_state": tractian_transport_state,
    }

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
    app.state.tractian_transport_state = tractian_transport_state

    _LOGGER.info(
        "remote_production_composed",
        extra={
            "academy_event": "remote_production_composed",
            "tractian_transport_state": tractian_transport_state,
            "provider_calls_enabled": config.provider_calls_enabled,
            "actions_enabled": False,
            "browser_iam_mode": config.browser_iam_mode,
        },
    )

    @app.get("/api/meta/release")
    def release_identity() -> dict[str, object]:
        return dict(release_metadata)

    return app
