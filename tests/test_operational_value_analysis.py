from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.operational_value_analysis import (
    OperationalValueAnalysisProtocol,
    OperationalValueCollectionSnapshot,
    OperationalValueTaskSlot,
    OperationalValueValidMeasurement,
    analyze_operational_value,
    build_operational_value_snapshot,
)


PACKET_ID = "ovpkt_" + "a" * 24


def _pair_ids(count: int) -> tuple[str, ...]:
    return tuple(f"ovpair_{index:024x}" for index in range(1, count + 1))


def _task_id(index: int) -> str:
    return f"ovt_{index:024x}"


def _operator(index: int) -> str:
    return f"{index:064x}"


def _protocol(*, minimum_complete_pairs: int = 4) -> OperationalValueAnalysisProtocol:
    return OperationalValueAnalysisProtocol(
        status="FROZEN",
        protocol_id="engineer-effort-analysis-v1",
        minimum_complete_pairs=minimum_complete_pairs,
        confidence_level=0.95,
        bootstrap_iterations=5000,
        bootstrap_seed=20260903,
    )


def _slots(count: int) -> tuple[OperationalValueTaskSlot, ...]:
    slots: list[OperationalValueTaskSlot] = []
    task_index = 1
    for pair_id in _pair_ids(count):
        slots.append(
            OperationalValueTaskSlot(
                task_id=_task_id(task_index),
                pair_id=pair_id,
                condition="MANUAL",
            )
        )
        task_index += 1
        slots.append(
            OperationalValueTaskSlot(
                task_id=_task_id(task_index),
                pair_id=pair_id,
                condition="ASSISTED",
            )
        )
        task_index += 1
    return tuple(slots)


def _measurements(
    manual: tuple[float, ...],
    assisted: tuple[float, ...],
) -> tuple[OperationalValueValidMeasurement, ...]:
    assert len(manual) == len(assisted)
    measurements: list[OperationalValueValidMeasurement] = []
    task_index = 1
    for pair_index, pair_id in enumerate(_pair_ids(len(manual)), start=1):
        measurements.append(
            OperationalValueValidMeasurement(
                task_id=_task_id(task_index),
                pair_id=pair_id,
                condition="MANUAL",
                operator_ref_sha256=_operator(pair_index * 2 - 1),
                elapsed_seconds=manual[pair_index - 1],
                terminal_decision="ORIENT",
            )
        )
        task_index += 1
        measurements.append(
            OperationalValueValidMeasurement(
                task_id=_task_id(task_index),
                pair_id=pair_id,
                condition="ASSISTED",
                operator_ref_sha256=_operator(pair_index * 2),
                elapsed_seconds=assisted[pair_index - 1],
                terminal_decision="ORIENT",
            )
        )
        task_index += 1
    return tuple(measurements)


def _snapshot(
    *,
    closed: bool = True,
    active: int = 0,
    invalid: int = 0,
    slots: tuple[OperationalValueTaskSlot, ...] | None = None,
    measurements: tuple[OperationalValueValidMeasurement, ...] | None = None,
):
    task_slots = slots if slots is not None else _slots(4)
    valid = measurements if measurements is not None else _measurements(
        (120.0, 180.0, 150.0, 210.0),
        (60.0, 90.0, 90.0, 120.0),
    )
    return build_operational_value_snapshot(
        organization_id="org-a",
        packet_id=PACKET_ID,
        collection_closed=closed,
        active_assignment_count=active,
        invalid_trial_count=invalid,
        task_slots=task_slots,
        valid_measurements=valid,
    )


def test_analysis_computes_paired_engineer_effort_signal_without_business_claim() -> None:
    result = analyze_operational_value(snapshot=_snapshot(invalid=2), protocol=_protocol())

    assert result.status == "POSITIVE_TIME_SIGNAL"
    assert result.business_claim_ready is False
    assert result.requires_operational_quality_gate is True
    assert result.registered_pair_count == 4
    assert result.complete_pair_count == 4
    assert result.incomplete_pair_count == 0
    assert result.invalid_trial_count == 2
    assert result.mean_manual_seconds == pytest.approx(165.0)
    assert result.mean_assisted_seconds == pytest.approx(90.0)
    assert result.mean_delta_seconds == pytest.approx(75.0)
    assert result.median_delta_seconds == pytest.approx(75.0)
    assert result.engineer_minutes_saved_per_ticket == pytest.approx(1.25)
    assert result.observed_engineer_minutes_saved_total == pytest.approx(5.0)
    assert result.relative_time_reduction == pytest.approx(75.0 / 165.0)
    assert result.manual_tickets_per_engineer_hour == pytest.approx(3600.0 / 165.0)
    assert result.assisted_tickets_per_engineer_hour == pytest.approx(40.0)
    assert result.mean_delta_ci_lower_seconds is not None
    assert result.mean_delta_ci_lower_seconds > 0.0
    assert result.mean_delta_ci_upper_seconds is not None
    assert len(result.evidence_sha256) == 64


def test_analysis_is_deterministic_for_same_frozen_snapshot_and_protocol() -> None:
    snapshot = _snapshot()
    protocol = _protocol()
    first = analyze_operational_value(snapshot=snapshot, protocol=protocol)
    second = analyze_operational_value(snapshot=snapshot, protocol=protocol)

    assert first == second
    assert first.evidence_sha256 == second.evidence_sha256
    assert first.protocol_sha256 == second.protocol_sha256
    assert first.snapshot_sha256 == snapshot.snapshot_sha256


def test_analysis_stays_not_ready_until_collection_is_closed_and_complete() -> None:
    full = _snapshot(closed=False)
    assert analyze_operational_value(snapshot=full, protocol=_protocol()).status == "NOT_READY"

    slots = _slots(2)
    only_first_pair = _measurements((120.0,), (60.0,))
    incomplete = _snapshot(
        closed=True,
        slots=slots,
        measurements=only_first_pair,
    )
    result = analyze_operational_value(
        snapshot=incomplete,
        protocol=_protocol(minimum_complete_pairs=2),
    )
    assert result.status == "NOT_READY"
    assert result.registered_pair_count == 2
    assert result.complete_pair_count == 1
    assert result.incomplete_pair_count == 1

    active = _snapshot(active=1)
    assert analyze_operational_value(snapshot=active, protocol=_protocol()).status == "NOT_READY"


def test_analysis_reports_inconclusive_and_negative_time_signals() -> None:
    inconclusive = _snapshot(
        measurements=_measurements(
            (100.0, 100.0, 100.0, 100.0),
            (90.0, 110.0, 90.0, 110.0),
        )
    )
    assert analyze_operational_value(
        snapshot=inconclusive,
        protocol=_protocol(),
    ).status == "INCONCLUSIVE_TIME_SIGNAL"

    negative = _snapshot(
        measurements=_measurements(
            (60.0, 70.0, 80.0, 90.0),
            (120.0, 130.0, 140.0, 150.0),
        )
    )
    result = analyze_operational_value(snapshot=negative, protocol=_protocol())
    assert result.status == "NEGATIVE_TIME_SIGNAL"
    assert result.engineer_minutes_saved_per_ticket is not None
    assert result.engineer_minutes_saved_per_ticket < 0.0


def test_analysis_fails_closed_on_operator_crossover_or_slot_binding_corruption() -> None:
    measurements = list(_measurements((120.0, 180.0), (60.0, 90.0)))
    measurements[1] = measurements[1].model_copy(
        update={"operator_ref_sha256": measurements[0].operator_ref_sha256}
    )
    crossover = _snapshot(
        slots=_slots(2),
        measurements=tuple(measurements),
    )
    with pytest.raises(ValueError, match="operator_crossover"):
        analyze_operational_value(
            snapshot=crossover,
            protocol=_protocol(minimum_complete_pairs=2),
        )

    corrupted = list(_measurements((120.0, 180.0), (60.0, 90.0)))
    corrupted[0] = corrupted[0].model_copy(update={"pair_id": _pair_ids(2)[1]})
    binding_mismatch = _snapshot(
        slots=_slots(2),
        measurements=tuple(corrupted),
    )
    with pytest.raises(ValueError, match="slot_binding_mismatch"):
        analyze_operational_value(
            snapshot=binding_mismatch,
            protocol=_protocol(minimum_complete_pairs=2),
        )


def test_snapshot_hash_rejects_tampering() -> None:
    snapshot = _snapshot()
    payload = snapshot.model_dump(mode="json")
    payload["invalid_trial_count"] = 99
    with pytest.raises(ValidationError, match="snapshot_hash_mismatch"):
        OperationalValueCollectionSnapshot.model_validate(payload)
