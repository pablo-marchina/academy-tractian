from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from academy_tractian.verification_api import install_verification_api


class _AccessPolicy:
    def authorize_run(self, request, run_id: str) -> None:
        if request.headers.get("x-test-user") != "owner" or run_id != "run_good":
            raise HTTPException(status_code=404, detail="run_not_found")


class _Store:
    def get_run(self, run_id: str):
        if run_id != "run_good":
            return None
        return {"run_id": run_id, "completed": True, "terminal_reason_code": None, "terminal_response_mode": "complete"}

    def get_events(self, run_id: str):
        assert run_id == "run_good"
        return [
            {"event_type": "run_started"},
            {"event_type": "tool_result", "tool_name": "get_current_user", "status_code": 200},
            {"event_type": "run_finished"},
        ]

    def get_evaluation(self, run_id: str):
        assert run_id == "run_good"
        return [
            {"check_name": "trace_lifecycle", "passed": True, "blocking": True},
            {"check_name": "production_trace_identity", "passed": True, "blocking": True},
            {"check_name": "proposal_contract_validity", "passed": True, "blocking": True},
            {"check_name": "identity_seed_model_isolation", "passed": True, "blocking": True},
            {"check_name": "execution_chain_integrity", "passed": True, "blocking": True},
            {"check_name": "policy_denial_containment", "passed": True, "blocking": True},
        ]


def _app() -> FastAPI:
    app = FastAPI()
    app.state.observability_store = _Store()
    app.state.product_access_policy = _AccessPolicy()
    install_verification_api(app)
    return app


def test_verification_endpoint_never_upgrades_structural_green_to_task_success() -> None:
    response = TestClient(_app()).get("/api/runs/run_good/verification", headers={"x-test-user": "owner"})
    assert response.status_code == 200
    body = response.json()
    assert body["overall_status"] == "NOT_VERIFIED"
    by_name = {item["name"]: item for item in body["dimensions"]}
    assert by_name["runtime_integrity"]["status"] == "VERIFIED"
    assert by_name["functional_success"]["status"] == "NOT_VERIFIED"
    assert by_name["evidence_sufficiency"]["status"] == "NOT_VERIFIED"


def test_verification_endpoint_preserves_run_authorization_boundary() -> None:
    response = TestClient(_app()).get("/api/runs/run_good/verification")
    assert response.status_code == 404
