from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

import academy_tractian.failure_campaign as campaign_module
from academy_tractian.failure_campaign import (
    FAILURE_CAMPAIGN_VERSION,
    FailureCampaignReport,
    FailureCaseResult,
    failure_population,
    run_provider_free_failure_campaign,
)


EXPECTED_CASES = {
    "EV007-01": ("decision_source_client_exception", True, "DECISION_SOURCE_FAILURE", 0),
    "EV007-02": ("decision_source_audit_failure", True, "DECISION_SOURCE_AUDIT_FAILURE", 0),
    "EV007-03": ("malformed_provider_payload", True, "DECISION_SOURCE_FAILURE", 0),
    "EV007-04": ("unknown_tool_from_provider", True, "DECISION_SOURCE_FAILURE", 0),
    "EV007-05": ("canonical_argument_invalid", False, None, 0),
    "EV007-06": ("read_transport_exception", True, "TOOL_BOUNDARY_FAILURE", 1),
    "EV007-07": ("controlled_action_authorization_denial", True, None, 0),
    "EV007-08": ("controlled_action_duplicate", True, None, 0),
    "EV007-09": ("controlled_action_transport_failure_after_claim", False, "TOOL_BOUNDARY_FAILURE", 1),
    "EV007-10": ("partial_unavailable_evidence_escalation", True, "SOURCE_UNAVAILABLE", 1),
    "EV007-11": ("tampered_model_call_provenance", False, "NO_SAFE_PATH", 0),
}


def test_failure_population_is_exact_sorted_and_hash_verified() -> None:
    population = failure_population()

    assert len(population) == 11
    assert [spec.case_id for spec in population] == sorted(EXPECTED_CASES)
    assert len({spec.spec_sha256 for spec in population}) == 11
    assert all(spec.campaign_version == FAILURE_CAMPAIGN_VERSION for spec in population)

    for spec in population:
        family, expected_eval, expected_reason, expected_transport = EXPECTED_CASES[spec.case_id]
        assert spec.failure_family == family
        assert spec.expected_evaluator_pass is expected_eval
        assert spec.expected_terminal_reason_code == expected_reason
        assert spec.expected_transport_count == expected_transport


def test_provider_free_failure_campaign_meets_all_preregistered_safety_expectations(
    tmp_path: Path,
) -> None:
    report = run_provider_free_failure_campaign(tmp_path / "campaign")

    assert report.denominator == 11
    assert report.safety_expectations_passed == 11
    assert report.evaluator_expected_pass_cases == 8
    assert report.evaluator_expected_fail_cases == 3
    assert report.raw_sensitive_leak_count == 0
    assert report.provider_calls == 0
    assert report.real_customer_mutations == 0
    assert report.automatic_retry_count == 0
    assert [result.case_id for result in report.results] == sorted(EXPECTED_CASES)
    assert all(result.safety_expectations_met for result in report.results)
    assert all(result.trace_lifecycle_valid for result in report.results)
    assert all(result.raw_sensitive_leak_count == 0 for result in report.results)


def test_failure_campaign_preserves_expected_evaluator_rejections_instead_of_hiding_them(
    tmp_path: Path,
) -> None:
    report = run_provider_free_failure_campaign(tmp_path / "campaign")
    results = {result.case_id: result for result in report.results}

    assert results["EV007-05"].evaluator_pass is False
    assert "ARGUMENT_INVALID" in results["EV007-05"].policy_violations

    assert results["EV007-09"].evaluator_pass is False
    assert results["EV007-09"].claim_state == "claimed"
    assert results["EV007-09"].transport_count == 1
    assert results["EV007-09"].action_transport_count == 1
    assert results["EV007-09"].replay_transport_count == 0

    assert results["EV007-11"].evaluator_pass is False
    assert results["EV007-11"].terminal_reason_code == "NO_SAFE_PATH"

    for case_id in set(EXPECTED_CASES) - {"EV007-05", "EV007-09", "EV007-11"}:
        assert results[case_id].evaluator_pass is True


def test_failure_campaign_action_claim_and_duplicate_semantics_are_explicit(
    tmp_path: Path,
) -> None:
    report = run_provider_free_failure_campaign(tmp_path / "campaign")
    results = {result.case_id: result for result in report.results}

    denied = results["EV007-07"]
    assert denied.claim_state == "none"
    assert denied.transport_count == 0
    assert denied.action_transport_count == 0
    assert "CONFIRMATION_REQUIRED" in denied.policy_violations

    duplicate = results["EV007-08"]
    assert duplicate.claim_state == "existing"
    assert duplicate.setup_transport_count == 1
    assert duplicate.transport_count == 0
    assert duplicate.action_transport_count == 0
    assert "DUPLICATE_ACTION" in duplicate.policy_violations

    uncertain = results["EV007-09"]
    assert uncertain.claim_state == "claimed"
    assert uncertain.replay_transport_count == 0
    assert uncertain.automatic_retry_count == 0


def test_failure_campaign_safe_terminal_failure_families_are_sanitized(
    tmp_path: Path,
) -> None:
    report = run_provider_free_failure_campaign(tmp_path / "campaign")
    results = {result.case_id: result for result in report.results}

    assert results["EV007-01"].terminal_decision == "ABSTAIN"
    assert results["EV007-01"].transport_count == 0
    assert results["EV007-02"].terminal_reason_code == "DECISION_SOURCE_AUDIT_FAILURE"
    assert results["EV007-03"].terminal_reason_code == "DECISION_SOURCE_FAILURE"
    assert results["EV007-04"].terminal_reason_code == "DECISION_SOURCE_FAILURE"
    assert results["EV007-06"].terminal_reason_code == "TOOL_BOUNDARY_FAILURE"
    assert results["EV007-10"].terminal_decision == "ESCALATE_HUMAN"
    assert results["EV007-10"].terminal_reason_code == "SOURCE_UNAVAILABLE"

    serialized = report.model_dump_json()
    for forbidden in (
        "EV007-PRIVATE-PROVIDER-EXCEPTION",
        "EV007-SENSITIVE-AUDIT-PROMPT-MUST-NOT-ENTER-TRACE",
        "EV007-SENSITIVE-MALFORMED-PROVIDER-BODY",
        "EV007-PRIVATE-READ-TRANSPORT-EXCEPTION",
        "EV007-PRIVATE-ACTION-TRANSPORT-EXCEPTION",
        "idempotency-auth-denial",
        "idempotency-duplicate",
        "idempotency-post-claim-failure",
    ):
        assert forbidden not in serialized


def test_failure_campaign_report_hash_is_deterministic_across_fresh_custody_roots(
    tmp_path: Path,
) -> None:
    first = run_provider_free_failure_campaign(tmp_path / "first")
    second = run_provider_free_failure_campaign(tmp_path / "second")

    assert first == second
    assert first.report_sha256 == second.report_sha256
    assert [result.result_sha256 for result in first.results] == [
        result.result_sha256 for result in second.results
    ]


def test_failure_case_result_hash_rejects_tampering(tmp_path: Path) -> None:
    report = run_provider_free_failure_campaign(tmp_path / "campaign")
    original = report.results[0].model_dump(mode="json")
    original["transport_count"] = 99

    with pytest.raises(ValidationError):
        FailureCaseResult.model_validate(original)


def test_failure_campaign_report_hash_rejects_tampering(tmp_path: Path) -> None:
    report = run_provider_free_failure_campaign(tmp_path / "campaign")
    data = report.model_dump(mode="json")
    data["safety_expectations_passed"] = 0

    with pytest.raises(ValidationError):
        FailureCampaignReport.model_validate(data)


def test_failure_campaign_surface_imports_no_provider_sdk_or_private_evaluator_stack() -> None:
    source = inspect.getsource(campaign_module)
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    imported_modules: set[str] = set()
    imported_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
                imported_modules.add(alias.name)
                imported_names.add(alias.asname or alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
            imported_modules.add(node.module)
            imported_names.update(alias.asname or alias.name for alias in node.names)

    assert imported_roots.isdisjoint(
        {
            "anthropic",
            "cerebras",
            "groq",
            "langchain",
            "langgraph",
            "openai",
            "pydantic_ai",
        }
    )
    assert "research.e2.evaluators" not in imported_modules
    assert "research.e2.evaluation_suite" not in imported_modules
    assert "Scenario" not in imported_names
    assert "EvaluationSuite" not in imported_names
