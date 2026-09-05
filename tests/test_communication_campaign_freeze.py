from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path
import re

from academy_tractian.communication_campaign import run_provider_free_communication_campaign


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/ev011-provider-free-customer-safe-communication-freeze-v1.json"
RESULT_PATH = ROOT / "research/results/ev011-provider-free-communication-campaign-result-2026-08-28.json"
FROZEN_MANIFEST_GIT_BLOB = "38ab66419090279b95972a95e6a36bf7ef9fadd3"


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return sha1(header + content).hexdigest()


def _freeze() -> dict:
    return json.loads(FREEZE_PATH.read_text(encoding="utf-8"))


def test_ev011_freeze_preserves_direct_files_and_historical_foundation_manifest() -> None:
    freeze = _freeze()

    # Bind the complete freeze artifact so historical foundation hashes cannot be silently changed.
    assert _git_blob_sha(FREEZE_PATH) == FROZEN_MANIFEST_GIT_BLOB

    # Direct campaign files remain reproducible byte-for-byte.
    for relative_path, expected_sha in freeze["direct_blobs"].items():
        path = ROOT / relative_path
        assert path.is_file(), relative_path
        assert _git_blob_sha(path) == expected_sha, relative_path

    # Foundation blobs describe the validated historical runtime. Current production evolution is
    # allowed; the immutable manifest preserves the exact historical blob declarations.
    for relative_path, expected_sha in freeze["frozen_foundation_blobs"].items():
        assert (ROOT / relative_path).is_file(), relative_path
        assert re.fullmatch(r"[0-9a-f]{40}", expected_sha), relative_path


def test_ev011_result_manifest_matches_freeze() -> None:
    freeze = _freeze()
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    frozen_result = freeze["result"]

    for key in (
        "report_sha256",
        "denominator",
        "predicate_definition_count",
        "total_predicate_slots",
        "applicable_predicate_checks",
        "passed_predicate_checks",
        "failed_predicate_checks",
        "not_applicable_predicate_checks",
        "contract_expectations_passed",
        "evaluator_pass_cases",
        "evaluator_fail_cases",
        "evaluator_fail_case_ids",
        "provider_calls",
        "real_customer_mutations",
        "semantic_private_blind_access",
        "automatic_retry_count",
        "replay_count",
    ):
        assert result[key] == frozen_result[key], key

    manifest_cases = {
        case["case_id"]: {
            "spec_sha256": case["spec_sha256"],
            "result_sha256": case["result_sha256"],
        }
        for case in result["cases"]
    }
    assert manifest_cases == frozen_result["case_hashes"]


def test_ev011_frozen_campaign_reproduces_exact_report_and_case_hashes(tmp_path: Path) -> None:
    freeze = _freeze()
    report = run_provider_free_communication_campaign(tmp_path / "reproduction")
    frozen_result = freeze["result"]

    assert report.report_sha256 == frozen_result["report_sha256"]
    assert report.denominator == 10
    assert report.total_predicate_slots == 120
    assert report.applicable_predicate_checks == 60
    assert report.passed_predicate_checks == 60
    assert report.failed_predicate_checks == 0
    assert report.not_applicable_predicate_checks == 60
    assert report.contract_expectations_passed == 10
    assert report.provider_calls == 0
    assert report.real_customer_mutations == 0
    assert report.semantic_private_blind_access == 0
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0

    assert sum(result.evaluator_pass for result in report.results) == 9
    assert [result.case_id for result in report.results if not result.evaluator_pass] == ["COMM-07"]

    reproduced_cases = {
        result.case_id: {
            "spec_sha256": result.spec_sha256,
            "result_sha256": result.result_sha256,
        }
        for result in report.results
    }
    assert reproduced_cases == frozen_result["case_hashes"]


def test_ev011_freeze_preserves_non_authorization_boundaries() -> None:
    boundaries = _freeze()["boundaries"]

    assert boundaries["adr009_live_calls_consumed"] == 0
    assert boundaries["credential_account_probes"] == 0
    assert boundaries["production_provider_selected"] is False
    assert boundaries["real_customer_mutations"] == 0
    assert boundaries["default_production_runtime_actions_enabled"] is False
    assert boundaries["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert boundaries["semantic_private_blind_access"] is False
    assert boundaries["production_readiness_claim_authorized"] is False


def test_ev011_freeze_preserves_expected_evaluator_fail_as_distinct_from_communication_pass() -> None:
    frozen_result = _freeze()["result"]

    assert frozen_result["passed_predicate_checks"] == 60
    assert frozen_result["failed_predicate_checks"] == 0
    assert frozen_result["evaluator_pass_cases"] == 9
    assert frozen_result["evaluator_fail_cases"] == 1
    assert frozen_result["evaluator_fail_case_ids"] == ["COMM-07"]
