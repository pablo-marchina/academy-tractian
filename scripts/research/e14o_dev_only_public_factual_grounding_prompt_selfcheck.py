#!/usr/bin/env python3
"""Oracle-free structural self-check for E14o factual-grounding prompt candidate."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
RUNNER_PATH = HERE / "e14o_dev_only_public_factual_grounding_prompt.py"
SPEC = importlib.util.spec_from_file_location("e14o_selfcheck_runner", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load E14o runner")
e14o = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(e14o)


def main() -> int:
    e14o.run_self_checks()

    original = e14o.e10b.STRICT_E10B_SYSTEM_PROMPT
    effective = e14o.effective_system_prompt()
    assert original == e14o.e10b.STRICT_E10B_SYSTEM_PROMPT
    assert effective != original
    assert effective.startswith(original)
    assert effective.count(e14o.PROMPT_MARKER) == 1

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "capture.json"
        lock = e14o._consume_real_attempt(out)
        assert lock.exists()
        payload = json.loads(lock.read_text(encoding="utf-8"))
        assert payload["experiment_id"] == "E14o"
        assert payload["status"] == "REAL_CAPTURE_ATTEMPT_CONSUMED"
        assert payload["rerun_allowed"] is False
        assert payload["contains_raw_output"] is False
        assert payload["contains_private_oracle"] is False
        assert payload["contains_private_scorer_rows"] is False

        blocked = False
        try:
            e14o._consume_real_attempt(out)
        except AssertionError:
            blocked = True
        assert blocked, "second real attempt must be blocked by the local attempt lock"

    print(json.dumps({
        "status": "E14O_PUBLIC_FACTUAL_GROUNDING_STRUCTURAL_SELFCHECK_PASS",
        "prompt_marker_exactly_once": True,
        "parent_prompt_mutated_by_builder": False,
        "manifest_frozen": True,
        "single_intervention": True,
        "attempt_lock_blocks_second_capture": True,
        "provider_calls_made": 0,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
