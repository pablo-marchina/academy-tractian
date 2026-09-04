from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.restart_recovery_campaign import (
    RestartRecoveryObservation,
    RestartRecoveryReport,
    verify_restart_recovery,
)


def _valid_observation(**overrides) -> RestartRecoveryObservation:
    values = {
        "first_restart_runtime_interrupted": 2,
        "first_restart_action_execution_uncertain": 1,
        "first_restart_action_custody_uncertain": 1,
        "first_restart_ledger_uncertain": 1,
        "pending_confirmation_preserved": True,
        "completed_runtime_preserved": True,
        "failed_runtime_preserved": True,
        "fresh_runtime_completed_after_recovery": True,
        "cross_tenant_visibility_blocked": True,
        "first_restart_provider_calls": 0,
        "first_restart_action_transport_calls": 0,
        "second_restart_new_runtime_recoveries": 0,
        "second_restart_new_action_custody_recoveries": 0,
        "second_restart_new_ledger_recoveries": 0,
        "second_restart_provider_calls": 0,
        "second_restart_action_transport_calls": 0,
    }
    values.update(overrides)
    return RestartRecoveryObservation(**values)


def test_restart_recovery_report_is_hash_bound_and_claim_limited() -> None:
    report = verify_restart_recovery(_valid_observation())

    assert report.status == "VERIFIED"
    assert report.interpretation == "safety_contract_only"
    assert report.production_availability_claim_ready is False
    assert report.automatic_retry_count == 0
    assert report.replay_count == 0
    assert len(report.evidence_sha256) == 64

    serialized = report.model_dump_json()
    for private_fragment in (
        "run-",
        "act_",
        "org-",
        "user-",
        "identity-",
        "Bearer",
        "idempotency_key",
        "arguments",
        "trace",
    ):
        assert private_fragment not in serialized


def test_restart_recovery_fails_closed_on_missing_safety_invariant_or_replay_work() -> None:
    with pytest.raises(ValueError, match="pending_confirmation_preserved"):
        verify_restart_recovery(_valid_observation(pending_confirmation_preserved=False))

    with pytest.raises(ValueError, match="first_restart_action_transport_calls"):
        verify_restart_recovery(_valid_observation(first_restart_action_transport_calls=1))

    with pytest.raises(ValueError, match="exactly two"):
        verify_restart_recovery(_valid_observation(first_restart_runtime_interrupted=1))


def test_restart_recovery_report_rejects_hash_tampering() -> None:
    report = verify_restart_recovery(_valid_observation())
    payload = report.model_dump(mode="json")
    payload["first_restart_runtime_interrupted"] = 3
    with pytest.raises(ValidationError, match="hash mismatch"):
        RestartRecoveryReport.model_validate(payload)
