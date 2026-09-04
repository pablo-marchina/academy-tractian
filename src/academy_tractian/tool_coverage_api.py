from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI, Request

from .product_api import RuntimeContextProvider, trusted_runtime_context
from .tool_coverage import build_tractian_tool_coverage
from .tractian_integration_campaign import build_tractian_integration_campaign_report
from .tractian_integration_evidence import IntegrationEvidenceLedger


HostedEvidenceProvider = Callable[[], IntegrationEvidenceLedger]


def attach_tool_coverage_api(
    app: FastAPI,
    *,
    hosted_evidence_provider: HostedEvidenceProvider | None = None,
    context_provider: RuntimeContextProvider | None = None,
) -> None:
    """Attach authenticated, evidence-bounded TRACTIAN integration surfaces once."""

    protected_paths = {"/api/tools/coverage", "/api/tools/campaign"}
    if any(getattr(route, "path", None) in protected_paths for route in app.routes):
        raise ValueError("tool coverage API is already attached")

    def hosted_evidence() -> IntegrationEvidenceLedger | None:
        if hosted_evidence_provider is None:
            return None
        try:
            return hosted_evidence_provider()
        except Exception:
            # Evidence availability must never fail open or inflate a claim.
            # Keep the public error bounded: do not expose exception text.
            return IntegrationEvidenceLedger(
                source_label="hosted_live:provider",
                state="INVALID",
                validation_errors=("provider:evidence_unavailable",),
            )

    def authorize(request: Request) -> None:
        if context_provider is not None:
            trusted_runtime_context(context_provider, request)

    @app.get("/api/tools/coverage")
    def tool_coverage(request: Request) -> dict[str, object]:
        authorize(request)
        return build_tractian_tool_coverage(hosted_evidence=hosted_evidence())

    @app.get("/api/tools/campaign")
    def tool_campaign(request: Request) -> dict[str, object]:
        authorize(request)
        report = build_tractian_integration_campaign_report(
            hosted_evidence=hosted_evidence()
        )
        return report.model_dump(mode="json")
