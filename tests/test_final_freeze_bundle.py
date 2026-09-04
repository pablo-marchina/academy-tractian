from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from academy_tractian.final_freeze_bundle import (
    EXPECTED_DECISION_STATUS,
    REQUIRED_NON_CLAIMS,
    FinalFreezeManifest,
    build_manifest,
    validate_final_freeze_manifest,
)
from academy_tractian.handoff_audit import git_blob_sha1


def _manifest(tmp_path: Path) -> FinalFreezeManifest:
    artifact_paths = []
    artifacts = []
    for index, decision_id in enumerate(EXPECTED_DECISION_STATUS):
        relative = Path("evidence") / f"artifact-{index:02d}.txt"
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"evidence for {decision_id}\n", encoding="utf-8")
        path = relative.as_posix()
        artifact_paths.append(path)
        artifacts.append(
            {
                "path": path,
                "git_blob_sha1": git_blob_sha1(target.read_bytes()),
                "role": "current_decision",
                "description": f"Evidence for {decision_id}",
            }
        )

    decisions = []
    for index, (decision_id, status) in enumerate(EXPECTED_DECISION_STATUS.items()):
        decisions.append(
            {
                "decision_id": decision_id,
                "status": status,
                "evidence_paths": [artifact_paths[index]],
                "claim_boundary": f"Bounded claim for {decision_id}",
            }
        )

    return build_manifest(
        schema_version="final-freeze-evidence-bundle-v1",
        bundle_state="READY_FOR_HARD_FREEZE",
        bundle_date="2026-09-04",
        hard_freeze_effective_date="2026-09-05",
        final_delivery_date="2026-09-08",
        required_gate_name="required-gate",
        branch_protection_enforced=False,
        artifacts=artifacts,
        decisions=decisions,
        non_claims=sorted(REQUIRED_NON_CLAIMS),
    )


def test_final_freeze_manifest_is_hash_bound_and_validates_registered_blobs(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)

    assert validate_final_freeze_manifest(manifest, tmp_path) == []
    assert len(manifest.manifest_sha256) == 64
    assert manifest.branch_protection_enforced is False


def test_final_freeze_manifest_fails_closed_on_artifact_tamper(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    target = tmp_path / manifest.artifacts[0].path
    target.write_text("tampered\n", encoding="utf-8")

    failures = validate_final_freeze_manifest(manifest, tmp_path)
    assert "artifact_0_blob_mismatch" in failures


def test_final_freeze_manifest_rejects_hash_tampering(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    payload = manifest.model_dump(mode="json")
    payload["non_claims"] = payload["non_claims"][:-1]

    with pytest.raises(ValidationError, match="hash mismatch"):
        FinalFreezeManifest.model_validate(payload)


def test_final_freeze_manifest_rejects_missing_decision_and_unregistered_evidence(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    payload = manifest.model_dump(mode="json", exclude={"manifest_sha256"})
    payload["decisions"] = payload["decisions"][:-1]
    payload["decisions"][0]["evidence_paths"] = ["not-registered.txt"]
    mutated = build_manifest(**payload)

    failures = validate_final_freeze_manifest(mutated, tmp_path)
    assert "decision_set" in failures
    assert "decision_0_unregistered_evidence" in failures


def test_final_freeze_manifest_requires_all_explicit_non_claims(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    payload = manifest.model_dump(mode="json", exclude={"manifest_sha256"})
    payload["non_claims"] = [
        value for value in payload["non_claims"] if value != "branch_protection_enforced"
    ]
    mutated = build_manifest(**payload)

    assert "required_non_claims" in validate_final_freeze_manifest(mutated, tmp_path)
