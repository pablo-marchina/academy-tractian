#!/usr/bin/env python3
"""Full-DEV cardinality wrapper for the frozen E14p epistemic serializer.

Reuses E14p serialize_output() byte-for-byte at the function level and changes
only the structural completeness requirement from six representative calls to
ten calls from five DEV groups x two repeats. No provider, oracle, VALIDATION,
LOCKED_TEST, or semantic-judge rows are read.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
PARENT_PATH = HERE / "e14p_public_epistemic_serialization_guard.py"
SPEC = importlib.util.spec_from_file_location("e14p_targeted_parent_for_full_dev", PARENT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load frozen E14p serializer")
parent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parent)

MANIFEST = Path("research/experiments/e14p-full-dev-five-group-execution-manifest.json")
EXPECTED_GROUPS = ["asset_G501", "asset_C710", "asset_S420", "asset_M208", "asset_M101"]
EXPECTED_REPEATS = 2
EXPECTED_CALLS = 10
PASS_STATUS = "E14P_FULL_DEV_PUBLIC_EPISTEMIC_SERIALIZATION_GUARD_PASS"
FAIL_STATUS = "E14P_FULL_DEV_PUBLIC_EPISTEMIC_SERIALIZATION_GUARD_NEEDS_REVIEW"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_manifest(path: Path) -> None:
    manifest = _load(path)
    if not isinstance(manifest, dict) or manifest.get("experiment_id") != "E14p-full-DEV-five-group":
        raise AssertionError("frozen E14p full-DEV execution manifest required")
    reps = manifest.get("representative_groups")
    if not isinstance(reps, dict) or reps.get("DEV") != EXPECTED_GROUPS or sorted(reps.keys()) != ["DEV"]:
        raise AssertionError("full-DEV group set/order changed")
    repeats = manifest.get("repeats")
    if not isinstance(repeats, dict) or repeats.get("DEV_ACTION_ESCALATION_CALIBRATION") != EXPECTED_REPEATS:
        raise AssertionError("full-DEV repeat count changed")


def run(args: argparse.Namespace) -> dict[str, Any]:
    assert_manifest(args.manifest)
    fixed = _load(args.fixed_output_file)
    split_manifest = _load(args.split_manifest)
    if not isinstance(fixed, dict) or not isinstance(split_manifest, dict):
        raise AssertionError("fixed output and split manifest must be objects")

    transformed = copy.deepcopy(fixed)
    calls = parent.v4.collect_calls(transformed)
    parent.v4.assert_fixed_scope(transformed, calls, split_manifest)

    parsed = 0
    changed_calls = 0
    changed_fields = 0
    decision_changes = 0
    endpoint_changes = 0
    trace_changes = 0
    signature_loss = 0
    signature_gain = 0
    signature_order_changes = 0

    for call in calls:
        output = parent.v4.output_payload(call)
        if not isinstance(output, dict):
            continue
        parsed += 1
        before_decision = parent._decision_signature(output)
        before_rubric = output.get("action_escalation_rubric") if isinstance(output.get("action_escalation_rubric"), dict) else {}
        before_endpoint = before_rubric.get("action_endpoint")
        before_trace = copy.deepcopy(output.get("trace_quality_self_check"))

        serialized, stats = parent.serialize_output(output)
        after_decision = parent._decision_signature(serialized)
        after_rubric = serialized.get("action_escalation_rubric") if isinstance(serialized.get("action_escalation_rubric"), dict) else {}

        decision_changes += int(before_decision != after_decision)
        endpoint_changes += int(before_endpoint != after_rubric.get("action_endpoint"))
        trace_changes += int(before_trace != serialized.get("trace_quality_self_check"))
        changed_fields += int(stats["changed_text_fields"])
        changed_calls += int(stats["changed_text_fields"] > 0)
        signature_loss += int(stats["evidence_public_signature_loss"])
        signature_gain += int(stats["evidence_public_signature_gain"])
        signature_order_changes += int(stats["evidence_public_signature_order_changed"])
        call["parsed_output"] = serialized

    group_counts = Counter(str(call.get("group_id") or "") for call in calls)
    group_cardinality_ok = dict(group_counts) == {group: EXPECTED_REPEATS for group in EXPECTED_GROUPS}
    complete = len(calls) == EXPECTED_CALLS and parsed == EXPECTED_CALLS and group_cardinality_ok
    passed = (
        complete
        and decision_changes == 0
        and endpoint_changes == 0
        and trace_changes == 0
        and signature_loss == 0
        and signature_gain == 0
        and signature_order_changes == 0
    )
    status = PASS_STATUS if passed else FAIL_STATUS

    transformed["report_version"] = "e14p-full-dev-public-epistemic-serialization-guard-v1"
    transformed["status"] = status
    transformed["e14p_full_dev_epistemic_serialization"] = {
        "parent_capture_status": fixed.get("status"),
        "provider_calls_made": 0,
        "fixed_calls_consumed": len(calls),
        "parsed_outputs": parsed,
        "required_dev_groups": len(EXPECTED_GROUPS),
        "observed_dev_groups": len(group_counts),
        "repeats_per_group": EXPECTED_REPEATS,
        "each_group_exactly_two_calls": group_cardinality_ok,
        "complete_fixed_transform": complete,
        "calls_changed": changed_calls,
        "changed_text_fields": changed_fields,
        "decision_action_escalation_semantic_changes": decision_changes,
        "action_endpoint_changes": endpoint_changes,
        "trace_quality_self_check_changes": trace_changes,
        "evidence_public_signature_loss": signature_loss,
        "evidence_public_signature_gain": signature_gain,
        "evidence_public_signature_order_changes": signature_order_changes,
        "serializer_function_reused_from_targeted_E14p_without_edits": True,
        "task_world_facts_added_by_serializer": False,
        "private_oracle_used": False,
        "private_scorer_rows_used": False,
        "semantic_judge_rows_used": False,
        "validation_feedback_used": False,
        "locked_test_used": False,
        "validation_gate_authorized": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(transformed, indent=2), encoding="utf-8")
    return {
        "status": status,
        **transformed["e14p_full_dev_epistemic_serialization"],
        "raw_outputs_printed": False,
        "claim_text_printed": False,
        "identifiers_printed": False,
        "private_paths_printed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-output-file", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, default=Path("research/frozen/benchmark-split-v1.json"))
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == PASS_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
