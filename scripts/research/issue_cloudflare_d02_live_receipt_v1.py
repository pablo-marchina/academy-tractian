from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (SRC_ROOT, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from academy_tractian.cloudflare_d02_live_authorization_v1 import (  # noqa: E402
    CloudflareD02ZeroUseEvidenceV1,
    issue_d02_live_authorization_receipt,
    validate_frozen_d02_live_authorization,
)
from academy_tractian.cloudflare_reset_window_capture_v1 import (  # noqa: E402
    ResetWindowCaptureError,
    ensure_provider_credentials_absent,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Issue a short-lived provider-free D02 live receipt.")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        ensure_provider_credentials_absent()
        validate_frozen_d02_live_authorization(REPO_ROOT)
        evidence = CloudflareD02ZeroUseEvidenceV1.model_validate(
            json.loads(args.evidence.read_text(encoding="utf-8"))
        )
        receipt = issue_d02_live_authorization_receipt(
            evidence,
            custody_root=args.custody_root.expanduser().resolve(strict=False),
            now_utc=datetime.now(timezone.utc),
        )
    except (ResetWindowCaptureError, ValueError, OSError) as exc:
        raise SystemExit(str(exc)) from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        receipt.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"
    try:
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SystemExit("D02 receipt output already exists") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    print(
        json.dumps(
            {
                "status": "D02_LIVE_RECEIPT_ISSUED_PROVIDER_FREE",
                "issued_at_utc": receipt.issued_at_utc.isoformat(),
                "expires_at_utc": receipt.expires_at_utc.isoformat(),
                "derived_free_neurons": receipt.derived_free_neurons_at_issue,
                "d02_worst_case_packet_neurons": receipt.d02_worst_case_packet_neurons,
                "provider_model_inference_calls": 0,
                "credential_account_probes": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
