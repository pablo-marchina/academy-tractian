from __future__ import annotations

import os
from pathlib import Path

from fastapi import Request

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    DecisionSource,
    ToolProposal,
)
from research.e2.models import BoundRequest, Permission
from research.e2.transport import RequestTransport, TransportResponse

from .action_safety import ResourceCompanyBinding
from .postgres_product_api import create_postgres_action_capable_product_app
from .product_api import AuthenticatedRuntimeContext
from .production_actions_v2 import ProductionActionPrincipal


class ProviderFreeScenarioDecisionSource(DecisionSource):
    """Deterministic acceptance source over the real production controller/tool boundary.

    Scenario selection is encoded in the user request solely for browser acceptance. The source
    never receives identity, tenant, seed, action custody, evaluator truth or raw transport state.
    Runtime, tool binding, policy, persistence, SSE and evaluation remain the production path.
    """

    def decide(self, context: ControllerContext) -> ControllerDecision:
        request = context.user_request.lower()

        if "scenario:clarify" in request:
            return ControllerDecision(
                kind=ControllerDecisionKind.CLARIFY,
                reason_code="E2E_INFORMATION_REQUIRED",
                message="Please provide the missing asset identifier before investigation continues.",
            )
        if "scenario:escalate" in request:
            return ControllerDecision(
                kind=ControllerDecisionKind.ESCALATE,
                reason_code="E2E_AMBIGUOUS_EVIDENCE",
                message="Collected evidence remains contradictory; an engineer should continue the investigation.",
            )
        if "scenario:abstain" in request:
            return ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                reason_code="E2E_EVIDENCE_UNAVAILABLE",
                message="Required evidence is unavailable, so no autonomous conclusion is safe.",
            )

        if not context.observations:
            if "scenario:pending-action" in request:
                return ControllerDecision(
                    kind=ControllerDecisionKind.TOOL,
                    proposal=ToolProposal(
                        tool_name="reprocess_analysis",
                        arguments={
                            "analysis_id": "analysis-e2e",
                            "body": {
                                "justification": "Verified evidence requires this exact reprocessing action after operator confirmation."
                            },
                        },
                        evidence_id="EV-e2e-action-proposal",
                    ),
                )
            if "scenario:blocked-action" in request:
                return ControllerDecision(
                    kind=ControllerDecisionKind.TOOL,
                    proposal=ToolProposal(
                        tool_name="update_asset_config",
                        arguments={
                            "asset_id": "asset-e2e",
                            "body": {
                                "justification": "Attempt a high-impact configuration change to prove deterministic permission blocking."
                            },
                        },
                        evidence_id="EV-e2e-blocked-action",
                    ),
                )
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={
                        "asset_id": "asset-error" if "scenario:tool-error" in request else "asset-e2e"
                    },
                    evidence_id="EV-e2e-asset",
                ),
            )

        observation = context.observations[-1]
        if "scenario:pending-action" in request:
            return ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final={
                    "decision": "ORIENT",
                    "response_mode": "partial",
                    "reason_code": "ACTION_CONFIRMATION_REQUIRED",
                    "message": "The exact consequential action is pending explicit operator confirmation.",
                },
            )
        if "scenario:blocked-action" in request:
            return ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                reason_code=observation.blocked_code or "ACTION_BLOCKED",
                message="The high-impact action was blocked by the deterministic safety policy.",
            )
        if observation.status != "success":
            return ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                reason_code=observation.error_code or "TOOL_UNAVAILABLE",
                message="The evidence tool failed; the agent will not invent a conclusion.",
            )
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "reason_code": "E2E_EVIDENCE_CONFIRMED",
                "message": "Asset evidence was inspected through the production tool boundary and supports a safe conclusion.",
            },
        )


class ProviderFreeTransport(RequestTransport):
    """Local deterministic dependency substitute; never presented as a TRACTIAN live call."""

    def request(self, request: BoundRequest) -> TransportResponse:
        if request.path == "/assets/asset-error":
            return TransportResponse(
                status_code=503,
                headers={"content-type": "application/json"},
                body={"error": "provider_free_dependency_unavailable"},
            )
        if request.path == "/assets/asset-e2e" and request.method == "GET":
            return TransportResponse(
                status_code=200,
                headers={"content-type": "application/json"},
                body={
                    "assetId": "asset-e2e",
                    "companyId": "company-e2e",
                    "status": "monitored",
                    "anomalyState": "stable",
                    "source": "provider-free-acceptance-profile",
                },
            )
        if request.path == "/analyses/analysis-e2e/reprocess" and request.method == "POST":
            return TransportResponse(
                status_code=202,
                headers={"content-type": "application/json"},
                body={"accepted": True, "operation": "reprocessAnalysis"},
            )
        return TransportResponse(
            status_code=404,
            headers={"content-type": "application/json"},
            body={"error": "provider_free_route_not_defined"},
        )


def provider_free_runtime_context(request: Request) -> AuthenticatedRuntimeContext:
    user_id = request.headers.get("x-e2e-user", "e2e-user-a")
    organization_id = request.headers.get("x-e2e-organization", "e2e-org-a")
    return AuthenticatedRuntimeContext(
        organization_id=organization_id,
        identity_id=f"identity:{organization_id}:{user_id}",
        user_id=user_id,
        role="operator",
        seed="provider-free-e2e-seed",
    )


def provider_free_action_principal(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-e2e",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="analysis-e2e", company_id="company-e2e"),
            ResourceCompanyBinding(resource_id="asset-e2e", company_id="company-e2e"),
        ),
    )


def build_provider_free_product():
    internal_dsn = os.environ["ACADEMY_POSTGRES_INTERNAL_DSN"]
    scoped_dsn = os.environ["ACADEMY_POSTGRES_SCOPED_DSN"]
    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_e2e")
    db_path = Path(os.environ.get("ACADEMY_OBSERVABILITY_DB", ".runtime/provider-free-e2e.duckdb"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_postgres_action_capable_product_app(
        db_path=db_path,
        internal_dsn=internal_dsn,
        scoped_dsn=scoped_dsn,
        schema=schema,
        initialize_schema=os.environ.get("ACADEMY_INITIALIZE_SCHEMA", "0") == "1",
        decision_source_factory=ProviderFreeScenarioDecisionSource,
        transport_factory=ProviderFreeTransport,
        context_provider=provider_free_runtime_context,
        authorization_resolver=provider_free_action_principal,
        actions_enabled=True,
        provider_calls_enabled=True,
        max_workers=8,
        heartbeat_interval_ms=250,
    )


def main() -> None:
    import uvicorn

    uvicorn.run(
        build_provider_free_product(),
        host=os.environ.get("ACADEMY_HOST", "127.0.0.1"),
        port=int(os.environ.get("ACADEMY_PORT", "8000")),
        log_level=os.environ.get("ACADEMY_LOG_LEVEL", "warning"),
    )


if __name__ == "__main__":
    main()
