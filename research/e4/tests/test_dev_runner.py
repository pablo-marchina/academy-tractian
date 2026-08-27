from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.research.e4_dev_runner import (
    classify_proposal_source,
    run_dev,
)


def write_split(tmp_path: Path) -> Path:
    manifest = {
        "schema_version": "benchmark-split-v1",
        "status": "FROZEN",
        "splits": {
            "DEV": {"groups": [{"group_id": "asset_G501", "scenarios": ["CEN-01"]}]},
            "VALIDATION": {"groups": [{"group_id": "asset_B204", "scenarios": ["CEN-07"]}]},
            "LOCKED_TEST": {"groups": [{"group_id": "asset_V301", "scenarios": ["CEN-08"]}]},
        },
    }
    path = tmp_path / "benchmark-split-v1.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_proposal_source_class_is_explicit_and_marks_scripted_as_infrastructure_only():
    scripted = classify_proposal_source("scripted_reference")
    assert scripted["agent_quality_evidence"] is False
    assert scripted["evidence_class"] == "infrastructure_only"

    model = classify_proposal_source("model_agent")
    assert model["agent_quality_evidence"] is True
    assert model["evidence_class"] == "agent_candidate"

    with pytest.raises(ValueError):
        classify_proposal_source("")


def test_dev_runner_rejects_locked_test_and_validation(tmp_path: Path):
    split = write_split(tmp_path)
    with pytest.raises(ValueError, match="locked"):
        run_dev(split_manifest=split, split="LOCKED_TEST", proposal_source_class="scripted_reference")
    with pytest.raises(ValueError, match="only allows DEV"):
        run_dev(split_manifest=split, split="VALIDATION", proposal_source_class="scripted_reference")


def test_dev_runner_executes_b0_b3_and_exports_per_variant_metrics(tmp_path: Path):
    report = run_dev(split_manifest=write_split(tmp_path), split="DEV", proposal_source_class="scripted_reference")
    assert report["split"] == "DEV"
    assert report["locked_test_accessed"] is False
    assert report["infrastructure_only"] is True
    assert report["agent_quality_claim"] is False

    by_variant = {item["variant"]: item for item in report["variants"]}
    assert set(by_variant) == {"B0", "B1", "B2", "B3"}

    assert by_variant["B0"]["invalid_argument_executions"] == 1
    assert by_variant["B0"]["cross_company_action_executions"] == 1
    assert by_variant["B0"]["premature_action_executions"] == 1

    assert by_variant["B1"]["blocked_by_code"]["ARGUMENT_INVALID"] >= 1
    assert by_variant["B2"]["blocked_by_code"]["RESOURCE_SCOPE_DENIED"] >= 1
    assert by_variant["B3"]["blocked_by_code"]["EVIDENCE_INSUFFICIENT"] >= 1
    assert by_variant["B3"]["valid_action_after_evidence_executions"] == 1
