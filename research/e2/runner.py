from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .action_gate import EvidenceAwareActionGate
from .models import ExecutionBinding, RunTrace, Scenario, ToolKind, ToolSpec, TraceEvent
from .policy import ResourcePolicy
from .replay import ReplayStore
from .trace import append_event, validate_trace
from .transport import RequestTransport, TransportResponse, build_b0_request
from .validation import validate_arguments


@dataclass(frozen=True)
class ToolExecution:
    tool_name: str
    executed: bool
    blocked_code: str | None = None
    response: TransportResponse | None = None


def _response_record(response: TransportResponse) -> dict[str, Any]:
    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.body,
    }


def _response_from_record(record: dict[str, Any]) -> TransportResponse:
    return TransportResponse(
        status_code=int(record["status_code"]),
        headers=dict(record.get("headers") or {}),
        body=record.get("body"),
    )


class HarnessRunner:
    """Framework-neutral execution harness.

    This class does not implement agent reasoning. It executes tool proposals emitted by an
    external agent/runtime and records enough evidence for B0-B3 experiments, replay and
    deterministic evaluation.
    """

    def __init__(
        self,
        *,
        run_id: str,
        scenario_id: str,
        config_hash: str,
        registry: dict[str, ToolSpec],
        binding: ExecutionBinding,
        transport: RequestTransport | None,
        replay: ReplayStore | None = None,
        execution_mode: Literal["live", "replay"] = "live",
        strict_arguments: bool = False,
        resource_policy: ResourcePolicy | None = None,
        action_gate: EvidenceAwareActionGate | None = None,
        scenario: Scenario | None = None,
    ) -> None:
        if execution_mode == "live" and transport is None:
            raise ValueError("live execution requires a transport")
        if execution_mode == "replay" and replay is None:
            raise ValueError("replay execution requires a ReplayStore")
        if action_gate is not None and scenario is None:
            raise ValueError("B3 action gate requires a Scenario")

        self.registry = registry
        self.binding = binding
        self.transport = transport
        self.replay = replay or ReplayStore()
        self.execution_mode = execution_mode
        self.strict_arguments = strict_arguments
        self.resource_policy = resource_policy
        self.action_gate = action_gate
        self.scenario = scenario
        self.trace = RunTrace(
            run_id=run_id,
            scenario_id=scenario_id,
            config_hash=config_hash,
            identity_binding_id=binding.identity_id,
            seed_ref="runner-bound" if binding.seed is not None else "none",
            events=[TraceEvent(sequence=0, event_type="run_started", metadata={"execution_mode": execution_mode})],
        )

    def _emit(self, event_type: str, **kwargs: Any) -> None:
        self.trace = append_event(
            self.trace,
            TraceEvent(sequence=len(self.trace.events), event_type=event_type, **kwargs),
        )

    def _block(self, *, tool: ToolSpec, code: str, reason: str, stage: str) -> ToolExecution:
        self._emit(
            "policy_check",
            tool_name=tool.name,
            metadata={"allowed": False, "violation": code, "reason": reason, "stage": stage},
        )
        return ToolExecution(tool_name=tool.name, executed=False, blocked_code=code)

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        evidence_id: str | None = None,
    ) -> ToolExecution:
        if tool_name not in self.registry:
            raise KeyError(tool_name)
        tool = self.registry[tool_name]

        # Preserve the model/runtime proposal separately from the eventual executed request.
        self._emit("tool_proposal", tool_name=tool.name, arguments=dict(arguments))

        if self.strict_arguments:
            issues = validate_arguments(tool, arguments)
            if issues:
                return self._block(
                    tool=tool,
                    code="ARGUMENT_INVALID",
                    reason="; ".join(f"{issue.code}:{issue.field or ''}" for issue in issues),
                    stage="B1",
                )

        if self.resource_policy is not None and tool.kind is ToolKind.ACTION:
            decision = self.resource_policy.check(tool, arguments)
            self._emit(
                "policy_check",
                tool_name=tool.name,
                metadata={
                    "allowed": decision.allowed,
                    "violation": None if decision.allowed else decision.code,
                    "reason": decision.reason,
                    "stage": "B2",
                },
            )
            if not decision.allowed:
                return ToolExecution(tool_name=tool.name, executed=False, blocked_code=decision.code)

        if self.action_gate is not None and tool.kind is ToolKind.ACTION:
            assert self.scenario is not None
            decision = self.action_gate.check(
                scenario=self.scenario,
                tool=tool,
                arguments=arguments,
                trace=list(self.trace.events),
            )
            self._emit(
                "policy_check",
                tool_name=tool.name,
                metadata={
                    "allowed": decision.allowed,
                    "violation": None if decision.allowed else decision.code,
                    "reason": decision.reason,
                    "stage": "B3",
                },
            )
            if not decision.allowed:
                return ToolExecution(tool_name=tool.name, executed=False, blocked_code=decision.code)

        request = build_b0_request(tool, arguments, self.binding)
        request_record = request.model_dump(mode="json")
        self._emit(
            "tool_call",
            tool_name=tool.name,
            arguments=dict(arguments),
            metadata={
                "method": tool.method,
                "path": tool.path_template,
                "resolved_path": request.path,
                "kind": tool.kind.value,
            },
        )

        if self.execution_mode == "replay":
            response = _response_from_record(self.replay.replay(request_record))
        else:
            assert self.transport is not None
            response = self.transport.request(request)
            self.replay.record(request_record, _response_record(response))

        result = _response_record(response)
        self._emit(
            "tool_result",
            tool_name=tool.name,
            result=result,
            metadata={"status_code": response.status_code},
        )
        self._emit(
            "observation",
            tool_name=tool.name,
            result=response.body,
            metadata={
                "evidence_id": evidence_id,
                "status_code": response.status_code,
            },
        )
        return ToolExecution(tool_name=tool.name, executed=True, response=response)

    def finish(self, final: dict[str, Any]) -> RunTrace:
        self._emit("final_response", result=final)
        self._emit("run_finished")
        errors = validate_trace(self.trace)
        if errors:
            raise ValueError("invalid integrated trace: " + "; ".join(errors))
        return self.trace
