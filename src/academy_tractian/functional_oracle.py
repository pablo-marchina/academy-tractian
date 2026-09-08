from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.models import ResponseMode, RunTrace, TraceEvent

from .verification import IndependentOracleResult, VerificationStatus


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RequiredToolGroup(_FrozenModel):
    """At least `minimum_satisfied` tools in the group must execute before terminal."""

    group_id: str = Field(min_length=1)
    tools: tuple[str, ...] = Field(min_length=1)
    minimum_satisfied: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_minimum(self) -> "RequiredToolGroup":
        if self.minimum_satisfied > len(self.tools):
            raise ValueError("minimum_satisfied cannot exceed tool count")
        return self


class ToolResourceRequirement(_FrozenModel):
    """Require a canonical resource identifier to appear in arguments for one of the tools."""

    requirement_id: str = Field(min_length=1)
    tools: tuple[str, ...] = Field(min_length=1)
    resource_id: str = Field(min_length=1)


class FunctionalCaseSpec(_FrozenModel):
    schema_version: Literal["functional-case-v1"] = "functional-case-v1"
    case_id: str = Field(min_length=1)
    required_tool_groups: tuple[RequiredToolGroup, ...] = ()
    required_resources: tuple[ToolResourceRequirement, ...] = ()
    forbidden_tools: tuple[str, ...] = ()
    allowed_response_modes: tuple[ResponseMode, ...] = ()
    forbidden_reason_codes: tuple[str, ...] = (
        "DECISION_SOURCE_FAILURE",
        "DECISION_SOURCE_AUDIT_FAILURE",
        "TOOL_BOUNDARY_FAILURE",
        "TOOL_CALL_BUDGET_EXHAUSTED",
        "TURN_BUDGET_EXHAUSTED",
    )
    minimum_tool_calls: int = Field(default=0, ge=0)
    require_terminal: bool = True


class EvidenceRequirementSpec(_FrozenModel):
    schema_version: Literal["evidence-requirements-v1"] = "evidence-requirements-v1"
    requirement_id: str = Field(min_length=1)
    required_tool_groups: tuple[RequiredToolGroup, ...] = ()
    required_resources: tuple[ToolResourceRequirement, ...] = ()
    require_successful_results: bool = True


class FunctionalOracleReport(_FrozenModel):
    schema_version: Literal["functional-oracle-v1"] = "functional-oracle-v1"
    case_id: str
    status: VerificationStatus
    failures: tuple[str, ...]
    observed_tool_sequence: tuple[str, ...]
    observed_response_mode: str | None
    observed_reason_code: str | None
    tool_calls: int

    def as_independent_oracle(self) -> IndependentOracleResult:
        return IndependentOracleResult(
            status=self.status,
            source=self.schema_version,
            summary=(
                f"Functional case {self.case_id} satisfied its independent rubric."
                if self.status == "VERIFIED"
                else f"Functional case {self.case_id} failed: {', '.join(self.failures)}."
            ),
            evidence=tuple(self.failures) if self.failures else (f"case:{self.case_id}",),
            metrics={"tool_calls": self.tool_calls, "failure_count": len(self.failures)},
        )


class EvidenceOracleReport(_FrozenModel):
    schema_version: Literal["evidence-oracle-v1"] = "evidence-oracle-v1"
    requirement_id: str
    status: VerificationStatus
    failures: tuple[str, ...]
    satisfied_groups: int
    required_groups: int

    def as_independent_oracle(self) -> IndependentOracleResult:
        return IndependentOracleResult(
            status=self.status,
            source=self.schema_version,
            summary=(
                f"Evidence requirements {self.requirement_id} were satisfied."
                if self.status == "VERIFIED"
                else f"Evidence requirements {self.requirement_id} failed: {', '.join(self.failures)}."
            ),
            evidence=tuple(self.failures) if self.failures else (f"requirements:{self.requirement_id}",),
            metrics={
                "satisfied_groups": self.satisfied_groups,
                "required_groups": self.required_groups,
                "failure_count": len(self.failures),
            },
        )


def _terminal(trace: RunTrace) -> dict[str, Any] | None:
    finals = [event for event in trace.events if event.event_type == "final_response"]
    if len(finals) != 1 or not isinstance(finals[0].result, dict):
        return None
    return dict(finals[0].result)


def _tool_calls(trace: RunTrace) -> list[TraceEvent]:
    return [event for event in trace.events if event.event_type == "tool_call"]


def _successful_call_ids(trace: RunTrace) -> set[str]:
    successful: set[str] = set()
    for event in trace.events:
        if event.event_type != "tool_result" or not event.call_id:
            continue
        status = event.metadata.get("status_code")
        if isinstance(status, int) and 200 <= status < 300:
            successful.add(event.call_id)
    return successful


def _successful_calls(trace: RunTrace) -> list[TraceEvent]:
    successful_ids = _successful_call_ids(trace)
    return [
        event
        for event in trace.events
        if event.event_type == "tool_call"
        and event.call_id is not None
        and event.call_id in successful_ids
    ]


def _contains_scalar(value: Any, expected: str) -> bool:
    if isinstance(value, dict):
        return any(_contains_scalar(item, expected) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_scalar(item, expected) for item in value)
    return isinstance(value, str) and value == expected


def _resource_observed(calls: list[TraceEvent], requirement: ToolResourceRequirement) -> bool:
    return any(
        call.tool_name in requirement.tools
        and _contains_scalar(call.arguments or {}, requirement.resource_id)
        for call in calls
    )


def _group_satisfied(group: RequiredToolGroup, observed_tools: set[str]) -> bool:
    return sum(tool in observed_tools for tool in group.tools) >= group.minimum_satisfied


def evaluate_functional_trace(trace: RunTrace, spec: FunctionalCaseSpec) -> FunctionalOracleReport:
    """Evaluate externally specified task requirements without consulting AgentController policy."""

    calls = _tool_calls(trace)
    tool_sequence = tuple(call.tool_name or "" for call in calls)
    observed_tools = set(tool_sequence)
    terminal = _terminal(trace)
    failures: list[str] = []

    if spec.require_terminal and terminal is None:
        failures.append("MISSING_TERMINAL")

    for group in spec.required_tool_groups:
        if not _group_satisfied(group, observed_tools):
            failures.append(f"MISSING_TOOL_GROUP:{group.group_id}")

    for requirement in spec.required_resources:
        if not _resource_observed(calls, requirement):
            failures.append(f"MISSING_RESOURCE:{requirement.requirement_id}")

    forbidden_seen = sorted(observed_tools.intersection(spec.forbidden_tools))
    if forbidden_seen:
        failures.append(f"FORBIDDEN_TOOLS:{','.join(forbidden_seen)}")

    if len(calls) < spec.minimum_tool_calls:
        failures.append("TOO_FEW_TOOL_CALLS")

    response_mode = None if terminal is None else terminal.get("response_mode")
    reason_code = None if terminal is None else terminal.get("reason_code")
    if spec.allowed_response_modes:
        allowed = {mode.value for mode in spec.allowed_response_modes}
        if response_mode not in allowed:
            failures.append("UNACCEPTABLE_RESPONSE_MODE")
    if isinstance(reason_code, str) and reason_code in spec.forbidden_reason_codes:
        failures.append(f"FORBIDDEN_TERMINAL_REASON:{reason_code}")

    return FunctionalOracleReport(
        case_id=spec.case_id,
        status="FAILED" if failures else "VERIFIED",
        failures=tuple(failures),
        observed_tool_sequence=tool_sequence,
        observed_response_mode=response_mode if isinstance(response_mode, str) else None,
        observed_reason_code=reason_code if isinstance(reason_code, str) else None,
        tool_calls=len(calls),
    )


def evaluate_evidence_trace(trace: RunTrace, spec: EvidenceRequirementSpec) -> EvidenceOracleReport:
    """Evaluate evidence coverage separately from functional task success.

    Successful evidence is correlated by call_id, never by tool name alone. A successful call for
    asset B therefore cannot make a failed call for asset A count as evidence merely because both
    used `get_rms` or another shared tool.
    """

    calls = _successful_calls(trace) if spec.require_successful_results else _tool_calls(trace)
    observed_tools = {call.tool_name for call in calls if call.tool_name}
    failures: list[str] = []
    satisfied_groups = 0

    for group in spec.required_tool_groups:
        if _group_satisfied(group, observed_tools):
            satisfied_groups += 1
        else:
            failures.append(f"MISSING_EVIDENCE_GROUP:{group.group_id}")

    for requirement in spec.required_resources:
        if not _resource_observed(calls, requirement):
            failures.append(f"MISSING_EVIDENCE_RESOURCE:{requirement.requirement_id}")

    return EvidenceOracleReport(
        requirement_id=spec.requirement_id,
        status="FAILED" if failures else "VERIFIED",
        failures=tuple(failures),
        satisfied_groups=satisfied_groups,
        required_groups=len(spec.required_tool_groups),
    )
