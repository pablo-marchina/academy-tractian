from __future__ import annotations

from fastapi.testclient import TestClient

from research.e2.controller import ControllerDecision, ControllerDecisionKind, ControllerContext, ToolProposal
from research.e2.models import BoundRequest, Permission
from research.e2.transport import TransportResponse

from academy_tractian.action_product_api import create_action_capable_product_app
from academy_tractian.action_safety import ResourceCompanyBinding
from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.production_actions_v2 import ProductionActionPrincipal


ACTION_ARGS = {
    "analysis_id": "analysis-1",
    "body": {
        "justification": "Evidence reviewed and the operator must confirm this exact reprocessing action before execution."
    },
}


class ActionThenFinalSource:
    def __init__(self) -> None:
        self.calls = 0

    def decide(self, _context: ControllerContext) -> ControllerDecision:
        self.calls += 1
        if self.calls == 1:
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="reprocess_analysis",
                    arguments=ACTION_ARGS,
                    evidence_id="EV-action-api",
                ),
            )
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "partial",
                "message": "The consequential action is pending explicit operator confirmation.",
            },
        )


class RecordingTransport:
    def __init__(self, calls: list[BoundRequest]) -> None:
        self.calls = calls

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=202,
            headers={"content-type": "application/json"},
            body={"accepted": True},
        )


def _context(request) -> AuthenticatedRuntimeContext:
    user = request.headers.get("x-test-user", "user-1")
    return AuthenticatedRuntimeContext(identity_id=f"identity-{user}", user_id=user)


def _resolver(*, user_id: str) -> ProductionActionPrincipal:
    return ProductionActionPrincipal(
        user_id=user_id,
        user_company_id="company-1",
        permissions=frozenset({Permission.ACTION_LOW}),
        resource_company_bindings=(
            ResourceCompanyBinding(resource_id="analysis-1", company_id="company-1"),
        ),
    )


def _make_app(tmp_path, *, actions_enabled: bool, calls: list[BoundRequest]):
    return create_action_capable_product_app(
        db_path=tmp_path / "observability.duckdb",
        action_custody_path=tmp_path / "private-actions.duckdb",
        action_ledger_path=tmp_path / "action-ledger.duckdb",
        decision_source_factory=ActionThenFinalSource,
        transport_factory=lambda: RecordingTransport(calls),
        context_provider=_context,
        authorization_resolver=_resolver,
        actions_enabled=actions_enabled,
        heartbeat_interval_ms=250,
    )


def _submit_and_wait(app, client: TestClient) -> tuple[dict, dict]:
    accepted = client.post(
        "/api/runs",
        json={"user_request": "Reprocess analysis-1 if it is authorized and justified."},
    ).json()
    future = app.state.run_execution_registry.future(accepted["run_id"])
    assert future is not None
    future.result(timeout=10)
    response = client.get(f"/api/runs/{accepted['run_id']}/actions")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    return accepted, body["items"][0]


def test_action_kill_switch_default_blocks_confirmation_without_consuming_pending_action(tmp_path) -> None:
    calls: list[BoundRequest] = []
    app = _make_app(tmp_path, actions_enabled=False, calls=calls)
    with TestClient(app) as client:
        _, pending = _submit_and_wait(app, client)
        assert calls == []
        assert pending["state"] == "PENDING_CONFIRMATION"

        response = client.post(
            f"/api/actions/{pending['action_id']}/confirm",
            json={"confirm": True},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "action_kill_switch_engaged"
        assert client.get(f"/api/actions/{pending['action_id']}").json()["state"] == "PENDING_CONFIRMATION"
        assert calls == []

        health = client.get("/api/production/health").json()
        action_switch = health["measured"]["controls"]["action_kill_switch"]
        assert action_switch["engaged"] is True
        assert action_switch["actions_enabled"] is False
        assert action_switch["base_runtime_actions_enabled"] is False


def test_confirmed_action_executes_once_in_separate_realtime_evaluated_run(tmp_path) -> None:
    calls: list[BoundRequest] = []
    app = _make_app(tmp_path, actions_enabled=True, calls=calls)
    with TestClient(app) as client:
        origin, pending = _submit_and_wait(app, client)
        assert calls == []
        action_id = pending["action_id"]
        safe_serialized = str(pending)
        assert "justification" not in safe_serialized
        assert "idempotency" not in safe_serialized

        confirmation = client.post(
            f"/api/actions/{action_id}/confirm",
            json={"confirm": True},
        )
        assert confirmation.status_code == 202
        confirmed = confirmation.json()
        assert confirmed["action_id"] == action_id
        assert confirmed["execution_run_id"] != origin["run_id"]

        future = app.state.run_execution_registry.future(confirmed["execution_run_id"])
        assert future is not None
        future.result(timeout=10)
        assert app.state.run_execution_registry.status(confirmed["execution_run_id"]) == "completed"
        assert len(calls) == 1
        assert calls[0].method == "POST"
        assert calls[0].path.endswith("/analyses/analysis-1/reprocess")

        detail = client.get(f"/api/actions/{action_id}").json()
        assert detail["state"] == "ACCEPTED"
        assert detail["execution_run_id"] == confirmed["execution_run_id"]

        action_run = client.get(confirmed["run_path"]).json()
        assert action_run["completed"] is True
        assert action_run["terminal_reason_code"] == "ACTION_ACCEPTED"
        trace_events = client.get(f"/api/runs/{confirmed['execution_run_id']}/events").json()["items"]
        assert [item["event_type"] for item in trace_events] == [
            "run_started",
            "tool_proposal",
            "policy_check",
            "tool_call",
            "tool_result",
            "observation",
            "final_response",
            "run_finished",
        ]
        policy = next(item for item in trace_events if item["event_type"] == "policy_check")
        assert policy["policy_allowed"] is True
        assert policy["policy_stage"] == "B2"
        evaluation = client.get(f"/api/runs/{confirmed['execution_run_id']}/evaluation").json()
        assert evaluation["count"] > 0

        replay = client.get(f"{confirmed['stream_path']}&follow=false")
        assert replay.status_code == 200
        assert "event: trace_event" in replay.text

        duplicate = client.post(
            f"/api/actions/{action_id}/confirm",
            json={"confirm": True},
        )
        assert duplicate.status_code == 409
        assert len(calls) == 1


def test_confirmation_payload_cannot_supply_tool_arguments_or_authorization(tmp_path) -> None:
    calls: list[BoundRequest] = []
    app = _make_app(tmp_path, actions_enabled=True, calls=calls)
    with TestClient(app) as client:
        _, pending = _submit_and_wait(app, client)
        response = client.post(
            f"/api/actions/{pending['action_id']}/confirm",
            json={
                "confirm": True,
                "arguments": {"analysis_id": "attacker-controlled"},
                "user_permissions": ["action_high"],
                "idempotency_key": "browser-controlled",
            },
        )
        assert response.status_code == 422
        assert calls == []
        assert client.get(f"/api/actions/{pending['action_id']}").json()["state"] == "PENDING_CONFIRMATION"


def test_other_requester_cannot_discover_or_confirm_action(tmp_path) -> None:
    calls: list[BoundRequest] = []
    app = _make_app(tmp_path, actions_enabled=True, calls=calls)
    with TestClient(app) as client:
        _, pending = _submit_and_wait(app, client)
        headers = {"x-test-user": "user-2"}
        detail = client.get(f"/api/actions/{pending['action_id']}", headers=headers)
        confirm = client.post(
            f"/api/actions/{pending['action_id']}/confirm",
            headers=headers,
            json={"confirm": True},
        )
        assert detail.status_code == 404
        assert confirm.status_code == 404
        assert calls == []


def test_safe_pending_action_list_never_serializes_private_custody_payload(tmp_path) -> None:
    calls: list[BoundRequest] = []
    app = _make_app(tmp_path, actions_enabled=False, calls=calls)
    with TestClient(app) as client:
        origin, _ = _submit_and_wait(app, client)
        text = client.get(f"/api/runs/{origin['run_id']}/actions").text.lower()
        for forbidden in (
            "operator must confirm this exact",
            "identity-user-1",
            "idem-",
            "company-1",
        ):
            assert forbidden not in text
