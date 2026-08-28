from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.communication_campaign import run_provider_free_communication_campaign


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ev011-communication-") as temp_dir:
        report = run_provider_free_communication_campaign(Path(temp_dir))

    failures: list[str] = []
    expected = {
        "denominator": 10,
        "total_predicate_slots": 120,
        "applicable_predicate_checks": 60,
        "passed_predicate_checks": 60,
        "failed_predicate_checks": 0,
        "not_applicable_predicate_checks": 60,
        "contract_expectations_passed": 10,
        "provider_calls": 0,
        "real_customer_mutations": 0,
        "semantic_private_blind_access": 0,
        "automatic_retry_count": 0,
        "replay_count": 0,
    }
    for field, value in expected.items():
        actual = getattr(report, field)
        if actual != value:
            failures.append(f"{field}={actual},expected={value}")

    for result in report.results:
        if not result.contract_expectations_met:
            failures.append(f"{result.case_id}.contract_expectations_met=false")
        if result.failed_predicate_count != 0:
            failures.append(f"{result.case_id}.failed_predicates={result.failed_predicate_count}")
        if result.passed_predicate_count != result.applicable_predicate_count:
            failures.append(
                f"{result.case_id}.passed={result.passed_predicate_count},applicable={result.applicable_predicate_count}"
            )
        if not result.trace_lifecycle_valid:
            failures.append(f"{result.case_id}.trace_lifecycle_valid=false")

    if failures:
        print("EV011_VALIDATION=FAIL")
        for failure in failures:
            print(f"EV011_FAILURE={failure}")
        return 1

    print("EV011_VALIDATION=PASS")
    print(f"EV011_REPORT_SHA256={report.report_sha256}")
    print(f"EV011_DENOMINATOR={report.denominator}")
    print(f"EV011_APPLICABLE_PREDICATES={report.applicable_predicate_checks}")
    print(f"EV011_PASSED_PREDICATES={report.passed_predicate_checks}")
    print(f"EV011_FAILED_PREDICATES={report.failed_predicate_checks}")
    print(f"EV011_NOT_APPLICABLE_PREDICATES={report.not_applicable_predicate_checks}")
    print(f"EV011_CONTRACT_EXPECTATIONS_PASSED={report.contract_expectations_passed}")
    print(f"EV011_PROVIDER_CALLS={report.provider_calls}")
    print(f"EV011_REAL_CUSTOMER_MUTATIONS={report.real_customer_mutations}")
    print(f"EV011_SEMANTIC_PRIVATE_BLIND_ACCESS={report.semantic_private_blind_access}")
    print(f"EV011_AUTOMATIC_RETRIES={report.automatic_retry_count}")
    print(f"EV011_REPLAYS={report.replay_count}")
    for result in report.results:
        print(f"EV011_{result.case_id.replace('-', '_')}_SPEC_SHA256={result.spec_sha256}")
        print(f"EV011_{result.case_id.replace('-', '_')}_RESULT_SHA256={result.result_sha256}")
    print(
        "EV011_REPORT_JSON="
        + json.dumps(
            report.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
