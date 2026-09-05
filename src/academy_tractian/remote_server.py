from __future__ import annotations

import os

from research.e2.controller import ControllerContext, ControllerDecision, DecisionSource
from research.e2.models import BoundRequest
from research.e2.transport import RequestTransport, TransportResponse

from .production_actions_v2 import ProductionActionPrincipal
from .release_identity import load_artifact_release_identity
from .remote_production import create_remote_production_app, load_remote_production_config


class NoSelectedProviderDecisionSource(DecisionSource):
    """Fail-closed source used only while provider selection remains NO_SELECTION."""

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        raise RuntimeError("production_provider_not_selected")


class NoSelectedProviderTransport(RequestTransport):
    """Never permits a TRACTIAN/provider transport call before a production provider is promoted."""

    def request(self, _request: BoundRequest) -> TransportResponse:
        raise RuntimeError("production_provider_not_selected")


def deny_production_action_principal(*, user_id: str) -> ProductionActionPrincipal:
    """The P0 infrastructure probe does not authorize consequential actions."""

    raise PermissionError(f"production_actions_not_enabled:{user_id}")


def app_factory():
    """Uvicorn factory for the remotely deployed infrastructure-validation phase.

    The application is intentionally provider-closed. Remote infrastructure, TLS, PostgreSQL,
    RLS, SSE, restart/recovery and release identity can be evaluated without pretending that a
    hosted model has passed the separate provider-selection gates.
    """

    config = load_remote_production_config()
    artifact_release_identity = load_artifact_release_identity()
    if config.provider_calls_enabled:
        raise RuntimeError(
            "provider calls cannot be enabled by the infrastructure-probe entrypoint while provider state is NO_SELECTION"
        )
    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational")
    app = create_remote_production_app(
        config=config,
        artifact_release_identity=artifact_release_identity,
        railway_runtime_git_sha=os.environ.get("RAILWAY_GIT_COMMIT_SHA"),
        decision_source_factory=NoSelectedProviderDecisionSource,
        transport_factory=NoSelectedProviderTransport,
        authorization_resolver=deny_production_action_principal,
        schema=schema,
        max_workers=int(os.environ.get("ACADEMY_MAX_WORKERS", "4")),
        heartbeat_interval_ms=int(os.environ.get("ACADEMY_HEARTBEAT_INTERVAL_MS", "1000")),
    )
    app.state.provider_selection_state = "NO_SELECTION"
    app.state.infrastructure_probe = True
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
