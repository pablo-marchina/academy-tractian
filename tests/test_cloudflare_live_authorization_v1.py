from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from academy_tractian.cloudflare_live_authorization_v1 import (
    ADR_018_GIT_BLOB,
    ADR_019_GIT_BLOB,
    ADR_020_GIT_BLOB,
    ALLOWED_MODELS,
    AUTHORIZATION_PROTOCOL_VERSION,
    CloudflareAuthorizationError,
    CloudflareLiveAuthorizationEvidenceV1,
    canonical_custody_root_sha256,
    authorization_to_adr020_pre_live_evidence,
    issue_live_authorization_receipt,
    validate_frozen_authorization_protocol,
    validate_receipt_for_execution,
)


NOW = datetime(2026, 9, 1, 13, 10, 0, tzinfo=timezone.utc)
ARTIFACT_SHA = "1" * 64


def _evidence(**overrides):
    payload = {
        "observed_at_utc": NOW - timedelta(seconds=60),
        "utc_day": "2026-09-01",
        "workers_plan": "Workers Free",
        "workers_paid_enabled": False,
        "neurons_used_today": 500.0,
        "free_neurons_remaining": 9500.0,
        "direct_workers_ai_route": True,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "gateway_header_present": False,
        "comparison_attempts_consumed": 0,
        "exclusive_workers_ai_usage_window_attested": True,
        "inference_used_to_obtain_evidence": False,
        "credential_account_probe_used": False,
        "account_identifier_recorded": False,
        "secret_recorded": False,
        "dashboard_source_artifact_sha256": ARTIFACT_SHA,
        "dashboard_source_retained_outside_repo": True,
    }
    payload.update(overrides)
    return CloudflareLiveAuthorizationEvidenceV1(**payload)


def test_frozen_protocol_is_provider_free_and_pinned() -> None:
    protocol = validate_frozen_authorization_protocol()
    assert protocol["schema_version"] == AUTHORIZATION_PROTOCOL_VERSION
    assert protocol["upstream_pins"]["adr_018_blob"] == ADR_018_GIT_BLOB
    assert protocol["upstream_pins"]["adr_019_blob"] == ADR_019_GIT_BLOB
    assert protocol["upstream_pins"]["adr_020_blob"] == ADR_020_GIT_BLOB
    assert tuple(protocol["candidate_identity"]["models"]) == ALLOWED_MODELS
    assert protocol["authorization_evidence"]["minimum_free_neurons_remaining"] == 9000
    assert protocol["authorization_evidence"]["max_age_seconds"] == 600
    assert protocol["authorization_receipt"]["max_lifetime_seconds"] == 300
    assert protocol["current_task_boundaries"]["provider_model_inference_calls"] == 0
    assert protocol["current_task_boundaries"]["credential_account_probes"] == 0
    assert protocol["current_task_boundaries"]["attempt_1_authorized"] is False


def test_valid_fresh_evidence_issues_short_lived_root_bound_receipt(tmp_path: Path) -> None:
    evidence = _evidence()
    root = tmp_path / "canonical-custody"
    receipt = issue_live_authorization_receipt(evidence, custody_root=root, now_utc=NOW)

    assert receipt.evidence_sha256 == evidence.canonical_sha256
    assert receipt.custody_root_sha256 == canonical_custody_root_sha256(root)
    assert receipt.available_free_neurons_at_issue == 9500
    assert receipt.attempt_1_authorized is True
    assert receipt.credentials_recorded is False
    assert receipt.account_identifier_recorded is False
    assert receipt.raw_local_custody_path_recorded is False
    assert (receipt.expires_at_utc - receipt.issued_at_utc).total_seconds() <= 300
    validate_receipt_for_execution(
        receipt,
        evidence,
        custody_root=root,
        now_utc=NOW + timedelta(seconds=120),
    )


def test_receipt_serialization_contains_no_account_id_secret_or_raw_root(tmp_path: Path) -> None:
    evidence = _evidence()
    root = tmp_path / "private-user-path" / "custody"
    receipt = issue_live_authorization_receipt(evidence, custody_root=root, now_utc=NOW)
    serialized = json.dumps(receipt.model_dump(mode="json"), sort_keys=True)
    assert "CLOUDFLARE_API_TOKEN" not in serialized
    assert "CLOUDFLARE_ACCOUNT_ID" not in serialized
    assert "private-user-path" not in serialized
    assert ARTIFACT_SHA not in serialized


def test_stale_future_and_cross_day_evidence_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "custody"
    with pytest.raises(CloudflareAuthorizationError, match="stale"):
        issue_live_authorization_receipt(
            _evidence(observed_at_utc=NOW - timedelta(seconds=601)),
            custody_root=root,
            now_utc=NOW,
        )
    with pytest.raises(CloudflareAuthorizationError, match="future"):
        issue_live_authorization_receipt(
            _evidence(observed_at_utc=NOW + timedelta(seconds=31)),
            custody_root=root,
            now_utc=NOW,
        )
    previous_day = datetime(2026, 8, 31, 23, 59, 0, tzinfo=timezone.utc)
    cross_day = _evidence(observed_at_utc=previous_day, utc_day="2026-08-31")
    with pytest.raises(CloudflareAuthorizationError, match="current UTC day"):
        issue_live_authorization_receipt(cross_day, custody_root=root, now_utc=NOW)


def test_neuron_accounting_and_paid_or_gateway_states_are_schema_hard_gates() -> None:
    with pytest.raises(ValidationError):
        _evidence(neurons_used_today=1001.0, free_neurons_remaining=8999.0)
    with pytest.raises(ValidationError):
        _evidence(neurons_used_today=100.0, free_neurons_remaining=9500.0)
    with pytest.raises(ValidationError):
        _evidence(workers_paid_enabled=True)
    with pytest.raises(ValidationError):
        _evidence(ai_gateway_route_used=True)
    with pytest.raises(ValidationError):
        _evidence(prepaid_unified_billing_route_used=True)
    with pytest.raises(ValidationError):
        _evidence(gateway_header_present=True)
    with pytest.raises(ValidationError):
        _evidence(exclusive_workers_ai_usage_window_attested=False)
    with pytest.raises(ValidationError):
        _evidence(comparison_attempts_consumed=1)


def test_receipt_cannot_move_to_another_root_or_outlive_window(tmp_path: Path) -> None:
    evidence = _evidence()
    root = tmp_path / "custody-a"
    receipt = issue_live_authorization_receipt(evidence, custody_root=root, now_utc=NOW)

    with pytest.raises(CloudflareAuthorizationError, match="custody root mismatch"):
        validate_receipt_for_execution(
            receipt,
            evidence,
            custody_root=tmp_path / "custody-b",
            now_utc=NOW + timedelta(seconds=1),
        )
    with pytest.raises(CloudflareAuthorizationError):
        validate_receipt_for_execution(
            receipt,
            evidence,
            custody_root=root,
            now_utc=NOW + timedelta(seconds=301),
        )


def test_evidence_mutation_invalidates_receipt(tmp_path: Path) -> None:
    evidence = _evidence()
    receipt = issue_live_authorization_receipt(
        evidence,
        custody_root=tmp_path / "custody",
        now_utc=NOW,
    )
    mutated = _evidence(neurons_used_today=600.0, free_neurons_remaining=9400.0)
    with pytest.raises(CloudflareAuthorizationError, match="evidence hash mismatch"):
        validate_receipt_for_execution(
            receipt,
            mutated,
            custody_root=tmp_path / "custody",
            now_utc=NOW + timedelta(seconds=1),
        )


def test_valid_receipt_converts_exactly_to_adr020_pre_live_evidence(tmp_path: Path) -> None:
    evidence = _evidence()
    root = tmp_path / "custody"
    receipt = issue_live_authorization_receipt(evidence, custody_root=root, now_utc=NOW)
    pre_live = authorization_to_adr020_pre_live_evidence(
        receipt,
        evidence,
        custody_root=root,
        now_utc=NOW + timedelta(seconds=1),
    )
    assert pre_live.workers_plan == "Workers Free"
    assert pre_live.workers_paid_enabled is False
    assert pre_live.prepaid_ai_gateway_enabled is False
    assert pre_live.direct_workers_ai_route is True
    assert pre_live.actual_cash_cost_usd == 0.0
    assert pre_live.free_neurons_remaining == 9500.0
    assert pre_live.utc_day == "2026-09-01"
    assert receipt.receipt_sha256 in pre_live.evidence_source
    assert pre_live.inference_used_to_obtain_evidence is False
    assert pre_live.credential_account_probe_used is False
