from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import time

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
from academy_tractian.provider_tournament_v3 import run_packet  # noqa: E402
from academy_tractian.provider_tournament_v3_analysis import analyze_tournament  # noqa: E402


SCHEMA = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational").strip() or "academy_operational"
CAMPAIGN_ID = "DP-004-provider-tournament-v3"


def _ident(value: str) -> sql.Identifier:
    if not value or not value.replace("_", "").isalnum():
        raise ValueError("invalid PostgreSQL identifier")
    return sql.Identifier(value)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_state(dsn: str) -> None:
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(_ident(SCHEMA)))
            cur.execute(
                sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {}.provider_tournament_v3_packets (
                        campaign_id text NOT NULL,
                        repetition_index integer NOT NULL,
                        status text NOT NULL,
                        reset_date date NOT NULL,
                        claimed_at timestamptz NOT NULL,
                        completed_at timestamptz NULL,
                        packet_json jsonb NULL,
                        packet_sha256 text NULL,
                        error_code text NULL,
                        PRIMARY KEY (campaign_id, repetition_index),
                        CHECK (repetition_index >= 0 AND repetition_index < 5),
                        CHECK (status IN ('CLAIMED','COMPLETE','UNCERTAIN'))
                    )
                    """
                ).format(_ident(SCHEMA))
            )
            cur.execute(
                sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {}.provider_tournament_v3_result (
                        campaign_id text PRIMARY KEY,
                        status text NOT NULL,
                        finalized_at timestamptz NOT NULL,
                        result_json jsonb NOT NULL,
                        CHECK (status IN ('PROMOTE','NO_SELECTION','INCONCLUSIVE'))
                    )
                    """
                ).format(_ident(SCHEMA))
            )
        conn.commit()


def _existing_result(dsn: str) -> dict | None:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT result_json FROM {}.provider_tournament_v3_result WHERE campaign_id=%s").format(_ident(SCHEMA)),
                (CAMPAIGN_ID,),
            )
            row = cur.fetchone()
    return None if row is None else row[0]


def _packet_rows(dsn: str) -> list[tuple]:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    "SELECT repetition_index,status,packet_json,error_code FROM {}.provider_tournament_v3_packets "
                    "WHERE campaign_id=%s ORDER BY repetition_index"
                ).format(_ident(SCHEMA)),
                (CAMPAIGN_ID,),
            )
            return list(cur.fetchall())


def _claim_packet(dsn: str, repetition: int, reset_date) -> None:
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (CAMPAIGN_ID,))
            cur.execute(
                sql.SQL(
                    "SELECT repetition_index,status FROM {}.provider_tournament_v3_packets "
                    "WHERE campaign_id=%s ORDER BY repetition_index"
                ).format(_ident(SCHEMA)),
                (CAMPAIGN_ID,),
            )
            rows = list(cur.fetchall())
            if any(status in ("CLAIMED", "UNCERTAIN") for _, status in rows):
                raise RuntimeError("campaign_has_claimed_or_uncertain_packet")
            completed = [idx for idx, status in rows if status == "COMPLETE"]
            if completed != list(range(repetition)):
                raise RuntimeError("campaign_repetition_sequence_invalid")
            cur.execute(
                sql.SQL(
                    "INSERT INTO {}.provider_tournament_v3_packets "
                    "(campaign_id,repetition_index,status,reset_date,claimed_at) VALUES (%s,%s,'CLAIMED',%s,%s)"
                ).format(_ident(SCHEMA)),
                (CAMPAIGN_ID, repetition, reset_date, _now()),
            )
        conn.commit()


def _mark_complete(dsn: str, repetition: int, packet: dict) -> None:
    from hashlib import sha256

    encoded = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    "UPDATE {}.provider_tournament_v3_packets SET status='COMPLETE',completed_at=%s,packet_json=%s::jsonb,packet_sha256=%s "
                    "WHERE campaign_id=%s AND repetition_index=%s AND status='CLAIMED'"
                ).format(_ident(SCHEMA)),
                (_now(), encoded, digest, CAMPAIGN_ID, repetition),
            )
            if cur.rowcount != 1:
                raise RuntimeError("campaign_packet_claim_lost")
        conn.commit()


def _mark_uncertain(dsn: str, repetition: int, code: str) -> None:
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    "UPDATE {}.provider_tournament_v3_packets SET status='UNCERTAIN',completed_at=%s,error_code=%s "
                    "WHERE campaign_id=%s AND repetition_index=%s AND status='CLAIMED'"
                ).format(_ident(SCHEMA)),
                (_now(), code[:200], CAMPAIGN_ID, repetition),
            )
        conn.commit()


def _finalize_if_ready(dsn: str) -> dict | None:
    rows = _packet_rows(dsn)
    if len(rows) != 5 or any(status != "COMPLETE" for _, status, _, _ in rows):
        return None
    with tempfile.TemporaryDirectory(prefix="provider-tournament-v3-finalize-") as tmp:
        paths: list[Path] = []
        for repetition, _status, packet_json, _error in rows:
            path = Path(tmp) / f"packet-{repetition}.json"
            path.write_text(json.dumps(packet_json, sort_keys=True), encoding="utf-8")
            paths.append(path)
        result = analyze_tournament(paths)
    selection = str(result["selection"])
    status = "PROMOTE" if selection.startswith("PROMOTE:") else selection
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL(
                    "INSERT INTO {}.provider_tournament_v3_result (campaign_id,status,finalized_at,result_json) "
                    "VALUES (%s,%s,%s,%s::jsonb) ON CONFLICT (campaign_id) DO NOTHING"
                ).format(_ident(SCHEMA)),
                (CAMPAIGN_ID, status, _now(), encoded),
            )
        conn.commit()
    return result


def _seconds_until_reset(now: datetime) -> tuple[datetime, float]:
    next_day = (now + timedelta(days=1)).date()
    reset = datetime(next_day.year, next_day.month, next_day.day, tzinfo=timezone.utc)
    return reset, (reset - now).total_seconds()


def main() -> int:
    dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "").strip()
    api_token = os.environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
    account_id = os.environ.get("ACADEMY_PROVIDER_ACCOUNT_ID", "").strip()
    if not dsn or not api_token or not account_id:
        print(json.dumps({"status": "BLOCKED", "reason": "required_server_credentials_missing"}))
        return 2

    _ensure_state(dsn)
    gate = PostgresProviderBudgetGate(dsn=dsn, schema=SCHEMA)
    gate.ensure_schema()

    existing = _existing_result(dsn)
    if existing is not None:
        print(json.dumps({"status": "ALREADY_FINAL", "result": existing}, sort_keys=True))
        return 0

    rows = _packet_rows(dsn)
    if any(status in ("CLAIMED", "UNCERTAIN") for _, status, _, _ in rows):
        print(json.dumps({"status": "BLOCKED", "reason": "campaign_has_claimed_or_uncertain_packet"}))
        return 3
    completed = [idx for idx, status, _, _ in rows if status == "COMPLETE"]
    if completed != list(range(len(completed))):
        print(json.dumps({"status": "BLOCKED", "reason": "campaign_sequence_invalid"}))
        return 4
    if len(completed) == 5:
        result = _finalize_if_ready(dsn)
        print(json.dumps({"status": "FINALIZED", "result": result}, sort_keys=True))
        return 0

    now = _now()
    # Cron is intentionally scheduled before 00:00 UTC. Starting after reset cannot prove that
    # production made zero Workers AI calls between reset and lease acquisition.
    if now.hour != 23 or now.minute < 55:
        print(json.dumps({"status": "NOOP", "reason": "outside_pre_reset_window", "utc": now.isoformat()}))
        return 0

    try:
        plan = probe_workers_plan(api_token=api_token, account_id=account_id)
    except CloudflarePlanProbeError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 5
    if plan.state != "WORKERS_FREE" or plan.workers_paid_detected:
        result = {
            "schema_version": "provider-tournament-v3-final-analysis-v1",
            "decision_id": "DP-004",
            "selection": "INCONCLUSIVE",
            "selection_reason": "EXTERNAL_WORKERS_PLAN_NO_LONGER_MATCHES_PREREGISTRATION",
            "production_config_changed": False,
            "plan_evidence": {
                "state": plan.state,
                "default_usage_model": plan.default_usage_model,
                "account_subscription_count": plan.account_subscription_count,
                "raw_response_recorded": False,
            },
        }
        encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        "INSERT INTO {}.provider_tournament_v3_result (campaign_id,status,finalized_at,result_json) "
                        "VALUES (%s,'INCONCLUSIVE',%s,%s::jsonb) ON CONFLICT (campaign_id) DO NOTHING"
                    ).format(_ident(SCHEMA)),
                    (CAMPAIGN_ID, _now(), encoded),
                )
            conn.commit()
        print(json.dumps({"status": "FINALIZED", "result": result}, sort_keys=True))
        return 0

    lease: ProviderBudgetLease | None = None
    repetition = len(completed)
    try:
        lease = gate.acquire(
            purpose=f"{CAMPAIGN_ID}:repetition:{repetition}",
            ttl=timedelta(minutes=45),
        )
        reset, wait_seconds = _seconds_until_reset(_now())
        if wait_seconds <= 0 or wait_seconds > 5 * 60:
            raise RuntimeError("pre_reset_lease_window_invalid")
        print(json.dumps({
            "status": "LEASED_PRE_RESET",
            "repetition_index": repetition,
            "seconds_until_reset": round(wait_seconds, 3),
            "plan_state": plan.state,
        }, sort_keys=True), flush=True)
        time.sleep(wait_seconds + 5.0)
        after_reset = _now()
        if after_reset.date() != reset.date() or (after_reset - reset).total_seconds() > 600:
            raise RuntimeError("reset_window_expired")

        _claim_packet(dsn, repetition, reset.date())
        with tempfile.TemporaryDirectory(prefix=f"provider-tournament-v3-{repetition}-") as tmp:
            output_path = Path(tmp) / "packet.json"
            try:
                packet = run_packet(
                    repetition_index=repetition,
                    available_free_neurons=10000.0,
                    api_token=api_token,
                    account_id=account_id,
                    output_path=output_path,
                    repo_root=REPO_ROOT,
                )
            except Exception as exc:
                _mark_uncertain(dsn, repetition, type(exc).__name__)
                raise
        _mark_complete(dsn, repetition, packet)
        print(json.dumps({
            "status": "PACKET_COMPLETE",
            "repetition_index": repetition,
            "attempt_count": packet["attempt_count"],
            "observed_neurons": packet["packet_observed_neurons"],
            "cash_cost_usd": packet["actual_cash_cost_usd"],
        }, sort_keys=True), flush=True)
    finally:
        if lease is not None:
            try:
                gate.release(lease)
            except Exception as exc:
                print(json.dumps({"status": "LEASE_RELEASE_ERROR", "error": type(exc).__name__}), flush=True)

    result = _finalize_if_ready(dsn)
    if result is not None:
        print(json.dumps({"status": "TOURNAMENT_FINAL", "result": result}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
