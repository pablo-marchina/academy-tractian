from __future__ import annotations

from hashlib import sha256
import json
from math import sqrt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .provider_promotion import (
    ProviderHumanCalibrationEvidence,
    build_provider_human_calibration_artifact,
)
from .semantic_annotation_sources import SemanticAnnotationSourceManifest
from .semantic_human_calibration import (
    SemanticAnnotationManifest,
    SemanticHumanResolutionReport,
)


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


def _model_sha256(model: BaseModel) -> str:
    return _canonical_sha256(model.model_dump(mode="json"))


class ProviderHumanCalibrationProtocol(_StrictModel):
    """Frozen computation contract for candidate-level human OCA evidence.

    This protocol defines *how* the metric is computed, not the promotion threshold. Thresholds
    remain preregistered independently in ``ProviderPromotionPolicy`` so observed validation
    outcomes cannot silently change the acceptance rule.
    """

    schema_version: Literal["provider-human-calibration-protocol-v1"] = (
        "provider-human-calibration-protocol-v1"
    )
    status: Literal["FROZEN"] = "FROZEN"
    protocol_id: str = Field(min_length=1, max_length=128)
    source_split: Literal["VALIDATION"] = "VALIDATION"
    dimension: Literal["operational_usefulness"] = "operational_usefulness"
    passing_score: Literal[2] = 2
    confidence_level: Literal[0.95] = 0.95
    interval_method: Literal["wilson_score"] = "wilson_score"
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_hash(self) -> "ProviderHumanCalibrationProtocol":
        material = self.model_dump(mode="json", exclude={"protocol_sha256"})
        if self.protocol_sha256 != _canonical_sha256(material):
            raise ValueError("provider_human_calibration_protocol_hash_mismatch")
        return self


def build_provider_human_calibration_protocol(
    *,
    protocol_id: str,
) -> ProviderHumanCalibrationProtocol:
    material = {
        "schema_version": "provider-human-calibration-protocol-v1",
        "status": "FROZEN",
        "protocol_id": protocol_id,
        "source_split": "VALIDATION",
        "dimension": "operational_usefulness",
        "passing_score": 2,
        "confidence_level": 0.95,
        "interval_method": "wilson_score",
    }
    return ProviderHumanCalibrationProtocol.model_validate(
        {
            **material,
            "protocol_sha256": _canonical_sha256(material),
        }
    )


def _wilson_lower_bound_95(successes: int, total: int) -> float:
    if total <= 0:
        raise ValueError("provider_human_calibration_requires_at_least_one_case")
    if successes < 0 or successes > total:
        raise ValueError("provider_human_calibration_success_count_invalid")

    # 0.975 quantile of the standard normal distribution for a two-sided 95% interval.
    z = 1.959963984540054
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    margin = (
        z
        * sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)
        / denominator
    )
    return max(0.0, center - margin)


def derive_provider_human_calibration_evidence(
    *,
    candidate_id: str,
    protocol: ProviderHumanCalibrationProtocol,
    source_manifest: SemanticAnnotationSourceManifest,
    annotation_manifest: SemanticAnnotationManifest,
    resolution_report: SemanticHumanResolutionReport,
) -> ProviderHumanCalibrationEvidence:
    """Derive candidate OCA directly from complete adjudicated held-out human evidence.

    The function refuses mixed configurations, incomplete human resolution, split mismatches and
    any mismatch between the source manifest, reviewer annotation manifest and resolved human
    references. OCA is the fraction of held-out ``operational_usefulness`` cases scored 2 by the
    resolved human reference. The lower confidence bound is the Wilson two-sided 95% interval.
    """

    if annotation_manifest.purpose != "HELD_OUT_CALIBRATION":
        raise ValueError("provider_human_calibration_requires_held_out_calibration")
    if annotation_manifest.source_split != protocol.source_split:
        raise ValueError("provider_human_calibration_source_split_mismatch")
    if source_manifest.source_split != protocol.source_split:
        raise ValueError("provider_human_calibration_source_manifest_split_mismatch")
    if source_manifest.frozen_split_sha256 != annotation_manifest.frozen_split_sha256:
        raise ValueError("provider_human_calibration_frozen_split_mismatch")
    if resolution_report.packet_id != annotation_manifest.packet_id:
        raise ValueError("provider_human_calibration_packet_mismatch")
    if not resolution_report.calibration_ready or resolution_report.unresolved_task_ids:
        raise ValueError("provider_human_calibration_resolution_not_ready")

    config_hashes = {binding.config_hash for binding in source_manifest.bindings}
    if len(config_hashes) != 1:
        raise ValueError("provider_human_calibration_mixed_config_hashes")
    config_hash = next(iter(config_hashes))

    source_keys = {
        (binding.scenario_id, binding.output_sha256, binding.context_sha256)
        for binding in source_manifest.bindings
    }
    if len(source_keys) != source_manifest.source_count:
        raise ValueError("provider_human_calibration_source_binding_not_unique")

    operational_entries = tuple(
        entry
        for entry in annotation_manifest.entries
        if entry.dimension == protocol.dimension
    )
    if not operational_entries:
        raise ValueError("provider_human_calibration_has_no_operational_cases")
    annotation_source_keys = {
        (entry.scenario_id, entry.output_sha256, entry.context_sha256)
        for entry in operational_entries
    }
    if annotation_source_keys != source_keys:
        raise ValueError("provider_human_calibration_source_annotation_mismatch")
    if len(operational_entries) != len(annotation_source_keys):
        raise ValueError("provider_human_calibration_duplicate_operational_case")

    expected_reference_keys = {
        (
            entry.scenario_id,
            entry.output_sha256,
            entry.context_sha256,
            entry.response_mode,
            entry.dimension,
        )
        for entry in operational_entries
    }
    operational_references = tuple(
        reference
        for reference in resolution_report.human_references
        if reference.dimension == protocol.dimension
    )
    actual_reference_keys = {
        (
            reference.scenario_id,
            reference.output_sha256,
            reference.context_sha256,
            reference.response_mode,
            reference.dimension,
        )
        for reference in operational_references
    }
    if actual_reference_keys != expected_reference_keys:
        raise ValueError("provider_human_calibration_reference_mismatch")
    if len(operational_references) != len(actual_reference_keys):
        raise ValueError("provider_human_calibration_duplicate_reference")

    agreement_metrics = tuple(
        metric
        for metric in resolution_report.inter_rater
        if metric.dimension == protocol.dimension
    )
    if len(agreement_metrics) != 1:
        raise ValueError("provider_human_calibration_inter_rater_metric_missing")
    agreement = agreement_metrics[0]
    case_count = len(operational_references)
    if agreement.paired_tasks != case_count or agreement.exact_agreement is None:
        raise ValueError("provider_human_calibration_inter_rater_count_mismatch")

    successes = sum(reference.score == protocol.passing_score for reference in operational_references)
    oca = successes / case_count
    oca_ci_low = _wilson_lower_bound_95(successes, case_count)

    return build_provider_human_calibration_artifact(
        candidate_id=candidate_id,
        config_hash=config_hash,
        protocol_id=protocol.protocol_id,
        protocol_hash=protocol.protocol_sha256,
        source_manifest_sha256=source_manifest.manifest_sha256,
        annotation_manifest_sha256=_model_sha256(annotation_manifest),
        resolution_report_sha256=_model_sha256(resolution_report),
        calibration_ready=True,
        case_count=case_count,
        human_agreement_rate=agreement.exact_agreement,
        operational_conclusion_accuracy=oca,
        operational_conclusion_accuracy_ci_low=oca_ci_low,
    )
