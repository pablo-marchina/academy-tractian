from __future__ import annotations

from hashlib import sha256

import pytest
from pydantic import ValidationError

from academy_tractian.operational_value_pilot import (
    OperationalPilotCompletion,
    OperationalPilotPacket,
    OperationalPilotSource,
    build_operational_pilot_packet,
    resolve_operational_pilot,
)


def _ref(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _split_manifest() -> dict[str, object]:
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
                "groups": [{"group_id": "asset_B204", "scenarios": ["CEN-07"]}]
            },
            "LOCKED_TEST": {
                "groups": [{"group_id": "asset_V301", "scenarios": ["CEN-08"]}]
            },
        },
    }


def _sources() -> list[OperationalPilotSource]:
    return [
        OperationalPilotSource(
            scenario_id="CEN-01",
            case_id="TKT-INV-04",
            ticket_request="Investigate why the expected monitoring insight is unavailable.",
            agent_terminal_decision="ESCALATE_HUMAN",
            agent_terminal_message="Evidence is insufficient for a reliable automated conclusion.",
            safe_evidence_context=("Required recent measurements are incomplete.",),
            agent_runtime_seconds=4.0,
        ),
        OperationalPilotSource(
            scenario_id="CEN-02",
            case_id="TKT-INV-05",
            ticket_request="Investigate why the latest monitoring analysis remains pending.",
            agent_terminal_decision="FINAL",
            agent_terminal_message="The analysis is still processing; no action is justified yet.",
            safe_evidence_context=("The current analysis state is pending.",),
            agent_runtime_seconds=3.0,
        ),
    ]


def _prepare():
    return build_operational_pilot_packet(
        sources=_sources(),
        frozen_split_payload=_split_manifest(),
        protocol_id="effort-pilot-integrity-v1",
        deterministic_shuffle_seed=31,
    )


def _completions(packet, manifest):
    result = []
    entry_by_task = {entry.task_id: entry for entry in manifest.entries}
    for task in packet.tasks:
        entry = entry_by_task[task.task_id]
        result.append(
            OperationalPilotCompletion(
                packet_id=packet.packet_id,
                task_id=task.task_id,
                operator_ref_sha256=_ref(f"{entry.pair_id}:{entry.condition}"),
                status="VALID",
                elapsed_seconds=240.0 if entry.condition == "MANUAL" else 90.0,
                terminal_decision="FINAL",
                conclusion_summary="A safe operational conclusion for evaluator-side scoring.",
            )
        )
    return result


def test_resolver_rejects_ticket_content_tampering_after_prepare() -> None:
    packet, manifest = _prepare()
    payload = packet.model_dump(mode="json")
    payload["tasks"][0]["ticket_request"] = "A different but still public-safe ticket was substituted."
    tampered = OperationalPilotPacket.model_validate(payload)

    with pytest.raises(ValueError, match="ticket content hash mismatch"):
        resolve_operational_pilot(
            packet=tampered,
            manifest=manifest,
            completions=_completions(tampered, manifest),
        )


def test_resolver_rejects_assistance_content_tampering_after_prepare() -> None:
    packet, manifest = _prepare()
    payload = packet.model_dump(mode="json")
    assisted = next(task for task in payload["tasks"] if task["condition"] == "ASSISTED")
    assisted["assistance"]["terminal_message"] = "A substituted safe-looking agent conclusion."
    tampered = OperationalPilotPacket.model_validate(payload)

    with pytest.raises(ValueError, match="assistance content hash mismatch"):
        resolve_operational_pilot(
            packet=tampered,
            manifest=manifest,
            completions=_completions(tampered, manifest),
        )


def test_loaded_packet_rejects_private_markers_even_if_source_validation_was_bypassed() -> None:
    packet, _ = _prepare()
    payload = packet.model_dump(mode="json")
    payload["tasks"][0]["ticket_request"] = "Read private_truth before deciding."

    with pytest.raises(ValidationError):
        OperationalPilotPacket.model_validate(payload)


def test_resolver_revalidates_nonvalidating_model_copy_completion() -> None:
    packet, manifest = _prepare()
    completions = _completions(packet, manifest)
    invalid_copy = completions[0].model_copy(update={"elapsed_seconds": None})
    completions[0] = invalid_copy

    with pytest.raises(ValidationError):
        resolve_operational_pilot(
            packet=packet,
            manifest=manifest,
            completions=completions,
        )


def test_entire_host_packet_is_order_invariant_for_same_sources_and_seed() -> None:
    first_packet, first_manifest = _prepare()
    second_packet, second_manifest = build_operational_pilot_packet(
        sources=list(reversed(_sources())),
        frozen_split_payload=_split_manifest(),
        protocol_id="effort-pilot-integrity-v1",
        deterministic_shuffle_seed=31,
    )

    assert first_packet.model_dump(mode="json") == second_packet.model_dump(mode="json")
    assert first_manifest.model_dump(mode="json") == second_manifest.model_dump(mode="json")
