#!/usr/bin/env python3
"""P12-C4 evaluator-side deterministic scoring only.

Scientific boundary:
- consumes exactly the already-frozen 144 C4 factorial outputs;
- uses the frozen E9 evaluator v4.1 deterministic scoring semantics;
- requires exact unique ticket alignment to evaluator-side private oracle rows;
- performs zero provider/model/network calls;
- performs zero bootstrap, LOGO, slice, semantic or independent/blind analysis;
- never serializes private expected-path text or private endpoint lists;
- does not authorize the next statistical gate by itself.

This runner intentionally does not define how the private oracle is provisioned.
That evaluator-side custody/handoff must be frozen separately before execution.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FREEZE = ROOT / "research/results/p12-c4-complete-packet-freeze-2026-08-26.json"
ACTIVATION = ROOT / "research/experiments/p12-c2-exposed-pool-activation-eligibility-v1.json"
EVALUATOR_V41 = ROOT / "scripts/research/e9_evaluator_side_scorer_v4_1.py"

EXPECTED_BLOBS = {
    "research/results/p12-c4-complete-packet-freeze-2026-08-26.json": "03b7d5a27ffdec9173e25bdf47377858bf6aeb30",
    "research/experiments/p12-c2-exposed-pool-activation-eligibility-v1.json": "96c38036411365bb2f64c5df85f9eafc31c6901e",
    "scripts/research/e9_evaluator_side_scorer_v4_1.py": "b33afab0b3bfc9b81037a5391f49d286ef0d7c35",
    "scripts/research/e9_evaluator_side_scorer_v4.py": "63145e6fe14d7dd9b90d5567ffca6aa54ced933f",
    "research/e2/tool_registry.py": "97e15fa24bfe865a1cd3a7b9798365f1d3325c8b",
    "research/e2/models.py": "b4a17ab686d93f51d7055174c1bc688c0af58647",
    "scripts/research/p12_c2_factorial_score.py": "dc20be4896ff023989ee6deb012ad440c39ec531",
}

EXPECTED_FIXED_SHA256 = "0d8df31e28e19ad3a23cf78c976daacdded4dbe995db3740d9126317182b9d37"
EXPECTED_COMMON_PARENT_FREEZE_HASH = "45ae5ed8860721350db98457c44e41c587c23b710f917c9ceb66c69a901c123e"
EXPECTED_EXPERIMENT_ID = "P12-C4-PROSPECTIVE-EXPOSED-POOL"
EXPECTED_ARMS = ["A00", "A10", "A01", "A11"]
EXPECTED_FACTORS = {
    "A00": {"evidence": "E0", "safety": "S0"},
    "A10": {"evidence": "E1", "safety": "S0"},
    "A01": {"evidence": "E0", "safety": "S1"},
    "A11": {"evidence": "E1", "safety": "S1"},
}
EXPECTED_PARENTS = 36
EXPECTED_OUTPUTS = 144

PROVIDER_CREDENTIAL_ENVS = (
    "NVIDIA_API_KEY",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "CEREBRAS_API_KEY",
    "OPENROUTER_API_KEY",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def bytes_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_no_provider_credentials() -> None:
    present = sorted(name for name in PROVIDER_CREDENTIAL_ENVS if os.getenv(name))
    if present:
        raise AssertionError(f"provider credential(s) present in evaluator-side scoring environment: {present}")


def verify_frozen_sources() -> None:
    for rel, expected in EXPECTED_BLOBS.items():
        path = ROOT / rel
        if not path.is_file():
            raise AssertionError(f"missing frozen scoring source: {rel}")
        actual = git_blob_sha(path)
        if actual != expected:
            raise AssertionError(f"frozen scoring source mismatch: {rel}: {actual} != {expected}")


def verify_freeze() -> dict[str, Any]:
    freeze = load_json(FREEZE)
    if freeze.get("schema_version") != "p12-c4-complete-packet-freeze-v1":
        raise AssertionError("C4 freeze schema changed")
    if freeze.get("experiment_id") != EXPECTED_EXPERIMENT_ID:
        raise AssertionError("C4 freeze experiment changed")
    if freeze.get("status") != "FROZEN_COMPLETE_C4_PACKET":
        raise AssertionError("C4 packet is not frozen complete")

    scientific = freeze.get("scientific_state") or {}
    if scientific.get("complete_packet_frozen") is not True:
        raise AssertionError("C4 complete packet is not frozen")
    if scientific.get("partial_packet") is not False:
        raise AssertionError("partial C4 packet cannot be scored")
    if int(scientific.get("fresh_common_parent_count") or 0) != EXPECTED_PARENTS:
        raise AssertionError("C4 fresh parent count changed")
    if int(scientific.get("fixed_arm_output_count") or 0) != EXPECTED_OUTPUTS:
        raise AssertionError("C4 fixed output count changed")

    local = freeze.get("local_factorial_expansion") or {}
    files = local.get("artifact_files") or {}
    fixed = files.get("fixed-factorial-outputs.json") or {}
    if local.get("status") != "PASS_144_OF_144_LOCAL_ARM_OUTPUTS":
        raise AssertionError("C4 local factorial expansion is not complete")
    if int(local.get("artifact_id") or 0) != 9629510247:
        raise AssertionError("C4 fixed-output artifact id changed")
    if local.get("artifact_digest") != "sha256:8b9a07355c96372ead4841ec6dc9b2338ba75a6455209fad1b97f621fbe31a58":
        raise AssertionError("C4 fixed-output artifact digest changed")
    if fixed.get("sha256") != EXPECTED_FIXED_SHA256:
        raise AssertionError("C4 fixed-output file hash changed in freeze")
    if local.get("common_parent_freeze_hash") != EXPECTED_COMMON_PARENT_FREEZE_HASH:
        raise AssertionError("C4 common-parent freeze hash changed")

    boundary = freeze.get("access_and_execution_boundary_at_freeze") or {}
    expected_zero = (
        "provider_calls_during_local_expansion",
        "arm_specific_provider_calls",
        "private_oracle_accesses",
        "fresh_blind_accesses",
        "legacy_locked_test_accesses",
    )
    for key in expected_zero:
        if int(boundary.get(key) or 0) != 0:
            raise AssertionError(f"C4 freeze boundary changed: {key}")
    if boundary.get("deterministic_private_scoring_executed") is not False:
        raise AssertionError("C4 deterministic scoring was already marked executed at packet freeze")
    if boundary.get("bootstrap_executed") is not False:
        raise AssertionError("bootstrap was already marked executed at packet freeze")

    auth = freeze.get("post_freeze_authorization") or {}
    if auth.get("deterministic_private_scoring_authorized") is not True:
        raise AssertionError("deterministic private scoring is not authorized")
    if auth.get("bootstrap_authorized_before_deterministic_scoring_completes") is not False:
        raise AssertionError("bootstrap boundary changed")
    if auth.get("fresh_blind_authorized") is not False or auth.get("legacy_locked_test_authorized") is not False:
        raise AssertionError("independent/locked partition authorization changed")
    if int(auth.get("provider_calls_authorized") or 0) != 0:
        raise AssertionError("provider calls are not allowed during deterministic scoring")
    if freeze.get("next_gate") != "DETERMINISTIC_SCORING":
        raise AssertionError("C4 freeze no longer points to deterministic scoring")
    return freeze


def verify_fixed_packet(path: Path, activation: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if bytes_sha256(path) != EXPECTED_FIXED_SHA256:
        raise AssertionError("fixed-factorial-outputs.json bytes differ from frozen artifact")

    fixed = load_json(path)
    if fixed.get("schema_version") != "p12-c4-fixed-factorial-outputs-v1":
        raise AssertionError("C4 fixed output schema changed")
    if fixed.get("status") != "PASS_144_OF_144_LOCAL_ARM_OUTPUTS":
        raise AssertionError("C4 fixed output packet is not complete")
    if fixed.get("experiment_id") != EXPECTED_EXPERIMENT_ID:
        raise AssertionError("C4 fixed output experiment changed")
    if fixed.get("partition") != "EXPOSED_POOL":
        raise AssertionError("C4 scoring may consume EXPOSED_POOL only")
    if fixed.get("participating_arms") != EXPECTED_ARMS:
        raise AssertionError("C4 arm ordering/set changed")
    if fixed.get("factorial_semantics") != EXPECTED_FACTORS:
        raise AssertionError("C4 factorial semantics changed")
    if int(fixed.get("common_parent_count") or 0) != EXPECTED_PARENTS:
        raise AssertionError("C4 common parent count changed")
    if int(fixed.get("fixed_arm_output_count") or 0) != EXPECTED_OUTPUTS:
        raise AssertionError("C4 fixed arm output count changed")
    if fixed.get("common_parent_freeze_hash") != EXPECTED_COMMON_PARENT_FREEZE_HASH:
        raise AssertionError("C4 common-parent freeze hash changed in packet")

    for key in ("provider_calls", "arm_specific_provider_calls", "private_oracle_accesses", "fresh_blind_accesses", "legacy_locked_test_accesses"):
        if int(fixed.get(key) or 0) != 0:
            raise AssertionError(f"pre-scoring fixed packet access boundary changed: {key}")
    if fixed.get("deterministic_private_scoring_executed") is not False:
        raise AssertionError("fixed packet already marks deterministic scoring executed")
    if fixed.get("bootstrap_executed") is not False:
        raise AssertionError("fixed packet already marks bootstrap executed")

    mapping = activation.get("exposed_pool_mapping")
    if not isinstance(mapping, list) or len(mapping) != 12:
        raise AssertionError("activation exposed-pool mapping changed")
    mapping_by_ticket = {str(row["ticket_id"]): row for row in mapping}
    if len(mapping_by_ticket) != 12:
        raise AssertionError("activation ticket mapping is not unique")

    calls = fixed.get("calls")
    if not isinstance(calls, list) or len(calls) != EXPECTED_OUTPUTS:
        raise AssertionError("C4 fixed packet must contain exactly 144 calls")

    per_parent: dict[str, list[dict[str, Any]]] = {}
    for call in calls:
        if not isinstance(call, dict):
            raise AssertionError("C4 fixed call is not an object")
        parent_id = str(call.get("parent_id"))
        per_parent.setdefault(parent_id, []).append(call)

        arm = str(call.get("arm"))
        if arm not in EXPECTED_ARMS:
            raise AssertionError(f"unexpected C4 arm: {arm}")
        factors = EXPECTED_FACTORS[arm]
        if call.get("evidence_factor") != factors["evidence"] or call.get("safety_factor") != factors["safety"]:
            raise AssertionError(f"factor binding changed for {parent_id}/{arm}")
        if call.get("partition") != "EXPOSED_POOL":
            raise AssertionError(f"non-EXPOSED_POOL call found: {parent_id}/{arm}")

        ticket = str(call.get("ticket_id"))
        mapping_row = mapping_by_ticket.get(ticket)
        if not isinstance(mapping_row, dict):
            raise AssertionError(f"unknown exposed ticket: {ticket}")
        if str(call.get("group_id")) != str(mapping_row.get("group_id")):
            raise AssertionError(f"ticket/group binding changed for {parent_id}/{arm}")
        if str(call.get("scenario_id")) != str(mapping_row.get("scenario_id")):
            raise AssertionError(f"ticket/scenario binding changed for {parent_id}/{arm}")
        if str(call.get("modality")) != str(mapping_row.get("modality")):
            raise AssertionError(f"ticket/modality binding changed for {parent_id}/{arm}")

        parsed = call.get("parsed_output")
        if not isinstance(parsed, dict):
            raise AssertionError(f"parsed output missing for {parent_id}/{arm}")
        if str(call.get("output_sha256")) != stable_hash(parsed):
            raise AssertionError(f"output hash mismatch for {parent_id}/{arm}")

    expected_parent_ids = [f"P{i:02d}" for i in range(1, EXPECTED_PARENTS + 1)]
    if sorted(per_parent) != expected_parent_ids:
        raise AssertionError("C4 parent coverage is not exactly P01..P36")

    for parent_id, rows in per_parent.items():
        if len(rows) != 4 or {str(row["arm"]) for row in rows} != set(EXPECTED_ARMS):
            raise AssertionError(f"incomplete factorial coverage for {parent_id}")
        if len({int(row.get("ordinal")) for row in rows}) != 1:
            raise AssertionError(f"ordinal changed across arms for {parent_id}")
        if len({int(row.get("seed")) for row in rows}) != 1:
            raise AssertionError(f"seed changed across arms for {parent_id}")
        if len({int(row.get("repeat_index")) for row in rows}) != 1:
            raise AssertionError(f"repeat index changed across arms for {parent_id}")
        if len({str(row.get("request_sha256")) for row in rows}) != 1:
            raise AssertionError(f"request hash changed across arms for {parent_id}")
        if len({str(row.get("common_parent_row_sha256")) for row in rows}) != 1:
            raise AssertionError(f"common parent row changed across arms for {parent_id}")
        if len({str(row.get("common_parent_output_sha256")) for row in rows}) != 1:
            raise AssertionError(f"common parent output changed across arms for {parent_id}")

    return fixed, calls


def exact_unique_ticket_oracle(evaluator_v41: Any, oracle_payload: Any, ticket_id: str) -> dict[str, Any]:
    # This is the exact P12-C2 deterministic alignment rule, separated from the
    # historical monolithic scorer so no bootstrap/LOGO/slice code is executed.
    matches = [
        row for row in evaluator_v41.v4.expected_path_rows(oracle_payload)
        if isinstance(row, dict) and row.get("ticket_id") == ticket_id
    ]
    if len(matches) != 1:
        raise AssertionError(f"exact ticket oracle alignment requires one row for {ticket_id}; got {len(matches)}")
    oracle = evaluator_v41.v4._normalize_expected_row(matches[0])
    if oracle.get("alignment_status") != evaluator_v41.v4.ALIGNMENT_UNIQUE:
        raise AssertionError(f"exact ticket oracle normalization failed for {ticket_id}")
    if int(oracle.get("unrecognized_expected_steps") or 0) != 0:
        raise AssertionError(f"expected-step normalization incomplete for {ticket_id}")
    return oracle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-outputs", type=Path, required=True)
    parser.add_argument("--oracle-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    verify_no_provider_credentials()
    verify_frozen_sources()
    freeze = verify_freeze()

    activation = load_json(ACTIVATION)
    if activation.get("status") != "ACTIVATION_ELIGIBILITY_PASS":
        raise AssertionError("frozen P12-C2 activation is no longer PASS")
    if activation.get("factorial_arms") != EXPECTED_FACTORS:
        raise AssertionError("frozen factorial arm semantics changed")

    _fixed, calls = verify_fixed_packet(args.fixed_outputs, activation)
    if not args.oracle_file.is_file():
        raise AssertionError("authorized evaluator-side oracle file is missing")

    evaluator_v41 = load_module("p12_c4_frozen_evaluator_v41", EVALUATOR_V41)
    oracle_payload = load_json(args.oracle_file)

    rows: list[dict[str, Any]] = []
    for call in calls:
        ticket = str(call["ticket_id"])
        group = str(call["group_id"])
        oracle = exact_unique_ticket_oracle(evaluator_v41, oracle_payload, ticket)
        score = evaluator_v41.score_call({"group_id": group, "parsed_output": call["parsed_output"]}, oracle)
        if score.get("scoreable") is not True:
            raise AssertionError(f"unscoreable fixed output for {call['parent_id']}/{call['arm']}: {score.get('reason')}")
        rows.append({
            "parent_id": str(call["parent_id"]),
            "ordinal": int(call["ordinal"]),
            "arm": str(call["arm"]),
            "group_id": group,
            "scenario_id": str(call["scenario_id"]),
            "ticket_id": ticket,
            "modality": str(call["modality"]),
            "seed": int(call["seed"]),
            "repeat_index": int(call["repeat_index"]),
            "request_sha256": str(call["request_sha256"]),
            "common_parent_row_sha256": str(call["common_parent_row_sha256"]),
            "common_parent_output_sha256": str(call["common_parent_output_sha256"]),
            "fixed_output_sha256": str(call["output_sha256"]),
            "score": score,
        })

    if len(rows) != EXPECTED_OUTPUTS:
        raise AssertionError("deterministic scorer did not produce exactly 144 score rows")
    if any(row["score"].get("scoreable") is not True for row in rows):
        raise AssertionError("one or more C4 deterministic rows are unscoreable")

    summary = {
        "schema_version": "p12-c4-deterministic-private-scoring-rows-v1",
        "status": "PASS_144_OF_144_DETERMINISTIC_SCORES",
        "experiment_id": EXPECTED_EXPERIMENT_ID,
        "partition": "EXPOSED_POOL",
        "participating_arms": EXPECTED_ARMS,
        "fixed_factorial_outputs_scored": EXPECTED_OUTPUTS,
        "scoreable_outputs": EXPECTED_OUTPUTS,
        "common_parent_count": EXPECTED_PARENTS,
        "source_provenance": {
            "packet_freeze_git_blob_sha": EXPECTED_BLOBS["research/results/p12-c4-complete-packet-freeze-2026-08-26.json"],
            "fixed_factorial_outputs_sha256": EXPECTED_FIXED_SHA256,
            "fixed_factorial_artifact_id": int(freeze["local_factorial_expansion"]["artifact_id"]),
            "fixed_factorial_artifact_digest": str(freeze["local_factorial_expansion"]["artifact_digest"]),
            "common_parent_freeze_hash": EXPECTED_COMMON_PARENT_FREEZE_HASH,
            "activation_git_blob_sha": EXPECTED_BLOBS["research/experiments/p12-c2-exposed-pool-activation-eligibility-v1.json"],
            "evaluator_v4_1_git_blob_sha": EXPECTED_BLOBS["scripts/research/e9_evaluator_side_scorer_v4_1.py"],
            "evaluator_v4_git_blob_sha": EXPECTED_BLOBS["scripts/research/e9_evaluator_side_scorer_v4.py"],
            "tool_registry_git_blob_sha": EXPECTED_BLOBS["research/e2/tool_registry.py"],
            "e2_models_git_blob_sha": EXPECTED_BLOBS["research/e2/models.py"],
            "historical_c2_scorer_semantic_reference_git_blob_sha": EXPECTED_BLOBS["scripts/research/p12_c2_factorial_score.py"],
        },
        "scoring_semantics": {
            "evaluator": "E9 evaluator v4.1 deterministic score_call",
            "oracle_alignment": "EXACT_UNIQUE_TICKET_ID",
            "group_union_fallback": False,
            "candidate_outputs_fixed_before_private_scoring": True,
            "private_oracle_loaded_evaluator_side": True,
            "private_oracle_rows_serialized": False,
            "private_expected_path_text_serialized": False,
            "private_endpoint_names_serialized": False,
        },
        "execution_boundaries": {
            "provider_credentials_present": False,
            "provider_calls": 0,
            "model_calls": 0,
            "network_io": 0,
            "candidate_private_oracle_accesses": 0,
            "fresh_blind_accesses": 0,
            "legacy_locked_test_accesses": 0,
            "bootstrap_executed": False,
            "logo_executed": False,
            "slice_analysis_executed": False,
            "semantic_stage_executed": False,
            "independent_validation_executed": False,
        },
        "rows": rows,
        "automatic_preferred_state": False,
        "architecture_frozen": False,
        "production_readiness_claim": False,
        "next_required_transition": "FREEZE_AND_INDEPENDENTLY_VALIDATE_DETERMINISTIC_SCORING_RESULT",
        "next_statistical_gate_authorized_by_this_runner": False,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": summary["status"],
        "fixed_factorial_outputs_scored": EXPECTED_OUTPUTS,
        "scoreable_outputs": EXPECTED_OUTPUTS,
        "private_rows_printed": False,
        "bootstrap_executed": False,
        "next_statistical_gate_authorized": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
