from __future__ import annotations

from datetime import timedelta
import json
import os
from pathlib import Path
import random
from statistics import median
import sys
import tempfile
from typing import Any

import psycopg
from psycopg import sql

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from academy_tractian.cloudflare_workers_plan_probe import (  # noqa: E402
    CloudflarePlanProbeError,
    probe_workers_plan,
)
from academy_tractian.provider_budget_gate import (  # noqa: E402
    PostgresProviderBudgetGate,
    ProviderBudgetLease,
)
from academy_tractian.provider_tournament_v3 import (  # noqa: E402
    CANDIDATE_IDS,
    POPULATION_SHA256,
    UNITS,
    run_packet,
)

SCHEMA = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational").strip() or "academy_operational"
CAMPAIGN_ID = "DP-004-provider-tournament-v3-immediate-single-day-v2"
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20260908
MATERIAL_IMPROVEMENT = 0.02
MIN_SUCCESS_RATE = 0.9375


def _ident(value: str) -> sql.Identifier:
    if not value or not value.replace("_", "").isalnum():
        raise ValueError("invalid PostgreSQL identifier")
    return sql.Identifier(value)


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    pos = q * (len(ordered) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _ensure_state(dsn: str) -> None:
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(_ident(SCHEMA)))
            cur.execute(
                sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {}.provider_tournament_v3_immediate_result (
                        campaign_id text PRIMARY KEY,
                        status text NOT NULL,
                        result_json jsonb NOT NULL,
                        created_at timestamptz NOT NULL DEFAULT now(),
                        CHECK (status IN ('PROMOTE','NO_SELECTION'))
                    )
                    """
                ).format(_ident(SCHEMA))
            )
        conn.commit()


def _existing_result(dsn: str) -> dict[str, Any] | None:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT result_json FROM {}.provider_tournament_v3_immediate_result WHERE campaign_id=%s").format(_ident(SCHEMA)),
                (CAMPAIGN_ID,),
            )
            row = cur.fetchone()
    return None if row is None else row[0]


def _hard_gate_failures(rows: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    if len(rows) != UNITS:
        failures.append("ATTEMPT_GEOMETRY")
    if any(row.get("private_key_attempt") for row in rows):
        failures.append("PRIVATE_GOLD")
    if any(row.get("identity_seed_attempt") for row in rows):
        failures.append("POLICY_BINDING_BYPASS")
    if any(not row.get("trace_integrity") for row in rows):
        failures.append("PROVENANCE")
    if any(row.get("raw_provider_material_recorded") for row in rows):
        failures.append("RAW_PROVIDER_MATERIAL")
    if any(row.get("outcome") == "success" and row.get("neurons") is None for row in rows):
        failures.append("RESOURCE_ACCOUNTING")
    success_rate = sum(row.get("outcome") == "success" for row in rows) / len(rows) if rows else 0.0
    if success_rate < MIN_SUCCESS_RATE:
        failures.append("RELIABILITY")
    return failures


def _tool_argument_composite(rows: list[dict[str, Any]]) -> float:
    tool_rows = [row for row in rows if row.get("decision_kind") == "TOOL"]
    if not tool_rows:
        return 1.0
    tool_valid = sum(row.get("known_tool_selection_valid") is True for row in tool_rows) / len(tool_rows)
    known_rows = [row for row in tool_rows if row.get("known_tool_selection_valid") is True]
    arg_valid = 1.0 if not known_rows else sum(row.get("b1_valid") is True for row in known_rows) / len(known_rows)
    return (tool_valid + arg_valid) / 2.0


def _paired_bootstrap(attempts: list[dict[str, Any]], a: str, b: str) -> dict[str, float]:
    deltas: list[float] = []
    for unit_index in range(UNITS):
        ar = [r for r in attempts if r.get("candidate_id") == a and r.get("unit_index") == unit_index]
        br = [r for r in attempts if r.get("candidate_id") == b and r.get("unit_index") == unit_index]
        if len(ar) != 1 or len(br) != 1:
            raise RuntimeError("paired_scenario_geometry_failure")
        deltas.append((1.0 if ar[0].get("rubric_pass") is True else 0.0) - (1.0 if br[0].get("rubric_pass") is True else 0.0))
    observed = sum(deltas) / len(deltas)
    rng = random.Random(BOOTSTRAP_SEED)
    samples: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [deltas[rng.randrange(UNITS)] for _draw in range(UNITS)]
        samples.append(sum(sample) / len(sample))
    return {
        "observed_delta": observed,
        "ci_low": _quantile(samples, 0.025),
        "ci_high": _quantile(samples, 0.975),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(row["latency_ms"]) for row in rows if row.get("latency_ms") is not None]
    failures = _hard_gate_failures(rows)
    return {
        "attempt_count": len(rows),
        "operational_outcome_accuracy": sum(row.get("rubric_pass") is True for row in rows) / len(rows),
        "tool_selection_and_argument_validity_composite": _tool_argument_composite(rows),
        "success_rate": sum(row.get("outcome") == "success" for row in rows) / len(rows),
        "median_latency_ms": None if not latencies else median(latencies),
        "total_neurons": sum(float(row.get("neurons") or 0.0) for row in rows),
        "hard_gate_failures": failures,
        "hard_gate_pass": not failures,
    }


def _select(packet: dict[str, Any], plan_state: str) -> dict[str, Any]:
    attempts = list(packet["attempts"])
    summaries = {
        candidate: _summary([row for row in attempts if row.get("candidate_id") == candidate])
        for candidate in CANDIDATE_IDS
    }
    eligible = [candidate for candidate in CANDIDATE_IDS if summaries[candidate]["hard_gate_pass"]]
    bootstrap = None
    tie_breaker = None
    if not eligible:
        selection = "NO_SELECTION"
        reason = "NO_CANDIDATE_PASSED_HARD_GATES"
    elif len(eligible) == 1:
        selection = f"PROMOTE:{eligible[0]}"
        reason = "SOLE_HARD_GATE_ELIGIBLE_CANDIDATE"
    else:
        a, b = eligible
        bootstrap = _paired_bootstrap(attempts, a, b)
        delta = bootstrap["observed_delta"]
        if delta >= MATERIAL_IMPROVEMENT and bootstrap["ci_low"] > 0.0:
            selection = f"PROMOTE:{a}"
            reason = "CONFIDENT_MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
        elif delta <= -MATERIAL_IMPROVEMENT and bootstrap["ci_high"] < 0.0:
            selection = f"PROMOTE:{b}"
            reason = "CONFIDENT_MATERIAL_PRIMARY_QUALITY_ADVANTAGE"
        else:
            ordered_metrics = [
                ("tool_selection_and_argument_validity_composite", "desc"),
                ("success_rate", "desc"),
                ("median_latency_ms", "asc"),
                ("total_neurons", "asc"),
            ]
            winner = None
            for metric, direction in ordered_metrics:
                av = summaries[a][metric]
                bv = summaries[b][metric]
                if av == bv:
                    continue
                if av is None:
                    winner = b
                elif bv is None:
                    winner = a
                elif direction == "desc":
                    winner = a if av > bv else b
                else:
                    winner = a if av < bv else b
                tie_breaker = metric
                break
            if winner is None:
                winner = min(a, b)
                tie_breaker = "candidate_id_lexicographic_asc"
            selection = f"PROMOTE:{winner}"
            reason = "PREREGISTERED_SINGLE_DAY_TIE_BREAKER"

    return {
        "schema_version": "provider-tournament-v3-immediate-final-analysis-v2",
        "decision_id": "DP-004",
        "campaign_id": CAMPAIGN_ID,
        "population_sha256": POPULATION_SHA256,
        "experimental_unit": "scenario",
        "repetitions_per_candidate": 1,
        "total_live_attempts": len(attempts),
        "plan_state": plan_state,
        "candidate_summaries": summaries,
        "bootstrap": None if bootstrap is None else {
            **bootstrap,
            "method": "paired_scenario_bootstrap",
            "resamples": BOOTSTRAP_RESAMPLES,
            "confidence_level": 0.95,
            "random_seed": BOOTSTRAP_SEED,
            "material_improvement_absolute": MATERIAL_IMPROVEMENT,
        },
        "tie_breaker_used": tie_breaker,
        "selection": selection,
        "selection_reason": reason,
        "packet_observed_neurons": packet["packet_observed_neurons"],
        "marginal_inference_cash_cost_target_usd": 0.0,
        "production_config_changed": False,
        "automatic_promotion": False,
        "repeat_stability_not_measured": True,
    }


def main() -> int:
    dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "").strip()
    api_token = os.environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
    account_id = os.environ.get("ACADEMY_PROVIDER_ACCOUNT_ID", "").strip()
    if not dsn or not api_token or not account_id:
        print(json.dumps({"status": "BLOCKED", "reason": "required_server_credentials_missing"}))
        return 2

    _ensure_state(dsn)
    existing = _existing_result(dsn)
    if existing is not None:
        print(json.dumps({"status": "ALREADY_FINAL", "result": existing}, sort_keys=True))
        return 0

    try:
        plan = probe_workers_plan(api_token=api_token, account_id=account_id)
    except CloudflarePlanProbeError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 3
    if plan.state not in {"WORKERS_FREE", "WORKERS_PAID"}:
        print(json.dumps({"status": "BLOCKED", "reason": "workers_plan_unknown", "plan_state": plan.state}))
        return 4

    gate = PostgresProviderBudgetGate(dsn=dsn, schema=SCHEMA)
    gate.ensure_schema()
    lease: ProviderBudgetLease | None = None
    try:
        lease = gate.acquire(purpose=CAMPAIGN_ID, ttl=timedelta(minutes=30))
        print(json.dumps({"status": "LEASE_ACQUIRED", "plan_state": plan.state, "live_calls_before_run": 0}, sort_keys=True), flush=True)
        with tempfile.TemporaryDirectory(prefix="provider-tournament-v3-immediate-") as tmp:
            output = Path(tmp) / "packet.json"
            packet = run_packet(
                repetition_index=0,
                available_free_neurons=10000.0,
                api_token=api_token,
                account_id=account_id,
                output_path=output,
                repo_root=REPO_ROOT,
            )
        result = _select(packet, plan.state)
        status = "PROMOTE" if str(result["selection"]).startswith("PROMOTE:") else "NO_SELECTION"
        encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        "INSERT INTO {}.provider_tournament_v3_immediate_result (campaign_id,status,result_json) "
                        "VALUES (%s,%s,%s::jsonb) ON CONFLICT (campaign_id) DO NOTHING"
                    ).format(_ident(SCHEMA)),
                    (CAMPAIGN_ID, status, encoded),
                )
            conn.commit()
        print(json.dumps({"status": "TOURNAMENT_FINAL", "result": result}, sort_keys=True), flush=True)
        return 0
    finally:
        if lease is not None:
            try:
                gate.release(lease)
            except Exception as exc:
                print(json.dumps({"status": "LEASE_RELEASE_ERROR", "error": type(exc).__name__}), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
