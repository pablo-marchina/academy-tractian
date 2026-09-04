from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .authenticated_postgres_product_api import (
    create_authenticated_postgres_action_capable_product_app,
)
from .hosted_config import HostedProductConfig
from .hosted_provider import create_hosted_decision_source
from .hosted_tractian_transport import HostedTractianTransport
from .production_actions_v2 import ProductionActionPrincipal
from .tool_coverage_api import attach_tool_coverage_api


# The hosted Postgres topology injects every persistent store, so this path is intentionally never
# created. Keeping the argument makes the hosted entrypoint compatible with the frozen product
# factory while the regression test proves no DuckDB file appears.
_UNUSED_LOCAL_STATE_PATH = Path("/tmp/academy-tractian-hosted-unused.duckdb")


def _deny_unqualified_hosted_actions(*, user_id: str) -> ProductionActionPrincipal:
    """Fail closed until hosted resource/company authorization has independent evidence."""

    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="hosted-unbound-company",
        permissions=frozenset(),
        resource_company_bindings=(),
    )


def build_hosted_product(config: HostedProductConfig | None = None) -> FastAPI:
    """Build the hosted-only product path from fail-closed environment configuration."""

    active = config or HostedProductConfig.from_environment(require_serving_ready=True)
    active.assert_serving_ready()
    assert active.provider is not None
    assert active.provider_api_key is not None
    assert active.tractian_base_url is not None

    def decision_source_factory():
        return create_hosted_decision_source(
            provider=active.provider or "",
            api_key=active.provider_api_key or "",
        )

    def transport_factory():
        return HostedTractianTransport(
            base_url=active.tractian_base_url or "",
            bearer_token=active.tractian_bearer_token,
        )

    app = create_authenticated_postgres_action_capable_product_app(
        db_path=_UNUSED_LOCAL_STATE_PATH,
        internal_dsn=active.postgres_internal_dsn,
        scoped_dsn=active.postgres_scoped_dsn,
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        authorization_resolver=_deny_unqualified_hosted_actions,
        runtime_identity_secret=active.runtime_identity_secret,
        runtime_identity_issuer=active.runtime_identity_issuer,
        runtime_identity_audience=active.runtime_identity_audience,
        schema=active.postgres_schema,
        observability_schema=active.observability_schema,
        observability_backend="postgresql",
        initialize_schema=False,
        max_workers=active.max_workers,
        provider_calls_enabled=True,
        actions_enabled=False,
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
    attach_tool_coverage_api(app)
    app.state.hosted_config = active.sanitized_summary()
    app.state.hosted_actions_qualified = False
    app.state.hosted_action_block_reason = "RESOURCE_AUTHORIZATION_NOT_YET_QUALIFIED"
    app.state.hosted_local_persistent_state_required = False
    return app


def main() -> None:
    import uvicorn

    uvicorn.run(
        build_hosted_product(),
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
