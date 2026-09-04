from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from academy_tractian.tool_coverage_api import attach_tool_coverage_api


def test_tool_coverage_api_exposes_evidence_bounded_matrix() -> None:
    app = FastAPI()
    attach_tool_coverage_api(app)

    response = TestClient(app).get("/api/tools/coverage")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["normalized_operations"] == 18
    assert payload["summary"]["integrated_route_execution_evidenced"] == 1
    assert payload["status"] == "PARTIAL_INTEGRATED_ROUTE_EVIDENCE"


def test_tool_coverage_api_rejects_double_attachment() -> None:
    app = FastAPI()
    attach_tool_coverage_api(app)
    with pytest.raises(ValueError, match="already attached"):
        attach_tool_coverage_api(app)
