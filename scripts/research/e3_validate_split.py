from __future__ import annotations

"""Validate BENCHMARK-SPLIT-v1 without reading evaluator-only gold.

This script protects the benchmark split from accidental leakage. It uses only the
public group/scenario metadata stored in research/frozen/benchmark-split-v1.json.
"""

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_GROUPS = {
    "asset_G501",
    "asset_C710",
    "asset_S420",
    "asset_M208",
    "asset_M101",
    "asset_B204",
    "asset_M102",
    "asset_V301",
    "asset_M605",
    "asset_M205",
}

EXPECTED_SCENARIOS = {f"CEN-{i:02d}" for i in range(1, 17)}
EXPECTED_SPLITS = {"DEV", "VALIDATION", "LOCKED_TEST"}


def iter_groups(manifest: dict[str, Any]):
    for split_name, split in manifest["splits"].items():
        for group in split["groups"]:
            yield split_name, group


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split",
        type=Path,
        default=Path("research/frozen/benchmark-split-v1.json"),
        help="Path to public BENCHMARK-SPLIT-v1 manifest.",
    )
    args = parser.parse_args()

    manifest = json.loads(args.split.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "benchmark-split-v1"
    assert manifest["status"] == "FROZEN"
    assert set(manifest["splits"]) == EXPECTED_SPLITS
    assert manifest["rules"]["no_storyline_split"] is True
    assert manifest["rules"]["locked_test_available_for_architecture_selection"] is False
    assert manifest["rules"]["locked_test_available_for_prompt_or_model_selection"] is False
    assert manifest["rules"]["gold_is_evaluator_only"] is True

    group_to_split: dict[str, str] = {}
    scenario_to_split: dict[str, str] = {}
    for split_name, group in iter_groups(manifest):
        group_id = group["group_id"]
        if group_id in group_to_split:
            raise AssertionError(
                f"leakage: group {group_id} appears in both {group_to_split[group_id]} and {split_name}"
            )
        group_to_split[group_id] = split_name
        for scenario_id in group["scenarios"]:
            if scenario_id in scenario_to_split:
                raise AssertionError(
                    f"leakage: scenario {scenario_id} appears in both {scenario_to_split[scenario_id]} and {split_name}"
                )
            scenario_to_split[scenario_id] = split_name

    assert set(group_to_split) == EXPECTED_GROUPS, sorted(EXPECTED_GROUPS - set(group_to_split))
    assert set(scenario_to_split) == EXPECTED_SCENARIOS, sorted(EXPECTED_SCENARIOS - set(scenario_to_split))

    for split_name, expected in manifest["aggregate_counts"].items():
        actual_groups = [group for candidate, group in iter_groups(manifest) if candidate == split_name]
        actual_scenarios = [scenario for group in actual_groups for scenario in group["scenarios"]]
        assert expected["groups"] == len(actual_groups), split_name
        assert expected["scenarios"] == len(actual_scenarios), split_name

    for split_name, split in manifest["splits"].items():
        modalities = {modality for group in split["groups"] for modality in group["modalities"]}
        assert "investigate" in modalities, f"{split_name} lacks investigate coverage"

    # Contextualization appears in all three splits by design, but with different families.
    for split_name, split in manifest["splits"].items():
        modalities = {modality for group in split["groups"] for modality in group["modalities"]}
        assert "contextualize" in modalities, f"{split_name} lacks contextualize coverage"

    # Actions/execute coverage appears in all three splits; exact action endpoints need not duplicate.
    for split_name, split in manifest["splits"].items():
        modalities = {modality for group in split["groups"] for modality in group["modalities"]}
        assert "execute" in modalities, f"{split_name} lacks execute coverage"

    print(json.dumps({
        "status": "PASS",
        "groups": len(group_to_split),
        "scenarios": len(scenario_to_split),
        "splits": {name: manifest["aggregate_counts"][name] for name in sorted(EXPECTED_SPLITS)},
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
