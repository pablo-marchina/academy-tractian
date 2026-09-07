from __future__ import annotations

import os

from research.e2.controller import ControllerContext, ControllerDecision, DecisionSource
from research.e2.models import BoundRequest
from research.e2.transport import RequestTransport, TransportResponse

from .evaluation import ProductionEvaluationPolicy, ProductionEvaluator
from .production_actions_v2 import ProductionActionPrincipal
from .production_config import RemoteProductionConfig
from .release0_capabilities import install_release0_capabilities
from .release_identity import load_artifact_release_identity
from .release_provider import (
    NO_PROVIDER_SELECTION_STATE,
    PROVISIONAL_RELEASE_PROVIDER_STATE,
    validate_release_provider_config,
)
from .release_provider_v13 import build_release_provider_decision_source_factory_v13
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
    return build_release_provider_decision_source_factory_v13(config)


def _provider_selection_state(config: RemoteProductionConfig) -> str:
    return (
        PROVISIONAL_RELEASE_PROVIDER_STATE
        if config.provider_calls_enabled
        else NO_PROVIDER_SELECTION_STATE
    )


def deny_production_action_principal(*, user_id: str) -> ProductionActionPrincipal:
    """Fail closed when no user-serving Release 0 runtime is enabled."""

    raise PermissionError(f"production_actions_not_enabled:{user_id}")


def release0_read_only_action_principal(*, user_id: str) -> ProductionActionPrincipal:
    """Bind a real user to a server-owned principal that authorizes reads and no actions.

    ActionProposalRealtimeProductionRuntime resolves a principal before it knows whether the
    model will select a read or an action tool. Release 0 therefore needs a valid principal for
    genuine read-only runs, but it must not grant any consequential permission or resource
    binding. Read tools bypass the action policy; every action proposal is deterministically
    blocked before custody or transport because this principal has zero permissions.
    """

    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="__release0_read_only__",
        permissions=frozenset(),
        resource_company_bindings=(),
    )


def _configure_runtime_evaluator(app, *, provider_calls_enabled: bool) -> None:
    """Bind the remote runtime evaluator to the serving provider mode before startup.

    The generic product defaults to provider-free evaluation for backwards-compatible tests and
    offline paths. Remote Release 0 is different by construction: a successful trace must contain
    one validated model-call provenance record per live provider decision.

    Composition tests intentionally replace the real production factory with a minimal FastAPI
    app that has no evaluator attribute; keep that seam supported without weakening the real app.
    """

    runtime = getattr(app, "state", None)
    runtime = getattr(runtime, "product_runtime", None)
    if runtime is None:
        return
    runtime.evaluator = ProductionEvaluator(
        policy=ProductionEvaluationPolicy(
            require_live_model_provenance=provider_calls_enabled,
        )
    )


def create_remote_server_app():
    """Compose the production app from environment-backed configuration."""

    config = load_remote_production_config()
    release_identity = load_artifact_release_identity(
        configured_sha=config.release_git_sha,
        railway_sha=os.getenv("RAILWAY_GIT_COMMIT_SHA"),
    )
    app = create_remote_production_app(
        config,
        decision_source_factory=_decision_source_factory(config),
        transport=build_tractian_transport(config),
        action_principal_resolver=(
            release0_read_only_action_principal
            if config.provider_calls_enabled
            else deny_production_action_principal
        ),
    )
    app.state.release_identity = release_identity
    _configure_runtime_evaluator(app, provider_calls_enabled=config.provider_calls_enabled)
    install_release0_capabilities(app, config=config)
    app.state.provider_selection_state = _provider_selection_state(config)
    app.state.tractian_transport_state = _tractian_transport_state(config)
    return app


app = create_remote_server_app()
