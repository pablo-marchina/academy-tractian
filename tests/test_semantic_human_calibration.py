from __future__ import annotations

from hashlib import sha256
import json

import pytest

from academy_tractian.semantic_human_calibration import (
    SemanticAnnotationSource,
    SemanticHumanAdjudication,
    SemanticReviewerLabel,
    build_semantic_reviewer_packet,
    resolve_human_semantic_labels,
)


def _split_payload() -> dict:
    return {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {
                "groups": [
                    {"group_id": "asset-dev-a", "scenarios": ["CEN-DEV-A"]},
                    {"group_id": "asset-dev-b", "scenarios": ["CEN-DEV-B"]},
                ]
            },
            "VALIDATION": {
                "groups": [
                    {"group_id": "asset-val-a", "scenarios": ["CEN-VAL-A"]},
                    {"group_id": "asset-val-b", "scenarios": ["CEN-VAL-B"]},
                ]
            },
            "LOCKED_TEST": {
                "groups": [
                    {"group_id": "asset-lock-a", "scenarios": ["CEN-LOCK-A"]},
                    {"group_id": "asset-lock-b", "scenarios": ["CEN-LOCK-B"]},
                ]
            },
        },
    }


def _source(scenario: str, *, decision: str = "ORIENT", message: str | None = None):
    return SemanticAnnotationSource(
        scenario_id=scenario,
        terminal_decision=decision,
        response_mode="complete" if decision != "ESCALATE_HUMAN" else "partial",
        terminal_message=message or f"Safe operational conclusion for {scenario}.",
        safe_evidence_context=(
            "Asset evidence was available and the measured state is represented without private fields.",
        ),
    )


def _reviewer_ref(seed: str) -> str:
    return sha256(seed.encode("utf-8")).hexdigest()


def _pilot_packet():
    return build_semantic_reviewer_packet(
        sources=[_source("CEN-DEV-A"), _source("CEN-DEV-B", decision="ESCALATE_HUMAN")],
        frozen_split_payload=_split_payload(),
        purpose="PILOT",
        deterministic_shuffle_seed=17,
        minimum_distinct_groups=2,
    )


def test_packet_is_deterministic_blind_and_escalation_aware() -> None:
    first_packet, first_manifest = _pilot_packet()
    second_packet, second_manifest = _pilot_packet()

    assert first_packet == second_packet
    assert first_manifest == second_manifest
    assert first_packet.source_count == 2
    assert first_packet.task_count == 7  # 3 normal dimensions + 4 escalation dimensions
    assert set(first_manifest.group_ids) == {"asset-dev-a", "asset-dev-b"}
    assert first_manifest.source_split == "DEV"

    reviewer_json = json.dumps(first_packet.model_dump(mode="json"), sort_keys=True).lower()
    assert "group_id" not in reviewer_json
    assert "source_split" not in reviewer_json
    assert "locked_test" not in reviewer_json
    assert "gold_answer" not in reviewer_json
    assert "private_truth" not in reviewer_json
    assert "chain_of_thought" not in reviewer_json

    dev_a_dimensions = {
        task.dimension for task in first_packet.tasks if task.scenario_id == "CEN-DEV-A"
    }
    dev_b_dimensions = {
        task.dimension for task in first_packet.tasks if task.scenario_id == "CEN-DEV-B"
    }
    assert dev_a_dimensions == {
        "groundedness",
        "operational_usefulness",
        "customer_safe_clarity",
    }
    assert dev_b_dimensions == dev_a_dimensions | {"escalation_quality"}


def test_pilot_and_holdout_are_bound_to_frozen_group_splits() -> None:
    with pytest.raises(ValueError, match="PILOT requires DEV"):
        build_semantic_reviewer_packet(
            sources=[_source("CEN-VAL-A"), _source("CEN-VAL-B")],
            frozen_split_payload=_split_payload(),
            purpose="PILOT",
        )

    packet, manifest = build_semantic_reviewer_packet(
        sources=[_source("CEN-VAL-A"), _source("CEN-VAL-B")],
        frozen_split_payload=_split_payload(),
        purpose="HELD_OUT_CALIBRATION",
    )
    assert packet.purpose == "HELD_OUT_CALIBRATION"
    assert manifest.source_split == "VALIDATION"


def test_locked_test_is_rejected_even_if_caller_attempts_to_use_it() -> None:
    with pytest.raises(ValueError, match="locked-test semantic material is forbidden"):
        build_semantic_reviewer_packet(
            sources=[_source("CEN-LOCK-A"), _source("CEN-LOCK-B")],
            frozen_split_payload=_split_payload(),
            purpose="HELD_OUT_CALIBRATION",
        )


def test_packet_requires_multiple_independent_story_groups() -> None:
    with pytest.raises(ValueError, match="at least 2 distinct groups"):
        build_semantic_reviewer_packet(
            sources=[_source("CEN-DEV-A")],
            frozen_split_payload=_split_payload(),
            purpose="PILOT",
        )


def test_source_rejects_obvious_private_or_evaluator_material() -> None:
    with pytest.raises(ValueError, match="forbidden evaluator/runtime material"):
        _source("CEN-DEV-A", message="Use Authorization: Bearer secret")


def _label(packet, task_id: str, slot: str, score: int, reviewer: str):
    return SemanticReviewerLabel(
        packet_id=packet.packet_id,
        task_id=task_id,
        rubric_sha256=packet.rubric_sha256,
        reviewer_slot=slot,
        reviewer_ref_sha256=_reviewer_ref(reviewer),
        score=score,
        reason_codes=("NO_MATERIAL_DEFECT",) if score == 2 else ("MISSING_NEXT_STEP",),
    )


def test_two_agreeing_independent_passes_create_adjudicated_reference_set() -> None:
    packet, manifest = _pilot_packet()
    labels = []
    for task in packet.tasks:
        labels.extend(
            [
                _label(packet, task.task_id, "A", 2, "reviewer-a"),
                _label(packet, task.task_id, "B", 2, "reviewer-b"),
            ]
        )

    report = resolve_human_semantic_labels(
        packet=packet,
        manifest=manifest,
        labels=labels,
    )

    assert report.calibration_ready is True
    assert report.resolved_count == packet.task_count
    assert report.agreed_count == packet.task_count
    assert report.adjudicated_count == 0
    assert report.unresolved_task_ids == ()
    assert all(reference.resolution == "AGREED" for reference in report.human_references)
    assert all(reference.annotator_count == 2 for reference in report.human_references)
    populated = [metric for metric in report.inter_rater if metric.paired_tasks]
    assert populated
    assert all(metric.exact_agreement == 1.0 for metric in populated)


def test_disagreement_is_unresolved_until_distinct_third_party_adjudicates() -> None:
    packet, manifest = _pilot_packet()
    task = packet.tasks[0]
    labels = [
        _label(packet, task.task_id, "A", 2, "reviewer-a"),
        _label(packet, task.task_id, "B", 1, "reviewer-b"),
    ]

    unresolved = resolve_human_semantic_labels(
        packet=packet,
        manifest=manifest,
        labels=labels,
    )
    assert unresolved.calibration_ready is False
    assert task.task_id in unresolved.unresolved_task_ids
    assert all(reference.output_sha256 != task.output_sha256 or reference.dimension != task.dimension for reference in unresolved.human_references)

    adjudication = SemanticHumanAdjudication(
        packet_id=packet.packet_id,
        task_id=task.task_id,
        rubric_sha256=packet.rubric_sha256,
        adjudicator_ref_sha256=_reviewer_ref("adjudicator-c"),
        score=1,
    )
    still_incomplete = resolve_human_semantic_labels(
        packet=packet,
        manifest=manifest,
        labels=labels,
        adjudications=[adjudication],
    )
    resolved_task = next(
        reference
        for reference in still_incomplete.human_references
        if reference.output_sha256 == task.output_sha256 and reference.dimension == task.dimension
    )
    assert resolved_task.resolution == "ADJUDICATED"
    assert resolved_task.annotator_count == 3
    assert resolved_task.score == 1
    # The other packet tasks have not been labelled, so the full packet remains fail-closed.
    assert still_incomplete.calibration_ready is False


def test_same_reviewer_cannot_fill_both_independent_slots() -> None:
    packet, manifest = _pilot_packet()
    task = packet.tasks[0]
    labels = [
        _label(packet, task.task_id, "A", 2, "same-reviewer"),
        _label(packet, task.task_id, "B", 2, "same-reviewer"),
    ]

    with pytest.raises(ValueError, match="independent reviewer slots share the same reviewer reference"):
        resolve_human_semantic_labels(packet=packet, manifest=manifest, labels=labels)


def test_adjudicator_must_be_distinct_from_both_reviewers() -> None:
    packet, manifest = _pilot_packet()
    task = packet.tasks[0]
    labels = [
        _label(packet, task.task_id, "A", 2, "reviewer-a"),
        _label(packet, task.task_id, "B", 0, "reviewer-b"),
    ]
    adjudication = SemanticHumanAdjudication(
        packet_id=packet.packet_id,
        task_id=task.task_id,
        rubric_sha256=packet.rubric_sha256,
        adjudicator_ref_sha256=_reviewer_ref("reviewer-a"),
        score=1,
    )

    with pytest.raises(ValueError, match="adjudicator must be distinct"):
        resolve_human_semantic_labels(
            packet=packet,
            manifest=manifest,
            labels=labels,
            adjudications=[adjudication],
        )
