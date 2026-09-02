from __future__ import annotations

import json
from pathlib import Path

from academy_tractian.handoff_audit import (
    EXPECTED_GROUP_COUNTS,
    EXPECTED_REPORTS,
    EXPECTED_STATUS_COUNTS,
    git_blob_sha1,
    load_audit,
    validate_handoff_audit,
)

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/final-handoff-acceptance-audit-freeze-v1.json"
RELOCATION_PATH = ROOT / "research/frozen/final-handoff-documentation-relocation-v2.json"
ADR016_FREEZE = ROOT / "research/frozen/provider-free-final-delivery-reproduction-evidence-freeze-v1.json"
ADR017_FREEZE_BLOB = "dec6c7e0beacd8003f65e6aedf7b45b74d99ddfd"


def _load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_adr017_freeze_is_unchanged_and_declared_blobs_are_preserved() -> None:
    freeze = _load(FREEZE_PATH)
    relocation = _load(RELOCATION_PATH)

    assert git_blob_sha1(FREEZE_PATH.read_bytes()) == ADR017_FREEZE_BLOB
    assert relocation["historical_freeze"] == {
        "path": "research/frozen/final-handoff-acceptance-audit-freeze-v1.json",
        "git_blob_sha1": ADR017_FREEZE_BLOB,
        "status": "UNCHANGED_HISTORICAL_EVIDENCE",
    }

    relocated = relocation["relocations"]
    direct_blobs = freeze["direct_blobs"]
    assert isinstance(direct_blobs, dict)

    for original_path, expected_blob in direct_blobs.items():
        if original_path in relocated:
            spec = relocated[original_path]
            assert spec["git_blob_sha1"] == expected_blob
            target = ROOT / spec["archive_path"]
        else:
            target = ROOT / original_path
        assert target.is_file(), original_path
        assert git_blob_sha1(target.read_bytes()) == expected_blob, original_path

    upstream = freeze["frozen_upstream_evidence"]
    adr016 = upstream["ADR016"]
    assert git_blob_sha1(ADR016_FREEZE.read_bytes()) == adr016["freeze_git_blob"]


def test_adr028_allows_active_docs_to_advance_without_erasing_v1() -> None:
    relocation = _load(RELOCATION_PATH)
    assert relocation["status"] == "FROZEN_HISTORICAL_HANDOFF_DOCUMENTATION_RELOCATION"
    assert relocation["active_documentation_policy"]["exact_blob_freeze_before_final_feature_freeze"] is False
    assert relocation["active_documentation_policy"]["final_exact_documentation_freeze_required"] is True

    old_readme = ROOT / relocation["relocations"]["README.md"]["archive_path"]
    old_runbook = ROOT / relocation["relocations"]["docs/FINAL-HANDOFF-RUNBOOK.md"]["archive_path"]
    assert git_blob_sha1(old_readme.read_bytes()) == "7298d2b4d7546b4ea93b64021faf95fb24958b0f"
    assert git_blob_sha1(old_runbook.read_bytes()) == "c7df131f555e3b07161fd1d518965958d245555c"
    assert git_blob_sha1((ROOT / "README.md").read_bytes()) != git_blob_sha1(old_readme.read_bytes())
    assert git_blob_sha1((ROOT / "docs/FINAL-HANDOFF-RUNBOOK.md").read_bytes()) != git_blob_sha1(old_runbook.read_bytes())


def test_adr017_freeze_reruns_canonical_83_row_audit() -> None:
    freeze = _load(FREEZE_PATH)
    audit = load_audit(ROOT)
    assert validate_handoff_audit(audit, ROOT) == []
    assert freeze["audit_population"]["total_rows"] == len(audit["rows"]) == 83
    assert freeze["audit_population"]["group_counts"] == EXPECTED_GROUP_COUNTS
    assert freeze["audit_disposition"] == {
        **EXPECTED_STATUS_COUNTS,
        "GAP_ACTION_REQUIRED": 0,
    }
    assert audit["status_counts"] == EXPECTED_STATUS_COUNTS


def test_adr017_freeze_preserves_provider_c4_and_scientific_boundaries() -> None:
    freeze = _load(FREEZE_PATH)
    assert freeze["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert freeze["scientific_state_changed"] is False
    assert freeze["production_provider_model_selected"] is False
    assert freeze["live_provider_calls_consumed"] == 0
    assert freeze["live_provider_call_envelope_max"] == 32
    assert freeze["credential_account_probes"] == 0
    assert freeze["real_customer_mutations"] == 0
    assert freeze["semantic_private_blind_access"] == 0
    assert freeze["global_architecture_frozen"] is False
    assert freeze["production_readiness_authorized"] is False

    upstream = freeze["frozen_upstream_evidence"]
    assert upstream["EV007"]["report_sha256"] == EXPECTED_REPORTS["ev007_report_sha256"]
    assert upstream["EV008"]["report_sha256"] == EXPECTED_REPORTS["ev008_report_sha256"]
    assert upstream["EV011"]["report_sha256"] == EXPECTED_REPORTS["ev011_report_sha256"]
    assert upstream["ADR016"]["demo_report_sha256"] == EXPECTED_REPORTS["delivery_demo_report_sha256"]
    assert upstream["provider_comparison"]["plan_sha256"] == EXPECTED_REPORTS["provider_comparison_plan_sha256"]
    assert upstream["provider_comparison"]["status"] == "UNEXECUTED_GATED"
    assert upstream["provider_comparison"]["calls_consumed"] == 0
    assert upstream["provider_comparison"]["provider_selected"] is False
    assert upstream["c4_score_row_artifact"]["sha256"] == EXPECTED_REPORTS["c4_required_artifact_sha256"]
    assert upstream["c4_score_row_artifact"]["repository_resident"] is False
    assert upstream["c4_score_row_artifact"]["status"] == "EXTERNALLY_BLOCKED"

    assert all(value is False for value in freeze["boundaries"].values())


def test_adr017_freeze_keeps_mandatory_nonpass_rows_visible() -> None:
    freeze = _load(FREEZE_PATH)
    audit = load_audit(ROOT)
    by_id = {row["audit_id"]: row for row in audit["rows"]}

    provider_contract = freeze["anti_overclaim_contract"]["provider_quality_row"]
    c4_contract = freeze["anti_overclaim_contract"]["c4_evaluation_integrity_row"]
    assert by_id[provider_contract["audit_id"]]["status"] == provider_contract["required_status"] == "UNEXECUTED_GATED"
    assert by_id[c4_contract["audit_id"]]["status"] == c4_contract["required_status"] == "EXTERNALLY_BLOCKED"
    assert freeze["anti_overclaim_contract"]["unclosed_gap_count"] == 0
    assert freeze["audit_disposition"]["GAP_ACTION_REQUIRED"] == 0


def test_adr017_freeze_records_validated_pre_freeze_baseline() -> None:
    freeze = _load(FREEZE_PATH)
    validation = freeze["validation"]
    assert freeze["validated_pre_freeze_head"] == "79101b51c7ff85a2ed08ba229bd54760eab1c226"
    assert validation["dedicated_workflow_run_id"] == 33165305212
    assert validation["production_runtime_run_id"] == 33165305239
    assert validation["adr016_reproduction_run_id"] == 33165305189
    assert validation["production_tests_in_clean_checkout_pre_freeze"] == 246
    assert validation["adr004_controller_regression_passed"] == 12
    assert validation["triggered_workflows_passed"] == validation["triggered_workflows_total"] == 14
    assert validation["final_audit_validation"] == "PASS"
