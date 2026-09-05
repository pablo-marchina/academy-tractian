from __future__ import annotations

from pathlib import Path

from academy_tractian.final_freeze_reopen import (
    FINAL_FREEZE_REOPEN_PATH,
    load_final_freeze_reopen_manifest,
    validate_final_freeze_reopen_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def test_current_freeze_reopen_manifest_is_hash_bound_and_truthful() -> None:
    manifest = load_final_freeze_reopen_manifest(ROOT)
    assert manifest.state == "FREEZE_REOPENED"
    assert manifest.hard_constraints["local_required_components_target"] == 0
    assert manifest.hard_constraints["production_path_hosted_only"] is True
    assert validate_final_freeze_reopen_manifest(manifest, ROOT) == []
    assert (ROOT / FINAL_FREEZE_REOPEN_PATH).is_file()


def test_superseded_freeze_bundle_is_preserved_byte_for_byte() -> None:
    manifest = load_final_freeze_reopen_manifest(ROOT)
    target = ROOT / manifest.superseded_manifest_path
    assert target.is_file()
    assert target.read_text(encoding="utf-8")
