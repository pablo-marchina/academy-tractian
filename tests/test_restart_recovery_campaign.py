from __future__ import annotations

import pytest
from pydantic import ValidationError

from academy_tractian.restart_recovery_campaign import (
    RecoveryCaseObservation,
    RestartRecoveryProtocol,
    RestartRecoveryReport,
    build_restart_recovery_report,
)


def _protocol() -> RestartRecoveryProtocol:
    return RestartRecoveryProtocol(
        protocol_id="restart-contract-v1",
        case_ids=tuple(f"RR-{index:02d}" for index in range(1, 11)),
    )


def _cases() -> tuple[RecoveryCaseObservation, ...]:
    expected = {
        "RR-01": "interrupted",
        "RR-02": "interrupted",
        "RR-03": "uncertain",
        "RR-04": "uncertain",
        "RR-05": "UNCERTAIN",
        "RR-06": "UNCERTAIN",
        "RR-07": "PENDING_CONFIRMATION",
        "RR-08": "ACCEPTED",
        "RR-09": "owner_visible_cross_tenant_hidden",
        "RR-10": "no_additional_transitions",
    }
    return tuple(
        RecoveryCaseObservation(
            case_id=case_id,
            expected_state=state,
            observed_state=state,
            transition_count_delta=1 if case_id in {"RR-01", "RR-02", "RR-03", "RR-04", "RR-05", "RR-06"} else 0,
            expectation_met=True,
        )
        for case_id, state in expected.items()
    )


def _report() -> RestartRecoveryReport:
    return build_restart_recovery_report(
        _protocol(),
        cases=_cases(),
        startup_recovered_execution_count=4,
        startup_interrupted_runtime_count=2,
        startup_uncertain_action_execution_count=2,
        startup_uncertain_custody_count=1,
        startup_uncertain_claim_count=1,
        second_startup_recovered_execution_count=0,
        second_startup_recovered_custody_count=0,
        second_startup_recovered_claim_count=0,
        transport_replay_count=0,
        automatic_retry_count=0,
        real_customer_mutations=0,
        authenticated_tenant_isolation_preserved=True,
        second_restart_idempotent=True,
    )


def test_restart_recovery_report_is_hash_bound_and_fail_safe() -> None:
    report = _report()
    assert report.status == "MEASURED"
    assert report.denominator == 10
    assert report.expectations_passed == 10
    assert report.startup_recovered_execution_count == 4
    assert report.startup_interrupted_runtime_count == 2
    assert report.startup_uncertain_action_execution_count == 2
    assert report.startup_uncertain_custody_count == 1
    assert report.startup_uncertain_claim_count == 1
    assert report.second_startup_recovered_execution_count == 0
    assert report.transport_replay_count == 0
    assert report.automatic_retry_count == 0
    assert report.real_customer_mutations == 0
    assert report.authenticated_tenant_isolation_preserved is True
    assert report.second_restart_idempotent is True
    assert len(report.evidence_sha256) == 64


def test_restart_recovery_builder_rejects_missing_cases_replay_retry_or_failed_invariant() -> None:
    kwargs = dict(
        startup_recovered_execution_count=4,
        startup_interrupted_runtime_count=2,
        startup_uncertain_action_execution_count=2,
        startup_uncertain_custody_count=1,
        startup_uncertain_claim_count=1,
        second_startup_recovered_execution_count=0,
        second_startup_recovered_custody_count=0,
        second_startup_recovered_claim_count=0,
        transport_replay_count=0,
        automatic_retry_count=0,
        real_customer_mutations=0,
        authenticated_tenant_isolation_preserved=True,
        second_restart_idempotent=True,
    )
    with pytest.raises(ValueError, match="frozen protocol"):
        build_restart_recovery_report(_protocol(), cases=_cases()[:-1], **kwargs)
    with pytest.raises(ValueError, match="replay transport"):
        build_restart_recovery_report(
            _protocol(), cases=_cases(), **{**kwargs, "transport_replay_count": 1}
        )
    with pytest.raises(ValueError, match="automatically retry"):
        build_restart_recovery_report(
            _protocol(), cases=_cases(), **{**kwargs, "automatic_retry_count": 1}
        )
    with pytest.raises(ValueError, match="tenant isolation"):
        build_restart_recovery_report(
            _protocol(),
            cases=_cases(),
            **{**kwargs, "authenticated_tenant_isolation_preserved": False},
        )


def test_recovery_case_and_report_reject_inconsistent_flags_and_hash_tampering() -> None:
    with pytest.raises(ValidationError, match="expectation flag"):
        RecoveryCaseObservation(
            case_id="RR-01",
            expected_state="interrupted",
            observed_state="running",
            expectation_met=True,
        )

    payload = _report().model_dump(mode="json")
    payload["startup_recovered_execution_count"] = 99
    with pytest.raises(ValidationError, match="evidence hash mismatch"):
        RestartRecoveryReport.model_validate(payload)
