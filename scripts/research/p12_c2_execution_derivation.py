#!/usr/bin/env python3
"""Deterministically derive the P12-C2 runner from the qualified P12-C1 runner.

The parent generation/repair/guard path is retained byte-for-byte except for
experiment identifiers/seeds and the post-parent C0/C1 expansion, which is
replaced by the preregistered E0/E1 x S0/S1 factorial expansion.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
from pathlib import Path

PARENT_SOURCE_SHA256 = "be16ec6d2c33ad68134a0fbf7aa280b4103ee411b01233b6de7a76668e899a50"
DERIVED_SOURCE_SHA256 = "f494eeac56d69cee85609e79d383b150ccc9e1a51a6e2bf61913bf07cef84d59"

OLD_ARMS = '''    if activation.get("participating_arms") != ["C0", "C1"]:\n        raise AssertionError("participating arm set changed")\n    eligibility = activation.get("candidate_eligibility", {})\n    if eligibility.get("C0", {}).get("eligible") is not True or eligibility.get("C1", {}).get("eligible") is not True:\n        raise AssertionError("C0/C1 eligibility changed")\n    if eligibility.get("C2", {}).get("eligible") is not False:\n        raise AssertionError("C2 must remain ineligible in this cycle")\n'''
NEW_ARMS = '''    arms = activation.get("factorial_arms", {})\n    expected_arms = {\n        "A00": {"evidence": "E0", "safety": "S0"},\n        "A10": {"evidence": "E1", "safety": "S0"},\n        "A01": {"evidence": "E0", "safety": "S1"},\n        "A11": {"evidence": "E1", "safety": "S1"},\n    }\n    if arms != expected_arms:\n        raise AssertionError("P12-C2 factorial arm set changed")\n'''

NEW_FACTORIAL_BLOCK = '''    # Freeze all 36 parents before any arm-specific transform.\n    parent_freeze_hash = stable_hash([{"call_id": r["call_id"], "parent_hash": r["parent_hash"]} for r in common_records])\n    e0_inputs = [{"visible_case": r["visible_case"], "output": r["parent_output"]} for r in common_records]\n    e0_outputs, e0_meta = candidates.apply_e0_batch(e0_inputs)\n    e1_pairs = [candidates.apply_e1(r["visible_case"], r["parent_output"]) for r in common_records]\n    e1_outputs = [pair[0] for pair in e1_pairs]\n\n    final_calls: list[dict[str, Any]] = []\n    safety_meta_counts = {"A00": 0, "A10": 0, "A01": 0, "A11": 0}\n    for idx, record in enumerate(common_records):\n        a00, a00_meta = candidates.apply_s0(e0_outputs[idx])\n        a10, a10_meta = candidates.apply_s0(e1_outputs[idx])\n        a01_base, _ = candidates.apply_s0(e0_outputs[idx])\n        a01, a01_meta = candidates.apply_s1(a01_base, record["visible_case"])\n        a11_base, _ = candidates.apply_s0(e1_outputs[idx])\n        a11, a11_meta = candidates.apply_s1(a11_base, record["visible_case"])\n        arm_outputs = {\n            "A00": (a00, {"evidence": "E0", "safety": "S0", "safety_meta": a00_meta}),\n            "A10": (a10, {"evidence": "E1", "safety": "S0", "safety_meta": a10_meta}),\n            "A01": (a01, {"evidence": "E0", "safety": "S1", "safety_meta": a01_meta}),\n            "A11": (a11, {"evidence": "E1", "safety": "S1", "safety_meta": a11_meta}),\n        }\n        for arm, (final_output, meta) in arm_outputs.items():\n            if arm in {"A01", "A11"} and meta["safety_meta"].get("certificate_failure_reason") is not None:\n                safety_meta_counts[arm] += 1\n            final_calls.append({\n                "arm": arm,\n                "evidence_factor": meta["evidence"],\n                "safety_factor": meta["safety"],\n                "call_id": record["call_id"],\n                "group_id": record["group_id"],\n                "scenario_id": record["scenario_id"],\n                "ticket_id": record["ticket_id"],\n                "modality": record["modality"],\n                "source_split": record["source_split"],\n                "partition": "EXPOSED_POOL",\n                "seed": record["seed"],\n                "repeat_index": record["repeat_index"],\n                "common_parent_hash": record["parent_hash"],\n                "parsed_output": final_output,\n                "output_hash": stable_hash(final_output),\n                "arm_transform_meta": meta["safety_meta"],\n            })\n\n    if len(final_calls) != EXPECTED_PARENTS * 4:\n        raise AssertionError("expected exactly 144 fixed factorial outputs")\n    paired: dict[str, set[str]] = {}\n    arm_sets: dict[str, set[str]] = {}\n    for call in final_calls:\n        call_id = str(call["call_id"])\n        paired.setdefault(call_id, set()).add(str(call["common_parent_hash"]))\n        arm_sets.setdefault(call_id, set()).add(str(call["arm"]))\n    expected_arms = {"A00", "A10", "A01", "A11"}\n    if len(paired) != EXPECTED_PARENTS or any(len(values) != 1 for values in paired.values()):\n        raise AssertionError("factorial arms did not preserve one identical common parent per call")\n    if any(values != expected_arms for values in arm_sets.values()):\n        raise AssertionError("factorial arm coverage incomplete for one or more calls")\n\n    fixed = {\n        "schema_version": "p12-c2-fixed-factorial-outputs-v1",\n        "status": PASS,\n        "activation_id": activation["activation_id"],\n        "experiment_id": activation["experiment_id"],\n        "partition": "EXPOSED_POOL",\n        "participating_arms": ["A00", "A10", "A01", "A11"],\n        "common_parent_count": EXPECTED_PARENTS,\n        "fixed_arm_output_count": len(final_calls),\n        "common_parent_freeze_hash": parent_freeze_hash,\n        "e0_policy_meta": e0_meta,\n        "e1_policy_meta": {\n            "candidate_id": candidates.E1_ID,\n            "output_count": len(e1_outputs),\n            "max_final_reads_per_output": candidates.MAX_FINAL_READS,\n            "private_oracle_used": False,\n        },\n        "s0_policy_id": candidates.S0_ID,\n        "s1_policy_id": candidates.S1_ID,\n        "s1_certificate_failure_counts": safety_meta_counts,\n        "candidate_private_oracle_accesses": 0,\n        "fresh_blind_accesses": 0,\n        "legacy_locked_test_accesses": 0,\n        "arm_specific_provider_calls": 0,\n        "fixed_before_private_scoring": True,\n        "calls": final_calls,\n    }\n    args.fixed_outputs.parent.mkdir(parents=True, exist_ok=True)\n    args.fixed_outputs.write_text(json.dumps(fixed, indent=2), encoding="utf-8")\n\n    sanitized.update({\n        "status": "PASS",\n        "common_parent_freeze_hash": parent_freeze_hash,\n        "e0_global_addition_budget": int(e0_meta.get("global_addition_budget") or 0),\n        "e0_additions_total": int(e0_meta.get("additions_total") or 0),\n        "fixed_arm_outputs": len(final_calls),\n        "same_parent_hash_for_all_four_arms": True,\n        "candidate_outputs_fixed_before_private_scoring": True,\n        "s1_certificate_failure_counts": safety_meta_counts,\n    })\n    args.generation_summary.write_text(json.dumps(sanitized, indent=2), encoding="utf-8")\n    return 0'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive(parent: str) -> str:
    if sha256(parent.encode()) != PARENT_SOURCE_SHA256:
        raise AssertionError("qualified P12-C1 parent runner source hash changed")
    replacements = [
        ("Execute the one authorized P12-C1 common-parent C0-vs-C1 cycle.", "Execute one authorized P12-C2 2x2 factorial EXPOSED_POOL cycle."),
        ("from the activation mapping, freezes them in memory/on disk, applies C0/C1 to\nthe exact same parent for every ticket/repetition, then reapplies unchanged\nE14q -> E14q2. No evaluator or private oracle code is invoked here.", "from the activation mapping, freezes them in memory/on disk, then expands the\nexact same parent into E0/E1 x S0/S1 factorial arms. No evaluator or private\noracle code is invoked here."),
        ("p12_c1_evidence_route_candidates.py", "p12_c2_factorial_candidates.py"),
        ("P12_C1_FIXED_CANDIDATE_OUTPUTS_PASS", "P12_C2_FIXED_FACTORIAL_OUTPUTS_PASS"),
        ("P12_C1_FIXED_CANDIDATE_OUTPUTS_NEEDS_REVIEW", "P12_C2_FIXED_FACTORIAL_OUTPUTS_NEEDS_REVIEW"),
        ("P12-C1-ACTIVATION-2026-08-23", "P12-C2-ACTIVATION-2026-08-23"),
        ("ONE_DETERMINISTIC_PAIRED_C0_VS_C1_EXPOSED_POOL_COMMON_PARENT_GENERATION_EVALUATION_CYCLE", "ONE_P12_C2_FACTORIAL_A00_A10_A01_A11_EXPOSED_POOL_COMMON_PARENT_GENERATION_EVALUATION_CYCLE"),
        ("[2026082301, 2026082302, 2026082303]", "[2026082304, 2026082305, 2026082306]"),
        ("P12-C1 provider cycle may not be rerun with github.run_attempt > 1", "P12-C2 provider cycle may not be rerun with github.run_attempt > 1"),
        ("P12-C1 mapping reached a forbidden historical split", "P12-C2 mapping reached a forbidden historical split"),
        ('"schema_version": "p12-c1-common-parent-generation-summary-v1"', '"schema_version": "p12-c2-common-parent-generation-summary-v1"'),
        ('        "c2_provider_calls": 0,\n', '        "arm_specific_provider_calls": 0,\n'),
    ]
    out = parent
    for old, new in replacements:
        if out.count(old) != 1:
            raise AssertionError(f"runner derivation anchor count changed: {old[:80]!r}")
        out = out.replace(old, new)
    if out.count(OLD_ARMS) != 1:
        raise AssertionError("P12-C1 arm eligibility anchor changed")
    out = out.replace(OLD_ARMS, NEW_ARMS)
    start_marker = "    # Freeze all 36 parents before any candidate transform.\n"
    end_marker = '    args.generation_summary.write_text(json.dumps(sanitized, indent=2), encoding="utf-8")\n    return 0'
    if out.count(start_marker) != 1 or out.count(end_marker) != 1:
        raise AssertionError("post-parent transform anchors changed")
    start = out.index(start_marker)
    end = out.index(end_marker, start) + len(end_marker)
    out = out[:start] + NEW_FACTORIAL_BLOCK + out[end:]
    if sha256(out.encode()) != DERIVED_SOURCE_SHA256:
        raise AssertionError("derived P12-C2 runner source hash mismatch")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-gz", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    parent = gzip.decompress(args.parent_gz.read_bytes()).decode("utf-8")
    derived = derive(parent)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(derived, encoding="utf-8")
    print(DERIVED_SOURCE_SHA256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
