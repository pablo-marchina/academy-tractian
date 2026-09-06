from __future__ import annotations

import os

from research.e2.controller import ControllerContext, ControllerDecision, DecisionSource
from research.e2.models import BoundRequest
from research.e2.transport import RequestTransport, TransportResponse

from .production_actions_v2 import ProductionActionPrincipal
from .production_config import RemoteProductionConfig
from .release0_capabilities import install_release0_capabilities
from .release_identity import load_artifact_release_identity
from .release_provider import (
    NO_PROVIDER_SELECTION_STATE,
    PROVISIONAL_RELEASE_PROVIDER_STATE,
    build_release_provider_decision_source_factory,
    validate_release_provider_config,
)
from .remote_production import create_remote_production_app, load_remote_production_config
from .tractian_transport import ProductionTractianTransport


PROVIDER_SELECTION_STATE = NO_PROVIDER_SELECTION_STATE
TRACTIAN_TRANSPORT_STATE_UNCONFIGURED = "UNCONFIGURED"
TRACTIAN_TRANSPORT_STATE_CONFIGURED_UNVERIFIED = "CONFIGURED_UNVERIFIED"


class NoSelectedProviderDecisionSource(DecisionSource):
    """Fail-closed source used while production provider state remains NO_SELECTION."""

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        raise RuntimeError("production_provider_not_selected")


class NoConfiguredTractianTransport(RequestTransport):
    """Fail before I/O while no authoritative TRACTIAN endpoint/auth contract is configured."""

    def request(self, _request: BoundRequest) -> TransportResponse:
        raise RuntimeError(
            "production_tractian_transport_unconfigured; production_provider_not_selected is a legacy transport label only"
        )


# Compatibility alias for historical tests/imports. The canonical production concept is now
# NoConfiguredTractianTransport; provider/model selection is governed only by DecisionSource.
NoSelectedProviderTransport = NoConfiguredTractianTransport


def build_tractian_transport(config: RemoteProductionConfig) -> RequestTransport:
    """Build the TRACTIAN transport without performing a remote request."""

    if not config.tractian_transport_enabled:
        return NoConfiguredTractianTransport()
    if config.tractian_base_url is None:
        raise RuntimeError("validated TRACTIAN configuration is missing its base URL")
    headers = config.tractian_server_headers()
    if not headers:
        raise RuntimeError("validated TRACTIAN configuration is missing server-managed headers")
    return ProductionTractianTransport(
        base_url=config.tractian_base_url,
        server_headers=headers,
    )


def _tractian_transport_state(config: RemoteProductionConfig) -> str:
    return (
        TRACTIAN_TRANSPORT_STATE_CONFIGURED_UNVERIFIED
        if config.tractian_transport_enabled
        else TRACTIAN_TRANSPORT_STATE_UNCONFIGURED
    )


def _decision_source_factory(config: RemoteProductionConfig):
    if not config.provider_calls_enabled:
        return NoSelectedProviderDecisionSource
    validate_release_provider_config(config)
    return build_release_provider_decision_source_factory(config)


def _provider_selection_state(config: RemoteProductionConfig) -> str:
    return (
        PROVISIONAL_RELEASE_PROVIDER_STATE
        if config.provider_calls_enabled
        else NO_PROVIDER_SELECTION_STATE
    )


def deny_production_action_principal(*, user_id: str) -> ProductionActionPrincipal:
    """Release 0 never authorizes consequential external action execution."""

    raise PermissionError(f"production_actions_not_enabled:{user_id}")


def app_factory():
    """Compose the remote product in infrastructure-probe or read-only Release 0 mode.

    Provider calls are opt-in and fail closed. Enabling them requires an explicitly configured
    provisional Release 0 provider and a real configured TRACTIAN transport. Consequential
    actions remain disabled by the production app composition regardless of provider state.
    """

    config = load_remote_production_config()
    artifact_release_identity = load_artifact_release_identity()

    tractian_transport_state = _tractian_transport_state(config)
    provider_selection_state = _provider_selection_state(config)
    # Validate provider/TRACTIAN composition before PostgreSQL pools or runtime workers open.
    build_tractian_transport(config)
    decision_source_factory = _decision_source_factory(config)

    if config.tractian_transport_enabled:
        transport_factory = lambda: build_tractian_transport(config)
    else:
        transport_factory = NoConfiguredTractianTransport

    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational")
    app = create_remote_production_app(
        config=config,
        artifact_release_identity=artifact_release_identity,
        railway_runtime_git_sha=os.environ.get("RAILWAY_GIT_COMMIT_SHA"),
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        authorization_resolver=deny_production_action_principal,
        tractian_transport_state=tractian_transport_state,
        schema=schema,
        max_workers=int(os.environ.get("ACADEMY_MAX_WORKERS", "4")),
        heartbeat_interval_ms=int(os.environ.get("ACADEMY_HEARTBEAT_INTERVAL_MS", "1000")),
    )
    app.state.provider_selection_state = provider_selection_state
    app.state.infrastructure_probe = not config.provider_calls_enabled
    app.state.release0_read_only = config.provider_calls_enabled
    install_release0_capabilities(
        app,
        config=config,
        artifact_release_identity=artifact_release_identity,
        provider_selection_state=provider_selection_state,
        tractian_transport_state=tractian_transport_state,
    )
    return app


def main() -> None:
    import uvicorn

    uvicorn.run(
        "academy_tractian.remote_server:app_factory",
        factory=True,
        host=os.environ.get("ACADEMY_BIND_HOST", "0.0.0.0"),
        port=int(os.environ.get("ACADEMY_PORT", "8000")),
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "info"),
        proxy_headers=True,
        forwarded_allow_ips=os.environ.get("ACADEMY_FORWARDED_ALLOW_IPS", "127.0.0.1"),
    )


if __name__ == "__main__":
    main()
