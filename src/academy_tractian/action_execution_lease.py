from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


ACTION_EXECUTION_LEASE_SCHEMA_VERSION = "action-execution-lease-v1"


@dataclass(frozen=True, slots=True)
class ActionExecutionLeaseClaim:
    """One non-transferable ownership token for a consequential action attempt.

    Unlike read-only runtime handoff, an expired action lease is never reclaimable for another
    transport attempt. Expiry means the external side effect may have happened and the action must
    converge to UNCERTAIN until a human or an external idempotency source resolves it.
    """

    action_id: str
    execution_run_id: str
    owner_instance_id: str
    generation: int


@dataclass(frozen=True, slots=True)
class ActionExecutionRecoveryReport:
    actions_marked_uncertain: tuple[str, ...]
    execution_runs_marked_uncertain: tuple[str, ...]
    ledger_entries_marked_uncertain: tuple[str, ...]


class ActionExecutionLeaseStore(Protocol):
    def ready(self) -> bool: ...

    def acquire(
        self,
        *,
        action_id: str,
        execution_run_id: str,
        owner_instance_id: str,
        lease_seconds: float,
    ) -> ActionExecutionLeaseClaim | None: ...

    def renew(
        self,
        *,
        claim: ActionExecutionLeaseClaim,
        lease_seconds: float,
    ) -> bool: ...

    def is_current_owner(self, claim: ActionExecutionLeaseClaim) -> bool: ...

    def release_terminal(self, claim: ActionExecutionLeaseClaim) -> bool: ...

    def reconcile_expired(self) -> ActionExecutionRecoveryReport: ...

    def snapshot(self) -> dict[str, Any]: ...


class ActionExecutionLeaseLost(RuntimeError):
    pass


class ActionExecutionLeaseGuard:
    """Fail-closed guard used immediately before side effects and terminal writes."""

    def __init__(self, store: ActionExecutionLeaseStore, claim: ActionExecutionLeaseClaim) -> None:
        self.store = store
        self.claim = claim

    def assert_active(self) -> None:
        if not self.store.is_current_owner(self.claim):
            raise ActionExecutionLeaseLost("action_execution_lease_not_current")
