from __future__ import annotations

import json
from threading import Event

from fastapi.testclient import TestClient

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    ToolProposal,
)
from research.e2.models import BoundRequest
from research.e2.transport import TransportResponse

from academy_tractian.product_api import (
    AuthenticatedRuntimeContext,
    create_product_app,
)
from academy_tractian.realtime_runtime import RealtimeProductionRuntime


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[BoundRequest] = []

    def request(self, request: BoundRequest) -> TransportResponse:
        self.calls.append(request)
        return TransportResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body={"asset_id": "asset-1", "status": "ok"},
        )


class BlockingToolThenFinalSource:
    def __init__(self, *, entered: Event, release: Event) -> None:
        self.entered = entered
        self.release = release
        self.calls = 0

    def decide(self, context: ControllerContext) -> ControllerDecision:
        self.calls += 1
        if self.calls == 1:
            self.entered.set()
            if not self.release.wait(timeout=10):
                raise RuntimeError("test decision source release timeout")
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=ToolProposal(
                    tool_name="get_asset",
                    arguments={"asset_id": "asset-1"},
                    evidence_id="EV-product-asset",
                ),
            )
        return ControllerDecision(
            kind=ControllerDecisionKind.FINAL,
            final={
                "decision": "ORIENT",
                "response_mode": "complete",
                "message": "Product API completed the real runtime path.",
            },
        )


def _sse_data_payloads(text: str) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for line in text.splitlines():
        if line.startswith("data: "):
            payloads.append(json.loads(line.removeprefix("data: ")))
    return payloads


def test_post_run_persists_real_start_before_background_execution_and_evaluates_after(tmp_path) -> None:
    entered = Event()
    release = Event()
    transports: list[FakeTransport] = []

    def context_provider(_request) -> AuthenticatedRuntimeContext:
        return AuthenticatedRuntimeContext(
            identity_id="server-owned-identity",
            user_id="server-owned-user",
            seed="server-owned-seed",
        )

    def runtime_factory(sink) -> RealtimeProductionRuntime:
        transport = FakeTransport()
        transports.append(transport)
        return RealtimeProductionRuntime(
            decision_source=BlockingToolThenFinalSource(
                entered=entered,
                release=release,
            ),
            transport=transport,
            observability_sink=sink,
        )

    app = create_product_app(
        db_path=tmp_path / "product.duckdb",
        runtime_factory=runtime_factory,
        context_provider=context_provider,
        max_workers=2,
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            json={"user_request": "Inspect asset-1 and summarize the evidence."},
        )
        assert response.status_code == 202
        accepted = response.json()
        run_id = accepted["run_id"]
        assert run_id.startswith("run_")
        assert "server-owned" not in json.dumps(accepted)
        assert entered.wait(timeout=5), "background runtime never entered decision source"

        # Decision source is blocked, so only the genuine run_started event may exist.
        run_before = client.get(accepted["run_path"])
        assert run_before.status_code == 200
        assert run_before.json()["completed"] is False
        assert run_before.json()["event_count"] == 1
        events_before = client.get(f"/api/runs/{run_id}/events").json()["items"]
        assert [item["event_type"] for item in events_before] == ["run_started"]

        replay_before = client.get(
            f"{accepted['stream_path']}&follow=false"
        )
        assert replay_before.status_code == 200
        assert replay_before.text.count("event: trace_event") == 1
        replay_payloads = _sse_data_payloads(replay_before.text)
        assert [item["event_type"] for item in replay_payloads] == ["run_started"]
        assert all(item["event_type"] != "tool_call" for item in replay_payloads)
        assert all(item["event_type"] != "final_response" for item in replay_payloads)

        execution_before = client.get(accepted["execution_path"])
        assert execution_before.status_code == 200
        assert execution_before.json()["status"] in {"accepted", "running"}

        release.set()
        future = app.state.run_execution_registry.future(run_id)
        assert future is not None
        future.result(timeout=10)

        execution_after = client.get(accepted["execution_path"])
        assert execution_after.json()["status"] == "completed"
        run_after = client.get(accepted["run_path"]).json()
        assert run_after["completed"] is True
        assert run_after["terminal_decision"] == "ORIENT"
        assert run_after["terminal_message"] == "Product API completed the real runtime path."

        events_after = client.get(f"/api/runs/{run_id}/events").json()["items"]
        assert events_after[-1]["event_type"] == "run_finished"
        assert any(item["event_type"] == "tool_call" for item in events_after)
        assert any(item["event_type"] == "observation" for item in events_after)
        assert len(transports) == 1
        assert len(transports[0].calls) == 1

        evaluation = client.get(f"/api/runs/{run_id}/evaluation")
        assert evaluation.status_code == 200
        assert evaluation.json()["count"] > 0

        serialized = json.dumps(
            {
                "run": run_after,
                "events": events_after,
                "evaluation": evaluation.json(),
            },
            sort_keys=True,
        )
        assert "server-owned-identity" not in serialized
        assert "server-owned-user" not in serialized
        assert "server-owned-seed" not in serialized


def test_browser_cannot_submit_identity_or_seed_fields(tmp_path) -> None:
    def context_provider(_request) -> AuthenticatedRuntimeContext:
        return AuthenticatedRuntimeContext(identity_id="identity", user_id="user")

    def runtime_factory(sink) -> RealtimeProductionRuntime:
        return RealtimeProductionRuntime(
            decision_source=BlockingToolThenFinalSource(entered=Event(), release=Event()),
            transport=FakeTransport(),
            observability_sink=sink,
        )

    app = create_product_app(
        db_path=tmp_path / "product.duckdb",
        runtime_factory=runtime_factory,
        context_provider=context_provider,
    )
    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            json={
                "user_request": "Inspect asset-1.",
                "user_id": "attacker-controlled-user",
                "identity_id": "attacker-controlled-identity",
                "seed": "favorable-seed",
            },
        )
        assert response.status_code == 422


def test_context_provider_failure_is_generic_401(tmp_path) -> None:
    def context_provider(_request):
        raise RuntimeError("private authentication backend detail")

    def runtime_factory(sink) -> RealtimeProductionRuntime:
        raise AssertionError("runtime must not be constructed without trusted context")

    app = create_product_app(
        db_path=tmp_path / "product.duckdb",
        runtime_factory=runtime_factory,
        context_provider=context_provider,
    )
    with TestClient(app) as client:
        response = client.post("/api/runs", json={"user_request": "Inspect asset."})
        assert response.status_code == 401
        assert response.json()["detail"] == "trusted_runtime_context_unavailable"
        assert "private authentication backend detail" not in response.text
