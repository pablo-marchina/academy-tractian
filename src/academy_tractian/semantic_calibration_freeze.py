from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .semantic_evaluation import (
    CalibrationState,
    HumanSemanticReference,
    JudgeSemanticObservation,
    SemanticCalibrationAcceptancePolicy,
    SemanticCalibrationReport,
    SemanticDimension,
    calibrate_semantic_judge,
    semantic_rubric_v1,
)
from .semantic_human_calibration import (
    SemanticAnnotationManifest,
    SemanticHumanResolutionReport,
    SemanticReviewerPacket,
)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _canonical_sha256(payload: object) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


class SemanticCalibrationProtocol(_FrozenModel):
    """Preregistered gate contract for held-out semantic calibration.

    There are intentionally no defaults for acceptance thresholds. A protocol must be frozen
    before VALIDATION outcomes are inspected; LOCKED_TEST is never eligible for calibration.
    """

    schema_version: Literal["semantic-calibration-protocol-v2"] = (
        "semantic-calibration-protocol-v2"
    )
    status: Literal["FROZEN"]
    protocol_id: str = Field(min_length=1, max_length=128)
    purpose: Literal["HELD_OUT_CALIBRATION"]
    source_split: Literal["VALIDATION"]
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    minimum_pairs_per_dimension: int = Field(ge=1)
    minimum_exact_agreement: float = Field(ge=0.0, le=1.0)
    minimum_quadratic_weighted_kappa: float = Field(ge=-1.0, le=1.0)
    maximum_mean_absolute_error: float = Field(ge=0.0, le=2.0)
    maximum_false_pass_rate: float = Field(ge=0.0, le=1.0)
    maximum_invalid_rate: float = Field(ge=0.0, le=1.0)


class SemanticCalibrationEvidenceEntry(_FrozenModel):
    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    scenario_id: str = Field(min_length=1)
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_mode: str = Field(min_length=1)
    dimension: SemanticDimension


class SemanticCalibrationEvidenceManifest(_FrozenModel):
    """Hash-bound proof that human references came from one held-out VALIDATION packet."""

    schema_version: Literal["semantic-calibration-evidence-v2"] = (
        "semantic-calibration-evidence-v2"
    )
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    purpose: Literal["HELD_OUT_CALIBRATION"]
    source_split: Literal["VALIDATION"]
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    task_count: int = Field(ge=1)
    entries: tuple[SemanticCalibrationEvidenceEntry, ...]
    evidence_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_manifest(self) -> "SemanticCalibrationEvidenceManifest":
        if self.task_count != len(self.entries):
            raise ValueError("semantic_calibration_evidence_task_count_mismatch")
        if len({entry.task_id for entry in self.entries}) != len(self.entries):
            raise ValueError("semantic_calibration_evidence_duplicate_task")
        expected = semantic_calibration_evidence_sha256(
            packet_id=self.packet_id,
            purpose=self.purpose,
            source_split=self.source_split,
            rubric_sha256=self.rubric_sha256,
            frozen_split_sha256=self.frozen_split_sha256,
            entries=self.entries,
        )
        if self.evidence_manifest_sha256 != expected:
            raise ValueError("semantic_calibration_evidence_hash_mismatch")
        return self


class FrozenSemanticCalibrationReport(_FrozenModel):
    schema_version: Literal["semantic-calibration-report-v2"] = (
        "semantic-calibration-report-v2"
    )
    state: CalibrationState
    gate_authorized: bool
    protocol_id: str
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_split: Literal["VALIDATION"]
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    judge_ids: tuple[str, ...]
    expected_keys: int = Field(ge=0)
    valid_pairs: int = Field(ge=0)
    gate_failures: tuple[str, ...]
    calibration: SemanticCalibrationReport
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_evidence_hash(self) -> "FrozenSemanticCalibrationReport":
        expected = frozen_semantic_calibration_report_sha256(
            state=self.state,
            gate_authorized=self.gate_authorized,
            protocol_id=self.protocol_id,
            protocol_sha256=self.protocol_sha256,
            evidence_manifest_sha256=self.evidence_manifest_sha256,
            source_split=self.source_split,
            frozen_split_sha256=self.frozen_split_sha256,
            rubric_sha256=self.rubric_sha256,
            dataset_sha256=self.dataset_sha256,
            judge_ids=self.judge_ids,
            expected_keys=self.expected_keys,
            valid_pairs=self.valid_pairs,
            gate_failures=self.gate_failures,
            calibration=self.calibration,
        )
        if self.evidence_sha256 != expected:
            raise ValueError("semantic_calibration_report_hash_mismatch")
        return self


def semantic_calibration_protocol_sha256(protocol: SemanticCalibrationProtocol) -> str:
    return _canonical_sha256(protocol.model_dump(mode="json"))


def semantic_calibration_evidence_sha256(
    *,
    packet_id: str,
    purpose: str,
    source_split: str,
    rubric_sha256: str,
    frozen_split_sha256: str,
    entries: tuple[SemanticCalibrationEvidenceEntry, ...],
) -> str:
    payload = {
        "schema_version": "semantic-calibration-evidence-v2",
        "packet_id": packet_id,
        "purpose": purpose,
        "source_split": source_split,
        "rubric_sha256": rubric_sha256,
        "frozen_split_sha256": frozen_split_sha256,
        "task_count": len(entries),
        "entries": [
            entry.model_dump(mode="json")
            for entry in sorted(entries, key=lambda item: item.task_id)
        ],
    }
    return _canonical_sha256(payload)


def frozen_semantic_calibration_report_sha256(
    *,
    state: CalibrationState,
    gate_authorized: bool,
    protocol_id: str,
    protocol_sha256: str,
    evidence_manifest_sha256: str,
    source_split: str,
    frozen_split_sha256: str,
    rubric_sha256: str,
    dataset_sha256: str,
    judge_ids: tuple[str, ...],
    expected_keys: int,
    valid_pairs: int,
    gate_failures: tuple[str, ...],
    calibration: SemanticCalibrationReport,
) -> str:
    payload = {
        "schema_version": "semantic-calibration-report-v2",
        "state": state,
        "gate_authorized": gate_authorized,
        "protocol_id": protocol_id,
        "protocol_sha256": protocol_sha256,
        "evidence_manifest_sha256": evidence_manifest_sha256,
        "source_split": source_split,
        "frozen_split_sha256": frozen_split_sha256,
        "rubric_sha256": rubric_sha256,
        "dataset_sha256": dataset_sha256,
        "judge_ids": list(judge_ids),
        "expected_keys": expected_keys,
        "valid_pairs": valid_pairs,
        "gate_failures": list(gate_failures),
        "calibration": calibration.model_dump(mode="json"),
    }
    return _canonical_sha256(payload)


def _reference_key(reference: HumanSemanticReference) -> tuple[str, str, str, str, str]:
    return (
        reference.scenario_id,
        reference.output_sha256,
        reference.context_sha256,
        reference.response_mode,
        reference.dimension,
    )


def _entry_key(entry: SemanticCalibrationEvidenceEntry) -> tuple[str, str, str, str, str]:
    return (
        entry.scenario_id,
        entry.output_sha256,
        entry.context_sha256,
        entry.response_mode,
        entry.dimension,
    )


def build_semantic_calibration_evidence_manifest(
    *,
    packet: SemanticReviewerPacket,
    annotation_manifest: SemanticAnnotationManifest,
    resolution_report: SemanticHumanResolutionReport,
) -> SemanticCalibrationEvidenceManifest:
    """Bind a complete held-out human review to its frozen VALIDATION split."""

    rubric = semantic_rubric_v1()
    if packet.purpose != "HELD_OUT_CALIBRATION":
        raise ValueError("semantic_calibration_evidence_requires_held_out_packet")
    if annotation_manifest.purpose != "HELD_OUT_CALIBRATION":
        raise ValueError("semantic_calibration_evidence_requires_held_out_manifest")
    if annotation_manifest.source_split != "VALIDATION":
        raise ValueError("semantic_calibration_evidence_requires_validation_split")
    if packet.packet_id != annotation_manifest.packet_id:
        raise ValueError("semantic_calibration_evidence_packet_manifest_mismatch")
    if resolution_report.packet_id != packet.packet_id:
        raise ValueError("semantic_calibration_evidence_resolution_packet_mismatch")
    if not resolution_report.calibration_ready:
        raise ValueError("semantic_calibration_evidence_requires_complete_resolution")
    if packet.rubric_sha256 != rubric.rubric_sha256:
        raise ValueError("semantic_calibration_evidence_packet_rubric_mismatch")
    if resolution_report.rubric_sha256 != packet.rubric_sha256:
        raise ValueError("semantic_calibration_evidence_resolution_rubric_mismatch")

    task_by_id = {task.task_id: task for task in packet.tasks}
    private_by_id = {entry.task_id: entry for entry in annotation_manifest.entries}
    if set(task_by_id) != set(private_by_id):
        raise ValueError("semantic_calibration_evidence_task_set_mismatch")

    entries: list[SemanticCalibrationEvidenceEntry] = []
    for task_id in sorted(task_by_id):
        task = task_by_id[task_id]
        private = private_by_id[task_id]
        if (
            task.scenario_id != private.scenario_id
            or task.output_sha256 != private.output_sha256
            or task.context_sha256 != private.context_sha256
            or task.response_mode != private.response_mode
            or task.dimension != private.dimension
        ):
            raise ValueError("semantic_calibration_evidence_task_binding_mismatch")
        entries.append(
            SemanticCalibrationEvidenceEntry(
                task_id=task_id,
                scenario_id=task.scenario_id,
                output_sha256=task.output_sha256,
                context_sha256=task.context_sha256,
                response_mode=task.response_mode,
                dimension=task.dimension,
            )
        )

    reference_keys = {_reference_key(item) for item in resolution_report.human_references}
    entry_tuple = tuple(entries)
    entry_keys = {_entry_key(item) for item in entry_tuple}
    if len(reference_keys) != len(resolution_report.human_references):
        raise ValueError("semantic_calibration_evidence_duplicate_human_reference")
    if reference_keys != entry_keys:
        raise ValueError("semantic_calibration_evidence_human_reference_set_mismatch")

    evidence_hash = semantic_calibration_evidence_sha256(
        packet_id=packet.packet_id,
        purpose="HELD_OUT_CALIBRATION",
        source_split="VALIDATION",
        rubric_sha256=packet.rubric_sha256,
        frozen_split_sha256=annotation_manifest.frozen_split_sha256,
        entries=entry_tuple,
    )
    return SemanticCalibrationEvidenceManifest(
        packet_id=packet.packet_id,
        purpose="HELD_OUT_CALIBRATION",
        source_split="VALIDATION",
        rubric_sha256=packet.rubric_sha256,
        frozen_split_sha256=annotation_manifest.frozen_split_sha256,
        task_count=len(entry_tuple),
        entries=entry_tuple,
        evidence_manifest_sha256=evidence_hash,
    )


def _acceptance_policy(protocol: SemanticCalibrationProtocol) -> SemanticCalibrationAcceptancePolicy:
    """Adapt the frozen v2 protocol into the metric implementation's threshold shape."""

    return SemanticCalibrationAcceptancePolicy(
        policy_id=protocol.protocol_id,
        minimum_pairs_per_dimension=protocol.minimum_pairs_per_dimension,
        minimum_exact_agreement=protocol.minimum_exact_agreement,
        minimum_quadratic_weighted_kappa=protocol.minimum_quadratic_weighted_kappa,
        maximum_mean_absolute_error=protocol.maximum_mean_absolute_error,
        maximum_false_pass_rate=protocol.maximum_false_pass_rate,
        maximum_invalid_rate=protocol.maximum_invalid_rate,
    )


def calibrate_semantic_judge_frozen(
    *,
    human_references: Sequence[HumanSemanticReference],
    judge_observations: Sequence[JudgeSemanticObservation],
    protocol: SemanticCalibrationProtocol,
    evidence_manifest: SemanticCalibrationEvidenceManifest,
) -> FrozenSemanticCalibrationReport:
    """Run the only promotion-authorizing semantic calibration path.

    The v1 metric implementation remains usable for descriptive/historical analysis, but a
    promotion gate is authorized only through this frozen v2 binding to held-out VALIDATION.
    """

    rubric = semantic_rubric_v1()
    binding_failures: list[str] = []
    if protocol.rubric_sha256 != rubric.rubric_sha256:
        binding_failures.append("PROTOCOL_RUBRIC_HASH_MISMATCH")
    if evidence_manifest.rubric_sha256 != protocol.rubric_sha256:
        binding_failures.append("EVIDENCE_RUBRIC_HASH_MISMATCH")
    if evidence_manifest.frozen_split_sha256 != protocol.frozen_split_sha256:
        binding_failures.append("EVIDENCE_FROZEN_SPLIT_HASH_MISMATCH")
    if evidence_manifest.source_split != "VALIDATION":
        binding_failures.append("EVIDENCE_NOT_VALIDATION")
    if evidence_manifest.purpose != "HELD_OUT_CALIBRATION":
        binding_failures.append("EVIDENCE_NOT_HELD_OUT_CALIBRATION")

    human_keys = {_reference_key(item) for item in human_references}
    evidence_keys = {_entry_key(item) for item in evidence_manifest.entries}
    if len(human_keys) != len(human_references):
        binding_failures.append("DUPLICATE_HUMAN_REFERENCE_KEYS")
    if human_keys != evidence_keys:
        binding_failures.append("HUMAN_REFERENCE_EVIDENCE_SET_MISMATCH")

    calibration = calibrate_semantic_judge(
        human_references=human_references,
        judge_observations=judge_observations,
        acceptance_policy=(None if binding_failures else _acceptance_policy(protocol)),
        rubric=rubric,
    )
    combined_failures = tuple(sorted(set(binding_failures) | set(calibration.gate_failures)))
    gate_authorized = not binding_failures and calibration.gate_authorized
    if binding_failures:
        state: CalibrationState = (
            "NOT_CALIBRATED"
            if calibration.state == "NOT_CALIBRATED"
            else "DESCRIPTIVE_ONLY"
        )
    else:
        state = calibration.state

    protocol_hash = semantic_calibration_protocol_sha256(protocol)
    evidence_hash = frozen_semantic_calibration_report_sha256(
        state=state,
        gate_authorized=gate_authorized,
        protocol_id=protocol.protocol_id,
        protocol_sha256=protocol_hash,
        evidence_manifest_sha256=evidence_manifest.evidence_manifest_sha256,
        source_split="VALIDATION",
        frozen_split_sha256=evidence_manifest.frozen_split_sha256,
        rubric_sha256=rubric.rubric_sha256,
        dataset_sha256=calibration.dataset_sha256,
        judge_ids=calibration.judge_ids,
        expected_keys=calibration.expected_keys,
        valid_pairs=calibration.valid_pairs,
        gate_failures=combined_failures,
        calibration=calibration,
    )
    return FrozenSemanticCalibrationReport(
        state=state,
        gate_authorized=gate_authorized,
        protocol_id=protocol.protocol_id,
        protocol_sha256=protocol_hash,
        evidence_manifest_sha256=evidence_manifest.evidence_manifest_sha256,
        source_split="VALIDATION",
        frozen_split_sha256=evidence_manifest.frozen_split_sha256,
        rubric_sha256=rubric.rubric_sha256,
        dataset_sha256=calibration.dataset_sha256,
        judge_ids=calibration.judge_ids,
        expected_keys=calibration.expected_keys,
        valid_pairs=calibration.valid_pairs,
        gate_failures=combined_failures,
        calibration=calibration,
        evidence_sha256=evidence_hash,
    )
