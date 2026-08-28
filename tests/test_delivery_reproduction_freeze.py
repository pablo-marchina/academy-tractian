from __future__ import annotations

import json
from pathlib import Path

from academy_tractian.delivery_evidence import (
    EXPECTED_DELIVERY_DEMO_REPORT_SHA256,
    EXPECTED_DELIVERY_DEMO_RESULT_SHA256,
    validate_delivery_evidence_index,
)
from academy_tractian.delivery_reproduction import (
    EXPECTED_C4_ARTIFACT_BYTES,
    EXPECTED_C4_ARTIFACT_ROWS,
    EXPECTED_C4_ARTIFACT_SHA256,
    EXPECTED_EV007_REPORT_SHA256,
    EXPECTED_EV008_REPORT_SHA256,
    EXPECTED_EV011_REPORT_SHA256,
    EXPECTED_PROVIDER_PLAN_SHA256,
    EvidenceIndex,
    git_blob_sha1,
    run_provider_free_delivery_demo,
)


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/provider-free-final-delivery-reproduction-evidence-freeze-v1.json"
INDEX_PATH = ROOT / "research/results/final-delivery-evidence-index-2026-08-28.json"
MANIFEST_PATH = ROOT / "research/results/provider-free-final-delivery-demo-result-2026-08-28.json"


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_final_delivery_freeze_declared_blobs_are_exact() -> None:
    freeze = _load(FREEZE_PATH)
    direct_blobs = freeze["direct_blobs"]
    assert isinstance(direct_blobs, dict)
    for path, expected_blob in direct_blobs.items():
        assert isinstance(path, str)
        assert isinstance(expected_blob, str)
        assert git_blob_sha1(ROOT / path) == expected_blob

    upstream = freeze["frozen_upstream_evidence"]
    assert isinstance(upstream, dict)
    for family in ("EV007", "EV008", "EV011"):
        item = upstream[family]
        assert isinstance(item, dict)
        assert git_blob_sha1(ROOT / item["freeze_path"]) == item["freeze_git_blob"]
        assert git_blob_sha1(ROOT / item["result_path"]) == item["result_git_blob"]

    provider = upstream["provider_comparison_plan"]
    assert isinstance(provider, dict)
    assert git_blob_sha1(ROOT / provider["path"]) == provider["git_blob"]


def test_final_delivery_freeze_preserves_upstream_identities_and_boundaries() -> None:
    freeze = _load(FREEZE_PATH)
    assert freeze["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert freeze["scientific_state_changed"] is False
    assert freeze["production_provider_model_selected"] is False
    assert freeze["adr_009_live_calls_consumed"] == 0
    assert freeze["adr_009_live_call_envelope_max"] == 32
    assert freeze["credential_account_probes"] == 0
    assert freeze["real_customer_mutations"] == 0
    assert freeze["semantic_private_blind_access"] == 0

    upstream = freeze["frozen_upstream_evidence"]
    assert upstream["EV007"]["report_sha256"] == EXPECTED_EV007_REPORT_SHA256
    assert upstream["EV008"]["report_sha256"] == EXPECTED_EV008_REPORT_SHA256
    assert upstream["EV011"]["report_sha256"] == EXPECTED_EV011_REPORT_SHA256
    assert upstream["EV011"]["deliberate_evaluator_fail_case"] == "COMM-07"
    assert upstream["provider_comparison_plan"]["plan_sha256"] == EXPECTED_PROVIDER_PLAN_SHA256
    assert upstream["provider_comparison_plan"]["reproduction_status"] == "UNEXECUTED_GATED"

    c4 = upstream["c4_score_row_artifact"]
    assert c4["repository_resident"] is False
    assert c4["sha256"] == EXPECTED_C4_ARTIFACT_SHA256
    assert c4["bytes"] == EXPECTED_C4_ARTIFACT_BYTES
    assert c4["rows"] == EXPECTED_C4_ARTIFACT_ROWS
    assert c4["reproduction_status"] == "EXTERNALLY_BLOCKED"

    boundaries = freeze["boundaries"]
    assert isinstance(boundaries, dict)
    assert all(value is False for value in boundaries.values())


def test_final_delivery_freeze_evidence_index_resolves_exactly() -> None:
    freeze = _load(FREEZE_PATH)
    index = EvidenceIndex.model_validate(_load(INDEX_PATH))
    validation = validate_delivery_evidence_index(index, ROOT)

    expected = freeze["evidence_index"]
    assert isinstance(expected, dict)
    assert validation.passed
    assert validation.entry_count == expected["entry_count"] == 31
    assert validation.repository_resident_count == expected["repository_resident_count"] == 30
    assert validation.resolved_repository_entries == expected["resolved_repository_entries"] == 30
    assert len(validation.violations) == expected["violation_count"] == 0
    assert expected["external_blocker_count"] == 1
    assert expected["self_indexed"] is False
    assert not any(entry.repository_path == str(INDEX_PATH.relative_to(ROOT)) for entry in index.entries)


def test_final_delivery_freeze_manifest_matches_rerun(tmp_path: Path) -> None:
    freeze = _load(FREEZE_PATH)
    manifest = _load(MANIFEST_PATH)
    report = run_provider_free_delivery_demo(tmp_path / "freeze-reproduction")

    assert report.report_sha256 == EXPECTED_DELIVERY_DEMO_REPORT_SHA256
    assert report.report_sha256 == freeze["integrated_demo"]["report_sha256"]
    assert manifest["report_sha256"] == report.report_sha256
    assert report.denominator == 5
    assert report.exact_traces_evaluated == 5
    assert report.contract_expectations_passed == 5
    assert report.provider_calls == 0
    assert report.credential_account_probes == 0
    assert report.real_customer_mutations == 0
    assert report.semantic_private_blind_access == 0
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0

    frozen_scenarios = freeze["integrated_demo"]["scenario_hashes"]
    manifest_scenarios = {item["scenario_id"]: item for item in manifest["scenarios"]}
    assert [result.scenario_id for result in report.results] == list(EXPECTED_DELIVERY_DEMO_RESULT_SHA256)
    for result in report.results:
        expected = frozen_scenarios[result.scenario_id]
        static = manifest_scenarios[result.scenario_id]
        assert result.result_sha256 == EXPECTED_DELIVERY_DEMO_RESULT_SHA256[result.scenario_id]
        assert result.spec_sha256 == expected["spec_sha256"] == static["spec_sha256"]
        assert result.result_sha256 == expected["result_sha256"] == static["result_sha256"]
        assert result.trace_sha256 == expected["trace_sha256"] == static["trace_sha256"]
        assert (
            result.behavioral_trace_sha256
            == expected["behavioral_trace_sha256"]
            == static["behavioral_trace_sha256"]
        )
        assert result.trace_lifecycle_valid
        assert result.contract_expectations_met
        assert result.evaluator_pass


def test_final_delivery_freeze_records_preserved_falsifications() -> None:
    freeze = _load(FREEZE_PATH)
    falsifications = freeze["preserved_falsifications"]
    assert isinstance(falsifications, list)
    classes = {item["class"] for item in falsifications}
    assert classes == {
        "INFERRED_ADR_PATHS",
        "HISTORICAL_FREEZE_REPRESENTATION_ASSUMPTION",
    }
    historical = next(
        item
        for item in falsifications
        if item["class"] == "HISTORICAL_FREEZE_REPRESENTATION_ASSUMPTION"
    )
    assert historical["dedicated_workflow_run_id"] == 33158501340
    assert historical["production_tests"] == "231 passed / 1 failed"
