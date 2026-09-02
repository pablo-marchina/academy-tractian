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

from academy_tractian.cloudflare_d02_live_authorization_v1 import (  # noqa: E402
    CloudflareD02LiveAuthorizationReceiptV1,
    CloudflareD02ZeroUseEvidenceV1,
    d02_receipt_to_pre_live_evidence,
    validate_frozen_d02_live_authorization,
)
from academy_tractian.cloudflare_frozen_bundle_portability import (  # noqa: E402
    materialize_canonical_frozen_bundle,
)
from academy_tractian.cloudflare_provider_comparison_v2 import (  # noqa: E402
    GLM_CANDIDATE_ID,
    NEMOTRON_CANDIDATE_ID,
)
from academy_tractian.cloudflare_provider_d02_executor import (  # noqa: E402
    CLOUDFLARE_D02_RUN_DIRNAME,
    GovernedCloudflareD02Execution,
    build_d02_clients,
    reserve_d02_custody,
)
from academy_tractian.cloudflare_provider_live_v2 import (  # noqa: E402
    build_cloudflare_one_shot_transport_v2,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute D02 only after a valid ADR-027 fresh-reset receipt. "
            "This is the sole D02 live entrypoint."
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

    # All protocol/evidence/custody validation happens before provider credentials are read.
    validate_frozen_d02_live_authorization(REPO_ROOT)
    evidence = CloudflareD02ZeroUseEvidenceV1.model_validate(
        json.loads(args.evidence.read_text(encoding="utf-8"))
    )
    receipt = CloudflareD02LiveAuthorizationReceiptV1.model_validate(
        json.loads(args.receipt.read_text(encoding="utf-8"))
    )
    custody_root = args.custody_root.expanduser().resolve(strict=False)
    pre_live_evidence = d02_receipt_to_pre_live_evidence(
        receipt,
        evidence,
        custody_root=custody_root,
        now_utc=_current_utc(),
    )

    # Credentials enter process state only after authorization succeeded and are never persisted.
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if not api_token.strip() or not account_id.strip():
        raise SystemExit("D02 launcher requires CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID")

    transport = build_cloudflare_one_shot_transport_v2()
    clients = build_d02_clients(
        api_token=api_token,
        account_id=account_id,
        transports={
            GLM_CANDIDATE_ID: transport,
            NEMOTRON_CANDIDATE_ID: transport,
        },
    )

    with TemporaryDirectory(prefix="academy-tractian-cloudflare-d02-frozen-") as temp_dir:
        frozen_root = Path(temp_dir)
        materialize_canonical_frozen_bundle(
            repo_root=REPO_ROOT,
            target_root=frozen_root,
        )

        # Custody reservation is exclusive-create and precedes the governed run directory.
        reserve_d02_custody(
            custody_root=custody_root,
            pre_live_evidence=pre_live_evidence,
        )
        execution = GovernedCloudflareD02Execution.prepare(
            run_dir=custody_root / CLOUDFLARE_D02_RUN_DIRNAME,
            clients=clients,
            pre_live_evidence=pre_live_evidence,
            fixture_result=False,
            repo_root=frozen_root,
        )

        original_cwd = Path.cwd()
        try:
            os.chdir(frozen_root)
            result = execution.execute_all()
        finally:
            os.chdir(original_cwd)

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
