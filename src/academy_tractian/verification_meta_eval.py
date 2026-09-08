from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class MutationOutcome(_FrozenModel):
    mutation_id: str = Field(min_length=1)
    defect_class: str = Field(min_length=1)
    defect_present: bool
    evaluator_failed: bool
    critical: bool = False


class MetaEvaluationReport(_FrozenModel):
    schema_version: Literal["evaluator-meta-eval-v1"] = "evaluator-meta-eval-v1"
    trials: int
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int
    sensitivity: float
    specificity: float
    precision: float
    false_negative_rate: float
    false_positive_rate: float
    critical_false_negatives: tuple[str, ...]
    promotable: bool


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def score_mutation_outcomes(outcomes: list[MutationOutcome] | tuple[MutationOutcome, ...], *, minimum_sensitivity: float = 0.95, minimum_specificity: float = 0.90) -> MetaEvaluationReport:
    if not 0.0 <= minimum_sensitivity <= 1.0:
        raise ValueError("minimum_sensitivity must be within [0, 1]")
    if not 0.0 <= minimum_specificity <= 1.0:
        raise ValueError("minimum_specificity must be within [0, 1]")

    tp = sum(item.defect_present and item.evaluator_failed for item in outcomes)
    tn = sum((not item.defect_present) and (not item.evaluator_failed) for item in outcomes)
    fp = sum((not item.defect_present) and item.evaluator_failed for item in outcomes)
    fn = sum(item.defect_present and (not item.evaluator_failed) for item in outcomes)
    sensitivity = _ratio(tp, tp + fn)
    specificity = _ratio(tn, tn + fp)
    precision = _ratio(tp, tp + fp)
    fnr = _ratio(fn, tp + fn)
    fpr = _ratio(fp, tn + fp)
    critical_fn = tuple(item.mutation_id for item in outcomes if item.critical and item.defect_present and not item.evaluator_failed)
    has_positive = any(item.defect_present for item in outcomes)
    has_negative = any(not item.defect_present for item in outcomes)
    promotable = bool(outcomes) and has_positive and has_negative and not critical_fn and sensitivity >= minimum_sensitivity and specificity >= minimum_specificity

    return MetaEvaluationReport(
        trials=len(outcomes), true_positive=tp, true_negative=tn, false_positive=fp,
        false_negative=fn, sensitivity=sensitivity, specificity=specificity, precision=precision,
        false_negative_rate=fnr, false_positive_rate=fpr, critical_false_negatives=critical_fn,
        promotable=promotable,
    )
