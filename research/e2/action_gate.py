from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import ActionOracle, Scenario, ToolSpec, TraceEvent
from .policy import ResourcePolicy
from .validation import validate_arguments


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    code: str
    reason: str


class EvidenceAwareActionGate:
    """Deterministic B3 pre-execution gate; it never infers policy from model text."""

    def __init__(self, policy: ResourcePolicy) -> None:
        self.policy = policy

    def check(
        self,
        *,
        scenario: Scenario,
        tool: ToolSpec,
        arguments: dict[str, Any],
        trace: list[TraceEvent],
    ) -> GateDecision:
        if tool.kind.value != "action":
            return GateDecision(True, "NOT_AN_ACTION", "no action gate required")

        issues = validate_arguments(tool, arguments)
        if issues:
            return GateDecision(False, "ARGUMENT_INVALID", "; ".join(i.code for i in issues))

        policy = self.policy.check(tool, arguments)
        if not policy.allowed:
            return GateDecision(False, policy.code, policy.reason)

        oracle: ActionOracle | None = scenario.action_oracle
        if oracle is not None:
            if oracle.execution_expectation == "forbidden":
                return GateDecision(False, "ACTION_FORBIDDEN_BY_ORACLE", "scenario forbids this action")
            if oracle.required_action and tool.name != oracle.required_action:
                return GateDecision(False, "WRONG_ACTION", "action does not match scenario oracle")
            if oracle.target_resource:
                target_values = {
                    value
                    for key, value in arguments.items()
                    if key.endswith("_id") and key != "point_id"
                }
                if oracle.target_resource not in target_values:
                    return GateDecision(False, "TARGET_MISMATCH", "action target does not match scenario oracle")

            required_sources = {
                requirement.source
                for group in scenario.evidence_oracle.required_groups
                for requirement in group.requirements
                if requirement.required_before_action
            }
            observed_sources = {
                event.metadata.get("evidence_id")
                for event in trace
                if event.event_type == "observation" and event.metadata.get("evidence_id")
            }
            missing = sorted(required_sources - observed_sources)
            if missing:
                return GateDecision(
                    False,
                    "EVIDENCE_INSUFFICIENT",
                    f"required evidence missing: {missing}",
                )

        return GateDecision(True, "ALLOWED", "deterministic B3 preconditions satisfied")
