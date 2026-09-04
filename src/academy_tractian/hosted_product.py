from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .hosted_config import HostedProductConfig
from .hosted_integration_evidence_recorder import (
    EvidenceRecordingTractianTransport,
    HostedIntegrationEvidenceRecorder,
)
from .hosted_provider import (
    create_hosted_decision_source,
    hosted_runtime_configuration_identity,
)
from .hosted_tractian_transport import HostedTractianTransport
from .oidc_runtime_identity import OIDCClaimMapping, OIDCRuntimeContextProvider
from .postgres_campaign_evidence_store import PostgresCampaignEvidenceStore
from .postgres_product_api import create_postgres_action_capable_product_app
from .production_actions_v2 import ProductionActionPrincipal
from .runtime_identity import SignedBearerRuntimeContextProvider
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


def _runtime_context_provider(config: HostedProductConfig):
    if config.identity_backend == "oidc":
        if config.oidc_jwks_url is None or not config.oidc_algorithms:
            raise ValueError("hosted_oidc_configuration_incomplete")
        return OIDCRuntimeContextProvider(
            issuer=config.runtime_identity_issuer,
            audience=config.runtime_identity_audience,
            jwks_url=config.oidc_jwks_url,
            algorithms=config.oidc_algorithms,
            claim_mapping=OIDCClaimMapping(
                organization_claim=config.oidc_organization_claim,
                role_claim=config.oidc_role_claim,
                permissions_claim=config.oidc_permissions_claim,
                identity_claim=config.oidc_identity_claim,
            ),
            allowed_claim_permissions=(),
            allowed_privileged_permissions=(),
            authorized_parties=config.oidc_authorized_parties,
        )

    if not config.runtime_identity_secret:
        raise ValueError("hosted_signed_bearer_secret_missing")
    return SignedBearerRuntimeContextProvider(
        secret=config.runtime_identity_secret,
        issuer=config.runtime_identity_issuer,
        audience=config.runtime_identity_audience,
    )


def build_hosted_product(config: HostedProductConfig | None = None) -> FastAPI:
    """Build the hosted-only product path from fail-closed environment configuration."""

    active = config or HostedProductConfig.from_environment(require_serving_ready=True)
    active.assert_serving_ready()
    assert active.provider is not None
    assert active.model is not None
    assert active.provider_api_key is not None
    assert active.tractian_base_url is not None

    live_evidence = HostedIntegrationEvidenceRecorder()
    runtime_configuration_identity = hosted_runtime_configuration_identity(
        active.provider,
        active.model,
    )

    def decision_source_factory():
        return create_hosted_decision_source(
            provider=active.provider or "",
            model=active.model or "",
            api_key=active.provider_api_key or "",
        )

    def transport_factory():
        transport = HostedTractianTransport(
            base_url=active.tractian_base_url or "",
            bearer_token=active.tractian_bearer_token,
        )
        return EvidenceRecordingTractianTransport(transport, live_evidence)

    context_provider = _runtime_context_provider(active)
    app = create_postgres_action_capable_product_app(
        db_path=_UNUSED_LOCAL_STATE_PATH,
        internal_dsn=active.postgres_internal_dsn,
        scoped_dsn=active.postgres_scoped_dsn,
        decision_source_factory=decision_source_factory,
        transport_factory=transport_factory,
        context_provider=context_provider,
        authorization_resolver=_deny_unqualified_hosted_actions,
        schema=active.postgres_schema,
        observability_schema=active.observability_schema,
        observability_backend="postgresql",
        initialize_schema=False,
        max_workers=active.max_workers,
        provider_calls_enabled=True,
        actions_enabled=False,
        heartbeat_interval_ms=active.heartbeat_interval_ms,
        runtime_configuration_identity=runtime_configuration_identity,
    )
    persistent_evidence = app.state.tractian_integration_evidence_store
    if persistent_evidence is None:
        raise RuntimeError("hosted_postgres_integration_evidence_store_missing")
    live_evidence.attach_persistent_store(persistent_evidence)

    campaign_evidence_store = PostgresCampaignEvidenceStore(
        app.state.postgres_operational_database,
        schema=active.observability_schema,
        initialize=False,
    )
    if not campaign_evidence_store.ready():
        raise RuntimeError("hosted_postgres_campaign_evidence_store_missing")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(active.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Last-Event-ID"],
        expose_headers=["Content-Type"],
        max_age=600,
    )
    attach_tool_coverage_api(
        app,
        hosted_evidence_provider=live_evidence.ledger,
        campaign_evidence_provider=campaign_evidence_store.ledger,
        context_provider=context_provider,
    )
    app.state.hosted_config = active.sanitized_summary()
    app.state.runtime_identity_backend = (
        "oidc-jwks-v1" if active.identity_backend == "oidc" else "signed-bearer-hmac-sha256-v1"
    )
    app.state.runtime_identity_issuer = active.runtime_identity_issuer
    app.state.runtime_identity_audience = active.runtime_identity_audience
    app.state.hosted_candidate_id = runtime_configuration_identity.candidate_id
    app.state.hosted_runtime_config_identity = runtime_configuration_identity.model_dump(mode="json")
    app.state.hosted_actions_qualified = False
    app.state.hosted_action_block_reason = "RESOURCE_AUTHORIZATION_NOT_YET_QUALIFIED"
    app.state.hosted_local_persistent_state_required = False
    app.state.tractian_live_evidence_recorder = live_evidence
    app.state.tractian_live_evidence_persistence = "managed-postgresql-bounded-safe-metadata"
    app.state.tractian_campaign_evidence_store = campaign_evidence_store
    app.state.tractian_campaign_evidence_persistence = "managed-postgresql-bounded-semantic-proof"
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
