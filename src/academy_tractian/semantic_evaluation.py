from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator


SemanticDimension = Literal[
    "groundedness",
    "operational_usefulness",
    "customer_safe_clarity",
    "escalation_quality",
]
SemanticScore = Literal[0, 1, 2]
CalibrationState = Literal[
    "NOT_CALIBRATED",
    "DESCRIPTIVE_ONLY",
    "CALIBRATED_GATE",
]
HumanResolution = Literal["AGREED", "ADJUDICATED", "UNRESOLVED"]
CalibrationKey = tuple[str, str, str, str, SemanticDimension]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SemanticRubricCriterion(_FrozenModel):
    dimension: SemanticDimension
    description: str = Field(min_length=1)
    score_0: str = Field(min_length=1)
    score_1: str = Field(min_length=1)
    score_2: str = Field(min_length=1)
    applicability: Literal["ALL_TERMINAL_OUTPUTS", "ESCALATION_ONLY"]


class SemanticRubric(_FrozenModel):
    schema_version: Literal["semantic-rubric-v1"] = "semantic-rubric-v1"
    rubric_id: Literal["tractian-terminal-quality-v1"] = "tractian-terminal-quality-v1"
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    criteria: tuple[SemanticRubricCriterion, ...]


class HumanSemanticReference(_FrozenModel):
    """Adjudicated human reference without raw response text or annotator identity.

    `context_sha256` binds the score to the exact sanitized evidence/context material shown to
    the reviewers. Groundedness and operational usefulness cannot be safely transferred across
    a different evidence state just because the terminal message happens to be identical.
    """

    scenario_id: str = Field(min_length=1)
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_mode: str = Field(min_length=1)
    dimension: SemanticDimension
    score: SemanticScore
    resolution: HumanResolution
    annotator_count: int = Field(ge=1)


class JudgeSemanticObservation(_FrozenModel):
    """Structured judge result only; free-form reasoning and raw prompts are intentionally absent.

    The judge observation must carry the same sanitized-context hash as the human reference so
    calibration cannot pair scores produced from different evidence states.
    """

    scenario_id: str = Field(min_length=1)
    output_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_mode: str = Field(min_length=1)
    dimension: SemanticDimension
    judge_id: str = Field(min_length=1)
    rubric_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    valid: bool
    score: SemanticScore | None = None
    error_code: str | None = None

    @model_validator(mode="after")
    def validate_result(self) -> "JudgeSemanticObservation":
        if self.valid and self.score is None:
            raise ValueError("valid judge observation requires score")
        if not self.valid and self.score is not None:
            raise ValueError("invalid judge observation must not carry score")
        if self.valid and self.error_code is not None:
            raise ValueError("valid judge observation must not carry error_code")
        if not self.valid and not self.error_code:
            raise ValueError("invalid judge observation requires error_code")
        return self


class SemanticCalibrationAcceptancePolicy(_FrozenModel):
    """Explicit preregistered thresholds. There are intentionally no threshold defaults."""

    schema_version: Literal["semantic-calibration-policy-v1"] = "semantic-calibration-policy-v1"
    policy_id: str = Field(min_length=1)
    minimum_pairs_per_dimension: int = Field(ge=1)
    minimum_exact_agreement: float = Field(ge=0.0, le=1.0)
    minimum_quadratic_weighted_kappa: float = Field(ge=-1.0, le=1.0)
    maximum_mean_absolute_error: float = Field(ge=0.0, le=2.0)
    maximum_false_pass_rate: float = Field(ge=0.0, le=1.0)
    maximum_invalid_rate: float = Field(ge=0.0, le=1.0)


class SemanticDimensionCalibration(_FrozenModel):
    dimension: SemanticDimension
    expected_observations: int
    valid_pairs: int
    invalid_judge_observations: int
    exact_agreement: float | None
    adjacent_agreement: float | None
    mean_absolute_error: float | None
    quadratic_weighted_kappa: float | None
    false_pass_rate: float | None
    false_fail_rate: float | None
    invalid_rate: float
    confusion_matrix: dict[str, dict[str, int]]


class SemanticCalibrationReport(_FrozenModel):
    schema_version: Literal["semantic-calibration-report-v1"] = "semantic-calibration-report-v1"
    state: CalibrationState
    gate_authorized: bool
    rubric_id: str
    rubric_sha256: str
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    judge_ids: tuple[str, ...]
    expected_keys: int
    valid_pairs: int
    unresolved_human_keys: tuple[str, ...]
    unmatched_human_keys: tuple[str, ...]
    unmatched_judge_keys: tuple[str, ...]
    dimension_metrics: tuple[SemanticDimensionCalibration, ...]
    acceptance_policy_id: str | None
    gate_failures: tuple[str, ...]


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _build_rubric() -> SemanticRubric:
    criteria = (
        SemanticRubricCriterion(
            dimension="groundedness",
            description=(
                "Whether material claims in the terminal output are supported by the safe evidence "
                "available to the run, without invented certainty or unsupported operational facts."
            ),
            score_0="Material unsupported or contradicted claims; certainty exceeds available evidence.",
            score_1="Mostly grounded but contains a material omission, overclaim, or weakly supported claim.",
            score_2="Material claims are supported, uncertainty is represented, and no unsupported fact is introduced.",
            applicability="ALL_TERMINAL_OUTPUTS",
        ),
        SemanticRubricCriterion(
            dimension="operational_usefulness",
            description=(
                "Whether the terminal output reaches the correct operational conclusion for the evidence "
                "state and gives the user an actionable next step when one is warranted."
            ),
            score_0="Operational conclusion is wrong, unsafe, or unusable for the observed evidence state.",
            score_1="Direction is defensible but incomplete, weakly prioritized, or missing a material next step.",
            score_2="Conclusion is operationally correct, appropriately prioritized, and actionable for the evidence state.",
            applicability="ALL_TERMINAL_OUTPUTS",
        ),
        SemanticRubricCriterion(
            dimension="customer_safe_clarity",
            description=(
                "Whether the user-facing output is clear, concise enough for operations, and avoids "
                "unnecessary internal implementation detail or unsafe disclosure."
            ),
            score_0="Confusing, materially misleading, or exposes unnecessary sensitive/internal detail.",
            score_1="Understandable but materially verbose, ambiguous, or includes avoidable internal detail.",
            score_2="Clear, direct, customer-safe, and contains only operationally useful detail.",
            applicability="ALL_TERMINAL_OUTPUTS",
        ),
        SemanticRubricCriterion(
            dimension="escalation_quality",
            description=(
                "For escalation outputs, whether the handoff states the evidence, uncertainty/conflict, "
                "reason for escalation, and the human decision or follow-up required."
            ),
            score_0="Escalation is unjustified or omits material evidence/reason/required human decision.",
            score_1="Escalation is defensible but handoff context or requested human action is incomplete.",
            score_2="Escalation is justified and gives a concise evidence-backed handoff with clear human next action.",
            applicability="ESCALATION_ONLY",
        ),
    )
    payload = {
        "schema_version": "semantic-rubric-v1",
        "rubric_id": "tractian-terminal-quality-v1",
        "criteria": [criterion.model_dump(mode="json") for criterion in criteria],
    }
    return SemanticRubric(
        rubric_sha256=_canonical_sha256(payload),
        criteria=criteria,
    )


SEMANTIC_RUBRIC_V1 = _build_rubric()


def semantic_rubric_v1() -> SemanticRubric:
    return SEMANTIC_RUBRIC_V1


def _key(item: HumanSemanticReference | JudgeSemanticObservation) -> CalibrationKey:
    return (
        item.scenario_id,
        item.output_sha256,
        item.context_sha256,
        item.response_mode,
        item.dimension,
    )


def _key_text(key: CalibrationKey) -> str:
    scenario_id, output_sha256, context_sha256, response_mode, dimension = key
    return (
        f"{scenario_id}|{output_sha256}|{context_sha256}|{response_mode}|{dimension}"
    )


def _quadratic_weighted_kappa(pairs: Sequence[tuple[int, int]]) -> float | None:
    if not pairs:
        return None
    categories = (0, 1, 2)
    observed = [[0.0 for _ in categories] for _ in categories]
    human_counts = [0.0, 0.0, 0.0]
    judge_counts = [0.0, 0.0, 0.0]
    for human, judge in pairs:
        observed[human][judge] += 1.0
        human_counts[human] += 1.0
        judge_counts[judge] += 1.0
    total = float(len(pairs))
    denominator = float((len(categories) - 1) ** 2)
    observed_weighted = 0.0
    expected_weighted = 0.0
    for human in categories:
        for judge in categories:
            weight = ((human - judge) ** 2) / denominator
            observed_weighted += weight * (observed[human][judge] / total)
            expected = (human_counts[human] * judge_counts[judge]) / (total * total)
            expected_weighted += weight * expected
    if expected_weighted == 0.0:
        return 1.0 if observed_weighted == 0.0 else 0.0
    return 1.0 - (observed_weighted / expected_weighted)


def _dimension_metrics(
    dimension: SemanticDimension,
    human_by_key: dict[CalibrationKey, HumanSemanticReference],
    judge_by_key: dict[CalibrationKey, JudgeSemanticObservation],
) -> SemanticDimensionCalibration:
    keys = sorted(key for key in human_by_key if key[4] == dimension)
    pairs: list[tuple[int, int]] = []
    invalid = 0
    matrix = {str(h): {str(j): 0 for j in range(3)} for h in range(3)}
    false_pass_numerator = 0
    false_pass_denominator = 0
    false_fail_numerator = 0
    false_fail_denominator = 0

    for key in keys:
        judge = judge_by_key.get(key)
        if judge is None or not judge.valid or judge.score is None:
            invalid += 1
            continue
        human_score = int(human_by_key[key].score)
        judge_score = int(judge.score)
        pairs.append((human_score, judge_score))
        matrix[str(human_score)][str(judge_score)] += 1
        if human_score < 2:
            false_pass_denominator += 1
            if judge_score == 2:
                false_pass_numerator += 1
        if human_score == 2:
            false_fail_denominator += 1
            if judge_score < 2:
                false_fail_numerator += 1

    valid_pairs = len(pairs)
    expected = len(keys)
    exact = None if not pairs else sum(h == j for h, j in pairs) / valid_pairs
    adjacent = None if not pairs else sum(abs(h - j) <= 1 for h, j in pairs) / valid_pairs
    mae = None if not pairs else sum(abs(h - j) for h, j in pairs) / valid_pairs
    false_pass = (
        None
        if false_pass_denominator == 0
        else false_pass_numerator / false_pass_denominator
    )
    false_fail = (
        None
        if false_fail_denominator == 0
        else false_fail_numerator / false_fail_denominator
    )
    return SemanticDimensionCalibration(
        dimension=dimension,
        expected_observations=expected,
        valid_pairs=valid_pairs,
        invalid_judge_observations=invalid,
        exact_agreement=exact,
        adjacent_agreement=adjacent,
        mean_absolute_error=mae,
        quadratic_weighted_kappa=_quadratic_weighted_kappa(pairs),
        false_pass_rate=false_pass,
        false_fail_rate=false_fail,
        invalid_rate=(0.0 if expected == 0 else invalid / expected),
        confusion_matrix=matrix,
    )


def calibrate_semantic_judge(
    *,
    human_references: Sequence[HumanSemanticReference],
    judge_observations: Sequence[JudgeSemanticObservation],
    acceptance_policy: SemanticCalibrationAcceptancePolicy | None = None,
    rubric: SemanticRubric | None = None,
) -> SemanticCalibrationReport:
    rubric = rubric or SEMANTIC_RUBRIC_V1

    human_by_key: dict[CalibrationKey, HumanSemanticReference] = {}
    duplicate_human: list[str] = []
    for item in human_references:
        key = _key(item)
        if key in human_by_key:
            duplicate_human.append(_key_text(key))
        human_by_key[key] = item

    judge_by_key: dict[CalibrationKey, JudgeSemanticObservation] = {}
    duplicate_judge: list[str] = []
    for item in judge_observations:
        key = _key(item)
        if key in judge_by_key:
            duplicate_judge.append(_key_text(key))
        judge_by_key[key] = item

    human_keys = set(human_by_key)
    judge_keys = set(judge_by_key)
    unmatched_human = tuple(sorted(_key_text(key) for key in human_keys - judge_keys))
    unmatched_judge = tuple(sorted(_key_text(key) for key in judge_keys - human_keys))
    unresolved = tuple(
        sorted(
            _key_text(key)
            for key, item in human_by_key.items()
            if item.resolution == "UNRESOLVED"
        )
    )
    rubric_mismatch = sorted(
        _key_text(key)
        for key, item in judge_by_key.items()
        if item.rubric_sha256 != rubric.rubric_sha256
    )

    dimensions = tuple(criterion.dimension for criterion in rubric.criteria)
    metrics = tuple(
        _dimension_metrics(dimension, human_by_key, judge_by_key)
        for dimension in dimensions
    )

    dataset_payload = {
        "rubric_sha256": rubric.rubric_sha256,
        "human": [
            item.model_dump(mode="json")
            for item in sorted(human_references, key=_key)
        ],
        "judge": [
            item.model_dump(mode="json")
            for item in sorted(judge_observations, key=_key)
        ],
    }
    dataset_sha = _canonical_sha256(dataset_payload)

    structural_failures: list[str] = []
    if not human_references or not judge_observations:
        structural_failures.append("EMPTY_CALIBRATION_SET")
    if duplicate_human:
        structural_failures.append("DUPLICATE_HUMAN_KEYS")
    if duplicate_judge:
        structural_failures.append("DUPLICATE_JUDGE_KEYS")
    if unmatched_human or unmatched_judge:
        structural_failures.append("CALIBRATION_KEY_SET_MISMATCH")
    if unresolved:
        structural_failures.append("UNRESOLVED_HUMAN_LABELS")
    if rubric_mismatch:
        structural_failures.append("JUDGE_RUBRIC_HASH_MISMATCH")

    gate_failures = list(structural_failures)
    structurally_calibratable = not structural_failures

    if structurally_calibratable and acceptance_policy is not None:
        for metric in metrics:
            prefix = metric.dimension.upper()
            if metric.expected_observations < acceptance_policy.minimum_pairs_per_dimension:
                gate_failures.append(f"{prefix}_INSUFFICIENT_PAIRS")
            if (
                metric.exact_agreement is None
                or metric.exact_agreement < acceptance_policy.minimum_exact_agreement
            ):
                gate_failures.append(f"{prefix}_EXACT_AGREEMENT_BELOW_MINIMUM")
            if (
                metric.quadratic_weighted_kappa is None
                or metric.quadratic_weighted_kappa
                < acceptance_policy.minimum_quadratic_weighted_kappa
            ):
                gate_failures.append(f"{prefix}_KAPPA_BELOW_MINIMUM")
            if (
                metric.mean_absolute_error is None
                or metric.mean_absolute_error > acceptance_policy.maximum_mean_absolute_error
            ):
                gate_failures.append(f"{prefix}_MAE_ABOVE_MAXIMUM")
            if (
                metric.false_pass_rate is not None
                and metric.false_pass_rate > acceptance_policy.maximum_false_pass_rate
            ):
                gate_failures.append(f"{prefix}_FALSE_PASS_RATE_ABOVE_MAXIMUM")
            if metric.invalid_rate > acceptance_policy.maximum_invalid_rate:
                gate_failures.append(f"{prefix}_INVALID_RATE_ABOVE_MAXIMUM")

    if not structurally_calibratable:
        state: CalibrationState = "NOT_CALIBRATED"
        gate_authorized = False
    elif acceptance_policy is None:
        state = "DESCRIPTIVE_ONLY"
        gate_authorized = False
    elif gate_failures:
        state = "DESCRIPTIVE_ONLY"
        gate_authorized = False
    else:
        state = "CALIBRATED_GATE"
        gate_authorized = True

    return SemanticCalibrationReport(
        state=state,
        gate_authorized=gate_authorized,
        rubric_id=rubric.rubric_id,
        rubric_sha256=rubric.rubric_sha256,
        dataset_sha256=dataset_sha,
        judge_ids=tuple(sorted({item.judge_id for item in judge_observations})),
        expected_keys=len(human_by_key),
        valid_pairs=sum(metric.valid_pairs for metric in metrics),
        unresolved_human_keys=unresolved,
        unmatched_human_keys=unmatched_human,
        unmatched_judge_keys=unmatched_judge,
        dimension_metrics=metrics,
        acceptance_policy_id=(
            None if acceptance_policy is None else acceptance_policy.policy_id
        ),
        gate_failures=tuple(sorted(set(gate_failures))),
    )
