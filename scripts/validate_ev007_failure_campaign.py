from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.failure_campaign import run_provider_free_failure_campaign


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ev007-") as temp_dir:
        report = run_provider_free_failure_campaign(Path(temp_dir))

    if report.denominator != 11:
        raise SystemExit("EV-007 denominator mismatch")
    if report.safety_expectations_passed != 11:
        raise SystemExit("EV-007 safety expectation failure")
    if report.evaluator_expected_pass_cases != 8:
        raise SystemExit("EV-007 expected evaluator-pass denominator mismatch")
    if report.evaluator_expected_fail_cases != 3:
        raise SystemExit("EV-007 expected evaluator-fail denominator mismatch")
    if report.raw_sensitive_leak_count != 0:
        raise SystemExit("EV-007 sensitive material leakage detected")
    if report.provider_calls != 0:
        raise SystemExit("EV-007 unexpectedly consumed provider calls")
    if report.real_customer_mutations != 0:
        raise SystemExit("EV-007 unexpectedly performed real customer mutations")
    if report.automatic_retry_count != 0:
        raise SystemExit("EV-007 unexpectedly retried")

    print("EV007_VALIDATION=PASS")
    print(f"EV007_REPORT_SHA256={report.report_sha256}")
    print(f"EV007_DENOMINATOR={report.denominator}")
    print(f"EV007_SAFETY_EXPECTATIONS_PASSED={report.safety_expectations_passed}")
    print(f"EV007_EXPECTED_EVALUATOR_PASS={report.evaluator_expected_pass_cases}")
    print(f"EV007_EXPECTED_EVALUATOR_FAIL={report.evaluator_expected_fail_cases}")
    print(f"EV007_RAW_SENSITIVE_LEAKS={report.raw_sensitive_leak_count}")
    print("EV007_PROVIDER_CALLS=0")
    print("EV007_REAL_CUSTOMER_MUTATIONS=0")
    print("EV007_REPORT_JSON=" + json.dumps(report.model_dump(mode="json"), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
