#!/usr/bin/env python3
"""Print aggregate-only error categories for an E14v synthetic artifact.

This diagnostic never prints case ids, selected reads, expected reads, raw model
outputs, prompts, identifiers, or per-row data. It is intended only to decide
whether an already-consumed public synthetic attempt failed at transport/parse/
shape level before any scientific amendment is considered.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-output-file", type=Path, required=True)
    args = parser.parse_args()

    payload = load(args.synthetic_output_file)
    if not isinstance(payload, dict):
        raise AssertionError("synthetic artifact must be an object")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("synthetic artifact rows missing")

    provider_errors: Counter[str] = Counter()
    contract_reasons: Counter[str] = Counter()
    transport_attempts: Counter[str] = Counter()
    valid_contract_rows = 0
    rows_with_provider_error = 0
    rows_with_no_provider_error = 0

    for row in rows:
        if not isinstance(row, dict):
            provider_errors["malformed_row"] += 1
            continue
        provider = row.get("provider_meta")
        provider = provider if isinstance(provider, dict) else {}
        err = provider.get("error")
        key = str(err) if err not in (None, "") else "NONE"
        provider_errors[key] += 1
        rows_with_provider_error += int(key != "NONE")
        rows_with_no_provider_error += int(key == "NONE")
        transport_attempts[str(provider.get("transport_attempts"))] += 1

        contract = row.get("route_contract")
        contract = contract if isinstance(contract, dict) else {}
        reason = contract.get("reason")
        contract_reasons[str(reason) if reason not in (None, "") else "NONE"] += 1
        valid_contract_rows += int(contract.get("valid") is True)

    report = {
        "report_version": "e14v-synthetic-sanitized-failure-diagnostic-v1",
        "synthetic_rows": len(rows),
        "rows_with_provider_error": rows_with_provider_error,
        "rows_with_no_provider_error": rows_with_no_provider_error,
        "provider_error_category_counts": dict(sorted(provider_errors.items())),
        "transport_attempt_count_distribution": dict(sorted(transport_attempts.items())),
        "route_contract_reason_counts": dict(sorted(contract_reasons.items())),
        "valid_route_contract_rows": valid_contract_rows,
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
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
