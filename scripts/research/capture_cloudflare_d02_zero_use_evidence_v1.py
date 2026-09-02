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
    validate_frozen_d02_live_authorization,
)
from academy_tractian.cloudflare_reset_window_capture_v1 import (  # noqa: E402
    ResetWindowCaptureError,
    ensure_provider_credentials_absent,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Capture provider-free D02 fresh-reset zero-use evidence. "
            "This command performs no provider inference, credential probe or live validation."
        )
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--attest-workers-free-active", action="store_true")
    parser.add_argument("--attest-workers-paid-disabled", action="store_true")
    parser.add_argument("--attest-no-workers-ai-calls-since-reset", action="store_true")
    parser.add_argument("--attest-no-automated-workers-ai-consumers-since-reset", action="store_true")
    parser.add_argument(
        "--attest-exclusive-workers-ai-window-until-packet-completion",
        action="store_true",
    )
    parser.add_argument("--attest-direct-workers-ai-route", action="store_true")
    parser.add_argument("--attest-no-ai-gateway-or-prepaid-unified-billing", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    required = {
        "workers_free_active": args.attest_workers_free_active,
        "workers_paid_disabled": args.attest_workers_paid_disabled,
        "no_workers_ai_calls_since_reset": args.attest_no_workers_ai_calls_since_reset,
        "no_automated_workers_ai_consumers_since_reset": (
            args.attest_no_automated_workers_ai_consumers_since_reset
        ),
        "exclusive_workers_ai_window_until_packet_completion": (
            args.attest_exclusive_workers_ai_window_until_packet_completion
        ),
        "direct_workers_ai_route": args.attest_direct_workers_ai_route,
        "no_ai_gateway_or_prepaid_unified_billing": (
            args.attest_no_ai_gateway_or_prepaid_unified_billing
        ),
    }
    missing = sorted(name for name, value in required.items() if not value)
    if missing:
        raise SystemExit("all D02 zero-use attestations must be explicitly true: " + ",".join(missing))

    try:
        ensure_provider_credentials_absent()
        validate_frozen_d02_live_authorization(REPO_ROOT)
        observed = datetime.now(timezone.utc)
        reset = observed.replace(hour=0, minute=0, second=0, microsecond=0)
        evidence = CloudflareD02ZeroUseEvidenceV1(
            observed_at_utc=observed,
            utc_day=observed.date().isoformat(),
            reset_at_utc=reset,
            workers_free_active_attested=True,
            workers_paid_disabled_attested=True,
            no_workers_ai_calls_since_reset_attested=True,
            no_automated_workers_ai_consumers_since_reset_attested=True,
            exclusive_workers_ai_account_window_until_packet_completion_attested=True,
            direct_workers_ai_route=True,
            ai_gateway_route_used=False,
            prepaid_unified_billing_route_used=False,
            comparison_attempts_consumed=0,
            inference_used_to_obtain_evidence=False,
            credential_account_probe_used=False,
            account_identifier_recorded=False,
            secret_recorded=False,
            external_plan_source_artifact_required=False,
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
        raise SystemExit("D02 evidence output already exists") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    print(
        json.dumps(
            {
                "status": "D02_ZERO_USE_EVIDENCE_CAPTURED_PROVIDER_FREE",
                "observed_at_utc": evidence.observed_at_utc.isoformat(),
                "reset_at_utc": evidence.reset_at_utc.isoformat(),
                "utc_day": evidence.utc_day,
                "derived_free_neurons_remaining": 10000.0,
                "d02_worst_case_packet_neurons": 9352.805376,
                "provider_model_inference_calls": 0,
                "credential_account_probes": 0,
                "live_network_validation": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
