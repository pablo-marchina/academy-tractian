from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Protocol


RUN_ACCESS_SCHEMA_VERSION = "run-access-v1"
RUN_EXECUTION_SCHEMA_VERSION = "run-execution-store-v1"

ExecutionKind = Literal["runtime", "action"]
ExecutionState = Literal[
    "accepted",
    "running",
    "completed",
    "failed",
    "interrupted",
    "uncertain",
]


@dataclass(frozen=True, slots=True)
class RunOwnership:
    run_id: str
    organization_id: str
    user_id: str


class RunAccessStore(Protocol):
    """Engine-independent durable ownership contract used by product authorization."""

    def ready(self) -> bool: ...

    def claim(self, *, run_id: str, organization_id: str, user_id: str) -> bool: ...

    def get(self, run_id: str) -> RunOwnership | None: ...

    def get_many(self, run_ids: Iterable[str]) -> dict[str, RunOwnership]: ...

    def get_scoped(self, *, run_id: str, organization_id: str) -> RunOwnership | None: ...

    def get_many_scoped(
        self,
        *,
        run_ids: Iterable[str],
        organization_id: str,
    ) -> dict[str, RunOwnership]: ...


@dataclass(frozen=True, slots=True)
class DurableExecution:
    run_id: str
    execution_kind: ExecutionKind
    state: ExecutionState
    related_action_id: str | None
    transition_count: int


class RunExecutionStore(Protocol):
    """Engine-independent durable execution-state contract used by product orchestration."""

    def ready(self) -> bool: ...

    def create_accepted(
        self,
        *,
        run_id: str,
        execution_kind: ExecutionKind = "runtime",
        related_action_id: str | None = None,
    ) -> None: ...

    def transition(
        self,
        *,
        run_id: str,
        expected_states: frozenset[str],
        new_state: ExecutionState,
    ) -> bool: ...

    def get(self, run_id: str) -> DurableExecution | None: ...

    def reconcile_orphaned(self) -> tuple[DurableExecution, ...]: ...

    def counts(self) -> dict[str, int]: ...
