from __future__ import annotations

from hashlib import sha256
from typing import Literal, Protocol

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .product_api import (
    AuthenticatedRuntimeContext,
    RuntimeContextProvider,
    require_runtime_permission,
    trusted_runtime_context,
)
from .semantic_evaluation import SemanticDimension, SemanticScore
from .semantic_human_calibration import HumanLabelReason, SemanticReviewerTask


SEMANTIC_REVIEW_PERMISSION = "semantic-calibration:review"
SemanticReviewPhase = Literal["REVIEW", "ADJUDICATION"]
SemanticReviewState = Literal["ACTIVE", "COMPLETED", "WITHDRAWN"]
ReviewerSlot = Literal["A", "B"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SemanticReviewAssignmentRecord(_FrozenModel):
    """Private assignment state. Reviewer slot and principal markers never reach the browser."""

    assignment_id: str = Field(pattern=r"^semassign_[0-9a-f]{24}$")
    organization_id: str = Field(min_length=1)
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    task: SemanticReviewerTask
    phase: SemanticReviewPhase
    reviewer_slot: ReviewerSlot | None
    user_id: str = Field(min_length=1)
    reviewer_ref_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_phase_slot(self) -> "SemanticReviewAssignmentRecord":
        if self.phase == "REVIEW" and self.reviewer_slot not in ("A", "B"):
            raise ValueError("semantic_review_review_phase_requires_slot")
        if self.phase == "ADJUDICATION" and self.reviewer_slot is not None:
            raise ValueError("semantic_review_adjudication_must_not_have_slot")
        return self


class SemanticReviewerTaskSafe(_FrozenModel):
    """Minimum task projection needed for blind human scoring.

    Scenario identity and evaluator binding hashes remain private. They are useful for evaluator
    integrity but provide no benefit to the reviewer and can create cross-task correlation cues.
    """

    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    response_mode: str = Field(min_length=1)
    dimension: SemanticDimension
    terminal_decision: str = Field(min_length=1)
    terminal_message: str = Field(min_length=1)
    safe_evidence_context: tuple[str, ...]
    criterion_description: str = Field(min_length=1)
    score_0_anchor: str = Field(min_length=1)
    score_1_anchor: str = Field(min_length=1)
    score_2_anchor: str = Field(min_length=1)


class SemanticReviewAssignmentSafe(_FrozenModel):
    """Blind reviewer payload with evaluator-only binding metadata removed."""

    assignment_id: str = Field(pattern=r"^semassign_[0-9a-f]{24}$")
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    task: SemanticReviewerTaskSafe


class SemanticReviewSubmission(_FrozenModel):
    score: SemanticScore
    reason_codes: tuple[HumanLabelReason, ...]

    @model_validator(mode="after")
    def validate_reasons(self) -> "SemanticReviewSubmission":
        if len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("semantic_review_reason_codes_must_be_unique")
        if self.score == 2 and self.reason_codes != ("NO_MATERIAL_DEFECT",):
            raise ValueError("semantic_review_score_2_requires_no_material_defect")
        if self.score < 2 and not self.reason_codes:
            raise ValueError("semantic_review_defect_score_requires_reason")
        if self.score < 2 and "NO_MATERIAL_DEFECT" in self.reason_codes:
            raise ValueError("semantic_review_defect_score_rejects_no_material_defect")
        return self


class SemanticReviewAccepted(_FrozenModel):
    assignment_id: str = Field(pattern=r"^semassign_[0-9a-f]{24}$")
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    state: Literal["COMPLETED"] = "COMPLETED"


class SemanticReviewWithdrawn(_FrozenModel):
    assignment_id: str = Field(pattern=r"^semassign_[0-9a-f]{24}$")
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    state: Literal["WITHDRAWN"] = "WITHDRAWN"


class SemanticReviewCollectionStore(Protocol):
    def get_active_for_user(
        self,
        *,
        organization_id: str,
        user_id: str,
    ) -> SemanticReviewAssignmentRecord | None: ...

    def assign_next(
        self,
        *,
        organization_id: str,
        user_id: str,
        principal_ref_sha256: str,
    ) -> SemanticReviewAssignmentRecord | None: ...

    def complete(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
        score: int,
        reason_codes: tuple[HumanLabelReason, ...],
    ) -> SemanticReviewAssignmentRecord: ...

    def withdraw(
        self,
        *,
        assignment_id: str,
        organization_id: str,
        user_id: str,
    ) -> SemanticReviewAssignmentRecord: ...


def semantic_reviewer_ref_sha256(
    *, packet_id: str, organization_id: str, principal_ref_sha256: str
) -> str:
    """Packet-scoped reviewer pseudonym; raw product identity never enters calibration exports."""

    material = "\0".join(
        (
            "semantic-reviewer-v1",
            packet_id,
            organization_id,
            principal_ref_sha256,
        )
    )
    return sha256(material.encode("utf-8")).hexdigest()


def _safe_task(task: SemanticReviewerTask) -> SemanticReviewerTaskSafe:
    return SemanticReviewerTaskSafe(
        task_id=task.task_id,
        response_mode=task.response_mode,
        dimension=task.dimension,
        terminal_decision=task.terminal_decision,
        terminal_message=task.terminal_message,
        safe_evidence_context=task.safe_evidence_context,
        criterion_description=task.criterion_description,
        score_0_anchor=task.score_0_anchor,
        score_1_anchor=task.score_1_anchor,
        score_2_anchor=task.score_2_anchor,
    )


def _safe(record: SemanticReviewAssignmentRecord) -> SemanticReviewAssignmentSafe:
    return SemanticReviewAssignmentSafe(
        assignment_id=record.assignment_id,
        packet_id=record.packet_id,
        task=_safe_task(record.task),
    )


def attach_semantic_review_collection_api(
    app: FastAPI,
    *,
    context_provider: RuntimeContextProvider,
    store: SemanticReviewCollectionStore,
) -> None:
    """Attach blind human semantic review to the existing authenticated product identity."""

    app.state.semantic_review_collection_store = store

    def context(request: Request) -> AuthenticatedRuntimeContext:
        trusted = trusted_runtime_context(context_provider, request)
        require_runtime_permission(trusted, SEMANTIC_REVIEW_PERMISSION)
        return trusted

    def active_assignment(
        assignment_id: str,
        trusted: AuthenticatedRuntimeContext,
    ) -> SemanticReviewAssignmentRecord:
        active = store.get_active_for_user(
            organization_id=trusted.organization_id,
            user_id=trusted.user_id,
        )
        if active is None or active.assignment_id != assignment_id:
            raise HTTPException(status_code=404, detail="semantic_review_assignment_not_found")
        return active

    @app.post("/api/semantic-review/tasks/next", response_model=SemanticReviewAssignmentSafe)
    def next_semantic_review_task(request: Request) -> SemanticReviewAssignmentSafe:
        trusted = context(request)
        principal_marker = sha256(
            "\0".join(
                ("semantic-review-principal-v1", trusted.organization_id, trusted.user_id)
            ).encode("utf-8")
        ).hexdigest()
        try:
            assigned = store.assign_next(
                organization_id=trusted.organization_id,
                user_id=trusted.user_id,
                principal_ref_sha256=principal_marker,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if assigned is None:
            raise HTTPException(status_code=404, detail="semantic_review_no_task_available")
        return _safe(assigned)

    @app.post(
        "/api/semantic-review/assignments/{assignment_id}/complete",
        response_model=SemanticReviewAccepted,
    )
    def complete_semantic_review(
        assignment_id: str,
        payload: SemanticReviewSubmission,
        request: Request,
    ) -> SemanticReviewAccepted:
        trusted = context(request)
        active_assignment(assignment_id, trusted)
        try:
            completed = store.complete(
                assignment_id=assignment_id,
                organization_id=trusted.organization_id,
                user_id=trusted.user_id,
                score=int(payload.score),
                reason_codes=payload.reason_codes,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="semantic_review_assignment_not_found") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return SemanticReviewAccepted(
            assignment_id=completed.assignment_id,
            packet_id=completed.packet_id,
            task_id=completed.task.task_id,
        )

    @app.post(
        "/api/semantic-review/assignments/{assignment_id}/withdraw",
        response_model=SemanticReviewWithdrawn,
    )
    def withdraw_semantic_review(
        assignment_id: str,
        request: Request,
    ) -> SemanticReviewWithdrawn:
        trusted = context(request)
        active_assignment(assignment_id, trusted)
        try:
            withdrawn = store.withdraw(
                assignment_id=assignment_id,
                organization_id=trusted.organization_id,
                user_id=trusted.user_id,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="semantic_review_assignment_not_found") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return SemanticReviewWithdrawn(
            assignment_id=withdrawn.assignment_id,
            packet_id=withdrawn.packet_id,
            task_id=withdrawn.task.task_id,
        )