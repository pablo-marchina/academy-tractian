from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.final_freeze_bundle import (
    load_final_freeze_manifest,
    validate_final_freeze_manifest,
)


def main() -> int:
    manifest = load_final_freeze_manifest(ROOT)
    failures = validate_final_freeze_manifest(manifest, ROOT)
    statuses = Counter(decision.status for decision in manifest.decisions)

    status = "PASS" if not failures else "FAIL"
    print(f"FINAL_FREEZE_BUNDLE_VALIDATION={status}")
    print(f"FINAL_FREEZE_BUNDLE_STATE={manifest.bundle_state}")
    print(f"FINAL_FREEZE_BUNDLE_SHA256={manifest.manifest_sha256}")
    print(f"FINAL_FREEZE_ARTIFACTS={len(manifest.artifacts)}")
    print(f"FINAL_FREEZE_DECISIONS={len(manifest.decisions)}")
    print(f"FINAL_FREEZE_REQUIRED_GATE={manifest.required_gate_name}")
    print(
        "FINAL_FREEZE_BRANCH_PROTECTION_ENFORCED="
        f"{str(manifest.branch_protection_enforced).lower()}"
    )
    for decision_status in (
        "PASS_EVIDENCED",
        "PASS_BOUNDED",
        "NO_SELECTION",
        "NO_CHANGE",
        "NOT_PROMOTED",
        "NOT_READY_HUMAN_DATA",
        "EXTERNALLY_BLOCKED",
        "PENDING_EXTERNAL_ENFORCEMENT",
    ):
        print(
            f"FINAL_FREEZE_STATUS_{decision_status}="
            f"{statuses.get(decision_status, 0)}"
        )
    if failures:
        print("FINAL_FREEZE_FAILURES=" + ",".join(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
