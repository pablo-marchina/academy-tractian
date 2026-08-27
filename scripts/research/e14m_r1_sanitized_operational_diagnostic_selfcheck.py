#!/usr/bin/env python3
"""Oracle-free self-check for the E14m-R1 sanitized diagnostic."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "e14m_r1_sanitized_operational_diagnostic.py"

spec = importlib.util.spec_from_file_location("e14m_r1_diag", TARGET)
if spec is None or spec.loader is None:
    raise RuntimeError("failed to load E14m-R1 diagnostic")
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)


def main() -> int:
    synthetic = {
        "status": "E14M_R1_OPERATIONAL_REPLACEMENT_CAPTURE_NEEDS_REVIEW",
        "report_version": "e14m-r1-operational-replacement-v1",
        "dry_run": False,
        "e14m_r1_operational_replacement": {
            "amendment_id": "E14m-R1",
            "replacement_capture_index": 1,
            "replacement_captures_allowed": 1,
            "same_candidate": True,
        },
        "e14l_reasoning_configuration": {
            "model": "openai/gpt-oss-120b",
            "reasoning_effort": "medium",
            "max_completion_tokens": 4096,
            "response_format": "json_schema",
            "strict": True,
        },
        "dev_action_escalation_calibration": {
            "calls": [
                {
                    "error": "E14_MODEL_CALL_FAILED",
                    "e14_completeness": {
                        "attempt_count": 3,
                        "retry_count": 2,
                        "sanitized_attempt_failures": ["model_call_failed"] * 3,
                        "sanitized_provider_failure_categories": ["rate_limit_long_window"] * 3,
                    },
                }
            ]
        },
    }
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "r1.json"
        path.write_text(json.dumps(synthetic), encoding="utf-8")
        result = diag.run(path)

    assert result["status"] == "E14M_R1_SANITIZED_OPERATIONAL_DIAGNOSTIC"
    assert result["replacement_amendment_id"] == "E14m-R1"
    assert result["replacement_capture_index"] == 1
    assert result["replacement_captures_allowed"] == 1
    assert result["parsed_calls"] == 0
    assert result["missing_final_outputs"] == 1
    assert result["sanitized_provider_failure_category_counts"] == {"rate_limit_long_window": 3}
    assert result["rerun_allowed"] is False
    assert result["quality_scoring_allowed"] is False
    print("E14M_R1_SANITIZED_OPERATIONAL_DIAGNOSTIC_SELF_CHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
