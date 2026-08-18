#!/usr/bin/env python3
"""Sanitized public-output diagnostic for the fixed E14l DEV capture.

This diagnostic reads only the fixed model capture. It does not read the E9
scorer output, private oracle, expected paths, VALIDATION material or LOCKED_TEST.
It reports aggregate distributions of public model fields so the next candidate
can be motivated without inferring any private per-row labels.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ENDPOINT_NORMALIZER_PATH = HERE / "e14c_public_action_endpoint_normalization.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


endpoint_norm = load_module("e14l_public_diag_endpoint_norm", ENDPOINT_NORMALIZER_PATH)


def collect_calls(payload: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "calls" and isinstance(value, list):
                calls.extend(item for item in value if isinstance(item, dict))
            elif isinstance(value, (dict, list)):
                calls.extend(collect_calls(value))
    elif isinstance(payload, list):
        for item in payload:
            calls.extend(collect_calls(item))
    return calls


def bool_label(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "missing_or_non_boolean"


def output_payload(call: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("parsed_output", "model_output", "output", "response"):
        value = call.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.capture.read_text(encoding="utf-8"))
    calls = collect_calls(payload)
    outputs = [output_payload(call) for call in calls]
    outputs = [output for output in outputs if isinstance(output, dict)]

    decisions: Counter[str] = Counter()
    action_flags: Counter[str] = Counter()
    escalation_flags: Counter[str] = Counter()
    needs_more: Counter[str] = Counter()
    safe_to_act: Counter[str] = Counter()
    rubric_human: Counter[str] = Counter()
    endpoints: Counter[str] = Counter()
    joint: Counter[str] = Counter()

    for output in outputs:
        decision = str(output.get("decision_class") or "missing").strip().lower()
        decisions[decision] += 1
        action = bool_label(output.get("should_take_action_now"))
        escalation = bool_label(output.get("requires_human_escalation"))
        action_flags[action] += 1
        escalation_flags[escalation] += 1

        rubric = output.get("action_escalation_rubric")
        rubric = rubric if isinstance(rubric, dict) else {}
        needs = bool_label(rubric.get("needs_more_evidence"))
        safe = bool_label(rubric.get("safe_to_act"))
        human = bool_label(rubric.get("needs_human_escalation"))
        needs_more[needs] += 1
        safe_to_act[safe] += 1
        rubric_human[human] += 1

        canonical = endpoint_norm.canonical_public_endpoint_or_none(rubric.get("action_endpoint"))
        endpoint = canonical or "none_or_unsupported"
        endpoints[endpoint] += 1
        joint[f"decision={decision}|action={action}|escalation={escalation}|endpoint={endpoint}"] += 1

    config = payload.get("e14l_reasoning_configuration") if isinstance(payload, dict) else None
    config = config if isinstance(config, dict) else {}
    result = {
        "status": "E14L_PUBLIC_DECISION_DISTRIBUTION_DIAGNOSTIC",
        "capture_status": payload.get("status") if isinstance(payload, dict) else None,
        "model": config.get("model"),
        "reasoning_effort": config.get("reasoning_effort"),
        "response_format": config.get("response_format"),
        "strict": config.get("strict"),
        "max_completion_tokens": config.get("max_completion_tokens"),
        "total_calls_found": len(calls),
        "parseable_outputs_found": len(outputs),
        "decision_class_histogram": dict(sorted(decisions.items())),
        "should_take_action_now_histogram": dict(sorted(action_flags.items())),
        "requires_human_escalation_histogram": dict(sorted(escalation_flags.items())),
        "rubric_needs_more_evidence_histogram": dict(sorted(needs_more.items())),
        "rubric_safe_to_act_histogram": dict(sorted(safe_to_act.items())),
        "rubric_needs_human_escalation_histogram": dict(sorted(rubric_human.items())),
        "canonical_action_endpoint_histogram": dict(sorted(endpoints.items())),
        "public_joint_decision_action_escalation_endpoint_histogram": dict(sorted(joint.items())),
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "reads_e9_score_file": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
        "infers_private_per_row_labels": False,
        "prints_raw_model_outputs": False,
        "prints_prompts": False,
        "prints_group_ids": False,
        "prints_hashes": False,
        "prints_private_paths": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
