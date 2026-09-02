from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import subprocess

from .cloudflare_provider_comparison_v2 import (
    ADR_018_GIT_BLOB,
    ADR_018_PATH,
    ADR_019_GIT_BLOB,
    ADR_019_PATH,
    CLOUDFLARE_CLIENT_GIT_BLOB,
    CLOUDFLARE_CLIENT_PATH,
    DESIGN_V2_GIT_BLOB,
    DESIGN_V2_PATH,
    POPULATION_GIT_BLOB,
    POPULATION_PATH,
)


class CloudflareFrozenBundlePortabilityError(RuntimeError):
    pass


PINNED_FROZEN_INPUTS: tuple[tuple[str, str], ...] = (
    (DESIGN_V2_PATH, DESIGN_V2_GIT_BLOB),
    (POPULATION_PATH, POPULATION_GIT_BLOB),
    (ADR_018_PATH, ADR_018_GIT_BLOB),
    (ADR_019_PATH, ADR_019_GIT_BLOB),
    (CLOUDFLARE_CLIENT_PATH, CLOUDFLARE_CLIENT_GIT_BLOB),
)


def _git_blob_sha1(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _normalize_line_endings(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def worktree_bytes_equivalent_to_canonical(worktree: bytes, canonical: bytes) -> bool:
    if worktree == canonical:
        return True
    return _normalize_line_endings(worktree) == _normalize_line_endings(canonical)


def _git_show_head_bytes(repo_root: Path, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CloudflareFrozenBundlePortabilityError(
            f"cannot resolve canonical Git object for frozen input: {path}"
        )
    return completed.stdout


def materialize_canonical_frozen_bundle(
    *,
    repo_root: Path | str,
    target_root: Path | str,
) -> tuple[Path, ...]:
    """Materialize exact pinned Git bytes without trusting platform line endings.

    A dirty worktree is accepted only when its bytes differ from the canonical Git
    object by line-ending normalization alone. Any material content drift fails
    closed. The returned files always contain the exact pinned Git-object bytes.
    """

    source_root = Path(repo_root).resolve()
    destination_root = Path(target_root).resolve()
    materialized: list[Path] = []

    for path, expected_blob in PINNED_FROZEN_INPUTS:
        source_path = source_root / path
        if not source_path.is_file():
            raise CloudflareFrozenBundlePortabilityError(
                f"frozen worktree input missing: {path}"
            )

        canonical = _git_show_head_bytes(source_root, path)
        if _git_blob_sha1(canonical) != expected_blob:
            raise CloudflareFrozenBundlePortabilityError(
                f"canonical Git object does not match frozen blob: {path}"
            )

        worktree = source_path.read_bytes()
        if not worktree_bytes_equivalent_to_canonical(worktree, canonical):
            raise CloudflareFrozenBundlePortabilityError(
                f"material frozen worktree drift detected: {path}"
            )

        destination = destination_root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(canonical)
        materialized.append(destination)

    return tuple(materialized)
