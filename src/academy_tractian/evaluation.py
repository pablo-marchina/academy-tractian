from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Literal, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.binding import MODEL_CONTROLLED_FIELDS
from research.e2.models import Decision, ResponseMode, RunTrace, ToolKind, ToolSpec, TraceEvent
from research.e2.trace import validate_trace
from research.e2.validation import validate_arguments

from .decision_source import ProviderModelCallRecord
from .runtime import ProductionRequest, ProductionRuntime, canonical_tool_registry


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProductionEvaluationPolicy(_FrozenModel):
    """Deterministic policy for production trace evaluation.

    Provider-free remains the default. Traced-provider mode is structural/provenance validation
    only; it does not authorize a provider call or claim semantic task correctness.
    """

    schema_version: Literal["prod-eval-policy-v2"] = "prod-eval-policy-v2"
    provider_free: bool = True
    require_model_call_provenance: bool = False
    read_only: Literal[True] = True
    require_production_scenario_prefix: Literal[True] = True

    @model_validator(mode="after")
    def validate_provider_mode(self) -> "ProductionEvaluationPolicy":
        if self.provider_free == self.require_model_call_provenance:
            raise ValueError(
                "evaluation policy must choose exactly one provider mode: "
                "provider_free or require_model_call_provenance"
            )
        return self


class ProductionEvaluationCheck(_FrozenModel):
    name: str = Field(min_length=1)
    passed: bool
    blocking: bool = True
    details: dict[str, Any] = Field(default_factory=dict)


class ProductionEvaluationReport(_FrozenModel):
    schema_version: Literal["prod-eval-v1"] = "prod-eval-v1"
    run_id: str
    scenario_id: str
    config_hash: str
    trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    blocking_pass: bool
    checks: tuple[ProductionEvaluationCheck, ...]

    @property
    def passed(self) -> bool:
        return self.blocking_pass

    def by_name(self) -> dict[str, ProductionEvaluationCheck]:
        return {check.name: check for check in self.checks}


class TraceEvaluator(Protocol):
    def evaluate(self, trace: RunTrace) -> ProductionEvaluationReport: ...


@dataclass(frozen=True)
class EvaluatedProductionRun:
    trace: RunTrace
    evaluation: ProductionEvaluationReport


def _canonical_trace_hash(trace: RunTrace) -> str:
    payload = json.dumps(
        trace.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


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


def _events(trace: RunTrace, event_type: str) -> list[TraceEvent]:
    return [event for event in trace.events if event.event_type == event_type]


def _final_payload(trace: RunTrace) -> dict[str, Any] | None:
    finals = _events(trace, "final_response")
    if len(finals) != 1 or not isinstance(finals[0].result, dict):
        return None
    return dict(finals[0].result)


def _execution_chain_issues(trace: RunTrace) -> list[dict[str, Any]]:
    """Validate executed proposal/call/result/observation chains without reading response bodies."""

    events = trace.events
    call_indices = [i for i, event in enumerate(events) if event.event_type == "tool_call"]
    used_proposals: set[int] = set()
    used_results: set[int] = set()
    used_observations: set[int] = set()
    issues: list[dict[str, Any]] = []
    final = _final_payload(trace) or {}
    terminal_reason = final.get("reason_code")

    previous_call_index = -1
    for ordinal, call_index in enumerate(call_indices):
        call = events[call_index]
        next_call_index = call_indices[ordinal + 1] if ordinal + 1 < len(call_indices) else len(events)

        proposal_candidates = [
            i
            for i in range(previous_call_index + 1, call_index)
            if events[i].event_type == "tool_proposal"
            and events[i].tool_name == call.tool_name
            and i not in used_proposals
        ]
        if not proposal_candidates:
            issues.append(
                {
                    "sequence": call.sequence,
                    "tool_name": call.tool_name,
                    "code": "MISSING_PROPOSAL",
                }
            )
        else:
            proposal_index = proposal_candidates[-1]
            used_proposals.add(proposal_index)
            proposal = events[proposal_index]
            if (proposal.arguments or {}) != (call.arguments or {}):
                issues.append(
                    {
                        "sequence": call.sequence,
                        "tool_name": call.tool_name,
                        "code": "PROPOSAL_CALL_ARGUMENT_MISMATCH",
                    }
                )

        result_candidates = [
            i
            for i in range(call_index + 1, next_call_index)
            if events[i].event_type == "tool_result"
            and events[i].tool_name == call.tool_name
            and i not in used_results
        ]
        if not result_candidates:
            is_last_call = ordinal == len(call_indices) - 1
            if not (is_last_call and terminal_reason == "TOOL_BOUNDARY_FAILURE"):
                issues.append(
                    {
                        "sequence": call.sequence,
                        "tool_name": call.tool_name,
                        "code": "MISSING_TOOL_RESULT",
                    }
                )
            previous_call_index = call_index
            continue

        result_index = result_candidates[0]
        used_results.add(result_index)
        observation_candidates = [
            i
            for i in range(result_index + 1, next_call_index)
            if events[i].event_type == "observation"
            and events[i].tool_name == call.tool_name
            and events[i].metadata.get("controller_generated") is not True
            and i not in used_observations
        ]
        if not observation_candidates:
            issues.append(
                {
                    "sequence": call.sequence,
                    "tool_name": call.tool_name,
                    "code": "MISSING_OBSERVATION",
                }
            )
        else:
            used_observations.add(observation_candidates[0])

        previous_call_index = call_index

    unmatched_results = [
        event.sequence
        for i, event in enumerate(events)
        if event.event_type == "tool_result" and i not in used_results
    ]
    if unmatched_results:
        issues.append({"code": "UNMATCHED_TOOL_RESULT", "sequences": unmatched_results})

    unmatched_observations = [
        event.sequence
        for i, event in enumerate(events)
        if event.event_type == "observation"
        and event.metadata.get("controller_generated") is not True
        and i not in used_observations
    ]
    if unmatched_observations:
        issues.append(
            {"code": "UNMATCHED_OBSERVATION", "sequences": unmatched_observations}
        )

    return issues


def _model_call_provenance(
    trace: RunTrace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate sanitized model-call records and their controller ordering without raw payloads."""

    events = trace.events
    model_indices = [i for i, event in enumerate(events) if event.event_type == "model_call"]
    issues: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    parsed: list[tuple[int, ProviderModelCallRecord]] = []
    seen_call_ids: set[str] = set()

    for index in model_indices:
        event = events[index]
        if event.tool_name is not None or event.arguments is not None or event.result is not None:
            issues.append({"sequence": event.sequence, "code": "MODEL_CALL_HAS_RAW_EVENT_PAYLOAD"})
        try:
            record = ProviderModelCallRecord.from_trace_event(
                call_id=event.call_id,
                metadata=event.metadata,
            )
        except Exception:
            issues.append({"sequence": event.sequence, "code": "INVALID_MODEL_CALL_RECORD"})
            continue

        if record.call_id in seen_call_ids:
            issues.append({"sequence": event.sequence, "code": "DUPLICATE_MODEL_CALL_ID"})
        seen_call_ids.add(record.call_id)
        parsed.append((index, record))
        summaries.append(
            {
                "sequence": event.sequence,
                "call_id": record.call_id,
                "provider_id": record.provider_id,
                "model_id": record.model_id,
                "route_id": record.route_id,
                "live_call": record.live_call,
                "outcome": record.outcome,
                "decision_kind": None if record.decision_kind is None else record.decision_kind.value,
                "failure_code": record.failure_code,
                "turn_index": record.turn_index,
                "tool_call_count": record.tool_call_count,
                "latency_ms": record.latency_ms,
            }
        )

    for ordinal, (index, record) in enumerate(parsed):
        next_model_index = parsed[ordinal + 1][0] if ordinal + 1 < len(parsed) else len(events)
        decisions = [
            event
            for event in events[index + 1 : next_model_index]
            if event.event_type == "decision"
        ]

        if record.outcome == "success":
            if len(decisions) != 1:
                issues.append(
                    {
                        "sequence": events[index].sequence,
                        "code": "MODEL_CALL_DECISION_COUNT_MISMATCH",
                        "decision_count": len(decisions),
                    }
                )
                continue
            decision = decisions[0]
            result = decision.result if isinstance(decision.result, dict) else {}
            expected_kind = record.decision_kind.value if record.decision_kind is not None else None
            if result.get("kind") != expected_kind:
                issues.append(
                    {
                        "sequence": events[index].sequence,
                        "code": "MODEL_CALL_DECISION_KIND_MISMATCH",
                    }
                )
            if result.get("turn_index") != record.turn_index:
                issues.append(
                    {
                        "sequence": events[index].sequence,
                        "code": "MODEL_CALL_TURN_INDEX_MISMATCH",
                    }
                )
            if result.get("tool_call_count") != record.tool_call_count:
                issues.append(
                    {
                        "sequence": events[index].sequence,
                        "code": "MODEL_CALL_TOOL_COUNT_MISMATCH",
                    }
                )
        else:
            if decisions:
                issues.append(
                    {
                        "sequence": events[index].sequence,
                        "code": "FAILED_MODEL_CALL_HAS_DECISION",
                    }
                )
            if ordinal + 1 < len(parsed):
                issues.append(
                    {
                        "sequence": events[index].sequence,
                        "code": "FAILED_MODEL_CALL_NOT_TERMINAL",
                    }
                )

    failure_records = [record for _, record in parsed if record.outcome == "failure"]
    if failure_records:
        final = _final_payload(trace) or {}
        if final.get("reason_code") != "DECISION_SOURCE_FAILURE":
            issues.append({"code": "FAILED_MODEL_CALL_TERMINAL_REASON_MISMATCH"})

    return issues, summaries


class ProductionEvaluator:
    """Trace-only deterministic evaluator for the production runtime boundary.

    It intentionally does not accept benchmark scenarios, expected paths, private references,
    semantic judges, model clients or provider clients. The evaluator can establish structural,
    provenance and safety properties visible in the production trace; it cannot establish
    semantic task correctness that is not represented by public deterministic contracts.
    """

    def __init__(
        self,
        *,
        registry: Mapping[str, ToolSpec] | None = None,
        policy: ProductionEvaluationPolicy | None = None,
    ) -> None:
        self.registry = dict(registry or canonical_tool_registry())
        self.policy = policy or ProductionEvaluationPolicy()

    def evaluate(self, trace: RunTrace) -> ProductionEvaluationReport:
        checks: list[ProductionEvaluationCheck] = []

        lifecycle_errors = validate_trace(trace)
        finals = _events(trace, "final_response")
        finished = _events(trace, "run_finished")
        lifecycle_ok = (
            not lifecycle_errors
            and len(finals) == 1
            and len(finished) == 1
            and trace.events[-1].event_type == "run_finished"
            and finals[0].sequence == finished[0].sequence - 1
        )
        checks.append(
            _check(
                "trace_lifecycle",
                lifecycle_ok,
                errors=lifecycle_errors,
                final_response_count=len(finals),
                run_finished_count=len(finished),
            )
        )

        production_namespace_ok = (
            not self.policy.require_production_scenario_prefix
            or trace.scenario_id.startswith("prod:")
        )
        config_hash_ok = len(trace.config_hash) == 64 and all(
            character in "0123456789abcdef" for character in trace.config_hash
        )
        checks.append(
            _check(
                "production_trace_identity",
                production_namespace_ok
                and bool(trace.run_id)
                and bool(trace.identity_binding_id)
                and trace.seed_ref in {"none", "runner-bound"}
                and config_hash_ok,
                scenario_id=trace.scenario_id,
                identity_binding_present=bool(trace.identity_binding_id),
                seed_ref=trace.seed_ref,
                config_hash_valid=config_hash_ok,
            )
        )

        proposal_issues: list[dict[str, Any]] = []
        unknown_tools: list[dict[str, Any]] = []
        for event in _events(trace, "tool_proposal"):
            if not event.tool_name or event.tool_name not in self.registry:
                unknown_tools.append(
                    {"sequence": event.sequence, "tool_name": event.tool_name}
                )
                continue
            tool = self.registry[event.tool_name]
            arguments = dict(event.arguments or {})
            issues = validate_arguments(tool, arguments)
            if issues:
                proposal_issues.append(
                    {
                        "sequence": event.sequence,
                        "tool_name": event.tool_name,
                        "issue_codes": [issue.code for issue in issues],
                    }
                )
        checks.append(
            _check(
                "proposal_contract_validity",
                not unknown_tools and not proposal_issues,
                unknown_tools=unknown_tools,
                invalid_proposals=proposal_issues,
            )
        )

        controlled_field_events: list[dict[str, Any]] = []
        for event in trace.events:
            if event.event_type not in {"tool_proposal", "tool_call"}:
                continue
            arguments = event.arguments or {}
            forbidden = sorted(set(arguments) & MODEL_CONTROLLED_FIELDS)
            if forbidden:
                controlled_field_events.append(
                    {
                        "sequence": event.sequence,
                        "event_type": event.event_type,
                        "tool_name": event.tool_name,
                        "fields": forbidden,
                    }
                )
        checks.append(
            _check(
                "identity_seed_model_isolation",
                not controlled_field_events,
                violations=controlled_field_events,
            )
        )

        execution_issues = _execution_chain_issues(trace)
        checks.append(
            _check(
                "execution_chain_integrity",
                not execution_issues,
                issues=execution_issues,
            )
        )

        denied_policy_events = [
            event
            for event in _events(trace, "policy_check")
            if event.metadata.get("allowed") is False
        ]
        uncontained = [
            {
                "sequence": event.sequence,
                "tool_name": event.tool_name,
                "stage": event.metadata.get("stage"),
                "violation": event.metadata.get("violation"),
            }
            for event in denied_policy_events
            if event.metadata.get("contained") is not True
        ]
        checks.append(
            _check(
                "policy_denial_containment",
                not uncontained,
                denied_count=len(denied_policy_events),
                uncontained=uncontained,
            )
        )
        checks.append(
            _check(
                "contained_policy_denials",
                True,
                blocking=False,
                count=len(denied_policy_events),
                denials=[
                    {
                        "sequence": event.sequence,
                        "tool_name": event.tool_name,
                        "stage": event.metadata.get("stage"),
                        "violation": event.metadata.get("violation"),
                    }
                    for event in denied_policy_events
                ],
            )
        )

        action_calls: list[dict[str, Any]] = []
        for event in _events(trace, "tool_call"):
            tool = self.registry.get(event.tool_name or "")
            if tool is not None and tool.kind is ToolKind.ACTION:
                action_calls.append(
                    {"sequence": event.sequence, "tool_name": event.tool_name}
                )
        allowed_action_policy = [
            {
                "sequence": event.sequence,
                "tool_name": event.tool_name,
                "stage": event.metadata.get("stage"),
            }
            for event in _events(trace, "policy_check")
            if event.metadata.get("stage") == "B2"
            and event.metadata.get("allowed") is True
            and (self.registry.get(event.tool_name or "") is not None)
            and self.registry[event.tool_name or ""].kind is ToolKind.ACTION
        ]
        read_only_ok = (
            not self.policy.read_only
            or (not action_calls and not allowed_action_policy)
        )
        checks.append(
            _check(
                "read_only_action_safety",
                read_only_ok,
                executed_actions=action_calls,
                allowed_action_policy_events=allowed_action_policy,
            )
        )

        model_calls = _events(trace, "model_call")
        checks.append(
            _check(
                "provider_free_trace",
                not self.policy.provider_free or not model_calls,
                model_call_count=len(model_calls),
            )
        )

        provenance_issues, provenance_summaries = _model_call_provenance(trace)
        provenance_ok = (
            (self.policy.provider_free and not model_calls and not provenance_issues)
            or (
                self.policy.require_model_call_provenance
                and bool(model_calls)
                and not provenance_issues
                and len(provenance_summaries) == len(model_calls)
            )
        )
        checks.append(
            _check(
                "model_call_provenance",
                provenance_ok,
                mode=(
                    "provider_free"
                    if self.policy.provider_free
                    else "traced_provider"
                ),
                model_call_count=len(model_calls),
                issues=provenance_issues,
                calls=provenance_summaries,
            )
        )

        final = _final_payload(trace)
        terminal_issues: list[str] = []
        if final is None:
            terminal_issues.append("MISSING_OR_NON_OBJECT_FINAL")
        else:
            decision = final.get("decision")
            response_mode = final.get("response_mode")
            controller_decision = final.get("controller_decision")
            valid_decisions = {member.value for member in Decision}
            valid_response_modes = {member.value for member in ResponseMode}
            if decision not in valid_decisions:
                terminal_issues.append("INVALID_DECISION")
            if response_mode not in valid_response_modes:
                terminal_issues.append("INVALID_RESPONSE_MODE")

            expected_decision = {
                "CLARIFY": Decision.ASK_CLARIFICATION.value,
                "ESCALATE": Decision.ESCALATE_HUMAN.value,
                "ABSTAIN": Decision.ABSTAIN.value,
            }.get(controller_decision)
            if expected_decision is not None and decision != expected_decision:
                terminal_issues.append("CONTROLLER_DECISION_MISMATCH")

            safe_failure_reasons = {
                "DECISION_SOURCE_FAILURE",
                "DECISION_SOURCE_AUDIT_FAILURE",
                "TOOL_BOUNDARY_FAILURE",
                "TOOL_CALL_BUDGET_EXHAUSTED",
                "TURN_BUDGET_EXHAUSTED",
            }
            if final.get("reason_code") in safe_failure_reasons:
                if decision != Decision.ABSTAIN.value or controller_decision != "ABSTAIN":
                    terminal_issues.append("FAILURE_NOT_SAFE_ABSTENTION")

            escalation_count = len(_events(trace, "escalation"))
            if controller_decision == "ESCALATE" and escalation_count != 1:
                terminal_issues.append("ESCALATION_EVENT_MISMATCH")

        checks.append(
            _check(
                "terminal_consistency",
                not terminal_issues,
                issues=terminal_issues,
                controller_decision=None if final is None else final.get("controller_decision"),
                decision=None if final is None else final.get("decision"),
                reason_code=None if final is None else final.get("reason_code"),
            )
        )

        blocking_pass = all(
            check.passed for check in checks if check.blocking
        )
        return ProductionEvaluationReport(
            run_id=trace.run_id,
            scenario_id=trace.scenario_id,
            config_hash=trace.config_hash,
            trace_sha256=_canonical_trace_hash(trace),
            blocking_pass=blocking_pass,
            checks=tuple(checks),
        )


class IntegratedProductionRunner:
    """Runs the production runtime once and evaluates that exact captured trace."""

    def __init__(
        self,
        *,
        runtime: ProductionRuntime,
        evaluator: TraceEvaluator | None = None,
    ) -> None:
        self.runtime = runtime
        self.evaluator = evaluator or ProductionEvaluator(registry=runtime.registry)

    def run(self, request: ProductionRequest) -> EvaluatedProductionRun:
        trace = self.runtime.run(request)
        evaluation = self.evaluator.evaluate(trace)
        return EvaluatedProductionRun(trace=trace, evaluation=evaluation)
