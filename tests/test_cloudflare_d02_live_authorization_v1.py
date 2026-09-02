from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from academy_tractian.cloudflare_d02_live_authorization_v1 import (
    D02_WORST_CASE_PACKET_NEURONS,
    CloudflareD02LiveAuthorizationReceiptV1,
    CloudflareD02ZeroUseEvidenceV1,
    d02_receipt_to_pre_live_evidence,
    issue_d02_live_authorization_receipt,
    validate_d02_receipt_for_execution,
    validate_d02_zero_use_evidence,
    validate_frozen_d02_live_authorization,
)
from academy_tractian.cloudflare_live_authorization_v1 import CloudflareAuthorizationError


REPO_ROOT = Path(__file__).resolve().parents[1]


def _evidence(observed: datetime) -> CloudflareD02ZeroUseEvidenceV1:
    observed = observed.astimezone(timezone.utc)
    return CloudflareD02ZeroUseEvidenceV1(
        observed_at_utc=observed,
        utc_day=observed.date().isoformat(),
        reset_at_utc=observed.replace(hour=0, minute=0, second=0, microsecond=0),
    )


def test_frozen_d02_live_authorization_protocol_and_source_pins_validate() -> None:
    protocol = validate_frozen_d02_live_authorization(REPO_ROOT)
    assert protocol["d02_plan_sha256"] == (
        "e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"
    )
    assert protocol["resource_gate"]["authorization_requires_exact_fresh_reset_zero_use_capacity"] == 10000.0
    assert protocol["resource_gate"]["d02_worst_case_packet_neurons"] == pytest.approx(9352.805376)


def test_d02_explicitly_rejects_the_d01_used_2026_09_02_utc_window() -> None:
    with pytest.raises(ValueError, match="D01 already consumed Workers AI"):
        _evidence(datetime(2026, 9, 2, 14, 0, tzinfo=timezone.utc))


def test_d02_future_reset_zero_use_evidence_derives_exact_10000_and_freshness() -> None:
    observed = datetime(2026, 9, 3, 0, 1, tzinfo=timezone.utc)
    evidence = _evidence(observed)
    assert evidence.derived_free_neurons_remaining == 10000.0
    assert evidence.d02_worst_case_packet_neurons == pytest.approx(9352.805376)
    assert evidence.derived_free_neurons_remaining > D02_WORST_CASE_PACKET_NEURONS

    validate_d02_zero_use_evidence(evidence, now_utc=observed + timedelta(seconds=599))
    with pytest.raises(CloudflareAuthorizationError, match="stale"):
        validate_d02_zero_use_evidence(evidence, now_utc=observed + timedelta(seconds=601))


def test_d02_receipt_is_short_lived_bound_to_evidence_and_custody(tmp_path: Path) -> None:
    observed = datetime(2026, 9, 3, 0, 2, tzinfo=timezone.utc)
    evidence = _evidence(observed)
    custody = tmp_path / "custody-a"
    issued = observed + timedelta(seconds=30)
    receipt = issue_d02_live_authorization_receipt(
        evidence,
        custody_root=custody,
        now_utc=issued,
    )
    assert receipt.derived_free_neurons_at_issue == 10000.0
    assert receipt.d02_worst_case_packet_neurons == pytest.approx(9352.805376)
    assert 0 < (receipt.expires_at_utc - receipt.issued_at_utc).total_seconds() <= 300

    validate_d02_receipt_for_execution(
        receipt,
        evidence,
        custody_root=custody,
        now_utc=issued + timedelta(seconds=1),
    )
    with pytest.raises(CloudflareAuthorizationError, match="custody binding mismatch"):
        validate_d02_receipt_for_execution(
            receipt,
            evidence,
            custody_root=tmp_path / "custody-b",
            now_utc=issued + timedelta(seconds=1),
        )

    pre_live = d02_receipt_to_pre_live_evidence(
        receipt,
        evidence,
        custody_root=custody,
        now_utc=issued + timedelta(seconds=1),
    )
    assert pre_live.free_neurons_remaining == 10000.0
    assert pre_live.workers_paid_enabled is False
    assert pre_live.actual_cash_cost_usd == 0.0


def test_d02_receipt_model_rejects_tampered_hash(tmp_path: Path) -> None:
    observed = datetime(2026, 9, 3, 0, 3, tzinfo=timezone.utc)
    evidence = _evidence(observed)
    receipt = issue_d02_live_authorization_receipt(
        evidence,
        custody_root=tmp_path / "custody",
        now_utc=observed + timedelta(seconds=1),
    )
    payload = receipt.model_dump(mode="json")
    payload["receipt_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="receipt_sha256 mismatch"):
        CloudflareD02LiveAuthorizationReceiptV1.model_validate(payload)


def test_capture_cli_requires_provider_credentials_absent_before_any_evidence(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["CLOUDFLARE_API_TOKEN"] = "must-not-be-used"
    env["CLOUDFLARE_ACCOUNT_ID"] = "0123456789abcdef0123456789abcdef"
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/research/capture_cloudflare_d02_zero_use_evidence_v1.py"),
            "--output",
            str(output),
            "--attest-workers-free-active",
            "--attest-workers-paid-disabled",
            "--attest-no-workers-ai-calls-since-reset",
            "--attest-no-automated-workers-ai-consumers-since-reset",
            "--attest-exclusive-workers-ai-window-until-packet-completion",
            "--attest-direct-workers-ai-route",
            "--attest-no-ai-gateway-or-prepaid-unified-billing",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert "CLOUDFLARE_API_TOKEN" in combined
    assert not output.exists()
    assert "must-not-be-used" not in combined


def test_d02_clis_bootstrap_without_pythonpath() -> None:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    for relative in (
        "scripts/research/capture_cloudflare_d02_zero_use_evidence_v1.py",
        "scripts/research/issue_cloudflare_d02_live_receipt_v1.py",
        "scripts/research/execute_cloudflare_d02_live_v1.py",
    ):
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / relative), "--help"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr


def test_launcher_source_validates_receipt_before_reading_provider_environment() -> None:
    source = (REPO_ROOT / "scripts/research/execute_cloudflare_d02_live_v1.py").read_text()
    receipt_gate = source.index("d02_receipt_to_pre_live_evidence(")
    token_read = source.index('os.environ.get("CLOUDFLARE_API_TOKEN"')
    account_read = source.index('os.environ.get("CLOUDFLARE_ACCOUNT_ID"')
    custody_reserve = source.index("reserve_d02_custody(")
    execute = source.index("execution.execute_all()")
    assert receipt_gate < token_read < custody_reserve < execute
    assert receipt_gate < account_read < custody_reserve < execute
    assert "requests" not in source
    assert "httpx" not in source
