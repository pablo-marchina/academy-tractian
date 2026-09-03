from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from academy_tractian.operational_value_collection import (
    HostMonotonicPilotTimerRegistry,
    OPERATIONAL_VALUE_PARTICIPATE_PERMISSION,
    PilotAssignmentRecord,
    attach_operational_value_collection_api,
)
from academy_tractian.operational_value_pilot import (
    OperationalPilotCompletion,
    OperationalPilotTask,
)
from academy_tractian.product_api import AuthenticatedRuntimeContext


PACKET_ID = "ovpkt_" + "a" * 24
TASK_ID = "ovt_" + "b" * 24
PAIR_ID = "ovpair_" + "c" * 24
ASSIGNMENT_ID = "ova_" + "d" * 24
OPERATOR_REF = "e" * 64


class ControlledClock:
    def __init__(self, value: float) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


class FakeStore:
    def __init__(self) -> None:
        self.active: PilotAssignmentRecord | None = None
        self.completed: OperationalPilotCompletion | None = None
        self.reconciled_session: str | None = None
        self.failure_reason: str | None = None

    def reconcile_active_host_session(self, host_session_id: str) -> tuple[str, ...]:
        self.reconciled_session = host_session_id
        if self.active is not None and self.active.host_session_id != host_session_id:
            assignment_id = self.active.assignment_id
            self.active = None
            return (assignment_id,)
        return ()

    def get_active_for_user(self, *, organization_id: str, user_id: str):
        if (
            self.active is not None
            and self.active.organization_id == organization_id
            and self.active.user_id == user_id
        ):
            return self.active
        return None

    def assign_next(
        self,
        *,
        organization_id: str,
        user_id: str,
        operator_ref_sha256: str,
        host_session_id: str,
    ):
        del operator_ref_sha256
        if self.active is not None or self.completed is not None:
            return None
        self.active = PilotAssignmentRecord(
            assignment_id=ASSIGNMENT_ID,
            organization_id=organization_id,
            packet_id=PACKET_ID,
            task=OperationalPilotTask(
                task_id=TASK_ID,
                condition="MANUAL",
                ticket_request="Investigate the customer ticket and record the operational conclusion.",
            ),
            pair_id=PAIR_ID,
            user_id=user_id,
            operator_ref_sha256=OPERATOR_REF,
            host_session_id=host_session_id,
        )
        return self.active

    def fail_active(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        reason: str,
    ) -> bool:
        if (
            self.active is None
            or self.active.assignment_id != assignment_id
            or self.active.organization_id != organization_id
            or self.active.user_id != user_id
        ):
            return False
        self.failure_reason = reason
        self.active = None
        return True

    def complete_valid(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        elapsed_seconds: float,
        terminal_decision: str,
        conclusion_summary: str,
    ) -> OperationalPilotCompletion:
        if (
            self.active is None
            or self.active.assignment_id != assignment_id
            or self.active.organization_id != organization_id
            or self.active.user_id != user_id
        ):
            raise KeyError(assignment_id)
        self.completed = OperationalPilotCompletion(
            packet_id=self.active.packet_id,
            task_id=self.active.task.task_id,
            operator_ref_sha256=self.active.operator_ref_sha256,
            status="VALID",
            elapsed_seconds=elapsed_seconds,
            terminal_decision=terminal_decision,
            conclusion_summary=conclusion_summary,
        )
        self.active = None
        return self.completed


def _context(request: Request) -> AuthenticatedRuntimeContext:
    user = request.headers.get("x-test-user", "user-a")
    permissions = {OPERATIONAL_VALUE_PARTICIPATE_PERMISSION}
    if request.headers.get("x-no-pilot-permission") == "1":
        permissions.clear()
    return AuthenticatedRuntimeContext(
        organization_id=request.headers.get("x-test-organization", "org-a"),
        identity_id=f"identity-{user}",
        user_id=user,
        permissions=frozenset(permissions),
    )


def test_collection_api_owns_elapsed_time_and_hides_private_assignment_material() -> None:
    clock = ControlledClock(100.0)
    timers = HostMonotonicPilotTimerRegistry(clock=clock)
    store = FakeStore()
    app = FastAPI()
    attach_operational_value_collection_api(
        app,
        context_provider=_context,
        store=store,
        timer_registry=timers,
    )

    with TestClient(app) as client:
        assigned = client.post("/api/operational-value/tasks/next")
        assert assigned.status_code == 200
        payload = assigned.json()
        assert payload["assignment_id"] == ASSIGNMENT_ID
        assert payload["task"]["task_id"] == TASK_ID
        serialized = assigned.text.lower()
        for forbidden in (
            "pair_id",
            "scenario_id",
            "group_id",
            "source_split",
            "operator_ref",
            "host_session",
            "gold_answer",
            "private_truth",
            "oracle",
        ):
            assert forbidden not in serialized

        clock.value = 112.75
        completed = client.post(
            f"/api/operational-value/assignments/{ASSIGNMENT_ID}/complete",
            json={
                "terminal_decision": "FINAL",
                "conclusion_summary": "The evidence supports waiting for the current analysis to finish.",
            },
        )
        assert completed.status_code == 200
        assert completed.json()["elapsed_seconds"] == 12.75
        assert store.completed is not None
        assert store.completed.elapsed_seconds == 12.75
        assert store.completed.measurement_source == "HOST_MONOTONIC_TIMER"


def test_collection_rejects_client_elapsed_and_requires_explicit_permission() -> None:
    clock = ControlledClock(10.0)
    store = FakeStore()
    app = FastAPI()
    attach_operational_value_collection_api(
        app,
        context_provider=_context,
        store=store,
        timer_registry=HostMonotonicPilotTimerRegistry(clock=clock),
    )

    with TestClient(app) as client:
        denied = client.post(
            "/api/operational-value/tasks/next",
            headers={"x-no-pilot-permission": "1"},
        )
        assert denied.status_code == 403

        assigned = client.post("/api/operational-value/tasks/next")
        assert assigned.status_code == 200
        clock.value = 14.0
        tampered = client.post(
            f"/api/operational-value/assignments/{ASSIGNMENT_ID}/complete",
            json={
                "terminal_decision": "FINAL",
                "conclusion_summary": "Recorded conclusion.",
                "elapsed_seconds": 0.001,
            },
        )
        assert tampered.status_code == 422
        assert store.completed is None
        assert timers_still_active(app, ASSIGNMENT_ID)


def timers_still_active(app: FastAPI, assignment_id: str) -> bool:
    return app.state.operational_value_timer_registry.has(assignment_id)


def test_collection_fails_closed_when_monotonic_session_is_lost() -> None:
    clock = ControlledClock(20.0)
    timers = HostMonotonicPilotTimerRegistry(clock=clock)
    store = FakeStore()
    app = FastAPI()
    attach_operational_value_collection_api(
        app,
        context_provider=_context,
        store=store,
        timer_registry=timers,
    )
    with TestClient(app) as client:
        assert client.post("/api/operational-value/tasks/next").status_code == 200
        timers.discard(ASSIGNMENT_ID)
        clock.value = 25.0
        lost = client.post(
            f"/api/operational-value/assignments/{ASSIGNMENT_ID}/complete",
            json={
                "terminal_decision": "FINAL",
                "conclusion_summary": "This result must not receive a fabricated duration.",
            },
        )
        assert lost.status_code == 409
        assert lost.json()["detail"] == "operational_pilot_timer_session_lost"
        assert store.failure_reason == "host_timer_session_lost"
        assert store.completed is None
