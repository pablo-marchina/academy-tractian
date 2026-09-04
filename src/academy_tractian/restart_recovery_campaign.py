from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


class RestartRecoveryProtocol(_FrozenModel):
    schema_version: Literal["restart-recovery-protocol-v1"] = "restart-recovery-protocol-v1"
    status: Literal["FROZEN"] = "FROZEN"
    protocol_id: str = Field(min_length=8, max_length=128)
    case_ids: tuple[str, ...] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def validate_cases(self) -> "RestartRecoveryProtocol":
        if len(set(self.case_ids)) != len(self.case_ids):
            raise ValueError("recovery case_ids must be unique")
        if tuple(sorted(self.case_ids)) != self.case_ids:
            raise ValueError("recovery case_ids must be sorted")
        if any(not case_id.startswith("RR-") for case_id in self.case_ids):
            raise ValueError("recovery case ids must use RR- prefix")
        return self

    def sha256(self) -> str:
        return _sha256(self.model_dump(mode="json"))


class RecoveryCaseObservation(_FrozenModel):
    case_id: str = Field(pattern=r"^RR-[0-9]{2}$")
    expected_state: str = Field(min_length=1, max_length=128)
    observed_state: str = Field(min_length=1, max_length=128)
    transition_count_delta: int = Field(default=0, ge=0)
    expectation_met: bool

    @model_validator(mode="after")
    def validate_expectation(self) -> "RecoveryCaseObservation":
        if self.expectation_met != (self.expected_state == self.observed_state):
            raise ValueError("recovery expectation flag does not match observed state")
        return self


class RestartRecoveryReport(_FrozenModel):
    schema_version: Literal["restart-recovery-report-v1"] = "restart-recovery-report-v1"
    status: Literal["MEASURED"] = "MEASURED"
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    denominator: int = Field(ge=1)
    expectations_passed: int = Field(ge=0)
    startup_recovered_execution_count: int = Field(ge=0)
    startup_interrupted_runtime_count: int = Field(ge=0)
    startup_uncertain_action_execution_count: int = Field(ge=0)
    startup_uncertain_custody_count: int = Field(ge=0)
    startup_uncertain_claim_count: int = Field(ge=0)
    second_startup_recovered_execution_count: int = Field(ge=0)
    second_startup_recovered_custody_count: int = Field(ge=0)
    second_startup_recovered_claim_count: int = Field(ge=0)
    transport_replay_count: Literal[0] = 0
    automatic_retry_count: Literal[0] = 0
    real_customer_mutations: Literal[0] = 0
    authenticated_tenant_isolation_preserved: bool
    second_restart_idempotent: bool
    production_recovery_claim_ready: Literal[True] = True
    cases: tuple[RecoveryCaseObservation, ...] = Field(min_length=1)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_report(self) -> "RestartRecoveryReport":
        if self.denominator != len(self.cases):
            raise ValueError("restart recovery denominator mismatch")
        if self.expectations_passed != sum(item.expectation_met for item in self.cases):
            raise ValueError("restart recovery pass count mismatch")
        if tuple(item.case_id for item in self.cases) != tuple(
            sorted(item.case_id for item in self.cases)
        ):
            raise ValueError("restart recovery cases must be sorted")
        if _sha256(self.model_dump(mode="json", exclude={"evidence_sha256"})) != self.evidence_sha256:
            raise ValueError("restart recovery evidence hash mismatch")
        return self


def build_restart_recovery_report(
    protocol: RestartRecoveryProtocol,
    *,
    cases: tuple[RecoveryCaseObservation, ...],
    startup_recovered_execution_count: int,
    startup_interrupted_runtime_count: int,
    startup_uncertain_action_execution_count: int,
    startup_uncertain_custody_count: int,
    startup_uncertain_claim_count: int,
    second_startup_recovered_execution_count: int,
    second_startup_recovered_custody_count: int,
    second_startup_recovered_claim_count: int,
    transport_replay_count: int,
    automatic_retry_count: int,
    real_customer_mutations: int,
    authenticated_tenant_isolation_preserved: bool,
    second_restart_idempotent: bool,
) -> RestartRecoveryReport:
    """Build one hash-bound recovery report from already observed production-store state.

    The builder fails closed rather than allowing a report to silently omit a preregistered case or
    to describe any transport replay, automatic retry, or real customer mutation as successful
    recovery evidence.
    """

    ordered = tuple(sorted(cases, key=lambda item: item.case_id))
    if tuple(item.case_id for item in ordered) != protocol.case_ids:
        raise ValueError("observed recovery cases do not match frozen protocol")
    if transport_replay_count != 0:
        raise ValueError("restart recovery must never replay transport")
    if automatic_retry_count != 0:
        raise ValueError("restart recovery must never automatically retry")
    if real_customer_mutations != 0:
        raise ValueError("restart recovery evidence cannot include real customer mutations")
    if not all(item.expectation_met for item in ordered):
        raise ValueError("restart recovery case expectation failed")
    if not authenticated_tenant_isolation_preserved:
        raise ValueError("authenticated tenant isolation was not preserved")
    if not second_restart_idempotent:
        raise ValueError("second restart was not idempotent")

    payload = {
        "schema_version": "restart-recovery-report-v1",
        "status": "MEASURED",
        "protocol_sha256": protocol.sha256(),
        "denominator": len(ordered),
        "expectations_passed": sum(item.expectation_met for item in ordered),
        "startup_recovered_execution_count": startup_recovered_execution_count,
        "startup_interrupted_runtime_count": startup_interrupted_runtime_count,
        "startup_uncertain_action_execution_count": startup_uncertain_action_execution_count,
        "startup_uncertain_custody_count": startup_uncertain_custody_count,
        "startup_uncertain_claim_count": startup_uncertain_claim_count,
        "second_startup_recovered_execution_count": second_startup_recovered_execution_count,
        "second_startup_recovered_custody_count": second_startup_recovered_custody_count,
        "second_startup_recovered_claim_count": second_startup_recovered_claim_count,
        "transport_replay_count": 0,
        "automatic_retry_count": 0,
        "real_customer_mutations": 0,
        "authenticated_tenant_isolation_preserved": True,
        "second_restart_idempotent": True,
        "production_recovery_claim_ready": True,
        "cases": [item.model_dump(mode="json") for item in ordered],
    }
    return RestartRecoveryReport(
        **payload,
        evidence_sha256=_sha256(payload),
    )
