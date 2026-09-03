from __future__ import annotations

from hashlib import sha256

from academy_tractian.action_recovery import reconcile_orphaned_actions
from academy_tractian.production_actions_v2 import (
    DuckDBActionIdempotencyLedger,
    PendingActionCustody,
)
from academy_tractian.runtime import canonical_tool_registry


ACTION_ARGS = {
    "analysis_id": "analysis-1",
    "body": {
        "justification": "Evidence reviewed and this exact action requires explicit confirmation before execution."
    },
}


def test_startup_recovery_marks_executing_custody_and_claimed_ledger_uncertain(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "custody.duckdb")
    ledger = DuckDBActionIdempotencyLedger(tmp_path / "ledger.duckdb")
    tool = canonical_tool_registry()["reprocess_analysis"]

    pending = custody.create_or_get(
        origin_raw_run_id="raw-origin-run",
        requester_user_id="user-1",
        tool=tool,
        arguments=ACTION_ARGS,
    )
    private = custody.get_private_for_requester(
        action_id=pending.action_id,
        requester_user_id="user-1",
    )
    assert custody.transition(
        action_id=pending.action_id,
        expected_states=frozenset({"PENDING_CONFIRMATION"}),
        new_state="EXECUTING",
        execution_run_id="run-action-1",
    )

    key_sha256 = sha256(private.idempotency_key.encode("utf-8")).hexdigest()
    assert ledger.claim(
        key_sha256=key_sha256,
        action_fingerprint=pending.action_fingerprint,
        action_id=pending.action_id,
    )

    report = reconcile_orphaned_actions(custody=custody, ledger=ledger)

    assert report.executing_actions_marked_uncertain == (pending.action_id,)
    assert report.claimed_ledger_entries_marked_uncertain == (pending.action_id,)
    assert custody.get_safe(pending.action_id).state == "UNCERTAIN"
    assert ledger.get(key_sha256)["state"] == "UNCERTAIN"  # type: ignore[index]

    # Recovery is idempotent and never turns UNCERTAIN back into executable state.
    second = reconcile_orphaned_actions(custody=custody, ledger=ledger)
    assert second.executing_actions_marked_uncertain == ()
    assert second.claimed_ledger_entries_marked_uncertain == ()
    assert custody.get_safe(pending.action_id).state == "UNCERTAIN"


def test_pending_confirmation_is_not_modified_by_restart_recovery(tmp_path) -> None:
    custody = PendingActionCustody(tmp_path / "pending-custody.duckdb")
    ledger = DuckDBActionIdempotencyLedger(tmp_path / "pending-ledger.duckdb")
    tool = canonical_tool_registry()["reprocess_analysis"]

    pending = custody.create_or_get(
        origin_raw_run_id="raw-pending-run",
        requester_user_id="user-1",
        tool=tool,
        arguments=ACTION_ARGS,
    )

    report = reconcile_orphaned_actions(custody=custody, ledger=ledger)

    assert report.executing_actions_marked_uncertain == ()
    assert report.claimed_ledger_entries_marked_uncertain == ()
    assert custody.get_safe(pending.action_id).state == "PENDING_CONFIRMATION"
