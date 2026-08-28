from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path

from academy_tractian.stability_campaign import run_provider_free_stability_campaign


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/ev008-provider-free-repeated-run-stability-freeze-v1.json"
RESULT_PATH = ROOT / "research/results/ev008-provider-free-stability-campaign-result-2026-08-28.json"


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return sha1(header + content).hexdigest()


def _freeze() -> dict:
    return json.loads(FREEZE_PATH.read_text(encoding="utf-8"))


def test_ev008_freeze_declared_blobs_match_checkout() -> None:
    freeze = _freeze()
    declared = {
        **freeze["direct_blobs"],
        **freeze["frozen_foundation_blobs"],
    }

    for relative_path, expected_sha in declared.items():
        path = ROOT / relative_path
        assert path.is_file(), relative_path
        assert _git_blob_sha(path) == expected_sha, relative_path


def test_ev008_result_manifest_matches_freeze() -> None:
    freeze = _freeze()
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    frozen_result = freeze["result"]

    for key in (
        "report_sha256",
        "unit_count",
        "repetitions_per_unit",
        "denominator",
        "stable_unit_count",
        "stable_dimension_checks",
        "total_dimension_checks",
        "contract_expectations_passed",
        "sensitive_leak_count",
        "automatic_retry_count",
        "replay_count",
        "provider_calls",
        "real_customer_mutations",
    ):
        assert result[key] == frozen_result[key], key

    manifest_summaries = {
        unit["unit_id"]: unit["summary_sha256"] for unit in result["units"]
    }
    assert manifest_summaries == frozen_result["unit_summary_sha256"]


def test_ev008_frozen_campaign_reproduces_exact_report_and_unit_hashes(tmp_path: Path) -> None:
    freeze = _freeze()
    report = run_provider_free_stability_campaign(tmp_path / "reproduction")
    frozen_result = freeze["result"]

    assert report.report_sha256 == frozen_result["report_sha256"]
    assert report.unit_count == 6
    assert report.repetitions_per_unit == 5
    assert report.denominator == 30
    assert report.stable_unit_count == 6
    assert report.stable_dimension_checks == 66
    assert report.total_dimension_checks == 66
    assert report.contract_expectations_passed == 30
    assert report.sensitive_leak_count == 0
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0
    assert report.provider_calls == 0
    assert report.real_customer_mutations == 0

    reproduced_summaries = {
        summary.unit_id: summary.summary_sha256 for summary in report.summaries
    }
    assert reproduced_summaries == frozen_result["unit_summary_sha256"]


def test_ev008_freeze_preserves_non_authorization_boundaries() -> None:
    boundaries = _freeze()["boundaries"]

    assert boundaries["adr009_live_calls_consumed"] == 0
    assert boundaries["credential_account_probes"] == 0
    assert boundaries["production_provider_selected"] is False
    assert boundaries["real_customer_mutations"] == 0
    assert boundaries["default_production_runtime_actions_enabled"] is False
    assert boundaries["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert boundaries["semantic_private_blind_access"] is False
    assert boundaries["production_readiness_claim_authorized"] is False
