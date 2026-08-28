from __future__ import annotations

import json
from pathlib import Path
import tempfile

from academy_tractian.stability_campaign import (
    STABILITY_DIMENSIONS,
    run_provider_free_stability_campaign,
)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ev008-stability-") as temp_dir:
        report = run_provider_free_stability_campaign(Path(temp_dir))

    failures: list[str] = []
    if report.unit_count != 6:
        failures.append(f"unit_count={report.unit_count}")
    if report.repetitions_per_unit != 5:
        failures.append(f"repetitions_per_unit={report.repetitions_per_unit}")
    if report.denominator != 30:
        failures.append(f"denominator={report.denominator}")
    if report.stable_unit_count != 6:
        failures.append(f"stable_unit_count={report.stable_unit_count}")
    if report.stable_dimension_checks != 66:
        failures.append(f"stable_dimension_checks={report.stable_dimension_checks}")
    if report.total_dimension_checks != 66:
        failures.append(f"total_dimension_checks={report.total_dimension_checks}")
    if report.contract_expectations_passed != 30:
        failures.append(f"contract_expectations_passed={report.contract_expectations_passed}")
    if report.sensitive_leak_count != 0:
        failures.append(f"sensitive_leak_count={report.sensitive_leak_count}")
    if report.automatic_retry_count != 0:
        failures.append(f"automatic_retry_count={report.automatic_retry_count}")
    if report.replay_count != 0:
        failures.append(f"replay_count={report.replay_count}")
    if report.provider_calls != 0:
        failures.append(f"provider_calls={report.provider_calls}")
    if report.real_customer_mutations != 0:
        failures.append(f"real_customer_mutations={report.real_customer_mutations}")

    for summary in report.summaries:
        if not summary.all_dimensions_stable:
            failures.append(
                f"{summary.unit_id}.unstable={','.join(summary.unstable_dimensions)}"
            )
        if summary.stable_dimensions != STABILITY_DIMENSIONS:
            failures.append(f"{summary.unit_id}.stable_dimensions_mismatch")
        if summary.contract_expectations_passed != 5:
            failures.append(
                f"{summary.unit_id}.contract_expectations_passed={summary.contract_expectations_passed}"
            )

    action_summary = next(summary for summary in report.summaries if summary.unit_id == "STAB-05")
    if action_summary.transport_count != 5:
        failures.append(f"STAB-05.transport_count={action_summary.transport_count}")
    if action_summary.action_transport_count != 5:
        failures.append(
            f"STAB-05.action_transport_count={action_summary.action_transport_count}"
        )

    if failures:
        print("EV008_VALIDATION=FAIL")
        for failure in failures:
            print(f"EV008_FAILURE={failure}")
        return 1

    print("EV008_VALIDATION=PASS")
    print(f"EV008_REPORT_SHA256={report.report_sha256}")
    print(f"EV008_DENOMINATOR={report.denominator}")
    print(f"EV008_STABLE_UNITS={report.stable_unit_count}")
    print(f"EV008_STABLE_DIMENSION_CHECKS={report.stable_dimension_checks}")
    print(f"EV008_TOTAL_DIMENSION_CHECKS={report.total_dimension_checks}")
    print(f"EV008_CONTRACT_EXPECTATIONS_PASSED={report.contract_expectations_passed}")
    print(f"EV008_RAW_SENSITIVE_LEAKS={report.sensitive_leak_count}")
    print(f"EV008_PROVIDER_CALLS={report.provider_calls}")
    print(f"EV008_REAL_CUSTOMER_MUTATIONS={report.real_customer_mutations}")
    print(f"EV008_AUTOMATIC_RETRIES={report.automatic_retry_count}")
    print(f"EV008_REPLAYS={report.replay_count}")
    print(
        "EV008_REPORT_JSON="
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
