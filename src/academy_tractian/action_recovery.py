from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import duckdb

from .production_actions_v2 import DuckDBActionIdempotencyLedger, PendingActionCustody


@dataclass(frozen=True, slots=True)
class ActionRecoveryReport:
    executing_actions_marked_uncertain: tuple[str, ...]
    claimed_ledger_entries_marked_uncertain: tuple[str, ...]


def _duckdb_recovery(
    *,
    custody: PendingActionCustody,
    ledger: DuckDBActionIdempotencyLedger,
) -> ActionRecoveryReport:
    custody_connection = duckdb.connect(custody.path)
    try:
        custody_connection.execute("BEGIN TRANSACTION")
        executing_rows = custody_connection.execute(
            """
            SELECT action_id
            FROM pending_actions
            WHERE state = 'EXECUTING'
            ORDER BY action_id
            """
        ).fetchall()
        executing_action_ids = tuple(str(row[0]) for row in executing_rows)
        if executing_action_ids:
            custody_connection.execute(
                """
                UPDATE pending_actions
                SET state = 'UNCERTAIN'
                WHERE state = 'EXECUTING'
                """
            )
        uncertain_rows = custody_connection.execute(
            """
            SELECT action_id
            FROM pending_actions
            WHERE state = 'UNCERTAIN'
            ORDER BY action_id
            """
        ).fetchall()
        uncertain_action_ids = tuple(str(row[0]) for row in uncertain_rows)
        custody_connection.execute("COMMIT")
    except Exception:
        try:
            custody_connection.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        custody_connection.close()

    ledger_recovered: tuple[str, ...] = ()
    if uncertain_action_ids:
        placeholders = ",".join("?" for _ in uncertain_action_ids)
        ledger_connection = duckdb.connect(ledger.path)
        try:
            ledger_connection.execute("BEGIN TRANSACTION")
            claimed_rows = ledger_connection.execute(
                f"""
                SELECT action_id
                FROM action_claims
                WHERE state = 'CLAIMED' AND action_id IN ({placeholders})
                ORDER BY action_id
                """,
                list(uncertain_action_ids),
            ).fetchall()
            ledger_recovered = tuple(str(row[0]) for row in claimed_rows)
            if ledger_recovered:
                claimed_placeholders = ",".join("?" for _ in ledger_recovered)
                ledger_connection.execute(
                    f"""
                    UPDATE action_claims
                    SET state = 'UNCERTAIN'
                    WHERE state = 'CLAIMED' AND action_id IN ({claimed_placeholders})
                    """,
                    list(ledger_recovered),
                )
            ledger_connection.execute("COMMIT")
        except Exception:
            try:
                ledger_connection.execute("ROLLBACK")
            except Exception:
                pass
            raise
        finally:
            ledger_connection.close()

    return ActionRecoveryReport(
        executing_actions_marked_uncertain=executing_action_ids,
        claimed_ledger_entries_marked_uncertain=ledger_recovered,
    )


def reconcile_orphaned_actions(*, custody: Any, ledger: Any) -> ActionRecoveryReport:
    """Fail-safe action recovery across qualified operational backends.

    PostgreSQL stores own their recovery transaction boundaries. The legacy DuckDB baseline
    keeps its existing recovery implementation for regression tests. No backend is allowed to
    interpret restart as permission to retry a consequential action.
    """

    recover_custody = getattr(custody, "reconcile_executing", None)
    recover_ledger = getattr(ledger, "reconcile_claimed_for_actions", None)
    if callable(recover_custody) and callable(recover_ledger):
        recovered, uncertain = recover_custody()
        ledger_recovered = recover_ledger(uncertain)
        return ActionRecoveryReport(
            executing_actions_marked_uncertain=tuple(recovered),
            claimed_ledger_entries_marked_uncertain=tuple(ledger_recovered),
        )

    if isinstance(custody, PendingActionCustody) and isinstance(
        ledger, DuckDBActionIdempotencyLedger
    ):
        return _duckdb_recovery(custody=custody, ledger=ledger)

    raise TypeError("action operational stores do not implement a supported recovery contract")
