#!/usr/bin/env python3
"""Provider-free sanitized transport diagnostic for the consumed E14v-B artifact.

The diagnostic reads only top-level experiment identity plus aggregate-safe fields
inside ``provider_meta`` and ``route_contract``. It intentionally does not read
or print case ids, selected reads, expected reads, raw outputs, prompts, private
scorer rows, private oracle rows, VALIDATION feedback, or LOCKED_TEST material.

It makes no provider call and never mutates the fixed synthetic artifact.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_REPORT_VERSION = "e14v-b-public-synthetic-route-planner-qualification-v1"
EXPECTED_CASES = 14
EXPECTED_MODEL = "openai/gpt-oss-120b"
EXPECTED_REASONING_EFFORT = "medium"
EXPECTED_TEMPERATURE = 0.0
EXPECTED_PROVIDER = "groq_zero_cost"
EXPECTED_AMENDMENT_CLASS = "external_provider_permission_remediation_only"

TRANSPORT_ERRORS = {"HTTPError", "URLError", "TimeoutError"}
RESPONSE_CONTRACT_ERRORS = {"KeyError", "JSONDecodeError"}
SAFE_ERROR_CATEGORIES = TRANSPORT_ERRORS | RESPONSE_CONTRACT_ERRORS

CLASS_PROVIDER_TRANSPORT = "PROVIDER_TRANSPORT_FAILURE"
CLASS_PROVIDER_RESPONSE = "PROVIDER_RESPONSE_CONTRACT_FAILURE"
CLASS_PLANNER_CONTRACT = "PLANNER_OUTPUT_CONTRACT_FAILURE"
CLASS_VALID = "VALID_ROUTE_CONTRACT_OUTPUTS_PRESENT"
CLASS_MIXED = "MIXED_FAILURE_MODES"
CLASS_INVALID = "INVALID_DIAGNOSTIC_ARTIFACT"
CLASS_UNKNOWN = "UNCLASSIFIED_FAILURE"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_error(value: Any) -> str:
    if value in (None, ""):
        return "NONE"
    text = str(value)
    return text if text in SAFE_ERROR_CATEGORIES else "OTHER_SANITIZED_ERROR"


def _safe_status(value: Any) -> str:
    if value is None:
        return "NONE"
    if isinstance(value, bool):
        return "INVALID"
    if isinstance(value, (int, float)) and int(value) == value:
        status = int(value)
        return str(status) if 100 <= status <= 599 else "INVALID"
    return "INVALID"


def _safe_attempts(value: Any) -> str:
    if isinstance(value, bool):
        return "INVALID"
    if isinstance(value, (int, float)) and int(value) == value:
        attempts = int(value)
        return str(attempts) if 0 <= attempts <= 20 else "INVALID"
    return "INVALID"


def _safe_reason(value: Any) -> str:
    if value in (None, ""):
        return "NONE"
    text = str(value)
    allowed = {
        "wrong_object_shape",
        "reads_not_string_array",
        "route_contract_failure",
    }
    return text if text in allowed else "OTHER_SANITIZED_REASON"


def _assert_e14v_b_identity(payload: dict[str, Any]) -> None:
    if payload.get("report_version") != EXPECTED_REPORT_VERSION:
        raise AssertionError("artifact is not the consumed E14v-B report version")
    if payload.get("dry_run") is not False:
        raise AssertionError("E14v-B diagnostic requires the consumed non-dry-run artifact")
    if payload.get("provider") != EXPECTED_PROVIDER:
        raise AssertionError("unexpected E14v-B provider marker")
    if payload.get("model") != EXPECTED_MODEL:
        raise AssertionError("unexpected E14v-B model")
    if payload.get("reasoning_effort") != EXPECTED_REASONING_EFFORT:
        raise AssertionError("unexpected E14v-B reasoning effort")
    if float(payload.get("temperature")) != EXPECTED_TEMPERATURE:
        raise AssertionError("unexpected E14v-B temperature")
    if int(payload.get("synthetic_cases") or 0) != EXPECTED_CASES:
        raise AssertionError("unexpected E14v-B synthetic case count")

    remediation = payload.get("provider_permission_remediation")
    if not isinstance(remediation, dict):
        raise AssertionError("E14v-B remediation provenance missing")
    if remediation.get("amendment_class") != EXPECTED_AMENDMENT_CLASS:
        raise AssertionError("unexpected E14v-B amendment class")
    if remediation.get("manual_permission_confirmation_received") is not True:
        raise AssertionError("E14v-B permission confirmation missing")
    if remediation.get("transport_reused_from_e14v_a_without_edits") is not True:
        raise AssertionError("E14v-B transport provenance changed")
    frozen_false = (
        "model_changed",
        "prompt_changed",
        "fixture_changed",
        "thresholds_changed",
        "provider_changed",
        "response_contract_changed",
        "temperature_changed",
        "reasoning_effort_changed",
        "real_dev_authorized_by_this_run",
    )
    for key in frozen_false:
        if remediation.get(key) is not False:
            raise AssertionError(f"E14v-B frozen provenance changed: {key}")


def _row_outcome(
    provider_error: str,
    http_status: str,
    route_contract_valid: bool,
) -> str:
    if provider_error in TRANSPORT_ERRORS:
        return "provider_transport_failure"
    if http_status not in {"NONE", "INVALID"}:
        status = int(http_status)
        if status < 200 or status >= 300:
            return "provider_transport_failure"
    if provider_error in RESPONSE_CONTRACT_ERRORS:
        return "provider_response_contract_failure"
    if provider_error == "OTHER_SANITIZED_ERROR":
        return "unclassified_failure"
    if route_contract_valid:
        return "valid_route_contract_output"
    return "planner_output_contract_failure"


def _aggregate_classification(
    outcome_counts: Counter[str],
    *,
    malformed_rows: int,
    total_rows: int,
) -> str:
    if malformed_rows:
        return CLASS_INVALID
    if total_rows != EXPECTED_CASES:
        return CLASS_INVALID

    present = {name for name, count in outcome_counts.items() if count}
    if present == {"provider_transport_failure"}:
        return CLASS_PROVIDER_TRANSPORT
    if present == {"provider_response_contract_failure"}:
        return CLASS_PROVIDER_RESPONSE
    if present == {"planner_output_contract_failure"}:
        return CLASS_PLANNER_CONTRACT
    if present == {"valid_route_contract_output"}:
        return CLASS_VALID
    if not present or present == {"unclassified_failure"}:
        return CLASS_UNKNOWN
    return CLASS_MIXED


def run(path: Path) -> dict[str, Any]:
    payload = _load(path)
    if not isinstance(payload, dict):
        raise AssertionError("synthetic artifact must be a JSON object")
    _assert_e14v_b_identity(payload)

    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("synthetic artifact rows missing")
    if len(rows) != EXPECTED_CASES:
        raise AssertionError("E14v-B artifact must contain exactly 14 rows")

    provider_errors: Counter[str] = Counter()
    http_statuses: Counter[str] = Counter()
    contract_reasons: Counter[str] = Counter()
    transport_attempts: Counter[str] = Counter()
    row_outcomes: Counter[str] = Counter()

    valid_contract_rows = 0
    malformed_rows = 0
    rows_with_provider_error = 0
    rows_with_no_provider_error = 0
    rows_with_non_2xx_http = 0

    for row in rows:
        if not isinstance(row, dict):
            malformed_rows += 1
            row_outcomes["malformed_artifact_row"] += 1
            continue

        provider = row.get("provider_meta")
        provider = provider if isinstance(provider, dict) else {}
        error = _safe_error(provider.get("error"))
        status = _safe_status(provider.get("http_status"))
        attempts = _safe_attempts(provider.get("transport_attempts"))

        provider_errors[error] += 1
        http_statuses[status] += 1
        transport_attempts[attempts] += 1
        rows_with_provider_error += int(error != "NONE")
        rows_with_no_provider_error += int(error == "NONE")
        if status not in {"NONE", "INVALID"}:
            code = int(status)
            rows_with_non_2xx_http += int(code < 200 or code >= 300)

        contract = row.get("route_contract")
        contract = contract if isinstance(contract, dict) else {}
        valid = contract.get("valid") is True
        reason = _safe_reason(contract.get("reason"))
        contract_reasons[reason] += 1
        valid_contract_rows += int(valid)

        row_outcomes[_row_outcome(error, status, valid)] += 1

    classification = _aggregate_classification(
        row_outcomes,
        malformed_rows=malformed_rows,
        total_rows=len(rows),
    )
    route_quality_fully_evaluable = (
        malformed_rows == 0 and valid_contract_rows == EXPECTED_CASES
    )
    planner_quality_failure_established = classification == CLASS_PLANNER_CONTRACT
    operational_failure_established = classification in {
        CLASS_PROVIDER_TRANSPORT,
        CLASS_PROVIDER_RESPONSE,
    }

    return {
        "report_version": "e14v-b-sanitized-transport-diagnostic-v1",
        "source_report_version": EXPECTED_REPORT_VERSION,
        "synthetic_rows": len(rows),
        "malformed_rows": malformed_rows,
        "rows_with_provider_error": rows_with_provider_error,
        "rows_with_no_provider_error": rows_with_no_provider_error,
        "rows_with_non_2xx_http_status": rows_with_non_2xx_http,
        "provider_error_category_counts": dict(sorted(provider_errors.items())),
        "http_status_count_distribution": dict(sorted(http_statuses.items())),
        "transport_attempt_count_distribution": dict(sorted(transport_attempts.items())),
        "route_contract_reason_counts": dict(sorted(contract_reasons.items())),
        "valid_route_contract_rows": valid_contract_rows,
        "sanitized_row_outcome_counts": dict(sorted(row_outcomes.items())),
        "classification": classification,
        "operational_failure_established": operational_failure_established,
        "planner_output_contract_failure_established": planner_quality_failure_established,
        "route_quality_fully_evaluable": route_quality_fully_evaluable,
        "diagnostic_makes_provider_call": False,
        "diagnostic_writes_source_artifact": False,
        "prints_case_ids": False,
        "prints_selected_reads": False,
        "prints_expected_reads": False,
        "prints_raw_outputs": False,
        "prints_prompts": False,
        "reads_private_oracle": False,
        "reads_private_scorer_rows": False,
        "uses_validation_feedback": False,
        "uses_locked_test": False,
    }


def _fixture_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "report_version": EXPECTED_REPORT_VERSION,
        "status": "E14V_PUBLIC_SYNTHETIC_ROUTE_PLANNER_QUALIFICATION_FAIL",
        "dry_run": False,
        "provider": EXPECTED_PROVIDER,
        "model": EXPECTED_MODEL,
        "reasoning_effort": EXPECTED_REASONING_EFFORT,
        "temperature": EXPECTED_TEMPERATURE,
        "synthetic_cases": EXPECTED_CASES,
        "provider_permission_remediation": {
            "amendment_class": EXPECTED_AMENDMENT_CLASS,
            "manual_permission_confirmation_received": True,
            "transport_reused_from_e14v_a_without_edits": True,
            "model_changed": False,
            "prompt_changed": False,
            "fixture_changed": False,
            "thresholds_changed": False,
            "provider_changed": False,
            "response_contract_changed": False,
            "temperature_changed": False,
            "reasoning_effort_changed": False,
            "real_dev_authorized_by_this_run": False,
        },
        "rows": rows,
    }


def _safe_test_row(
    *,
    error: str | None,
    http_status: int | None,
    attempts: int,
    valid: bool,
    reason: str | None,
) -> dict[str, Any]:
    return {
        # Deliberately include forbidden-to-print source fields so the self-check
        # proves they are not propagated into the report.
        "case_id": "SECRET_CASE_MARKER",
        "selected_reads": ["SECRET_SELECTED_READ_MARKER"],
        "expected_reads": ["SECRET_EXPECTED_READ_MARKER"],
        "provider_meta": {
            "error": error,
            "http_status": http_status,
            "transport_attempts": attempts,
        },
        "route_contract": {
            "valid": valid,
            "reason": reason,
        },
    }


def run_self_checks() -> None:
    scenarios = [
        (
            CLASS_PROVIDER_TRANSPORT,
            _safe_test_row(
                error="HTTPError",
                http_status=403,
                attempts=3,
                valid=False,
                reason="wrong_object_shape",
            ),
        ),
        (
            CLASS_PROVIDER_RESPONSE,
            _safe_test_row(
                error="JSONDecodeError",
                http_status=200,
                attempts=3,
                valid=False,
                reason="wrong_object_shape",
            ),
        ),
        (
            CLASS_PLANNER_CONTRACT,
            _safe_test_row(
                error=None,
                http_status=200,
                attempts=1,
                valid=False,
                reason="route_contract_failure",
            ),
        ),
        (
            CLASS_VALID,
            _safe_test_row(
                error=None,
                http_status=200,
                attempts=1,
                valid=True,
                reason=None,
            ),
        ),
    ]

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for index, (expected_classification, row) in enumerate(scenarios):
            path = root / f"scenario-{index}.json"
            path.write_text(
                json.dumps(_fixture_payload([row for _ in range(EXPECTED_CASES)])),
                encoding="utf-8",
            )
            report = run(path)
            assert report["classification"] == expected_classification
            rendered = json.dumps(report, sort_keys=True)
            for forbidden in (
                "SECRET_CASE_MARKER",
                "SECRET_SELECTED_READ_MARKER",
                "SECRET_EXPECTED_READ_MARKER",
            ):
                assert forbidden not in rendered

        mixed_rows = [
            _safe_test_row(
                error="HTTPError",
                http_status=403,
                attempts=3,
                valid=False,
                reason="wrong_object_shape",
            )
            for _ in range(EXPECTED_CASES - 1)
        ]
        mixed_rows.append(
            _safe_test_row(
                error=None,
                http_status=200,
                attempts=1,
                valid=False,
                reason="route_contract_failure",
            )
        )
        path = root / "mixed.json"
        path.write_text(json.dumps(_fixture_payload(mixed_rows)), encoding="utf-8")
        assert run(path)["classification"] == CLASS_MIXED


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-output-file", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        run_self_checks()
        print(json.dumps({"status": "E14V_B_SANITIZED_TRANSPORT_DIAGNOSTIC_SELFCHECK_PASS"}, indent=2))
        return 0

    if args.synthetic_output_file is None:
        parser.error("--synthetic-output-file is required unless --self-check is used")
    print(json.dumps(run(args.synthetic_output_file), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
