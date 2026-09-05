from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Literal, Protocol


RUN_ACCESS_SCHEMA_VERSION = "run-access-v1"
RUN_EXECUTION_SCHEMA_VERSION = "run-execution-store-v1"
RUNTIME_HANDOFF_SCHEMA_VERSION = "runtime-handoff-v1"

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


@dataclass(frozen=True, slots=True)
class RuntimeExecutionEnvelope:
    """Private durable input required to reconstruct a read-only runtime after replica loss.

    This object is server-internal and must never be exposed through browser-safe observability.
    Production stores should retain it only while the execution is non-terminal.
    """

    run_id: str
    request_id: str
    identity_id: str
    user_id: str
    user_request: str
    seed: str | None = None


@dataclass(frozen=True, slots=True)
class RuntimeHandoffClaim:
    envelope: RuntimeExecutionEnvelope
    owner_instance_id: str
    claim_generation: int
    previous_state: ExecutionState
    recovery_count: int


class RuntimeHandoffStore(Protocol):
    """Durable multi-replica queue/lease contract for read-only runtime executions only.

    Consequential action executions deliberately do not use this automatic replay path.
    A generation token fences tool access, projection writes and terminal state from stale workers
    after handoff.
    """

    def ready(self) -> bool: ...

    def enqueue(self, envelope: RuntimeExecutionEnvelope) -> None: ...

    def claim_specific(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        lease_seconds: float,
    ) -> RuntimeHandoffClaim | None: ...

    def claim_available(
        self,
        *,
        owner_instance_id: str,
        lease_seconds: float,
        limit: int,
    ) -> tuple[RuntimeHandoffClaim, ...]: ...

    def is_current_owner(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
    ) -> bool: ...

    def renew(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
        lease_seconds: float,
    ) -> bool: ...

    def complete(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
    ) -> bool: ...

    def fail(
        self,
        *,
        run_id: str,
        owner_instance_id: str,
        claim_generation: int,
    ) -> bool: ...

    def reconcile_unrecoverable(self) -> tuple[DurableExecution, ...]: ...

    def snapshot(self) -> dict[str, Any]: ...
