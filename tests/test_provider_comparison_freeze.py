from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "research/frozen/provider-comparison-executor-freeze-v1.json"
ADR_PATH = ROOT / "docs/adr/010-provider-comparison-executor-2026-08-28.md"


def _git_blob(path: Path) -> str:
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def test_provider_comparison_executor_freeze_is_self_consistent() -> None:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    assert freeze["schema_version"] == "provider-comparison-executor-freeze-v1"
    assert freeze["status"] == "FROZEN_PROVIDER_FREE_EXECUTOR"
    assert freeze["issue"] == 38
    assert freeze["scientific_gate"] == "REQUIRED_PER_GROUP_AND_SLICE_REPORTING"
    assert freeze["scientific_state_changed"] is False
    assert freeze["production_live_calls_consumed"] == 0
    assert freeze["production_provider_model_selected"] is False
    assert freeze["production_mutating_actions_enabled"] is False
    assert freeze["validated_pre_adr_head"] == "58e0e13a2a0ec72d86ab607162914dcf3f6a4159"
    assert freeze["plan_sha256"] == "69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f"
    assert freeze["fixture"]["fixture_result"] is True
    assert freeze["fixture"]["selection"] == "NO_SELECTION"
    assert freeze["fixture"]["production_selection_claim"] is False

    adr_text = ADR_PATH.read_text(encoding="utf-8")
    assert "**Status:** ACCEPTED" in adr_text
    assert "FROZEN_FOR_PROVIDER_COMPARISON_EXECUTOR" in adr_text

    for item in freeze["frozen_files"]:
        path = ROOT / item["path"]
        assert path.is_file(), item["path"]
        assert _git_blob(path) == item["git_blob"], item["path"]

    fixture_path = ROOT / freeze["fixture"]["path"]
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert fixture["status"] == "PASS_PROVIDER_FREE_FIXTURE_NO_SELECTION"
    assert fixture["plan"]["sha256"] == freeze["plan_sha256"]
    assert fixture["production_live_calls_consumed"] == 0
    assert fixture["selection"] == "NO_SELECTION"
