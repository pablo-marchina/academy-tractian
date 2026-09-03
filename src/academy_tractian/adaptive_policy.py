from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    DecisionSource,
    DecisionSourceAuditRecord,
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


AdaptivePolicyOutcome = Literal["CONTINUE", "SAFE_ABSTAIN", "BASELINE_FALLBACK"]


class AdaptiveSoftBudgetPolicyConfig(_FrozenModel):
    """Candidate-only soft stopping policy inside immutable controller hard caps.

    This policy cannot authorize tools, increase budgets, change permissions or execute actions.
    Its only behavioral intervention is to replace a proposed TOOL decision with safe ABSTAIN
    after repeated observable non-progress.
    """

    schema_version: Literal["adaptive-soft-budget-policy-v1"] = "adaptive-soft-budget-policy-v1"
    policy_id: Literal["repeated-nonprogress-soft-stop-v1"] = "repeated-nonprogress-soft-stop-v1"
    minimum_tool_calls_before_stop: int = Field(default=2, ge=1, le=6)
    consecutive_nonprogress_limit: int = Field(default=2, ge=1, le=6)


class AdaptivePolicyEvaluation(_FrozenModel):
    schema_version: Literal["adaptive-policy-evaluation-v1"] = "adaptive-policy-evaluation-v1"
    policy_id: str = Field(min_length=1)
    policy_config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    turn_index: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    proposed_kind: ControllerDecisionKind
    consecutive_nonprogress: int = Field(ge=0)
    outcome: AdaptivePolicyOutcome
    reason_code: str | None = None


class AdaptiveStoppingPolicy(Protocol):
    @property
    def config(self) -> AdaptiveSoftBudgetPolicyConfig: ...

    @property
    def config_sha256(self) -> str: ...

    def evaluate(
        self,
        *,
        context: ControllerContext,
        proposed_decision: ControllerDecision,
    ) -> AdaptivePolicyEvaluation: ...


def _canonical_sha256(payload: Any) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def _consecutive_nonprogress(context: ControllerContext) -> int:
    """Count the trailing observable failure/blocked streak without reading response bodies."""

    count = 0
    for observation in reversed(context.observations):
        if observation.status not in {"failure", "blocked"}:
            break
        count += 1
    return count


class RepeatedNonprogressSoftStopPolicy:
    """Interpretable Experiment-A policy for bounded failure-conditioned early stopping."""

    def __init__(self, config: AdaptiveSoftBudgetPolicyConfig | None = None) -> None:
        self._config = config or AdaptiveSoftBudgetPolicyConfig()
        self._config_sha256 = _canonical_sha256(self._config.model_dump(mode="json"))

    @property
    def config(self) -> AdaptiveSoftBudgetPolicyConfig:
        return self._config

    @property
    def config_sha256(self) -> str:
        return self._config_sha256

    def evaluate(
        self,
        *,
        context: ControllerContext,
        proposed_decision: ControllerDecision,
    ) -> AdaptivePolicyEvaluation:
        streak = _consecutive_nonprogress(context)
        should_stop = (
            proposed_decision.kind is ControllerDecisionKind.TOOL
            and context.tool_call_count >= self.config.minimum_tool_calls_before_stop
            and streak >= self.config.consecutive_nonprogress_limit
        )
        return AdaptivePolicyEvaluation(
            policy_id=self.config.policy_id,
            policy_config_sha256=self.config_sha256,
            turn_index=context.turn_index,
            tool_call_count=context.tool_call_count,
            proposed_kind=proposed_decision.kind,
            consecutive_nonprogress=streak,
            outcome="SAFE_ABSTAIN" if should_stop else "CONTINUE",
            reason_code="REPEATED_NONPROGRESS" if should_stop else None,
        )


class AdaptiveStoppingDecisionSource(DecisionSource):
    """Candidate wrapper that is monotone with respect to agent autonomy.

    The wrapped source decides first. This wrapper can return that exact decision or replace a
    TOOL proposal with ABSTAIN. It can never create/modify a tool proposal or terminal success.
    If policy evaluation itself fails, the original decision is returned unchanged; deterministic
    controller/HarnessRunner safety boundaries therefore remain authoritative.
    """

    def __init__(
        self,
        *,
        source: DecisionSource,
        policy: AdaptiveStoppingPolicy | None = None,
    ) -> None:
        self.source = source
        self.policy = policy or RepeatedNonprogressSoftStopPolicy()
        self._pending_policy_records: list[AdaptivePolicyEvaluation] = []

    def decide(self, context: ControllerContext) -> ControllerDecision:
        proposed = self.source.decide(context)
        try:
            evaluation = self.policy.evaluate(
                context=context,
                proposed_decision=proposed,
            )
        except Exception:
            evaluation = AdaptivePolicyEvaluation(
                policy_id=self.policy.config.policy_id,
                policy_config_sha256=self.policy.config_sha256,
                turn_index=context.turn_index,
                tool_call_count=context.tool_call_count,
                proposed_kind=proposed.kind,
                consecutive_nonprogress=_consecutive_nonprogress(context),
                outcome="BASELINE_FALLBACK",
                reason_code="POLICY_EVALUATION_FAILURE",
            )
            self._pending_policy_records.append(evaluation)
            return proposed

        self._pending_policy_records.append(evaluation)
        if evaluation.outcome == "SAFE_ABSTAIN":
            # evaluate() may recommend stop only for TOOL, but keep this assertion local so an
            # invalid future policy cannot accidentally rewrite an already-terminal decision.
            if proposed.kind is not ControllerDecisionKind.TOOL:
                return proposed
            return ControllerDecision(
                kind=ControllerDecisionKind.ABSTAIN,
                reason_code="ADAPTIVE_SOFT_STOP_REPEATED_NONPROGRESS",
                message=(
                    "Investigation stopped safely after repeated non-progress; "
                    "no additional tool was executed."
                ),
            )
        return proposed

    def drain_policy_records(self) -> tuple[AdaptivePolicyEvaluation, ...]:
        records = tuple(self._pending_policy_records)
        self._pending_policy_records.clear()
        return records

    def drain_audit_records(self) -> tuple[DecisionSourceAuditRecord, ...]:
        """Preserve provider/model-call audit forwarding through the wrapper."""

        drain = getattr(self.source, "drain_audit_records", None)
        if drain is None:
            return ()
        if not callable(drain):
            raise TypeError("wrapped decision source audit drain must be callable")
        records = drain()
        if not isinstance(records, tuple):
            raise TypeError("wrapped decision source audit drain must return a tuple")
        return records
