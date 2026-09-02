from __future__ import annotations

from hashlib import sha1
from pathlib import Path

from academy_tractian.cloudflare_frozen_bundle_portability import (
    PINNED_FROZEN_INPUTS,
    materialize_canonical_frozen_bundle,
    worktree_bytes_equivalent_to_canonical,
)


def _git_blob_sha1(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def test_crlf_only_difference_is_equivalent() -> None:
    canonical = b'{"schema_version":"fixture"}\n{"x":1}\n'
    windows = canonical.replace(b"\n", b"\r\n")
    assert windows != canonical
    assert worktree_bytes_equivalent_to_canonical(windows, canonical)


def test_material_content_drift_is_not_equivalent() -> None:
    canonical = b'{"x":1}\n'
    changed = b'{"x":2}\r\n'
    assert not worktree_bytes_equivalent_to_canonical(changed, canonical)


def test_materialize_uses_exact_pinned_git_object_bytes(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    materialized = materialize_canonical_frozen_bundle(
        repo_root=repo_root,
        target_root=tmp_path,
    )

    assert len(materialized) == len(PINNED_FROZEN_INPUTS) == 5
    expected = dict(PINNED_FROZEN_INPUTS)
    for destination in materialized:
        relative = destination.relative_to(tmp_path).as_posix()
        assert _git_blob_sha1(destination.read_bytes()) == expected[relative]
