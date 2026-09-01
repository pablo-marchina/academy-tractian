from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import os
from pathlib import Path

from .cloudflare_live_authorization_reset_v2 import CloudflareResetWindowEvidenceV1


FORBIDDEN_PROVIDER_ENV = (
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
)


class ResetWindowCaptureError(RuntimeError):
    pass


def ensure_provider_credentials_absent(environ: dict[str, str] | None = None) -> None:
    env = os.environ if environ is None else environ
    present = [name for name in FORBIDDEN_PROVIDER_ENV if env.get(name)]
    if present:
        raise ResetWindowCaptureError(
            "reset-window evidence must be captured before provider secrets are provisioned: "
            + ",".join(present)
        )


def sha256_file(path: Path | str) -> str:
    source = Path(path)
    if not source.is_file():
        raise ResetWindowCaptureError("Workers Free source artifact must be an existing file")
    digest = sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_reset_window_evidence(
    *,
    workers_free_source_artifact: Path | str,
    now_utc: datetime,
    attest_workers_free_active: bool,
    attest_workers_paid_disabled: bool,
    attest_no_workers_ai_calls_since_reset: bool,
    attest_no_automated_workers_ai_consumers_since_reset: bool,
    attest_exclusive_workers_ai_window_until_packet_completion: bool,
    attest_direct_workers_ai_route: bool,
    attest_no_ai_gateway_or_prepaid_unified_billing: bool,
) -> CloudflareResetWindowEvidenceV1:
    required = {
        "workers_free_active": attest_workers_free_active,
        "workers_paid_disabled": attest_workers_paid_disabled,
        "no_workers_ai_calls_since_reset": attest_no_workers_ai_calls_since_reset,
        "no_automated_workers_ai_consumers_since_reset": (
            attest_no_automated_workers_ai_consumers_since_reset
        ),
        "exclusive_workers_ai_window_until_packet_completion": (
            attest_exclusive_workers_ai_window_until_packet_completion
        ),
        "direct_workers_ai_route": attest_direct_workers_ai_route,
        "no_ai_gateway_or_prepaid_unified_billing": (
            attest_no_ai_gateway_or_prepaid_unified_billing
        ),
    }
    missing = sorted(name for name, value in required.items() if not value)
    if missing:
        raise ResetWindowCaptureError(
            "all ADR-022 attestations must be explicitly true: " + ",".join(missing)
        )

    if now_utc.tzinfo is None or now_utc.utcoffset() is None:
        raise ResetWindowCaptureError("capture clock must be timezone-aware")
    observed = now_utc.astimezone(timezone.utc)
    reset = observed.replace(hour=0, minute=0, second=0, microsecond=0)

    return CloudflareResetWindowEvidenceV1(
        observed_at_utc=observed,
        utc_day=observed.date().isoformat(),
        reset_at_utc=reset,
        workers_plan="Workers Free",
        workers_paid_enabled=False,
        free_allocation_neurons=10000.0,
        derived_free_neurons_remaining=10000.0,
        no_workers_ai_calls_since_reset_attested=True,
        no_automated_workers_ai_consumers_since_reset_attested=True,
        exclusive_workers_ai_account_window_until_packet_completion_attested=True,
        direct_workers_ai_route=True,
        ai_gateway_route_used=False,
        prepaid_unified_billing_route_used=False,
        gateway_header_present=False,
        comparison_attempts_consumed=0,
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
        account_identifier_recorded=False,
        secret_recorded=False,
        workers_free_source_artifact_sha256=sha256_file(workers_free_source_artifact),
        source_artifact_retained_outside_repo=True,
    )
