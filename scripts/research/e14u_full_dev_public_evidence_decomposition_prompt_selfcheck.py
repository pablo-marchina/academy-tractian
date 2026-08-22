#!/usr/bin/env python3
"""Public structural checks for E14u. No provider inference or private oracle."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
RUNNER_PATH = HERE / "e14u_full_dev_public_evidence_decomposition_prompt.py"
SPEC = importlib.util.spec_from_file_location("e14u_runner_selfcheck", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14u runner")
e14u = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14u)


def main() -> int:
    e14u.run_self_checks()

    parent_prompt = e14u.BASE_E14O_EFFECTIVE_SYSTEM_PROMPT()
    effective = e14u.effective_system_prompt()
    assert effective.startswith(parent_prompt.rstrip())
    assert effective != parent_prompt
    assert effective.count(e14u.PROMPT_MARKER) == 1

    assert e14u.parent.EXPECTED_CALLS == 10
    assert e14u.parent.EXPECTED_REPEATS == 2
    assert len(e14u.parent.EXPECTED_GROUPS) == 5

    suffix = e14u.EVIDENCE_DECOMPOSITION_SUFFIX
    required_routes = (
        "GET /users/me",
        "GET /assets/{assetId}",
        "GET /assets/{assetId}/analyses",
        "GET /analyses/{analysisId}",
        "GET /assets/{assetId}/baseline",
        "GET /assets/{assetId}/data-quality",
        "GET /assets/{assetId}/rms",
        "GET /assets/{assetId}/spectrum",
        "GET /models/{modelId}",
        "GET /knowledge/search",
        "GET /knowledge/{docId}",
    )
    for route in required_routes:
        assert route in suffix, route

    assert "never emit more than 7 distinct public reads" in suffix
    assert "smallest complete set" in suffix
    assert "generic checklist item" in suffix
    assert "Do not change the existing decision/action/escalation calibration rules" in suffix

    print("E14U_PUBLIC_EVIDENCE_DECOMPOSITION_STRUCTURAL_SELFCHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
