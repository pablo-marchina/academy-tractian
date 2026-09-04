from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


HARD_FREEZE_NOT_BEFORE_UTC = datetime(2026, 9, 6, 3, 0, tzinfo=timezone.utc)
REQUIRED_STATUS_CONTEXT = "required-gate"

GitHubConclusion = Literal[
    "success",
    "failure",
    "cancelled",
    "timed_out",
    "action_required",
    "neutral",
    "skipped",
    "stale",
    "startup_failure",
]


class HardFreezeReadinessObservation(BaseModel):
    """Sanitized external observations required to authorize freeze activation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    observed_main_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    observed_at_utc: datetime
    branch_protected: bool
    required_status_contexts: tuple[str, ...] = ()
    final_ci_run_id: int | None = Field(default=None, ge=1)
    final_ci_head_sha: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    final_ci_conclusion: GitHubConclusion | None = None
    required_gate_conclusion: GitHubConclusion | None = None
    bundle_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bundle_validation_failures: tuple[str, ...] = ()

    @model_validator(mode="after")
    def normalize_time(self) -> "HardFreezeReadinessObservation":
        if self.observed_at_utc.tzinfo is None:
            raise ValueError("observed_at_utc must be timezone-aware")
        return self


class HardFreezeReadinessReport(BaseModel):
    """Aggregate-only readiness evidence. It never marks the hard freeze effective."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["hard-freeze-readiness-v1"] = "hard-freeze-readiness-v1"
    status: Literal["READY_FOR_ACTIVATION", "BLOCKED"]
    hard_freeze_effective: Literal[False] = False
    candidate_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    observed_main_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    observed_at_utc: datetime
    freeze_not_before_utc: datetime = HARD_FREEZE_NOT_BEFORE_UTC
    branch_protected: bool
    required_gate_required: bool
    final_ci_run_id: int | None = Field(default=None, ge=1)
    final_ci_success: bool
    required_gate_success: bool
    bundle_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bundle_validation_failure_count: int = Field(ge=0)
    blockers: tuple[str, ...]
    interpretation: Literal["freeze_readiness_only"] = "freeze_readiness_only"
    production_readiness_claim_ready: Literal[False] = False
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_hash(self) -> "HardFreezeReadinessReport":
        payload = self.model_dump(mode="json", exclude={"evidence_sha256"})
        expected = compute_evidence_sha256(payload)
        if self.evidence_sha256 != expected:
            raise ValueError("hard freeze readiness hash mismatch")
        return self


def compute_evidence_sha256(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(canonical.encode("utf-8")).hexdigest()


def evaluate_hard_freeze_readiness(
    observation: HardFreezeReadinessObservation,
) -> HardFreezeReadinessReport:
    blockers: list[str] = []

    observed_at = observation.observed_at_utc.astimezone(timezone.utc)
    if observed_at < HARD_FREEZE_NOT_BEFORE_UTC:
        blockers.append("freeze_window_not_open")
    if observation.observed_main_sha != observation.candidate_sha:
        blockers.append("main_sha_mismatch")
    if not observation.branch_protected:
        blockers.append("branch_protection_not_enforced")

    required_gate_required = REQUIRED_STATUS_CONTEXT in observation.required_status_contexts
    if not required_gate_required:
        blockers.append("required_gate_not_required")

    final_ci_success = (
        observation.final_ci_run_id is not None
        and observation.final_ci_head_sha == observation.candidate_sha
        and observation.final_ci_conclusion == "success"
    )
    if not final_ci_success:
        blockers.append("final_ci_not_success_on_candidate")

    required_gate_success = observation.required_gate_conclusion == "success"
    if not required_gate_success:
        blockers.append("required_gate_not_success")

    if observation.bundle_validation_failures:
        blockers.append("final_bundle_validation_failed")

    blockers = list(dict.fromkeys(blockers))
    status: Literal["READY_FOR_ACTIVATION", "BLOCKED"] = (
        "READY_FOR_ACTIVATION" if not blockers else "BLOCKED"
    )

    payload: dict[str, object] = {
        "schema_version": "hard-freeze-readiness-v1",
        "status": status,
        "hard_freeze_effective": False,
        "candidate_sha": observation.candidate_sha,
        "observed_main_sha": observation.observed_main_sha,
        "observed_at_utc": observed_at.isoformat().replace("+00:00", "Z"),
        "freeze_not_before_utc": HARD_FREEZE_NOT_BEFORE_UTC.isoformat().replace(
            "+00:00", "Z"
        ),
        "branch_protected": observation.branch_protected,
        "required_gate_required": required_gate_required,
        "final_ci_run_id": observation.final_ci_run_id,
        "final_ci_success": final_ci_success,
        "required_gate_success": required_gate_success,
        "bundle_manifest_sha256": observation.bundle_manifest_sha256,
        "bundle_validation_failure_count": len(observation.bundle_validation_failures),
        "blockers": blockers,
        "interpretation": "freeze_readiness_only",
        "production_readiness_claim_ready": False,
    }
    payload["evidence_sha256"] = compute_evidence_sha256(payload)
    return HardFreezeReadinessReport.model_validate(payload)
