#!/usr/bin/env python3
"""Provider-free structural self-checks for the frozen Qwen synthetic judge runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
RUNNER_PATH = HERE / "e9_v4_2_qwen36_27b_synthetic_judge_runner.py"
SPEC = importlib.util.spec_from_file_location("e9_v42_qwen_runner", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load Qwen synthetic judge runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def run() -> dict[str, object]:
    suite = {
        "suite_version": runner.EXPECTED_SUITE_VERSION,
        "cases": [
            {
                "case_id": f"S{i:02d}",
                "visible_case": {"asset": {"status": "active"}},
                "claim": "The asset is active.",
                "expected_claim_type": "factual_assertion",
                "expected_support_label": "SUPPORTED",
            }
            for i in range(1, runner.EXPECTED_CASES + 1)
        ],
    }
    suite["cases"][-1]["public_contract_fact"] = "A public endpoint exists."

    provider_cases = runner.build_provider_cases(suite)
    if len(provider_cases) != runner.EXPECTED_CASES:
        raise AssertionError("provider case count changed")
    if any("expected_claim_type" in row or "expected_support_label" in row for row in provider_cases):
        raise AssertionError("synthetic gold labels leaked into provider cases")
    if "public_contract_fact" not in provider_cases[-1]:
        raise AssertionError("explicit public contract fact must be preserved")

    request = runner.build_request_payload(provider_cases)
    if request.get("model") != runner.MODEL:
        raise AssertionError("judge model drifted")
    if request.get("temperature") != 0 or request.get("reasoning_effort") != "none":
        raise AssertionError("frozen deterministic judge settings drifted")
    if request.get("response_format") != {"type": "json_object"}:
        raise AssertionError("Qwen judge must use JSON Object Mode")
    if request.get("max_completion_tokens") != 2048:
        raise AssertionError("completion budget drifted")

    serialized_messages = json.dumps(request.get("messages"), ensure_ascii=False)
    if "expected_claim_type" in serialized_messages or "expected_support_label" in serialized_messages:
        raise AssertionError("gold fields leaked into serialized provider request")

    expected_ids = [row["case_id"] for row in provider_cases]
    perfect_payload = {
        "results": [
            {
                "case_id": case_id,
                "claim_type": "factual_assertion",
                "support_label": "SUPPORTED",
            }
            for case_id in expected_ids
        ]
    }
    clean = runner.validate_judge_payload(perfect_payload, expected_ids)
    if len(clean) != runner.EXPECTED_CASES:
        raise AssertionError("valid complete judge payload rejected")

    failures_rejected = 0
    malformed = [
        {"extra": [], "results": perfect_payload["results"]},
        {"results": perfect_payload["results"][:-1]},
        {"results": perfect_payload["results"] + [perfect_payload["results"][0]]},
        {"results": [{**perfect_payload["results"][0], "support_label": "MAYBE"}] + perfect_payload["results"][1:]},
        {"results": [{**perfect_payload["results"][0], "rationale": "not allowed"}] + perfect_payload["results"][1:]},
    ]
    for payload in malformed:
        try:
            runner.validate_judge_payload(payload, expected_ids)
        except AssertionError:
            failures_rejected += 1
    if failures_rejected != len(malformed):
        raise AssertionError("runner accepted malformed/incomplete judge output")

    operational = runner._operational_summary(
        "E9_V4_2_QWEN_SYNTHETIC_JUDGE_OPERATIONAL_FAILURE", 429, "rate_limit"
    )
    if operational["reliability_metrics_authorized"] is not False:
        raise AssertionError("operational failure must not authorize reliability metrics")
    if operational["real_dev_packet_read"] is not False:
        raise AssertionError("synthetic runner must never read real DEV packet")

    return {
        "status": "E9_V4_2_QWEN_SYNTHETIC_JUDGE_RUNNER_SELF_CHECK_PASS",
        "model_frozen": runner.MODEL,
        "synthetic_cases_frozen": runner.EXPECTED_CASES,
        "gold_labels_stripped_before_provider": True,
        "single_json_object_request_contract": True,
        "complete_shape_validation": True,
        "malformed_contract_cases_rejected": failures_rejected,
        "operational_failure_does_not_authorize_reliability": True,
        "provider_call_made": False,
        "real_dev_packet_read": False,
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
