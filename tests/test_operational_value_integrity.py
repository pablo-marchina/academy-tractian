from __future__ import annotations

import pytest

from academy_tractian.operational_value import (
    OperationalValueObservation,
    build_operational_value_report,
    operational_value_metric_bundle,
)


def _manifest() -> dict[str, object]:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {"group_id": "group-a", "scenarios": ["scenario-a"]},
                    {"group_id": "group-b", "scenarios": ["scenario-b"]},
                ]
            },
            "VALIDATION": {
                "groups": [
                    {"group_id": "group-v", "scenarios": ["scenario-v"]},
                ]
            },
            "LOCKED_TEST": {
                "groups": [
                    {"group_id": "group-l", "scenarios": ["scenario-l"]},
                ]
            },
        },
    }


def _observations() -> list[OperationalValueObservation]:
    return [
        OperationalValueObservation(
            scenario_id="scenario-b",
            group_id="group-b",
            case_id="case-b",
            split="DEV",
            response_mode="escalation",
            operational_conclusion_correct=True,
            escalation_required=True,
            escalated=True,
            handoff_ready_to_continue=True,
        ),
        OperationalValueObservation(
            scenario_id="scenario-a",
            group_id="group-a",
            case_id="case-a",
            split="DEV",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
        ),
    ]


def test_bundle_is_order_invariant() -> None:
    first = operational_value_metric_bundle(
        config_id="candidate-v1",
        observations=_observations(),
        frozen_split_payload=_manifest(),
    )
    second = operational_value_metric_bundle(
        config_id="candidate-v1",
        observations=list(reversed(_observations())),
        frozen_split_payload=_manifest(),
    )

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert [record.case_id for record in first.records] == ["case-a", "case-b"]


def test_caller_metadata_cannot_override_canonical_hashes_or_contract_fields() -> None:
    for reserved_key in (
        "contract",
        "dataset_sha256",
        "split_manifest_sha256",
        "source_splits",
        "ticket_count",
    ):
        with pytest.raises(ValueError, match="cannot override canonical"):
            operational_value_metric_bundle(
                config_id="candidate-v1",
                observations=_observations(),
                frozen_split_payload=_manifest(),
                metadata={reserved_key: "attacker-controlled"},
            )


def test_manifest_must_be_frozen_and_complete() -> None:
    not_frozen = _manifest()
    not_frozen["status"] = "DRAFT"
    with pytest.raises(ValueError, match="must be FROZEN"):
        build_operational_value_report(
            _observations(),
            frozen_split_payload=not_frozen,
        )

    incomplete = _manifest()
    splits = incomplete["splits"]
    assert isinstance(splits, dict)
    del splits["LOCKED_TEST"]
    with pytest.raises(ValueError, match="missing LOCKED_TEST"):
        build_operational_value_report(
            _observations(),
            frozen_split_payload=incomplete,
        )


def test_scenario_absent_from_frozen_manifest_is_rejected() -> None:
    unknown = OperationalValueObservation(
        scenario_id="scenario-unknown",
        group_id="group-a",
        case_id="case-unknown",
        split="DEV",
        response_mode="complete",
        operational_conclusion_correct=True,
        escalation_required=False,
        escalated=False,
    )

    with pytest.raises(ValueError, match="scenario absent"):
        build_operational_value_report(
            [unknown],
            frozen_split_payload=_manifest(),
        )
