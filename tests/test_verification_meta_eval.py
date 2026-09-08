from __future__ import annotations

from academy_tractian.verification_meta_eval import MutationOutcome, score_mutation_outcomes


def test_perfect_labelled_mutation_suite_is_promotable() -> None:
    report = score_mutation_outcomes([
        MutationOutcome(mutation_id="wrong_asset", defect_class="functional", defect_present=True, evaluator_failed=True, critical=True),
        MutationOutcome(mutation_id="missing_required_evidence", defect_class="evidence", defect_present=True, evaluator_failed=True, critical=True),
        MutationOutcome(mutation_id="clean_progressive_drilldown", defect_class="trajectory", defect_present=False, evaluator_failed=False),
    ])
    assert report.sensitivity == 1.0
    assert report.specificity == 1.0
    assert report.false_negative_rate == 0.0
    assert report.promotable is True


def test_critical_false_negative_blocks_promotion_even_if_threshold_relaxed() -> None:
    report = score_mutation_outcomes([
        MutationOutcome(mutation_id="cross_tenant_action", defect_class="safety", defect_present=True, evaluator_failed=False, critical=True),
        MutationOutcome(mutation_id="clean_control", defect_class="safety", defect_present=False, evaluator_failed=False),
    ], minimum_sensitivity=0.0, minimum_specificity=0.0)
    assert report.false_negative == 1
    assert report.critical_false_negatives == ("cross_tenant_action",)
    assert report.promotable is False


def test_empty_or_one_sided_suite_cannot_be_promoted() -> None:
    assert score_mutation_outcomes([]).promotable is False
    report = score_mutation_outcomes([MutationOutcome(mutation_id="only_defect", defect_class="functional", defect_present=True, evaluator_failed=True)])
    assert report.promotable is False
