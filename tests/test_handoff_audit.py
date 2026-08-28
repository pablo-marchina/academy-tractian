from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from academy_tractian.handoff_audit import load_audit, validate_handoff_audit

ROOT = Path(__file__).resolve().parents[1]


def _payload() -> dict:
    return load_audit(ROOT)


def test_canonical_final_handoff_audit_passes() -> None:
    assert validate_handoff_audit(_payload(), ROOT) == []


def test_duplicate_audit_id_is_rejected() -> None:
    payload = deepcopy(_payload())
    payload["rows"][1]["audit_id"] = payload["rows"][0]["audit_id"]
    assert "duplicate_audit_id" in validate_handoff_audit(payload, ROOT)


def test_pass_without_evidence_is_rejected() -> None:
    payload = deepcopy(_payload())
    payload["rows"][0]["evidence"] = []
    failures = validate_handoff_audit(payload, ROOT)
    assert "row_00_pass_without_evidence" in failures


def test_bounded_row_without_limitation_is_rejected() -> None:
    payload = deepcopy(_payload())
    bounded_index = next(
        index for index, row in enumerate(payload["rows"])
        if row["status"] == "PASS_BOUNDED"
    )
    payload["rows"][bounded_index]["limitation_or_blocker"] = None
    failures = validate_handoff_audit(payload, ROOT)
    assert f"row_{bounded_index:02d}_missing_limitation" in failures


def test_gap_without_action_is_rejected() -> None:
    payload = deepcopy(_payload())
    payload["rows"][0]["status"] = "GAP_ACTION_REQUIRED"
    payload["rows"][0]["gap_action"] = None
    failures = validate_handoff_audit(payload, ROOT)
    assert "row_00_gap_without_action" in failures
    assert "unclosed_gap" in failures


def test_provider_quality_cannot_be_relabelled_pass() -> None:
    payload = deepcopy(_payload())
    row = next(row for row in payload["rows"] if row["audit_id"] == "E-11")
    row["status"] = "PASS_EVIDENCED"
    row["evidence"] = [{"path": "docs/CURRENT-PROJECT-STATUS.md"}]
    failures = validate_handoff_audit(payload, ROOT)
    assert "provider_disposition" in failures


def test_c4_blocker_cannot_be_relabelled_pass() -> None:
    payload = deepcopy(_payload())
    row = next(row for row in payload["rows"] if row["audit_id"] == "C-13")
    row["status"] = "PASS_EVIDENCED"
    row["evidence"] = [{"path": "docs/BENCHMARK-INTEGRITY-GATE.md"}]
    failures = validate_handoff_audit(payload, ROOT)
    assert "c4_blocker_disposition" in failures


def test_missing_evidence_path_is_rejected() -> None:
    payload = deepcopy(_payload())
    payload["rows"][0]["evidence"] = [{"path": "does/not/exist.json"}]
    failures = validate_handoff_audit(payload, ROOT)
    assert "row_00_evidence_0_missing" in failures


def test_declared_group_population_cannot_drift() -> None:
    payload = deepcopy(_payload())
    payload["population"]["group_counts"]["C"] = 12
    failures = validate_handoff_audit(payload, ROOT)
    assert "population_group_counts" in failures
