#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "research/experiments/p12-c3-capacity-controlled-live-execution-v1.json"
EXPECTED_EXECUTION_ID = "P12-C3-LIVE-CAPACITY-CONTROLLED-2026-08-23"
EXPECTED_EXPERIMENT_ID = "P12-C3_EXPOSED_POOL_CAPACITY_CONTROLLED_FACTORIAL"
EXPECTED_TRIGGER = ROOT / "research/experiments/p12-c3-live-batch-trigger-v1.json"
EXPECTED_ARMS = {
    "A00": {"evidence": "E0", "safety": "S0"},
    "A10": {"evidence": "E1", "safety": "S0"},
    "A01": {"evidence": "E0", "safety": "S1"},
    "A11": {"evidence": "E1", "safety": "S1"},
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected object: {path}")
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode() + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)

    check("schema", manifest.get("schema_version") == "p12-c3-capacity-controlled-live-execution-v1")
    check("execution_id", manifest.get("execution_id") == EXPECTED_EXECUTION_ID)
    check("experiment_id", manifest.get("experiment_id") == EXPECTED_EXPERIMENT_ID)
    check("frozen_ready_not_started", manifest.get("status") == "FROZEN_READY_NOT_STARTED")
    check("execution_frozen", manifest.get("decision_state") == "EXPERIMENT_EXECUTION_FROZEN")
    check("protocol_frozen", manifest.get("protocol_state") == "FROZEN")
    check("activation_pass", manifest.get("activation_state") == "ACTIVATION_ELIGIBILITY_PASS")
    check("activation_authorizes_one", manifest.get("execution_authorized_by_activation") is True and manifest.get("authorized_live_experiments") == 1)
    check("trigger_absent_manifest", manifest.get("live_trigger_present_at_freeze") is False)
    check("trigger_absent_repo", not EXPECTED_TRIGGER.exists())
    check("no_first_provider_call", manifest.get("first_provider_call_occurred_at_freeze") is False)
    check("no_candidate_outcomes", manifest.get("p12_c3_candidate_outcomes_observed_at_freeze") == 0)
    check("no_private_oracle_rows", manifest.get("private_oracle_rows_read_at_freeze") == 0)
    check("no_fresh_blind", manifest.get("fresh_blind_accesses_at_freeze") == 0)
    check("no_locked_test", manifest.get("legacy_locked_test_accesses_at_freeze") == 0)
    check("no_groq_secret_in_self_check", not os.getenv("GROQ_API_KEY"))
    check("private_expected_paths_absent", not (ROOT / "eval/expected-paths.json").exists() and not (ROOT / "private-eval/expected-paths.json").exists())

    pins = manifest.get("source_pins")
    check("source_pins_object", isinstance(pins, dict))
    pin_count = 0
    for key, pin in sorted(pins.items()):
        if not isinstance(pin, dict) or "path" not in pin or "git_blob_sha" not in pin:
            continue
        path = ROOT / str(pin["path"])
        check(f"pin_exists:{key}", path.is_file())
        check(f"pin_blob:{key}", git_blob_sha(path.read_bytes()) == str(pin["git_blob_sha"]))
        pin_count += 1
    check("all_expected_blob_pins_checked", pin_count >= 18)

    live_workflow_pin = pins["live_workflow"]
    live_workflow_path = ROOT / live_workflow_pin["path"]
    live_workflow = live_workflow_path.read_text(encoding="utf-8")
    check("live_workflow_sha256", sha256_bytes(live_workflow_path.read_bytes()) == live_workflow_pin["source_sha256"])
    check("live_workflow_trigger_path_only", "p12-c3-live-batch-trigger-v1.json" in live_workflow)
    check("live_workflow_no_dispatch", "workflow_dispatch:" not in live_workflow)
    check("live_workflow_no_schedule", "schedule:" not in live_workflow)
    check("live_workflow_no_pr_trigger", "pull_request:" not in live_workflow)
    check("live_workflow_no_github_rerun", "github.run_attempt != 1" in live_workflow or "github.run_attempt == 1" in live_workflow)
    check("live_workflow_checkpoint_artifact", "p12-c3-private-checkpoint-latest" in live_workflow)
    check("live_workflow_private_scoring_absent", "p12_c2_factorial_score.py" not in live_workflow and "e9_evaluator_side_scorer_v4_1.py" not in live_workflow)

    base_path = ROOT / pins["checkpoint_runner_base"]["path"]
    fixup_path = ROOT / pins["checkpoint_runner_fixup"]["path"]
    fixup = load_module("p12_c3_live_manifest_fixup_check", fixup_path)
    effective = fixup.derive(base_path.read_text(encoding="utf-8"))
    check("effective_checkpoint_runner_sha256", sha256_bytes(effective.encode()) == pins["effective_checkpoint_runner"]["source_sha256"])

    activation = load_json(ROOT / pins["activation"]["path"])
    batch_map = load_json(ROOT / pins["batch_map"]["path"])
    check("activation_current_pass", activation.get("status") == "ACTIVATION_ELIGIBILITY_PASS" and activation.get("execution_authorized") is True)
    check("activation_same_scope", activation.get("authorized_scope_if_passed") == manifest.get("authorized_scope"))
    check("batch_map_frozen", batch_map.get("status") == "FROZEN")
    batches = batch_map.get("batches") or []
    check("six_batches", len(batches) == 6)
    check("six_parents_each", all(len(b.get("cells") or []) == 6 for b in batches))
    cell_ids = [str(c["cell_id"]) for b in batches for c in b.get("cells") or []]
    check("36_unique_cells", len(cell_ids) == 36 and len(set(cell_ids)) == 36)
    check("batch_order", [b.get("batch_id") for b in batches] == ["B1", "B2", "B3", "B4", "B5", "B6"])
    check("seed_schedule", batch_map.get("seed_schedule") == [2026082307, 2026082308, 2026082309])

    lock = manifest.get("factorial_candidate_lock") or {}
    check("candidate_definitions_unchanged", lock.get("definitions_changed_from_p12_c2") is False)
    for arm, expected in EXPECTED_ARMS.items():
        check(f"candidate_lock:{arm}", lock.get(arm) == expected)
    check("no_group_or_ticket_specific_logic", lock.get("group_specific_logic") is False and lock.get("ticket_specific_logic") is False)
    check("no_p12_c2_parent_reuse", lock.get("p12_c2_partial_parents_reused") is False)

    geometry = manifest.get("scientific_geometry") or {}
    check("geometry_exposed_only", geometry.get("partition") == "EXPOSED_POOL")
    check("geometry_36_to_144", geometry.get("new_common_parent_cells") == 36 and geometry.get("fixed_factorial_outputs_after_completeness") == 144)
    check("geometry_7_groups_11_scenarios_12_tickets", geometry.get("independent_groups") == 7 and geometry.get("scenario_families") == 11 and geometry.get("agent_visible_tickets") == 12)

    capacity = manifest.get("capacity_control") or {}
    check("capacity_30s_delay", capacity.get("minimum_inter_request_delay_seconds") == 30)
    check("capacity_30s_margin", capacity.get("reset_safety_margin_seconds") == 30)
    check("capacity_three_pre_output_attempts", capacity.get("max_pre_output_transport_attempts_per_cell") == 3)
    check("capacity_72h", capacity.get("collection_horizon_hours") == 72)
    check("capacity_fail_closed", capacity.get("if_reset_metadata_required_but_missing") == "FAIL_CLOSED_NO_SHORT_WAIT_GUESS")

    checkpoint = manifest.get("checkpoint_contract") or {}
    check("completed_cells_immutable", checkpoint.get("completed_cells_immutable") is True)
    check("resume_pending_only", checkpoint.get("resume_only_pending_predeclared_cells") is True)
    check("strict_prior_batch_completion", checkpoint.get("later_batch_requires_all_prior_batches_complete") is True)
    check("single_live_concurrency", checkpoint.get("simultaneous_live_batches_allowed") is False)
    check("github_rerun_forbidden", checkpoint.get("github_workflow_rerun_allowed") is False)
    check("public_checkpoint_no_raw_outputs", checkpoint.get("public_checkpoint_contains_raw_outputs") is False)
    check("public_checkpoint_no_private_oracle", checkpoint.get("public_checkpoint_contains_private_oracle") is False)

    gate = manifest.get("completeness_gate_before_private_scoring") or {}
    check("completeness_gate_36", gate.get("common_parents_required") == "36/36")
    check("completeness_gate_144", gate.get("fixed_factorial_outputs_required") == "144/144")
    check("partial_analysis_forbidden", gate.get("partial_factorial_analysis") == "FORBIDDEN" and gate.get("complete_case_only_reinterpretation") == "FORBIDDEN")
    check("private_scoring_between_batches_forbidden", gate.get("private_scoring_between_batches") == "FORBIDDEN")

    evidence = manifest.get("qualification_evidence") or {}
    check("infra_qualification_success", evidence.get("conclusion") == "success")
    check("infra_qualification_zero_provider", evidence.get("provider_calls") == 0)
    check("infra_qualification_36_144", evidence.get("dry_common_parents") == 36 and evidence.get("dry_fixed_arm_outputs") == 144)
    check("infra_resume_tests_pass", evidence.get("resume_test") == "PASS" and evidence.get("premature_batch_test") == "PASS" and evidence.get("terminal_summary_test") == "PASS")
    check("infra_trigger_absent", evidence.get("live_trigger_present") is False)

    denied = manifest.get("not_authorized") or {}
    check("semantic_v4_2_denied", denied.get("semantic_v4_2") is True)
    check("fresh_blind_denied", denied.get("fresh_blind") is True)
    check("locked_test_denied", denied.get("legacy_locked_test") is True)
    check("final_measurement_denied", denied.get("final_measurement") is True)
    check("architecture_freeze_denied", denied.get("architecture_freeze") is True)
    check("production_claim_denied", denied.get("production_readiness_claim") is True)

    passed = sum(1 for item in checks if item["passed"])
    return {
        "schema_version": "p12-c3-live-manifest-freeze-self-check-v1",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "execution_id": EXPECTED_EXECUTION_ID,
        "manifest_status": manifest.get("status"),
        "checks_passed": passed,
        "checks_total": len(checks),
        "provider_calls": 0,
        "private_oracle_access": 0,
        "fresh_blind_access": 0,
        "legacy_locked_test_access": 0,
        "live_trigger_present": EXPECTED_TRIGGER.exists(),
        "first_provider_call_occurred": False,
        "effective_checkpoint_runner_sha256": pins["effective_checkpoint_runner"]["source_sha256"],
        "live_workflow_sha256": live_workflow_pin["source_sha256"],
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.manifest)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks_passed", "checks_total", "provider_calls", "live_trigger_present")}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
