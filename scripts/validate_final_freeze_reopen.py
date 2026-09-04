from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.final_freeze_reopen import (
    load_final_freeze_reopen_manifest,
    validate_final_freeze_reopen_manifest,
)


def main() -> int:
    manifest = load_final_freeze_reopen_manifest(ROOT)
    failures = validate_final_freeze_reopen_manifest(manifest, ROOT)
    status = "PASS" if not failures else "FAIL"
    print(f"FINAL_FREEZE_REOPEN_VALIDATION={status}")
    print(f"FINAL_FREEZE_STATE={manifest.state}")
    print(f"FINAL_FREEZE_REOPEN_SHA256={manifest.manifest_sha256}")
    print(
        "FINAL_FREEZE_SUPERSEDED_BLOB_SHA1="
        f"{manifest.superseded_manifest_git_blob_sha1}"
    )
    print(
        "LOCAL_REQUIRED_COMPONENTS_TARGET="
        f"{manifest.hard_constraints['local_required_components_target']}"
    )
    print(f"FINAL_FREEZE_BLOCKING_GATES={len(manifest.blocking_gates)}")
    if failures:
        print("FINAL_FREEZE_REOPEN_FAILURES=" + ",".join(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
