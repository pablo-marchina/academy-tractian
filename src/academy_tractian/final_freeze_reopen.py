from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from academy_tractian.handoff_audit import git_blob_sha1


FINAL_FREEZE_REOPEN_PATH = "research/results/final-freeze-reopen-2026-09-04.json"


class FinalFreezeReopenManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["final-freeze-reopen-v1"] = "final-freeze-reopen-v1"
    state: Literal["FREEZE_REOPENED"] = "FREEZE_REOPENED"
    date: Literal["2026-09-04"] = "2026-09-04"
    superseded_manifest_path: str = Field(min_length=1)
    superseded_manifest_git_blob_sha1: str = Field(pattern=r"^[0-9a-f]{40}$")
    superseded_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reopen_reason: str = Field(min_length=1)
    hard_constraints: dict[str, object]
    blocking_gates: tuple[str, ...] = Field(min_length=1)
    non_claims: tuple[str, ...] = Field(min_length=1)
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _verify_hash(self) -> "FinalFreezeReopenManifest":
        payload = self.model_dump(mode="json", exclude={"manifest_sha256"})
        expected = compute_manifest_sha256(payload)
        if self.manifest_sha256 != expected:
            raise ValueError("final freeze reopen manifest hash mismatch")
        return self


def compute_manifest_sha256(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(canonical.encode("utf-8")).hexdigest()


def load_final_freeze_reopen_manifest(root: Path) -> FinalFreezeReopenManifest:
    payload = json.loads((root / FINAL_FREEZE_REOPEN_PATH).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("final freeze reopen manifest root must be an object")
    return FinalFreezeReopenManifest.model_validate(payload)


def validate_final_freeze_reopen_manifest(
    manifest: FinalFreezeReopenManifest,
    root: Path,
) -> list[str]:
    failures: list[str] = []

    superseded = root / manifest.superseded_manifest_path
    if not superseded.is_file():
        failures.append("superseded_manifest_missing")
    else:
        observed_blob = git_blob_sha1(superseded.read_bytes())
        if observed_blob != manifest.superseded_manifest_git_blob_sha1:
            failures.append("superseded_manifest_blob_mismatch")

    constraints = manifest.hard_constraints
    if constraints.get("local_required_components_target") != 0:
        failures.append("local_required_components_target")
    if constraints.get("production_path_hosted_only") is not True:
        failures.append("production_path_hosted_only")
    if constraints.get("multi_user_required") is not True:
        failures.append("multi_user_required")
    if constraints.get("no_demo_only_path") is not True:
        failures.append("no_demo_only_path")

    if len(set(manifest.blocking_gates)) != len(manifest.blocking_gates):
        failures.append("duplicate_blocking_gate")
    if len(set(manifest.non_claims)) != len(manifest.non_claims):
        failures.append("duplicate_non_claim")

    required_non_claims = {
        "hard_freeze_currently_effective",
        "unconditional_production_readiness",
        "hosted_postgres_pilot_passed",
        "production_provider_selected",
        "hosted_consequential_actions_qualified",
        "hosted_full_product_e2e_passed",
        "human_semantic_calibration_complete",
        "branch_protection_enforced",
    }
    if not required_non_claims.issubset(set(manifest.non_claims)):
        failures.append("required_non_claims")

    return failures
