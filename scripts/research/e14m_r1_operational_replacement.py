#!/usr/bin/env python3
"""E14m-R1: one preregistered operational replacement capture.

This wrapper does not change the E14m candidate. It exists only to identify the
single replacement capture authorized after the first E14m real run became
non-scoreable because one initial provider call hit a Groq long-window rate
limit. All model, prompt, adjudication, transport, policy, scorer and gate
settings remain the E14m settings.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
E14M_PATH = HERE / "e14m_dev_only_public_decision_adjudication.py"
AMENDMENT = Path("research/experiments/e14m-operational-replacement-r1-amendment.json")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14m = load_module("e14m_parent_for_r1", E14M_PATH)


def _load_amendment() -> dict[str, Any]:
    payload = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("E14m-R1 amendment must be a JSON object")
    if payload.get("amendment_id") != "E14m-R1":
        raise AssertionError("unexpected E14m-R1 amendment id")
    rule = payload.get("replacement_rule")
    if not isinstance(rule, dict) or int(rule.get("replacement_captures_allowed") or 0) != 1:
        raise AssertionError("E14m-R1 must authorize exactly one replacement capture")
    if rule.get("same_candidate_required") is not True:
        raise AssertionError("E14m-R1 must preserve the same candidate")
    return payload


def run(args: argparse.Namespace) -> dict[str, Any]:
    amendment = _load_amendment()
    e14m.assert_frozen_configuration(dry_run=args.dry_run)
    summary = e14m.run(args)
    parent_status = summary.get("status")
    complete = parent_status == "E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION_CAPTURE_PASS"

    summary["report_version"] = "e14m-r1-operational-replacement-v1"
    summary["status"] = (
        "E14M_R1_OPERATIONAL_REPLACEMENT_CAPTURE_PASS"
        if complete
        else "E14M_R1_OPERATIONAL_REPLACEMENT_CAPTURE_NEEDS_REVIEW"
    )
    summary["e14m_r1_operational_replacement"] = {
        "amendment_id": amendment["amendment_id"],
        "replacement_capture_index": 1,
        "replacement_captures_allowed": 1,
        "parent_e14m_status": parent_status,
        "same_candidate": True,
        "model_changed": False,
        "reasoning_effort_changed": False,
        "response_format_changed": False,
        "schema_changed": False,
        "completion_budget_changed": False,
        "temperature_changed": False,
        "pacing_changed": False,
        "transport_retry_policy_changed": False,
        "initial_prompt_changed": False,
        "adjudication_trigger_changed": False,
        "adjudication_prompt_changed": False,
        "semantic_repair_changed": False,
        "post_model_policy_changed": False,
        "scorer_changed": False,
        "acceptance_thresholds_changed": False,
        "first_incomplete_capture_scored": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "if_complete_run_unchanged_e9_exactly_once": True,
        "if_incomplete_stop_without_third_capture": True,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    _load_amendment()
    e14m.run_self_checks()
    e14m.assert_frozen_configuration(dry_run=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("research/experiments/e14m-dev-only-public-decision-adjudication-manifest.json"),
    )
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--agent-input-cases", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--dev-repeats", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        run_self_checks()
    summary = run(args)
    completeness = summary.get("e14_completeness", {})
    adjudication = summary.get("e14m_public_decision_adjudication", {})
    print(json.dumps({
        "status": summary["status"],
        "model": summary.get("e14l_reasoning_configuration", {}).get("model"),
        "reasoning_effort": summary.get("e14l_reasoning_configuration", {}).get("reasoning_effort"),
        "response_format": summary.get("e14l_reasoning_configuration", {}).get("response_format"),
        "strict": summary.get("e14l_reasoning_configuration", {}).get("strict"),
        "max_completion_tokens": summary.get("e14l_reasoning_configuration", {}).get("max_completion_tokens"),
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "adjudication_triggered_calls": adjudication.get("triggered_calls"),
        "additional_adjudication_calls": adjudication.get("additional_adjudication_calls"),
        "parseable_adjudication_responses": adjudication.get("parseable_adjudication_responses"),
        "preserved_initial_drafts": adjudication.get("preserved_initial_drafts"),
        "final_collapse_shape_calls": adjudication.get("final_outputs_matching_preregistered_collapse_shape_before_downstream_guards"),
        "replacement_capture_index": 1,
        "replacement_captures_allowed": 1,
    }, indent=2))
    return 0 if summary["status"] == "E14M_R1_OPERATIONAL_REPLACEMENT_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
