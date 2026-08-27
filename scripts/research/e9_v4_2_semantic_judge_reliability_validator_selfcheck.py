#!/usr/bin/env python3
"""Oracle-free self-check for E9 v4.2 semantic judge reliability validation."""

from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
VALIDATOR_PATH = HERE / "e9_v4_2_semantic_judge_reliability_validator.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_validator", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load semantic judge reliability validator")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

SUITE_PATH = Path("research/frozen/e9-v4-2-semantic-groundedness-synthetic-suite-v1.json")


def _args(path: Path) -> argparse.Namespace:
    return argparse.Namespace(synthetic_suite=SUITE_PATH, judge_results=path)


def run() -> dict[str, object]:
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    cases = suite["cases"]

    perfect = {
        "results": [
            {
                "case_id": row["case_id"],
                "claim_type": row["expected_claim_type"],
                "support_label": row["expected_support_label"],
                "support_source_type": "synthetic_visible_packet",
                "brief_rationale": "synthetic self-check",
            }
            for row in cases
        ]
    }

    with tempfile.TemporaryDirectory() as tmp:
        perfect_path = Path(tmp) / "perfect.json"
        perfect_path.write_text(json.dumps(perfect), encoding="utf-8")
        perfect_result = validator.run(_args(perfect_path))
        if perfect_result["status"] != "E9_V4_2_SEMANTIC_JUDGE_RELIABILITY_PASS":
            raise AssertionError("perfect synthetic labels must pass reliability")

        dangerous = json.loads(json.dumps(perfect))
        target = next(
            row for row in dangerous["results"]
            if next(case for case in cases if case["case_id"] == row["case_id"])["expected_support_label"]
            in {"CONTRADICTED", "NOT_SUPPORTED"}
        )
        target["support_label"] = "SUPPORTED"
        dangerous_path = Path(tmp) / "dangerous.json"
        dangerous_path.write_text(json.dumps(dangerous), encoding="utf-8")
        dangerous_result = validator.run(_args(dangerous_path))
        if dangerous_result["status"] != "E9_V4_2_SEMANTIC_JUDGE_RELIABILITY_FAIL":
            raise AssertionError("a critical false support must fail reliability")
        if dangerous_result["critical_false_support_rate"] <= 0:
            raise AssertionError("critical false support rate must be positive")
        if dangerous_result["judge_authorized_for_real_dev_semantic_measurement"] is not False:
            raise AssertionError("failed judge must not be authorized for real DEV measurement")

    return {
        "status": "E9_V4_2_SEMANTIC_JUDGE_RELIABILITY_VALIDATOR_SELF_CHECK_PASS",
        "frozen_synthetic_cases": len(cases),
        "perfect_labels_pass": True,
        "critical_false_support_fails": True,
        "thresholds_frozen_before_real_labels": True,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation": False,
        "uses_locked_test": False,
    }


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
