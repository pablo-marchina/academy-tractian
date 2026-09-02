from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from research.e2.binding import MODEL_CONTROLLED_FIELDS
from research.e2.models import RunTrace, ToolKind, ToolSpec
from research.e2.trace import validate_trace
from research.e2.validation import validate_arguments

from .action_safety import PRODUCTION_RUNTIME_CONTROLLED_ACTION_FIELDS
from .evaluation import ProductionEvaluationCheck, ProductionEvaluationReport
from .runtime import canonical_tool_registry


def _trace_hash(trace: RunTrace) -> str:
    payload = json.dumps(
        trace.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def _check(name: str, passed: bool, **details: Any) -> ProductionEvaluationCheck:
    return ProductionEvaluationCheck(name=name, passed=passed, blocking=True, details=details)


class ProductionActionEvaluator:
    """Trace-only deterministic evaluator for a confirmed action execution run."""

    def __init__(self, *, registry: Mapping[str, ToolSpec] | None = None) -> None:
        self.registry = dict(registry or canonical_tool_registry())

    def evaluate(self, trace: RunTrace) -> ProductionEvaluationReport:
        checks: list[ProductionEvaluationCheck] = []
        lifecycle_errors = validate_trace(trace)
        finals = [event for event in trace.events if event.event_type == "final_response"]
        finished = [event for event in trace.events if event.event_type == "run_finished"]
        checks.append(
            _check(
                "action_trace_lifecycle",
                not lifecycle_errors
                and len(finals) == 1
                and len(finished) == 1
                and trace.events[-1].event_type == "run_finished",
                errors=lifecycle_errors,
            )
        )

        config_hash_valid = len(trace.config_hash) == 64 and all(
            character in "0123456789abcdef" for character in trace.config_hash
        )
        checks.append(
            _check(
                "action_trace_identity",
                trace.scenario_id.startswith("prod:action:")
                and bool(trace.identity_binding_id)
                and trace.seed_ref == "none"
                and config_hash_valid,
                scenario_id=trace.scenario_id,
                config_hash_valid=config_hash_valid,
            )
        )

        proposals = [event for event in trace.events if event.event_type == "tool_proposal"]
        calls = [event for event in trace.events if event.event_type == "tool_call"]
        results = [event for event in trace.events if event.event_type == "tool_result"]
        observations = [event for event in trace.events if event.event_type == "observation"]
        policy = [event for event in trace.events if event.event_type == "policy_check"]
        exact_chain = (
            len(proposals) == len(calls) == len(results) == len(observations) == len(policy) == 1
        )
        tool_name = calls[0].tool_name if len(calls) == 1 else None
        tool = self.registry.get(tool_name or "")
        action_tool = tool is not None and tool.kind is ToolKind.ACTION
        checks.append(
            _check(
                "single_consequential_action_chain",
                exact_chain and action_tool,
                proposals=len(proposals),
                calls=len(calls),
                results=len(results),
                observations=len(observations),
                policies=len(policy),
                tool_name=tool_name,
            )
        )

        arguments = dict(calls[0].arguments or {}) if len(calls) == 1 else {}
        validation_issues = [] if tool is None else validate_arguments(tool, arguments)
        proposal_matches = (
            len(proposals) == 1
            and len(calls) == 1
            and proposals[0].tool_name == calls[0].tool_name
            and (proposals[0].arguments or {}) == (calls[0].arguments or {})
        )
        checks.append(
            _check(
                "action_argument_contract",
                bool(tool) and not validation_issues and proposal_matches,
                issue_codes=[item.code for item in validation_issues],
                proposal_matches=proposal_matches,
            )
        )

        forbidden_fields = sorted(
            set(arguments)
            & (set(MODEL_CONTROLLED_FIELDS) | set(PRODUCTION_RUNTIME_CONTROLLED_ACTION_FIELDS))
        )
        checks.append(
            _check(
                "action_runtime_context_isolation",
                not forbidden_fields,
                forbidden_fields=forbidden_fields,
            )
        )

        b2_allowed = (
            len(policy) == 1
            and policy[0].metadata.get("stage") == "B2"
            and policy[0].metadata.get("allowed") is True
            and policy[0].metadata.get("contained") is False
        )
        checks.append(
            _check(
                "action_policy_authorized",
                b2_allowed,
                violation=None if not policy else policy[0].metadata.get("violation"),
            )
        )

        result_record = results[0].result if len(results) == 1 and isinstance(results[0].result, dict) else {}
        result_body = result_record.get("body") if isinstance(result_record, dict) else None
        status_code = result_record.get("status_code") if isinstance(result_record, dict) else None
        final = finals[0].result if len(finals) == 1 and isinstance(finals[0].result, dict) else {}
        reason = final.get("reason_code") if isinstance(final, dict) else None
        accepted = isinstance(result_body, dict) and result_body.get("accepted") is True
        accepted_semantics_ok = (
            (reason == "ACTION_ACCEPTED" and accepted and isinstance(status_code, int) and 200 <= status_code < 300)
            or (reason in {"ACTION_NOT_ACCEPTED", "ACTION_EXECUTION_UNCERTAIN", "ACTION_BLOCKED"} and not accepted)
        )
        checks.append(
            _check(
                "tractian_action_acceptance_semantics",
                accepted_semantics_ok,
                terminal_reason=reason,
                accepted=accepted,
                status_code=status_code,
            )
        )

        blocking_pass = all(check.passed for check in checks if check.blocking)
        return ProductionEvaluationReport(
            run_id=trace.run_id,
            scenario_id=trace.scenario_id,
            config_hash=trace.config_hash,
            trace_sha256=_trace_hash(trace),
            blocking_pass=blocking_pass,
            checks=tuple(checks),
        )
