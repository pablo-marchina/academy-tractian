from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from academy_tractian.live_deployment_attestation import (
    LiveDeploymentPolicy,
    build_live_deployment_attestation,
    decide_live_deployment_attestation,
)


NOW = datetime(2026, 9, 4, 21, 0, tzinfo=UTC)
EXPECTED_SHA = "a" * 40
POLICY = LiveDeploymentPolicy(
    require_exact_source_revision=True,
    require_exact_branch=True,
    approved_build_contracts=("root-dockerfile",),
    required_python_major_minor="3.11",
)


def _evidence(**overrides):
    payload = {
        "candidate_id": "test-host",
        "deployment_id": "deployment-1",
        "collected_at": NOW,
        "expected_source_revision": EXPECTED_SHA,
        "observed_source_revision": EXPECTED_SHA,
        "expected_branch": "feat/cloud-production-baseline",
        "observed_branch": "feat/cloud-production-baseline",
        "expected_build_contract": "root-dockerfile",
        "observed_build_contract": "root-dockerfile",
        "expected_python_major_minor": "3.11",
        "observed_python_version": "3.11.14",
    }
    payload.update(overrides)
    return build_live_deployment_attestation(**payload)


def test_exact_source_build_and_runtime_pass() -> None:
    decision = decide_live_deployment_attestation(evidence=_evidence(), policy=POLICY)
    assert decision.outcome == "LIVE_ATTESTATION_PASS"
    assert decision.reason_codes == ()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"observed_source_revision": "b" * 40}, "SOURCE_REVISION_MISMATCH"),
        ({"observed_source_revision": None}, "SOURCE_REVISION_NOT_OBSERVED"),
        ({"observed_branch": "main"}, "SOURCE_BRANCH_MISMATCH"),
        ({"observed_branch": None}, "SOURCE_BRANCH_NOT_OBSERVED"),
        ({"observed_build_contract": "railpack"}, "OBSERVED_BUILD_CONTRACT_NOT_APPROVED"),
        ({"observed_build_contract": "unknown"}, "OBSERVED_BUILD_CONTRACT_NOT_APPROVED"),
        ({"observed_python_version": "3.13.15"}, "PYTHON_RUNTIME_MISMATCH"),
        ({"observed_python_version": None}, "PYTHON_RUNTIME_NOT_OBSERVED"),
    ],
)
def test_live_execution_hard_gates_are_non_compensatory(overrides, reason: str) -> None:
    decision = decide_live_deployment_attestation(
        evidence=_evidence(**overrides), policy=POLICY
    )
    assert decision.outcome == "LIVE_ATTESTATION_FAIL"
    assert reason in decision.reason_codes


def test_wrong_build_contract_also_reports_contract_mismatch() -> None:
    decision = decide_live_deployment_attestation(
        evidence=_evidence(observed_build_contract="railpack"), policy=POLICY
    )
    assert decision.outcome == "LIVE_ATTESTATION_FAIL"
    assert "BUILD_CONTRACT_MISMATCH" in decision.reason_codes


def test_expected_runtime_cannot_silently_drift_from_policy() -> None:
    decision = decide_live_deployment_attestation(
        evidence=_evidence(expected_python_major_minor="3.13", observed_python_version="3.13.15"),
        policy=POLICY,
    )
    assert decision.outcome == "LIVE_ATTESTATION_FAIL"
    assert "EXPECTED_PYTHON_RUNTIME_NOT_APPROVED" in decision.reason_codes


def test_attestation_is_hash_bound() -> None:
    evidence = _evidence()
    payload = evidence.model_dump(mode="json")
    payload["observed_branch"] = "main"
    with pytest.raises(ValidationError, match="live_deployment_attestation_hash_mismatch"):
        type(evidence).model_validate(payload)
