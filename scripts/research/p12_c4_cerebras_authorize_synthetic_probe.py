#!/usr/bin/env python3
"""Provider-free one-shot authorization generator for the P12-C4 Cerebras synthetic probe.

This script never imports the Cerebras SDK, reads provider credentials, or performs
network I/O. It emits an authorization only after the exact effective-capacity
attestation v2 passes the same fail-closed validator used by the live probe.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "scripts" / "research" / "p12_c4_cerebras_synthetic_probe.py"
DEFAULT_ATTESTATION = ROOT / "research" / "experiments" / "p12-c4-cerebras-account-capacity-attestation-v2.json"
DEFAULT_OUTPUT = ROOT / "research" / "frozen" / "p12-c4-cerebras-synthetic-probe-live-authorization-v1.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("p12_c4_cerebras_synthetic_probe", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen synthetic probe runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_authorization(attestation_path: Path) -> dict[str, Any]:
    runner = load_runner()
    attestation = runner.validate_account_attestation(attestation_path)
    prereg, _serving, pacing = runner.validate_frozen_contracts()
    request_hashes = [runner.canonical_sha256(x["request_contract"]) for x in prereg["frozen_probe_calls"]]
    return {
        "schema_version": "p12-c4-cerebras-synthetic-probe-live-authorization-v1",
        "status": "AUTHORIZED_ONE_SYNTHETIC_PROBE_ATTEMPT",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "probe_id": runner.EXPECTED_PROBE_ID,
        "attestation_schema_version": runner.ATTESTATION_SCHEMA,
        "attestation_sha256": runner.canonical_sha256(attestation),
        "probe_request_sha256": request_hashes,
        "minimum_seconds_between_any_provider_requests": pacing["frozen_pacing"]["minimum_seconds_between_any_provider_requests"],
        "authorized_attempts": 1,
        "github_actions_run_attempt_required": 1,
        "rerun_allowed": False,
        "automatic_retry_allowed": False,
        "exposed_pool_live_generation_authorized": False,
        "private_scoring_authorized": False,
        "fresh_blind_access_authorized": False,
        "legacy_locked_test_access_authorized": False,
        "authorization_scope": "EXACTLY_TWO_PREREGISTERED_SYNTHETIC_CEREBRAS_CALLS_ONLY",
    }


def write_once(output: Path, value: dict[str, Any]) -> None:
    if output.exists():
        raise RuntimeError("one-shot authorization already exists; replacement is forbidden")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attestation", type=Path, default=DEFAULT_ATTESTATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    authorization = build_authorization(args.attestation)
    write_once(args.output, authorization)
    print(json.dumps(authorization, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
