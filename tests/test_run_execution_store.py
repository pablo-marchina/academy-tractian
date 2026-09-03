from __future__ import annotations

from academy_tractian.run_execution_store import DuckDBRunExecutionStore


def test_runtime_nonterminal_state_becomes_interrupted_on_restart_reconciliation(tmp_path) -> None:
    path = tmp_path / "execution.duckdb"
    first = DuckDBRunExecutionStore(path)
    first.create_accepted(run_id="run-runtime")
    assert first.transition(
        run_id="run-runtime",
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )

    second = DuckDBRunExecutionStore(path)
    recovered = second.reconcile_orphaned()

    assert len(recovered) == 1
    assert recovered[0].run_id == "run-runtime"
    assert recovered[0].execution_kind == "runtime"
    assert recovered[0].state == "interrupted"
    assert second.get("run-runtime").state == "interrupted"  # type: ignore[union-attr]
    assert second.reconcile_orphaned() == ()


def test_action_nonterminal_state_becomes_uncertain_and_never_reaccepted(tmp_path) -> None:
    path = tmp_path / "action-execution.duckdb"
    first = DuckDBRunExecutionStore(path)
    first.create_accepted(
        run_id="run-action",
        execution_kind="action",
        related_action_id="act-1",
    )
    assert first.transition(
        run_id="run-action",
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )

    second = DuckDBRunExecutionStore(path)
    recovered = second.reconcile_orphaned()

    assert len(recovered) == 1
    assert recovered[0].state == "uncertain"
    assert recovered[0].related_action_id == "act-1"
    assert second.get("run-action").state == "uncertain"  # type: ignore[union-attr]

    # A restart is not permission to replay or reset the logical execution.
    try:
        second.create_accepted(
            run_id="run-action",
            execution_kind="action",
            related_action_id="act-1",
        )
    except RuntimeError as exc:
        assert str(exc) == "run_execution_conflict"
    else:
        raise AssertionError("uncertain action execution must never be silently reaccepted")


def test_terminal_states_are_preserved_across_reconciliation(tmp_path) -> None:
    store = DuckDBRunExecutionStore(tmp_path / "terminal.duckdb")
    store.create_accepted(run_id="run-complete")
    assert store.transition(
        run_id="run-complete",
        expected_states=frozenset({"accepted"}),
        new_state="running",
    )
    assert store.transition(
        run_id="run-complete",
        expected_states=frozenset({"running"}),
        new_state="completed",
    )

    store.create_accepted(run_id="run-failed")
    assert store.transition(
        run_id="run-failed",
        expected_states=frozenset({"accepted"}),
        new_state="failed",
    )

    restarted = DuckDBRunExecutionStore(store.path)
    assert restarted.reconcile_orphaned() == ()
    assert restarted.get("run-complete").state == "completed"  # type: ignore[union-attr]
    assert restarted.get("run-failed").state == "failed"  # type: ignore[union-attr]
