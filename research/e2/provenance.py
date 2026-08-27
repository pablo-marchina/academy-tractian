from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .hash import sha256_json

@dataclass(frozen=True)
class ArtifactRef:
    name: str
    sha256: str


def build_config_hash(config: dict[str, Any]) -> str:
    return sha256_json(config)


def build_run_manifest(*, config: dict[str, Any], artifacts: list[ArtifactRef], scenario_id: str, run_id: str) -> dict[str, Any]:
    manifest = {
        "manifest_version": "run-manifest-v1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "config_hash": build_config_hash(config),
        "artifacts": [{"name": a.name, "sha256": a.sha256} for a in sorted(artifacts, key=lambda x: x.name)],
    }
    manifest["manifest_hash"] = sha256_json(manifest)
    return manifest
