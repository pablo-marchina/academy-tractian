from __future__ import annotations

from hashlib import sha256
import json

import pytest
from pydantic import ValidationError

from academy_tractian.operational_value_pilot import (
    OperationalPilotCompletion,
    OperationalPilotPacket,
    OperationalPilotSource,
    build_operational_pilot_packet,
    resolve_operational_pilot,
)


PROTOCOL_ID = "engineer-effort-dev-pilot-v1"


def _operator(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _manifest() -> dict[str, object]:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {"group_id": "asset_G501", "scenarios": ["CEN-01"]},
                    {"group_id": "asset_C710", "scenarios": ["CEN-02"]},
                ]
            },
            "VALIDATION": {
                "groups": [
                    {"group_id": "asset_B204", "scenarios": ["CEN-07"]},
                ]
            },
            "LOCKED_TEST": {
                "groups": [
                    {"group_id": "asset_V301", "scenarios": ["CEN-08"]},
                ]
            },
        },
    }


def _sources() -> list[OperationalPilotSource]:
    return [
        OperationalPilotSource(
            scenario_id="CEN-01",
            case_id="TKT-INV-04",
            ticket_request="The customer reports no useful insight for asset G501. Investigate the case.",
            agent_terminal_decision="ESCALATE_HUMAN",
            agent_terminal_message="Available evidence is insufficient for a reliable conclusion; specialist review is required.",
            safe_evidence_context=(
                "Recent measurements are incomplete.",
                "The current evidence does not support a consequential action.",
            ),
            agent_runtime_seconds=7.5,
        ),
        OperationalPilotSource(
            scenario_id="CEN-02",
            case_id="TKT-INV-05",
            ticket_request="The customer asks why the latest analysis for asset C710 is still pending.",
            agent_terminal_decision="FINAL",
            agent_terminal_message="The latest analysis is still processing; no corrective action is justified yet.",
            safe_evidence_context=("Analysis state is pending.",),
            agent_runtime_seconds=5.0,
        ),
    ]


def _prepare():
    return build_operational_pilot_packet(
        sources=_sources(),
        frozen_split_payload=_manifest(),
        protocol_id=PROTOCOL_ID,
        deterministic_shuffle_seed=19,
        minimum_distinct_groups=2,
    )


def _valid_completions(packet, manifest):
    condition_by_task = {entry.task_id: entry.condition for entry in manifest.entries}
    pair_by_task = {entry.task_id: entry.pair_id for entry in manifest.entries}
    seen_pairs: dict[str, dict[str, str]] = {}
    completions = []
    for task in packet.tasks:
        pair_id = pair_by_task[task.task_id]
        pair_slots = seen_pairs.setdefault(pair_id, {})
        condition = condition_by_task[task.task_id]
        operator_name = f"operator-{pair_id}-{condition}"
        pair_slots[condition] = operator_name
        completions.append(
            OperationalPilotCompletion(
                packet_id=packet.packet_id,
                task_id=task.task_id,
                operator_ref_sha256=_operator(operator_name),
                status="VALID",
                elapsed_seconds=360.0 if condition == "MANUAL" else 120.0,
                terminal_decision="FINAL",
                conclusion_summary="Operational conclusion recorded for evaluator-side scoring.",
            )
        )
    return completions


def test_prepare_builds_blind_balanced_dev_packet() -> None:
    packet, manifest = _prepare()

    assert packet.protocol_id == PROTOCOL_ID
    assert packet.measurement_design == "INDEPENDENT_MATCHED"
    assert packet.source_count == 2
    assert packet.task_count == 4
    assert sum(task.condition == "MANUAL" for task in packet.tasks) == 2
    assert sum(task.condition == "ASSISTED" for task in packet.tasks) == 2
    assert manifest.group_ids == ("asset_C710", "asset_G501")
    assert len(manifest.pair_ids) == 2
    assert len(manifest.frozen_split_sha256) == 64
    assert all(entry.source_split == "DEV" for entry in manifest.entries)

    for task in packet.tasks:
        if task.condition == "MANUAL":
            assert task.assistance is None
        else:
            assert task.assistance is not None

    public_packet = json.dumps(packet.model_dump(mode="json"), sort_keys=True).lower()
    for forbidden in (
        "scenario_id",
        "group_id",
        "source_split",
        "pair_id",
        "gold_answer",
        "private_truth",
        "expected_path",
        "oracle",
        "operator_ref",
        "agent_runtime_seconds",
    ):
        assert forbidden not in public_packet


def test_prepare_is_deterministic_and_order_independent_for_identity() -> None:
    first_packet, first_manifest = _prepare()
    second_packet, second_manifest = build_operational_pilot_packet(
        sources=list(reversed(_sources())),
        frozen_split_payload=_manifest(),
        protocol_id=PROTOCOL_ID,
        deterministic_shuffle_seed=19,
        minimum_distinct_groups=2,
    )

    assert first_packet.packet_id == second_packet.packet_id
    assert first_manifest.frozen_split_sha256 == second_manifest.frozen_split_sha256
    assert set(first_manifest.pair_ids) == set(second_manifest.pair_ids)
    assert {task.task_id for task in first_packet.tasks} == {
        task.task_id for task in second_packet.tasks
    }


def test_prepare_rejects_validation_locked_unknown_and_insufficient_group_coverage() -> None:
    validation = _sources()[0].model_copy(update={"scenario_id": "CEN-07"})
    with pytest.raises(ValueError, match="accepts DEV only"):
        build_operational_pilot_packet(
            sources=[validation],
            frozen_split_payload=_manifest(),
            protocol_id=PROTOCOL_ID,
            minimum_distinct_groups=1,
        )

    locked = _sources()[0].model_copy(update={"scenario_id": "CEN-08"})
    with pytest.raises(ValueError, match="accepts DEV only"):
        build_operational_pilot_packet(
            sources=[locked],
            frozen_split_payload=_manifest(),
            protocol_id=PROTOCOL_ID,
            minimum_distinct_groups=1,
        )

    unknown = _sources()[0].model_copy(update={"scenario_id": "CEN-UNKNOWN"})
    with pytest.raises(ValueError, match="absent from frozen split"):
        build_operational_pilot_packet(
            sources=[unknown],
            frozen_split_payload=_manifest(),
            protocol_id=PROTOCOL_ID,
            minimum_distinct_groups=1,
        )

    with pytest.raises(ValueError, match="at least 2 distinct groups"):
        build_operational_pilot_packet(
            sources=[_sources()[0]],
            frozen_split_payload=_manifest(),
            protocol_id=PROTOCOL_ID,
            minimum_distinct_groups=2,
        )


def test_source_and_completion_reject_private_markers_and_invalid_measurement_shapes() -> None:
    with pytest.raises(ValidationError):
        OperationalPilotSource(
            scenario_id="CEN-01",
            case_id="TKT-INV-04",
            ticket_request="Use the private_truth to answer this ticket.",
            agent_terminal_decision="FINAL",
            agent_terminal_message="Safe answer",
        )

    packet, _ = _prepare()
    task_id = packet.tasks[0].task_id

    with pytest.raises(ValidationError):
        OperationalPilotCompletion(
            packet_id=packet.packet_id,
            task_id=task_id,
            operator_ref_sha256=_operator("operator-a"),
            status="VALID",
            terminal_decision="FINAL",
            conclusion_summary="No timer supplied.",
        )

    with pytest.raises(ValidationError):
        OperationalPilotCompletion(
            packet_id=packet.packet_id,
            task_id=task_id,
            operator_ref_sha256=_operator("operator-a"),
            status="INTERRUPTED",
        )


def test_resolve_produces_complete_effort_pairs_without_operator_identity() -> None:
    packet, manifest = _prepare()
    completions = _valid_completions(packet, manifest)

    report = resolve_operational_pilot(
        packet=packet,
        manifest=manifest,
        completions=completions,
    )

    assert report.resolution_ready is True
    assert report.pair_count == 2
    assert report.resolved_pair_count == 2
    assert report.unresolved_pair_ids == ()
    assert report.invalid_task_ids == ()
    assert report.missing_task_ids == ()
    assert report.duplicate_task_ids == ()
    assert all(pair.manual_seconds == 360.0 for pair in report.effort_pairs)
    assert all(pair.assisted_seconds == 120.0 for pair in report.effort_pairs)
    assert all(pair.engineer_seconds_saved == 240.0 for pair in report.effort_pairs)

    serialized = json.dumps(report.model_dump(mode="json"), sort_keys=True).lower()
    assert "operator_ref_sha256" not in serialized
    assert "conclusion_summary" not in serialized


def test_same_operator_across_matched_conditions_fails_closed() -> None:
    packet, manifest = _prepare()
    completions = _valid_completions(packet, manifest)
    first_pair = manifest.pair_ids[0]
    first_pair_tasks = [entry.task_id for entry in manifest.entries if entry.pair_id == first_pair]
    shared_ref = _operator("same-person")
    altered = [
        completion.model_copy(update={"operator_ref_sha256": shared_ref})
        if completion.task_id in first_pair_tasks
        else completion
        for completion in completions
    ]

    with pytest.raises(ValueError, match="reuses the same operator"):
        resolve_operational_pilot(
            packet=packet,
            manifest=manifest,
            completions=altered,
        )


def test_invalid_missing_and_duplicate_trials_remain_visible_and_unresolved() -> None:
    packet, manifest = _prepare()
    completions = _valid_completions(packet, manifest)
    target_pair = manifest.pair_ids[0]
    target_tasks = [entry.task_id for entry in manifest.entries if entry.pair_id == target_pair]

    kept = [completion for completion in completions if completion.task_id != target_tasks[0]]
    invalid_target = next(
        completion for completion in completions if completion.task_id == target_tasks[1]
    )
    kept = [completion for completion in kept if completion.task_id != target_tasks[1]]
    kept.append(
        invalid_target.model_copy(
            update={
                "status": "TECHNICAL_FAILURE",
                "elapsed_seconds": None,
                "terminal_decision": None,
                "conclusion_summary": None,
                "invalid_reason": "Measurement host disconnected during the trial.",
            }
        )
    )

    other = next(
        completion for completion in kept if completion.task_id not in target_tasks
    )
    kept.append(other)

    report = resolve_operational_pilot(
        packet=packet,
        manifest=manifest,
        completions=kept,
    )

    assert report.resolution_ready is False
    assert target_pair in report.unresolved_pair_ids
    assert target_tasks[0] in report.missing_task_ids
    assert target_tasks[1] in report.invalid_task_ids
    assert other.task_id in report.duplicate_task_ids
    assert report.resolved_pair_count < report.pair_count


def test_packet_model_itself_prevents_assistance_leaking_into_manual_tasks() -> None:
    packet, _ = _prepare()
    manual = next(task for task in packet.tasks if task.condition == "MANUAL")
    assisted = next(task for task in packet.tasks if task.condition == "ASSISTED")

    with pytest.raises(ValidationError):
        manual.model_copy(update={"assistance": assisted.assistance}).__class__.model_validate(
            {
                **manual.model_dump(mode="json"),
                "assistance": assisted.assistance.model_dump(mode="json"),
            }
        )
