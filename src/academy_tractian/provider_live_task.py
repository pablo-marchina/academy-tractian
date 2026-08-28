from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .provider_comparison import (
    build_provider_comparison_plan,
    load_frozen_provider_comparison_bundle,
)
from .provider_live_execution import (
    EXPECTED_PLAN_SHA256,
    LIVE_PROVIDER_EXECUTION_VERSION,
    ExistingLiveRunError,
    GovernedLiveProviderComparison,
    LiveComparisonExecutionResult,
    LiveProviderSecrets,
)


LIVE_PROVIDER_TASK_VERSION = "provider-live-task-v1"
CUSTODY_FILENAME = "adr-009-live-comparison-custody.json"
CANONICAL_RUN_DIRNAME = "run"


class ExistingAuthorizationCustodyError(ExistingLiveRunError):
    """ADR-009 already has durable execution custody in this governed root."""


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuthorizationCustodyRecord(_FrozenModel):
    schema_version: Literal["provider-live-authorization-custody-v1"] = (
        "provider-live-authorization-custody-v1"
    )
    task_version: Literal["provider-live-task-v1"] = LIVE_PROVIDER_TASK_VERSION
    wrapper_version: Literal["provider-live-execution-v1"] = LIVE_PROVIDER_EXECUTION_VERSION
    authorization_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    canonical_run_dirname: Literal["run"] = CANONICAL_RUN_DIRNAME
    state: Literal["reserved"] = "reserved"
    live_calls_consumed_at_reservation: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False


def _fsync_directory(path: Path) -> None:
    """Best-effort directory durability for POSIX execution custody."""
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _reserve_authorization_custody(
    *,
    custody_root: Path,
    record: AuthorizationCustodyRecord,
) -> Path:
    custody_root.mkdir(parents=True, exist_ok=True)
    path = custody_root / CUSTODY_FILENAME
    data = json.dumps(
        record.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ExistingAuthorizationCustodyError(
            "ADR-009 authorization custody already exists; refusing a second run or budget reset"
        ) from exc

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(custody_root)
    except Exception:
        # Fail closed: once exclusive custody was obtained, never remove it automatically.
        raise
    return path


@dataclass
class GovernedProviderLiveTask:
    """Authorization-level entrypoint for the single ADR-009 live comparison.

    The lower-level `GovernedLiveProviderComparison` remains useful execution plumbing, but direct
    live use is not the governed entrypoint. This task first reserves one durable ADR-009 custody
    marker and then fixes the lower-level run directory to `<custody_root>/run`. Restarting with
    the same canonical custody root therefore cannot switch to a fresh run directory to reset the
    in-memory ADR-010 budget.

    A different custody root is a different external custody decision and is not authorized by
    this class or ADR-011; the separately governed live task must provision one canonical durable
    root and preserve it as execution evidence.
    """

    custody_root: Path
    custody_path: Path
    execution: GovernedLiveProviderComparison

    @classmethod
    def prepare(
        cls,
        *,
        custody_root: Path | str,
        secrets: LiveProviderSecrets,
        repo_root: Path | str = ".",
    ) -> "GovernedProviderLiveTask":
        # Missing secrets must fail before even reserving the authorization custody marker.
        secrets.validate_presence()

        bundle = load_frozen_provider_comparison_bundle(repo_root)
        plan = build_provider_comparison_plan(bundle)
        if plan.plan_sha256 != EXPECTED_PLAN_SHA256:
            raise ValueError("canonical ADR-010 plan SHA-256 drift")

        root = Path(custody_root)
        record = AuthorizationCustodyRecord(
            authorization_blob=bundle.authorization_blob,
            plan_sha256=plan.plan_sha256,
        )
        custody_path = _reserve_authorization_custody(
            custody_root=root,
            record=record,
        )

        # The run path is not caller-selectable. If preparation fails from this point onward, the
        # custody marker intentionally remains and blocks automatic retry/reset.
        execution = GovernedLiveProviderComparison.prepare(
            run_dir=root / CANONICAL_RUN_DIRNAME,
            secrets=secrets,
            repo_root=repo_root,
        )
        return cls(
            custody_root=root,
            custody_path=custody_path,
            execution=execution,
        )

    def execute_all(self) -> LiveComparisonExecutionResult:
        return self.execution.execute_all()
