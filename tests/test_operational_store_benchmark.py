from __future__ import annotations

import os
from uuid import uuid4

import pytest

from research.operational_store.adapters import (
    DuckDBOperationalCandidate,
    PostgreSQLOperationalCandidate,
)
from research.operational_store.benchmark import _decision, run_benchmark


def _candidate_result(
    *,
    eligible: bool = True,
    valid: bool = True,
    single_p95: float = 10.0,
    high_p95: float = 100.0,
    high_throughput: float = 100.0,
) -> dict:
    return {
        "benchmark_valid": valid,
        "eligible_after_hard_gates": eligible,
        "aggregate_by_concurrency": {
            "1": {
                "lifecycle": {"p95_ms": single_p95},
                "throughput_lifecycles_per_second": 10.0,
            },
            "25": {
                "lifecycle": {"p95_ms": high_p95},
                "throughput_lifecycles_per_second": high_throughput,
            },
        },
    }


def test_decision_hard_gates_dominate_performance() -> None:
    duck = _candidate_result(eligible=False, high_p95=1.0, high_throughput=10_000.0)
    postgres = _candidate_result(eligible=True, high_p95=1_000.0, high_throughput=1.0)

    decision = _decision(duck, postgres, highest_concurrency=25)

    assert decision["outcome"] == "PROMOTE_POSTGRES_OPERATIONAL"
    assert "hard gates" in decision["reason"]


def test_decision_keeps_duckdb_when_postgres_fails_a_hard_gate() -> None:
    duck = _candidate_result(eligible=True)
    postgres = _candidate_result(eligible=False, high_p95=1.0, high_throughput=10_000.0)

    decision = _decision(duck, postgres, highest_concurrency=25)

    assert decision["outcome"] == "KEEP_DUCKDB_SINGLE_NODE"


def test_decision_promotes_postgres_only_after_preregistered_materiality() -> None:
    duck = _candidate_result(single_p95=10.0, high_p95=100.0, high_throughput=100.0)
    postgres = _candidate_result(single_p95=15.0, high_p95=75.0, high_throughput=95.0)

    decision = _decision(duck, postgres, highest_concurrency=25)

    assert decision["outcome"] == "PROMOTE_POSTGRES_OPERATIONAL"
    assert decision["materiality"]["lower_p95_condition"] is True


def test_decision_keeps_bounded_duckdb_when_postgres_is_not_materially_better() -> None:
    duck = _candidate_result(single_p95=10.0, high_p95=100.0, high_throughput=100.0)
    postgres = _candidate_result(single_p95=12.0, high_p95=95.0, high_throughput=105.0)

    decision = _decision(duck, postgres, highest_concurrency=25)

    assert decision["outcome"] == "KEEP_DUCKDB_SINGLE_NODE"


def test_decision_is_inconclusive_if_postgres_breaks_single_user_guardrail() -> None:
    duck = _candidate_result(single_p95=10.0)
    postgres = _candidate_result(single_p95=21.0)

    decision = _decision(duck, postgres, highest_concurrency=25)

    assert decision["outcome"] == "INCONCLUSIVE"
    assert "2x single-user" in decision["reason"]


def test_duckdb_candidate_contract_recovery_and_scope(tmp_path) -> None:
    candidate = DuckDBOperationalCandidate(tmp_path / "duckdb-candidate")
    try:
        assert candidate.claim_run(run_id="run-1", organization_id="org-a", user_id="user-a") is True
        assert candidate.claim_run(run_id="run-1", organization_id="org-a", user_id="user-a") is False
        with pytest.raises(RuntimeError, match="run_ownership_conflict"):
            candidate.claim_run(run_id="run-1", organization_id="org-a", user_id="user-b")
        assert candidate.scoped_owner(run_id="run-1", organization_id="org-b") is None

        candidate.create_execution(run_id="run-1", organization_id="org-a")
        assert (
            candidate.transition_execution(
                run_id="run-1",
                organization_id="org-a",
                expected_states=frozenset({"running"}),
                new_state="completed",
            )
            is False
        )
        assert candidate.transition_execution(
            run_id="run-1",
            organization_id="org-a",
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )
        assert candidate.transition_execution(
            run_id="run-1",
            organization_id="org-a",
            expected_states=frozenset({"running"}),
            new_state="completed",
        )
        candidate.reconnect()
        assert candidate.execution_state(run_id="run-1", organization_id="org-a") == "completed"

        assert candidate.claim_run(
            run_id="runtime-orphan", organization_id="org-a", user_id="user-a"
        )
        candidate.create_execution(run_id="runtime-orphan", organization_id="org-a")
        assert candidate.transition_execution(
            run_id="runtime-orphan",
            organization_id="org-a",
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )

        assert candidate.claim_run(
            run_id="action-orphan", organization_id="org-a", user_id="user-a"
        )
        candidate.create_execution(
            run_id="action-orphan",
            organization_id="org-a",
            execution_kind="action",
            related_action_id="action-1",
        )
        assert candidate.transition_execution(
            run_id="action-orphan",
            organization_id="org-a",
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )

        recovery = candidate.reconcile_orphaned()
        assert recovery == {"interrupted": 1, "uncertain": 1}
        assert (
            candidate.execution_state(run_id="runtime-orphan", organization_id="org-a")
            == "interrupted"
        )
        assert (
            candidate.execution_state(run_id="action-orphan", organization_id="org-a")
            == "uncertain"
        )
    finally:
        candidate.destroy()


@pytest.mark.skipif(
    not os.environ.get("OPERATIONAL_POSTGRES_DSN"),
    reason="OPERATIONAL_POSTGRES_DSN is required for PostgreSQL integration",
)
def test_postgresql_candidate_enforces_rls_and_recovery() -> None:
    schema = "academy_ops_test_" + uuid4().hex[:16]
    candidate = PostgreSQLOperationalCandidate(
        admin_dsn=os.environ["OPERATIONAL_POSTGRES_DSN"],
        schema=schema,
        pool_max_size=8,
    )
    try:
        assert candidate.claim_run(run_id="run-1", organization_id="org-a", user_id="user-a") is True
        assert candidate.claim_run(run_id="run-1", organization_id="org-a", user_id="user-a") is False
        assert candidate.scoped_owner(run_id="run-1", organization_id="org-b") is None
        assert candidate.direct_cross_tenant_probe(run_id="run-1", organization_id="org-b") == 0
        with pytest.raises(RuntimeError, match="run_ownership_conflict"):
            candidate.claim_run(run_id="run-1", organization_id="org-a", user_id="user-b")

        candidate.create_execution(run_id="run-1", organization_id="org-a")
        assert candidate.transition_execution(
            run_id="run-1",
            organization_id="org-a",
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )
        assert candidate.transition_execution(
            run_id="run-1",
            organization_id="org-a",
            expected_states=frozenset({"running"}),
            new_state="completed",
        )
        candidate.reconnect()
        assert candidate.execution_state(run_id="run-1", organization_id="org-a") == "completed"

        assert candidate.claim_run(
            run_id="runtime-orphan", organization_id="org-a", user_id="user-a"
        )
        candidate.create_execution(run_id="runtime-orphan", organization_id="org-a")
        assert candidate.transition_execution(
            run_id="runtime-orphan",
            organization_id="org-a",
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )

        assert candidate.claim_run(
            run_id="action-orphan", organization_id="org-a", user_id="user-a"
        )
        candidate.create_execution(
            run_id="action-orphan",
            organization_id="org-a",
            execution_kind="action",
            related_action_id="action-1",
        )
        assert candidate.transition_execution(
            run_id="action-orphan",
            organization_id="org-a",
            expected_states=frozenset({"accepted"}),
            new_state="running",
        )

        recovery = candidate.reconcile_orphaned()
        assert recovery == {"interrupted": 1, "uncertain": 1}
        assert (
            candidate.execution_state(run_id="runtime-orphan", organization_id="org-a")
            == "interrupted"
        )
        assert (
            candidate.execution_state(run_id="action-orphan", organization_id="org-a")
            == "uncertain"
        )
    finally:
        candidate.destroy()


@pytest.mark.skipif(
    not os.environ.get("OPERATIONAL_POSTGRES_DSN"),
    reason="OPERATIONAL_POSTGRES_DSN is required for paired benchmark smoke test",
)
def test_paired_benchmark_produces_machine_readable_decision(tmp_path) -> None:
    result = run_benchmark(
        postgres_dsn=os.environ["OPERATIONAL_POSTGRES_DSN"],
        concurrency_levels=(1, 5),
        repetitions=1,
        operations_per_worker=3,
        work_root=tmp_path / "paired",
    )

    assert result["decision_id"] == "OPS-STORE-001"
    assert result["candidates"]["duckdb"] is not None
    assert result["candidates"]["postgresql"] is not None
    assert result["candidates"]["duckdb"]["benchmark_valid"] is True
    assert result["candidates"]["postgresql"]["benchmark_valid"] is True
    assert result["decision"]["outcome"] in {
        "PROMOTE_POSTGRES_OPERATIONAL",
        "KEEP_DUCKDB_SINGLE_NODE",
        "INCONCLUSIVE",
    }
