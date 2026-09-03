from __future__ import annotations

from academy_tractian.adaptive_policy import adaptive_soft_budget_eval_rules
from academy_tractian.eval_driven import (
    EvalMetricBundle,
    EvalScenarioRecord,
    compare_eval_bundles,
)


def _bundle(
    config_id: str,
    *,
    tool_calls: float,
    nonprogress_calls: float,
    task_success: float = 1.0,
    decision_accuracy: float = 1.0,
) -> EvalMetricBundle:
    return EvalMetricBundle(
        config_id=config_id,
        records=tuple(
            EvalScenarioRecord(
                group_id=group_id,
                case_id=f"case-{index}",
                response_mode="unavailable",
                metrics={
                    "task_success_rate": task_success,
                    "decision_accuracy": decision_accuracy,
                    "tool_calls_per_run": tool_calls,
                    "nonprogress_tool_calls": nonprogress_calls,
                },
            )
            for index, group_id in enumerate(("asset-dev-a", "asset-dev-b"), start=1)
        ),
    )


def test_equal_quality_and_material_tool_reduction_promotes_candidate() -> None:
    baseline = _bundle(
        "prod-runtime-v1-fixed-budget",
        tool_calls=3.0,
        nonprogress_calls=3.0,
    )
    candidate = _bundle(
        "repeated-nonprogress-soft-stop-v1",
        tool_calls=2.0,
        nonprogress_calls=2.0,
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=adaptive_soft_budget_eval_rules(),
        bootstrap_samples=200,
    )

    assert report.decision == "PROMOTE"
    assert "MATERIAL_IMPROVEMENT:tool_calls_per_run" in report.decision_reasons
    assert report.candidate_hard_gate_failures == ()


def test_quality_regression_rejects_even_when_tool_count_improves() -> None:
    baseline = _bundle(
        "prod-runtime-v1-fixed-budget",
        tool_calls=3.0,
        nonprogress_calls=3.0,
    )
    candidate = _bundle(
        "repeated-nonprogress-soft-stop-v1",
        tool_calls=2.0,
        nonprogress_calls=2.0,
        task_success=0.5,
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=adaptive_soft_budget_eval_rules(),
        bootstrap_samples=200,
    )

    assert report.decision == "REJECT"
    assert "REGRESSION:task_success_rate" in report.decision_reasons


def test_hard_gate_failure_rejects_independent_of_efficiency_gain() -> None:
    baseline = _bundle(
        "prod-runtime-v1-fixed-budget",
        tool_calls=3.0,
        nonprogress_calls=3.0,
    )
    candidate = EvalMetricBundle(
        config_id="repeated-nonprogress-soft-stop-v1",
        records=(
            EvalScenarioRecord(
                group_id="asset-dev-a",
                case_id="case-1",
                response_mode="unavailable",
                metrics={
                    "task_success_rate": 1.0,
                    "decision_accuracy": 1.0,
                    "tool_calls_per_run": 1.0,
                    "nonprogress_tool_calls": 1.0,
                },
                hard_gate_failures=("UNAUTHORIZED_ACTION",),
            ),
            EvalScenarioRecord(
                group_id="asset-dev-b",
                case_id="case-2",
                response_mode="unavailable",
                metrics={
                    "task_success_rate": 1.0,
                    "decision_accuracy": 1.0,
                    "tool_calls_per_run": 1.0,
                    "nonprogress_tool_calls": 1.0,
                },
            ),
        ),
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=adaptive_soft_budget_eval_rules(),
        bootstrap_samples=200,
    )

    assert report.decision == "REJECT"
    assert report.candidate_hard_gate_failures == ("UNAUTHORIZED_ACTION",)
    assert "CANDIDATE_HARD_GATE_FAILURE" in report.decision_reasons


def test_submaterial_efficiency_change_is_inconclusive_not_promoted() -> None:
    baseline = _bundle(
        "prod-runtime-v1-fixed-budget",
        tool_calls=3.0,
        nonprogress_calls=3.0,
    )
    candidate = _bundle(
        "repeated-nonprogress-soft-stop-v1",
        tool_calls=2.75,
        nonprogress_calls=2.75,
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=adaptive_soft_budget_eval_rules(),
        bootstrap_samples=200,
    )

    assert report.decision == "INCONCLUSIVE"
    assert report.decision_reasons == ("NO_MATERIAL_IMPROVEMENT",)
