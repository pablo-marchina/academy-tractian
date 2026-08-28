from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.delivery_reproduction import run_provider_free_delivery_demo


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="delivery-reproduction-") as tmp:
        report = run_provider_free_delivery_demo(Path(tmp) / "demo")

    failures: list[str] = []
    if report.denominator != 5:
        failures.append("denominator")
    if report.exact_traces_evaluated != 5:
        failures.append("exact_traces_evaluated")
    if report.contract_expectations_passed != 5:
        failures.append("contract_expectations_passed")
    if report.provider_calls != 0:
        failures.append("provider_calls")
    if report.credential_account_probes != 0:
        failures.append("credential_account_probes")
    if report.real_customer_mutations != 0:
        failures.append("real_customer_mutations")
    if report.semantic_private_blind_access != 0:
        failures.append("semantic_private_blind_access")
    if report.automatic_retry_count != 0:
        failures.append("automatic_retry_count")
    if report.replay_count != 0:
        failures.append("replay_count")
    if not all(result.trace_lifecycle_valid for result in report.results):
        failures.append("trace_lifecycle")
    if not all(result.evaluator_pass for result in report.results):
        failures.append("evaluator_classification")
    if not all(result.contract_expectations_met for result in report.results):
        failures.append("scenario_contracts")

    controlled = report.results[-1]
    if controlled.scenario_id != "DEMO-05":
        failures.append("controlled_scenario_order")
    if controlled.action_transport_count != 1:
        failures.append("controlled_action_transport_count")
    if controlled.durable_claim_count != 1:
        failures.append("controlled_durable_claim_count")

    status = "PASS" if not failures else "FAIL"
    print(f"DELIVERY_REPRODUCTION_VALIDATION={status}")
    print(f"DELIVERY_DEMO_REPORT_SHA256={report.report_sha256}")
    print(f"DELIVERY_DEMO_DENOMINATOR={report.denominator}")
    print(f"DELIVERY_DEMO_EXACT_TRACES_EVALUATED={report.exact_traces_evaluated}")
    print(f"DELIVERY_DEMO_CONTRACT_EXPECTATIONS_PASSED={report.contract_expectations_passed}")
    print(f"DELIVERY_DEMO_PROVIDER_CALLS={report.provider_calls}")
    print(f"DELIVERY_DEMO_CREDENTIAL_ACCOUNT_PROBES={report.credential_account_probes}")
    print(f"DELIVERY_DEMO_REAL_CUSTOMER_MUTATIONS={report.real_customer_mutations}")
    print(f"DELIVERY_DEMO_SEMANTIC_PRIVATE_BLIND_ACCESS={report.semantic_private_blind_access}")
    for result in report.results:
        key = result.scenario_id.replace("-", "_")
        print(f"DELIVERY_{key}_SPEC_SHA256={result.spec_sha256}")
        print(f"DELIVERY_{key}_RESULT_SHA256={result.result_sha256}")
        print(f"DELIVERY_{key}_TRACE_SHA256={result.trace_sha256}")
        print(f"DELIVERY_{key}_BEHAVIOR_SHA256={result.behavioral_trace_sha256}")
    if failures:
        print("DELIVERY_REPRODUCTION_FAILURES=" + ",".join(failures))
    print(
        "DELIVERY_DEMO_REPORT_JSON="
        + json.dumps(
            report.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
