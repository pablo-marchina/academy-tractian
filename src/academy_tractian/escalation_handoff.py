from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.models import RunTrace, TraceEvent

from .runtime import ProductionRequest


HANDOFF_SCHEMA_VERSION = "production-escalation-handoff-v1"
HANDOFF_EVALUATION_SCHEMA_VERSION = "production-escalation-handoff-evaluation-v1"
REVIEWER_INSTRUCTION = (
    "Review the unresolved request and the referenced trace observations before deciding "
    "the next step. Do not execute a consequential action without independent authorization."
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def _canonical_hash(payload: Any) -> str:
    raw = json.dumps(
        _jsonable(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def _final_payload(trace: RunTrace) -> dict[str, Any] | None:
    finals = [event for event in trace.events if event.event_type == "final_response"]
    if len(finals) != 1 or not isinstance(finals[0].result, dict):
        return None
    return dict(finals[0].result)


def _observation_events(trace: RunTrace) -> tuple[TraceEvent, ...]:
    return tuple(event for event in trace.events if event.event_type == "observation")


class EscalationEvidenceReference(_FrozenModel):
    sequence: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    status_code: int | None = None
    blocked_code: str | None = None
    controller_generated: bool = False
    result_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @classmethod
    def from_event(cls, event: TraceEvent) -> "EscalationEvidenceReference":
        result = event.result if isinstance(event.result, dict) else {}
        status_code = event.metadata.get("status_code")
        if status_code is None and isinstance(result.get("status_code"), int):
            status_code = result["status_code"]
        blocked_code = result.get("blocked_code") if isinstance(result.get("blocked_code"), str) else None
        return cls(
            sequence=event.sequence,
            tool_name=event.tool_name or "unknown_tool",
            status_code=status_code if isinstance(status_code, int) else None,
            blocked_code=blocked_code,
            controller_generated=event.metadata.get("controller_generated") is True,
            result_sha256=_canonical_hash(event.result),
        )


class HumanEscalationHandoff(_FrozenModel):
    schema_version: Literal["production-escalation-handoff-v1"] = HANDOFF_SCHEMA_VERSION
    request_id: str = Field(min_length=1)
    unresolved_request: str = Field(min_length=1)
    reason_code: str = Field(min_length=1)
    terminal_message: str = Field(min_length=1)
    evidence_state: Literal["COLLECTED", "NONE_COLLECTED"]
    evidence_references: tuple[EscalationEvidenceReference, ...]
    reviewer_instruction: Literal[
        "Review the unresolved request and the referenced trace observations before deciding the next step. Do not execute a consequential action without independent authorization."
    ] = REVIEWER_INSTRUCTION
    handoff_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_handoff(self) -> "HumanEscalationHandoff":
        expected_state = "COLLECTED" if self.evidence_references else "NONE_COLLECTED"
        if self.evidence_state != expected_state:
            raise ValueError("escalation handoff evidence_state mismatch")
        payload = self.model_dump(mode="json", exclude={"handoff_sha256"})
        if self.handoff_sha256 != _canonical_hash(payload):
            raise ValueError("escalation handoff SHA mismatch")
        return self

    @classmethod
    def build(cls, **kwargs: Any) -> "HumanEscalationHandoff":
        payload = {
            "schema_version": HANDOFF_SCHEMA_VERSION,
            **kwargs,
            "reviewer_instruction": REVIEWER_INSTRUCTION,
        }
        return cls(**payload, handoff_sha256=_canonical_hash(payload))


class EscalationHandoffEvaluation(_FrozenModel):
    schema_version: Literal[
        "production-escalation-handoff-evaluation-v1"
    ] = HANDOFF_EVALUATION_SCHEMA_VERSION
    applicable: bool
    passed: bool
    violations: tuple[str, ...]
    evidence_reference_count: int = Field(ge=0)
    evaluation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_evaluation(self) -> "EscalationHandoffEvaluation":
        if self.passed != (not self.violations):
            raise ValueError("escalation handoff evaluation pass mismatch")
        payload = self.model_dump(mode="json", exclude={"evaluation_sha256"})
        if self.evaluation_sha256 != _canonical_hash(payload):
            raise ValueError("escalation handoff evaluation SHA mismatch")
        return self

    @classmethod
    def build(
        cls,
        *,
        applicable: bool,
        violations: tuple[str, ...],
        evidence_reference_count: int,
    ) -> "EscalationHandoffEvaluation":
        payload = {
            "schema_version": HANDOFF_EVALUATION_SCHEMA_VERSION,
            "applicable": applicable,
            "passed": not violations,
            "violations": violations,
            "evidence_reference_count": evidence_reference_count,
        }
        return cls(**payload, evaluation_sha256=_canonical_hash(payload))


def build_escalation_handoff(
    *,
    request: ProductionRequest,
    trace: RunTrace,
) -> HumanEscalationHandoff | None:
    final = _final_payload(trace)
    if final is None or final.get("decision") != "ESCALATE_HUMAN":
        return None

    reason_code = final.get("reason_code")
    message = final.get("message")
    if not isinstance(reason_code, str) or not reason_code.strip():
        raise ValueError("escalation final response requires a reason_code")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("escalation final response requires a message")

    references = tuple(
        EscalationEvidenceReference.from_event(event)
        for event in _observation_events(trace)
    )
    return HumanEscalationHandoff.build(
        request_id=request.request_id,
        unresolved_request=request.user_request,
        reason_code=reason_code,
        terminal_message=message,
        evidence_state="COLLECTED" if references else "NONE_COLLECTED",
        evidence_references=references,
    )


def evaluate_escalation_handoff(
    *,
    request: ProductionRequest,
    trace: RunTrace,
    handoff: HumanEscalationHandoff | None,
) -> EscalationHandoffEvaluation:
    final = _final_payload(trace)
    is_escalation = final is not None and final.get("decision") == "ESCALATE_HUMAN"
    if not is_escalation:
        violations = ("UNEXPECTED_HANDOFF_FOR_NON_ESCALATION",) if handoff is not None else ()
        return EscalationHandoffEvaluation.build(
            applicable=False,
            violations=violations,
            evidence_reference_count=0 if handoff is None else len(handoff.evidence_references),
        )

    if handoff is None:
        return EscalationHandoffEvaluation.build(
            applicable=True,
            violations=("MISSING_ESCALATION_HANDOFF",),
            evidence_reference_count=0,
        )

    violations: list[str] = []
    if handoff.request_id != request.request_id:
        violations.append("REQUEST_ID_MISMATCH")
    if handoff.unresolved_request != request.user_request:
        violations.append("UNRESOLVED_REQUEST_MISMATCH")
    if handoff.reviewer_instruction != REVIEWER_INSTRUCTION:
        violations.append("REVIEWER_INSTRUCTION_MISMATCH")

    assert final is not None
    if handoff.reason_code != final.get("reason_code"):
        violations.append("REASON_CODE_MISMATCH")
    if handoff.terminal_message != final.get("message"):
        violations.append("TERMINAL_MESSAGE_MISMATCH")

    expected_references = tuple(
        EscalationEvidenceReference.from_event(event)
        for event in _observation_events(trace)
    )
    if handoff.evidence_references != expected_references:
        violations.append("EVIDENCE_REFERENCE_MISMATCH")
    expected_state = "COLLECTED" if expected_references else "NONE_COLLECTED"
    if handoff.evidence_state != expected_state:
        violations.append("EVIDENCE_STATE_MISMATCH")

    return EscalationHandoffEvaluation.build(
        applicable=True,
        violations=tuple(violations),
        evidence_reference_count=len(handoff.evidence_references),
    )
