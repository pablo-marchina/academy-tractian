from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from academy_tractian.handoff_audit import git_blob_sha1


FINAL_FREEZE_MANIFEST_PATH = "research/results/final-freeze-evidence-bundle-2026-09-04.json"

FreezeRole = Literal[
    "current_contract",
    "current_decision",
    "frozen_historical_evidence",
    "current_reproduction",
    "current_ci",
]

DecisionStatus = Literal[
    "PASS_EVIDENCED",
    "PASS_BOUNDED",
    "NO_SELECTION",
    "NO_CHANGE",
    "NOT_PROMOTED",
    "NOT_READY_HUMAN_DATA",
    "EXTERNALLY_BLOCKED",
    "PENDING_EXTERNAL_ENFORCEMENT",
]

EXPECTED_DECISION_STATUS: dict[str, DecisionStatus] = {
    "FINAL_REQUIRED_CI": "PASS_EVIDENCED",
    "CLEAN_CLONE_REPRODUCTION": "PASS_EVIDENCED",
    "FULL_PRODUCT_BROWSER": "PASS_EVIDENCED",
    "IDENTITY_TENANT": "PASS_EVIDENCED",
    "OPERATIONAL_STORAGE": "PASS_EVIDENCED",
    "RESTART_RECOVERY": "PASS_BOUNDED",
    "LOAD_CAPACITY": "PASS_BOUNDED",
    "PROVIDER_SELECTION": "NO_SELECTION",
    "SEMANTIC_CALIBRATION": "NOT_READY_HUMAN_DATA",
    "ENGINEER_TIME_VALUE": "NOT_READY_HUMAN_DATA",
    "ADAPTIVE_RUNTIME_STOPPING": "NOT_PROMOTED",
    "RUNTIME_HITL_TOPOLOGY": "NO_CHANGE",
    "BRANCH_PROTECTION": "PENDING_EXTERNAL_ENFORCEMENT",
    "C4_SCIENTIFIC_ARTIFACT": "EXTERNALLY_BLOCKED",
}

REQUIRED_NON_CLAIMS = frozenset(
    {
        "production_provider_selected",
        "human_semantic_calibration_complete",
        "engineer_minutes_saved_measured",
        "adaptive_runtime_stopping_improves_product",
        "ci_load_equals_production_capacity",
        "restart_ci_proves_rto_rpo_ha",
        "enterprise_oidc_sso_implemented",
        "langgraph_superior_or_required",
        "branch_protection_enforced",
    }
)


class FreezeArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str = Field(min_length=1)
    git_blob_sha1: str = Field(pattern=r"^[0-9a-f]{40}$")
    role: FreezeRole
    description: str = Field(min_length=1)


class FreezeDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str = Field(min_length=1)
    status: DecisionStatus
    evidence_paths: tuple[str, ...] = Field(min_length=1)
    claim_boundary: str = Field(min_length=1)


class FinalFreezeManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["final-freeze-evidence-bundle-v1"] = (
        "final-freeze-evidence-bundle-v1"
    )
    bundle_state: Literal["READY_FOR_HARD_FREEZE"] = "READY_FOR_HARD_FREEZE"
    bundle_date: Literal["2026-09-04"] = "2026-09-04"
    hard_freeze_effective_date: Literal["2026-09-05"] = "2026-09-05"
    final_delivery_date: Literal["2026-09-08"] = "2026-09-08"
    required_gate_name: Literal["required-gate"] = "required-gate"
    branch_protection_enforced: Literal[False] = False
    artifacts: tuple[FreezeArtifact, ...] = Field(min_length=1)
    decisions: tuple[FreezeDecision, ...] = Field(min_length=1)
    non_claims: tuple[str, ...] = Field(min_length=1)
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_hash(self) -> "FinalFreezeManifest":
        expected = compute_manifest_sha256(self.model_dump(mode="json", exclude={"manifest_sha256"}))
        if self.manifest_sha256 != expected:
            raise ValueError("final freeze manifest hash mismatch")
        return self


def compute_manifest_sha256(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(canonical.encode("utf-8")).hexdigest()


def build_manifest(**values: object) -> FinalFreezeManifest:
    payload = dict(values)
    payload["manifest_sha256"] = compute_manifest_sha256(payload)
    return FinalFreezeManifest.model_validate(payload)


def load_final_freeze_manifest(root: Path) -> FinalFreezeManifest:
    payload = json.loads((root / FINAL_FREEZE_MANIFEST_PATH).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("final freeze manifest root must be an object")
    return FinalFreezeManifest.model_validate(payload)


def validate_final_freeze_manifest(manifest: FinalFreezeManifest, root: Path) -> list[str]:
    failures: list[str] = []

    artifact_paths = [artifact.path for artifact in manifest.artifacts]
    if len(artifact_paths) != len(set(artifact_paths)):
        failures.append("duplicate_artifact_path")

    artifact_set = set(artifact_paths)
    for index, artifact in enumerate(manifest.artifacts):
        relative = Path(artifact.path)
        if relative.is_absolute() or ".." in relative.parts:
            failures.append(f"artifact_{index}_unsafe_path")
            continue
        target = root / relative
        if not target.is_file():
            failures.append(f"artifact_{index}_missing")
            continue
        observed = git_blob_sha1(target.read_bytes())
        if observed != artifact.git_blob_sha1:
            failures.append(f"artifact_{index}_blob_mismatch")

    decision_ids = [decision.decision_id for decision in manifest.decisions]
    if len(decision_ids) != len(set(decision_ids)):
        failures.append("duplicate_decision_id")

    observed_status = {decision.decision_id: decision.status for decision in manifest.decisions}
    if set(observed_status) != set(EXPECTED_DECISION_STATUS):
        failures.append("decision_set")
    else:
        for decision_id, expected_status in EXPECTED_DECISION_STATUS.items():
            if observed_status[decision_id] != expected_status:
                failures.append(f"decision_status_{decision_id}")

    for index, decision in enumerate(manifest.decisions):
        if not decision.claim_boundary.strip():
            failures.append(f"decision_{index}_claim_boundary")
        for evidence_path in decision.evidence_paths:
            if evidence_path not in artifact_set:
                failures.append(f"decision_{index}_unregistered_evidence")

    non_claims = set(manifest.non_claims)
    if len(non_claims) != len(manifest.non_claims):
        failures.append("duplicate_non_claim")
    missing_non_claims = REQUIRED_NON_CLAIMS - non_claims
    if missing_non_claims:
        failures.append("required_non_claims")

    if manifest.branch_protection_enforced is not False:
        failures.append("branch_protection_truthfulness")

    return failures
