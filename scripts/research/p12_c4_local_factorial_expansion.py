#!/usr/bin/env python3
"""P12-C4 provider-free local 2x2 factorial expansion from the frozen 36-parent NVIDIA packet.

Scientific boundary:
- consumes exactly the already-frozen 36 common parents;
- performs zero provider/model calls;
- applies E0 once to the full ordered batch of 36;
- applies E1 per frozen parent;
- applies S0/S1 with the exact P12-C2 candidate implementation;
- requires exactly 144 fixed arm outputs before emitting PASS;
- never reads private oracle, FRESH_BLIND, LEGACY_LOCKED_TEST, or scorer inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = ROOT / "scripts/research/p12_c2_factorial_candidates.py"
ACTIVATION = ROOT / "research/experiments/p12-c2-exposed-pool-activation-eligibility-v1.json"
CASES = ROOT / "research/fixtures/p12-c1-exposed-agent-input-cases-v1.json"
TRIGGER = ROOT / "research/frozen/p12-c4-local-factorial-expansion-trigger-v1.json"

EXPECTED_BLOBS = {
    "scripts/research/p12_c2_factorial_candidates.py": "33fbeec64d65ca666d30a14f9a3c196b6c607bec",
    "research/experiments/p12-c2-exposed-pool-activation-eligibility-v1.json": "96c38036411365bb2f64c5df85f9eafc31c6901e",
    "research/fixtures/p12-c1-exposed-agent-input-cases-v1.json": "f9fef316ab9245de1e36d1d6d787326cde2e27be",
    "research/frozen/p12-c2-public-intent-map-v1.json": "26c666e335d8264fb913c5598cfa6d12b42c6798",
    "scripts/research/p12_c1_evidence_route_candidates.py": "e5d0b3d005ffbd9068d32a094133c0cb7cd8a9f5",
    "scripts/research/e14n_public_identifier_provenance_guard_v1_1.py": "c7c72aaf667debd294fd25fd63dd575467f75da7",
    "scripts/research/e14q_full_dev_public_action_authorization_consistency_guard.py": "3c44e70429872825b1d21032d311137c9d428ebf",
    "scripts/research/e14q2_full_dev_public_route_role_purpose_consistency_guard.py": "a54139f7188b83bb0046050e6f4a6c6372091980",
}
EXPECTED_LIVE = {
    "run_id": 33020748838,
    "artifact_id": 9627504808,
    "artifact_digest": "sha256:f6c7e7c0673cc3030cb83efc2b7acb0f319634aa5cb1ab0ccf2244824c26986e",
    "common_parents_sha256": "9495480b7d1dd8f1339d3fe4cf30fb365964b4bf14991dd32f6c91b2feb47827",
    "request_ledger_sha256": "4564c4204a72668e7accec163579c28aa9ea410e52d9425a24eb4646c5299e03",
    "execution_result_sha256": "81efae2c2010e3c152891a461931d73b6ef25e100b7216e72eb51b21c7718866",
}
ARMS = {
    "A00": {"evidence": "E0", "safety": "S0"},
    "A10": {"evidence": "E1", "safety": "S0"},
    "A01": {"evidence": "E0", "safety": "S1"},
    "A11": {"evidence": "E1", "safety": "S1"},
}
EXPECTED_PARENTS = 36
EXPECTED_OUTPUTS = 144


def canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canon(value).encode("utf-8")).hexdigest()


def bytes_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise AssertionError(f"{path}:{lineno}: row is not an object")
        rows.append(value)
    return rows


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_frozen_sources() -> None:
    for rel, expected in EXPECTED_BLOBS.items():
        path = ROOT / rel
        if not path.is_file():
            raise AssertionError(f"missing frozen source: {rel}")
        actual = git_blob_sha(path)
        if actual != expected:
            raise AssertionError(f"frozen source blob mismatch: {rel}: {actual} != {expected}")


def verify_trigger() -> dict[str, Any]:
    trigger = load_json(TRIGGER)
    expected = {
        "schema_version": "p12-c4-local-factorial-expansion-trigger-v1",
        "experiment_id": "P12-C4-PROSPECTIVE-EXPOSED-POOL",
        "consume_live_run_id": EXPECTED_LIVE["run_id"],
        "consume_live_artifact_id": EXPECTED_LIVE["artifact_id"],
        "consume_live_artifact_digest": EXPECTED_LIVE["artifact_digest"],
        "required_common_parents": 36,
        "required_fixed_arm_outputs": 144,
        "provider_calls_authorized": 0,
        "private_scoring_authorized": False,
        "fresh_blind_authorized": False,
        "legacy_locked_test_authorized": False,
        "next_gate_on_pass": "FREEZE_COMPLETE_C4_PACKET",
    }
    for key, value in expected.items():
        if trigger.get(key) != value:
            raise AssertionError(f"trigger mismatch: {key}")
    if trigger.get("factorial_arms") != ARMS:
        raise AssertionError("trigger factorial arm semantics changed")
    return trigger


def visible_cases() -> dict[str, dict[str, Any]]:
    raw = load_json(CASES)
    if not isinstance(raw, list):
        raise AssertionError("visible cases fixture must be a list")
    out: dict[str, dict[str, Any]] = {}
    for case in raw:
        if not isinstance(case, dict) or not case.get("ticket_id"):
            raise AssertionError("malformed visible case")
        ticket = str(case["ticket_id"])
        if ticket in out:
            raise AssertionError(f"duplicate visible ticket: {ticket}")
        out[ticket] = case
    return out


def verify_live_packet(live_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    parents_path = live_root / "common-parents.jsonl"
    ledger_path = live_root / "request-ledger.jsonl"
    result_path = live_root / "execution-result.json"
    for path in (parents_path, ledger_path, result_path):
        if not path.is_file():
            raise AssertionError(f"missing live evidence file: {path}")

    if bytes_sha256(parents_path) != EXPECTED_LIVE["common_parents_sha256"]:
        raise AssertionError("common parent bytes changed")
    if bytes_sha256(ledger_path) != EXPECTED_LIVE["request_ledger_sha256"]:
        raise AssertionError("request ledger bytes changed")
    if bytes_sha256(result_path) != EXPECTED_LIVE["execution_result_sha256"]:
        raise AssertionError("execution result bytes changed")

    result = load_json(result_path)
    exact_result = {
        "status": "PASS_36_OF_36_FRESH_COMMON_PARENTS",
        "provider_request_attempts": 36,
        "valid_common_parents": 36,
        "automatic_retries": 0,
        "warming_requests": 0,
        "provider_fallbacks": 0,
        "model_fallbacks": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "local_arm_expansion_authorized": True,
        "expected_local_arm_outputs": 144,
        "private_scoring_authorized": False,
        "bootstrap_authorized": False,
        "rerun_allowed": False,
        "resume_allowed": False,
        "next_gate": "C4_144_OF_144_LOCAL_ARM_OUTPUTS",
        "common_parents_sha256": EXPECTED_LIVE["common_parents_sha256"],
        "request_ledger_sha256": EXPECTED_LIVE["request_ledger_sha256"],
    }
    for key, value in exact_result.items():
        if result.get(key) != value:
            raise AssertionError(f"live execution-result mismatch: {key}")

    parents = load_jsonl(parents_path)
    ledger = load_jsonl(ledger_path)
    if len(parents) != EXPECTED_PARENTS or len(ledger) != EXPECTED_PARENTS:
        raise AssertionError("live packet is not exactly 36/36")

    expected_ids = [f"P{i:02d}" for i in range(1, 37)]
    if [str(r.get("parent_id")) for r in parents] != expected_ids:
        raise AssertionError("common-parent ordering changed")
    if [str(r.get("parent_id")) for r in ledger] != expected_ids:
        raise AssertionError("ledger ordering changed")
    if [int(r.get("ordinal")) for r in parents] != list(range(1, 37)):
        raise AssertionError("common-parent ordinals changed")
    if [int(r.get("ordinal")) for r in ledger] != list(range(1, 37)):
        raise AssertionError("ledger ordinals changed")
    if len({int(r["seed"]) for r in parents}) != 36:
        raise AssertionError("common-parent seeds are not unique")
    if len({str(r["request_sha256"]) for r in parents}) != 36:
        raise AssertionError("common-parent requests are not unique")
    if [str(r["request_sha256"]) for r in parents] != [str(r["request_sha256"]) for r in ledger]:
        raise AssertionError("parent/ledger request hashes disagree")
    if any(int(r.get("http_status", -1)) != 200 for r in ledger):
        raise AssertionError("non-200 request present in frozen ledger")
    if any(str(r.get("provider_model")) != "openai/gpt-oss-120b" for r in parents):
        raise AssertionError("unexpected provider model in frozen parents")
    if any(str(r.get("finish_reason")) != "stop" for r in parents):
        raise AssertionError("non-stop parent present")

    return parents, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-root", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, required=True)
    args = parser.parse_args()

    verify_frozen_sources()
    trigger = verify_trigger()
    parents, live_result = verify_live_packet(args.live_root)

    activation = load_json(ACTIVATION)
    if activation.get("status") != "ACTIVATION_ELIGIBILITY_PASS":
        raise AssertionError("C2 activation is no longer PASS")
    if activation.get("factorial_arms") != ARMS:
        raise AssertionError("C2 activation factorial semantics changed")
    mapping = activation.get("exposed_pool_mapping")
    if not isinstance(mapping, list) or len(mapping) != 12:
        raise AssertionError("C2 exposed-pool mapping changed")
    mapping_by_ticket = {str(x["ticket_id"]): x for x in mapping}
    if len(mapping_by_ticket) != 12:
        raise AssertionError("duplicate ticket in exposed-pool mapping")

    case_by_ticket = visible_cases()
    candidate = load_module("p12_c4_frozen_factorial_candidates", CANDIDATES)

    records: list[dict[str, Any]] = []
    for idx, parent in enumerate(parents):
        ticket = str(parent["ticket_id"])
        group_id = str(parent["group_id"])
        if ticket not in case_by_ticket or ticket not in mapping_by_ticket:
            raise AssertionError(f"unknown public ticket in parent {parent['parent_id']}")
        case = case_by_ticket[ticket]
        mp = mapping_by_ticket[ticket]
        if str(case.get("asset_id")) != group_id or str(mp.get("group_id")) != group_id:
            raise AssertionError(f"ticket/group binding changed for {parent['parent_id']}")
        if int(parent.get("repeat_index")) not in (0, 1, 2):
            raise AssertionError("repeat index outside frozen 0..2")
        records.append({
            "stable_index": idx,
            "parent_id": str(parent["parent_id"]),
            "ordinal": int(parent["ordinal"]),
            "ticket_id": ticket,
            "group_id": group_id,
            "scenario_id": str(mp["scenario_id"]),
            "modality": str(mp["modality"]),
            "seed": int(parent["seed"]),
            "repeat_index": int(parent["repeat_index"]),
            "request_sha256": str(parent["request_sha256"]),
            "parent_row_sha256": stable_hash(parent),
            "parent_output_sha256": stable_hash(parent["parsed_output"]),
            "visible_case": case,
            "parent_output": parent["parsed_output"],
        })

    e0_inputs = [{"visible_case": r["visible_case"], "output": r["parent_output"]} for r in records]
    e0_outputs, e0_meta = candidate.apply_e0_batch(e0_inputs)
    if len(e0_outputs) != EXPECTED_PARENTS:
        raise AssertionError("E0 did not return exactly 36 outputs")

    e1_pairs = [candidate.apply_e1(r["visible_case"], r["parent_output"]) for r in records]
    e1_outputs = [x[0] for x in e1_pairs]
    e1_meta = [x[1] for x in e1_pairs]

    calls: list[dict[str, Any]] = []
    s1_failure_counts = {"A01": 0, "A11": 0}
    for idx, record in enumerate(records):
        a00, a00_meta = candidate.apply_s0(e0_outputs[idx])
        a10, a10_meta = candidate.apply_s0(e1_outputs[idx])
        a01_base, _ = candidate.apply_s0(e0_outputs[idx])
        a01, a01_meta = candidate.apply_s1(a01_base, record["visible_case"])
        a11_base, _ = candidate.apply_s0(e1_outputs[idx])
        a11, a11_meta = candidate.apply_s1(a11_base, record["visible_case"])
        arm_outputs = {"A00": (a00, a00_meta), "A10": (a10, a10_meta), "A01": (a01, a01_meta), "A11": (a11, a11_meta)}
        for arm, (output, safety_meta) in arm_outputs.items():
            if arm in s1_failure_counts and safety_meta.get("certificate_failure_reason") is not None:
                s1_failure_counts[arm] += 1
            calls.append({
                "arm": arm,
                "evidence_factor": ARMS[arm]["evidence"],
                "safety_factor": ARMS[arm]["safety"],
                "parent_id": record["parent_id"],
                "ordinal": record["ordinal"],
                "ticket_id": record["ticket_id"],
                "group_id": record["group_id"],
                "scenario_id": record["scenario_id"],
                "modality": record["modality"],
                "partition": "EXPOSED_POOL",
                "seed": record["seed"],
                "repeat_index": record["repeat_index"],
                "request_sha256": record["request_sha256"],
                "common_parent_row_sha256": record["parent_row_sha256"],
                "common_parent_output_sha256": record["parent_output_sha256"],
                "parsed_output": output,
                "output_sha256": stable_hash(output),
                "arm_transform_meta": safety_meta,
            })

    if len(calls) != EXPECTED_OUTPUTS:
        raise AssertionError("expected exactly 144 fixed factorial outputs")

    expected_arm_set = set(ARMS)
    per_parent: dict[str, list[dict[str, Any]]] = {}
    for call in calls:
        per_parent.setdefault(str(call["parent_id"]), []).append(call)
    if sorted(per_parent) != [f"P{i:02d}" for i in range(1, 37)]:
        raise AssertionError("144 packet parent coverage changed")
    for parent_id, rows in per_parent.items():
        if len(rows) != 4 or {str(x["arm"]) for x in rows} != expected_arm_set:
            raise AssertionError(f"incomplete arm coverage for {parent_id}")
        if len({str(x["common_parent_row_sha256"]) for x in rows}) != 1:
            raise AssertionError(f"common parent changed across arms for {parent_id}")
        if len({str(x["common_parent_output_sha256"]) for x in rows}) != 1:
            raise AssertionError(f"common parent output changed across arms for {parent_id}")

    common_parent_freeze_hash = stable_hash([{"parent_id": r["parent_id"], "row_sha256": r["parent_row_sha256"], "output_sha256": r["parent_output_sha256"]} for r in records])
    packet = {
        "schema_version": "p12-c4-fixed-factorial-outputs-v1",
        "status": "PASS_144_OF_144_LOCAL_ARM_OUTPUTS",
        "experiment_id": "P12-C4-PROSPECTIVE-EXPOSED-POOL",
        "partition": "EXPOSED_POOL",
        "participating_arms": ["A00", "A10", "A01", "A11"],
        "factorial_semantics": ARMS,
        "live_source": EXPECTED_LIVE,
        "common_parent_count": 36,
        "fixed_arm_output_count": 144,
        "common_parent_freeze_hash": common_parent_freeze_hash,
        "e0_policy_meta": e0_meta,
        "e1_policy_meta": {"candidate_id": candidate.E1_ID, "output_count": len(e1_outputs), "max_final_reads_per_output": candidate.MAX_FINAL_READS, "added_reads_total": sum(int(x.get("added_read_count") or 0) for x in e1_meta), "private_oracle_used": False},
        "s0_policy_id": candidate.S0_ID,
        "s1_policy_id": candidate.S1_ID,
        "s1_certificate_failure_counts": s1_failure_counts,
        "provider_calls": 0,
        "arm_specific_provider_calls": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "deterministic_private_scoring_executed": False,
        "bootstrap_executed": False,
        "calls": calls,
    }

    out_root = args.out_root
    out_root.mkdir(parents=True, exist_ok=True)
    fixed_path = out_root / "fixed-factorial-outputs.json"
    fixed_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    fixed_sha = bytes_sha256(fixed_path)

    result = {
        "schema_version": "p12-c4-local-factorial-expansion-result-v1",
        "status": "PASS_144_OF_144_LOCAL_ARM_OUTPUTS",
        "experiment_id": "P12-C4-PROSPECTIVE-EXPOSED-POOL",
        "live_run_id": EXPECTED_LIVE["run_id"],
        "live_artifact_id": EXPECTED_LIVE["artifact_id"],
        "live_artifact_digest": EXPECTED_LIVE["artifact_digest"],
        "common_parents_sha256": EXPECTED_LIVE["common_parents_sha256"],
        "request_ledger_sha256": EXPECTED_LIVE["request_ledger_sha256"],
        "common_parent_count": 36,
        "fixed_arm_output_count": 144,
        "common_parent_freeze_hash": common_parent_freeze_hash,
        "fixed_factorial_outputs_sha256": fixed_sha,
        "factorial_semantics": ARMS,
        "e0_global_batch_size": 36,
        "e0_global_addition_budget": int(e0_meta.get("global_addition_budget") or 0),
        "e0_additions_total": int(e0_meta.get("additions_total") or 0),
        "e1_output_count": 36,
        "s1_certificate_failure_counts": s1_failure_counts,
        "provider_calls": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "private_scoring_authorized": False,
        "deterministic_private_scoring_executed": False,
        "bootstrap_authorized": False,
        "bootstrap_executed": False,
        "next_gate": "FREEZE_COMPLETE_C4_PACKET",
        "source_git_blobs": EXPECTED_BLOBS,
        "trigger": trigger,
        "live_execution_status": live_result["status"],
    }
    result_path = out_root / "local-expansion-result.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    prefreeze = {
        "schema_version": "p12-c4-complete-packet-prefreeze-v1",
        "status": "READY_TO_FREEZE_COMPLETE_C4_PACKET",
        "experiment_id": "P12-C4-PROSPECTIVE-EXPOSED-POOL",
        "live_parent_packet": {"run_id": EXPECTED_LIVE["run_id"], "artifact_id": EXPECTED_LIVE["artifact_id"], "artifact_digest": EXPECTED_LIVE["artifact_digest"], "common_parents_sha256": EXPECTED_LIVE["common_parents_sha256"], "request_ledger_sha256": EXPECTED_LIVE["request_ledger_sha256"]},
        "local_factorial_packet": {"common_parent_count": 36, "fixed_arm_output_count": 144, "common_parent_freeze_hash": common_parent_freeze_hash, "fixed_factorial_outputs_sha256": fixed_sha},
        "provider_calls_during_local_expansion": 0,
        "private_oracle_accesses": 0,
        "fresh_blind_accesses": 0,
        "legacy_locked_test_accesses": 0,
        "private_scoring_executed": False,
        "bootstrap_executed": False,
        "next_gate": "FREEZE_COMPLETE_C4_PACKET",
    }
    prefreeze_path = out_root / "complete-packet-prefreeze.json"
    prefreeze_path.write_text(json.dumps(prefreeze, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    print("P12_C4_LOCAL_FACTORIAL_144_OF_144_PASS")
    print(json.dumps({"fixed_factorial_outputs_sha256": fixed_sha, "common_parent_freeze_hash": common_parent_freeze_hash, "e0_additions_total": result["e0_additions_total"], "s1_certificate_failure_counts": s1_failure_counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
