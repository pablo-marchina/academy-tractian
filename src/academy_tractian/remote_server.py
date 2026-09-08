from __future__ import annotations

import json
import os

from research.e2.controller import ControllerContext, ControllerDecision, DecisionSource
from research.e2.models import BoundRequest
from research.e2.transport import RequestTransport, TransportResponse

from .evaluation import ProductionEvaluationPolicy, ProductionEvaluator
from .production_actions_v2 import ProductionActionPrincipal
from .production_config import RemoteProductionConfig
from .read_capable_action_authorization import ReadCapableConfiguredActionAuthorizationResolver
from .release0_capabilities import install_release0_capabilities
from .release_identity import load_artifact_release_identity
from .release_provider import (
    NO_PROVIDER_SELECTION_STATE,
    PROVISIONAL_RELEASE_PROVIDER_STATE,
)
from .release_provider_v14 import (
    build_release_provider_decision_source_factory_v14,
    validate_release_provider_config_v14,
)
from .remote_production import create_remote_production_app, load_remote_production_config
from .tractian_transport import ProductionTractianTransport
from .trusted_action_authorization import ConfiguredServerOwnedActionAuthorizationSource
from .upstream_action_actors import (
    ConfiguredServerOwnedUpstreamActionActorSource,
    ServerOwnedUpstreamActionActorTransport,
)
from .verification_api import install_verification_api


PROVIDER_SELECTION_STATE = NO_PROVIDER_SELECTION_STATE
TRACTIAN_TRANSPORT_STATE_UNCONFIGURED = "UNCONFIGURED"
TRACTIAN_TRANSPORT_STATE_CONFIGURED_UNVERIFIED = "CONFIGURED_UNVERIFIED"
_UPSTREAM_ACTION_ACTORS_ENV = "ACADEMY_TRACTIAN_ACTION_ACTORS_JSON"


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
    validate_release_provider_config_v14(config)
    return build_release_provider_decision_source_factory_v14(config)


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


def _assert_actor_coverage_for_active_grants(
    *,
    raw_authorization_grants: str,
    authorization_source: ConfiguredServerOwnedActionAuthorizationSource,
    actor_source: ConfiguredServerOwnedUpstreamActionActorSource,
) -> None:
    """Make incomplete provider-side action identity a boot blocker, not a runtime surprise."""

    decoded = json.loads(raw_authorization_grants)
    if not isinstance(decoded, list):
        raise RuntimeError("validated action authorization grants lost list shape")
    for item in decoded:
        if not isinstance(item, dict) or item.get("active", True) is not True:
            continue
        user_id = item.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            raise RuntimeError("validated action authorization grant lost user identity")
        principal = authorization_source(user_id=user_id)
        actor_source.assert_complete_for_principal(principal)


def _configure_runtime_evaluator(app, *, provider_calls_enabled: bool) -> None:
    """Bind the remote runtime evaluator to the serving provider mode before startup.

    The generic product defaults to provider-free evaluation for backwards-compatible tests and
    offline paths. Remote Release 0 is different by construction: a successful trace must contain
    one validated model-call provenance record per live provider decision.

    Composition tests intentionally replace the real production factory with a minimal FastAPI
    application so they can assert dependency wiring without opening PostgreSQL resources. Those
    doubles are not remote-serving applications and must remain side-effect free. A genuine remote
    app sets ``app.state.remote_production = True``; for that topology the PostgreSQL horizontal
    runtime supervisor is mandatory and absence remains a fail-closed boot blocker.
    """

    supervisor = getattr(app.state, "runtime_handoff_supervisor", None)
    if supervisor is None:
        if getattr(app.state, "remote_production", False):
            raise RuntimeError("remote_runtime_handoff_supervisor_required")
        return

    if provider_calls_enabled:
        supervisor.evaluator = ProductionEvaluator(
            policy=ProductionEvaluationPolicy(
                provider_free=False,
                require_model_call_provenance=True,
            )
        )
        app.state.production_evaluation_mode = "traced_provider"
    else:
        supervisor.evaluator = ProductionEvaluator()
        app.state.production_evaluation_mode = "provider_free"


def app_factory():
    """Compose the remote product with fail-closed reads and governed action execution.

    Provider calls, the TRACTIAN transport, and consequential actions are independent opt-ins.
    Action execution additionally requires a valid server-owned grant document; the browser and
    model never supply canonical permissions, resource ownership, provider-side action identity,
    confirmation fingerprints or idempotency material.
    """

    config = load_remote_production_config()
    artifact_release_identity = load_artifact_release_identity()

    tractian_transport_state = _tractian_transport_state(config)
    provider_selection_state = _provider_selection_state(config)
    build_tractian_transport(config)
    decision_source_factory = _decision_source_factory(config)

    action_authorization_source = None
    action_actor_source = None
    raw_action_actors = os.environ.get(_UPSTREAM_ACTION_ACTORS_ENV, "").strip()
    if config.actions_enabled:
        if config.action_authorization_grants_json is None:
            raise RuntimeError("validated action configuration is missing authorization grants")
        if not raw_action_actors:
            raise RuntimeError(
                "enabled actions require server-owned ACADEMY_TRACTIAN_ACTION_ACTORS_JSON"
            )
        raw_authorization_grants = config.action_authorization_grants_json.get_secret_value()
        action_authorization_source = ConfiguredServerOwnedActionAuthorizationSource.from_json(
            raw_authorization_grants
        )
        action_actor_source = ConfiguredServerOwnedUpstreamActionActorSource.from_json(
            raw_action_actors
        )
        _assert_actor_coverage_for_active_grants(
            raw_authorization_grants=raw_authorization_grants,
            authorization_source=action_authorization_source,
            actor_source=action_actor_source,
        )
        authorization_resolver = ReadCapableConfiguredActionAuthorizationResolver(
            action_authorization_source
        )
    elif raw_action_actors:
        raise RuntimeError(
            "TRACTIAN upstream action actors cannot be configured while actions are disabled"
        )
    elif config.provider_calls_enabled:
        authorization_resolver = release0_read_only_action_principal
    else:
        authorization_resolver = deny_production_action_principal

    if config.tractian_transport_enabled:
        if action_actor_source is None:
            transport_factory = lambda: build_tractian_transport(config)
        else:
            def transport_factory() -> RequestTransport:
                return ServerOwnedUpstreamActionActorTransport(
                    transport=build_tractian_transport(config),
                    authorization_resolver=authorization_resolver,
                    actor_source=action_actor_source,
                )
    else:
        transport_factory = NoConfiguredTractianTransport

    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational")
    app = create_remote_production_app(
        config=config,
        artifact_release_identity=artifact_release_identity,
        railway_runtime_git_sha=os.environ.get("RAILWAY_GIT_COMMIT_SHA"),
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        authorization_resolver=authorization_resolver,
        tractian_transport_state=tractian_transport_state,
        schema=schema,
        max_workers=int(os.environ.get("ACADEMY_MAX_WORKERS", "4")),
        heartbeat_interval_ms=int(os.environ.get("ACADEMY_HEARTBEAT_INTERVAL_MS", "1000")),
    )
    _configure_runtime_evaluator(
        app,
        provider_calls_enabled=config.provider_calls_enabled,
    )
    app.state.provider_selection_state = provider_selection_state
    app.state.infrastructure_probe = not config.provider_calls_enabled
    app.state.release0_read_only = config.provider_calls_enabled and not config.actions_enabled
    app.state.action_authorization_summary = (
        action_authorization_source.safe_summary()
        if action_authorization_source is not None
        else {"configured_grants": 0, "active_grants": 0}
    )
    app.state.upstream_action_actor_summary = (
        action_actor_source.safe_summary()
        if action_actor_source is not None
        else {"configured_bindings": 0, "configured_companies": 0}
    )
    install_release0_capabilities(
        app,
        config=config,
        artifact_release_identity=artifact_release_identity,
        provider_selection_state=provider_selection_state,
        tractian_transport_state=tractian_transport_state,
    )
    install_verification_api(app)
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
