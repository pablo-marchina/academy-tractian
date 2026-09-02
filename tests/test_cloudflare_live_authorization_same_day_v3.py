from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from academy_tractian.cloudflare_live_authorization_same_day_v3 import (
    ADR_021_GIT_BLOB,
    ADR_022_GIT_BLOB,
    ADR_023_GIT_BLOB,
    DAILY_FREE_NEURONS,
    CloudflareAuthorizationError,
    CloudflareSameDayZeroUseEvidenceV1,
    issue_same_day_zero_use_receipt,
    same_day_zero_use_authorization_to_adr020_pre_live_evidence,
    validate_frozen_same_day_zero_use_amendment,
    validate_same_day_zero_use_receipt_for_execution,
)


RESET = datetime(2026, 9, 2, 0, 0, 0, tzinfo=timezone.utc)
OBSERVED = RESET + timedelta(minutes=39)
NOW = OBSERVED + timedelta(minutes=1)
ARTIFACT_SHA = "4" * 64


def _evidence(**overrides):
    payload = {
        "observed_at_utc": OBSERVED,
        "utc_day": "2026-09-02",
        "reset_at_utc": RESET,
        "workers_plan": "Workers Free",
        "workers_paid_enabled": False,
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
        "workers_free_source_artifact_sha256": ARTIFACT_SHA,
        "source_artifact_retained_outside_repo": True,
    }
    payload.update(overrides)
    return CloudflareSameDayZeroUseEvidenceV1(**payload)


def test_protocol_preserves_adr021_022_023_and_zero_live_boundaries() -> None:
    protocol = validate_frozen_same_day_zero_use_amendment()
    historical = protocol["historical_protocol"]
    assert historical["adr_021_blob"] == ADR_021_GIT_BLOB
    assert historical["adr_022_blob"] == ADR_022_GIT_BLOB
    assert historical["adr_023_blob"] == ADR_023_GIT_BLOB
    assert historical["preserve_adr_021"] is True
    assert historical["preserve_adr_022"] is True
    assert historical["preserve_adr_023"] is True
    assert protocol["evidence_mode"]["name"] == "SAME_DAY_ZERO_USE_ATTESTATION"
    assert protocol["evidence_mode"]["derived_free_neurons_at_evidence"] == 10000
    assert protocol["future_execution_boundary"]["provider_model_inference_calls_in_this_task"] == 0
    assert protocol["future_execution_boundary"]["attempt_1_authorized"] is False


def test_same_day_observation_after_ten_minutes_is_valid(tmp_path: Path) -> None:
    evidence = _evidence()
    assert (evidence.observed_at_utc - evidence.reset_at_utc).total_seconds() > 600

    receipt = issue_same_day_zero_use_receipt(
        evidence,
        custody_root=tmp_path / "custody",
        now_utc=NOW,
    )
    assert receipt.derived_free_neurons_at_issue == DAILY_FREE_NEURONS
    assert receipt.evidence_mode == "SAME_DAY_ZERO_USE_ATTESTATION"
    assert receipt.attempt_1_authorized is True

    pre_live = same_day_zero_use_authorization_to_adr020_pre_live_evidence(
        receipt,
        evidence,
        custody_root=tmp_path / "custody",
        now_utc=NOW + timedelta(seconds=30),
    )
    assert pre_live.workers_plan == "Workers Free"
    assert pre_live.workers_paid_enabled is False
    assert pre_live.prepaid_ai_gateway_enabled is False
    assert pre_live.direct_workers_ai_route is True
    assert pre_live.actual_cash_cost_usd == 0.0
    assert pre_live.free_neurons_remaining == 10000.0
    assert pre_live.inference_used_to_obtain_evidence is False
    assert pre_live.credential_account_probe_used is False


def test_reset_timestamp_must_be_current_utc_day_midnight() -> None:
    with pytest.raises(ValidationError, match="00:00:00 UTC"):
        _evidence(reset_at_utc=RESET + timedelta(seconds=1))
    with pytest.raises(ValidationError, match="00:00:00 UTC"):
        _evidence(reset_at_utc=RESET - timedelta(days=1))


def test_attestations_and_free_plan_are_hard_schema_gates() -> None:
    invalid_cases = (
        {"workers_paid_enabled": True},
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
        {"account_identifier_recorded": True},
        {"secret_recorded": True},
        {"source_artifact_retained_outside_repo": False},
    )
    for override in invalid_cases:
        with pytest.raises(ValidationError):
            _evidence(**override)


def test_allocation_values_cannot_be_weakened() -> None:
    with pytest.raises(ValidationError):
        _evidence(free_allocation_neurons=9000.0)
    with pytest.raises(ValidationError):
        _evidence(derived_free_neurons_remaining=9000.0)


def test_evidence_is_fresh_but_zero_use_claim_spans_from_reset(tmp_path: Path) -> None:
    evidence = _evidence()
    with pytest.raises(CloudflareAuthorizationError, match="stale"):
        issue_same_day_zero_use_receipt(
            evidence,
            custody_root=tmp_path / "custody",
            now_utc=OBSERVED + timedelta(seconds=601),
        )
    with pytest.raises(CloudflareAuthorizationError, match="future"):
        issue_same_day_zero_use_receipt(
            evidence,
            custody_root=tmp_path / "custody",
            now_utc=OBSERVED - timedelta(seconds=31),
        )
    with pytest.raises(CloudflareAuthorizationError, match="current UTC day"):
        issue_same_day_zero_use_receipt(
            evidence,
            custody_root=tmp_path / "custody",
            now_utc=datetime(2026, 9, 3, 0, 0, 1, tzinfo=timezone.utc),
        )


def test_receipt_is_bound_to_evidence_root_and_expiry(tmp_path: Path) -> None:
    evidence = _evidence()
    root = tmp_path / "custody-a"
    receipt = issue_same_day_zero_use_receipt(evidence, custody_root=root, now_utc=NOW)

    validate_same_day_zero_use_receipt_for_execution(
        receipt,
        evidence,
        custody_root=root,
        now_utc=NOW + timedelta(seconds=1),
    )
    with pytest.raises(CloudflareAuthorizationError, match="custody root mismatch"):
        validate_same_day_zero_use_receipt_for_execution(
            receipt,
            evidence,
            custody_root=tmp_path / "custody-b",
            now_utc=NOW + timedelta(seconds=1),
        )
    mutated = _evidence(workers_free_source_artifact_sha256="5" * 64)
    with pytest.raises(CloudflareAuthorizationError, match="evidence hash mismatch"):
        validate_same_day_zero_use_receipt_for_execution(
            receipt,
            mutated,
            custody_root=root,
            now_utc=NOW + timedelta(seconds=1),
        )
    with pytest.raises(CloudflareAuthorizationError):
        validate_same_day_zero_use_receipt_for_execution(
            receipt,
            evidence,
            custody_root=root,
            now_utc=NOW + timedelta(seconds=301),
        )
