from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .evaluator_extensions import ArgumentEvaluator, ConclusionEvaluator, EscalationHandoffEvaluator
from .evaluators import ActionEvaluator, DecisionEvaluator, EvaluationResult, EvidenceEvaluator, PolicyEvaluator, SafetyEvaluator, TrajectoryEvaluator
from .models import Scenario, TraceEvent, ToolSpec


@dataclass(frozen=True)
class EvaluationBundle:
    results: tuple[EvaluationResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    def by_name(self) -> dict[str, EvaluationResult]:
        return {result.evaluator: result for result in self.results}


class EvaluationSuite:
    """Runs independent evaluators without collapsing them into an arbitrary weighted score."""

    def __init__(self, evaluators: Iterable[Any]) -> None:
        self.evaluators = tuple(evaluators)

    def evaluate(
        self,
        *,
        scenario: Scenario,
        trace: list[TraceEvent],
        final: dict[str, Any],
    ) -> EvaluationBundle:
        return EvaluationBundle(
            tuple(
                evaluator.evaluate(scenario=scenario, trace=trace, final=final)
                for evaluator in self.evaluators
            )
        )


def default_suite(registry: dict[str, ToolSpec]) -> EvaluationSuite:
    return EvaluationSuite(
        (
            TrajectoryEvaluator(),
            DecisionEvaluator(),
            ArgumentEvaluator(registry),
            EvidenceEvaluator(),
            PolicyEvaluator(),
            ActionEvaluator(),
            ConclusionEvaluator(),
            EscalationHandoffEvaluator(),
            SafetyEvaluator(),
        )
    )
