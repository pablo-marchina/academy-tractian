from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
from typing import Any, Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .eval_driven import EvalMetricBundle, EvalScenarioRecord


EvaluationSplit = Literal["DEV", "VALIDATION"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OperationalValueObservation(_FrozenModel):
    """Evaluator-side per-ticket outcome and measured human-effort observation.

    This contract deliberately carries only outcome labels and measured durations. It does not
    carry expected/gold answer text, private trajectories, prompts, chain-of-thought, or raw
    provider material. `LOCKED_TEST` is intentionally not an accepted split in this prospective
    development/calibration contract.
    """

    schema_version: Literal["operational-value-observation-v1"] = "operational-value-observation-v1"
    scenario_id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    split: EvaluationSplit
    response_mode: str = Field(min_length=1)

    operational_conclusion_correct: bool
    evidence_correct: bool | None = None
    escalation_required: bool
    escalated: bool
    premature_action: bool = False
    unsupported_conclusion: bool = False
    auto_resolved: bool = False
    handoff_ready_to_continue: bool | None = None

    manual_baseline_seconds: float | None = Field(default=None, gt=0.0)
    assisted_human_seconds: float | None = Field(default=None, ge=0.0)
    agent_runtime_seconds: float | None = Field(default=None, ge=0.0)

    @model_validator(mode="after")
    def validate_measurement_contract(self) -> "OperationalValueObservation":
        baseline_present = self.manual_baseline_seconds is not None
        assisted_present = self.assisted_human_seconds is not None
        if baseline_present != assisted_present:
            raise ValueError(
                "manual_baseline_seconds and assisted_human_seconds must be supplied as a paired measurement"
            )
        if self.escalated and self.handoff_ready_to_continue is None:
            raise ValueError("escalated observations require handoff_ready_to_continue")
        if not self.escalated and self.handoff_ready_to_continue is not None:
            raise ValueError("non-escalated observations must not carry handoff readiness")
        if self.auto_resolved and self.escalated:
            raise ValueError("auto_resolved and escalated cannot both be true")
        if (
            self.auto_resolved
            and self.assisted_human_seconds is not None
            and self.assisted_human_seconds != 0.0
        ):
            raise ValueError(
                "auto_resolved observations must have zero assisted operational human time when effort is measured"
            )
        return self

    @property
    def useful_auto_resolution(self) -> bool:
        return (
            self.auto_resolved
            and self.operational_conclusion_correct
            and not self.premature_action
            and not self.unsupported_conclusion
        )


class OperationalValueReport(_FrozenModel):
    schema_version: Literal["operational-value-report-v1"] = "operational-value-report-v1"
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    ticket_count: int = Field(ge=1)
    source_splits: tuple[EvaluationSplit, ...]

    operational_conclusion_accuracy: float = Field(ge=0.0, le=1.0)
    evidence_correctness_sample_count: int = Field(ge=0)
    evidence_correctness_rate: float | None = Field(default=None, ge=0.0, le=1.0)

    escalation_required_count: int = Field(ge=0)
    escalated_count: int = Field(ge=0)
    escalation_correctness_rate: float = Field(ge=0.0, le=1.0)
    escalation_precision: float | None = Field(default=None, ge=0.0, le=1.0)
    escalation_recall: float | None = Field(default=None, ge=0.0, le=1.0)
    escalation_f1: float | None = Field(default=None, ge=0.0, le=1.0)

    premature_action_rate: float = Field(ge=0.0, le=1.0)
    unsupported_conclusion_rate: float = Field(ge=0.0, le=1.0)
    useful_auto_resolution_rate: float = Field(ge=0.0, le=1.0)

    escalated_handoff_sample_count: int = Field(ge=0)
    ready_to_continue_escalation_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    restart_from_zero_escalation_rate: float | None = Field(default=None, ge=0.0, le=1.0)

    paired_effort_sample_count: int = Field(ge=0)
    effort_sample_coverage_rate: float = Field(ge=0.0, le=1.0)
    manual_baseline_minutes_per_ticket: float | None = None
    human_review_minutes_per_ticket: float | None = None
    engineer_minutes_saved_per_ticket: float | None = None
    engineer_minutes_saved_total: float | None = None
    tickets_per_engineer_hour: float | None = Field(default=None, gt=0.0)

    runtime_sample_count: int = Field(ge=0)
    agent_runtime_p50_seconds: float | None = Field(default=None, ge=0.0)
    agent_runtime_p95_seconds: float | None = Field(default=None, ge=0.0)

    hard_failure_counts: dict[str, int] = Field(default_factory=dict)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot compute mean of empty values")
    return sum(values) / len(values)


def _percentile(values: Sequence[float], q: float) -> float:
    if not values:
        raise ValueError("cannot compute percentile of empty values")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be within [0, 1]")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _hard_failures(observation: OperationalValueObservation) -> tuple[str, ...]:
    failures: list[str] = []
    if observation.premature_action:
        failures.append("PREMATURE_ACTION")
    if observation.unsupported_conclusion:
        failures.append("UNSUPPORTED_OPERATIONAL_CONCLUSION")
    if observation.escalation_required and not observation.escalated:
        failures.append("MISSED_REQUIRED_ESCALATION")
    if observation.auto_resolved and not observation.operational_conclusion_correct:
        failures.append("INCORRECT_AUTO_RESOLUTION")
    return tuple(sorted(failures))


def build_operational_value_report(
    observations: Sequence[OperationalValueObservation],
) -> OperationalValueReport:
    if not observations:
        raise ValueError("at least one operational-value observation is required")

    ordered = sorted(observations, key=lambda item: (item.group_id, item.case_id, item.scenario_id))
    seen: set[tuple[str, str]] = set()
    for item in ordered:
        key = (item.group_id, item.case_id)
        if key in seen:
            raise ValueError(f"duplicate group/case observation: {item.group_id}/{item.case_id}")
        seen.add(key)

    count = len(ordered)
    conclusion_accuracy = sum(item.operational_conclusion_correct for item in ordered) / count

    evidence_values = [item.evidence_correct for item in ordered if item.evidence_correct is not None]
    evidence_rate = (
        None
        if not evidence_values
        else sum(bool(value) for value in evidence_values) / len(evidence_values)
    )

    required_count = sum(item.escalation_required for item in ordered)
    escalated_count = sum(item.escalated for item in ordered)
    true_positive = sum(item.escalation_required and item.escalated for item in ordered)
    escalation_matches = sum(item.escalation_required == item.escalated for item in ordered)
    precision = _safe_ratio(true_positive, escalated_count)
    recall = _safe_ratio(true_positive, required_count)
    if precision is None or recall is None:
        f1 = None
    elif precision + recall == 0.0:
        f1 = 0.0
    else:
        f1 = 2.0 * precision * recall / (precision + recall)

    escalations = [item for item in ordered if item.escalated]
    ready_count = sum(item.handoff_ready_to_continue is True for item in escalations)
    ready_rate = _safe_ratio(ready_count, len(escalations))
    restart_rate = None if ready_rate is None else 1.0 - ready_rate

    effort = [
        item
        for item in ordered
        if item.manual_baseline_seconds is not None and item.assisted_human_seconds is not None
    ]
    if effort:
        manual_seconds = [float(item.manual_baseline_seconds) for item in effort]
        assisted_seconds = [float(item.assisted_human_seconds) for item in effort]
        saved_seconds = [
            baseline - assisted
            for baseline, assisted in zip(manual_seconds, assisted_seconds, strict=True)
        ]
        baseline_minutes = _mean(manual_seconds) / 60.0
        assisted_minutes = _mean(assisted_seconds) / 60.0
        saved_per_ticket = _mean(saved_seconds) / 60.0
        saved_total = sum(saved_seconds) / 60.0
        total_assisted = sum(assisted_seconds)
        tickets_per_hour = (
            None if total_assisted == 0.0 else len(effort) / (total_assisted / 3600.0)
        )
    else:
        baseline_minutes = None
        assisted_minutes = None
        saved_per_ticket = None
        saved_total = None
        tickets_per_hour = None

    runtime_values = [
        float(item.agent_runtime_seconds)
        for item in ordered
        if item.agent_runtime_seconds is not None
    ]

    hard_failure_counts = Counter(
        failure
        for item in ordered
        for failure in _hard_failures(item)
    )

    dataset_sha = _canonical_sha256([item.model_dump(mode="json") for item in ordered])

    return OperationalValueReport(
        dataset_sha256=dataset_sha,
        ticket_count=count,
        source_splits=tuple(sorted({item.split for item in ordered})),
        operational_conclusion_accuracy=conclusion_accuracy,
        evidence_correctness_sample_count=len(evidence_values),
        evidence_correctness_rate=evidence_rate,
        escalation_required_count=required_count,
        escalated_count=escalated_count,
        escalation_correctness_rate=escalation_matches / count,
        escalation_precision=precision,
        escalation_recall=recall,
        escalation_f1=f1,
        premature_action_rate=sum(item.premature_action for item in ordered) / count,
        unsupported_conclusion_rate=sum(item.unsupported_conclusion for item in ordered) / count,
        useful_auto_resolution_rate=sum(item.useful_auto_resolution for item in ordered) / count,
        escalated_handoff_sample_count=len(escalations),
        ready_to_continue_escalation_rate=ready_rate,
        restart_from_zero_escalation_rate=restart_rate,
        paired_effort_sample_count=len(effort),
        effort_sample_coverage_rate=len(effort) / count,
        manual_baseline_minutes_per_ticket=baseline_minutes,
        human_review_minutes_per_ticket=assisted_minutes,
        engineer_minutes_saved_per_ticket=saved_per_ticket,
        engineer_minutes_saved_total=saved_total,
        tickets_per_engineer_hour=tickets_per_hour,
        runtime_sample_count=len(runtime_values),
        agent_runtime_p50_seconds=(
            None if not runtime_values else _percentile(runtime_values, 0.50)
        ),
        agent_runtime_p95_seconds=(
            None if not runtime_values else _percentile(runtime_values, 0.95)
        ),
        hard_failure_counts=dict(sorted(hard_failure_counts.items())),
    )


def operational_value_metric_bundle(
    *,
    config_id: str,
    observations: Sequence[OperationalValueObservation],
    metadata: dict[str, Any] | None = None,
) -> EvalMetricBundle:
    """Convert measured operational/value observations into the existing group-aware EDD format.

    No thresholds are chosen here. Promotion/regression thresholds remain a separate prospective
    `EvalMetricRule` decision so this adapter cannot fit acceptance criteria to observed results.
    """

    report = build_operational_value_report(observations)
    records: list[EvalScenarioRecord] = []

    for item in observations:
        metrics: dict[str, float] = {
            "operational_conclusion_accuracy": float(item.operational_conclusion_correct),
            "escalation_correctness": float(item.escalation_required == item.escalated),
            "premature_action_rate": float(item.premature_action),
            "unsupported_conclusion_rate": float(item.unsupported_conclusion),
            "useful_auto_resolution_rate": float(item.useful_auto_resolution),
        }
        if item.evidence_correct is not None:
            metrics["evidence_correctness"] = float(item.evidence_correct)
        if item.escalated:
            metrics["handoff_ready_rate"] = float(bool(item.handoff_ready_to_continue))
        if item.manual_baseline_seconds is not None and item.assisted_human_seconds is not None:
            metrics["engineer_minutes_saved"] = (
                item.manual_baseline_seconds - item.assisted_human_seconds
            ) / 60.0
            metrics["human_review_minutes"] = item.assisted_human_seconds / 60.0
            metrics["manual_baseline_minutes"] = item.manual_baseline_seconds / 60.0
        if item.agent_runtime_seconds is not None:
            metrics["agent_runtime_seconds"] = item.agent_runtime_seconds

        records.append(
            EvalScenarioRecord(
                group_id=item.group_id,
                case_id=item.case_id,
                response_mode=item.response_mode,
                metrics=metrics,
                hard_gate_failures=_hard_failures(item),
            )
        )

    bundle_metadata: dict[str, Any] = {
        "contract": "operational-value-v1",
        "dataset_sha256": report.dataset_sha256,
        "source_splits": list(report.source_splits),
        "ticket_count": report.ticket_count,
        "paired_effort_sample_count": report.paired_effort_sample_count,
        "effort_sample_coverage_rate": report.effort_sample_coverage_rate,
    }
    if metadata:
        bundle_metadata.update(metadata)

    return EvalMetricBundle(
        config_id=config_id,
        records=tuple(records),
        metadata=bundle_metadata,
    )
