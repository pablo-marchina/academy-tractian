from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field


ARTIFACT_RELEASE_IDENTITY_PATH = Path("/app/.academy-release-identity.json")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class ArtifactReleaseIdentity(BaseModel):
    """Immutable identity baked into the production container at build time."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["academy-release-artifact-v1"]
    git_sha: str = Field(pattern=r"^[0-9a-f]{40}$")


def load_artifact_release_identity(
    path: Path = ARTIFACT_RELEASE_IDENTITY_PATH,
) -> ArtifactReleaseIdentity:
    """Load the image identity and fail closed on absence, corruption, or drift."""

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("production_release_identity_missing_or_unreadable") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("production_release_identity_invalid_json") from exc

    try:
        return ArtifactReleaseIdentity.model_validate(payload)
    except ValueError as exc:
        raise RuntimeError("production_release_identity_invalid_contract") from exc


def build_verified_release_metadata(
    *,
    configured_metadata: Mapping[str, object],
    artifact_identity: ArtifactReleaseIdentity,
    railway_runtime_git_sha: str | None = None,
) -> dict[str, object]:
    """Bind public release metadata to the immutable image identity.

    The baked artifact is authoritative. Runtime configuration may add deployment
    metadata, but it cannot claim a different source commit. When Railway exposes
    its runtime commit SHA, that independent signal must agree as well.
    """

    configured_git_sha = configured_metadata.get("release_git_sha")
    if not isinstance(configured_git_sha, str) or not _SHA40.fullmatch(configured_git_sha):
        raise RuntimeError("production_release_identity_invalid_configured_sha")
    if configured_git_sha != artifact_identity.git_sha:
        raise RuntimeError("production_release_identity_config_artifact_mismatch")

    if railway_runtime_git_sha is not None:
        if not _SHA40.fullmatch(railway_runtime_git_sha):
            raise RuntimeError("production_release_identity_invalid_railway_runtime_sha")
        if railway_runtime_git_sha != artifact_identity.git_sha:
            raise RuntimeError("production_release_identity_railway_artifact_mismatch")

    verified = dict(configured_metadata)
    verified["schema_version"] = "remote-production-release-v3"
    verified["artifact_git_sha"] = artifact_identity.git_sha
    verified["artifact_identity_schema_version"] = artifact_identity.schema_version
    verified["artifact_identity_verified"] = True
    verified["railway_runtime_identity_verified"] = railway_runtime_git_sha is not None
    return verified
