from __future__ import annotations

import json
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from academy_tractian.cloudflare_workers_plan_probe import CloudflarePlanProbeError, probe_workers_plan
from academy_tractian.provider_budget_gate import PostgresProviderBudgetGate
from academy_tractian.provider_tournament_v3 import load_frozen_tournament_v3


def main() -> int:
    token = os.environ.get("ACADEMY_PROVIDER_API_TOKEN", "").strip()
    account = os.environ.get("ACADEMY_PROVIDER_ACCOUNT_ID", "").strip()
    dsn = os.environ.get("ACADEMY_POSTGRES_INTERNAL_DSN", "").strip()
    schema = os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational").strip() or "academy_operational"
    if not token or not account or not dsn:
        print(json.dumps({"status": "BLOCKED", "reason": "required_server_credentials_missing"}, sort_keys=True))
        return 2
    try:
        bundle = load_frozen_tournament_v3(REPO_ROOT)
        gate = PostgresProviderBudgetGate(dsn=dsn, schema=schema)
        gate.ensure_schema()
        gate.assert_provider_available()
        evidence = probe_workers_plan(api_token=token, account_id=account)
    except CloudflarePlanProbeError as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True))
        return 3
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "reason": type(exc).__name__}, sort_keys=True))
        return 4
    result = {
        "status": "READY" if evidence.state == "WORKERS_FREE" and not evidence.workers_paid_detected else "BLOCKED",
        "plan_state": evidence.state,
        "workers_paid_detected": evidence.workers_paid_detected,
        "default_usage_model": evidence.default_usage_model,
        "account_subscription_count": evidence.account_subscription_count,
        "provider_inference_used": False,
        "raw_response_recorded": False,
        "population_units": len(bundle.population["units"]),
        "future_live_attempts": bundle.manifest["population"]["total_live_attempts"],
        "max_daily_packet_neurons": bundle.manifest["usd0_budget"]["max_daily_packet_neurons"],
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "READY" else 5


if __name__ == "__main__":
    raise SystemExit(main())
