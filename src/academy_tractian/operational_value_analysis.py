from __future__ import annotations

from hashlib import sha256
import json
from math import ceil, floor
from random import Random
from statistics import mean, median
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.models import Decision


OperationalPilotCondition = Literal["MANUAL", "ASSISTED"]
OperationalValueEvidenceStatus = Literal[
    "NOT_READY",
    "EVIDENCE_POSITIVE",
    "EVIDENCE_INCONCLUSIVE",
    "EVIDENCE_NEGATIVE",
]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OperationalValueValidMeasurement(_FrozenModel):
    task_id: str = Field(pattern=r"^ovt_[0-9a-f]{24}$")
    pair_id: str = Field(pattern=r"^ovpair_[0-9a-f]{24}$")
    condition: OperationalPilotCondition
    operator_ref_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    elapsed_seconds: float = Field(gt=0.0)
    terminal_decision: Decision


class OperationalValueCollectionSnapshot(_FrozenModel):
    schema_version: Literal["operational-value-snapshot-v1"] = "operational-value-snapshot-v1"
    organization_id: str = Field(min_length=1)
    packet_id: str = Field(pattern=r"^ovpkt_[0-9a-f]{24}$")
    collection_closed: bool
    active_assignment_count: int = Field(ge=0)
    invalid_trial_count: int = Field(ge=0)
    valid_measurements: tuple[OperationalValueValidMeasurement, ...]
    snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_snapshot_hash(self) -> "OperationalValueCollectionSnapshot":
        expected = operational_value_snapshot_sha256(
            organization_id=self.organization_id,
            packet_id=self.packet_id,
            collection_closed=self.collection_closed,
            active_assignment_count=self.active_assignment_count,
            invalid_trial_count=self.invalid_trial_count,
            valid_measurements=self.valid_measurements,
        )
        if self.snapshot_sha256 != expected:
            raise ValueError("operational_value_snapshot_hash_mismatch")
        return self


class OperationalValueAnalysisProtocol(_FrozenModel):
    schema_version: Literal["operational-value-analysis-protocol-v1"] = (
        "operational-value-analysis-protocol-v1"
    )
    status: Literal["FROZEN"]
    protocol_id: str = Field(min_length=1, max_length=128)
    minimum_complete_pairs: int = Field(ge=2, le=100000)
    confidence_level: float = Field(gt=0.5, lt=1.0)
    bootstrap_iterations: int = Field(ge=1000, le=1000000)
    bootstrap_seed: int


class OperationalValuePairResult(_FrozenModel):
    pair_index: int = Field(ge=1)
    manual_seconds: float = Field(gt=0.0)
    assisted_seconds: float = Field(gt=0.0)
    delta_seconds: float


class OperationalValueAnalysisResult(_FrozenModel):
    schema_version: Literal["operational-value-analysis-v1"] = "operational-value-analysis-v1"
    status: OperationalValueEvidenceStatus
    protocol_id: str
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    collection_closed: bool
    active_assignment_count: int = Field(ge=0)
    invalid_trial_count: int = Field(ge=0)
    valid_measurement_count: int = Field(ge=0)
    complete_pair_count: int = Field(ge=0)
    incomplete_pair_count: int = Field(ge=0)
    minimum_complete_pairs: int = Field(ge=2)
    mean_manual_seconds: float | None = None
    mean_assisted_seconds: float | None = None
    mean_delta_seconds: float | None = None
    median_delta_seconds: float | None = None
    engineer_minutes_saved_per_ticket: float | None = None
    observed_engineer_minutes_saved_total: float | None = None
    relative_time_reduction: float | None = None
    manual_tickets_per_engineer_hour: float | None = None
    assisted_tickets_per_engineer_hour: float | None = None
    mean_delta_ci_lower_seconds: float | None = None
    mean_delta_ci_upper_seconds: float | None = None
    confidence_level: float
    paired_results: tuple[OperationalValuePairResult, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def operational_value_protocol_sha256(protocol: OperationalValueAnalysisProtocol) -> str:
    payload = protocol.model_dump(mode="json")
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def operational_value_snapshot_sha256(
    *,
    organization_id: str,
    packet_id: str,
    collection_closed: bool,
    active_assignment_count: int,
    invalid_trial_count: int,
    valid_measurements: tuple[OperationalValueValidMeasurement, ...],
) -> str:
    ordered = sorted(
        (measurement.model_dump(mode="json") for measurement in valid_measurements),
        key=lambda item: (str(item["pair_id"]), str(item["condition"]), str(item["task_id"])),
    )
    payload = {
        "schema_version": "operational-value-snapshot-v1",
        "organization_id": organization_id,
        "packet_id": packet_id,
        "collection_closed": collection_closed,
        "active_assignment_count": active_assignment_count,
        "invalid_trial_count": invalid_trial_count,
        "valid_measurements": ordered,
    }
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_operational_value_snapshot(
    *,
    organization_id: str,
    packet_id: str,
    collection_closed: bool,
    active_assignment_count: int,
    invalid_trial_count: int,
    valid_measurements: tuple[OperationalValueValidMeasurement, ...],
) -> OperationalValueCollectionSnapshot:
    snapshot_hash = operational_value_snapshot_sha256(
        organization_id=organization_id,
        packet_id=packet_id,
        collection_closed=collection_closed,
        active_assignment_count=active_assignment_count,
        invalid_trial_count=invalid_trial_count,
        valid_measurements=valid_measurements,
    )
    return OperationalValueCollectionSnapshot(
        organization_id=organization_id,
        packet_id=packet_id,
        collection_closed=collection_closed,
        active_assignment_count=active_assignment_count,
        invalid_trial_count=invalid_trial_count,
        valid_measurements=valid_measurements,
        snapshot_sha256=snapshot_hash,
    )


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("percentile_requires_values")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = floor(position)
    upper = ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _paired_bootstrap_mean_delta_ci(
    deltas: tuple[float, ...],
    *,
    confidence_level: float,
    iterations: int,
    seed: int,
) -> tuple[float, float] | None:
    if len(deltas) < 2:
        return None
    rng = Random(seed)
    count = len(deltas)
    bootstrap_means: list[float] = []
    for _ in range(iterations):
        bootstrap_means.append(mean(deltas[rng.randrange(count)] for _ in range(count)))
    alpha = 1.0 - confidence_level
    return (
        _percentile(bootstrap_means, alpha / 2.0),
        _percentile(bootstrap_means, 1.0 - alpha / 2.0),
    )


def _pair_measurements(
    measurements: tuple[OperationalValueValidMeasurement, ...],
) -> tuple[tuple[OperationalValuePairResult, ...], int]:
    grouped: dict[str, dict[str, OperationalValueValidMeasurement]] = {}
    for measurement in measurements:
        conditions = grouped.setdefault(measurement.pair_id, {})
        if measurement.condition in conditions:
            raise ValueError("operational_value_duplicate_valid_condition_for_pair")
        conditions[measurement.condition] = measurement

    complete: list[tuple[str, OperationalValueValidMeasurement, OperationalValueValidMeasurement]] = []
    incomplete = 0
    for pair_id, conditions in grouped.items():
        manual = conditions.get("MANUAL")
        assisted = conditions.get("ASSISTED")
        if manual is None or assisted is None:
            incomplete += 1
            continue
        if manual.operator_ref_sha256 == assisted.operator_ref_sha256:
            raise ValueError("operational_value_pair_operator_crossover")
        complete.append((pair_id, manual, assisted))

    complete.sort(key=lambda row: row[0])
    paired_results = tuple(
        OperationalValuePairResult(
            pair_index=index,
            manual_seconds=manual.elapsed_seconds,
            assisted_seconds=assisted.elapsed_seconds,
            delta_seconds=manual.elapsed_seconds - assisted.elapsed_seconds,
        )
        for index, (_pair_id, manual, assisted) in enumerate(complete, start=1)
    )
    return paired_results, incomplete


def analyze_operational_value(
    *,
    snapshot: OperationalValueCollectionSnapshot,
    protocol: OperationalValueAnalysisProtocol,
) -> OperationalValueAnalysisResult:
    protocol_hash = operational_value_protocol_sha256(protocol)
    paired_results, incomplete_pair_count = _pair_measurements(snapshot.valid_measurements)
    complete_pair_count = len(paired_results)

    mean_manual_seconds: float | None = None
    mean_assisted_seconds: float | None = None
    mean_delta_seconds: float | None = None
    median_delta_seconds: float | None = None
    engineer_minutes_saved_per_ticket: float | None = None
    observed_engineer_minutes_saved_total: float | None = None
    relative_time_reduction: float | None = None
    manual_tickets_per_engineer_hour: float | None = None
    assisted_tickets_per_engineer_hour: float | None = None
    ci_lower: float | None = None
    ci_upper: float | None = None

    if paired_results:
        manual_times = tuple(result.manual_seconds for result in paired_results)
        assisted_times = tuple(result.assisted_seconds for result in paired_results)
        deltas = tuple(result.delta_seconds for result in paired_results)
        mean_manual_seconds = mean(manual_times)
        mean_assisted_seconds = mean(assisted_times)
        mean_delta_seconds = mean(deltas)
        median_delta_seconds = median(deltas)
        engineer_minutes_saved_per_ticket = mean_delta_seconds / 60.0
        observed_engineer_minutes_saved_total = sum(deltas) / 60.0
        relative_time_reduction = mean_delta_seconds / mean_manual_seconds
        manual_tickets_per_engineer_hour = 3600.0 / mean_manual_seconds
        assisted_tickets_per_engineer_hour = 3600.0 / mean_assisted_seconds
        ci = _paired_bootstrap_mean_delta_ci(
            deltas,
            confidence_level=protocol.confidence_level,
            iterations=protocol.bootstrap_iterations,
            seed=protocol.bootstrap_seed,
        )
        if ci is not None:
            ci_lower, ci_upper = ci

    ready = (
        snapshot.collection_closed
        and snapshot.active_assignment_count == 0
        and complete_pair_count >= protocol.minimum_complete_pairs
        and ci_lower is not None
        and ci_upper is not None
    )
    if not ready:
        evidence_status: OperationalValueEvidenceStatus = "NOT_READY"
    elif ci_lower > 0.0:
        evidence_status = "EVIDENCE_POSITIVE"
    elif ci_upper < 0.0:
        evidence_status = "EVIDENCE_NEGATIVE"
    else:
        evidence_status = "EVIDENCE_INCONCLUSIVE"

    result_payload = {
        "schema_version": "operational-value-analysis-v1",
        "status": evidence_status,
        "protocol_id": protocol.protocol_id,
        "protocol_sha256": protocol_hash,
        "snapshot_sha256": snapshot.snapshot_sha256,
        "collection_closed": snapshot.collection_closed,
        "active_assignment_count": snapshot.active_assignment_count,
        "invalid_trial_count": snapshot.invalid_trial_count,
        "valid_measurement_count": len(snapshot.valid_measurements),
        "complete_pair_count": complete_pair_count,
        "incomplete_pair_count": incomplete_pair_count,
        "minimum_complete_pairs": protocol.minimum_complete_pairs,
        "mean_manual_seconds": mean_manual_seconds,
        "mean_assisted_seconds": mean_assisted_seconds,
        "mean_delta_seconds": mean_delta_seconds,
        "median_delta_seconds": median_delta_seconds,
        "engineer_minutes_saved_per_ticket": engineer_minutes_saved_per_ticket,
        "observed_engineer_minutes_saved_total": observed_engineer_minutes_saved_total,
        "relative_time_reduction": relative_time_reduction,
        "manual_tickets_per_engineer_hour": manual_tickets_per_engineer_hour,
        "assisted_tickets_per_engineer_hour": assisted_tickets_per_engineer_hour,
        "mean_delta_ci_lower_seconds": ci_lower,
        "mean_delta_ci_upper_seconds": ci_upper,
        "confidence_level": protocol.confidence_level,
        "paired_results": [result.model_dump(mode="json") for result in paired_results],
    }
    evidence_hash = sha256(_canonical_json(result_payload).encode("utf-8")).hexdigest()
    return OperationalValueAnalysisResult(
        **result_payload,
        evidence_sha256=evidence_hash,
    )
