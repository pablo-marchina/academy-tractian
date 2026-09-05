from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest

from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.tool_coverage_api import attach_tool_coverage_api
from academy_tractian.tractian_campaign_evidence import (
    CampaignEvidenceLedger,
    parse_campaign_evidence_document,
)
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


def _semantic_get_company() -> CampaignEvidenceLedger:
    return parse_campaign_evidence_document(
        {
            "schema_version": "tractian-campaign-evidence-v1",
            "records": [
                {
                    "operation": "get_company",
                    "dimension": dimension,
                    "environment": "hosted_live",
                    "passed": True,
                    "observed_at": "2026-09-04T12:05:00Z",
                    "probe_id": f"semantic-{dimension}",
                    "evidence_ref": f"semantic://get_company/{dimension}",
                    "fingerprint": FINGERPRINT,
                }
                for dimension in (
                    "invalid_parameters_rejected",
                    "response_normalization_verified",
                    "agent_evaluator_behavior_verified",
                )
            ],
        },
        source_label="test:semantic",
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


def test_campaign_api_keeps_transport_and_semantic_proof_independent() -> None:
    app = FastAPI()
    attach_tool_coverage_api(
        app,
        hosted_evidence_provider=_hosted_success,
        campaign_evidence_provider=_semantic_get_company,
    )

    payload = TestClient(app).get("/api/tools/campaign").json()
    get_company = next(item for item in payload["operations"] if item["operation"] == "get_company")

    assert payload["schema_version"] == "tractian-integration-campaign-v3"
    assert payload["semantic_complete_operations"] == 1
    assert payload["transport_complete_operations"] == 0
    assert payload["complete_operations"] == 0
    assert payload["semantic_completion_status"] == "SEMANTIC_PARTIAL_1_OF_18"
    assert payload["transport_completion_status"] == "TRANSPORT_PARTIAL_0_OF_18"
    assert get_company["semantic_complete"] is True
    assert get_company["transport_complete"] is False
    assert get_company["complete"] is False


def test_tool_coverage_api_fails_closed_when_transport_evidence_provider_raises() -> None:
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


def test_campaign_api_fails_closed_when_semantic_provider_raises() -> None:
    app = FastAPI()

    def broken_semantic_provider() -> CampaignEvidenceLedger:
        raise RuntimeError("DO-NOT-LEAK-SEMANTIC-STORE-FAILURE")

    attach_tool_coverage_api(app, campaign_evidence_provider=broken_semantic_provider)
    payload = TestClient(app).get("/api/tools/campaign").json()

    assert payload["semantic_evidence_state"] == "INVALID"
    assert payload["semantic_complete_operations"] == 0
    assert payload["semantic_completion_status"] == "SEMANTIC_INVALID_EVIDENCE"
    assert "DO-NOT-LEAK-SEMANTIC-STORE-FAILURE" not in str(payload)


def test_tool_coverage_api_can_require_trusted_runtime_identity_for_both_surfaces() -> None:
    app = FastAPI()
    attach_tool_coverage_api(
        app,
        hosted_evidence_provider=_hosted_success,
        campaign_evidence_provider=_semantic_get_company,
        context_provider=_authenticated_context,
    )
    client = TestClient(app)

    for path in ("/api/tools/coverage", "/api/tools/campaign"):
        unauthenticated = client.get(path)
        assert unauthenticated.status_code == 401
        assert unauthenticated.json() == {"detail": "trusted_runtime_context_unavailable"}

    authenticated = client.get(
        "/api/tools/coverage",
        headers={"Authorization": "Bearer test-coverage-token"},
    )
    assert authenticated.status_code == 200
    assert authenticated.json()["summary"]["hosted_live_exercised"] == 1

    campaign = client.get(
        "/api/tools/campaign",
        headers={"Authorization": "Bearer test-coverage-token"},
    )
    assert campaign.status_code == 200
    assert campaign.json()["semantic_complete_operations"] == 1


def test_tool_coverage_api_rejects_double_attachment() -> None:
    app = FastAPI()
    attach_tool_coverage_api(app)
    with pytest.raises(ValueError, match="already attached"):
        attach_tool_coverage_api(app)
