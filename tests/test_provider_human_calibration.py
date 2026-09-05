from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.provider_human_calibration import (
    ProviderHumanCalibrationProtocol,
    build_provider_human_calibration_protocol,
    derive_provider_human_calibration_evidence,
)
from academy_tractian.semantic_annotation_sources import (
    SemanticAnnotationSourceManifest,
    SemanticSourceBinding,
    semantic_annotation_source_manifest_sha256,
)
from academy_tractian.semantic_evaluation import HumanSemanticReference
from academy_tractian.semantic_human_calibration import (
    HumanInterRaterDimension,
    SemanticAnnotationManifest,
    SemanticAnnotationManifestEntry,
    SemanticHumanResolutionReport,
)


PACKET_ID = "sempkt_" + "1" * 24
SPLIT_SHA = "2" * 64
SELECTION_SHA = "3" * 64
CONFIG_HASH = "cfg-openai-gpt-5-6-sol"


def _source_manifest(*, config_hashes: tuple[str, str] = (CONFIG_HASH, CONFIG_HASH)) -> SemanticAnnotationSourceManifest:
    bindings = (
        SemanticSourceBinding(
            scenario_id="CEN-VAL-A",
            run_id="run-a",
            config_hash=config_hashes[0],
            output_sha256="4" * 64,
            context_sha256="5" * 64,
        ),
        SemanticSourceBinding(
            scenario_id="CEN-VAL-B",
            run_id="run-b",
            config_hash=config_hashes[1],
            output_sha256="6" * 64,
            context_sha256="7" * 64,
        ),
    )
    manifest_sha = semantic_annotation_source_manifest_sha256(
        split_schema_version="benchmark-split-v1",
        split_sha256=SPLIT_SHA,
        selection_sha256=SELECTION_SHA,
        bindings=bindings,
    )
    return SemanticAnnotationSourceManifest(
        frozen_split_schema_version="benchmark-split-v1",
        frozen_split_sha256=SPLIT_SHA,
        selection_sha256=SELECTION_SHA,
        source_count=2,
        bindings=bindings,
        manifest_sha256=manifest_sha,
    )


def _annotation_manifest() -> SemanticAnnotationManifest:
    return SemanticAnnotationManifest(
        packet_id=PACKET_ID,
        purpose="HELD_OUT_CALIBRATION",
        source_split="VALIDATION",
        frozen_split_schema_version="benchmark-split-v1",
        frozen_split_sha256=SPLIT_SHA,
        group_ids=("val-a", "val-b"),
        entries=(
            SemanticAnnotationManifestEntry(
                task_id="sem_" + "8" * 24,
                scenario_id="CEN-VAL-A",
                group_id="val-a",
                source_split="VALIDATION",
                output_sha256="4" * 64,
                context_sha256="5" * 64,
                response_mode="complete",
                dimension="operational_usefulness",
            ),
            SemanticAnnotationManifestEntry(
                task_id="sem_" + "9" * 24,
                scenario_id="CEN-VAL-B",
                group_id="val-b",
                source_split="VALIDATION",
                output_sha256="6" * 64,
                context_sha256="7" * 64,
                response_mode="partial",
                dimension="operational_usefulness",
            ),
        ),
    )


def _resolution_report(*, calibration_ready: bool = True) -> SemanticHumanResolutionReport:
    references = (
        HumanSemanticReference(
            scenario_id="CEN-VAL-A",
            output_sha256="4" * 64,
            context_sha256="5" * 64,
            response_mode="complete",
            dimension="operational_usefulness",
            score=2,
            resolution="AGREED",
            annotator_count=2,
        ),
        HumanSemanticReference(
            scenario_id="CEN-VAL-B",
            output_sha256="6" * 64,
            context_sha256="7" * 64,
            response_mode="partial",
            dimension="operational_usefulness",
            score=1,
            resolution="ADJUDICATED",
            annotator_count=3,
        ),
    )
    return SemanticHumanResolutionReport(
        packet_id=PACKET_ID,
        rubric_sha256="a" * 64,
        task_count=2,
        resolved_count=2 if calibration_ready else 1,
        agreed_count=1,
        adjudicated_count=1 if calibration_ready else 0,
        unresolved_task_ids=() if calibration_ready else ("sem_" + "9" * 24,),
        calibration_ready=calibration_ready,
        human_references=references,
        inter_rater=(
            HumanInterRaterDimension(
                dimension="operational_usefulness",
                paired_tasks=2,
                exact_agreement=0.5,
                adjacent_agreement=1.0,
                quadratic_weighted_kappa=0.0,
                disagreements=1,
            ),
        ),
    )


def _protocol():
    return build_provider_human_calibration_protocol(protocol_id="provider-human-oca-v1")


def test_derives_hash_bound_candidate_oca_and_wilson_lower_bound() -> None:
    artifact = derive_provider_human_calibration_evidence(
        candidate_id="openai:gpt-5.6-sol",
        protocol=_protocol(),
        source_manifest=_source_manifest(),
        annotation_manifest=_annotation_manifest(),
        resolution_report=_resolution_report(),
    )

    assert artifact.candidate_id == "openai:gpt-5.6-sol"
    assert artifact.config_hash == CONFIG_HASH
    assert artifact.calibration_ready is True
    assert artifact.case_count == 2
    assert artifact.human_agreement_rate == 0.5
    assert artifact.operational_conclusion_accuracy == 0.5
    assert artifact.operational_conclusion_accuracy_ci_low == pytest.approx(
        0.09453120573423074,
        rel=1e-12,
    )
    assert artifact.protocol_hash == _protocol().protocol_sha256
    assert len(artifact.artifact_sha256) == 64


def test_protocol_is_hash_bound_and_tampering_fails_validation() -> None:
    protocol = _protocol()
    payload = protocol.model_dump(mode="json")
    payload["protocol_id"] = "tampered"

    with pytest.raises(
        ValidationError,
        match="provider_human_calibration_protocol_hash_mismatch",
    ):
        ProviderHumanCalibrationProtocol.model_validate(payload)


def test_mixed_candidate_config_hashes_are_rejected() -> None:
    with pytest.raises(ValueError, match="mixed_config_hashes"):
        derive_provider_human_calibration_evidence(
            candidate_id="openai:gpt-5.6-sol",
            protocol=_protocol(),
            source_manifest=_source_manifest(config_hashes=(CONFIG_HASH, "cfg-other-model")),
            annotation_manifest=_annotation_manifest(),
            resolution_report=_resolution_report(),
        )


def test_incomplete_human_resolution_cannot_create_promotion_evidence() -> None:
    with pytest.raises(ValueError, match="resolution_not_ready"):
        derive_provider_human_calibration_evidence(
            candidate_id="openai:gpt-5.6-sol",
            protocol=_protocol(),
            source_manifest=_source_manifest(),
            annotation_manifest=_annotation_manifest(),
            resolution_report=_resolution_report(calibration_ready=False),
        )


def test_source_annotation_binding_mismatch_is_rejected() -> None:
    annotation = _annotation_manifest()
    payload = annotation.model_dump(mode="json")
    payload["entries"][0]["output_sha256"] = "b" * 64
    mismatched = SemanticAnnotationManifest.model_validate(payload)

    with pytest.raises(ValueError, match="source_annotation_mismatch"):
        derive_provider_human_calibration_evidence(
            candidate_id="openai:gpt-5.6-sol",
            protocol=_protocol(),
            source_manifest=_source_manifest(),
            annotation_manifest=mismatched,
            resolution_report=_resolution_report(),
        )
