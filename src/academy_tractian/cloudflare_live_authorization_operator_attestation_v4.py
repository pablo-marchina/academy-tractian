from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
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
    _utc_json,
    canonical_custody_root_sha256,
)
from .cloudflare_provider_comparison_v2 import EXPECTED_PLAN_SHA256
from .cloudflare_provider_live_v2 import CloudflarePreLiveEvidence


AMENDMENT_PROTOCOL_VERSION = "cloudflare-live-authorization-operator-attestation-amendment-v1"
EVIDENCE_VERSION = "cloudflare-live-authorization-operator-attestation-evidence-v1"
RECEIPT_VERSION = "cloudflare-live-authorization-operator-attestation-receipt-v1"
AMENDMENT_PROTOCOL_PATH = (
    "research/experiments/cloudflare-live-authorization-operator-attestation-amendment-v1.json"
)
ADR_021_PATH = "docs/adr/021-cloudflare-live-execution-authorization-protocol-2026-09-01.md"
ADR_022_PATH = "docs/adr/022-cloudflare-reset-window-neuron-evidence-amendment-2026-09-01.md"
ADR_023_PATH = "docs/adr/023-cloudflare-governed-live-entrypoint-contract-2026-09-01.md"
ADR_024_PATH = "docs/adr/024-cloudflare-same-day-zero-use-neuron-evidence-amendment-2026-09-01.md"
ADR_021_GIT_BLOB = "9627219e5b9c64dda83d23e0f3e99f4c9b953519"
ADR_022_GIT_BLOB = "f32bc7e3ca37c74f04fce4cc0dfd56cfab2efcd0"
ADR_023_GIT_BLOB = "b124a02e89f4f604399e6a9a01616c91ceebb491"
ADR_024_GIT_BLOB = "0e03e84027721ab170976b483e81c3d08fb73a00"

DAILY_FREE_NEURONS = 10000.0
MIN_FREE_NEURONS = 9000.0
EVIDENCE_MAX_AGE_SECONDS = 600
RECEIPT_MAX_LIFETIME_SECONDS = 300
CLOCK_SKEW_SECONDS = 30


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareOperatorAttestationEvidenceV1(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-operator-attestation-evidence-v1"] = (
        EVIDENCE_VERSION
    )
    evidence_mode: Literal["OPERATOR_PLAN_STATE_ATTESTATION"] = "OPERATOR_PLAN_STATE_ATTESTATION"
    observed_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    reset_at_utc: datetime
    workers_free_active_attested: Literal[True] = True
    workers_paid_disabled_attested: Literal[True] = True
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
    external_plan_source_artifact_required: Literal[False] = False
    plan_state_evidence_basis: Literal["OPERATOR_ATTESTATION"] = "OPERATOR_ATTESTATION"

    @model_validator(mode="after")
    def validate_same_day(self) -> "CloudflareOperatorAttestationEvidenceV1":
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
        if observed < reset:
            raise ValueError("observation cannot precede current UTC reset")
        return self

    @property
    def canonical_sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class CloudflareOperatorAttestationReceiptV1(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-operator-attestation-receipt-v1"] = (
        RECEIPT_VERSION
    )
    amendment_protocol_version: Literal[
        "cloudflare-live-authorization-operator-attestation-amendment-v1"
    ] = AMENDMENT_PROTOCOL_VERSION
    issued_at_utc: datetime
    expires_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    custody_root_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    adr_021_blob: str = ADR_021_GIT_BLOB
    adr_022_blob: str = ADR_022_GIT_BLOB
    adr_023_blob: str = ADR_023_GIT_BLOB
    adr_024_blob: str = ADR_024_GIT_BLOB
    adr_018_blob: str = ADR_018_GIT_BLOB
    adr_019_blob: str = ADR_019_GIT_BLOB
    adr_020_blob: str = ADR_020_GIT_BLOB
    plan_sha256: str = EXPECTED_PLAN_SHA256
    provider_id: str = CLOUDFLARE_PROVIDER_ID
    route_id: str = CLOUDFLARE_ROUTE_ID
    model_ids: tuple[str, ...] = ALLOWED_MODELS
    evidence_mode: Literal["OPERATOR_PLAN_STATE_ATTESTATION"] = "OPERATOR_PLAN_STATE_ATTESTATION"
    derived_free_neurons_at_issue: Literal[10000.0] = DAILY_FREE_NEURONS
    workers_free_active_attested: Literal[True] = True
    workers_paid_disabled_attested: Literal[True] = True
    no_workers_ai_calls_since_reset_attested: Literal[True] = True
    no_automated_workers_ai_consumers_since_reset_attested: Literal[True] = True
    exclusive_workers_ai_account_window_until_packet_completion_attested: Literal[True] = True
    direct_workers_ai_route: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    external_plan_source_artifact_required: Literal[False] = False
    comparison_attempts_consumed_at_issue: Literal[0] = 0
    provider_inference_calls_at_issue: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    raw_local_custody_path_recorded: Literal[False] = False
    attempt_1_authorized: Literal[True] = True
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_receipt(self) -> "CloudflareOperatorAttestationReceiptV1":
        issued = _as_utc(self.issued_at_utc)
        expires = _as_utc(self.expires_at_utc)
        if expires <= issued:
            raise ValueError("receipt expiry must be after issue time")
        if (expires - issued).total_seconds() > RECEIPT_MAX_LIFETIME_SECONDS:
            raise ValueError("receipt lifetime exceeds 300 seconds")
        if issued.date().isoformat() != self.utc_day or expires.date().isoformat() != self.utc_day:
            raise ValueError("receipt must remain inside one UTC day")
        pins = (
            (self.adr_021_blob, ADR_021_GIT_BLOB, "ADR-021"),
            (self.adr_022_blob, ADR_022_GIT_BLOB, "ADR-022"),
            (self.adr_023_blob, ADR_023_GIT_BLOB, "ADR-023"),
            (self.adr_024_blob, ADR_024_GIT_BLOB, "ADR-024"),
            (self.adr_018_blob, ADR_018_GIT_BLOB, "ADR-018"),
            (self.adr_019_blob, ADR_019_GIT_BLOB, "ADR-019"),
            (self.adr_020_blob, ADR_020_GIT_BLOB, "ADR-020"),
        )
        for actual, expected, label in pins:
            if actual != expected:
                raise ValueError(f"{label} pin drift")
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


def _git_head_blob_sha(root: Path, path: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CloudflareAuthorizationError(f"cannot resolve canonical Git blob for {path}") from exc
    value = completed.stdout.strip().lower()
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value):
        raise CloudflareAuthorizationError(f"invalid Git blob identity for {path}")
    return value


def validate_frozen_operator_attestation_amendment(repo_root: Path | str = ".") -> dict:
    root = Path(repo_root).resolve()
    protocol = json.loads((root / AMENDMENT_PROTOCOL_PATH).read_text(encoding="utf-8"))
    if protocol.get("schema_version") != AMENDMENT_PROTOCOL_VERSION:
        raise CloudflareAuthorizationError("operator-attestation amendment schema drift")

    for path, expected in (
        (ADR_021_PATH, ADR_021_GIT_BLOB),
        (ADR_022_PATH, ADR_022_GIT_BLOB),
        (ADR_023_PATH, ADR_023_GIT_BLOB),
        (ADR_024_PATH, ADR_024_GIT_BLOB),
    ):
        if _git_head_blob_sha(root, path) != expected:
            raise CloudflareAuthorizationError(f"frozen historical blob mismatch: {path}")

    historical = protocol.get("historical_protocol", {})
    required_historical = {
        "adr_021_blob": ADR_021_GIT_BLOB,
        "adr_022_blob": ADR_022_GIT_BLOB,
        "adr_023_blob": ADR_023_GIT_BLOB,
        "adr_024_blob": ADR_024_GIT_BLOB,
        "preserve_adr_021": True,
        "preserve_adr_022": True,
        "preserve_adr_023": True,
        "preserve_adr_024": True,
    }
    for key, value in required_historical.items():
        if historical.get(key) != value:
            raise CloudflareAuthorizationError(f"historical pin drift: {key}")

    evidence_mode = protocol.get("evidence_mode", {})
    required_evidence = {
        "name": "OPERATOR_PLAN_STATE_ATTESTATION",
        "evidence_max_age_seconds": EVIDENCE_MAX_AGE_SECONDS,
        "receipt_max_lifetime_seconds": RECEIPT_MAX_LIFETIME_SECONDS,
        "reset_hour_utc": 0,
        "observation_must_be_same_utc_day_as_reset": True,
        "workers_free_active_attestation_required": True,
        "workers_paid_disabled_attestation_required": True,
        "no_workers_ai_calls_since_reset_required": True,
        "no_automated_workers_ai_consumers_since_reset_required": True,
        "exclusive_workers_ai_account_window_until_packet_completion_required": True,
        "direct_workers_ai_route_required": True,
        "ai_gateway_route_required": False,
        "prepaid_unified_billing_route_required": False,
        "comparison_attempts_consumed_required": 0,
        "provider_inference_used_to_obtain_evidence": False,
        "credential_account_probe_used_to_obtain_evidence": False,
        "external_plan_source_artifact_required": False,
        "derived_free_neurons_at_evidence": DAILY_FREE_NEURONS,
        "minimum_required_free_neurons": MIN_FREE_NEURONS,
    }
    for key, value in required_evidence.items():
        if evidence_mode.get(key) != value:
            raise CloudflareAuthorizationError(f"operator-attestation amendment drift: {key}")

    portability = protocol.get("portability", {})
    if portability != {
        "cli_adds_src_to_sys_path": True,
        "historical_blob_validation_uses_git_object_ids": True,
        "worktree_line_endings_do_not_define_historical_blob_identity": True,
    }:
        raise CloudflareAuthorizationError("operator-attestation portability contract drift")

    boundary = protocol.get("future_execution_boundary", {})
    if boundary != {
        "provider_model_inference_calls_in_this_task": 0,
        "credential_account_probes_in_this_task": 0,
        "live_network_validation_in_this_task": 0,
        "comparison_attempts_consumed": 0,
        "attempt_1_authorized": False,
        "production_provider_selected": False,
    }:
        raise CloudflareAuthorizationError("operator-attestation execution boundary drift")
    return protocol


def validate_operator_attestation_evidence(
    evidence: CloudflareOperatorAttestationEvidenceV1,
    *,
    now_utc: datetime,
) -> None:
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    if now.date().isoformat() != evidence.utc_day:
        raise CloudflareAuthorizationError("operator-attestation evidence is not from current UTC day")
    age = (now - observed).total_seconds()
    if age < -CLOCK_SKEW_SECONDS:
        raise CloudflareAuthorizationError("operator-attestation evidence observation is in the future")
    if age > EVIDENCE_MAX_AGE_SECONDS:
        raise CloudflareAuthorizationError("operator-attestation evidence is stale")


def issue_operator_attestation_receipt(
    evidence: CloudflareOperatorAttestationEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflareOperatorAttestationReceiptV1:
    validate_operator_attestation_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    evidence_expiry = _as_utc(evidence.observed_at_utc) + timedelta(seconds=EVIDENCE_MAX_AGE_SECONDS)
    receipt_expiry = min(evidence_expiry, now + timedelta(seconds=RECEIPT_MAX_LIFETIME_SECONDS))
    if receipt_expiry <= now:
        raise CloudflareAuthorizationError("operator-attestation evidence leaves no receipt lifetime")

    payload = {
        "schema_version": RECEIPT_VERSION,
        "amendment_protocol_version": AMENDMENT_PROTOCOL_VERSION,
        "issued_at_utc": _utc_json(now),
        "expires_at_utc": _utc_json(receipt_expiry),
        "utc_day": evidence.utc_day,
        "evidence_sha256": evidence.canonical_sha256,
        "custody_root_sha256": canonical_custody_root_sha256(custody_root),
        "adr_021_blob": ADR_021_GIT_BLOB,
        "adr_022_blob": ADR_022_GIT_BLOB,
        "adr_023_blob": ADR_023_GIT_BLOB,
        "adr_024_blob": ADR_024_GIT_BLOB,
        "adr_018_blob": ADR_018_GIT_BLOB,
        "adr_019_blob": ADR_019_GIT_BLOB,
        "adr_020_blob": ADR_020_GIT_BLOB,
        "plan_sha256": EXPECTED_PLAN_SHA256,
        "provider_id": CLOUDFLARE_PROVIDER_ID,
        "route_id": CLOUDFLARE_ROUTE_ID,
        "model_ids": list(ALLOWED_MODELS),
        "evidence_mode": "OPERATOR_PLAN_STATE_ATTESTATION",
        "derived_free_neurons_at_issue": DAILY_FREE_NEURONS,
        "workers_free_active_attested": True,
        "workers_paid_disabled_attested": True,
        "no_workers_ai_calls_since_reset_attested": True,
        "no_automated_workers_ai_consumers_since_reset_attested": True,
        "exclusive_workers_ai_account_window_until_packet_completion_attested": True,
        "direct_workers_ai_route": True,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "external_plan_source_artifact_required": False,
        "comparison_attempts_consumed_at_issue": 0,
        "provider_inference_calls_at_issue": 0,
        "credentials_recorded": False,
        "account_identifier_recorded": False,
        "raw_local_custody_path_recorded": False,
        "attempt_1_authorized": True,
    }
    return CloudflareOperatorAttestationReceiptV1(
        **payload,
        receipt_sha256=_canonical_sha256(payload),
    )


def validate_operator_attestation_receipt_for_execution(
    receipt: CloudflareOperatorAttestationReceiptV1,
    evidence: CloudflareOperatorAttestationEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> None:
    validate_operator_attestation_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    if now > _as_utc(receipt.expires_at_utc):
        raise CloudflareAuthorizationError("operator-attestation authorization receipt expired")
    if receipt.evidence_sha256 != evidence.canonical_sha256:
        raise CloudflareAuthorizationError("operator-attestation evidence hash mismatch")
    if receipt.custody_root_sha256 != canonical_custody_root_sha256(custody_root):
        raise CloudflareAuthorizationError("operator-attestation custody root mismatch")
    if receipt.utc_day != evidence.utc_day or receipt.utc_day != now.date().isoformat():
        raise CloudflareAuthorizationError("operator-attestation UTC day mismatch")


def operator_attestation_to_adr020_pre_live_evidence(
    receipt: CloudflareOperatorAttestationReceiptV1,
    evidence: CloudflareOperatorAttestationEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflarePreLiveEvidence:
    validate_operator_attestation_receipt_for_execution(
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
        evidence_source=f"ADR-025 operator attestation receipt {receipt.receipt_sha256}",
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
    )
