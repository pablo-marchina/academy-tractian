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
    CloudflareSameDayZeroUseReceiptV1,
    same_day_zero_use_authorization_to_adr020_pre_live_evidence,
    validate_frozen_same_day_zero_use_amendment,
)
from academy_tractian.cloudflare_provider_live_v2 import (  # noqa: E402
    CloudflareLiveSecrets,
    GovernedCloudflareLiveTaskV2,
    build_cloudflare_one_shot_transport_v2,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the frozen ADR-020 Cloudflare packet only after a valid ADR-024 "
            "same-day zero-use receipt has already been issued."
        )
    )
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    return parser


def _current_utc() -> datetime:
    return datetime.now(timezone.utc)


def main() -> None:
    args = _parser().parse_args()

    validate_frozen_same_day_zero_use_amendment()
    evidence = CloudflareSameDayZeroUseEvidenceV1.model_validate(
        json.loads(args.evidence.read_text(encoding="utf-8"))
    )
    receipt = CloudflareSameDayZeroUseReceiptV1.model_validate(
        json.loads(args.receipt.read_text(encoding="utf-8"))
    )
    pre_live_evidence = same_day_zero_use_authorization_to_adr020_pre_live_evidence(
        receipt,
        evidence,
        custody_root=args.custody_root,
        now_utc=_current_utc(),
    )

    secrets = CloudflareLiveSecrets(
        api_token=os.environ.get("CLOUDFLARE_API_TOKEN", ""),
        account_id=os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""),
    )
    transport = build_cloudflare_one_shot_transport_v2()
    task = GovernedCloudflareLiveTaskV2.prepare(
        custody_root=args.custody_root,
        secrets=secrets,
        pre_live_evidence=pre_live_evidence,
        transport=transport,
        fixture_result=False,
    )
    result = task.execute_all()

    print(
        json.dumps(
            result.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
