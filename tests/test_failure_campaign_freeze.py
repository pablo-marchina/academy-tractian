from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path
import re

from academy_tractian.failure_campaign import FailureCampaignReport


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/ev007-provider-free-failure-performance-freeze-v1.json"
FROZEN_MANIFEST_GIT_BLOB = "cd6bdb9c6036e1cbca2d7943d25af8bc64021c6e"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return sha1(header + data).hexdigest()


def _assert_frozen_file(entry: dict[str, str]) -> None:
    path = ROOT / entry["path"]
    assert path.is_file(), entry["path"]
    assert _git_blob_sha(path) == entry["git_blob"], entry["path"]


def _assert_historical_dependency_declaration(entry: dict[str, str]) -> None:
    path = ROOT / entry["path"]
    assert path.is_file(), entry["path"]
    assert re.fullmatch(r"[0-9a-f]{40}", entry["git_blob"])


def test_ev007_freeze_preserves_exact_campaign_and_historical_dependency_manifest() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))

    # The freeze manifest itself is immutable. Historical foundation blobs are therefore protected
    # without requiring the current checkout to remain byte-identical to the 2026-08-28 runtime.
    assert _git_blob_sha(FREEZE_PATH) == FROZEN_MANIFEST_GIT_BLOB
    assert freeze["schema_version"] == "ev007-provider-free-failure-performance-freeze-v1"
    assert freeze["status"] == "FROZEN_FOR_PROVIDER_FREE_FAILURE_PERFORMANCE_CAMPAIGN"
    assert freeze["adr_009_live_calls_consumed"] == 0
    assert freeze["real_customer_mutations"] == 0

    # Files owned directly by the frozen campaign remain reproducible from the current repository.
    for key in ("source", "tests", "validator", "workflow"):
        _assert_frozen_file(freeze["campaign"][key])
    _assert_frozen_file(freeze["result"])

    # Foundation dependencies are historical evidence, not an authorization to pin production code
    # forever. Their exact historical hashes remain protected by the immutable freeze manifest.
    for entry in freeze["preserved_dependencies"].values():
        _assert_historical_dependency_declaration(entry)


def test_ev007_frozen_result_revalidates_exact_campaign_contract() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    result_path = ROOT / freeze["result"]["path"]
    report = FailureCampaignReport.model_validate_json(result_path.read_text(encoding="utf-8"))

    assert report.report_sha256 == "7b281d3ad6b2d7e2f1407c6321b5200b4185625a284b1c8a20bd1818ced9ddf9"
    assert report.report_sha256 == freeze["result"]["report_sha256"]
    assert report.denominator == freeze["result"]["denominator"] == 11
    assert report.safety_expectations_passed == freeze["result"]["safety_expectations_passed"] == 11
    assert report.evaluator_expected_pass_cases == freeze["result"]["expected_evaluator_pass_cases"] == 8
    assert report.evaluator_expected_fail_cases == freeze["result"]["expected_evaluator_fail_cases"] == 3
    assert report.raw_sensitive_leak_count == freeze["result"]["raw_sensitive_leak_count"] == 0
    assert report.provider_calls == freeze["result"]["provider_calls"] == 0
    assert report.real_customer_mutations == freeze["result"]["real_customer_mutations"] == 0
    assert report.automatic_retry_count == freeze["result"]["automatic_retry_count"] == 0

    assert [result.case_id for result in report.results] == freeze["case_ids"]
    assert [
        result.case_id for result in report.results if not result.expected_evaluator_pass
    ] == freeze["expected_evaluator_failures"]
    assert all(result.safety_expectations_met for result in report.results)
    assert all(result.raw_sensitive_leak_count == 0 for result in report.results)
    assert all(result.automatic_retry_count == 0 for result in report.results)


def test_ev007_freeze_preserves_safety_and_authorization_boundaries() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    invariants = freeze["invariants"]

    assert invariants["safety_containment_distinct_from_evaluator_correctness"] is True
    assert invariants["provider_network_inference_used"] is False
    assert invariants["credential_probe_used"] is False
    assert invariants["second_tool_execution_path_added"] is False
    assert invariants["raw_exception_or_provider_body_persisted"] is False
    assert invariants["automatic_retry_used"] is False
    assert invariants["automatic_action_replay_used"] is False
    assert invariants["default_production_runtime_actions_enabled"] is False
    assert invariants["blanket_real_customer_mutation_authorized"] is False
