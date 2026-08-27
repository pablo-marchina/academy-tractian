#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research/experiments/p12-c3-exposed-pool-capacity-controlled-factorial-preregistration-v1.json"
ACTIVATION = ROOT / "research/experiments/p12-c3-capacity-controlled-activation-eligibility-v1.json"
BATCH_MAP = ROOT / "research/frozen/p12-c3-capacity-batch-map-v1.json"
CAPACITY = ROOT / "scripts/research/p12_c3_capacity_control.py"
CASES = ROOT / "research/fixtures/p12-c1-exposed-agent-input-cases-v1.json"

EXPECTED_CANDIDATE_PINS = {
    "scripts/research/p12_c2_factorial_candidates.py": "33fbeec64d65ca666d30a14f9a3c196b6c607bec",
    "research/frozen/p12-c2-public-intent-map-v1.json": "26c666e335d8264fb913c5598cfa6d12b42c6798",
    "scripts/research/p12_c1_evidence_route_candidates.py": "e5d0b3d005ffbd9068d32a094133c0cb7cd8a9f5",
    "scripts/research/e14q_full_dev_public_action_authorization_consistency_guard.py": "3c44e70429872825b1d21032d311137c9d428ebf",
    "scripts/research/e14q2_full_dev_public_route_role_purpose_consistency_guard.py": "a54139f7188b83bb0046050e6f4a6c6372091980",
    "research/e2/tool_registry.py": "97e15fa24bfe865a1cd3a7b9798365f1d3325c8b",
    "scripts/research/p12_c2_execution_derivation.py": "3fad678c60c99d50925360f12332a98386b8b400",
    "research/execution-bundles/p12-c1/p12_c1_paired_exposed_pool_execution.py.gz": "a5c27394014bac656faa0a2f923a5c5da72d66f5",
    "scripts/research/e9_evaluator_side_scorer_v4_1.py": "b33afab0b3bfc9b81037a5391f49d286ef0d7c35",
    "research/experiments/p12-c1-exact-ticket-evaluator-alignment-amendment-v1.json": "87c6ce56d7bd90ca866ad31721365e70f70d2e6c",
    "scripts/research/p12_c2_factorial_score.py": "dc20be4896ff023989ee6deb012ad440c39ec531",
}
EXPECTED_PARENT_CONFIG_SHA256 = "9033a78a5bab46e4c48ebfc0ec70b6476570519fa62f0526625916d0cd3d3b89"
EXPECTED_FACTORIAL_SCORER_SHA256 = "f3500751448c3b52bf361f4d565ba940c8e9e62e8ab197bb1206fdb7d89a7d22"
EXPECTED_SEEDS = [2026082307, 2026082308, 2026082309]
EXPECTED_TICKETS = ["TKT-INV-04","TKT-EXE-16","TKT-INV-05","TKT-EXE-13","TKT-INV-06","TKT-EXE-15","TKT-INV-11b","TKT-CTX-01","TKT-INV-09","TKT-EXE-12","TKT-CTX-02","TKT-INV-11"]
EXPECTED_GROUPS = {"asset_G501","asset_C710","asset_S420","asset_M208","asset_M101","asset_B204","asset_M102"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(checks: list[dict[str, Any]], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "pass": bool(ok), "detail": detail})
    if not ok:
        raise AssertionError(f"P12-C3 activation check failed: {name}: {detail}")


def load_capacity():
    spec = importlib.util.spec_from_file_location("p12_c3_capacity_control", CAPACITY)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load capacity control")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    if os.getenv("GROQ_API_KEY"):
        raise AssertionError("activation must be provider-free")
    prereg = load(PREREG)
    activation = load(ACTIVATION)
    batch_map = load(BATCH_MAP)
    cases = load(CASES)
    cap = load_capacity()
    checks: list[dict[str, Any]] = []

    add(checks, "prereg_frozen", prereg.get("decision_state") == "EXPERIMENT_FROZEN")
    add(checks, "experiment_id", activation.get("experiment_id") == "P12-C3_EXPOSED_POOL_CAPACITY_CONTROLLED_FACTORIAL")
    add(checks, "no_provider_calls", activation.get("provider_or_model_calls_during_activation") == 0)
    add(checks, "no_private_oracle", activation.get("private_oracle_access_during_activation") is False)
    add(checks, "no_blind", activation.get("fresh_blind_access_during_activation") is False and activation.get("legacy_locked_test_access_during_activation") is False)
    add(checks, "candidate_definition_unchanged", activation.get("candidate_definition_changed_from_p12_c2") is False)
    add(checks, "parent_config_unchanged", activation.get("common_parent_config_sha256") == EXPECTED_PARENT_CONFIG_SHA256)
    add(checks, "factorial_scorer_unchanged", activation.get("factorial_scorer_sha256") == EXPECTED_FACTORIAL_SCORER_SHA256)

    for rel, expected in EXPECTED_CANDIDATE_PINS.items():
        path = ROOT / rel
        add(checks, f"pin_exists:{rel}", path.is_file(), rel)
        add(checks, f"pin_match:{rel}", git_blob_sha(path) == expected, rel)
    add(checks, "factorial_scorer_sha256_match", sha256(ROOT / "scripts/research/p12_c2_factorial_score.py") == EXPECTED_FACTORIAL_SCORER_SHA256)

    add(checks, "batch_map_frozen", batch_map.get("status") == "FROZEN")
    add(checks, "six_batches", batch_map.get("batch_count") == 6 and len(batch_map.get("batches", [])) == 6)
    add(checks, "six_parents_per_batch", batch_map.get("parents_per_batch") == 6 and all(len(b["cells"]) == 6 for b in batch_map["batches"]))
    flat = [cell for batch in batch_map["batches"] for cell in batch["cells"]]
    ids = [c["cell_id"] for c in flat]
    add(checks, "exact_36_unique_cells", len(flat) == 36 and len(set(ids)) == 36)
    add(checks, "seed_schedule_exact", sorted({c["seed"] for c in flat}) == EXPECTED_SEEDS)
    for seed in EXPECTED_SEEDS:
        tickets = [c["ticket_id"] for c in flat if c["seed"] == seed]
        add(checks, f"ticket_order_exact:{seed}", tickets == EXPECTED_TICKETS, repr(tickets))
    add(checks, "seven_groups", {c["group_id"] for c in flat} == EXPECTED_GROUPS)
    add(checks, "public_cases_12", len(cases) == 12 and {r["ticket_id"] for r in cases} == set(EXPECTED_TICKETS))
    add(checks, "no_locked_groups", not ({c["group_id"] for c in flat} & {"asset_M605","asset_M205","asset_V301"}))

    add(checks, "capacity_constants", cap.SAFETY_MARGIN_SECONDS == 30 and cap.MIN_INTER_REQUEST_DELAY_SECONDS == 30 and cap.MAX_PRE_OUTPUT_TRANSPORT_ATTEMPTS_PER_CELL == 3 and cap.MAX_COLLECTION_HOURS == 72)
    add(checks, "duration_seconds", cap.parse_duration_seconds("7.66s") == 7.66)
    add(checks, "duration_mixed", abs(cap.parse_duration_seconds("2m59.56s") - 179.56) < 1e-9)
    add(checks, "duration_hours", cap.parse_duration_seconds("1h2m3s") == 3723)
    now = datetime(2026, 8, 23, 18, 0, 0, tzinfo=timezone.utc)
    later = cap.provider_wait_deadline({"retry-after":"2","x-ratelimit-reset-requests":"2m59.56s","x-ratelimit-reset-tokens":"7.66s"}, now)
    add(checks, "later_reset_plus_margin", later == now + timedelta(seconds=209.56), str(later))
    http_date = "Sun, 23 Aug 2026 18:01:00 GMT"
    retry = cap.provider_wait_deadline({"retry-after": http_date}, now)
    add(checks, "retry_after_http_date", retry == now + timedelta(seconds=90), str(retry))
    decision = cap.rate_limit_decision(429, {"retry-after":"10"}, False, now)
    add(checks, "429_no_output_same_cell_pending", decision["cell_pending"] and not decision["candidate_outcome"] and not decision["abort_batch"])
    missing = cap.rate_limit_decision(429, {}, False, now)
    add(checks, "429_no_reset_abort_batch", missing["cell_pending"] and missing["abort_batch"] and missing["resume_at"] is None)
    output429 = cap.rate_limit_decision(429, {"retry-after":"10"}, True, now)
    add(checks, "model_output_consumes_cell", output429["candidate_outcome"] and not output429["cell_pending"])
    headroom = cap.proactive_capacity_decision({"x-ratelimit-remaining-requests":"1","x-ratelimit-remaining-tokens":"9000"}, 4096, now)
    add(checks, "headroom_send", headroom["send"] is True)
    stop = cap.proactive_capacity_decision({"x-ratelimit-remaining-requests":"10","x-ratelimit-remaining-tokens":"100","x-ratelimit-reset-tokens":"7.66s"}, 4096, now)
    add(checks, "token_headroom_stop", stop["send"] is False and stop["resume_at"] is not None)
    abort = cap.proactive_capacity_decision({"x-ratelimit-remaining-requests":"0"}, 4096, now)
    add(checks, "no_reset_no_guess", abort["send"] is False and abort["reason"] == "INSUFFICIENT_HEADROOM_NO_RESET_METADATA")
    add(checks, "72h_horizon_inclusive", cap.within_horizon(now, now + timedelta(hours=72)))
    add(checks, "72h_horizon_no_extension", not cap.within_horizon(now, now + timedelta(hours=72, seconds=1)))

    declared = set(ids)
    checkpoint = {"completed": {}, "pending": list(ids), "transport_failure_count": 0, "rate_limit_event_count": 0, "provider_reset_timestamp_or_duration": None}
    cap.validate_checkpoint(checkpoint, declared)
    first = ids[0]
    cap.accept_parent(checkpoint, first, "hash-1", {"private":"raw-parent"})
    add(checks, "accepted_parent_removed_from_pending", first in checkpoint["completed"] and first not in checkpoint["pending"])
    try:
        cap.accept_parent(checkpoint, first, "hash-2", {"private":"replacement"})
        regen_blocked = False
    except AssertionError:
        regen_blocked = True
    add(checks, "completed_parent_regeneration_blocked", regen_blocked)
    cap.validate_checkpoint(checkpoint, declared)
    public = cap.public_checkpoint_record(checkpoint)
    add(checks, "public_checkpoint_fields_exact", set(public) == {"completed_cell_count","pending_cell_count","transport_failure_count","rate_limit_event_count","provider_reset_timestamp_or_duration","checkpoint_hash"})
    add(checks, "public_checkpoint_excludes_raw", "raw_parent" not in json.dumps(public))

    pins = activation.get("source_pins", {})
    for name, pin in pins.items():
        if isinstance(pin, dict) and pin.get("path") and pin.get("git_blob_sha"):
            path = ROOT / pin["path"]
            add(checks, f"activation_pin:{name}", path.is_file() and git_blob_sha(path) == pin["git_blob_sha"], pin["path"])

    all_pass = all(c["pass"] for c in checks)
    if activation.get("status") == "ACTIVATION_ELIGIBILITY_PASS":
        add(checks, "final_authorization", activation.get("execution_authorized") is True and activation.get("authorized_live_experiments") == 1)
    else:
        add(checks, "pending_not_authorized", activation.get("execution_authorized") is False and activation.get("authorized_live_experiments") == 0)

    result = {
        "schema_version": "p12-c3-capacity-activation-self-check-v1",
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks_passed": sum(1 for c in checks if c["pass"]),
        "checks_total": len(checks),
        "all_passed": all(c["pass"] for c in checks),
        "provider_calls": 0,
        "private_oracle_access": 0,
        "fresh_blind_access": 0,
        "legacy_locked_test_access": 0,
        "batch_geometry": {"batches": 6, "parents_per_batch": 6, "unique_cells": 36},
        "capacity_contract": {"min_delay_seconds":30,"max_pre_output_attempts":3,"horizon_hours":72,"reset_safety_margin_seconds":30},
        "candidate_definition_changed": False,
        "checks": checks,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
