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

from academy_tractian.cloudflare_reset_window_capture_v1 import (  # noqa: E402
    ResetWindowCaptureError,
    build_reset_window_evidence,
    ensure_provider_credentials_absent,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture sanitized ADR-022 reset-window evidence without provider I/O."
    )
    parser.add_argument("--workers-free-source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--attest-workers-free-active", action="store_true")
    parser.add_argument("--attest-workers-paid-disabled", action="store_true")
    parser.add_argument("--attest-no-workers-ai-calls-since-reset", action="store_true")
    parser.add_argument(
        "--attest-no-automated-workers-ai-consumers-since-reset",
        action="store_true",
    )
    parser.add_argument(
        "--attest-exclusive-workers-ai-window-until-packet-completion",
        action="store_true",
    )
    parser.add_argument("--attest-direct-workers-ai-route", action="store_true")
    parser.add_argument(
        "--attest-no-ai-gateway-or-prepaid-unified-billing",
        action="store_true",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        ensure_provider_credentials_absent()
        evidence = build_reset_window_evidence(
            workers_free_source_artifact=args.workers_free_source,
            now_utc=datetime.now(timezone.utc),
            attest_workers_free_active=args.attest_workers_free_active,
            attest_workers_paid_disabled=args.attest_workers_paid_disabled,
            attest_no_workers_ai_calls_since_reset=(
                args.attest_no_workers_ai_calls_since_reset
            ),
            attest_no_automated_workers_ai_consumers_since_reset=(
                args.attest_no_automated_workers_ai_consumers_since_reset
            ),
            attest_exclusive_workers_ai_window_until_packet_completion=(
                args.attest_exclusive_workers_ai_window_until_packet_completion
            ),
            attest_direct_workers_ai_route=args.attest_direct_workers_ai_route,
            attest_no_ai_gateway_or_prepaid_unified_billing=(
                args.attest_no_ai_gateway_or_prepaid_unified_billing
            ),
        )
    except (ResetWindowCaptureError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        evidence.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"
    try:
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SystemExit("evidence output already exists") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    print(
        json.dumps(
            {
                "status": "RESET_WINDOW_EVIDENCE_CAPTURED_PROVIDER_FREE",
                "observed_at_utc": evidence.observed_at_utc.isoformat(),
                "reset_at_utc": evidence.reset_at_utc.isoformat(),
                "utc_day": evidence.utc_day,
                "derived_free_neurons_remaining": evidence.derived_free_neurons_remaining,
                "source_artifact_sha256": evidence.workers_free_source_artifact_sha256,
                "provider_model_inference_calls": 0,
                "credential_account_probes": 0,
                "live_network_validation": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
