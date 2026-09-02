from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

from academy_tractian.cloudflare_live_authorization_operator_attestation_v4 import (
    ADR_021_GIT_BLOB,
    ADR_021_PATH,
    ADR_022_GIT_BLOB,
    ADR_022_PATH,
    ADR_023_GIT_BLOB,
    ADR_023_PATH,
    ADR_024_GIT_BLOB,
    ADR_024_PATH,
    CloudflareOperatorAttestationEvidenceV1,
    _git_head_blob_sha,
    issue_operator_attestation_receipt,
    operator_attestation_to_adr020_pre_live_evidence,
    validate_frozen_operator_attestation_amendment,
    validate_operator_attestation_evidence,
    validate_operator_attestation_receipt_for_execution,
)
from academy_tractian.cloudflare_live_authorization_v1 import CloudflareAuthorizationError


RESET = datetime(2026, 9, 2, 0, 0, 0, tzinfo=timezone.utc)
OBSERVED = RESET + timedelta(minutes=39)
NOW = OBSERVED + timedelta(minutes=1)


def _evidence(**overrides):
    payload = {
        "observed_at_utc": OBSERVED,
        "utc_day": "2026-09-02",
        "reset_at_utc": RESET,
        "workers_free_active_attested": True,
        "workers_paid_disabled_attested": True,
        "free_allocation_neurons": 10000.0,
        "derived_free_neurons_remaining": 10000.0,
        "no_workers_ai_calls_since_reset_attested": True,
        "no_automated_workers_ai_consumers_since_reset_attested": True,
        "exclusive_workers_ai_account_window_until_packet_completion_attested": True,
        "direct_workers_ai_route": True,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "gateway_header_present": False,
        "comparison_attempts_consumed": 0,
        "inference_used_to_obtain_evidence": False,
        "credential_account_probe_used": False,
        "account_identifier_recorded": False,
        "secret_recorded": False,
        "external_plan_source_artifact_required": False,
        "plan_state_evidence_basis": "OPERATOR_ATTESTATION",
    }
    payload.update(overrides)
    return CloudflareOperatorAttestationEvidenceV1(**payload)


def test_protocol_preserves_historical_git_objects() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    protocol = validate_frozen_operator_attestation_amendment(repo_root)
    assert protocol["evidence_mode"]["external_plan_source_artifact_required"] is False
    assert protocol["portability"]["historical_blob_validation_uses_git_object_ids"] is True
    assert _git_head_blob_sha(repo_root, ADR_021_PATH) == ADR_021_GIT_BLOB
    assert _git_head_blob_sha(repo_root, ADR_022_PATH) == ADR_022_GIT_BLOB
    assert _git_head_blob_sha(repo_root, ADR_023_PATH) == ADR_023_GIT_BLOB
    assert _git_head_blob_sha(repo_root, ADR_024_PATH) == ADR_024_GIT_BLOB


def test_same_day_operator_attestation_needs_no_source_artifact() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    assert evidence.evidence_mode == "OPERATOR_PLAN_STATE_ATTESTATION"
    assert evidence.plan_state_evidence_basis == "OPERATOR_ATTESTATION"
    assert evidence.external_plan_source_artifact_required is False
    assert "workers_free_source_artifact_sha256" not in payload
    assert "source_artifact_retained_outside_repo" not in payload
    assert evidence.derived_free_neurons_remaining == 10000.0


def test_all_operator_attestations_are_hard_schema_gates() -> None:
    invalid = (
        {"workers_free_active_attested": False},
        {"workers_paid_disabled_attested": False},
        {"no_workers_ai_calls_since_reset_attested": False},
        {"no_automated_workers_ai_consumers_since_reset_attested": False},
        {"exclusive_workers_ai_account_window_until_packet_completion_attested": False},
        {"direct_workers_ai_route": False},
        {"ai_gateway_route_used": True},
        {"prepaid_unified_billing_route_used": True},
        {"gateway_header_present": True},
        {"comparison_attempts_consumed": 1},
        {"inference_used_to_obtain_evidence": True},
        {"credential_account_probe_used": True},
        {"external_plan_source_artifact_required": True},
        {"plan_state_evidence_basis": "DASHBOARD"},
    )
    for override in invalid:
        with pytest.raises(ValidationError):
            _evidence(**override)


def test_evidence_freshness_is_still_strict() -> None:
    evidence = _evidence()
    validate_operator_attestation_evidence(evidence, now_utc=NOW)
    with pytest.raises(CloudflareAuthorizationError, match="stale"):
        validate_operator_attestation_evidence(
            evidence,
            now_utc=OBSERVED + timedelta(seconds=601),
        )
    with pytest.raises(CloudflareAuthorizationError, match="current UTC day"):
        validate_operator_attestation_evidence(
            evidence,
            now_utc=datetime(2026, 9, 3, 0, 0, 1, tzinfo=timezone.utc),
        )


def test_receipt_binds_evidence_and_existing_adr020_pre_live_contract(tmp_path: Path) -> None:
    evidence = _evidence()
    root = tmp_path / "custody"
    receipt = issue_operator_attestation_receipt(
        evidence,
        custody_root=root,
        now_utc=NOW,
    )
    assert receipt.external_plan_source_artifact_required is False
    assert receipt.workers_free_active_attested is True
    assert receipt.workers_paid_disabled_attested is True
    assert receipt.attempt_1_authorized is True

    validate_operator_attestation_receipt_for_execution(
        receipt,
        evidence,
        custody_root=root,
        now_utc=NOW + timedelta(seconds=1),
    )
    pre_live = operator_attestation_to_adr020_pre_live_evidence(
        receipt,
        evidence,
        custody_root=root,
        now_utc=NOW + timedelta(seconds=1),
    )
    assert pre_live.workers_plan == "Workers Free"
    assert pre_live.workers_paid_enabled is False
    assert pre_live.prepaid_ai_gateway_enabled is False
    assert pre_live.direct_workers_ai_route is True
    assert pre_live.free_neurons_remaining == 10000.0
    assert pre_live.actual_cash_cost_usd == 0.0

    with pytest.raises(CloudflareAuthorizationError, match="custody root mismatch"):
        validate_operator_attestation_receipt_for_execution(
            receipt,
            evidence,
            custody_root=tmp_path / "other",
            now_utc=NOW + timedelta(seconds=1),
        )


def test_cli_bootstraps_src_without_external_pythonpath() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "research" / "capture_cloudflare_operator_attestation_evidence_v1.py"),
            "--help",
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert "--attest-workers-free-active" in completed.stdout
    assert "--workers-free-source" not in completed.stdout


def test_capture_contract_does_not_accept_screenshot_argument(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "research" / "capture_cloudflare_operator_attestation_evidence_v1.py"),
            "--output",
            str(tmp_path / "evidence.json"),
            "--workers-free-source",
            "does-not-exist.png",
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode != 0
    assert "unrecognized arguments" in completed.stderr
