from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.handoff_audit import load_audit, validate_handoff_audit


def main() -> int:
    payload = load_audit(ROOT)
    failures = validate_handoff_audit(payload, ROOT)
    rows = payload.get("rows", [])
    groups = Counter(row.get("group") for row in rows if isinstance(row, dict))
    statuses = Counter(row.get("status") for row in rows if isinstance(row, dict))
    boundaries = payload.get("frozen_boundaries", {})

    status = "PASS" if not failures else "FAIL"
    print(f"FINAL_HANDOFF_AUDIT_VALIDATION={status}")
    print(f"FINAL_HANDOFF_AUDIT_ROWS={len(rows)}")
    for group in "ABCDEFGH":
        print(f"FINAL_HANDOFF_AUDIT_GROUP_{group}={groups.get(group, 0)}")
    for audit_status in (
        "PASS_EVIDENCED",
        "PASS_BOUNDED",
        "EXTERNALLY_BLOCKED",
        "UNEXECUTED_GATED",
        "GAP_ACTION_REQUIRED",
    ):
        print(f"FINAL_HANDOFF_AUDIT_STATUS_{audit_status}={statuses.get(audit_status, 0)}")
    print(
        "FINAL_HANDOFF_AUDIT_PROVIDER_CALLS="
        f"{boundaries.get('provider_calls_consumed')}/{boundaries.get('provider_calls_max')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_CREDENTIAL_ACCOUNT_PROBES="
        f"{boundaries.get('credential_account_probes')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_REAL_CUSTOMER_MUTATIONS="
        f"{boundaries.get('real_customer_mutations')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_SCIENTIFIC_GATE="
        f"{boundaries.get('scientific_gate')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_EV007_SHA256="
        f"{boundaries.get('ev007_report_sha256')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_EV008_SHA256="
        f"{boundaries.get('ev008_report_sha256')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_EV011_SHA256="
        f"{boundaries.get('ev011_report_sha256')}"
    )
    print(
        "FINAL_HANDOFF_AUDIT_DEMO_SHA256="
        f"{boundaries.get('delivery_demo_report_sha256')}"
    )
    if failures:
        print("FINAL_HANDOFF_AUDIT_FAILURES=" + ",".join(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
