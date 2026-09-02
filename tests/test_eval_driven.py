import pytest

from academy_tractian.eval_driven import (
    EvalMetricBundle,
    EvalMetricRule,
    EvalScenarioRecord,
    compare_eval_bundles,
)


def _bundle(config_id: str, rows: list[dict]) -> EvalMetricBundle:
    return EvalMetricBundle(
        config_id=config_id,
        records=tuple(EvalScenarioRecord(**row) for row in rows),
    )


def _rule(name: str = "task_success_rate", **kwargs) -> EvalMetricRule:
    return EvalMetricRule(
        name=name,
        direction=kwargs.pop("direction", "higher_is_better"),
        min_material_improvement=kwargs.pop("min_material_improvement", 0.02),
        **kwargs,
    )


def test_promotes_group_aware_material_improvement() -> None:
    baseline = _bundle(
        "baseline",
        [
            {"group_id": "s1", "case_id": "c1", "response_mode": "complete", "metrics": {"task_success_rate": 0.0}},
            {"group_id": "s1", "case_id": "c2", "response_mode": "complete", "metrics": {"task_success_rate": 1.0}},
            {"group_id": "s2", "case_id": "c3", "response_mode": "partial", "metrics": {"task_success_rate": 0.0}},
        ],
    )
    candidate = _bundle(
        "candidate",
        [
            {"group_id": "s1", "case_id": "c1", "response_mode": "complete", "metrics": {"task_success_rate": 1.0}},
            {"group_id": "s1", "case_id": "c2", "response_mode": "complete", "metrics": {"task_success_rate": 1.0}},
            {"group_id": "s2", "case_id": "c3", "response_mode": "partial", "metrics": {"task_success_rate": 1.0}},
        ],
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=(_rule(),),
        bootstrap_samples=500,
    )

    assert report.decision == "PROMOTE"
    assert report.paired_groups == ("s1", "s2")
    assert report.metric_deltas[0].baseline_mean == pytest.approx(0.25)
    assert report.metric_deltas[0].candidate_mean == 1.0


def test_hard_gate_failure_always_rejects() -> None:
    baseline = _bundle(
        "baseline",
        [{"group_id": "s1", "case_id": "c1", "metrics": {"task_success_rate": 0.0}}],
    )
    candidate = _bundle(
        "candidate",
        [
            {
                "group_id": "s1",
                "case_id": "c1",
                "metrics": {"task_success_rate": 1.0},
                "hard_gate_failures": ["UNAUTHORIZED_ACTION"],
            }
        ],
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=(_rule(),),
        bootstrap_samples=200,
    )

    assert report.decision == "REJECT"
    assert report.candidate_hard_gate_failures == ("UNAUTHORIZED_ACTION",)


def test_group_mismatch_is_inconclusive_not_promoted() -> None:
    baseline = _bundle(
        "baseline",
        [{"group_id": "s1", "case_id": "c1", "metrics": {"task_success_rate": 0.0}}],
    )
    candidate = _bundle(
        "candidate",
        [
            {"group_id": "s1", "case_id": "c1", "metrics": {"task_success_rate": 1.0}},
            {"group_id": "s2", "case_id": "c2", "metrics": {"task_success_rate": 1.0}},
        ],
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=(_rule(),),
        bootstrap_samples=200,
    )

    assert report.decision == "INCONCLUSIVE"
    assert "GROUP_SET_MISMATCH" in report.comparison_issues


def test_response_mode_regression_blocks_aggregate_promotion() -> None:
    baseline = _bundle(
        "baseline",
        [
            {"group_id": "s1", "case_id": "c1", "response_mode": "complete", "metrics": {"task_success_rate": 0.0}},
            {"group_id": "s2", "case_id": "c2", "response_mode": "conflict", "metrics": {"task_success_rate": 1.0}},
            {"group_id": "s3", "case_id": "c3", "response_mode": "complete", "metrics": {"task_success_rate": 0.0}},
        ],
    )
    candidate = _bundle(
        "candidate",
        [
            {"group_id": "s1", "case_id": "c1", "response_mode": "complete", "metrics": {"task_success_rate": 1.0}},
            {"group_id": "s2", "case_id": "c2", "response_mode": "conflict", "metrics": {"task_success_rate": 0.0}},
            {"group_id": "s3", "case_id": "c3", "response_mode": "complete", "metrics": {"task_success_rate": 1.0}},
        ],
    )

    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=(_rule(),),
        bootstrap_samples=500,
    )

    assert report.metric_deltas[0].directional_improvement > 0
    assert report.decision == "REJECT"
    assert "SLICE_REGRESSION:conflict:task_success_rate" in report.decision_reasons


def test_lower_is_better_metric_supported() -> None:
    baseline = _bundle(
        "baseline",
        [
            {"group_id": "s1", "case_id": "c1", "metrics": {"p95_latency_ms": 1000.0}},
            {"group_id": "s2", "case_id": "c2", "metrics": {"p95_latency_ms": 1200.0}},
        ],
    )
    candidate = _bundle(
        "candidate",
        [
            {"group_id": "s1", "case_id": "c1", "metrics": {"p95_latency_ms": 800.0}},
            {"group_id": "s2", "case_id": "c2", "metrics": {"p95_latency_ms": 900.0}},
        ],
    )

    latency_rule = _rule(
        "p95_latency_ms",
        direction="lower_is_better",
        min_material_improvement=100.0,
    )
    report = compare_eval_bundles(
        baseline,
        candidate,
        rules=(latency_rule,),
        bootstrap_samples=500,
    )

    assert report.decision == "PROMOTE"
    assert report.metric_deltas[0].directional_improvement == pytest.approx(250.0)
