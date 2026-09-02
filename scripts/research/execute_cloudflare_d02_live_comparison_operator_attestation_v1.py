from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (SRC_ROOT, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from academy_tractian.cloudflare_frozen_bundle_portability import (  # noqa: E402
    materialize_canonical_frozen_bundle,
)
from academy_tractian.cloudflare_live_authorization_d02_v1 import (  # noqa: E402
    CloudflareD02OperatorAttestationEvidenceV1,
    CloudflareD02OperatorAttestationReceiptV1,
    d02_operator_attestation_to_pre_live_evidence,
    validate_frozen_d02_live_authorization,
)
from academy_tractian.cloudflare_provider_d02_live import (  # noqa: E402
    GovernedCloudflareD02LiveTaskV1,
    build_cloudflare_d02_one_shot_transport,
)
from academy_tractian.cloudflare_provider_live_v2 import CloudflareLiveSecrets  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute one governed D02 packet only after a valid ADR-027 D02 receipt. No replay/resume is supported.")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    return parser


def _current_utc() -> datetime:
    return datetime.now(timezone.utc)


def main() -> None:
    args = _parser().parse_args()

    # All authorization and frozen-input validation happens before provider secrets are read.
    validate_frozen_d02_live_authorization(REPO_ROOT)
    evidence = CloudflareD02OperatorAttestationEvidenceV1.model_validate(
        json.loads(args.evidence.read_text(encoding="utf-8"))
    )
    receipt = CloudflareD02OperatorAttestationReceiptV1.model_validate(
        json.loads(args.receipt.read_text(encoding="utf-8"))
    )
    custody_root = args.custody_root.expanduser().resolve(strict=False)
    pre_live_evidence = d02_operator_attestation_to_pre_live_evidence(
        receipt,
        evidence,
        custody_root=custody_root,
        now_utc=_current_utc(),
    )

    # First credential read occurs only after the authorization gate above succeeds.
    secrets = CloudflareLiveSecrets(
        api_token=os.environ.get("CLOUDFLARE_API_TOKEN", ""),
        account_id=os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""),
    )
    transport = build_cloudflare_d02_one_shot_transport()

    with TemporaryDirectory(prefix="academy-tractian-cloudflare-d02-frozen-") as temp_dir:
        frozen_root = Path(temp_dir)
        materialize_canonical_frozen_bundle(
            repo_root=REPO_ROOT,
            target_root=frozen_root,
        )
        task = GovernedCloudflareD02LiveTaskV1.prepare(
            custody_root=custody_root,
            secrets=secrets,
            pre_live_evidence=pre_live_evidence,
            transport=transport,
            fixture_result=False,
            repo_root=frozen_root,
        )
        result = task.execute_all()

    print(json.dumps(result.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
