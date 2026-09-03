from __future__ import annotations

import json
from pathlib import Path

from academy_tractian.adaptive_experiment_preflight import run_adaptive_experiment_preflight


DEV_GROUPS = ("asset_G501", "asset_C710", "asset_S420", "asset_M208", "asset_M101")
VALIDATION_GROUPS = ("asset_B204", "asset_M102")
LOCKED_GROUPS = ("asset_V301", "asset_M605", "asset_M205")


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _manifest(tmp_path: Path) -> Path:
    def groups(values: tuple[str, ...]) -> list[dict[str, str]]:
        return [{"group_id": value} for value in values]

    return _write_json(
        tmp_path / "benchmark-split-v1.json",
        {
            "schema_version": "benchmark-split-v1",
            "status": "FROZEN",
            "splits": {
                "DEV": {"groups": groups(DEV_GROUPS)},
                "VALIDATION": {"groups": groups(VALIDATION_GROUPS)},
                "LOCKED_TEST": {"groups": groups(LOCKED_GROUPS)},
            },
        },
    )


def _cases(tmp_path: Path, groups: tuple[str, ...], *, name: str = "agent-input-cases.json") -> Path:
    return _write_json(
        tmp_path / name,
        {
            "cases": [
                {
                    "asset_group": group_id,
                    "prompt": f"private-prompt-{group_id}",
                    "oracle": f"private-gold-{group_id}",
                }
                for group_id in groups
            ]
        },
    )


def test_missing_canonical_source_fails_closed_with_exact_reason(tmp_path: Path) -> None:
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=tmp_path / "not-materialized.json",
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.experiment_id == "ADAPT-A-001"
    assert result.execution_status == "NOT_READY"
    assert result.decision == "INCONCLUSIVE"
    assert result.reason == "CANONICAL_DEV_CASE_SOURCE_NOT_MATERIALIZED"
    assert result.source_materialized is False
    assert result.source_sha256 is None
    assert result.required_dev_groups == DEV_GROUPS
    assert result.observed_group_ids == ()


def test_incomplete_dev_source_is_not_ready(tmp_path: Path) -> None:
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=_cases(tmp_path, DEV_GROUPS[:-1]),
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.decision == "INCONCLUSIVE"
    assert result.reason == "CANONICAL_DEV_CASE_SOURCE_INCOMPLETE"
    assert set(result.observed_group_ids) == set(DEV_GROUPS[:-1])


def test_validation_or_locked_group_contamination_fails_closed(tmp_path: Path) -> None:
    source = _cases(tmp_path, DEV_GROUPS + (VALIDATION_GROUPS[0],))
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.decision == "INCONCLUSIVE"
    assert result.reason == "FORBIDDEN_SPLIT_CONTAMINATION"
    assert VALIDATION_GROUPS[0] in result.observed_group_ids


def test_duplicate_dev_group_fails_closed(tmp_path: Path) -> None:
    source = _cases(tmp_path, DEV_GROUPS + (DEV_GROUPS[0],))
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=_manifest(tmp_path),
    )

    assert result.execution_status == "NOT_READY"
    assert result.decision == "INCONCLUSIVE"
    assert result.reason == "DUPLICATE_DEV_GROUP"


def test_exact_five_group_dev_source_is_ready_but_not_promoted(tmp_path: Path) -> None:
    manifest = _manifest(tmp_path)
    source = _cases(tmp_path, DEV_GROUPS)

    first = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=manifest,
    )
    second = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=manifest,
    )

    assert first.execution_status == "READY"
    assert first.decision == "INCONCLUSIVE"
    assert first.reason is None
    assert first.source_materialized is True
    assert first.required_dev_groups == DEV_GROUPS
    assert set(first.observed_group_ids) == set(DEV_GROUPS)
    assert first.source_sha256 is not None and len(first.source_sha256) == 64
    assert first.manifest_sha256 is not None and len(first.manifest_sha256) == 64
    assert first.source_sha256 == second.source_sha256
    assert first.manifest_sha256 == second.manifest_sha256


def test_safe_result_never_contains_prompt_or_oracle_payload(tmp_path: Path) -> None:
    source = _cases(tmp_path, DEV_GROUPS)
    result = run_adaptive_experiment_preflight(
        agent_input_cases_path=source,
        split_manifest_path=_manifest(tmp_path),
    )

    serialized = json.dumps(result.model_dump(), sort_keys=True)
    assert "private-prompt" not in serialized
    assert "private-gold" not in serialized
    assert "oracle" not in serialized
    assert "prompt" not in serialized
