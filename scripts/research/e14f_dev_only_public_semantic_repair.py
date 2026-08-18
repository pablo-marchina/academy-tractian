#!/usr/bin/env python3
"""E14f DEV-only conditional public semantic-consistency repair.

E14f inherits E14e. The initial GPT-OSS call and all post-model policies remain
unchanged. For a parseable initial draft only, E14f runs a deterministic public
consistency check. If and only if one of the preregistered contradiction codes
is present, the same model gets one repair call containing the original visible
prompt, its own first draft, and the public reason codes.

No private oracle, scorer row, VALIDATION feedback, or LOCKED_TEST material is
available to the repair pass. The repair is upstream of E14c/E14d/E14e and the
unchanged E10e/E10g/E11/E14 post-model policies.
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
E14E_PATH = HERE / "e14e_dev_only_explicit_current_handoff_semantics.py"
SEMANTICS_PATH = HERE / "e14f_public_semantic_consistency.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


e14e = load_module("e14e_parent_for_e14f", E14E_PATH)
semantics = load_module("e14f_semantics", SEMANTICS_PATH)
e10b = e14e.e14d.e14c.e14.e10b
base = e10b.base

E14F_MANIFEST = Path("research/experiments/e14f-dev-only-public-semantic-repair-manifest.json")


def _parse_model_json(raw: str) -> dict[str, Any] | None:
    parsed = base.extract_json_object(raw)
    return parsed if isinstance(parsed, dict) else None


def _semantic_repair_meta(
    *,
    triggered: bool,
    violations: tuple[str, ...] = (),
    repair_call_count: int = 0,
    repair_response_parseable: bool | None = None,
    residual_violations: tuple[str, ...] = (),
    dry_run_repair: bool = False,
) -> dict[str, Any]:
    return {
        "enabled": True,
        "triggered": triggered,
        "violation_codes": list(violations),
        "repair_call_count": repair_call_count,
        "repair_response_parseable": repair_response_parseable,
        "residual_violation_codes": list(residual_violations),
        "dry_run_repair": dry_run_repair,
        "max_repair_calls_per_draft": 1,
        "uses_original_visible_prompt": True,
        "uses_model_own_draft": True,
        "uses_public_consistency_codes_only": True,
        "uses_private_oracle": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    }


def _wrap_provider_meta(meta: dict[str, Any] | None, repair_meta: dict[str, Any]) -> dict[str, Any]:
    result = dict(meta or {})
    result["e14f_semantic_repair"] = repair_meta
    return result


def make_semantic_repair_call_model(
    original_call_model: Callable[[str, int, bool, dict[str, Any], int], tuple[str, dict[str, Any]]]
):
    def semantic_repair_call_model(
        prompt: str,
        timeout: int,
        dry_run: bool,
        packet: dict[str, Any],
        repeat_index: int,
    ) -> tuple[str, dict[str, Any]]:
        raw, initial_meta = original_call_model(prompt, timeout, dry_run, packet, repeat_index)
        draft = _parse_model_json(raw)
        if draft is None:
            return raw, _wrap_provider_meta(
                initial_meta,
                _semantic_repair_meta(triggered=False, repair_response_parseable=None),
            )

        violations = semantics.public_semantic_violations(draft)
        if not violations:
            return raw, _wrap_provider_meta(
                initial_meta,
                _semantic_repair_meta(triggered=False, repair_response_parseable=True),
            )

        if dry_run:
            repaired = semantics.dry_repair_output(draft, violations)
            residual = semantics.public_semantic_violations(repaired)
            return json.dumps(repaired), _wrap_provider_meta(
                initial_meta,
                _semantic_repair_meta(
                    triggered=True,
                    violations=violations,
                    repair_call_count=1,
                    repair_response_parseable=True,
                    residual_violations=residual,
                    dry_run_repair=True,
                ),
            )

        # Keep provider pacing conservative for the conditional second call.
        delay = float(os.getenv("E14F_REPAIR_DELAY_SECONDS", os.getenv("E8_BETWEEN_CALL_DELAY_SECONDS", "0")))
        if delay > 0:
            time.sleep(delay)

        repair_prompt = semantics.build_repair_prompt(prompt, draft, violations)
        repaired_raw, repair_provider_meta = original_call_model(
            repair_prompt,
            timeout,
            False,
            packet,
            repeat_index,
        )
        repaired = _parse_model_json(repaired_raw)
        residual = semantics.public_semantic_violations(repaired) if repaired is not None else ()
        return repaired_raw, _wrap_provider_meta(
            repair_provider_meta,
            _semantic_repair_meta(
                triggered=True,
                violations=violations,
                repair_call_count=1,
                repair_response_parseable=repaired is not None,
                residual_violations=residual,
                dry_run_repair=False,
            ),
        )

    return semantic_repair_call_model


def _capture_semantic_repair_stats(summary: dict[str, Any]) -> dict[str, Any]:
    stage = summary.get("dev_action_escalation_calibration")
    calls = stage.get("calls", []) if isinstance(stage, dict) else []
    trigger_codes: Counter[str] = Counter()
    residual_codes: Counter[str] = Counter()
    total = 0
    triggered = 0
    repair_calls = 0
    parseable_repairs = 0
    residual_calls = 0

    allow = set(semantics.PUBLIC_VIOLATION_CODES)
    for call in calls:
        if not isinstance(call, dict):
            continue
        provider_meta = call.get("provider_meta")
        repair = provider_meta.get("e14f_semantic_repair") if isinstance(provider_meta, dict) else None
        if not isinstance(repair, dict):
            continue
        total += 1
        is_triggered = repair.get("triggered") is True
        triggered += int(is_triggered)
        repair_calls += int(repair.get("repair_call_count") or 0)
        parseable_repairs += int(repair.get("repair_response_parseable") is True and is_triggered)
        residual = [str(x) for x in repair.get("residual_violation_codes") or [] if str(x) in allow]
        residual_calls += int(bool(residual))
        for code in repair.get("violation_codes") or []:
            code = str(code)
            trigger_codes[code if code in allow else "other_public_violation"] += 1
        for code in residual:
            residual_codes[code] += 1

    return {
        "enabled": True,
        "change_scope": "conditional_public_semantic_consistency_repair_before_guards_only",
        "calls_with_repair_metadata": total,
        "triggered_calls": triggered,
        "repair_calls": repair_calls,
        "trigger_violation_code_counts": dict(sorted(trigger_codes.items())),
        "parseable_repair_responses": parseable_repairs,
        "calls_with_residual_public_violations": residual_calls,
        "residual_violation_code_counts": dict(sorted(residual_codes.items())),
        "max_repair_calls_per_draft": 1,
        "initial_prompt_changed": False,
        "always_on_prompt_expansion": False,
        "post_model_guard_policy_changed": False,
        "private_oracle_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    original_call_model = e10b.call_model
    e10b.call_model = make_semantic_repair_call_model(original_call_model)
    try:
        summary = e14e.run(args)
    finally:
        e10b.call_model = original_call_model

    parent_status = summary.get("status")
    capture_pass = parent_status == "E14E_DEV_ONLY_EXPLICIT_CURRENT_HANDOFF_SEMANTICS_CAPTURE_PASS"
    summary["report_version"] = "e14f-dev-only-public-semantic-repair-v1"
    summary["status"] = (
        "E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS"
        if capture_pass
        else "E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_NEEDS_REVIEW"
    )
    summary["parent_e14e_capture_status"] = parent_status
    summary["e14f_public_semantic_repair"] = _capture_semantic_repair_stats(summary)
    summary["e14f_candidate"] = {
        "parent_gate": "E14",
        "comparison_anchor": "E14e_same_gpt_oss_settings",
        "change_class": "conditional_public_semantic_consistency_repair_before_guards_only",
        "initial_prompt_changed": False,
        "conditional_second_call_only": True,
        "same_model_provider_temperature_reasoning_and_json_mode": True,
        "max_repair_calls_per_draft": 1,
        "e14c_action_endpoint_canonicalization_preserved": True,
        "e14d_public_evidence_resource_canonicalization_preserved": True,
        "e14e_explicit_current_handoff_semantics_preserved": True,
        "e10e_policy_changed": False,
        "e10g_policy_changed": False,
        "e11_policy_changed": False,
        "e14_selective_reprocess_policy_changed": False,
        "thresholds_changed": False,
        "scorer_changed": False,
        "acceptance_thresholds_changed": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "private_oracle_used_by_model_or_repair": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_self_checks() -> None:
    e14e.run_self_checks()
    semantics.run_self_checks()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=E14F_MANIFEST)
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
    boundary = summary.get("selective_reprocess_authorization_boundary", {})
    print(json.dumps({
        "status": summary["status"],
        "total_calls": summary.get("aggregate_metrics", {}).get("total_calls"),
        "parsed_model_outputs_available": summary.get("aggregate_metrics", {}).get("parsed_model_outputs_available"),
        "scoreable_calls": summary.get("aggregate_metrics", {}).get("scoreable_calls"),
        "validation_ran": summary.get("scope", {}).get("validation_ran"),
        "dry_run": summary.get("dry_run"),
        "completeness_pass": completeness.get("passed"),
        "retry_count": completeness.get("retry_count"),
        "repair_count": completeness.get("repair_count"),
        "semantic_repair_triggered_calls": repair.get("triggered_calls"),
        "semantic_repair_calls": repair.get("repair_calls"),
        "semantic_repair_residual_violation_calls": repair.get("calls_with_residual_public_violations"),
        "target_reprocess_outputs_checked": boundary.get("target_reprocess_outputs_checked"),
        "authorized_target_reprocess_outputs": boundary.get("authorized_target_reprocess_outputs"),
        "blocked_target_reprocess_outputs": boundary.get("blocked_target_reprocess_outputs"),
    }, indent=2))
    return 0 if summary["status"] == "E14F_DEV_ONLY_PUBLIC_SEMANTIC_REPAIR_CAPTURE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
