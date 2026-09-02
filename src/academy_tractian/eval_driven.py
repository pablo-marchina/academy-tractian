from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import math
import random
from typing import Any, Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


MetricDirection = Literal["higher_is_better", "lower_is_better"]
Decision = Literal["PROMOTE", "REJECT", "INCONCLUSIVE"]


class EvalMetricRule(_FrozenModel):
    name: str = Field(min_length=1)
    direction: MetricDirection
    required: bool = True
    minimum_candidate: float | None = None
    maximum_candidate: float | None = None
    max_allowed_regression: float = Field(default=0.0, ge=0.0)
    min_material_improvement: float = Field(default=0.0, ge=0.0)
    promotion_metric: bool = True
    require_confident_improvement: bool = False

    @model_validator(mode="after")
    def validate_bounds(self) -> "EvalMetricRule":
        if (
            self.minimum_candidate is not None
            and self.maximum_candidate is not None
            and self.minimum_candidate > self.maximum_candidate
        ):
            raise ValueError("minimum_candidate cannot exceed maximum_candidate")
        return self


class EvalScenarioRecord(_FrozenModel):
    group_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    response_mode: str | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    hard_gate_failures: tuple[str, ...] = ()


class EvalMetricBundle(_FrozenModel):
    schema_version: Literal["eval-metric-bundle-v1"] = "eval-metric-bundle-v1"
    config_id: str = Field(min_length=1)
    records: tuple[EvalScenarioRecord, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_records(self) -> "EvalMetricBundle":
        if not self.records:
            raise ValueError("metric bundle must contain at least one record")
        seen: set[tuple[str, str]] = set()
        for record in self.records:
            key = (record.group_id, record.case_id)
            if key in seen:
                raise ValueError(
                    f"duplicate group/case record: {record.group_id}/{record.case_id}"
                )
            seen.add(key)
        return self


class EvalMetricDelta(_FrozenModel):
    name: str
    direction: MetricDirection
    groups: int
    baseline_mean: float
    candidate_mean: float
    raw_delta: float
    directional_improvement: float
    ci_low: float
    ci_high: float
    confidently_improved: bool
    materially_improved: bool
    regression: bool
    candidate_threshold_pass: bool


class EvalSliceDelta(_FrozenModel):
    dimension: Literal["response_mode"] = "response_mode"
    value: str
    paired_groups: tuple[str, ...]
    metric_deltas: tuple[EvalMetricDelta, ...]
    issues: tuple[str, ...] = ()


class EvalDrivenDecisionReport(_FrozenModel):
    schema_version: Literal["eval-driven-decision-v1"] = "eval-driven-decision-v1"
    baseline_config_id: str
    candidate_config_id: str
    comparison_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    paired_groups: tuple[str, ...]
    metric_deltas: tuple[EvalMetricDelta, ...]
    response_mode_slices: tuple[EvalSliceDelta, ...]
    candidate_hard_gate_failures: tuple[str, ...]
    comparison_issues: tuple[str, ...]
    decision: Decision
    decision_reasons: tuple[str, ...]


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot compute mean of empty values")
    return sum(values) / len(values)


def _percentile(sorted_values: Sequence[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute percentile of empty values")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be within [0, 1]")
    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def _group_metric_means(
    records: Sequence[EvalScenarioRecord],
    metric_name: str,
) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for record in records:
        value = record.metrics.get(metric_name)
        if value is not None:
            grouped[record.group_id].append(float(value))
    return {group_id: _mean(values) for group_id, values in grouped.items()}


def _bootstrap_delta_interval(
    baseline: Sequence[float],
    candidate: Sequence[float],
    *,
    seed: int,
    samples: int,
) -> tuple[float, float]:
    if len(baseline) != len(candidate) or not baseline:
        raise ValueError("paired bootstrap requires non-empty equal-length vectors")
    rng = random.Random(seed)
    size = len(baseline)
    deltas: list[float] = []
    for _ in range(samples):
        indices = [rng.randrange(size) for _ in range(size)]
        baseline_mean = _mean([baseline[index] for index in indices])
        candidate_mean = _mean([candidate[index] for index in indices])
        deltas.append(candidate_mean - baseline_mean)
    deltas.sort()
    return _percentile(deltas, 0.025), _percentile(deltas, 0.975)


def _comparison_id(
    baseline: EvalMetricBundle,
    candidate: EvalMetricBundle,
    rules: Sequence[EvalMetricRule],
) -> str:
    payload = {
        "baseline": baseline.model_dump(mode="json"),
        "candidate": candidate.model_dump(mode="json"),
        "rules": [rule.model_dump(mode="json") for rule in rules],
    }
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _hard_gate_failures(bundle: EvalMetricBundle) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                failure
                for record in bundle.records
                for failure in record.hard_gate_failures
            }
        )
    )


def _metric_deltas(
    baseline_records: Sequence[EvalScenarioRecord],
    candidate_records: Sequence[EvalScenarioRecord],
    *,
    paired_groups: Sequence[str],
    rules: Sequence[EvalMetricRule],
    seed_base: int,
    bootstrap_samples: int,
) -> tuple[tuple[EvalMetricDelta, ...], tuple[str, ...]]:
    deltas: list[EvalMetricDelta] = []
    issues: list[str] = []

    for ordinal, rule in enumerate(rules):
        baseline_by_group = _group_metric_means(baseline_records, rule.name)
        candidate_by_group = _group_metric_means(candidate_records, rule.name)
        metric_groups = tuple(
            group_id
            for group_id in paired_groups
            if group_id in baseline_by_group and group_id in candidate_by_group
        )

        if rule.required and set(metric_groups) != set(paired_groups):
            issues.append(f"MISSING_REQUIRED_METRIC:{rule.name}")
        if not metric_groups:
            continue

        baseline_values = [baseline_by_group[group_id] for group_id in metric_groups]
        candidate_values = [candidate_by_group[group_id] for group_id in metric_groups]
        baseline_mean = _mean(baseline_values)
        candidate_mean = _mean(candidate_values)
        raw_delta = candidate_mean - baseline_mean
        ci_low, ci_high = _bootstrap_delta_interval(
            baseline_values,
            candidate_values,
            seed=seed_base + ordinal,
            samples=bootstrap_samples,
        )

        if rule.direction == "higher_is_better":
            directional_improvement = raw_delta
            confident = ci_low > 0.0
        else:
            directional_improvement = -raw_delta
            confident = ci_high < 0.0

        threshold_pass = True
        if rule.minimum_candidate is not None:
            threshold_pass = threshold_pass and candidate_mean >= rule.minimum_candidate
        if rule.maximum_candidate is not None:
            threshold_pass = threshold_pass and candidate_mean <= rule.maximum_candidate

        regression = directional_improvement < -rule.max_allowed_regression
        material = directional_improvement >= rule.min_material_improvement
        if rule.require_confident_improvement:
            material = material and confident

        deltas.append(
            EvalMetricDelta(
                name=rule.name,
                direction=rule.direction,
                groups=len(metric_groups),
                baseline_mean=baseline_mean,
                candidate_mean=candidate_mean,
                raw_delta=raw_delta,
                directional_improvement=directional_improvement,
                ci_low=ci_low,
                ci_high=ci_high,
                confidently_improved=confident,
                materially_improved=material,
                regression=regression,
                candidate_threshold_pass=threshold_pass,
            )
        )

    return tuple(deltas), tuple(sorted(set(issues)))


def _response_mode_slices(
    baseline: EvalMetricBundle,
    candidate: EvalMetricBundle,
    *,
    rules: Sequence[EvalMetricRule],
    seed_base: int,
    bootstrap_samples: int,
) -> tuple[EvalSliceDelta, ...]:
    modes = sorted(
        {
            record.response_mode
            for record in (*baseline.records, *candidate.records)
            if record.response_mode is not None
        }
    )
    slices: list[EvalSliceDelta] = []
    for offset, mode in enumerate(modes, start=1):
        baseline_records = tuple(
            record for record in baseline.records if record.response_mode == mode
        )
        candidate_records = tuple(
            record for record in candidate.records if record.response_mode == mode
        )
        baseline_groups = {record.group_id for record in baseline_records}
        candidate_groups = {record.group_id for record in candidate_records}
        paired_groups = tuple(sorted(baseline_groups & candidate_groups))
        issues: list[str] = []
        if baseline_groups != candidate_groups:
            issues.append("GROUP_SET_MISMATCH")
        if not paired_groups:
            issues.append("NO_PAIRED_GROUPS")
            deltas: tuple[EvalMetricDelta, ...] = ()
        else:
            deltas, metric_issues = _metric_deltas(
                baseline_records,
                candidate_records,
                paired_groups=paired_groups,
                rules=rules,
                seed_base=seed_base + offset * 1000,
                bootstrap_samples=bootstrap_samples,
            )
            issues.extend(metric_issues)
        slices.append(
            EvalSliceDelta(
                value=mode,
                paired_groups=paired_groups,
                metric_deltas=deltas,
                issues=tuple(sorted(set(issues))),
            )
        )
    return tuple(slices)


def compare_eval_bundles(
    baseline: EvalMetricBundle,
    candidate: EvalMetricBundle,
    *,
    rules: Sequence[EvalMetricRule],
    bootstrap_samples: int = 4000,
) -> EvalDrivenDecisionReport:
    if bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be >= 100")
    if not rules:
        raise ValueError("at least one metric rule is required")

    comparison_issues: list[str] = []
    reasons: list[str] = []

    baseline_groups = {record.group_id for record in baseline.records}
    candidate_groups = {record.group_id for record in candidate.records}
    paired_groups = tuple(sorted(baseline_groups & candidate_groups))
    if baseline_groups != candidate_groups:
        comparison_issues.append("GROUP_SET_MISMATCH")
    if not paired_groups:
        comparison_issues.append("NO_PAIRED_GROUPS")

    comparison_id = _comparison_id(baseline, candidate, rules)
    seed_base = int(comparison_id[:16], 16)

    metric_deltas, metric_issues = _metric_deltas(
        baseline.records,
        candidate.records,
        paired_groups=paired_groups,
        rules=rules,
        seed_base=seed_base,
        bootstrap_samples=bootstrap_samples,
    ) if paired_groups else ((), ())
    comparison_issues.extend(metric_issues)

    response_mode_slices = _response_mode_slices(
        baseline,
        candidate,
        rules=rules,
        seed_base=seed_base,
        bootstrap_samples=bootstrap_samples,
    )

    candidate_hard_gate_failures = _hard_gate_failures(candidate)
    rules_by_name = {rule.name: rule for rule in rules}

    slice_regressions = [
        (slice_delta.value, delta.name)
        for slice_delta in response_mode_slices
        if not slice_delta.issues
        for delta in slice_delta.metric_deltas
        if delta.regression
    ]
    slice_threshold_failures = [
        (slice_delta.value, delta.name)
        for slice_delta in response_mode_slices
        if not slice_delta.issues
        for delta in slice_delta.metric_deltas
        if not delta.candidate_threshold_pass
    ]

    if comparison_issues:
        decision: Decision = "INCONCLUSIVE"
        reasons.extend(sorted(set(comparison_issues)))
    elif candidate_hard_gate_failures:
        decision = "REJECT"
        reasons.append("CANDIDATE_HARD_GATE_FAILURE")
    else:
        threshold_failures = [
            delta.name for delta in metric_deltas if not delta.candidate_threshold_pass
        ]
        regressions = [delta.name for delta in metric_deltas if delta.regression]
        material_improvements = [
            delta.name
            for delta in metric_deltas
            if delta.materially_improved
            and rules_by_name[delta.name].promotion_metric
        ]

        if threshold_failures or slice_threshold_failures:
            decision = "REJECT"
            reasons.extend(
                f"THRESHOLD_FAILURE:{name}" for name in threshold_failures
            )
            reasons.extend(
                f"SLICE_THRESHOLD_FAILURE:{mode}:{name}"
                for mode, name in slice_threshold_failures
            )
        elif regressions or slice_regressions:
            decision = "REJECT"
            reasons.extend(f"REGRESSION:{name}" for name in regressions)
            reasons.extend(
                f"SLICE_REGRESSION:{mode}:{name}"
                for mode, name in slice_regressions
            )
        elif material_improvements:
            decision = "PROMOTE"
            reasons.extend(
                f"MATERIAL_IMPROVEMENT:{name}" for name in material_improvements
            )
        else:
            decision = "INCONCLUSIVE"
            reasons.append("NO_MATERIAL_IMPROVEMENT")

    return EvalDrivenDecisionReport(
        baseline_config_id=baseline.config_id,
        candidate_config_id=candidate.config_id,
        comparison_id=comparison_id,
        paired_groups=paired_groups,
        metric_deltas=metric_deltas,
        response_mode_slices=response_mode_slices,
        candidate_hard_gate_failures=candidate_hard_gate_failures,
        comparison_issues=tuple(sorted(set(comparison_issues))),
        decision=decision,
        decision_reasons=tuple(reasons),
    )


def default_agent_quality_rules() -> tuple[EvalMetricRule, ...]:
    """Conservative defaults for provider-free candidate-vs-baseline comparisons.

    Project-specific hard safety/integrity failures belong in `hard_gate_failures` on
    each scenario record. Promotion requires a >=2 percentage-point improvement in at
    least one quality metric while no listed overall or response-mode slice regresses.
    """

    quality_metrics = (
        "task_success_rate",
        "decision_accuracy",
        "tool_selection_accuracy",
        "argument_validity_rate",
        "evidence_support_rate",
        "failure_recovery_rate",
        "stability_rate",
    )
    return tuple(
        EvalMetricRule(
            name=name,
            direction="higher_is_better",
            min_material_improvement=0.02,
            max_allowed_regression=0.0,
            promotion_metric=True,
            require_confident_improvement=False,
        )
        for name in quality_metrics
    )
