from __future__ import annotations

from pathlib import Path

from academy_tractian.cloudflare_frozen_bundle_portability import (
    materialize_canonical_frozen_bundle,
)
from academy_tractian.cloudflare_provider_live_v2 import (
    run_cloudflare_provider_free_fixed_failure_probes_v2,
)


def test_provider_free_fixed_failure_probes_run_from_canonical_frozen_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    frozen_root = tmp_path / "frozen"
    materialize_canonical_frozen_bundle(
        repo_root=repo_root,
        target_root=frozen_root,
    )

    monkeypatch.chdir(frozen_root)
    outcomes = run_cloudflare_provider_free_fixed_failure_probes_v2()

    assert outcomes
    assert all(outcomes.values())
