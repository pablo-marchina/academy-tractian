from __future__ import annotations

from fastapi import FastAPI

from .tool_coverage import build_tractian_tool_coverage


def attach_tool_coverage_api(app: FastAPI) -> None:
    """Attach the public, evidence-bounded TRACTIAN tool-coverage surface once."""

    if any(getattr(route, "path", None) == "/api/tools/coverage" for route in app.routes):
        raise ValueError("tool coverage API is already attached")

    @app.get("/api/tools/coverage")
    def tool_coverage() -> dict[str, object]:
        return build_tractian_tool_coverage()
