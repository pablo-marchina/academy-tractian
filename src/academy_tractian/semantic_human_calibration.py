from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import random
from typing import Any, Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .semantic_evaluation import (
    HumanSemanticReference,
    SemanticDimension,
    SemanticRubricCriterion,
    SemanticScore,
    semantic_rubric_v1,
)


AnnotationPurpose = Literal["PILOT", "HELD_OUT_CALIBRATION"]
BenchmarkSplit = Literal["DEV", "VALIDATION", "LOCKED_TEST"]
ReviewerSlot = Literal["A", "B"]

_FORBIDDEN_MATERIAL_MARKERS = (
    "authorization:",
    "bearer ",
    "api_key",
    "api-key",
    "identity_id",
    "seed_ref",
    "chain_of_thought",
    "raw_prompt",
    "raw_response",
    "gold_answer",
    "private_truth",
)


class _FrozenModel(BaseModel):
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


def _assert_public_safe_text(value: str, *, field_name: str) -> str:
    lowered = value.lower()
    hit = next((marker for marker in _FORBIDDEN_MATERIAL_MARKERS if marker in lowered), None)
    if hit is not None:
        raise ValueError(f"{field_name} contains forbidden evaluator/runtime material marker: {hit}")
    return value


class SemanticAnnotationSource(_FrozenModel):
    """Sanitized terminal material eligible for blind human semantic review.

    This is evaluator-time input, never an agent/runtime input. It intentionally contains only
    the customer-visible terminal output and an explicitly sanitized evidence/context digest.
    It carries no split, group, gold label, identity, prompt, model reasoning, or credentials;
    split/group assignment is derived from the frozen benchmark manifest instead.
    """

    scenario_id: str = Field(min_length=1)
    terminal_decision: str = Field(min_length=1)
    response_mode: str = Field(min_length=1)
    terminal_message: str = Field(min_length=1)
    safe_evidence_context: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_public_material(self) -> "SemanticAnnotationSource":
        _assert_public_safe_text(self.scenario_id, field_name="scenario_id")
        _assert_public_safe_text(self.terminal_decision, field_name="terminal_decision")
        _assert_public_safe_text(self.response_mode, field_name="response_mode")
        _assert_public_safe_text(self.terminal_message, field_name="terminal_message")
        for index, item in enumerate(self.safe_evidence_context):
            if not item.strip():
                raise ValueError("safe_evidence_context entries must be non-empty")
            _assert_public_safe_text(item, field_name=f"safe_evidence_context[{index}]")
        return self

    @property
    def output_sha256(self) -> str:
        return _canonical_sha256(
            {
                "terminal_decision": self.terminal_decision,
                "response_mode": self.response_mode,
                "terminal_message": self.terminal_message,
            }
        )

    @property
    def context_sha256(self) -> str:
        """Bind semantic labels to the exact sanitized evidence/context shown to reviewers."""

        return _canonical_sha256(
            {
                "safe_evidence_context": list(self.safe_evidence_context),
            }
        )


class SemanticReviewerTask(_FrozenModel):
    """Blind reviewer-facing task. No split/group or evaluator-private truth is present."""

    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    scenario_id: str = Field(min_length=1)
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_mode: str = Field(min_length=1)
    dimension: SemanticDimension
    terminal_decision: str = Field(min_length=1)
    terminal_message: str = Field(min_length=1)
    safe_evidence_context: tuple[str, ...]
    criterion_description: str = Field(min_length=1)
    score_0_anchor: str = Field(min_length=1)
    score_1_anchor: str = Field(min_length=1)
    score_2_anchor: str = Field(min_length=1)


class SemanticReviewerPacket(_FrozenModel):
    schema_version: Literal["semantic-reviewer-packet-v1"] = "semantic-reviewer-packet-v1"
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    purpose: AnnotationPurpose
    rubric_id: str = Field(min_length=1)
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    deterministic_shuffle_seed: int
    source_count: int = Field(ge=1)
    task_count: int = Field(ge=1)
    tasks: tuple[SemanticReviewerTask, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> "SemanticReviewerPacket":
        if self.task_count != len(self.tasks):
            raise ValueError("task_count does not match tasks")
        if len({task.task_id for task in self.tasks}) != len(self.tasks):
            raise ValueError("reviewer packet contains duplicate task ids")
        return self


class SemanticAnnotationManifestEntry(_FrozenModel):
    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    scenario_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    source_split: Literal["DEV", "VALIDATION"]
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_mode: str = Field(min_length=1)
    dimension: SemanticDimension


class SemanticAnnotationManifest(_FrozenModel):
    """Evaluator-private grouping manifest kept separate from the reviewer packet."""

    schema_version: Literal["semantic-annotation-manifest-v1"] = "semantic-annotation-manifest-v1"
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    purpose: AnnotationPurpose
    source_split: Literal["DEV", "VALIDATION"]
    frozen_split_schema_version: str = Field(min_length=1)
    frozen_split_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    group_ids: tuple[str, ...]
    entries: tuple[SemanticAnnotationManifestEntry, ...]

    @model_validator(mode="after")
    def validate_manifest(self) -> "SemanticAnnotationManifest":
        if not self.group_ids:
            raise ValueError("annotation manifest requires at least one group")
        if len(set(self.group_ids)) != len(self.group_ids):
            raise ValueError("group_ids must be unique")
        if len({entry.task_id for entry in self.entries}) != len(self.entries):
            raise ValueError("annotation manifest contains duplicate task ids")
        if any(entry.source_split != self.source_split for entry in self.entries):
            raise ValueError("annotation manifest mixes source splits")
        if set(entry.group_id for entry in self.entries) != set(self.group_ids):
            raise ValueError("group_ids do not match manifest entries")
        return self


HumanLabelReason = Literal[
    "UNSUPPORTED_CLAIM",
    "CONTRADICTED_CLAIM",
    "UNCERTAINTY_OVERSTATED",
    "WRONG_OPERATIONAL_CONCLUSION",
    "MISSING_NEXT_STEP",
    "WEAK_PRIORITIZATION",
    "AMBIGUOUS_COMMUNICATION",
    "UNNECESSARY_INTERNAL_DETAIL",
    "UNSAFE_DISCLOSURE",
    "ESCALATION_UNJUSTIFIED",
    "ESCALATION_CONTEXT_INCOMPLETE",
    "HUMAN_ACTION_UNCLEAR",
    "NO_MATERIAL_DEFECT",
]


class SemanticReviewerLabel(_FrozenModel):
    schema_version: Literal["semantic-reviewer-label-v1"] = "semantic-reviewer-label-v1"
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reviewer_slot: ReviewerSlot
    reviewer_ref_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    score: SemanticScore
    reason_codes: tuple[HumanLabelReason, ...] = ()

    @model_validator(mode="after")
    def validate_reason_codes(self) -> "SemanticReviewerLabel":
        if len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("reason_codes must be unique")
        if self.score == 2 and self.reason_codes != ("NO_MATERIAL_DEFECT",):
            raise ValueError("score 2 requires exactly NO_MATERIAL_DEFECT")
        if self.score < 2 and not self.reason_codes:
            raise ValueError("score below 2 requires at least one structured defect reason")
        if self.score < 2 and "NO_MATERIAL_DEFECT" in self.reason_codes:
            raise ValueError("NO_MATERIAL_DEFECT is incompatible with score below 2")
        return self


class SemanticHumanAdjudication(_FrozenModel):
    schema_version: Literal["semantic-human-adjudication-v1"] = "semantic-human-adjudication-v1"
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    task_id: str = Field(pattern=r"^sem_[0-9a-f]{24}$")
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    adjudicator_ref_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    score: SemanticScore


class HumanInterRaterDimension(_FrozenModel):
    dimension: SemanticDimension
    paired_tasks: int = Field(ge=0)
    exact_agreement: float | None
    adjacent_agreement: float | None
    quadratic_weighted_kappa: float | None
    disagreements: int = Field(ge=0)


class SemanticHumanResolutionReport(_FrozenModel):
    schema_version: Literal["semantic-human-resolution-v1"] = "semantic-human-resolution-v1"
    packet_id: str = Field(pattern=r"^sempkt_[0-9a-f]{24}$")
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    task_count: int = Field(ge=1)
    resolved_count: int = Field(ge=0)
    agreed_count: int = Field(ge=0)
    adjudicated_count: int = Field(ge=0)
    unresolved_task_ids: tuple[str, ...]
    calibration_ready: bool
    human_references: tuple[HumanSemanticReference, ...]
    inter_rater: tuple[HumanInterRaterDimension, ...]


class _SplitAssignment(_FrozenModel):
    split: BenchmarkSplit
    group_id: str


def _split_index(split_payload: Mapping[str, Any]) -> tuple[dict[str, _SplitAssignment], str, str]:
    schema_version = str(split_payload.get("schema_version") or "")
    if not schema_version:
        raise ValueError("split manifest missing schema_version")
    splits = split_payload.get("splits")
    if not isinstance(splits, Mapping):
        raise ValueError("split manifest missing splits object")

    index: dict[str, _SplitAssignment] = {}
    for split_name in ("DEV", "VALIDATION", "LOCKED_TEST"):
        section = splits.get(split_name)
        if not isinstance(section, Mapping):
            raise ValueError(f"split manifest missing {split_name}")
        groups = section.get("groups")
        if not isinstance(groups, list):
            raise ValueError(f"split manifest {split_name} groups must be a list")
        for group in groups:
            if not isinstance(group, Mapping):
                raise ValueError("split group must be an object")
            group_id = str(group.get("group_id") or "")
            scenarios = group.get("scenarios")
            if not group_id or not isinstance(scenarios, list):
                raise ValueError("split group missing group_id/scenarios")
            for scenario in scenarios:
                scenario_id = str(scenario)
                if scenario_id in index:
                    raise ValueError(f"scenario assigned more than once: {scenario_id}")
                index[scenario_id] = _SplitAssignment(
                    split=split_name,  # type: ignore[arg-type]
                    group_id=group_id,
                )

    split_sha = _canonical_sha256(split_payload)
    return index, schema_version, split_sha


def _criterion_for_dimension(dimension: SemanticDimension) -> SemanticRubricCriterion:
    rubric = semantic_rubric_v1()
    for criterion in rubric.criteria:
        if criterion.dimension == dimension:
            return criterion
    raise KeyError(dimension)


def _applicable_dimensions(source: SemanticAnnotationSource) -> tuple[SemanticDimension, ...]:
    base: list[SemanticDimension] = [
        "groundedness",
        "operational_usefulness",
        "customer_safe_clarity",
    ]
    if source.terminal_decision == "ESCALATE_HUMAN":
        base.append("escalation_quality")
    return tuple(base)


def _task_id(source: SemanticAnnotationSource, dimension: SemanticDimension) -> str:
    material = {
        "scenario_id": source.scenario_id,
        "output_sha256": source.output_sha256,
        "context_sha256": source.context_sha256,
        "response_mode": source.response_mode,
        "dimension": dimension,
    }
    return "sem_" + _canonical_sha256(material)[:24]


def build_semantic_reviewer_packet(
    *,
    sources: Sequence[SemanticAnnotationSource],
    frozen_split_payload: Mapping[str, Any],
    purpose: AnnotationPurpose,
    deterministic_shuffle_seed: int = 20260903,
    minimum_distinct_groups: int = 2,
) -> tuple[SemanticReviewerPacket, SemanticAnnotationManifest]:
    if not sources:
        raise ValueError("semantic annotation requires at least one source")
    if minimum_distinct_groups < 1:
        raise ValueError("minimum_distinct_groups must be >= 1")

    expected_split: Literal["DEV", "VALIDATION"] = (
        "DEV" if purpose == "PILOT" else "VALIDATION"
    )
    split_index, split_schema_version, split_sha = _split_index(frozen_split_payload)

    seen_outputs: set[tuple[str, str, str]] = set()
    source_assignments: list[tuple[SemanticAnnotationSource, _SplitAssignment]] = []
    for source in sources:
        assignment = split_index.get(source.scenario_id)
        if assignment is None:
            raise ValueError(f"scenario absent from frozen split manifest: {source.scenario_id}")
        if assignment.split == "LOCKED_TEST":
            raise ValueError(f"locked-test semantic material is forbidden before final: {source.scenario_id}")
        if assignment.split != expected_split:
            raise ValueError(
                f"{purpose} requires {expected_split} groups; {source.scenario_id} belongs to {assignment.split}"
            )
        output_identity = (source.scenario_id, source.output_sha256, source.context_sha256)
        if output_identity in seen_outputs:
            raise ValueError(
                "duplicate semantic output/context: "
                f"{source.scenario_id}|{source.output_sha256}|{source.context_sha256}"
            )
        seen_outputs.add(output_identity)
        source_assignments.append((source, assignment))

    group_ids = tuple(sorted({assignment.group_id for _, assignment in source_assignments}))
    if len(group_ids) < minimum_distinct_groups:
        raise ValueError(
            f"semantic annotation requires at least {minimum_distinct_groups} distinct groups; got {len(group_ids)}"
        )

    rubric = semantic_rubric_v1()
    task_rows: list[tuple[SemanticReviewerTask, SemanticAnnotationManifestEntry]] = []
    for source, assignment in source_assignments:
        for dimension in _applicable_dimensions(source):
            criterion = _criterion_for_dimension(dimension)
            task_id = _task_id(source, dimension)
            task = SemanticReviewerTask(
                task_id=task_id,
                scenario_id=source.scenario_id,
                output_sha256=source.output_sha256,
                context_sha256=source.context_sha256,
                response_mode=source.response_mode,
                dimension=dimension,
                terminal_decision=source.terminal_decision,
                terminal_message=source.terminal_message,
                safe_evidence_context=source.safe_evidence_context,
                criterion_description=criterion.description,
                score_0_anchor=criterion.score_0,
                score_1_anchor=criterion.score_1,
                score_2_anchor=criterion.score_2,
            )
            manifest_entry = SemanticAnnotationManifestEntry(
                task_id=task_id,
                scenario_id=source.scenario_id,
                group_id=assignment.group_id,
                source_split=expected_split,
                output_sha256=source.output_sha256,
                context_sha256=source.context_sha256,
                response_mode=source.response_mode,
                dimension=dimension,
            )
            task_rows.append((task, manifest_entry))

    packet_material = {
        "purpose": purpose,
        "rubric_sha256": rubric.rubric_sha256,
        "split_sha256": split_sha,
        "seed": deterministic_shuffle_seed,
        "tasks": sorted(row[0].task_id for row in task_rows),
    }
    packet_id = "sempkt_" + _canonical_sha256(packet_material)[:24]

    shuffled = list(task_rows)
    random.Random(deterministic_shuffle_seed).shuffle(shuffled)
    reviewer_tasks = tuple(row[0] for row in shuffled)
    manifest_entries = tuple(sorted((row[1] for row in task_rows), key=lambda item: item.task_id))

    packet = SemanticReviewerPacket(
        packet_id=packet_id,
        purpose=purpose,
        rubric_id=rubric.rubric_id,
        rubric_sha256=rubric.rubric_sha256,
        deterministic_shuffle_seed=deterministic_shuffle_seed,
        source_count=len(sources),
        task_count=len(reviewer_tasks),
        tasks=reviewer_tasks,
    )
    manifest = SemanticAnnotationManifest(
        packet_id=packet_id,
        purpose=purpose,
        source_split=expected_split,
        frozen_split_schema_version=split_schema_version,
        frozen_split_sha256=split_sha,
        group_ids=group_ids,
        entries=manifest_entries,
    )
    return packet, manifest


def _quadratic_weighted_kappa(pairs: Sequence[tuple[int, int]]) -> float | None:
    if not pairs:
        return None
    categories = (0, 1, 2)
    observed = [[0.0 for _ in categories] for _ in categories]
    left_counts = [0.0, 0.0, 0.0]
    right_counts = [0.0, 0.0, 0.0]
    for left, right in pairs:
        observed[left][right] += 1.0
        left_counts[left] += 1.0
        right_counts[right] += 1.0
    total = float(len(pairs))
    denominator = float((len(categories) - 1) ** 2)
    observed_weighted = 0.0
    expected_weighted = 0.0
    for left in categories:
        for right in categories:
            weight = ((left - right) ** 2) / denominator
            observed_weighted += weight * (observed[left][right] / total)
            expected = (left_counts[left] * right_counts[right]) / (total * total)
            expected_weighted += weight * expected
    if expected_weighted == 0.0:
        return 1.0 if observed_weighted == 0.0 else 0.0
    return 1.0 - (observed_weighted / expected_weighted)


def _inter_rater_metrics(
    *,
    task_by_id: Mapping[str, SemanticReviewerTask],
    labels_by_task: Mapping[str, Mapping[ReviewerSlot, SemanticReviewerLabel]],
) -> tuple[HumanInterRaterDimension, ...]:
    by_dimension: dict[SemanticDimension, list[tuple[int, int]]] = defaultdict(list)
    for task_id, slots in labels_by_task.items():
        left = slots.get("A")
        right = slots.get("B")
        if left is None or right is None:
            continue
        task = task_by_id[task_id]
        by_dimension[task.dimension].append((int(left.score), int(right.score)))

    metrics: list[HumanInterRaterDimension] = []
    for criterion in semantic_rubric_v1().criteria:
        pairs = by_dimension.get(criterion.dimension, [])
        count = len(pairs)
        exact = None if count == 0 else sum(left == right for left, right in pairs) / count
        adjacent = None if count == 0 else sum(abs(left - right) <= 1 for left, right in pairs) / count
        metrics.append(
            HumanInterRaterDimension(
                dimension=criterion.dimension,
                paired_tasks=count,
                exact_agreement=exact,
                adjacent_agreement=adjacent,
                quadratic_weighted_kappa=_quadratic_weighted_kappa(pairs),
                disagreements=sum(left != right for left, right in pairs),
            )
        )
    return tuple(metrics)


def resolve_human_semantic_labels(
    *,
    packet: SemanticReviewerPacket,
    manifest: SemanticAnnotationManifest,
    labels: Sequence[SemanticReviewerLabel],
    adjudications: Sequence[SemanticHumanAdjudication] = (),
) -> SemanticHumanResolutionReport:
    if packet.packet_id != manifest.packet_id:
        raise ValueError("reviewer packet and annotation manifest packet ids differ")
    if packet.purpose != manifest.purpose:
        raise ValueError("reviewer packet and annotation manifest purposes differ")
    if packet.rubric_sha256 != semantic_rubric_v1().rubric_sha256:
        raise ValueError("reviewer packet rubric hash is not the frozen rubric")

    task_by_id = {task.task_id: task for task in packet.tasks}
    manifest_by_task = {entry.task_id: entry for entry in manifest.entries}
    if set(task_by_id) != set(manifest_by_task):
        raise ValueError("reviewer packet and annotation manifest task sets differ")
    for task_id, task in task_by_id.items():
        entry = manifest_by_task[task_id]
        if (
            task.scenario_id != entry.scenario_id
            or task.output_sha256 != entry.output_sha256
            or task.context_sha256 != entry.context_sha256
            or task.response_mode != entry.response_mode
            or task.dimension != entry.dimension
        ):
            raise ValueError(f"reviewer packet and annotation manifest task binding differs: {task_id}")

    labels_by_task: dict[str, dict[ReviewerSlot, SemanticReviewerLabel]] = defaultdict(dict)
    for label in labels:
        if label.packet_id != packet.packet_id:
            raise ValueError("human label belongs to a different packet")
        if label.rubric_sha256 != packet.rubric_sha256:
            raise ValueError("human label rubric hash mismatch")
        if label.task_id not in task_by_id:
            raise ValueError(f"human label references unknown task: {label.task_id}")
        if label.reviewer_slot in labels_by_task[label.task_id]:
            raise ValueError(f"duplicate reviewer slot for task: {label.task_id}|{label.reviewer_slot}")
        labels_by_task[label.task_id][label.reviewer_slot] = label

    adjudication_by_task: dict[str, SemanticHumanAdjudication] = {}
    for adjudication in adjudications:
        if adjudication.packet_id != packet.packet_id:
            raise ValueError("adjudication belongs to a different packet")
        if adjudication.rubric_sha256 != packet.rubric_sha256:
            raise ValueError("adjudication rubric hash mismatch")
        if adjudication.task_id not in task_by_id:
            raise ValueError(f"adjudication references unknown task: {adjudication.task_id}")
        if adjudication.task_id in adjudication_by_task:
            raise ValueError(f"duplicate adjudication for task: {adjudication.task_id}")
        adjudication_by_task[adjudication.task_id] = adjudication

    for task_id, adjudication in adjudication_by_task.items():
        slots = labels_by_task.get(task_id, {})
        label_a = slots.get("A")
        label_b = slots.get("B")
        if label_a is None or label_b is None:
            raise ValueError(f"adjudication requires both independent reviewer labels: {task_id}")
        if label_a.score == label_b.score:
            raise ValueError(f"adjudication is invalid when reviewers already agree: {task_id}")
        if adjudication.adjudicator_ref_sha256 in {
            label_a.reviewer_ref_sha256,
            label_b.reviewer_ref_sha256,
        }:
            raise ValueError(f"adjudicator must be distinct from both reviewers: {task_id}")

    references: list[HumanSemanticReference] = []
    unresolved: list[str] = []
    agreed_count = 0
    adjudicated_count = 0

    for task_id in sorted(task_by_id):
        task = task_by_id[task_id]
        slots = labels_by_task.get(task_id, {})
        label_a = slots.get("A")
        label_b = slots.get("B")
        if label_a is None or label_b is None:
            unresolved.append(task_id)
            continue
        if label_a.reviewer_ref_sha256 == label_b.reviewer_ref_sha256:
            raise ValueError(f"independent reviewer slots share the same reviewer reference: {task_id}")

        if label_a.score == label_b.score:
            score = label_a.score
            resolution = "AGREED"
            annotator_count = 2
            agreed_count += 1
        else:
            adjudication = adjudication_by_task.get(task_id)
            if adjudication is None:
                unresolved.append(task_id)
                continue
            score = adjudication.score
            resolution = "ADJUDICATED"
            annotator_count = 3
            adjudicated_count += 1

        references.append(
            HumanSemanticReference(
                scenario_id=task.scenario_id,
                output_sha256=task.output_sha256,
                context_sha256=task.context_sha256,
                response_mode=task.response_mode,
                dimension=task.dimension,
                score=score,
                resolution=resolution,
                annotator_count=annotator_count,
            )
        )

    unresolved_tuple = tuple(sorted(unresolved))
    references_tuple = tuple(
        sorted(
            references,
            key=lambda item: (
                item.scenario_id,
                item.output_sha256,
                item.context_sha256,
                item.response_mode,
                item.dimension,
            ),
        )
    )
    return SemanticHumanResolutionReport(
        packet_id=packet.packet_id,
        rubric_sha256=packet.rubric_sha256,
        task_count=len(task_by_id),
        resolved_count=len(references_tuple),
        agreed_count=agreed_count,
        adjudicated_count=adjudicated_count,
        unresolved_task_ids=unresolved_tuple,
        calibration_ready=(not unresolved_tuple and len(references_tuple) == len(task_by_id)),
        human_references=references_tuple,
        inter_rater=_inter_rater_metrics(
            task_by_id=task_by_id,
            labels_by_task=labels_by_task,
        ),
    )
