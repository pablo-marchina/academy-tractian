from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import academy_tractian.stability_campaign as stability_module
from academy_tractian.stability_campaign import (
    STABILITY_DIMENSIONS,
    StabilityCampaignReport,
    StabilityRepetitionResult,
    StabilityUnitSpec,
    run_provider_free_stability_campaign,
    stability_population,
    summarize_stability_unit,
)


def _by_unit(report, unit_id: str):
    return tuple(result for result in report.repetitions if result.unit_id == unit_id)


def test_stability_population_is_exact_and_hash_verified() -> None:
    population = stability_population()
    assert [spec.unit_id for spec in population] == [
        "STAB-01",
        "STAB-02",
        "STAB-03",
        "STAB-04",
        "STAB-05",
        "STAB-06",
    ]
    assert [spec.fixture_kind for spec in population] == [
        "read_investigate",
        "clarify",
        "abstain",
        "escalate",
        "controlled_action",
        "safe_failure",
    ]
    assert all(spec.repetitions == 5 for spec in population)
    for spec in population:
        assert StabilityUnitSpec.model_validate(spec.model_dump(mode="json")) == spec


def test_provider_free_stability_campaign_is_exact_6_by_5_and_fully_stable(tmp_path: Path) -> None:
    report = run_provider_free_stability_campaign(tmp_path / "campaign")

    assert report.unit_count == 6
    assert report.repetitions_per_unit == 5
    assert report.denominator == 30
    assert len(report.repetitions) == 30
    assert len(report.summaries) == 6
    assert report.stable_unit_count == 6
    assert report.stable_dimension_checks == 66
    assert report.total_dimension_checks == 66
    assert report.contract_expectations_passed == 30
    assert report.sensitive_leak_count == 0
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0
    assert report.provider_calls == 0
    assert report.real_customer_mutations == 0
    assert all(summary.all_dimensions_stable for summary in report.summaries)
    assert all(summary.unstable_dimensions == () for summary in report.summaries)
    assert all(summary.stable_dimensions == STABILITY_DIMENSIONS for summary in report.summaries)
    assert all(result.trace_lifecycle_valid for result in report.repetitions)
    assert all(result.contract_expectations_met for result in report.repetitions)


def test_run_identity_is_normalized_without_hiding_behavior(tmp_path: Path) -> None:
    report = run_provider_free_stability_campaign(tmp_path / "campaign")
    read_results = _by_unit(report, "STAB-01")

    assert len({result.behavioral_trace_sha256 for result in read_results}) == 1
    assert len({result.tool_selection_sha256 for result in read_results}) == 1
    assert len({result.canonical_arguments_sha256 for result in read_results}) == 1
    assert len({result.final_response_sha256 for result in read_results}) == 1
    assert all(result.tool_sequence == ("get_asset",) for result in read_results)


def test_controlled_action_repetitions_use_isolated_claim_custody(tmp_path: Path) -> None:
    root = tmp_path / "campaign"
    report = run_provider_free_stability_campaign(root)
    action_results = _by_unit(report, "STAB-05")
    action_summary = next(summary for summary in report.summaries if summary.unit_id == "STAB-05")

    assert len(action_results) == 5
    assert action_summary.transport_count == 5
    assert action_summary.action_transport_count == 5
    assert all(result.transport_count == 1 for result in action_results)
    assert all(result.action_transport_count == 1 for result in action_results)
    assert all(result.tool_sequence == ("reprocess_analysis",) for result in action_results)
    assert len({result.action_fingerprint_sha256 for result in action_results}) == 1
    assert all("DUPLICATE_ACTION" not in "".join(result.policy_outcomes) for result in action_results)

    claim_files = []
    for repetition in range(1, 6):
        files = list((root / "STAB-05" / f"rep-{repetition}" / "claims").glob("*.json"))
        assert len(files) == 1
        claim_files.extend(files)
    assert len(claim_files) == 5


def test_safe_failure_family_is_repeatable_and_sanitized(tmp_path: Path) -> None:
    report = run_provider_free_stability_campaign(tmp_path / "campaign")
    failure_results = _by_unit(report, "STAB-06")

    assert all(result.terminal_decision == "ABSTAIN" for result in failure_results)
    assert all(result.terminal_reason_code == "TOOL_BOUNDARY_FAILURE" for result in failure_results)
    assert all(result.transport_count == 1 for result in failure_results)
    assert all(result.evaluator_pass for result in failure_results)
    assert all(result.sensitive_leak_count == 0 for result in failure_results)
    assert len({result.reason_code_sha256 for result in failure_results}) == 1
    assert len({result.behavioral_trace_sha256 for result in failure_results}) == 1


@pytest.mark.parametrize(
    ("field", "dimension"),
    [
        ("terminal_signature_sha256", "terminal_signature"),
        ("tool_selection_sha256", "tool_selection"),
        ("canonical_arguments_sha256", "canonical_arguments"),
        ("evaluator_classification_sha256", "evaluator_classification"),
        ("final_response_sha256", "final_response"),
    ],
)
def test_summary_detects_intentional_behavioral_instability(
    tmp_path: Path,
    field: str,
    dimension: str,
) -> None:
    report = run_provider_free_stability_campaign(tmp_path / field)
    spec = stability_population()[0]
    results = list(_by_unit(report, "STAB-01"))
    results[2] = results[2].model_copy(update={field: "0" * 64})

    summary = summarize_stability_unit(spec, tuple(results))

    assert summary.all_dimensions_stable is False
    assert dimension in summary.unstable_dimensions
    assert dimension not in summary.stable_dimensions


def test_campaign_report_hash_is_deterministic_across_fresh_roots(tmp_path: Path) -> None:
    first = run_provider_free_stability_campaign(tmp_path / "first")
    second = run_provider_free_stability_campaign(tmp_path / "second")

    assert first.report_sha256 == second.report_sha256
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_repetition_hash_and_report_hash_reject_tampering(tmp_path: Path) -> None:
    report = run_provider_free_stability_campaign(tmp_path / "campaign")

    repetition_data = report.repetitions[0].model_dump(mode="json")
    repetition_data["terminal_decision"] = "ABSTAIN"
    with pytest.raises(ValueError, match="result_sha256 mismatch"):
        StabilityRepetitionResult.model_validate(repetition_data)

    report_data = report.model_dump(mode="json")
    report_data["stable_unit_count"] = 5
    with pytest.raises(ValueError):
        StabilityCampaignReport.model_validate(report_data)


def test_stability_campaign_imports_no_live_provider_or_private_scientific_stack() -> None:
    source = inspect.getsource(stability_module)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    forbidden = {
        "openai",
        "google.generativeai",
        "academy_tractian.provider_clients",
        "academy_tractian.provider_live_execution",
        "academy_tractian.provider_live_task",
        "research.e2.evaluators",
        "research.e2.evaluation_suite",
    }
    assert imported_modules.isdisjoint(forbidden)
    assert "FRESH_BLIND" not in source
    assert "LEGACY_LOCKED_TEST" not in source
