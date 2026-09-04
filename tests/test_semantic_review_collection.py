from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from academy_tractian.product_api import AuthenticatedRuntimeContext
from academy_tractian.semantic_review_collection import (
    SEMANTIC_REVIEW_PERMISSION,
    SemanticReviewAssignmentRecord,
    attach_semantic_review_collection_api,
)
from academy_tractian.semantic_human_calibration import SemanticReviewerTask


def _task() -> SemanticReviewerTask:
    return SemanticReviewerTask(
        task_id="sem_" + "1" * 24,
        scenario_id="VAL-A",
        output_sha256="2" * 64,
        context_sha256="3" * 64,
        response_mode="partial",
        dimension="operational_usefulness",
        terminal_decision="ESCALATE_HUMAN",
        terminal_message="Escalate because the sanitized evidence is insufficient.",
        safe_evidence_context=("The API returned partial evidence and one unresolved blocker.",),
        criterion_description="Judge whether the response enables the correct next operational step.",
        score_0_anchor="Wrong or unusable operational guidance.",
        score_1_anchor="Partially useful but materially incomplete guidance.",
        score_2_anchor="Correct and actionable operational guidance.",
    )


class _Store:
    def __init__(self) -> None:
        self.record = SemanticReviewAssignmentRecord(
            assignment_id="semassign_" + "4" * 24,
            organization_id="org-a",
            packet_id="sempkt_" + "5" * 24,
            task=_task(),
            phase="ADJUDICATION",
            reviewer_slot=None,
            user_id="reviewer-a",
            reviewer_ref_sha256="6" * 64,
        )
        self.completed: tuple[int, tuple[str, ...]] | None = None
        self.withdrawn = False

    def get_active_for_user(self, *, organization_id: str, user_id: str):
        if self.withdrawn or self.completed is not None:
            return None
        if organization_id == self.record.organization_id and user_id == self.record.user_id:
            return self.record
        return None

    def assign_next(self, *, organization_id: str, user_id: str, principal_ref_sha256: str):
        if organization_id == self.record.organization_id and user_id == self.record.user_id:
            return self.record
        return None

    def complete(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        score: int,
        reason_codes: tuple[str, ...],
    ):
        if self.get_active_for_user(organization_id=organization_id, user_id=user_id) is None:
            raise KeyError(assignment_id)
        self.completed = (score, reason_codes)
        return self.record

    def withdraw(self, *, assignment_id: str, organization_id: str, user_id: str):
        if self.get_active_for_user(organization_id=organization_id, user_id=user_id) is None:
            raise KeyError(assignment_id)
        self.withdrawn = True
        return self.record


def _context(request: Request) -> AuthenticatedRuntimeContext:
    user_id = request.headers.get("x-test-user", "reviewer-a")
    permissions = (
        frozenset({SEMANTIC_REVIEW_PERMISSION})
        if request.headers.get("x-test-deny") != "1"
        else frozenset()
    )
    return AuthenticatedRuntimeContext(
        organization_id=request.headers.get("x-test-org", "org-a"),
        identity_id=f"identity-{user_id}",
        user_id=user_id,
        role="reviewer",
        permissions=permissions,
    )


def _client(store: _Store) -> TestClient:
    app = FastAPI()
    attach_semantic_review_collection_api(app, context_provider=_context, store=store)
    return TestClient(app)


def test_next_task_is_blind_even_for_adjudication() -> None:
    store = _Store()
    response = _client(store).post("/api/semantic-review/tasks/next")

    assert response.status_code == 200
    payload = response.json()
    assert payload["assignment_id"] == store.record.assignment_id
    assert payload["task"]["dimension"] == "operational_usefulness"
    serialized = str(payload).lower()
    for forbidden in (
        "phase",
        "reviewer_slot",
        "adjudication",
        "source_split",
        "group_id",
        "reviewer_ref_sha256",
        "user_id",
        "private_truth",
        "gold",
    ):
        assert forbidden not in serialized


def test_permission_wrong_tenant_and_wrong_user_fail_closed() -> None:
    store = _Store()
    client = _client(store)

    denied = client.post("/api/semantic-review/tasks/next", headers={"x-test-deny": "1"})
    assert denied.status_code == 403

    other_tenant = client.post(
        "/api/semantic-review/tasks/next",
        headers={"x-test-org": "org-b"},
    )
    assert other_tenant.status_code == 404

    wrong_user = client.post(
        f"/api/semantic-review/assignments/{store.record.assignment_id}/complete",
        headers={"x-test-user": "reviewer-b"},
        json={"score": 2, "reason_codes": ["NO_MATERIAL_DEFECT"]},
    )
    assert wrong_user.status_code == 404


def test_complete_accepts_only_canonical_score_reason_shape_and_returns_no_private_state() -> None:
    store = _Store()
    client = _client(store)

    invalid = client.post(
        f"/api/semantic-review/assignments/{store.record.assignment_id}/complete",
        json={"score": 2, "reason_codes": ["WRONG_OPERATIONAL_CONCLUSION"]},
    )
    assert invalid.status_code == 422
    assert store.completed is None

    accepted = client.post(
        f"/api/semantic-review/assignments/{store.record.assignment_id}/complete",
        json={"score": 1, "reason_codes": ["MISSING_NEXT_STEP"]},
    )
    assert accepted.status_code == 200
    assert store.completed == (1, ("MISSING_NEXT_STEP",))
    assert accepted.json() == {
        "assignment_id": store.record.assignment_id,
        "packet_id": store.record.packet_id,
        "task_id": store.record.task.task_id,
        "state": "COMPLETED",
    }


def test_withdrawal_persists_no_label_through_api_contract() -> None:
    store = _Store()
    client = _client(store)

    response = client.post(
        f"/api/semantic-review/assignments/{store.record.assignment_id}/withdraw"
    )
    assert response.status_code == 200
    assert store.withdrawn is True
    assert store.completed is None
    assert response.json()["state"] == "WITHDRAWN"
