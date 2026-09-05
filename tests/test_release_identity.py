from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from academy_tractian.release_identity import (
    ArtifactReleaseIdentity,
    build_verified_release_metadata,
    load_artifact_release_identity,
)


SHA = "a" * 40
BASE_METADATA: dict[str, object] = {
    "schema_version": "remote-production-release-v2",
    "release_git_sha": SHA,
    "deployment_id": "deploy-test",
}


def test_artifact_identity_loads_only_exact_frozen_contract(tmp_path) -> None:
    path = tmp_path / "identity.json"
    path.write_text(
        json.dumps({"schema_version": "academy-release-artifact-v1", "git_sha": SHA}),
        encoding="utf-8",
    )

    identity = load_artifact_release_identity(path)

    assert identity == ArtifactReleaseIdentity(
        schema_version="academy-release-artifact-v1",
        git_sha=SHA,
    )
    with pytest.raises(ValidationError):
        identity.git_sha = "b" * 40  # type: ignore[misc]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("not-json", "invalid_json"),
        (json.dumps({"schema_version": "academy-release-artifact-v1"}), "invalid_contract"),
        (
            json.dumps(
                {
                    "schema_version": "academy-release-artifact-v1",
                    "git_sha": SHA.upper(),
                }
            ),
            "invalid_contract",
        ),
        (
            json.dumps(
                {
                    "schema_version": "academy-release-artifact-v1",
                    "git_sha": SHA,
                    "runtime_override": True,
                }
            ),
            "invalid_contract",
        ),
    ],
)
def test_artifact_identity_rejects_corrupt_or_drifted_contract(
    tmp_path,
    payload: str,
    message: str,
) -> None:
    path = tmp_path / "identity.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(RuntimeError, match=message):
        load_artifact_release_identity(path)


def test_artifact_identity_is_mandatory(tmp_path) -> None:
    with pytest.raises(RuntimeError, match="missing_or_unreadable"):
        load_artifact_release_identity(tmp_path / "missing.json")


def test_verified_metadata_binds_config_artifact_and_railway_runtime_sha() -> None:
    identity = ArtifactReleaseIdentity(
        schema_version="academy-release-artifact-v1",
        git_sha=SHA,
    )

    metadata = build_verified_release_metadata(
        configured_metadata=BASE_METADATA,
        artifact_identity=identity,
        railway_runtime_git_sha=SHA,
    )

    assert metadata == {
        **BASE_METADATA,
        "schema_version": "remote-production-release-v3",
        "artifact_git_sha": SHA,
        "artifact_identity_schema_version": "academy-release-artifact-v1",
        "artifact_identity_verified": True,
        "railway_runtime_identity_verified": True,
    }


def test_verified_metadata_fails_closed_on_any_identity_disagreement() -> None:
    identity = ArtifactReleaseIdentity(
        schema_version="academy-release-artifact-v1",
        git_sha=SHA,
    )

    with pytest.raises(RuntimeError, match="config_artifact_mismatch"):
        build_verified_release_metadata(
            configured_metadata={**BASE_METADATA, "release_git_sha": "b" * 40},
            artifact_identity=identity,
        )

    with pytest.raises(RuntimeError, match="railway_artifact_mismatch"):
        build_verified_release_metadata(
            configured_metadata=BASE_METADATA,
            artifact_identity=identity,
            railway_runtime_git_sha="c" * 40,
        )

    with pytest.raises(RuntimeError, match="invalid_railway_runtime_sha"):
        build_verified_release_metadata(
            configured_metadata=BASE_METADATA,
            artifact_identity=identity,
            railway_runtime_git_sha="abc123",
        )
