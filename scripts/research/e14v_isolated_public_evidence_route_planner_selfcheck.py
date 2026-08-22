#!/usr/bin/env python3
"""Offline structural self-check for E14v."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14v_isolated_public_evidence_route_planner.py"
SPEC = importlib.util.spec_from_file_location("e14v_planner_for_selfcheck", TARGET)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14v planner")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def main() -> int:
    module.run_self_checks()
    print("E14V_ISOLATED_PUBLIC_EVIDENCE_ROUTE_PLANNER_SELFCHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
