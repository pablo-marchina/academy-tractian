#!/usr/bin/env python3
"""Recursion-safe E10 DEV-only quality capture wrapper.

The first E10 runner monkeypatches the base observation packet builder. This
wrapper preserves the original base packet function and patches only the E10
augmentation function so the dry-run and local runs do not recurse.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

MODULE_PATH = Path(__file__).with_name("e10_dev_only_groq_quality_capture.py")
SPEC = importlib.util.spec_from_file_location("e10_v1", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load e10_dev_only_groq_quality_capture.py")
e10_v1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e10_v1)

_ORIGINAL_OBSERVATION_PACKET = e10_v1.base.observation_packet


def recursion_safe_observation_packet(split_name: str, group_id: str, case_by_asset: dict[str, dict[str, Any]]) -> dict[str, Any]:
    packet = _ORIGINAL_OBSERVATION_PACKET(split_name, group_id, case_by_asset)
    packet["e10_dev_only_quality_policy"] = {
        "iteration_scope": "DEV_ONLY",
        "validation_tuning_forbidden": True,
        "locked_test_forbidden": True,
        "required_evidence_resources": e10_v1.EVIDENCE_RESOURCE_HINTS,
        "supported_action_resources": e10_v1.ACTION_RESOURCE_HINTS,
        "decision_gate": "Do not choose action/escalation unless visible evidence supports it after explicit resource-level evidence acquisition.",
        "insufficient_evidence_rule": "If any required asset, analysis, baseline, quality, RMS, spectrum, permission, or knowledge evidence is missing, choose investigate_only or insufficient_evidence.",
    }
    return packet


def main() -> int:
    e10_v1.e10_observation_packet = recursion_safe_observation_packet
    return e10_v1.main()


if __name__ == "__main__":
    raise SystemExit(main())
