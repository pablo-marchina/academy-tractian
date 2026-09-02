from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from academy_tractian.cloudflare_live_authorization_same_day_v3 import (  # noqa: E402
    CloudflareSameDayZeroUseEvidenceV1,
    issue_same_day_zero_use_receipt,
    validate_frozen_same_day_zero_use_amendment,
)


FORBIDDEN_PROVIDER_ENV = (
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Issue an ADR-024 same-day zero-use authorization receipt without provider I/O."
        )
    )
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    args = _parser().parse_args()
    present = [name for name in FORBIDDEN_PROVIDER_ENV if os.environ.get(name)]
    if present:
        raise SystemExit(
            "same-day receipt must be issued before provider secrets are provisioned: "
            + ",".join(present)
        )

    validate_frozen_same_day_zero_use_amendment()
    evidence = CloudflareSameDayZeroUseEvidenceV1.model_validate(
        json.loads(args.evidence.read_text(encoding="utf-8"))
    )
    receipt = issue_same_day_zero_use_receipt(
        evidence,
        custody_root=args.custody_root,
        now_utc=datetime.now(timezone.utc),
    )

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
        raise SystemExit("same-day receipt output already exists") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    print(
        json.dumps(
            {
                "status": "SAME_DAY_ZERO_USE_RECEIPT_ISSUED",
                "receipt_sha256": receipt.receipt_sha256,
                "expires_at_utc": receipt.expires_at_utc.isoformat(),
                "derived_free_neurons": receipt.derived_free_neurons_at_issue,
                "provider_model_inference_calls": 0,
                "credential_account_probes": 0,
                "live_network_validation": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
