from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cloudflare_live_authorization_v1 import (
    ADR_018_GIT_BLOB,
    ADR_019_GIT_BLOB,
    ADR_020_GIT_BLOB,
    ALLOWED_MODELS,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareAuthorizationError,
    _as_utc,
    _canonical_sha256,
    _git_blob_sha1,
    _utc_json,
    canonical_custody_root_sha256,
)
from .cloudflare_provider_comparison_v2 import EXPECTED_PLAN_SHA256
from .cloudflare_provider_live_v2 import CloudflarePreLiveEvidence


AMENDMENT_PROTOCOL_VERSION = "cloudflare-live-authorization-reset-window-amendment-v1"
RESET_EVIDENCE_VERSION = "cloudflare-live-authorization-reset-window-evidence-v1"
RESET_RECEIPT_VERSION = "cloudflare-live-authorization-reset-window-receipt-v1"
AMENDMENT_PROTOCOL_PATH = (
    "research/experiments/cloudflare-live-authorization-reset-window-amendment-v1.json"
)
ADR_021_PATH = "docs/adr/021-cloudflare-live-execution-authorization-protocol-2026-09-01.md"
ADR_021_GIT_BLOB = "9627219e5b9c64dda83d23e0f3e99f4c9b953519"

DAILY_FREE_NEURONS = 10000.0
MIN_FREE_NEURONS = 9000.0
RESET_CAPTURE_MAX_OFFSET_SECONDS = 600
EVIDENCE_MAX_AGE_SECONDS = 600
RECEIPT_MAX_LIFETIME_SECONDS = 300
CLOCK_SKEW_SECONDS = 30


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareResetWindowEvidenceV1(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-reset-window-evidence-v1"] = (
        RESET_EVIDENCE_VERSION
    )
    evidence_mode: Literal["RESET_WINDOW_ATTESTATION"] = "RESET_WINDOW_ATTESTATION"
    observed_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    reset_at_utc: datetime
    workers_plan: Literal["Workers Free"] = "Workers Free"
    workers_paid_enabled: Literal[False] = False
    free_allocation_neurons: Literal[10000.0] = DAILY_FREE_NEURONS
    derived_free_neurons_remaining: Literal[10000.0] = DAILY_FREE_NEURONS
    no_workers_ai_calls_since_reset_attested: Literal[True] = True
    no_automated_workers_ai_consumers_since_reset_attested: Literal[True] = True
    exclusive_workers_ai_account_window_until_packet_completion_attested: Literal[True] = True
    direct_workers_ai_route: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    gateway_header_present: Literal[False] = False
    comparison_attempts_consumed: Literal[0] = 0
    inference_used_to_obtain_evidence: Literal[False] = False
    credential_account_probe_used: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False
    workers_free_source_artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_artifact_retained_outside_repo: Literal[True] = True

    @model_validator(mode="after")
    def validate_reset_window(self) -> "CloudflareResetWindowEvidenceV1":
        observed = _as_utc(self.observed_at_utc)
        reset = _as_utc(self.reset_at_utc)
        expected_reset = datetime(
            observed.year,
            observed.month,
            observed.day,
            0,
            0,
            0,
            tzinfo=timezone.utc,
        )
        if observed.date().isoformat() != self.utc_day:
            raise ValueError("utc_day must match observed_at_utc UTC date")
        if reset != expected_reset:
            raise ValueError("reset_at_utc must be exactly 00:00:00 UTC on utc_day")
        offset = (observed - reset).total_seconds()
        if offset < 0 or offset > RESET_CAPTURE_MAX_OFFSET_SECONDS:
            raise ValueError("reset-window observation must occur within 600 seconds after 00:00 UTC")
        return self

    @property
    def canonical_sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class CloudflareResetWindowReceiptV1(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-reset-window-receipt-v1"] = (
        RESET_RECEIPT_VERSION
    )
    amendment_protocol_version: Literal[
        "cloudflare-live-authorization-reset-window-amendment-v1"
    ] = AMENDMENT_PROTOCOL_VERSION
    issued_at_utc: datetime
    expires_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    custody_root_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    adr_021_blob: str = ADR_021_GIT_BLOB
    adr_018_blob: str = ADR_018_GIT_BLOB
    adr_019_blob: str = ADR_019_GIT_BLOB
    adr_020_blob: str = ADR_020_GIT_BLOB
    plan_sha256: str = EXPECTED_PLAN_SHA256
    provider_id: str = CLOUDFLARE_PROVIDER_ID
    route_id: str = CLOUDFLARE_ROUTE_ID
    model_ids: tuple[str, ...] = ALLOWED_MODELS
    evidence_mode: Literal["RESET_WINDOW_ATTESTATION"] = "RESET_WINDOW_ATTESTATION"
    derived_free_neurons_at_issue: Literal[10000.0] = DAILY_FREE_NEURONS
    workers_free_required: Literal[True] = True
    workers_paid_enabled: Literal[False] = False
    no_workers_ai_calls_since_reset_attested: Literal[True] = True
    no_automated_workers_ai_consumers_since_reset_attested: Literal[True] = True
    exclusive_workers_ai_account_window_until_packet_completion_attested: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    comparison_attempts_consumed_at_issue: Literal[0] = 0
    provider_inference_calls_at_issue: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    raw_local_custody_path_recorded: Literal[False] = False
    attempt_1_authorized: Literal[True] = True
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_receipt(self) -> "CloudflareResetWindowReceiptV1":
        issued = _as_utc(self.issued_at_utc)
        expires = _as_utc(self.expires_at_utc)
        if expires <= issued:
            raise ValueError("receipt expiry must be after issue time")
        if (expires - issued).total_seconds() > RECEIPT_MAX_LIFETIME_SECONDS:
            raise ValueError("receipt lifetime exceeds 300 seconds")
        if issued.date().isoformat() != self.utc_day or expires.date().isoformat() != self.utc_day:
            raise ValueError("receipt must remain inside one UTC day")
        if self.adr_021_blob != ADR_021_GIT_BLOB:
            raise ValueError("ADR-021 pin drift")
        if self.adr_018_blob != ADR_018_GIT_BLOB or self.adr_019_blob != ADR_019_GIT_BLOB:
            raise ValueError("historical provider pin drift")
        if self.adr_020_blob != ADR_020_GIT_BLOB:
            raise ValueError("ADR-020 pin drift")
        if self.plan_sha256 != EXPECTED_PLAN_SHA256:
            raise ValueError("plan pin drift")
        if self.provider_id != CLOUDFLARE_PROVIDER_ID or self.route_id != CLOUDFLARE_ROUTE_ID:
            raise ValueError("provider/route drift")
        if tuple(self.model_ids) != ALLOWED_MODELS:
            raise ValueError("model identity drift")
        payload = self.model_dump(mode="json", exclude={"receipt_sha256"})
        if self.receipt_sha256 != _canonical_sha256(payload):
            raise ValueError("receipt_sha256 mismatch")
        return self


def validate_frozen_reset_window_amendment(repo_root: Path | str = ".") -> dict:
    root = Path(repo_root)
    protocol = json.loads((root / AMENDMENT_PROTOCOL_PATH).read_text(encoding="utf-8"))
    if protocol.get("schema_version") != AMENDMENT_PROTOCOL_VERSION:
        raise CloudflareAuthorizationError("reset-window amendment schema drift")
    if _git_blob_sha1((root / ADR_021_PATH).read_bytes()) != ADR_021_GIT_BLOB:
        raise CloudflareAuthorizationError("ADR-021 historical blob mismatch")
    historical = protocol.get("historical_protocol", {})
    if historical.get("adr_021_blob") != ADR_021_GIT_BLOB:
        raise CloudflareAuthorizationError("ADR-021 amendment pin drift")
    if historical.get("preserve_original_dashboard_balance_path") is not True:
        raise CloudflareAuthorizationError("historical dashboard-balance path must be preserved")
    fallback = protocol.get("fallback_mode", {})
    required = {
        "name": "RESET_WINDOW_ATTESTATION",
        "reset_capture_max_offset_seconds": RESET_CAPTURE_MAX_OFFSET_SECONDS,
        "evidence_max_age_seconds": EVIDENCE_MAX_AGE_SECONDS,
        "receipt_max_lifetime_seconds": RECEIPT_MAX_LIFETIME_SECONDS,
        "derived_free_neurons_at_evidence": DAILY_FREE_NEURONS,
        "minimum_required_free_neurons": MIN_FREE_NEURONS,
        "workers_plan_required": "Workers Free",
        "workers_paid_enabled_required": False,
        "no_workers_ai_calls_since_reset_required": True,
        "no_automated_workers_ai_consumers_since_reset_required": True,
        "exclusive_workers_ai_account_window_until_packet_completion_required": True,
        "direct_workers_ai_route_required": True,
        "ai_gateway_route_required": False,
        "prepaid_unified_billing_route_required": False,
        "comparison_attempts_consumed_required": 0,
        "provider_inference_used_to_obtain_evidence": False,
        "credential_account_probe_used_to_obtain_evidence": False,
    }
    for key, value in required.items():
        if fallback.get(key) != value:
            raise CloudflareAuthorizationError(f"reset-window amendment drift: {key}")
    boundary = protocol.get("future_execution_boundary", {})
    if boundary.get("provider_model_inference_calls_in_this_task") != 0:
        raise CloudflareAuthorizationError("provider inference boundary drift")
    if boundary.get("credential_account_probes_in_this_task") != 0:
        raise CloudflareAuthorizationError("credential probe boundary drift")
    if boundary.get("live_network_validation_in_this_task") != 0:
        raise CloudflareAuthorizationError("live network boundary drift")
    if boundary.get("attempt_1_authorized") is not False:
        raise CloudflareAuthorizationError("attempt 1 must remain unauthorized")
    return protocol


def validate_reset_window_evidence(
    evidence: CloudflareResetWindowEvidenceV1,
    *,
    now_utc: datetime,
) -> None:
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    if now.date().isoformat() != evidence.utc_day:
        raise CloudflareAuthorizationError("reset-window evidence is not from current UTC day")
    age = (now - observed).total_seconds()
    if age < -CLOCK_SKEW_SECONDS:
        raise CloudflareAuthorizationError("reset-window evidence observation is in the future")
    if age > EVIDENCE_MAX_AGE_SECONDS:
        raise CloudflareAuthorizationError("reset-window evidence is stale")


def issue_reset_window_receipt(
    evidence: CloudflareResetWindowEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflareResetWindowReceiptV1:
    validate_reset_window_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    evidence_expiry = observed + timedelta(seconds=EVIDENCE_MAX_AGE_SECONDS)
    receipt_expiry = min(evidence_expiry, now + timedelta(seconds=RECEIPT_MAX_LIFETIME_SECONDS))
    if receipt_expiry <= now:
        raise CloudflareAuthorizationError("reset-window evidence leaves no receipt lifetime")

    payload = {
        "schema_version": RESET_RECEIPT_VERSION,
        "amendment_protocol_version": AMENDMENT_PROTOCOL_VERSION,
        "issued_at_utc": _utc_json(now),
        "expires_at_utc": _utc_json(receipt_expiry),
        "utc_day": evidence.utc_day,
        "evidence_sha256": evidence.canonical_sha256,
        "custody_root_sha256": canonical_custody_root_sha256(custody_root),
        "adr_021_blob": ADR_021_GIT_BLOB,
        "adr_018_blob": ADR_018_GIT_BLOB,
        "adr_019_blob": ADR_019_GIT_BLOB,
        "adr_020_blob": ADR_020_GIT_BLOB,
        "plan_sha256": EXPECTED_PLAN_SHA256,
        "provider_id": CLOUDFLARE_PROVIDER_ID,
        "route_id": CLOUDFLARE_ROUTE_ID,
        "model_ids": list(ALLOWED_MODELS),
        "evidence_mode": "RESET_WINDOW_ATTESTATION",
        "derived_free_neurons_at_issue": DAILY_FREE_NEURONS,
        "workers_free_required": True,
        "workers_paid_enabled": False,
        "no_workers_ai_calls_since_reset_attested": True,
        "no_automated_workers_ai_consumers_since_reset_attested": True,
        "exclusive_workers_ai_account_window_until_packet_completion_attested": True,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "comparison_attempts_consumed_at_issue": 0,
        "provider_inference_calls_at_issue": 0,
        "credentials_recorded": False,
        "account_identifier_recorded": False,
        "raw_local_custody_path_recorded": False,
        "attempt_1_authorized": True,
    }
    return CloudflareResetWindowReceiptV1(
        **payload,
        receipt_sha256=_canonical_sha256(payload),
    )


def validate_reset_window_receipt_for_execution(
    receipt: CloudflareResetWindowReceiptV1,
    evidence: CloudflareResetWindowEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> None:
    validate_reset_window_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    if now > _as_utc(receipt.expires_at_utc):
        raise CloudflareAuthorizationError("reset-window authorization receipt expired")
    if receipt.evidence_sha256 != evidence.canonical_sha256:
        raise CloudflareAuthorizationError("reset-window evidence hash mismatch")
    if receipt.custody_root_sha256 != canonical_custody_root_sha256(custody_root):
        raise CloudflareAuthorizationError("reset-window custody root mismatch")
    if receipt.utc_day != evidence.utc_day or receipt.utc_day != now.date().isoformat():
        raise CloudflareAuthorizationError("reset-window UTC day mismatch")


def reset_window_authorization_to_adr020_pre_live_evidence(
    receipt: CloudflareResetWindowReceiptV1,
    evidence: CloudflareResetWindowEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflarePreLiveEvidence:
    validate_reset_window_receipt_for_execution(
        receipt,
        evidence,
        custody_root=custody_root,
        now_utc=now_utc,
    )
    return CloudflarePreLiveEvidence(
        workers_plan="Workers Free",
        workers_paid_enabled=False,
        prepaid_ai_gateway_enabled=False,
        direct_workers_ai_route=True,
        actual_cash_cost_usd=0.0,
        free_neurons_remaining=DAILY_FREE_NEURONS,
        utc_day=evidence.utc_day,
        evidence_source=f"ADR-022 reset-window receipt {receipt.receipt_sha256}",
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
    )
