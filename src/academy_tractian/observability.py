from __future__ import annotations

from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from research.e2.models import RunTrace, TraceEvent

from .evaluation import ProductionEvaluationReport


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


OutputOrigin = Literal[
    "MODEL",
    "CONTROLLER",
    "POLICY",
    "TOOL",
    "OBSERVATION",
    "EVALUATOR",
    "SYSTEM",
]


class SafeEvent(_FrozenModel):
    schema_version: Literal["safe-observability-event-v1"] = "safe-observability-event-v1"
    event_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    event_type: str
    origin: OutputOrigin
    timestamp: str | None = None
    tool_name: str | None = None
    decision_kind: str | None = None
    provider_id: str | None = None
    model_id: str | None = None
    route_id: str | None = None
    live_call: bool | None = None
    outcome: str | None = None
    failure_code: str | None = None
    latency_ms: int | None = None
    turn_index: int | None = None
    tool_call_count: int | None = None
    argument_names: tuple[str, ...] = ()
    method: str | None = None
    path_template: str | None = None
    tool_kind: str | None = None
    status_code: int | None = None
    policy_stage: str | None = None
    policy_allowed: bool | None = None
    policy_contained: bool | None = None
    policy_violation: str | None = None
    evidence_id: str | None = None
    reason_code: str | None = None
    response_mode: str | None = None
    message: str | None = None


class SafeEvidenceRef(_FrozenModel):
    evidence_id: str
    run_id: str
    sequence: int = Field(ge=0)
    tool_name: str | None = None
    status_code: int | None = None


class SafeRun(_FrozenModel):
    schema_version: Literal["safe-observability-run-v1"] = "safe-observability-run-v1"
    run_id: str = Field(min_length=1)
    scenario_id: str
    config_hash: str
    event_count: int = Field(ge=0)
    model_calls: int = Field(ge=0)
    tool_proposals: int = Field(ge=0)
    tool_calls: int = Field(ge=0)
    policy_blocks: int = Field(ge=0)
    errors: int = Field(ge=0)
    terminal_decision: str | None = None
    terminal_response_mode: str | None = None
    terminal_reason_code: str | None = None
    terminal_message: str | None = None
    completed: bool


class SafeEvaluationCheck(_FrozenModel):
    name: str
    passed: bool
    blocking: bool


class SafeEvaluation(_FrozenModel):
    schema_version: Literal["safe-observability-evaluation-v1"] = "safe-observability-evaluation-v1"
    run_id: str
    blocking_pass: bool
    checks: tuple[SafeEvaluationCheck, ...]


def safe_run_id(raw_run_id: str) -> str:
    return "run_" + sha256(raw_run_id.encode("utf-8")).hexdigest()[:20]


def _scalar_text(value: Any, *, max_length: int = 4096) -> str | None:
    if not isinstance(value, str):
        return None
    if len(value) > max_length:
        return value[:max_length]
    return value


def _origin(event_type: str) -> OutputOrigin:
    if event_type == "model_call":
        return "MODEL"
    if event_type in {"decision", "state_change", "escalation", "final_response"}:
        return "CONTROLLER"
    if event_type == "policy_check":
        return "POLICY"
    if event_type in {"tool_proposal", "tool_call", "tool_result"}:
        return "TOOL"
    if event_type == "observation":
        return "OBSERVATION"
    return "SYSTEM"


def project_event(*, raw_run_id: str, event: TraceEvent) -> SafeEvent:
    run_id = safe_run_id(raw_run_id)
    result = event.result if isinstance(event.result, dict) else {}
    metadata = event.metadata

    fields: dict[str, Any] = {
        "event_id": f"{run_id}:{event.sequence}",
        "run_id": run_id,
        "sequence": event.sequence,
        "event_type": event.event_type,
        "origin": _origin(event.event_type),
        "timestamp": None if event.timestamp is None else event.timestamp.isoformat(),
        "tool_name": event.tool_name,
    }

    if event.event_type == "run_started":
        fields["outcome"] = _scalar_text(metadata.get("execution_mode"), max_length=64)
    elif event.event_type == "model_call":
        fields.update(
            provider_id=_scalar_text(metadata.get("provider_id"), max_length=256),
            model_id=_scalar_text(metadata.get("model_id"), max_length=256),
            route_id=_scalar_text(metadata.get("route_id"), max_length=256),
            live_call=metadata.get("live_call") if isinstance(metadata.get("live_call"), bool) else None,
            outcome=_scalar_text(metadata.get("outcome"), max_length=64),
            decision_kind=_scalar_text(metadata.get("decision_kind"), max_length=64),
            failure_code=_scalar_text(metadata.get("failure_code"), max_length=256),
            latency_ms=metadata.get("latency_ms") if isinstance(metadata.get("latency_ms"), int) else None,
            turn_index=metadata.get("turn_index") if isinstance(metadata.get("turn_index"), int) else None,
            tool_call_count=metadata.get("tool_call_count") if isinstance(metadata.get("tool_call_count"), int) else None,
        )
    elif event.event_type == "decision":
        fields.update(
            decision_kind=_scalar_text(result.get("kind"), max_length=64),
            turn_index=result.get("turn_index") if isinstance(result.get("turn_index"), int) else None,
            tool_call_count=result.get("tool_call_count") if isinstance(result.get("tool_call_count"), int) else None,
        )
    elif event.event_type == "tool_proposal":
        fields["argument_names"] = tuple(sorted((event.arguments or {}).keys()))
    elif event.event_type == "policy_check":
        fields.update(
            policy_stage=_scalar_text(metadata.get("stage"), max_length=64),
            policy_allowed=metadata.get("allowed") if isinstance(metadata.get("allowed"), bool) else None,
            policy_contained=metadata.get("contained") if isinstance(metadata.get("contained"), bool) else None,
            policy_violation=_scalar_text(metadata.get("violation"), max_length=256),
        )
    elif event.event_type == "tool_call":
        fields.update(
            argument_names=tuple(sorted((event.arguments or {}).keys())),
            method=_scalar_text(metadata.get("method"), max_length=16),
            path_template=_scalar_text(metadata.get("path"), max_length=512),
            tool_kind=_scalar_text(metadata.get("kind"), max_length=64),
        )
    elif event.event_type in {"tool_result", "observation"}:
        fields["status_code"] = metadata.get("status_code") if isinstance(metadata.get("status_code"), int) else None
        if event.event_type == "observation":
            fields["evidence_id"] = _scalar_text(metadata.get("evidence_id"), max_length=512)
    elif event.event_type in {"state_change", "escalation"}:
        fields["reason_code"] = _scalar_text(
            metadata.get("reason_code") if event.event_type == "state_change" else result.get("reason_code"),
            max_length=256,
        )
    elif event.event_type == "final_response":
        fields.update(
            decision_kind=_scalar_text(result.get("decision") or result.get("controller_decision"), max_length=64),
            response_mode=_scalar_text(result.get("response_mode"), max_length=64),
            reason_code=_scalar_text(result.get("reason_code"), max_length=256),
            message=_scalar_text(result.get("message"), max_length=4096),
        )
    elif event.event_type == "error":
        fields.update(
            failure_code=_scalar_text(metadata.get("failure_code"), max_length=256),
            reason_code=_scalar_text(metadata.get("reason_code"), max_length=256),
        )

    return SafeEvent(**fields)


def project_trace(trace: RunTrace) -> tuple[SafeRun, tuple[SafeEvent, ...], tuple[SafeEvidenceRef, ...]]:
    run_id = safe_run_id(trace.run_id)
    events = tuple(project_event(raw_run_id=trace.run_id, event=event) for event in trace.events)
    finals = [event for event in events if event.event_type == "final_response"]
    final = finals[-1] if finals else None
    evidence = tuple(
        SafeEvidenceRef(
            evidence_id=event.evidence_id,
            run_id=run_id,
            sequence=event.sequence,
            tool_name=event.tool_name,
            status_code=event.status_code,
        )
        for event in events
        if event.event_type == "observation" and event.evidence_id is not None
    )
    run = SafeRun(
        run_id=run_id,
        scenario_id=trace.scenario_id,
        config_hash=trace.config_hash,
        event_count=len(events),
        model_calls=sum(event.event_type == "model_call" for event in events),
        tool_proposals=sum(event.event_type == "tool_proposal" for event in events),
        tool_calls=sum(event.event_type == "tool_call" for event in events),
        policy_blocks=sum(
            event.event_type == "policy_check" and event.policy_allowed is False
            for event in events
        ),
        errors=sum(event.event_type == "error" for event in events),
        terminal_decision=None if final is None else final.decision_kind,
        terminal_response_mode=None if final is None else final.response_mode,
        terminal_reason_code=None if final is None else final.reason_code,
        terminal_message=None if final is None else final.message,
        completed=bool(events and events[-1].event_type == "run_finished"),
    )
    return run, events, evidence


def project_evaluation(report: ProductionEvaluationReport) -> SafeEvaluation:
    return SafeEvaluation(
        run_id=safe_run_id(report.run_id),
        blocking_pass=report.blocking_pass,
        checks=tuple(
            SafeEvaluationCheck(
                name=check.name,
                passed=check.passed,
                blocking=check.blocking,
            )
            for check in report.checks
        ),
    )
