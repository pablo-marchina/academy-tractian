from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .binding import validate_model_arguments
from .models import Decision, ResponseMode, RunTrace, TraceEvent
from .runner import HarnessRunner, ToolExecution
from .trace import append_event


class ControllerDecisionKind(str, Enum):
    TOOL = "TOOL"
    FINAL = "FINAL"
    CLARIFY = "CLARIFY"
    ESCALATE = "ESCALATE"
    ABSTAIN = "ABSTAIN"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ToolProposal(_FrozenModel):
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    evidence_id: str | None = None

    @model_validator(mode="after")
    def reject_model_controlled_binding(self) -> "ToolProposal":
        validate_model_arguments(self.arguments)
        return self


class ControllerObservation(_FrozenModel):
    tool_name: str
    status: Literal["success", "failure", "blocked"]
    executed: bool
    blocked_code: str | None = None
    status_code: int | None = None
    body: Any = None
    error_code: str | None = None


class ControllerContext(_FrozenModel):
    user_request: str
    turn_index: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    observations: tuple[ControllerObservation, ...] = ()


class ControllerDecision(_FrozenModel):
    kind: ControllerDecisionKind
    proposal: ToolProposal | None = None
    final: dict[str, Any] | None = None
    message: str | None = None
    reason_code: str | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "ControllerDecision":
        if self.kind is ControllerDecisionKind.TOOL:
            if self.proposal is None:
                raise ValueError("TOOL decision requires proposal")
            if self.final is not None:
                raise ValueError("TOOL decision cannot include final payload")
            return self

        if self.proposal is not None:
            raise ValueError("terminal decision cannot include tool proposal")
        if self.kind is ControllerDecisionKind.FINAL and self.final is None:
            raise ValueError("FINAL decision requires final payload")
        return self


class DecisionSource(Protocol):
    def decide(self, context: ControllerContext) -> ControllerDecision: ...


class DecisionSourceAuditRecord(_FrozenModel):
    """Sanitized additive trace record emitted by an auditable DecisionSource.

    The controller owns sequence assignment and trace mutation. The DecisionSource may only
    supply a model-call identifier and metadata; it cannot emit tool events or bypass the
    execution boundary.
    """

    event_type: Literal["model_call"] = "model_call"
    call_id: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ControllerLimits(_FrozenModel):
    max_turns: int = Field(default=8, ge=1, le=64)
    max_tool_calls: int = Field(default=6, ge=0, le=64)


class AgentController:
    """Provider-free single-agent controller over the frozen E2 execution boundary.

    The decision source may propose tools or terminal decisions. It never receives the
    runner binding/seed/private evaluator state, and every real tool execution is routed
    exclusively through HarnessRunner.execute_tool(). Auditable decision sources may expose
    sanitized model-call records through `drain_audit_records()`; the controller alone appends
    those records to the canonical trace.
    """

    def __init__(
        self,
        *,
        runner: HarnessRunner,
        decision_source: DecisionSource,
        limits: ControllerLimits | None = None,
    ) -> None:
        self.runner = runner
        self.decision_source = decision_source
        self.limits = limits or ControllerLimits()

    def _emit(self, event_type: str, **kwargs: Any) -> None:
        self.runner.trace = append_event(
            self.runner.trace,
            TraceEvent(
                sequence=len(self.runner.trace.events),
                event_type=event_type,
                **kwargs,
            ),
        )

    def _drain_decision_source_audit(self) -> None:
        drain = getattr(self.decision_source, "drain_audit_records", None)
        if drain is None:
            return
        if not callable(drain):
            raise TypeError("decision source audit drain must be callable")
        records = drain()
        if not isinstance(records, tuple):
            raise TypeError("decision source audit drain must return a tuple")
        for item in records:
            record = (
                item
                if isinstance(item, DecisionSourceAuditRecord)
                else DecisionSourceAuditRecord.model_validate(item)
            )
            self._emit(
                record.event_type,
                call_id=record.call_id,
                metadata=dict(record.metadata),
            )

    def _finish_terminal(self, decision: ControllerDecision) -> RunTrace:
        if decision.kind is ControllerDecisionKind.FINAL:
            assert decision.final is not None
            final = dict(decision.final)
            final.setdefault("controller_decision", decision.kind.value)
            return self.runner.finish(final)

        if decision.kind is ControllerDecisionKind.CLARIFY:
            final = {
                "decision": Decision.ASK_CLARIFICATION.value,
                "response_mode": ResponseMode.PARTIAL.value,
                "controller_decision": decision.kind.value,
                "message": decision.message or "Additional information is required before proceeding.",
                "reason_code": decision.reason_code or "CLARIFICATION_REQUIRED",
            }
            return self.runner.finish(final)

        if decision.kind is ControllerDecisionKind.ESCALATE:
            self._emit(
                "escalation",
                result={"reason_code": decision.reason_code or "HUMAN_REVIEW_REQUIRED"},
            )
            final = {
                "decision": Decision.ESCALATE_HUMAN.value,
                "response_mode": ResponseMode.PARTIAL.value,
                "controller_decision": decision.kind.value,
                "message": decision.message or "Human review is required before proceeding.",
                "reason_code": decision.reason_code or "HUMAN_REVIEW_REQUIRED",
            }
            return self.runner.finish(final)

        final = {
            "decision": Decision.ABSTAIN.value,
            "response_mode": ResponseMode.UNAVAILABLE.value,
            "controller_decision": ControllerDecisionKind.ABSTAIN.value,
            "message": decision.message or "The controller cannot proceed safely.",
            "reason_code": decision.reason_code or "SAFE_ABSTENTION",
        }
        return self.runner.finish(final)

    def _safe_abstain(self, *, reason_code: str, message: str) -> RunTrace:
        self._emit("state_change", metadata={"reason_code": reason_code})
        return self._finish_terminal(
            ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                reason_code=reason_code,
                message=message,
            )
        )

    @staticmethod
    def _observation_from_execution(execution: ToolExecution) -> ControllerObservation:
        if not execution.executed:
            return ControllerObservation(
                tool_name=execution.tool_name,
                status="blocked",
                executed=False,
                blocked_code=execution.blocked_code,
            )
        assert execution.response is not None
        return ControllerObservation(
            tool_name=execution.tool_name,
            status="success" if 200 <= execution.response.status_code < 400 else "failure",
            executed=True,
            status_code=execution.response.status_code,
            body=execution.response.body,
        )

    def run(self, user_request: str) -> RunTrace:
        observations: list[ControllerObservation] = []
        tool_call_count = 0

        for turn_index in range(self.limits.max_turns):
            context = ControllerContext(
                user_request=user_request,
                turn_index=turn_index,
                tool_call_count=tool_call_count,
                observations=tuple(observations),
            )
            try:
                decision = self.decision_source.decide(context)
            except Exception:
                try:
                    self._drain_decision_source_audit()
                except Exception:
                    return self._safe_abstain(
                        reason_code="DECISION_SOURCE_AUDIT_FAILURE",
                        message="Decision-source provenance failed validation; no further action was executed.",
                    )
                return self._safe_abstain(
                    reason_code="DECISION_SOURCE_FAILURE",
                    message="The decision source failed; no further action was executed.",
                )

            try:
                self._drain_decision_source_audit()
            except Exception:
                return self._safe_abstain(
                    reason_code="DECISION_SOURCE_AUDIT_FAILURE",
                    message="Decision-source provenance failed validation; no further action was executed.",
                )

            self._emit(
                "decision",
                result={
                    "kind": decision.kind.value,
                    "turn_index": turn_index,
                    "tool_call_count": tool_call_count,
                },
            )

            if decision.kind is not ControllerDecisionKind.TOOL:
                return self._finish_terminal(decision)

            assert decision.proposal is not None
            if tool_call_count >= self.limits.max_tool_calls:
                return self._safe_abstain(
                    reason_code="TOOL_CALL_BUDGET_EXHAUSTED",
                    message="The bounded tool-call budget was exhausted; no additional tool was executed.",
                )

            tool_call_count += 1
            try:
                execution = self.runner.execute_tool(
                    decision.proposal.tool_name,
                    dict(decision.proposal.arguments),
                    evidence_id=decision.proposal.evidence_id,
                )
            except Exception:
                return self._safe_abstain(
                    reason_code="TOOL_BOUNDARY_FAILURE",
                    message="The deterministic tool boundary rejected or failed the proposal; execution stopped safely.",
                )

            observation = self._observation_from_execution(execution)
            observations.append(observation)
            if not execution.executed:
                self._emit(
                    "observation",
                    tool_name=execution.tool_name,
                    result=observation.model_dump(mode="json"),
                    metadata={"controller_generated": True, "contained": True},
                )

        return self._safe_abstain(
            reason_code="TURN_BUDGET_EXHAUSTED",
            message="The bounded turn budget was exhausted; the controller stopped without further action.",
        )
