from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI, Request

from .product_api import RuntimeContextProvider, trusted_runtime_context
from .tool_coverage import build_tractian_tool_coverage
from .tractian_integration_evidence import IntegrationEvidenceLedger


HostedEvidenceProvider = Callable[[], IntegrationEvidenceLedger]


def attach_tool_coverage_api(
    app: FastAPI,
    *,
    hosted_evidence_provider: HostedEvidenceProvider | None = None,
    context_provider: RuntimeContextProvider | None = None,
) -> None:
    """Attach the evidence-bounded TRACTIAN tool-coverage surface once.

    The generic helper may remain unauthenticated for isolated provider-free tests.
    Hosted production supplies ``context_provider`` so infrastructure/evidence state
    is never exposed to an unauthenticated browser.
    """

    if any(getattr(route, "path", None) == "/api/tools/coverage" for route in app.routes):
        raise ValueError("tool coverage API is already attached")

    @app.get("/api/tools/coverage")
    def tool_coverage(request: Request) -> dict[str, object]:
        if context_provider is not None:
            trusted_runtime_context(context_provider, request)

        hosted_evidence: IntegrationEvidenceLedger | None = None
        if hosted_evidence_provider is not None:
            try:
                hosted_evidence = hosted_evidence_provider()
            except Exception:
                # Evidence availability must never fail open or inflate a claim.
                # Keep the public error bounded: do not expose exception text.
                hosted_evidence = IntegrationEvidenceLedger(
                    source_label="hosted_live:provider",
                    state="INVALID",
                    validation_errors=("provider:evidence_unavailable",),
                )
        return build_tractian_tool_coverage(hosted_evidence=hosted_evidence)
