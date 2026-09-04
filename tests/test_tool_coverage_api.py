from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest

from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.tool_coverage_api import attach_tool_coverage_api
from academy_tractian.tractian_integration_evidence import (
    IntegrationEvidenceLedger,
    parse_integration_evidence_document,
)


FINGERPRINT = "sha256:" + ("c" * 64)


def _hosted_success() -> IntegrationEvidenceLedger:
    return parse_integration_evidence_document(
        {
            "schema_version": "tractian-integration-evidence-v1",
            "records": [
                {
                    "operation": "get_company",
                    "environment": "hosted_live",
                    "outcome": "success",
                    "method": "GET",
                    "path_template": "/companies/{companyId}",
                    "observed_at": "2026-09-04T12:00:00Z",
                    "probe_id": "api-test",
                    "evidence_ref": "api-test-observation",
                    "fingerprint": FINGERPRINT,
                    "http_status": 200,
                }
            ],
        },
        source_label="test:hosted",
        expected_environment="hosted_live",
    )


def _authenticated_context(request: Request) -> AuthenticatedRuntimeContext:
    if request.headers.get("authorization") != "Bearer test-coverage-token":
        raise ValueError("missing trusted test identity")
    return AuthenticatedRuntimeContext(
        organization_id="org-test",
        identity_id="identity-test",
        user_id="user-test",
    )


def test_tool_coverage_api_exposes_evidence_bounded_matrix() -> None:
    app = FastAPI()
    attach_tool_coverage_api(app)

    response = TestClient(app).get("/api/tools/coverage")
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["normalized_operations"] == 18
    assert payload["summary"]["integrated_route_execution_evidenced"] == 1
    assert payload["summary"]["hosted_live_exercised"] == 0
    assert payload["summary"]["hosted_live_success"] == 0
    assert payload["status"] == "PARTIAL_INTEGRATED_ROUTE_EVIDENCE"


def test_tool_coverage_api_reads_injected_hosted_evidence_provider() -> None:
    app = FastAPI()
    attach_tool_coverage_api(app, hosted_evidence_provider=_hosted_success)

    payload = TestClient(app).get("/api/tools/coverage").json()

    assert payload["status"] == "PARTIAL_HOSTED_LIVE_EVIDENCE"
    assert payload["summary"]["hosted_live_exercised"] == 1
    assert payload["summary"]["hosted_live_success"] == 1
    assert payload["summary"]["integrated_route_execution_evidenced"] == 2


def test_tool_coverage_api_fails_closed_when_evidence_provider_raises() -> None:
    app = FastAPI()

    def broken_provider() -> IntegrationEvidenceLedger:
        raise RuntimeError("SUPER-SECRET-PROVIDER-FAILURE")

    attach_tool_coverage_api(app, hosted_evidence_provider=broken_provider)
    payload = TestClient(app).get("/api/tools/coverage").json()

    assert payload["status"] == "EVIDENCE_INVALID_FAIL_CLOSED"
    assert payload["summary"]["hosted_live_exercised"] == 0
    assert payload["evidence"]["hosted_live"]["validation_errors"] == [
        "provider:evidence_unavailable"
    ]
    assert "SUPER-SECRET-PROVIDER-FAILURE" not in str(payload)


def test_tool_coverage_api_can_require_trusted_runtime_identity() -> None:
    app = FastAPI()
    attach_tool_coverage_api(
        app,
        hosted_evidence_provider=_hosted_success,
        context_provider=_authenticated_context,
    )
    client = TestClient(app)

    unauthenticated = client.get("/api/tools/coverage")
    assert unauthenticated.status_code == 401
    assert unauthenticated.json() == {"detail": "trusted_runtime_context_unavailable"}

    authenticated = client.get(
        "/api/tools/coverage",
        headers={"Authorization": "Bearer test-coverage-token"},
    )
    assert authenticated.status_code == 200
    assert authenticated.json()["summary"]["hosted_live_exercised"] == 1


def test_tool_coverage_api_rejects_double_attachment() -> None:
    app = FastAPI()
    attach_tool_coverage_api(app)
    with pytest.raises(ValueError, match="already attached"):
        attach_tool_coverage_api(app)
