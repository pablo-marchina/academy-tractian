from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RestartRecoveryObservation(_FrozenModel):
    """Sanitized observations from one promoted-topology restart campaign.

    The campaign intentionally carries only aggregate state-transition counts and boolean
    invariants. Run IDs, action IDs, tenants, users, tokens, raw arguments and traces stay in the
    trusted test harness and must never enter this model.
    """

    first_restart_runtime_interrupted: int = Field(ge=0)
    first_restart_action_execution_uncertain: int = Field(ge=0)
    first_restart_action_custody_uncertain: int = Field(ge=0)
    first_restart_ledger_uncertain: int = Field(ge=0)
    pending_confirmation_preserved: bool
    completed_runtime_preserved: bool
    failed_runtime_preserved: bool
    fresh_runtime_completed_after_recovery: bool
    cross_tenant_visibility_blocked: bool
    first_restart_provider_calls: int = Field(ge=0)
    first_restart_action_transport_calls: int = Field(ge=0)
    second_restart_new_runtime_recoveries: int = Field(ge=0)
    second_restart_new_action_custody_recoveries: int = Field(ge=0)
    second_restart_new_ledger_recoveries: int = Field(ge=0)
    second_restart_provider_calls: int = Field(ge=0)
    second_restart_action_transport_calls: int = Field(ge=0)


class RestartRecoveryReport(_FrozenModel):
    schema_version: Literal["restart-recovery-report-v1"] = "restart-recovery-report-v1"
    status: Literal["VERIFIED"] = "VERIFIED"
    interpretation: Literal["safety_contract_only"] = "safety_contract_only"
    production_availability_claim_ready: Literal[False] = False
    automatic_retry_count: Literal[0] = 0
    replay_count: Literal[0] = 0
    first_restart_runtime_interrupted: int
    first_restart_action_execution_uncertain: int
    first_restart_action_custody_uncertain: int
    first_restart_ledger_uncertain: int
    pending_confirmation_preserved: Literal[True] = True
    completed_runtime_preserved: Literal[True] = True
    failed_runtime_preserved: Literal[True] = True
    fresh_runtime_completed_after_recovery: Literal[True] = True
    cross_tenant_visibility_blocked: Literal[True] = True
    first_restart_provider_calls: Literal[0] = 0
    first_restart_action_transport_calls: Literal[0] = 0
    second_restart_new_runtime_recoveries: Literal[0] = 0
    second_restart_new_action_custody_recoveries: Literal[0] = 0
    second_restart_new_ledger_recoveries: Literal[0] = 0
    second_restart_provider_calls: Literal[0] = 0
    second_restart_action_transport_calls: Literal[0] = 0
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_hash(self) -> "RestartRecoveryReport":
        expected = _report_hash(self.model_dump(mode="json", exclude={"evidence_sha256"}))
        if self.evidence_sha256 != expected:
            raise ValueError("restart recovery report hash mismatch")
        return self


def _report_hash(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def verify_restart_recovery(observation: RestartRecoveryObservation) -> RestartRecoveryReport:
    """Fail closed unless every preregistered restart-safety invariant is satisfied."""

    if observation.first_restart_runtime_interrupted != 2:
        raise ValueError("expected exactly two orphaned runtime executions to become interrupted")
    if observation.first_restart_action_execution_uncertain != 1:
        raise ValueError("expected exactly one orphaned action execution to become uncertain")
    if observation.first_restart_action_custody_uncertain != 1:
        raise ValueError("expected exactly one executing action custody row to become uncertain")
    if observation.first_restart_ledger_uncertain != 1:
        raise ValueError("expected exactly one claimed action ledger row to become uncertain")

    required_true = {
        "pending_confirmation_preserved": observation.pending_confirmation_preserved,
        "completed_runtime_preserved": observation.completed_runtime_preserved,
        "failed_runtime_preserved": observation.failed_runtime_preserved,
        "fresh_runtime_completed_after_recovery": observation.fresh_runtime_completed_after_recovery,
        "cross_tenant_visibility_blocked": observation.cross_tenant_visibility_blocked,
    }
    failed = tuple(name for name, value in required_true.items() if not value)
    if failed:
        raise ValueError("restart recovery invariant failed: " + ",".join(failed))

    forbidden_counts = {
        "first_restart_provider_calls": observation.first_restart_provider_calls,
        "first_restart_action_transport_calls": observation.first_restart_action_transport_calls,
        "second_restart_new_runtime_recoveries": observation.second_restart_new_runtime_recoveries,
        "second_restart_new_action_custody_recoveries": observation.second_restart_new_action_custody_recoveries,
        "second_restart_new_ledger_recoveries": observation.second_restart_new_ledger_recoveries,
        "second_restart_provider_calls": observation.second_restart_provider_calls,
        "second_restart_action_transport_calls": observation.second_restart_action_transport_calls,
    }
    nonzero = tuple(name for name, value in forbidden_counts.items() if value != 0)
    if nonzero:
        raise ValueError("restart recovery performed forbidden work: " + ",".join(nonzero))

    payload: dict[str, object] = {
        "schema_version": "restart-recovery-report-v1",
        "status": "VERIFIED",
        "interpretation": "safety_contract_only",
        "production_availability_claim_ready": False,
        "automatic_retry_count": 0,
        "replay_count": 0,
        **observation.model_dump(mode="json"),
    }
    return RestartRecoveryReport(**payload, evidence_sha256=_report_hash(payload))
