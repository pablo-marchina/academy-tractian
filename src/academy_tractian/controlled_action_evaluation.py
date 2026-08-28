from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from research.e2.models import RunTrace, ToolKind, ToolSpec

from .controlled_actions import ControlledActionRuntime
from .evaluation import (
    EvaluatedProductionRun,
    ProductionEvaluationCheck,
    ProductionEvaluationReport,
    ProductionEvaluator,
    TraceEvaluator,
)
from .runtime import ProductionRequest, canonical_tool_registry


CONTROLLED_ACTION_EVALUATOR_VERSION = "controlled-action-evaluator-v1"


def _check(
    name: str,
    passed: bool,
    *,
    blocking: bool = True,
    **details: Any,
) -> ProductionEvaluationCheck:
    return ProductionEvaluationCheck(
        name=name,
        passed=passed,
        blocking=blocking,
        details=details,
    )


class ControlledActionEvaluator:
    """Trace-only evaluator for the explicit controlled-action runtime profile.

    The validated ProductionEvaluator remains the baseline for lifecycle, tool contracts,
    identity/seed isolation, execution-chain integrity, policy containment, model-call provenance
    and terminal consistency. This evaluator replaces only the baseline assumptions that are
    intentionally different in the controlled profile:

    - scenario namespace is `prod-action:*` instead of `prod:*`;
    - an action call is permitted only when a matching B2 `ALLOWED` event precedes it and the
      supplied synthetic API result records `accepted=true`.

    No benchmark Scenario/oracle/private truth is accepted here.
    """

    def __init__(
        self,
        *,
        registry: Mapping[str, ToolSpec] | None = None,
        base_evaluator: TraceEvaluator | None = None,
    ) -> None:
        self.registry = dict(registry or canonical_tool_registry())
        self.base_evaluator = base_evaluator or ProductionEvaluator(registry=self.registry)

    def _controlled_identity_check(self, trace: RunTrace) -> ProductionEvaluationCheck:
        config_hash_ok = len(trace.config_hash) == 64 and all(
            character in "0123456789abcdef" for character in trace.config_hash
        )
        return _check(
            "production_trace_identity",
            trace.scenario_id.startswith("prod-action:")
            and bool(trace.run_id)
            and bool(trace.identity_binding_id)
            and trace.seed_ref in {"none", "runner-bound"}
            and config_hash_ok,
            scenario_id=trace.scenario_id,
            identity_binding_present=bool(trace.identity_binding_id),
            seed_ref=trace.seed_ref,
            config_hash_valid=config_hash_ok,
            controlled_action_evaluator_version=CONTROLLED_ACTION_EVALUATOR_VERSION,
        )

    def _controlled_action_check(self, trace: RunTrace) -> ProductionEvaluationCheck:
        events = trace.events
        action_call_indices = [
            index
            for index, event in enumerate(events)
            if event.event_type == "tool_call"
            and event.tool_name in self.registry
            and self.registry[event.tool_name].kind is ToolKind.ACTION
        ]
        used_allowed_policy: set[int] = set()
        issues: list[dict[str, Any]] = []
        accepted_actions: list[dict[str, Any]] = []
        previous_call_index = -1

        for ordinal, call_index in enumerate(action_call_indices):
            call = events[call_index]
            next_action_call = (
                action_call_indices[ordinal + 1]
                if ordinal + 1 < len(action_call_indices)
                else len(events)
            )
            allowed_candidates = [
                index
                for index in range(previous_call_index + 1, call_index)
                if events[index].event_type == "policy_check"
                and events[index].tool_name == call.tool_name
                and events[index].metadata.get("stage") == "B2"
                and events[index].metadata.get("allowed") is True
                and index not in used_allowed_policy
            ]
            if not allowed_candidates:
                issues.append(
                    {
                        "sequence": call.sequence,
                        "tool_name": call.tool_name,
                        "code": "ACTION_CALL_WITHOUT_B2_ALLOW",
                    }
                )
            else:
                used_allowed_policy.add(allowed_candidates[-1])

            result_candidates = [
                event
                for event in events[call_index + 1 : next_action_call]
                if event.event_type == "tool_result" and event.tool_name == call.tool_name
            ]
            if not result_candidates:
                issues.append(
                    {
                        "sequence": call.sequence,
                        "tool_name": call.tool_name,
                        "code": "ACTION_RESULT_MISSING",
                    }
                )
                previous_call_index = call_index
                continue

            result_event = result_candidates[0]
            result_record = result_event.result if isinstance(result_event.result, dict) else {}
            body = result_record.get("body") if isinstance(result_record, dict) else None
            accepted = isinstance(body, dict) and body.get("accepted") is True
            if not accepted:
                issues.append(
                    {
                        "sequence": call.sequence,
                        "tool_name": call.tool_name,
                        "code": "ACTION_NOT_ACCEPTED",
                        "status_code": result_event.metadata.get("status_code"),
                    }
                )
            else:
                accepted_actions.append(
                    {
                        "sequence": call.sequence,
                        "tool_name": call.tool_name,
                        "status_code": result_event.metadata.get("status_code"),
                    }
                )
            previous_call_index = call_index

        allowed_action_policy_indices = [
            index
            for index, event in enumerate(events)
            if event.event_type == "policy_check"
            and event.tool_name in self.registry
            and self.registry[event.tool_name].kind is ToolKind.ACTION
            and event.metadata.get("stage") == "B2"
            and event.metadata.get("allowed") is True
        ]
        unmatched_allowed = [
            events[index].sequence
            for index in allowed_action_policy_indices
            if index not in used_allowed_policy
        ]
        if unmatched_allowed:
            issues.append(
                {
                    "code": "B2_ALLOW_WITHOUT_ACTION_CALL",
                    "sequences": unmatched_allowed,
                }
            )

        return _check(
            "controlled_action_execution",
            not issues,
            action_call_count=len(action_call_indices),
            accepted_action_count=len(accepted_actions),
            accepted_actions=accepted_actions,
            issues=issues,
            evaluator_version=CONTROLLED_ACTION_EVALUATOR_VERSION,
        )

    def evaluate(self, trace: RunTrace) -> ProductionEvaluationReport:
        base = self.base_evaluator.evaluate(trace)
        checks: list[ProductionEvaluationCheck] = []
        for check in base.checks:
            if check.name == "production_trace_identity":
                checks.append(self._controlled_identity_check(trace))
                continue
            if check.name == "read_only_action_safety":
                continue
            checks.append(check)

        checks.append(self._controlled_action_check(trace))
        blocking_pass = all(check.passed for check in checks if check.blocking)
        return ProductionEvaluationReport(
            run_id=base.run_id,
            scenario_id=base.scenario_id,
            config_hash=base.config_hash,
            trace_sha256=base.trace_sha256,
            blocking_pass=blocking_pass,
            checks=tuple(checks),
        )


@dataclass
class IntegratedControlledActionRunner:
    """Run the controlled action profile once and evaluate that exact captured trace."""

    runtime: ControlledActionRuntime
    evaluator: TraceEvaluator

    @classmethod
    def with_default_evaluator(
        cls,
        *,
        runtime: ControlledActionRuntime,
    ) -> "IntegratedControlledActionRunner":
        return cls(
            runtime=runtime,
            evaluator=ControlledActionEvaluator(registry=runtime.registry),
        )

    def run(self, request: ProductionRequest) -> EvaluatedProductionRun:
        trace = self.runtime.run(request)
        evaluation = self.evaluator.evaluate(trace)
        return EvaluatedProductionRun(trace=trace, evaluation=evaluation)
