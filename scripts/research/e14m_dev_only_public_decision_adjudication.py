#!/usr/bin/env python3
"""E14m DEV-only conditional public decision adjudication candidate.

E14m inherits the operational E14l stack and changes one thing only: after the
unchanged initial model draft, a second same-model public adjudication call may
run if and only if the first parseable draft matches the preregistered fully
conservative collapse shape. The adjudicator sees only the original visible
prompt, the model's own draft, and public endpoint/safety semantics.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).parent
E14L_PATH = HERE / "e14l_dev_only_120b_medium_reasoning_strict_4096.py"
ADJUDICATION_PATH = HERE / "e14m_public_decision_adjudication.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14l = load_module("e14l_parent_for_e14m", E14L_PATH)
adjudication = load_module("e14m_adjudication", ADJUDICATION_PATH)
e14f = e14l.e14k.e14f
e10b = e14f.e10b
base = e10b.base

E14M_MANIFEST = Path("research/experiments/e14m-dev-only-public-decision-adjudication-manifest.json")
REQUIRED_ADJUDICATION_DELAY_SECONDS = 25.0
MAX_ADJUDICATION_CALLS_PER_INITIAL_DRAFT = 1


def _parse_model_json(raw: str) -> dict[str, Any] | None:
    parsed = base.extract_json_object(raw)
    return parsed if isinstance(parsed, dict) else None


def _adjudication_delay(*, dry_run: bool) -> float:
    if dry_run:
        return 0.0
    value = os.getenv("E14M_ADJUDICATION_DELAY_SECONDS", os.getenv("E14F_REPAIR_DELAY_SECONDS", "25"))
    delay = float(value)
    if delay != REQUIRED_ADJUDICATION_DELAY_SECONDS:
        raise AssertionError("E14m requires E14M_ADJUDICATION_DELAY_SECONDS=25 for real execution")
    return delay


def _meta(
    *,
    triggered: bool,
    additional_call_count: int,
    adjudication_parseable: bool | None,
    preserved_initial: bool,
    fallback_reason: str | None,
    final_matches_collapse_shape: bool | None,
) -> dict[str, Any]:
    return {
        "enabled": True,
        "triggered": triggered,
        "additional_call_count": additional_call_count,
        "adjudication_parseable": adjudication_parseable,
        "preserved_initial": preserved_initial,
        "fallback_reason": fallback_reason,
        "final_matches_collapse_shape": final_matches_collapse_shape,
        "max_additional_calls_per_initial_draft": MAX_ADJUDICATION_CALLS_PER_INITIAL_DRAFT,
        "trigger_uses_model_own_draft_only": True,
        "uses_original_visible_prompt": True,
        "uses_model_own_first_draft": True,
        "uses_public_contract_only": True,
        "uses_private_oracle": False,
        "uses_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    }


def _wrap_provider_meta(provider_meta: dict[str, Any] | None, adjudication_meta: dict[str, Any]) -> dict[str, Any]:
    result = dict(provider_meta or {})
    result["e14m_public_decision_adjudication"] = adjudication_meta
    return result


def make_adjudicating_call_model(
    original_call_model: Callable[[str, int, bool, dict[str, Any], int], tuple[str, dict[str, Any]]],
    trace: list[dict[str, Any]],
):
    def adjudicating_call_model(
        prompt: str,
        timeout: int,
        dry_run: bool,
        packet: dict[str, Any],
        repeat_index: int,
    ) -> tuple[str, dict[str, Any]]:
        # E14f may make its own second repair call. E14m must not recursively
        # adjudicate that repair response; the candidate allows at most one
        # adjudication call per initial draft.
        if adjudication.is_e14f_repair_prompt(prompt):
            return original_call_model(prompt, timeout, dry_run, packet, repeat_index)

        initial_raw, initial_provider_meta = original_call_model(prompt, timeout, dry_run, packet, repeat_index)
        initial_draft = _parse_model_json(initial_raw)
        triggered = adjudication.is_public_conservative_collapse_draft(initial_draft)

        if not triggered:
            trace.append({
                "triggered": False,
                "additional_call_count": 0,
                "adjudication_parseable": None,
                "preserved_initial": False,
                "fallback_reason": None,
                "final_matches_collapse_shape": adjudication.is_public_conservative_collapse_draft(initial_draft),
            })
            return initial_raw, _wrap_provider_meta(
                initial_provider_meta,
                _meta(
                    triggered=False,
                    additional_call_count=0,
                    adjudication_parseable=None,
                    preserved_initial=False,
                    fallback_reason=None,
                    final_matches_collapse_shape=adjudication.is_public_conservative_collapse_draft(initial_draft),
                ),
            )

        assert initial_draft is not None
        adjudication_prompt = adjudication.build_adjudication_prompt(prompt, initial_draft)
        delay = _adjudication_delay(dry_run=dry_run)
        if delay > 0:
            time.sleep(delay)

        try:
            adjudicated_raw, adjudicated_provider_meta = original_call_model(
                adjudication_prompt,
                timeout,
                dry_run,
                packet,
                repeat_index,
            )
        except Exception:  # noqa: BLE001 - preregistered operational fallback, raw error not persisted here
            trace.append({
                "triggered": True,
                "additional_call_count": 1,
                "adjudication_parseable": False,
                "preserved_initial": True,
                "fallback_reason": "provider_exception",
                "final_matches_collapse_shape": True,
            })
            return initial_raw, _wrap_provider_meta(
                initial_provider_meta,
                _meta(
                    triggered=True,
                    additional_call_count=1,
                    adjudication_parseable=False,
                    preserved_initial=True,
                    fallback_reason="provider_exception",
                    final_matches_collapse_shape=True,
                ),
            )

        adjudicated = _parse_model_json(adjudicated_raw)
        if adjudicated is None:
            trace.append({
                "triggered": True,
                "additional_call_count": 1,
                "adjudication_parseable": False,
                "preserved_initial": True,
                "fallback_reason": "unparseable_adjudication",
                "final_matches_collapse_shape": True,
            })
            return initial_raw, _wrap_provider_meta(
                initial_provider_meta,
                _meta(
                    triggered=True,
                    additional_call_count=1,
                    adjudication_parseable=False,
                    preserved_initial=True,
                    fallback_reason="unparseable_adjudication",
                    final_matches_collapse_shape=True,
                ),
            )

        final_collapse = adjudication.is_public_conservative_collapse_draft(adjudicated)
        trace.append({
            "triggered": True,
            "additional_call_count": 1,
            "adjudication_parseable": True,
            "preserved_initial": False,
            "fallback_reason": None,
            "final_matches_collapse_shape": final_collapse,
        })
        return adjudicated_raw, _wrap_provider_meta(
            adjudicated_provider_meta,
            _meta(
                triggered=True,
                additional_call_count=1,
                adjudication_parseable=True,
                preserved_initial=False,
                fallback_reason=None,
                final_matches_collapse_shape=final_collapse,
            ),
        )

    return adjudicating_call_model


def _aggregate_trace(trace: list[dict[str, Any]]) -> dict[str, Any]:
    fallbacks: Counter[str] = Counter()
    triggered = 0
    additional = 0
    parseable = 0
    preserved = 0
    final_collapse = 0
    for row in trace:
        triggered += int(row.get("triggered") is True)
        additional += int(row.get("additional_call_count") or 0)
        parseable += int(row.get("adjudication_parseable") is True)
        preserved += int(row.get("preserved_initial") is True)
        final_collapse += int(row.get("final_matches_collapse_shape") is True)
        reason = row.get("fallback_reason")
        if reason:
            fallbacks[str(reason)] += 1
    return {
        "enabled": True,
        "change_scope": "conditional_public_semantic_decision_adjudication_only",
        "initial_drafts_observed": len(trace),
        "triggered_calls": triggered,
        "additional_adjudication_calls": additional,
        "parseable_adjudication_responses": parseable,
        "preserved_initial_drafts": preserved,
        "fallback_reason_counts": dict(sorted(fallbacks.items())),
        "final_outputs_matching_preregistered_collapse_shape_before_downstream_guards": final_collapse,
        "max_additional_calls_per_initial_draft": MAX_ADJUDICATION_CALLS_PER_INITIAL_DRAFT,
        "same_model": True,
        "same_provider": True,
        "same_response_schema": True,
        "same_completion_budget": True,
        "same_reasoning_effort": True,
        "initial_prompt_changed": False,
        "e14f_semantic_repair_changed": False,
        "post_model_policy_changed": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
    }


def assert_frozen_configuration(*, dry_run: bool) -> None:
    e14l.assert_frozen_configuration(dry_run=dry_run)
    if not dry_run:
        _adjudication_delay(dry_run=False)


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_frozen_configuration(dry_run=args.dry_run)
    e14l.schema.run_self_checks()
    adjudication.run_self_checks()

    trace: list[dict[str, Any]] = []
    original_call_model = e10b.call_model
    e10b.call_model = make_adjudicating_call_model(original_call_model, trace)
    try:
        # E14l supplies the frozen provider/model/schema/budget stack. Its E14f
        # layer then wraps this E14m call_model, so adjudication happens before
        # unchanged E14f public consistency repair and all downstream guards.
        summary = e14l.run(args)
    finally:
        e10b.call_model = original_call_model

    parent_status = summary.get("status")
    capture_pass = parent_status == "E14L_DEV_ONLY_120B_MEDIUM_REASONING_STRICT_4096_CAPTURE_PASS"
    summary["report_version"] = "e14m-dev-only-public-decision-adjudication-v1"
    summary["status"] = (
        "E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION_CAPTURE_PASS"
        if capture_pass
        else "E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14l_capture_status"] = parent_status
    summary["e14m_public_decision_adjudication"] = _aggregate_trace(trace)
    summary["e14m_candidate"] = {
        "change_class": "conditional_public_semantic_decision_adjudication_only",
        "trigger_source": "model_own_parseable_draft_only",
        "model_changed": False,
        "reasoning_effort_changed": False,
        "response_format_changed": False,
        "schema_changed": False,
        "completion_budget_changed": False,
        "temperature_changed": False,
        "initial_prompt_changed": False,
        "semantic_repair_changed": False,
        "post_model_policy_changed": False,
        "scorer_changed": False,
        "acceptance_thresholds_changed": False,
        "uses_private_oracle": False,
        "uses_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _wrapper_self_check() -> None:
    collapsed = {
        "decision_class": "investigate_only",
        "evidence_plan": ["GET /assets/asset-selfcheck"],
        "should_take_action_now": False,
        "requires_human_escalation": False,
        "proposed_next_step": "Collect more evidence.",
        "risk_notes": "Uncertainty remains.",
        "trace_quality_self_check": {"uses_only_visible_packet": True, "no_locked_test": True, "no_gold_claim": True},
        "action_escalation_rubric": {
            "needs_more_evidence": True,
            "safe_to_act": False,
            "action_endpoint": "none",
            "needs_human_escalation": False,
            "calibration_reason": "More evidence is needed.",
        },
    }
    adjudicated = json.loads(json.dumps(collapsed))
    adjudicated["decision_class"] = "escalation_candidate"
    adjudicated["requires_human_escalation"] = True
    adjudicated["action_escalation_rubric"]["needs_human_escalation"] = True
    adjudicated["action_escalation_rubric"]["action_endpoint"] = "POST /analyses/analysis-selfcheck/request-specialist"
    adjudicated["proposed_next_step"] = "Request specialist review for the visible high-impact diagnostic uncertainty."
    adjudicated["action_escalation_rubric"]["calibration_reason"] = "Visible diagnostic uncertainty is material enough to require specialist handling now."

    calls: list[str] = []
    def fake(prompt: str, timeout: int, dry_run: bool, packet: dict[str, Any], repeat_index: int):
        calls.append(prompt)
        payload = adjudicated if "PUBLIC DECISION ADJUDICATION PASS" in prompt else collapsed
        return json.dumps(payload), {"model": "fake"}

    trace: list[dict[str, Any]] = []
    saved = os.environ.get("E14M_ADJUDICATION_DELAY_SECONDS")
    os.environ["E14M_ADJUDICATION_DELAY_SECONDS"] = "25"
    try:
        wrapper = make_adjudicating_call_model(fake, trace)
        # dry_run=True suppresses structural sleep but still exercises the
        # second semantic call using the fake provider.
        raw, _ = wrapper("VISIBLE ORIGINAL PROMPT", 1, True, {}, 0)
    finally:
        if saved is None:
            os.environ.pop("E14M_ADJUDICATION_DELAY_SECONDS", None)
        else:
            os.environ["E14M_ADJUDICATION_DELAY_SECONDS"] = saved
    parsed = _parse_model_json(raw)
    if len(calls) != 2 or not isinstance(parsed, dict) or parsed.get("decision_class") != "escalation_candidate":
        raise AssertionError("E14m wrapper must make exactly one adjudication call for the collapse shape")
    if len(trace) != 1 or trace[0].get("triggered") is not True or trace[0].get("additional_call_count") != 1:
        raise AssertionError("E14m wrapper trace must record one triggered adjudication")

    repair_calls: list[str] = []
    def fake_repair(prompt: str, timeout: int, dry_run: bool, packet: dict[str, Any], repeat_index: int):
        repair_calls.append(prompt)
        return json.dumps(collapsed), {"model": "fake"}
    repair_wrapper = make_adjudicating_call_model(fake_repair, [])
    repair_wrapper("x PUBLIC SEMANTIC CONSISTENCY REPAIR PASS y", 1, True, {}, 0)
    if len(repair_calls) != 1:
        raise AssertionError("E14m must not retrigger inside an E14f repair call")


def run_self_checks() -> None:
    e14l.run_self_checks()
    adjudication.run_self_checks()
    assert_frozen_configuration(dry_run=True)
    _wrapper_self_check()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14M_MANIFEST)
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
    repair = summary.get("e14f_public_semantic_repair", {})
    adjudication_stats = summary.get("e14m_public_decision_adjudication", {})
    config = summary.get("e14l_reasoning_configuration", {})
    print(json.dumps({
        "status": summary["status"],
        "model": config.get("model"),
        "reasoning_effort": config.get("reasoning_effort"),
        "response_format": config.get("response_format"),
        "strict": config.get("strict"),
        "max_completion_tokens": config.get("max_completion_tokens"),
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "adjudication_triggered_calls": adjudication_stats.get("triggered_calls"),
        "additional_adjudication_calls": adjudication_stats.get("additional_adjudication_calls"),
        "parseable_adjudication_responses": adjudication_stats.get("parseable_adjudication_responses"),
        "preserved_initial_drafts": adjudication_stats.get("preserved_initial_drafts"),
        "final_collapse_shape_calls": adjudication_stats.get("final_outputs_matching_preregistered_collapse_shape_before_downstream_guards"),
        "semantic_repair_triggered_calls": repair.get("triggered_calls"),
        "semantic_repair_calls": repair.get("repair_calls"),
        "semantic_repair_residual_violation_calls": repair.get("calls_with_residual_public_violations"),
    }, indent=2))
    return 0 if summary["status"] == "E14M_DEV_ONLY_PUBLIC_DECISION_ADJUDICATION_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
