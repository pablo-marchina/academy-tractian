from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI

from .operational_value_collection import OPERATIONAL_VALUE_PARTICIPATE_PERMISSION
from .operational_value_pilot import OperationalPilotSource, build_operational_pilot_packet


_E2E_FLAG = "ACADEMY_E2E_OPERATIONAL_VALUE"
_E2E_ORGANIZATION = "e2e-org-a"


def provider_free_operational_value_enabled() -> bool:
    return os.environ.get(_E2E_FLAG, "0") == "1"


def provider_free_operational_value_permissions() -> frozenset[str]:
    if not provider_free_operational_value_enabled():
        return frozenset()
    return frozenset({OPERATIONAL_VALUE_PARTICIPATE_PERMISSION})


def _frozen_split() -> dict[str, Any]:
    # Acceptance-only split. It proves the real DEV-only packet boundary without importing or
    # exposing any project evaluator truth. VALIDATION/LOCKED_TEST entries exist only because the
    # production builder requires a complete frozen split manifest and are never packet sources.
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {"group_id": "e2e-group-a", "scenarios": ["OV-E2E-01"]},
                    {"group_id": "e2e-group-b", "scenarios": ["OV-E2E-02"]},
                ]
            },
            "VALIDATION": {
                "groups": [
                    {"group_id": "e2e-validation", "scenarios": ["OV-E2E-VALIDATION"]}
                ]
            },
            "LOCKED_TEST": {
                "groups": [
                    {"group_id": "e2e-locked", "scenarios": ["OV-E2E-LOCKED"]}
                ]
            },
        },
    }


def _sources() -> tuple[OperationalPilotSource, ...]:
    return (
        OperationalPilotSource(
            scenario_id="OV-E2E-01",
            case_id="E2E-TICKET-01",
            ticket_request="Investigate why the latest industrial analysis is still pending and record the operational conclusion.",
            agent_terminal_decision="FINAL",
            agent_terminal_message="The analysis is still processing; wait for completion before taking corrective action.",
            safe_evidence_context=(
                "The latest analysis state is pending.",
                "No completed diagnostic result is available yet.",
            ),
            agent_runtime_seconds=2.0,
        ),
        OperationalPilotSource(
            scenario_id="OV-E2E-02",
            case_id="E2E-TICKET-02",
            ticket_request="Investigate an inconclusive asset diagnostic and record whether specialist follow-up is required.",
            agent_terminal_decision="ESCALATE_HUMAN",
            agent_terminal_message="Available evidence is incomplete, so specialist review should continue the investigation.",
            safe_evidence_context=(
                "Recent measurements are incomplete.",
                "The current evidence does not support a definitive corrective action.",
            ),
            agent_runtime_seconds=2.5,
        ),
    )


def register_provider_free_operational_value_packet(app: FastAPI) -> None:
    if not provider_free_operational_value_enabled():
        return
    packet, manifest = build_operational_pilot_packet(
        sources=_sources(),
        frozen_split_payload=_frozen_split(),
        protocol_id="provider-free-operational-value-e2e-v1",
        deterministic_shuffle_seed=20260903,
        minimum_distinct_groups=2,
    )
    app.state.operational_value_collection_store.register_packet(
        organization_id=_E2E_ORGANIZATION,
        packet=packet,
        manifest=manifest,
    )
