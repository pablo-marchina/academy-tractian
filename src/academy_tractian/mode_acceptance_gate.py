from __future__ import annotations

from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from research.e2.models import Decision, ResponseMode, RunTrace, ToolSpec

from .escalation_handoff import build_escalation_handoff, evaluate_escalation_handoff
from .read_semantics_gate import ProductionReadSemanticsGate
from .runtime import ProductionRequest, canonical_tool_registry


PRODUCTION_AGENT_MODE_GATE_VERSION = "production-required-agent-modes-gate-v1"

AgentMode = Literal[
    "CONTEXTUALIZE",
    "INVESTIGATE",
    "CLARIFY",
    "ABSTAIN",
    "ESCALATE",
    "EXECUTION_DEFERRED",
    "UNKNOWN",
]

_ACTION_DECISIONS = {
    Decision.ACT_REPROCESS,
    Decision.ACT_REQUEST_SPECIALIST,
    Decision.ACT_UPDATE_CONFIG,
    Decision.ACT_REQUEST_RETRAINING,
}

_DECISION_TO_MODE: dict[Decision, AgentMode] = {
    Decision.ORIENT: "CONTEXTUALIZE",
    Decision.INVESTIGATE: "INVESTIGATE",
    Decision.ASK_CLARIFICATION: "CLARIFY",
    Decision.ABSTAIN: "ABSTAIN",
    Decision.ESCALATE_HUMAN: "ESCALATE",
    Decision.ACT_REPROCESS: "EXECUTION_DEFERRED",
    Decision.ACT_REQUEST_SPECIALIST: "EXECUTION_DEFERRED",
    Decision.ACT_UPDATE_CONFIG: "EXECUTION_DEFERRED",
    Decision.ACT_REQUEST_RETRAINING: "EXECUTION_DEFERRED",
}

_CONTROL_TERMINALS = {
    Decision.ASK_CLARIFICATION,
    Decision.ABSTAIN,
    Decision.ESCALATE_HUMAN,
}


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProductionAgentModeReport(_FrozenModel):
    """Sanitized structural acceptance report for the required non-action agent modes."""

    schema_version: Literal["production-required-agent-modes-gate-v1"] = (
        PRODUCTION_AGENT_MODE_GATE_VERSION
    )
    run_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    passed: bool
    applicable_to_required_modes: bool
    agent_mode: AgentMode
    terminal_decision: str | None = None
    terminal_response_mode: str | None = None
    read_result_count: int = Field(ge=0)
    read_contract_issue_count: int = Field(ge=0)
    read_mode_counts: dict[str, int]
    escalation_handoff_applicable: bool
    escalation_handoff_passed: bool | None = None
    escalation_evidence_reference_count: int = Field(ge=0)
    violations: tuple[str, ...]
    raw_response_recorded: Literal[False] = False
    terminal_message_recorded: Literal[False] = False
    trace_mutated: Literal[False] = False


class ProductionAgentModeGateError(RuntimeError):
    def __init__(self, report: ProductionAgentModeReport) -> None:
        super().__init__(
            "production required-agent-modes gate failed: "
            f"mode={report.agent_mode} "
            f"violations={','.join(report.violations) or 'none'}"
        )
        self.report = report


class ProductionAgentModeGate:
    """Evaluate deterministic mode invariants from an immutable production RunTrace.

    The gate intentionally does not judge whether a domain conclusion is semantically correct.
    It verifies only observable structural/safety invariants: known terminal decision and response
    mode, no false COMPLETE claim for uncertainty/control terminals, read-contract integrity, at
    least one canonical read before INVESTIGATE, and exact escalation handoff binding.
    Consequential action decisions are reported as EXECUTION_DEFERRED because they are promoted by
    a later independent gate.
    """

    def __init__(self, *, registry: Mapping[str, ToolSpec] | None = None) -> None:
        self.registry = dict(registry or canonical_tool_registry())
        self._read_gate = ProductionReadSemanticsGate(registry=self.registry)

    @staticmethod
    def _nonempty_text(value: object) -> bool:
        return isinstance(value, str) and bool(value.strip())

    def evaluate(
        self,
        *,
        request: ProductionRequest,
        trace: RunTrace,
    ) -> ProductionAgentModeReport:
        violations: list[str] = []
        finals = [event for event in trace.events if event.event_type == "final_response"]
        final_payload: dict[str, object] | None = None
        if len(finals) != 1:
            violations.append("FINAL_RESPONSE_COUNT_INVALID")
        elif not isinstance(finals[0].result, dict):
            violations.append("FINAL_RESPONSE_PAYLOAD_INVALID")
        else:
            final_payload = dict(finals[0].result)

        decision: Decision | None = None
        response_mode: ResponseMode | None = None
        terminal_decision: str | None = None
        terminal_response_mode: str | None = None
        agent_mode: AgentMode = "UNKNOWN"

        if final_payload is not None:
            raw_decision = final_payload.get("decision")
            if isinstance(raw_decision, str):
                terminal_decision = raw_decision
                try:
                    decision = Decision(raw_decision)
                    agent_mode = _DECISION_TO_MODE.get(decision, "UNKNOWN")
                except ValueError:
                    violations.append("TERMINAL_DECISION_UNKNOWN")
            else:
                violations.append("TERMINAL_DECISION_MISSING_OR_INVALID")

            raw_response_mode = final_payload.get("response_mode")
            if isinstance(raw_response_mode, str):
                terminal_response_mode = raw_response_mode
                try:
                    response_mode = ResponseMode(raw_response_mode)
                except ValueError:
                    violations.append("TERMINAL_RESPONSE_MODE_UNKNOWN")
            else:
                violations.append("TERMINAL_RESPONSE_MODE_MISSING_OR_INVALID")

            if decision is not None and not self._nonempty_text(final_payload.get("message")):
                violations.append("TERMINAL_MESSAGE_MISSING_OR_EMPTY")

            if decision in _CONTROL_TERMINALS:
                if response_mode is ResponseMode.COMPLETE:
                    violations.append("CONTROL_TERMINAL_CANNOT_CLAIM_COMPLETE")
                if not self._nonempty_text(final_payload.get("reason_code")):
                    violations.append("CONTROL_TERMINAL_REASON_CODE_MISSING_OR_EMPTY")

        read_report = self._read_gate.evaluate(trace)
        if not read_report.passed:
            violations.append("READ_SEMANTICS_CONTRACT_FAILED")

        if decision is Decision.INVESTIGATE and read_report.read_result_count == 0:
            violations.append("INVESTIGATE_REQUIRES_CANONICAL_READ")

        escalation_handoff_applicable = decision is Decision.ESCALATE_HUMAN
        escalation_handoff_passed: bool | None = None
        escalation_evidence_reference_count = 0
        if escalation_handoff_applicable:
            try:
                handoff = build_escalation_handoff(request=request, trace=trace)
                handoff_evaluation = evaluate_escalation_handoff(
                    request=request,
                    trace=trace,
                    handoff=handoff,
                )
                escalation_handoff_passed = handoff_evaluation.passed
                escalation_evidence_reference_count = handoff_evaluation.evidence_reference_count
                if not handoff_evaluation.passed:
                    violations.append("ESCALATION_HANDOFF_INVALID")
            except (TypeError, ValueError):
                escalation_handoff_passed = False
                violations.append("ESCALATION_HANDOFF_INVALID")

        applicable = decision is not None and decision not in _ACTION_DECISIONS
        return ProductionAgentModeReport(
            run_id=trace.run_id,
            scenario_id=trace.scenario_id,
            passed=not violations,
            applicable_to_required_modes=applicable,
            agent_mode=agent_mode,
            terminal_decision=terminal_decision,
            terminal_response_mode=terminal_response_mode,
            read_result_count=read_report.read_result_count,
            read_contract_issue_count=read_report.contract_issue_count,
            read_mode_counts=dict(read_report.mode_counts),
            escalation_handoff_applicable=escalation_handoff_applicable,
            escalation_handoff_passed=escalation_handoff_passed,
            escalation_evidence_reference_count=escalation_evidence_reference_count,
            violations=tuple(violations),
        )

    def require(
        self,
        *,
        request: ProductionRequest,
        trace: RunTrace,
    ) -> ProductionAgentModeReport:
        report = self.evaluate(request=request, trace=trace)
        if not report.passed:
            raise ProductionAgentModeGateError(report)
        return report
