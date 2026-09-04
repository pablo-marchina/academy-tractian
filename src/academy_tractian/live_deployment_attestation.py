from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _canonical_sha256(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _canonical_datetime(value: datetime) -> str:
    rendered = value.isoformat()
    return rendered[:-6] + "Z" if rendered.endswith("+00:00") else rendered


BuildContract = Literal["root-dockerfile", "railpack", "buildpack", "custom", "unknown"]


class LiveDeploymentAttestation(_StrictModel):
    """Secret-safe evidence that a hosted pilot executed the intended source/build contract.

    Static provider documentation can admit a candidate to a pilot, but it cannot prove what was
    actually deployed. This attestation is therefore a separate, post-admission hard gate that must
    pass before a live deployment is allowed to mutate production-candidate infrastructure.
    """

    schema_version: Literal["live-deployment-attestation-v1"] = "live-deployment-attestation-v1"
    candidate_id: str = Field(min_length=1, max_length=128)
    deployment_id: str = Field(min_length=1, max_length=256)
    collected_at: datetime
    expected_source_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    observed_source_revision: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    expected_branch: str = Field(min_length=1, max_length=256)
    observed_branch: str | None = Field(default=None, max_length=256)
    expected_build_contract: BuildContract
    observed_build_contract: BuildContract
    expected_python_major_minor: str = Field(pattern=r"^\d+\.\d+$")
    observed_python_version: str | None = Field(default=None, pattern=r"^\d+\.\d+(?:\.\d+)?$")
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_integrity(self) -> "LiveDeploymentAttestation":
        material = self.model_dump(mode="json", exclude={"artifact_sha256"})
        if self.artifact_sha256 != _canonical_sha256(material):
            raise ValueError("live_deployment_attestation_hash_mismatch")
        return self


class LiveDeploymentPolicy(_StrictModel):
    schema_version: Literal["live-deployment-policy-v1"] = "live-deployment-policy-v1"
    require_exact_source_revision: bool = True
    require_exact_branch: bool = True
    approved_build_contracts: tuple[BuildContract, ...] = ("root-dockerfile",)
    required_python_major_minor: str = Field(default="3.11", pattern=r"^\d+\.\d+$")

    @model_validator(mode="after")
    def validate_policy(self) -> "LiveDeploymentPolicy":
        if not self.approved_build_contracts:
            raise ValueError("live_deployment_approved_build_contracts_empty")
        if len(set(self.approved_build_contracts)) != len(self.approved_build_contracts):
            raise ValueError("live_deployment_duplicate_build_contract")
        return self


LiveDeploymentOutcome = Literal["LIVE_ATTESTATION_PASS", "LIVE_ATTESTATION_FAIL"]


class LiveDeploymentDecision(_StrictModel):
    schema_version: Literal["live-deployment-decision-v1"] = "live-deployment-decision-v1"
    candidate_id: str
    deployment_id: str
    outcome: LiveDeploymentOutcome
    reason_codes: tuple[str, ...]
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _major_minor(version: str) -> str:
    parts = version.split(".")
    return ".".join(parts[:2])


def decide_live_deployment_attestation(
    *, evidence: LiveDeploymentAttestation, policy: LiveDeploymentPolicy
) -> LiveDeploymentDecision:
    reasons: list[str] = []

    if evidence.observed_source_revision is None:
        reasons.append("SOURCE_REVISION_NOT_OBSERVED")
    elif policy.require_exact_source_revision and (
        evidence.observed_source_revision != evidence.expected_source_revision
    ):
        reasons.append("SOURCE_REVISION_MISMATCH")

    if evidence.observed_branch is None:
        reasons.append("SOURCE_BRANCH_NOT_OBSERVED")
    elif policy.require_exact_branch and evidence.observed_branch != evidence.expected_branch:
        reasons.append("SOURCE_BRANCH_MISMATCH")

    if evidence.expected_build_contract not in policy.approved_build_contracts:
        reasons.append("EXPECTED_BUILD_CONTRACT_NOT_APPROVED")
    if evidence.observed_build_contract not in policy.approved_build_contracts:
        reasons.append("OBSERVED_BUILD_CONTRACT_NOT_APPROVED")
    if evidence.observed_build_contract != evidence.expected_build_contract:
        reasons.append("BUILD_CONTRACT_MISMATCH")

    if evidence.expected_python_major_minor != policy.required_python_major_minor:
        reasons.append("EXPECTED_PYTHON_RUNTIME_NOT_APPROVED")
    if evidence.observed_python_version is None:
        reasons.append("PYTHON_RUNTIME_NOT_OBSERVED")
    elif _major_minor(evidence.observed_python_version) != policy.required_python_major_minor:
        reasons.append("PYTHON_RUNTIME_MISMATCH")

    return LiveDeploymentDecision(
        candidate_id=evidence.candidate_id,
        deployment_id=evidence.deployment_id,
        outcome="LIVE_ATTESTATION_FAIL" if reasons else "LIVE_ATTESTATION_PASS",
        reason_codes=tuple(dict.fromkeys(reasons)),
        evidence_sha256=evidence.artifact_sha256,
    )


def build_live_deployment_attestation(
    *,
    candidate_id: str,
    deployment_id: str,
    collected_at: datetime,
    expected_source_revision: str,
    observed_source_revision: str | None,
    expected_branch: str,
    observed_branch: str | None,
    expected_build_contract: BuildContract,
    observed_build_contract: BuildContract,
    expected_python_major_minor: str,
    observed_python_version: str | None,
) -> LiveDeploymentAttestation:
    material = {
        "schema_version": "live-deployment-attestation-v1",
        "candidate_id": candidate_id,
        "deployment_id": deployment_id,
        "collected_at": _canonical_datetime(collected_at),
        "expected_source_revision": expected_source_revision,
        "observed_source_revision": observed_source_revision,
        "expected_branch": expected_branch,
        "observed_branch": observed_branch,
        "expected_build_contract": expected_build_contract,
        "observed_build_contract": observed_build_contract,
        "expected_python_major_minor": expected_python_major_minor,
        "observed_python_version": observed_python_version,
    }
    return LiveDeploymentAttestation.model_validate(
        {**material, "artifact_sha256": _canonical_sha256(material)}
    )
