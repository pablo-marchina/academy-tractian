from __future__ import annotations

from typing import Any

from .evaluators import EvaluationResult, MetricResult
from .models import Scenario, TraceEvent
from .validation import validate_arguments


class ArgumentEvaluator:
    name = "arguments"

    def __init__(self, registry: dict[str, Any]) -> None:
        self.registry = registry

    def evaluate(
        self,
        *,
        scenario: Scenario,
        trace: list[TraceEvent],
        final: dict[str, Any],
    ) -> EvaluationResult:
        tool_calls = [event for event in trace if event.event_type == "tool_call" and event.tool_name]
        invalid: list[dict[str, Any]] = []
        required_missing: list[str] = []

        for event in tool_calls:
            tool = self.registry.get(event.tool_name)
            if tool is None:
                invalid.append({"tool": event.tool_name, "code": "UNKNOWN_TOOL"})
                continue
            arguments = event.arguments or {}
            issues = validate_arguments(tool, arguments)
            invalid.extend(
                {"tool": event.tool_name, "code": issue.code, "field": issue.field}
                for issue in issues
            )
            required = {parameter.name for parameter in tool.parameters if parameter.required}
            required_missing.extend(
                f"{event.tool_name}:{name}" for name in sorted(required - set(arguments))
            )

        valid = not invalid and not required_missing
        return EvaluationResult(
            self.name,
            (
                MetricResult("argument_schema_valid", 1.0 if valid else 0.0, valid, {"issues": invalid}),
                MetricResult(
                    "required_argument_completeness",
                    1.0 if not required_missing else 0.0,
                    not required_missing,
                    {"missing": required_missing},
                ),
            ),
        )


class ConclusionEvaluator:
    name = "conclusion"

    def evaluate(
        self,
        *,
        scenario: Scenario,
        trace: list[TraceEvent],
        final: dict[str, Any],
    ) -> EvaluationResult:
        observed_facts = set(final.get("facts", []))
        claims = set(final.get("claims", []))
        required = set(scenario.conclusion_oracle.required_facts)
        forbidden = set(scenario.conclusion_oracle.forbidden_claims)
        missing = sorted(required - observed_facts)
        violations = sorted(forbidden & claims)
        uncertainty_ok = (
            not scenario.conclusion_oracle.uncertainty_required
            or bool(final.get("uncertainty"))
        )
        return EvaluationResult(
            self.name,
            (
                MetricResult("required_fact_coverage", 1.0 if not missing else 0.0, not missing, {"missing": missing}),
                MetricResult("forbidden_claim_rate", 0.0 if violations else 1.0, not violations, {"violations": violations}),
                MetricResult("uncertainty_disclosure", 1.0 if uncertainty_ok else 0.0, uncertainty_ok),
            ),
        )


class EscalationHandoffEvaluator:
    name = "escalation_handoff"

    def evaluate(
        self,
        *,
        scenario: Scenario,
        trace: list[TraceEvent],
        final: dict[str, Any],
    ) -> EvaluationResult:
        actual = final.get("decision")
        expected_human = "ESCALATE_HUMAN" in {item.value for item in scenario.decision_oracle.required}
        actual_human = actual == "ESCALATE_HUMAN"
        handoff = final.get("handoff") or {}
        required = list(scenario.communication_oracle.handoff_requirements)
        missing = [key for key in required if not handoff.get(key)]
        decision_ok = actual_human == expected_human
        handoff_ok = not missing if actual_human else True
        return EvaluationResult(
            self.name,
            (
                MetricResult("escalation_decision_correct", 1.0 if decision_ok else 0.0, decision_ok),
                MetricResult("handoff_completeness", 1.0 if handoff_ok else 0.0, handoff_ok, {"missing": missing}),
            ),
        )
