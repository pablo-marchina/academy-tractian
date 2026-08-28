from __future__ import annotations

import json
from pathlib import Path

import pytest

import academy_tractian.provider_live_task as task
from academy_tractian.provider_live_execution import (
    LiveProviderSecrets,
    MissingProviderSecretsError,
)


def _secrets() -> LiveProviderSecrets:
    return LiveProviderSecrets(
        openai_api_key="openai-custody-test-secret",
        google_api_key="google-custody-test-secret",
    )


def test_missing_secret_fails_before_authorization_custody_exists(tmp_path: Path) -> None:
    custody_root = tmp_path / "custody"
    with pytest.raises(MissingProviderSecretsError):
        task.GovernedProviderLiveTask.prepare(
            custody_root=custody_root,
            secrets=LiveProviderSecrets(
                openai_api_key="",
                google_api_key="google-present",
            ),
        )
    assert not custody_root.exists()


def test_prepare_reserves_one_sanitized_authorization_custody(tmp_path: Path) -> None:
    custody_root = tmp_path / "custody"
    secrets = _secrets()
    prepared = task.GovernedProviderLiveTask.prepare(
        custody_root=custody_root,
        secrets=secrets,
    )

    assert prepared.custody_root == custody_root
    assert prepared.execution.run_dir == custody_root / task.CANONICAL_RUN_DIRNAME
    custody_path = custody_root / task.CUSTODY_FILENAME
    assert custody_path == prepared.custody_path
    assert custody_path.exists()

    payload = json.loads(custody_path.read_text(encoding="utf-8"))
    assert payload["state"] == "reserved"
    assert payload["canonical_run_dirname"] == "run"
    assert payload["live_calls_consumed_at_reservation"] == 0
    assert payload["credentials_recorded"] is False
    assert payload["raw_provider_material_recorded"] is False
    serialized = json.dumps(payload, sort_keys=True)
    assert secrets.openai_api_key not in serialized
    assert secrets.google_api_key not in serialized


def test_same_authorization_custody_cannot_start_second_run(tmp_path: Path) -> None:
    custody_root = tmp_path / "custody"
    task.GovernedProviderLiveTask.prepare(
        custody_root=custody_root,
        secrets=_secrets(),
    )

    with pytest.raises(
        task.ExistingAuthorizationCustodyError,
        match="refusing a second run or budget reset",
    ):
        task.GovernedProviderLiveTask.prepare(
            custody_root=custody_root,
            secrets=_secrets(),
        )


def test_operator_cannot_choose_alternate_run_dir_within_governed_task(tmp_path: Path) -> None:
    custody_root = tmp_path / "custody"
    prepared = task.GovernedProviderLiveTask.prepare(
        custody_root=custody_root,
        secrets=_secrets(),
    )
    assert prepared.execution.run_dir.name == task.CANONICAL_RUN_DIRNAME
    assert prepared.execution.run_dir.parent == custody_root


def test_failure_after_custody_reservation_leaves_marker_fail_closed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    custody_root = tmp_path / "custody"

    def explode(**kwargs):
        raise RuntimeError("post-custody preparation failure")

    monkeypatch.setattr(task.GovernedLiveProviderComparison, "prepare", explode)

    with pytest.raises(RuntimeError, match="post-custody preparation failure"):
        task.GovernedProviderLiveTask.prepare(
            custody_root=custody_root,
            secrets=_secrets(),
        )

    assert (custody_root / task.CUSTODY_FILENAME).exists()
    with pytest.raises(task.ExistingAuthorizationCustodyError):
        task.GovernedProviderLiveTask.prepare(
            custody_root=custody_root,
            secrets=_secrets(),
        )
