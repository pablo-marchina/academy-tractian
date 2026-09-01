from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pytest

from academy_tractian.cloudflare_reset_window_capture_v1 import (
    ResetWindowCaptureError,
    build_reset_window_evidence,
    ensure_provider_credentials_absent,
    sha256_file,
)


UTC = timezone.utc
VALID_NOW = datetime(2026, 9, 2, 0, 5, 0, tzinfo=UTC)


def _build(source: Path, **overrides):
    kwargs = {
        "workers_free_source_artifact": source,
        "now_utc": VALID_NOW,
        "attest_workers_free_active": True,
        "attest_workers_paid_disabled": True,
        "attest_no_workers_ai_calls_since_reset": True,
        "attest_no_automated_workers_ai_consumers_since_reset": True,
        "attest_exclusive_workers_ai_window_until_packet_completion": True,
        "attest_direct_workers_ai_route": True,
        "attest_no_ai_gateway_or_prepaid_unified_billing": True,
    }
    kwargs.update(overrides)
    return build_reset_window_evidence(**kwargs)


def test_builds_exact_sanitized_reset_window_evidence(tmp_path: Path) -> None:
    source = tmp_path / "workers-free-proof.txt"
    source.write_bytes(b"Workers Free / Active; Workers Paid not active")
    evidence = _build(source)

    assert evidence.utc_day == "2026-09-02"
    assert evidence.reset_at_utc == datetime(2026, 9, 2, 0, 0, 0, tzinfo=UTC)
    assert evidence.observed_at_utc == VALID_NOW
    assert evidence.derived_free_neurons_remaining == 10000.0
    assert evidence.comparison_attempts_consumed == 0
    assert evidence.inference_used_to_obtain_evidence is False
    assert evidence.credential_account_probe_used is False
    assert evidence.account_identifier_recorded is False
    assert evidence.secret_recorded is False
    assert evidence.workers_free_source_artifact_sha256 == sha256(source.read_bytes()).hexdigest()


def test_every_operator_attestation_is_required(tmp_path: Path) -> None:
    source = tmp_path / "proof.bin"
    source.write_bytes(b"proof")
    names = (
        "attest_workers_free_active",
        "attest_workers_paid_disabled",
        "attest_no_workers_ai_calls_since_reset",
        "attest_no_automated_workers_ai_consumers_since_reset",
        "attest_exclusive_workers_ai_window_until_packet_completion",
        "attest_direct_workers_ai_route",
        "attest_no_ai_gateway_or_prepaid_unified_billing",
    )
    for name in names:
        with pytest.raises(ResetWindowCaptureError, match="explicitly true"):
            _build(source, **{name: False})


def test_outside_first_ten_minutes_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "proof.bin"
    source.write_bytes(b"proof")
    with pytest.raises(ValueError):
        _build(source, now_utc=datetime(2026, 9, 2, 0, 10, 1, tzinfo=UTC))


def test_naive_clock_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "proof.bin"
    source.write_bytes(b"proof")
    with pytest.raises(ResetWindowCaptureError, match="timezone-aware"):
        _build(source, now_utc=datetime(2026, 9, 2, 0, 5, 0))


def test_source_artifact_must_exist(tmp_path: Path) -> None:
    with pytest.raises(ResetWindowCaptureError, match="existing file"):
        _build(tmp_path / "missing.png")


def test_sha256_file_is_binary_safe(tmp_path: Path) -> None:
    source = tmp_path / "proof.bin"
    payload = bytes(range(256)) * 32
    source.write_bytes(payload)
    assert sha256_file(source) == sha256(payload).hexdigest()


def test_provider_credentials_fail_before_capture() -> None:
    ensure_provider_credentials_absent({})
    with pytest.raises(ResetWindowCaptureError, match="before provider secrets"):
        ensure_provider_credentials_absent({"CLOUDFLARE_API_TOKEN": "secret"})
    with pytest.raises(ResetWindowCaptureError, match="before provider secrets"):
        ensure_provider_credentials_absent({"CLOUDFLARE_ACCOUNT_ID": "account"})
