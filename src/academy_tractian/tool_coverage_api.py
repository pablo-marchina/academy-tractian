from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI

from .tool_coverage import build_tractian_tool_coverage
from .tractian_integration_evidence import IntegrationEvidenceLedger


HostedEvidenceProvider = Callable[[], IntegrationEvidenceLedger]


def attach_tool_coverage_api(
    app: FastAPI,
    *,
    hosted_evidence_provider: HostedEvidenceProvider | None = None,
) -> None:
    """Attach the public, evidence-bounded TRACTIAN tool-coverage surface once."""

    if any(getattr(route, "path", None) == "/api/tools/coverage" for route in app.routes):
        raise ValueError("tool coverage API is already attached")

    @app.get("/api/tools/coverage")
    def tool_coverage() -> dict[str, object]:
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
