from __future__ import annotations

import json

from research.e2.controller import (
    AgentController,
    ControllerContext,
    ControllerDecisionKind,
    ControllerObservation,
)
from research.e2.models import ToolKind


DUPLICATE_SUCCESSFUL_READ = "DUPLICATE_SUCCESSFUL_READ"


def _read_proposal_fingerprint(tool_name: str, arguments: dict[str, object]) -> str:
    return json.dumps(
        {"tool_name": tool_name, "arguments": arguments},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


class ProductionAgentController(AgentController):
    """Production-only controller hardening over the frozen ADR-004 controller.

    Historical E2 campaigns pin ``research.e2.controller`` by Git blob and must remain immutable.
    Production behavior may evolve here without rewriting those frozen experiments.

    Exact successful read proposals are idempotent evidence within one run. If a provider proposes
    the same read with the same canonical JSON arguments after it already succeeded, the duplicate
    is contained before transport, does not consume another tool-call slot, and is returned as a
    blocked observation so the provider can choose a different evidence step or terminate.
    """

    def run(self, user_request: str):
        observations: list[ControllerObservation] = []
        tool_call_count = 0
        successful_read_fingerprints: set[str] = set()

        for turn_index in range(self.limits.max_turns):
            context = ControllerContext(
                user_request=user_request,
                turn_index=turn_index,
                tool_call_count=tool_call_count,
                observations=tuple(observations),
            )
            try:
                decision = self.decision_source.decide(context)
            except Exception:
                try:
                    self._drain_decision_source_audit()
                except Exception:
                    return self._safe_abstain(
                        reason_code="DECISION_SOURCE_AUDIT_FAILURE",
                        message="Decision-source provenance failed validation; no further action was executed.",
                    )
                return self._safe_abstain(
                    reason_code="DECISION_SOURCE_FAILURE",
                    message="The decision source failed; no further action was executed.",
                )

            try:
                self._drain_decision_source_audit()
            except Exception:
                return self._safe_abstain(
                    reason_code="DECISION_SOURCE_AUDIT_FAILURE",
                    message="Decision-source provenance failed validation; no further action was executed.",
                )

            self._emit(
                "decision",
                result={
                    "kind": decision.kind.value,
                    "turn_index": turn_index,
                    "tool_call_count": tool_call_count,
                },
            )

            if decision.kind is not ControllerDecisionKind.TOOL:
                return self._finish_terminal(decision)

            assert decision.proposal is not None
            proposal = decision.proposal
            tool = self.runner.registry.get(proposal.tool_name)
            fingerprint: str | None = None
            if tool is not None and tool.kind is ToolKind.READ:
                fingerprint = _read_proposal_fingerprint(
                    proposal.tool_name,
                    dict(proposal.arguments),
                )
                if fingerprint in successful_read_fingerprints:
                    self._emit(
                        "tool_proposal",
                        tool_name=proposal.tool_name,
                        arguments=dict(proposal.arguments),
                    )
                    self._emit(
                        "policy_check",
                        tool_name=proposal.tool_name,
                        metadata={
                            "allowed": False,
                            "contained": True,
                            "violation": DUPLICATE_SUCCESSFUL_READ,
                            "reason": "exact successful read already observed in this run",
                            "stage": "PRODUCTION_CONTROLLER",
                        },
                    )
                    observation = ControllerObservation(
                        tool_name=proposal.tool_name,
                        status="blocked",
                        executed=False,
                        blocked_code=DUPLICATE_SUCCESSFUL_READ,
                    )
                    observations.append(observation)
                    self._emit(
                        "observation",
                        tool_name=proposal.tool_name,
                        result=observation.model_dump(mode="json"),
                        metadata={"controller_generated": True, "contained": True},
                    )
                    continue

            if tool_call_count >= self.limits.max_tool_calls:
                return self._safe_abstain(
                    reason_code="TOOL_CALL_BUDGET_EXHAUSTED",
                    message="The bounded tool-call budget was exhausted; no additional tool was executed.",
                )

            tool_call_count += 1
            try:
                execution = self.runner.execute_tool(
                    proposal.tool_name,
                    dict(proposal.arguments),
                    evidence_id=proposal.evidence_id,
                )
            except Exception:
                return self._safe_abstain(
                    reason_code="TOOL_BOUNDARY_FAILURE",
                    message="The deterministic tool boundary rejected or failed the proposal; execution stopped safely.",
                )

            observation = self._observation_from_execution(execution)
            observations.append(observation)
            if fingerprint is not None and observation.status == "success":
                successful_read_fingerprints.add(fingerprint)
            if not execution.executed:
                self._emit(
                    "observation",
                    tool_name=execution.tool_name,
                    result=observation.model_dump(mode="json"),
                    metadata={"controller_generated": True, "contained": True},
                )

        return self._safe_abstain(
            reason_code="TURN_BUDGET_EXHAUSTED",
            message="The bounded turn budget was exhausted; the controller stopped without further action.",
        )
