from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from academy_tractian.operational_value import (
    OperationalValueObservation,
    build_operational_value_report,
    operational_value_metric_bundle,
)


PROTOCOL_ID = "engineer-effort-pilot-v1"
DESIGN = "INDEPENDENT_MATCHED"


def _frozen_manifest() -> dict[str, object]:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {
                        "group_id": "group-a",
                        "scenarios": ["scenario-a"],
                    },
                    {
                        "group_id": "group-b",
                        "scenarios": ["scenario-b"],
                    },
                ]
            },
            "VALIDATION": {
                "groups": [
                    {
                        "group_id": "group-c",
                        "scenarios": ["scenario-c"],
                    },
                    {
                        "group_id": "group-d",
                        "scenarios": ["scenario-d"],
                    },
                ]
            },
            "LOCKED_TEST": {
                "groups": [
                    {
                        "group_id": "group-locked",
                        "scenarios": ["scenario-locked"],
                    }
                ]
            },
        },
    }


def _observations() -> list[OperationalValueObservation]:
    return [
        OperationalValueObservation(
            scenario_id="scenario-a",
            group_id="group-a",
            case_id="case-a",
            split="DEV",
            response_mode="complete",
            operational_conclusion_correct=True,
            evidence_correct=True,
            escalation_required=False,
            escalated=False,
            auto_resolved=True,
            manual_baseline_seconds=600.0,
            assisted_human_seconds=0.0,
            effort_protocol_id=PROTOCOL_ID,
            effort_measurement_design=DESIGN,
            agent_runtime_seconds=5.0,
        ),
        OperationalValueObservation(
            scenario_id="scenario-b",
            group_id="group-b",
            case_id="case-b",
            split="DEV",
            response_mode="escalation",
            operational_conclusion_correct=True,
            evidence_correct=True,
            escalation_required=True,
            escalated=True,
            handoff_ready_to_continue=True,
            manual_baseline_seconds=900.0,
            assisted_human_seconds=180.0,
            effort_protocol_id=PROTOCOL_ID,
            effort_measurement_design=DESIGN,
            agent_runtime_seconds=8.0,
        ),
        OperationalValueObservation(
            scenario_id="scenario-c",
            group_id="group-c",
            case_id="case-c",
            split="VALIDATION",
            response_mode="complete",
            operational_conclusion_correct=False,
            evidence_correct=False,
            escalation_required=True,
            escalated=False,
            premature_action=True,
            unsupported_conclusion=True,
            manual_baseline_seconds=600.0,
            assisted_human_seconds=300.0,
            effort_protocol_id=PROTOCOL_ID,
            effort_measurement_design=DESIGN,
            agent_runtime_seconds=10.0,
        ),
        OperationalValueObservation(
            scenario_id="scenario-d",
            group_id="group-d",
            case_id="case-d",
            split="VALIDATION",
            response_mode="escalation",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=True,
            handoff_ready_to_continue=False,
        ),
    ]


def _report(observations: list[OperationalValueObservation]):
    return build_operational_value_report(
        observations,
        frozen_split_payload=_frozen_manifest(),
    )


def _bundle(observations: list[OperationalValueObservation], **kwargs):
    return operational_value_metric_bundle(
        config_id="candidate-v1",
        observations=observations,
        frozen_split_payload=_frozen_manifest(),
        **kwargs,
    )


def test_report_makes_operational_correctness_and_engineer_value_explicit() -> None:
    report = _report(_observations())

    assert report.ticket_count == 4
    assert report.source_splits == ("DEV", "VALIDATION")
    assert len(report.split_manifest_sha256) == 64
    assert report.effort_protocol_ids == (PROTOCOL_ID,)
    assert report.effort_measurement_designs == (DESIGN,)
    assert report.operational_conclusion_accuracy == pytest.approx(0.75)
    assert report.evidence_correctness_sample_count == 3
    assert report.evidence_correctness_rate == pytest.approx(2 / 3)

    assert report.escalation_required_count == 2
    assert report.escalated_count == 2
    assert report.escalation_correctness_rate == pytest.approx(0.5)
    assert report.escalation_precision == pytest.approx(0.5)
    assert report.escalation_recall == pytest.approx(0.5)
    assert report.escalation_f1 == pytest.approx(0.5)

    assert report.premature_action_rate == pytest.approx(0.25)
    assert report.unsupported_conclusion_rate == pytest.approx(0.25)
    assert report.useful_auto_resolution_rate == pytest.approx(0.25)

    assert report.escalated_handoff_sample_count == 2
    assert report.ready_to_continue_escalation_rate == pytest.approx(0.5)
    assert report.restart_from_zero_escalation_rate == pytest.approx(0.5)

    assert report.paired_effort_sample_count == 3
    assert report.effort_sample_coverage_rate == pytest.approx(0.75)
    assert report.manual_baseline_minutes_per_ticket == pytest.approx(35 / 3)
    assert report.human_review_minutes_per_ticket == pytest.approx(8 / 3)
    assert report.engineer_minutes_saved_per_ticket == pytest.approx(9.0)
    assert report.engineer_minutes_saved_total == pytest.approx(27.0)
    assert report.tickets_per_engineer_hour == pytest.approx(22.5)

    assert report.runtime_sample_count == 3
    assert report.agent_runtime_p50_seconds == pytest.approx(8.0)
    assert report.agent_runtime_p95_seconds == pytest.approx(9.8)

    assert report.hard_failure_counts == {
        "MISSED_REQUIRED_ESCALATION": 1,
        "PREMATURE_ACTION": 1,
        "UNSUPPORTED_OPERATIONAL_CONCLUSION": 1,
    }


def test_missing_effort_measurements_remain_unavailable_not_imputed() -> None:
    observation = OperationalValueObservation(
        scenario_id="scenario-a",
        group_id="group-a",
        case_id="case-a",
        split="DEV",
        response_mode="complete",
        operational_conclusion_correct=True,
        escalation_required=False,
        escalated=False,
    )

    report = _report([observation])

    assert report.paired_effort_sample_count == 0
    assert report.effort_sample_coverage_rate == 0.0
    assert report.effort_protocol_ids == ()
    assert report.effort_measurement_designs == ()
    assert report.manual_baseline_minutes_per_ticket is None
    assert report.human_review_minutes_per_ticket is None
    assert report.engineer_minutes_saved_per_ticket is None
    assert report.engineer_minutes_saved_total is None
    assert report.tickets_per_engineer_hour is None


def test_effort_measurement_requires_pair_protocol_and_design() -> None:
    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-a",
            group_id="group-a",
            case_id="case-a",
            split="DEV",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
            manual_baseline_seconds=600.0,
        )

    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-b",
            group_id="group-b",
            case_id="case-b",
            split="DEV",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
            manual_baseline_seconds=600.0,
            assisted_human_seconds=120.0,
        )

    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-c",
            group_id="group-c",
            case_id="case-c",
            split="VALIDATION",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
            effort_protocol_id=PROTOCOL_ID,
            effort_measurement_design=DESIGN,
        )


def test_auto_resolution_cannot_hide_human_work() -> None:
    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-a",
            group_id="group-a",
            case_id="case-a",
            split="DEV",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
            auto_resolved=True,
            manual_baseline_seconds=600.0,
            assisted_human_seconds=30.0,
            effort_protocol_id=PROTOCOL_ID,
            effort_measurement_design=DESIGN,
        )


def test_escalation_handoff_contract_is_fail_closed() -> None:
    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-a",
            group_id="group-a",
            case_id="case-a",
            split="DEV",
            response_mode="escalation",
            operational_conclusion_correct=True,
            escalation_required=True,
            escalated=True,
        )

    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-b",
            group_id="group-b",
            case_id="case-b",
            split="DEV",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
            handoff_ready_to_continue=True,
        )


def test_model_literal_rejects_direct_locked_test_label() -> None:
    with pytest.raises(ValidationError):
        OperationalValueObservation(
            scenario_id="scenario-locked",
            group_id="group-locked",
            case_id="case-locked",
            split="LOCKED_TEST",
            response_mode="complete",
            operational_conclusion_correct=True,
            escalation_required=False,
            escalated=False,
        )


def test_frozen_manifest_rejects_locked_scenario_even_if_caller_lies_about_split() -> None:
    disguised = OperationalValueObservation(
        scenario_id="scenario-locked",
        group_id="group-locked",
        case_id="case-locked",
        split="DEV",
        response_mode="complete",
        operational_conclusion_correct=True,
        escalation_required=False,
        escalated=False,
    )

    with pytest.raises(ValueError, match="LOCKED_TEST scenario"):
        _report([disguised])


def test_frozen_manifest_rejects_split_or_group_disagreement() -> None:
    wrong_split = OperationalValueObservation(
        scenario_id="scenario-c",
        group_id="group-c",
        case_id="case-c",
        split="DEV",
        response_mode="complete",
        operational_conclusion_correct=True,
        escalation_required=False,
        escalated=False,
    )
    with pytest.raises(ValueError, match="caller split disagrees"):
        _report([wrong_split])

    wrong_group = OperationalValueObservation(
        scenario_id="scenario-a",
        group_id="group-b",
        case_id="case-a",
        split="DEV",
        response_mode="complete",
        operational_conclusion_correct=True,
        escalation_required=False,
        escalated=False,
    )
    with pytest.raises(ValueError, match="caller group disagrees"):
        _report([wrong_group])


def test_metric_bundle_uses_existing_group_aware_edd_and_preserves_hard_failures() -> None:
    observations = _observations()
    bundle = _bundle(
        observations,
        metadata={"experiment_id": "value-exp-001"},
    )

    assert bundle.config_id == "candidate-v1"
    assert len(bundle.records) == 4
    assert bundle.metadata["contract"] == "operational-value-v1"
    assert len(bundle.metadata["split_manifest_sha256"]) == 64
    assert bundle.metadata["source_splits"] == ["DEV", "VALIDATION"]
    assert bundle.metadata["effort_sample_coverage_rate"] == pytest.approx(0.75)
    assert bundle.metadata["effort_protocol_ids"] == [PROTOCOL_ID]
    assert bundle.metadata["effort_measurement_designs"] == [DESIGN]
    assert bundle.metadata["experiment_id"] == "value-exp-001"

    by_case = {record.case_id: record for record in bundle.records}
    assert by_case["case-a"].metrics["operational_conclusion_accuracy"] == 1.0
    assert by_case["case-a"].metrics["engineer_minutes_saved"] == pytest.approx(10.0)
    assert by_case["case-b"].metrics["handoff_ready_rate"] == 1.0
    assert by_case["case-c"].hard_gate_failures == (
        "MISSED_REQUIRED_ESCALATION",
        "PREMATURE_ACTION",
        "UNSUPPORTED_OPERATIONAL_CONCLUSION",
    )
    assert "engineer_minutes_saved" not in by_case["case-d"].metrics


def test_incorrect_auto_resolution_is_a_hard_failure_without_weighted_compensation() -> None:
    observation = OperationalValueObservation(
        scenario_id="scenario-a",
        group_id="group-a",
        case_id="case-a",
        split="DEV",
        response_mode="complete",
        operational_conclusion_correct=False,
        escalation_required=False,
        escalated=False,
        auto_resolved=True,
        manual_baseline_seconds=600.0,
        assisted_human_seconds=0.0,
        effort_protocol_id=PROTOCOL_ID,
        effort_measurement_design=DESIGN,
    )

    bundle = _bundle([observation])

    assert bundle.records[0].metrics["useful_auto_resolution_rate"] == 0.0
    assert "INCORRECT_AUTO_RESOLUTION" in bundle.records[0].hard_gate_failures


def test_negative_engineer_minutes_saved_is_preserved_as_a_real_regression() -> None:
    observation = OperationalValueObservation(
        scenario_id="scenario-a",
        group_id="group-a",
        case_id="case-a",
        split="DEV",
        response_mode="escalation",
        operational_conclusion_correct=True,
        escalation_required=True,
        escalated=True,
        handoff_ready_to_continue=True,
        manual_baseline_seconds=120.0,
        assisted_human_seconds=180.0,
        effort_protocol_id=PROTOCOL_ID,
        effort_measurement_design="COUNTERBALANCED_CROSSOVER",
    )

    report = _report([observation])
    bundle = _bundle([observation])

    assert report.engineer_minutes_saved_per_ticket == pytest.approx(-1.0)
    assert bundle.records[0].metrics["engineer_minutes_saved"] == pytest.approx(-1.0)


def test_dataset_hash_and_manifest_hash_are_deterministic_and_no_private_material_is_serialized() -> None:
    first = _report(_observations())
    second = _report(list(reversed(_observations())))

    assert first.dataset_sha256 == second.dataset_sha256
    assert first.split_manifest_sha256 == second.split_manifest_sha256

    serialized = json.dumps(
        {
            "observations": [item.model_dump(mode="json") for item in _observations()],
            "report": first.model_dump(mode="json"),
        },
        sort_keys=True,
    ).lower()

    for forbidden in (
        "gold_answer",
        "expected_answer",
        "private_truth",
        "chain_of_thought",
        "raw_prompt",
        "raw_response",
        "authorization",
        "api_key",
        "user_id",
        "reviewer_name",
        "reviewer_email",
    ):
        assert forbidden not in serialized
