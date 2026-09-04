from __future__ import annotations

from hashlib import sha256

import pytest
from pydantic import ValidationError

from academy_tractian.semantic_calibration_freeze import (
    SemanticCalibrationEvidenceManifest,
    SemanticCalibrationProtocol,
    build_semantic_calibration_evidence_manifest,
    calibrate_semantic_judge_frozen,
    semantic_calibration_protocol_sha256,
)
from academy_tractian.semantic_evaluation import JudgeSemanticObservation, semantic_rubric_v1
from academy_tractian.semantic_human_calibration import (
    SemanticAnnotationSource,
    SemanticReviewerLabel,
    build_semantic_reviewer_packet,
    resolve_human_semantic_labels,
)


def _split_payload() -> dict[str, object]:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {"group_id": "dev-a", "scenarios": ["DEV-A"]},
                    {"group_id": "dev-b", "scenarios": ["DEV-B"]},
                ]
            },
            "VALIDATION": {
                "groups": [
                    {"group_id": "val-a", "scenarios": ["VAL-A"]},
                    {"group_id": "val-b", "scenarios": ["VAL-B"]},
                ]
            },
            "LOCKED_TEST": {
                "groups": [
                    {"group_id": "locked-a", "scenarios": ["LOCKED-A"]},
                    {"group_id": "locked-b", "scenarios": ["LOCKED-B"]},
                ]
            },
        },
    }


def _source(scenario_id: str, *, escalation: bool = False) -> SemanticAnnotationSource:
    return SemanticAnnotationSource(
        scenario_id=scenario_id,
        terminal_decision="ESCALATE_HUMAN" if escalation else "ORIENT",
        response_mode="partial" if escalation else "complete",
        terminal_message=f"Sanitized terminal conclusion for {scenario_id}.",
        safe_evidence_context=(
            f"Sanitized evidence for {scenario_id} supports the stated operational state.",
        ),
    )


def _reviewer_hash(seed: str) -> str:
    return sha256(seed.encode("utf-8")).hexdigest()


def _held_out_fixture():
    packet, manifest = build_semantic_reviewer_packet(
        sources=[_source("VAL-A"), _source("VAL-B", escalation=True)],
        frozen_split_payload=_split_payload(),
        purpose="HELD_OUT_CALIBRATION",
        deterministic_shuffle_seed=29,
        minimum_distinct_groups=2,
    )
    labels: list[SemanticReviewerLabel] = []
    for task in packet.tasks:
        labels.extend(
            [
                SemanticReviewerLabel(
                    packet_id=packet.packet_id,
                    task_id=task.task_id,
                    rubric_sha256=packet.rubric_sha256,
                    reviewer_slot="A",
                    reviewer_ref_sha256=_reviewer_hash("reviewer-a"),
                    score=2,
                    reason_codes=("NO_MATERIAL_DEFECT",),
                ),
                SemanticReviewerLabel(
                    packet_id=packet.packet_id,
                    task_id=task.task_id,
                    rubric_sha256=packet.rubric_sha256,
                    reviewer_slot="B",
                    reviewer_ref_sha256=_reviewer_hash("reviewer-b"),
                    score=2,
                    reason_codes=("NO_MATERIAL_DEFECT",),
                ),
            ]
        )
    resolution = resolve_human_semantic_labels(
        packet=packet,
        manifest=manifest,
        labels=labels,
    )
    evidence = build_semantic_calibration_evidence_manifest(
        packet=packet,
        annotation_manifest=manifest,
        resolution_report=resolution,
    )
    return packet, manifest, resolution, evidence


def _protocol(frozen_split_sha256: str, **updates) -> SemanticCalibrationProtocol:
    payload = {
        "status": "FROZEN",
        "protocol_id": "held-out-semantic-gate-test-v2",
        "purpose": "HELD_OUT_CALIBRATION",
        "source_split": "VALIDATION",
        "rubric_sha256": semantic_rubric_v1().rubric_sha256,
        "frozen_split_sha256": frozen_split_sha256,
        "minimum_pairs_per_dimension": 1,
        "minimum_exact_agreement": 1.0,
        "minimum_quadratic_weighted_kappa": 1.0,
        "maximum_mean_absolute_error": 0.0,
        "maximum_false_pass_rate": 0.0,
        "maximum_invalid_rate": 0.0,
    }
    payload.update(updates)
    return SemanticCalibrationProtocol.model_validate(payload)


def _judge_observations(resolution) -> list[JudgeSemanticObservation]:
    rubric_hash = semantic_rubric_v1().rubric_sha256
    return [
        JudgeSemanticObservation(
            scenario_id=reference.scenario_id,
            output_sha256=reference.output_sha256,
            context_sha256=reference.context_sha256,
            response_mode=reference.response_mode,
            dimension=reference.dimension,
            judge_id="candidate-judge-v2",
            rubric_sha256=rubric_hash,
            valid=True,
            score=reference.score,
        )
        for reference in resolution.human_references
    ]


def test_complete_held_out_validation_can_authorize_only_through_frozen_v2_binding() -> None:
    _, manifest, resolution, evidence = _held_out_fixture()
    protocol = _protocol(manifest.frozen_split_sha256)
    judge = _judge_observations(resolution)

    report = calibrate_semantic_judge_frozen(
        human_references=resolution.human_references,
        judge_observations=judge,
        protocol=protocol,
        evidence_manifest=evidence,
    )

    assert report.state == "CALIBRATED_GATE"
    assert report.gate_authorized is True
    assert report.gate_failures == ()
    assert report.source_split == "VALIDATION"
    assert report.protocol_sha256 == semantic_calibration_protocol_sha256(protocol)
    assert report.evidence_manifest_sha256 == evidence.evidence_manifest_sha256
    assert report.calibration.acceptance_policy_id == protocol.protocol_id
    assert len(report.evidence_sha256) == 64


def test_protocol_hash_binds_thresholds_so_post_hoc_change_is_a_different_protocol() -> None:
    _, manifest, _, _ = _held_out_fixture()
    first = _protocol(manifest.frozen_split_sha256)
    changed = _protocol(
        manifest.frozen_split_sha256,
        maximum_mean_absolute_error=0.5,
    )

    assert first.protocol_id == changed.protocol_id
    assert semantic_calibration_protocol_sha256(first) != semantic_calibration_protocol_sha256(changed)


def test_wrong_rubric_or_split_binding_never_authorizes_gate() -> None:
    _, manifest, resolution, evidence = _held_out_fixture()
    judge = _judge_observations(resolution)

    wrong_rubric = _protocol(manifest.frozen_split_sha256, rubric_sha256="f" * 64)
    rubric_report = calibrate_semantic_judge_frozen(
        human_references=resolution.human_references,
        judge_observations=judge,
        protocol=wrong_rubric,
        evidence_manifest=evidence,
    )
    assert rubric_report.gate_authorized is False
    assert "PROTOCOL_RUBRIC_HASH_MISMATCH" in rubric_report.gate_failures
    assert "EVIDENCE_RUBRIC_HASH_MISMATCH" in rubric_report.gate_failures

    wrong_split = _protocol("e" * 64)
    split_report = calibrate_semantic_judge_frozen(
        human_references=resolution.human_references,
        judge_observations=judge,
        protocol=wrong_split,
        evidence_manifest=evidence,
    )
    assert split_report.gate_authorized is False
    assert "EVIDENCE_FROZEN_SPLIT_HASH_MISMATCH" in split_report.gate_failures


def test_human_reference_set_must_match_hash_bound_evidence_exactly() -> None:
    _, manifest, resolution, evidence = _held_out_fixture()
    protocol = _protocol(manifest.frozen_split_sha256)
    human = list(resolution.human_references)
    removed = human.pop()
    judge = [
        item
        for item in _judge_observations(resolution)
        if not (
            item.scenario_id == removed.scenario_id
            and item.output_sha256 == removed.output_sha256
            and item.context_sha256 == removed.context_sha256
            and item.response_mode == removed.response_mode
            and item.dimension == removed.dimension
        )
    ]

    report = calibrate_semantic_judge_frozen(
        human_references=human,
        judge_observations=judge,
        protocol=protocol,
        evidence_manifest=evidence,
    )

    assert report.gate_authorized is False
    assert report.state == "DESCRIPTIVE_ONLY"
    assert "HUMAN_REFERENCE_EVIDENCE_SET_MISMATCH" in report.gate_failures


def test_evidence_manifest_hash_tampering_is_rejected() -> None:
    _, _, _, evidence = _held_out_fixture()
    payload = evidence.model_dump(mode="json")
    payload["evidence_manifest_sha256"] = "0" * 64

    with pytest.raises(ValidationError, match="semantic_calibration_evidence_hash_mismatch"):
        SemanticCalibrationEvidenceManifest.model_validate(payload)


def test_pilot_packet_cannot_be_promoted_to_calibration_evidence() -> None:
    packet, manifest = build_semantic_reviewer_packet(
        sources=[_source("DEV-A"), _source("DEV-B", escalation=True)],
        frozen_split_payload=_split_payload(),
        purpose="PILOT",
        minimum_distinct_groups=2,
    )
    labels: list[SemanticReviewerLabel] = []
    for task in packet.tasks:
        for slot, reviewer in (("A", "pilot-a"), ("B", "pilot-b")):
            labels.append(
                SemanticReviewerLabel(
                    packet_id=packet.packet_id,
                    task_id=task.task_id,
                    rubric_sha256=packet.rubric_sha256,
                    reviewer_slot=slot,
                    reviewer_ref_sha256=_reviewer_hash(reviewer),
                    score=2,
                    reason_codes=("NO_MATERIAL_DEFECT",),
                )
            )
    resolution = resolve_human_semantic_labels(
        packet=packet,
        manifest=manifest,
        labels=labels,
    )

    with pytest.raises(ValueError, match="requires_held_out_packet"):
        build_semantic_calibration_evidence_manifest(
            packet=packet,
            annotation_manifest=manifest,
            resolution_report=resolution,
        )
