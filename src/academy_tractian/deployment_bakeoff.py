from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .deployment_feasibility import DeploymentFeasibilityDecision
from .hosted_state_identity_pilot import HostedStateIdentityPilotDecision
from .live_deployment_attestation import LiveDeploymentDecision
from .load_concurrency_benchmark import LoadBenchmarkReport


EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256 = (
    "d272f88958a4cdf9cd4c4e830ae7bb52d1b7524333cc067a94e5e86003b1cadc"
)
EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256 = (
    "d1fec563a055d052fb221624a61aa5386ece4119c8c95921346ed39d9a2dc50f"
)
EXPECTED_CLOUD_BAKEOFF_CONCURRENCY_LEVELS = (1, 5, 20, 50)
EXPECTED_CLOUD_BAKEOFF_REQUESTS_PER_LEVEL = 20
EXPECTED_STATE_IDENTITY_BUNDLE_ID = "neon-plus-auth0"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


class DeploymentTopologyRule(_StrictModel):
    topology_id: str = Field(min_length=1, max_length=256)
    compute_candidate_id: str = Field(min_length=1, max_length=128)
    state_identity_bundle_id: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_identity(self) -> "DeploymentTopologyRule":
        expected = f"{self.compute_candidate_id}+{self.state_identity_bundle_id}"
        if self.topology_id != expected:
            raise ValueError("deployment_topology_identity_mismatch")
        return self


class DeploymentRuntimeEvidence(_StrictModel):
    """Secret-safe empirical evidence for one exact hosted topology deployment."""

    schema_version: Literal["deployment-runtime-evidence-v1"] = "deployment-runtime-evidence-v1"
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    topology_id: str = Field(min_length=1, max_length=256)
    compute_candidate_id: str = Field(min_length=1, max_length=128)
    state_identity_bundle_id: str = Field(min_length=1, max_length=128)
    deployment_id: str = Field(min_length=1, max_length=256)
    code_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    image_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    load_protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    load_report_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    required_local_components: int = Field(ge=0)
    observed_cash_cost_usd: float = Field(ge=0.0)
    tenant_leak_count: int = Field(ge=0)
    forbidden_data_leak_count: int = Field(ge=0)
    duplicate_action_count: int = Field(ge=0)
    sse_gap_count: int = Field(ge=0)
    sse_duplicate_event_count: int = Field(ge=0)
    unrecoverable_sse_reconnect_count: int = Field(ge=0)
    recovery_failure_count: int = Field(ge=0)
    persistence_integrity_failure_count: int = Field(ge=0)
    load_error_count: int = Field(ge=0)
    api_p95_ms: float = Field(gt=0)
    sse_first_event_p95_ms: float = Field(gt=0)
    sse_reconnect_p95_ms: float = Field(gt=0)
    cold_start_p95_ms: float = Field(gt=0)
    persistence_p95_ms: float = Field(ge=0)
    max_level_throughput_rps: float = Field(gt=0)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "DeploymentRuntimeEvidence":
        if self.topology_id != f"{self.compute_candidate_id}+{self.state_identity_bundle_id}":
            raise ValueError("deployment_runtime_topology_identity_mismatch")
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("deployment_runtime_evidence_hash_mismatch")
        return self


CandidateBakeoffOutcome = Literal["QUALIFIED", "EXCLUDED"]


class DeploymentCandidateAssessment(_StrictModel):
    topology_id: str
    compute_candidate_id: str
    outcome: CandidateBakeoffOutcome
    reason_codes: tuple[str, ...]


BakeoffOutcome = Literal["PROMOTE", "NO_SELECTION"]


class DeploymentBakeoffDecision(_StrictModel):
    schema_version: Literal["deployment-bakeoff-decision-v1"] = "deployment-bakeoff-decision-v1"
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    outcome: BakeoffOutcome
    selected_topology_id: str | None
    qualified_topology_ids: tuple[str, ...]
    assessments: tuple[DeploymentCandidateAssessment, ...]
    reason_codes: tuple[str, ...]


_REASON_ORDER = (
    "STATIC_FEASIBILITY_MISSING",
    "STATIC_FEASIBILITY_REJECTED",
    "STATE_IDENTITY_PILOT_MISSING",
    "STATE_IDENTITY_PILOT_FAILED",
    "LIVE_ATTESTATION_MISSING",
    "LIVE_ATTESTATION_FAILED",
    "RUNTIME_EVIDENCE_MISSING",
    "RUNTIME_MANIFEST_MISMATCH",
    "RUNTIME_TOPOLOGY_BINDING_MISMATCH",
    "RUNTIME_DEPLOYMENT_BINDING_MISMATCH",
    "LOCAL_COMPONENT_REQUIRED",
    "NONZERO_CASH_COST_OBSERVED",
    "TENANT_LEAK_OBSERVED",
    "FORBIDDEN_DATA_LEAK_OBSERVED",
    "DUPLICATE_ACTION_OBSERVED",
    "SSE_GAP_OBSERVED",
    "SSE_DUPLICATE_EVENT_OBSERVED",
    "UNRECOVERABLE_SSE_RECONNECT_OBSERVED",
    "RECOVERY_FAILURE_OBSERVED",
    "PERSISTENCE_INTEGRITY_FAILURE_OBSERVED",
    "LOAD_ERROR_OBSERVED",
    "LOAD_REPORT_MISSING",
    "LOAD_REPORT_HASH_MISMATCH",
    "LOAD_PROTOCOL_MISMATCH",
    "LOAD_CONCURRENCY_LEVELS_MISMATCH",
    "LOAD_REQUEST_COUNT_MISMATCH",
    "LOAD_REPORT_ERROR_OBSERVED",
)


def _ordered_reasons(values: list[str]) -> tuple[str, ...]:
    rank = {value: index for index, value in enumerate(_REASON_ORDER)}
    return tuple(dict.fromkeys(sorted(values, key=lambda value: (rank.get(value, len(rank)), value))))


def build_deployment_runtime_evidence(**values: object) -> DeploymentRuntimeEvidence:
    material = {"schema_version": "deployment-runtime-evidence-v1", **values}
    return DeploymentRuntimeEvidence.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )


def _load_report_error_count(report: LoadBenchmarkReport) -> int:
    return sum(level.request_count - level.completed_count for level in report.levels)


def _dominates(
    left: DeploymentRuntimeEvidence,
    right: DeploymentRuntimeEvidence,
) -> bool:
    lower_axes = (
        "api_p95_ms",
        "sse_reconnect_p95_ms",
        "cold_start_p95_ms",
        "persistence_p95_ms",
    )
    higher_axes = ("max_level_throughput_rps",)
    weakly_better = all(getattr(left, axis) <= getattr(right, axis) for axis in lower_axes)
    weakly_better = weakly_better and all(
        getattr(left, axis) >= getattr(right, axis) for axis in higher_axes
    )
    strictly_better = any(getattr(left, axis) < getattr(right, axis) for axis in lower_axes)
    strictly_better = strictly_better or any(
        getattr(left, axis) > getattr(right, axis) for axis in higher_axes
    )
    return weakly_better and strictly_better


def decide_deployment_bakeoff(
    *,
    manifest_sha256: str,
    topology_rules: tuple[DeploymentTopologyRule, ...],
    feasibility_decisions: tuple[DeploymentFeasibilityDecision, ...],
    state_identity_pilot: HostedStateIdentityPilotDecision | None,
    live_attestations: tuple[LiveDeploymentDecision, ...],
    runtime_evidence: tuple[DeploymentRuntimeEvidence, ...],
    load_reports: Mapping[str, LoadBenchmarkReport],
) -> DeploymentBakeoffDecision:
    """Apply hard hosted-deployment gates before any conservative performance comparison.

    Static rejection is terminal for the current preregistration. Live evidence cannot compensate
    for a static hard-gate failure. A unique live-qualified survivor may be selected; when multiple
    candidates survive, selection requires one candidate to Pareto-dominate every peer across the
    preregistered latency/persistence/throughput axes. Trade-offs or ties return NO_SELECTION.
    """

    if manifest_sha256 != EXPECTED_CLOUD_BAKEOFF_MANIFEST_SHA256:
        return DeploymentBakeoffDecision(
            manifest_sha256=manifest_sha256,
            outcome="NO_SELECTION",
            selected_topology_id=None,
            qualified_topology_ids=(),
            assessments=tuple(
                DeploymentCandidateAssessment(
                    topology_id=rule.topology_id,
                    compute_candidate_id=rule.compute_candidate_id,
                    outcome="EXCLUDED",
                    reason_codes=("MANIFEST_HASH_MISMATCH",),
                )
                for rule in topology_rules
            ),
            reason_codes=("MANIFEST_HASH_MISMATCH",),
        )

    topology_ids = [rule.topology_id for rule in topology_rules]
    compute_ids = [rule.compute_candidate_id for rule in topology_rules]
    if len(topology_ids) != len(set(topology_ids)) or len(compute_ids) != len(set(compute_ids)):
        raise ValueError("duplicate_deployment_bakeoff_topology_or_compute_id")
    if any(rule.state_identity_bundle_id != EXPECTED_STATE_IDENTITY_BUNDLE_ID for rule in topology_rules):
        raise ValueError("unexpected_state_identity_bundle_in_bakeoff_frontier")

    feasibility_by_id = {item.candidate_id: item for item in feasibility_decisions}
    live_by_id = {item.candidate_id: item for item in live_attestations}
    runtime_by_id = {item.topology_id: item for item in runtime_evidence}
    if len(feasibility_by_id) != len(feasibility_decisions):
        raise ValueError("duplicate_deployment_feasibility_decision")
    if len(live_by_id) != len(live_attestations):
        raise ValueError("duplicate_live_deployment_attestation_decision")
    if len(runtime_by_id) != len(runtime_evidence):
        raise ValueError("duplicate_deployment_runtime_evidence")

    assessments: list[DeploymentCandidateAssessment] = []
    qualified: list[str] = []

    for rule in topology_rules:
        reasons: list[str] = []
        feasibility = feasibility_by_id.get(rule.compute_candidate_id)
        if feasibility is None:
            reasons.append("STATIC_FEASIBILITY_MISSING")
        elif feasibility.outcome != "PILOT_ADMISSIBLE":
            reasons.append("STATIC_FEASIBILITY_REJECTED")

        # Do not inspect or credit live evidence after a static hard-gate rejection.
        if reasons:
            assessments.append(
                DeploymentCandidateAssessment(
                    topology_id=rule.topology_id,
                    compute_candidate_id=rule.compute_candidate_id,
                    outcome="EXCLUDED",
                    reason_codes=_ordered_reasons(reasons),
                )
            )
            continue

        if state_identity_pilot is None:
            reasons.append("STATE_IDENTITY_PILOT_MISSING")
        elif (
            state_identity_pilot.bundle_id != rule.state_identity_bundle_id
            or state_identity_pilot.outcome != "PILOT_PASS"
        ):
            reasons.append("STATE_IDENTITY_PILOT_FAILED")

        live = live_by_id.get(rule.compute_candidate_id)
        if live is None:
            reasons.append("LIVE_ATTESTATION_MISSING")
        elif live.outcome != "LIVE_ATTESTATION_PASS":
            reasons.append("LIVE_ATTESTATION_FAILED")

        runtime = runtime_by_id.get(rule.topology_id)
        if runtime is None:
            reasons.append("RUNTIME_EVIDENCE_MISSING")
        else:
            if runtime.manifest_sha256 != manifest_sha256:
                reasons.append("RUNTIME_MANIFEST_MISMATCH")
            if (
                runtime.compute_candidate_id != rule.compute_candidate_id
                or runtime.state_identity_bundle_id != rule.state_identity_bundle_id
            ):
                reasons.append("RUNTIME_TOPOLOGY_BINDING_MISMATCH")
            if live is not None and runtime.deployment_id != live.deployment_id:
                reasons.append("RUNTIME_DEPLOYMENT_BINDING_MISMATCH")
            if runtime.required_local_components != 0:
                reasons.append("LOCAL_COMPONENT_REQUIRED")
            if runtime.observed_cash_cost_usd != 0.0:
                reasons.append("NONZERO_CASH_COST_OBSERVED")

            zero_gates = (
                (runtime.tenant_leak_count, "TENANT_LEAK_OBSERVED"),
                (runtime.forbidden_data_leak_count, "FORBIDDEN_DATA_LEAK_OBSERVED"),
                (runtime.duplicate_action_count, "DUPLICATE_ACTION_OBSERVED"),
                (runtime.sse_gap_count, "SSE_GAP_OBSERVED"),
                (runtime.sse_duplicate_event_count, "SSE_DUPLICATE_EVENT_OBSERVED"),
                (
                    runtime.unrecoverable_sse_reconnect_count,
                    "UNRECOVERABLE_SSE_RECONNECT_OBSERVED",
                ),
                (runtime.recovery_failure_count, "RECOVERY_FAILURE_OBSERVED"),
                (
                    runtime.persistence_integrity_failure_count,
                    "PERSISTENCE_INTEGRITY_FAILURE_OBSERVED",
                ),
                (runtime.load_error_count, "LOAD_ERROR_OBSERVED"),
            )
            reasons.extend(reason for value, reason in zero_gates if value != 0)

            report = load_reports.get(rule.topology_id)
            if report is None:
                reasons.append("LOAD_REPORT_MISSING")
            else:
                if runtime.load_report_sha256 != report.evidence_sha256:
                    reasons.append("LOAD_REPORT_HASH_MISMATCH")
                if (
                    runtime.load_protocol_sha256 != EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256
                    or report.protocol_sha256 != EXPECTED_CLOUD_BAKEOFF_LOAD_PROTOCOL_SHA256
                ):
                    reasons.append("LOAD_PROTOCOL_MISMATCH")
                levels = tuple(level.concurrency_level for level in report.levels)
                if levels != EXPECTED_CLOUD_BAKEOFF_CONCURRENCY_LEVELS:
                    reasons.append("LOAD_CONCURRENCY_LEVELS_MISMATCH")
                if any(
                    level.request_count != EXPECTED_CLOUD_BAKEOFF_REQUESTS_PER_LEVEL
                    for level in report.levels
                ):
                    reasons.append("LOAD_REQUEST_COUNT_MISMATCH")
                report_error_count = _load_report_error_count(report)
                if report_error_count != 0:
                    reasons.append("LOAD_REPORT_ERROR_OBSERVED")
                if runtime.load_error_count != report_error_count:
                    reasons.append("LOAD_REPORT_ERROR_COUNT_BINDING_MISMATCH")
                max_level = max(report.levels, key=lambda item: item.concurrency_level)
                if runtime.max_level_throughput_rps != max_level.completed_throughput_rps:
                    reasons.append("LOAD_THROUGHPUT_BINDING_MISMATCH")

        assessment = DeploymentCandidateAssessment(
            topology_id=rule.topology_id,
            compute_candidate_id=rule.compute_candidate_id,
            outcome="EXCLUDED" if reasons else "QUALIFIED",
            reason_codes=_ordered_reasons(reasons),
        )
        assessments.append(assessment)
        if not reasons:
            qualified.append(rule.topology_id)

    if not qualified:
        return DeploymentBakeoffDecision(
            manifest_sha256=manifest_sha256,
            outcome="NO_SELECTION",
            selected_topology_id=None,
            qualified_topology_ids=(),
            assessments=tuple(assessments),
            reason_codes=("NO_LIVE_QUALIFIED_TOPOLOGY",),
        )

    if len(qualified) == 1:
        return DeploymentBakeoffDecision(
            manifest_sha256=manifest_sha256,
            outcome="PROMOTE",
            selected_topology_id=qualified[0],
            qualified_topology_ids=tuple(qualified),
            assessments=tuple(assessments),
            reason_codes=("UNIQUE_HARD_GATE_SURVIVOR_LIVE_QUALIFIED",),
        )

    qualified_evidence = {topology_id: runtime_by_id[topology_id] for topology_id in qualified}
    dominators = tuple(
        topology_id
        for topology_id, evidence in qualified_evidence.items()
        if all(
            topology_id == other_id or _dominates(evidence, other_evidence)
            for other_id, other_evidence in qualified_evidence.items()
        )
    )
    if len(dominators) != 1:
        return DeploymentBakeoffDecision(
            manifest_sha256=manifest_sha256,
            outcome="NO_SELECTION",
            selected_topology_id=None,
            qualified_topology_ids=tuple(qualified),
            assessments=tuple(assessments),
            reason_codes=("NO_UNIQUE_PARETO_DOMINANT_TOPOLOGY",),
        )

    return DeploymentBakeoffDecision(
        manifest_sha256=manifest_sha256,
        outcome="PROMOTE",
        selected_topology_id=dominators[0],
        qualified_topology_ids=tuple(qualified),
        assessments=tuple(assessments),
        reason_codes=("UNIQUE_PARETO_DOMINANT_TOPOLOGY",),
    )
