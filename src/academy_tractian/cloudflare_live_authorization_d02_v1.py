from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cloudflare_live_authorization_v1 import (
    ALLOWED_MODELS,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareAuthorizationError,
    _as_utc,
    _canonical_sha256,
    _utc_json,
    canonical_custody_root_sha256,
)
from .cloudflare_provider_d02 import (
    CLOUDFLARE_D02_EXPECTED_PLAN_SHA256,
    CLOUDFLARE_D02_MAX_PACKET_NEURONS,
    CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
    CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS,
    CloudflareD02PreLiveEvidence,
)


D02_AUTH_PROTOCOL_VERSION = "cloudflare-d02-live-authorization-protocol-v1"
D02_EVIDENCE_VERSION = "cloudflare-d02-operator-attestation-evidence-v1"
D02_RECEIPT_VERSION = "cloudflare-d02-operator-attestation-receipt-v1"
D02_AUTH_PROTOCOL_PATH = "research/experiments/cloudflare-d02-live-authorization-protocol-v1.json"
D02_AUTH_PROTOCOL_BLOB = "fc1dab851a047c4ebf7393e2bd70854ce7f6d4c9"
ADR_027_PATH = "docs/adr/027-cloudflare-d02-governed-live-authorization-2026-09-02.md"
ADR_027_BLOB = "40dac521503779427db5272421766e4290745124"
D02_COMPLETION_PROTOCOL_PATH = "research/experiments/cloudflare-d02-completion-budget-protocol-v1.json"
D02_COMPLETION_PROTOCOL_BLOB = "eda022821c4ffe08b28b80b814d0da28f84580f6"
ADR_026_PATH = "docs/adr/026-cloudflare-d02-completion-budget-amendment-2026-09-02.md"
ADR_026_BLOB = "c5d00a1668613cacd3b520cd241a8b969a262119"
D02_CONTRACT_PATH = "src/academy_tractian/cloudflare_provider_d02.py"
D02_CONTRACT_BLOB = "c6cc416c4201a30961861c852aaa746e6c5c9113"
D02_LIVE_CORE_PATH = "src/academy_tractian/cloudflare_provider_d02_live.py"
D02_LIVE_CORE_BLOB = "9da20694e4a1d0129b6e8fa9107b9e6f2d0f3fe2"

DAILY_FREE_NEURONS = CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS
EVIDENCE_MAX_AGE_SECONDS = 600
RECEIPT_MAX_LIFETIME_SECONDS = 300
CLOCK_SKEW_SECONDS = 30
D01_CONSUMED_UTC_DAY = "2026-09-02"
D01_OBSERVED_NEURONS = 2813.628464
D01_MAXIMUM_IMPLIED_REMAINING = DAILY_FREE_NEURONS - D01_OBSERVED_NEURONS


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareD02OperatorAttestationEvidenceV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-operator-attestation-evidence-v1"] = D02_EVIDENCE_VERSION
    evidence_mode: Literal["OPERATOR_ZERO_USE_AFTER_UTC_RESET"] = "OPERATOR_ZERO_USE_AFTER_UTC_RESET"
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
    d02_attempts_consumed: Literal[0] = 0
    inference_used_to_obtain_evidence: Literal[False] = False
    credential_account_probe_used: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False
    external_plan_source_artifact_required: Literal[False] = False
    plan_state_evidence_basis: Literal["OPERATOR_ATTESTATION"] = "OPERATOR_ATTESTATION"

    @model_validator(mode="after")
    def validate_reset_window(self) -> "CloudflareD02OperatorAttestationEvidenceV1":
        observed = _as_utc(self.observed_at_utc)
        reset = _as_utc(self.reset_at_utc)
        expected_reset = datetime(observed.year, observed.month, observed.day, 0, 0, 0, tzinfo=timezone.utc)
        if observed.date().isoformat() != self.utc_day:
            raise ValueError("D02 utc_day must match observed_at_utc UTC date")
        if reset != expected_reset:
            raise ValueError("D02 reset_at_utc must be exactly 00:00:00 UTC on utc_day")
        if observed < reset:
            raise ValueError("D02 evidence observation cannot precede reset")
        if self.utc_day == D01_CONSUMED_UTC_DAY:
            raise ValueError("D02 is blocked on 2026-09-02 UTC because D01 already consumed Workers AI allocation")
        return self

    @property
    def canonical_sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class CloudflareD02OperatorAttestationReceiptV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-operator-attestation-receipt-v1"] = D02_RECEIPT_VERSION
    authorization_protocol_version: Literal["cloudflare-d02-live-authorization-protocol-v1"] = D02_AUTH_PROTOCOL_VERSION
    issued_at_utc: datetime
    expires_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    custody_root_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authorization_protocol_blob: Literal["fc1dab851a047c4ebf7393e2bd70854ce7f6d4c9"] = D02_AUTH_PROTOCOL_BLOB
    adr_027_blob: Literal["40dac521503779427db5272421766e4290745124"] = ADR_027_BLOB
    d02_completion_protocol_blob: Literal["eda022821c4ffe08b28b80b814d0da28f84580f6"] = D02_COMPLETION_PROTOCOL_BLOB
    adr_026_blob: Literal["c5d00a1668613cacd3b520cd241a8b969a262119"] = ADR_026_BLOB
    d02_contract_blob: Literal["c6cc416c4201a30961861c852aaa746e6c5c9113"] = D02_CONTRACT_BLOB
    d02_live_core_blob: Literal["9da20694e4a1d0129b6e8fa9107b9e6f2d0f3fe2"] = D02_LIVE_CORE_BLOB
    plan_sha256: Literal["e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    provider_id: str = CLOUDFLARE_PROVIDER_ID
    route_id: str = CLOUDFLARE_ROUTE_ID
    model_ids: tuple[str, ...] = ALLOWED_MODELS
    evidence_mode: Literal["OPERATOR_ZERO_USE_AFTER_UTC_RESET"] = "OPERATOR_ZERO_USE_AFTER_UTC_RESET"
    derived_free_neurons_at_issue: Literal[10000.0] = DAILY_FREE_NEURONS
    maximum_packet_neurons: Literal[9352.805376] = 9352.805376
    minimum_free_neurons_before_attempt_1: Literal[9352.805376] = 9352.805376
    workers_free_active_attested: Literal[True] = True
    workers_paid_disabled_attested: Literal[True] = True
    no_workers_ai_calls_since_reset_attested: Literal[True] = True
    no_automated_workers_ai_consumers_since_reset_attested: Literal[True] = True
    exclusive_workers_ai_account_window_until_packet_completion_attested: Literal[True] = True
    direct_workers_ai_route: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    external_plan_source_artifact_required: Literal[False] = False
    d02_attempts_consumed_at_issue: Literal[0] = 0
    provider_inference_calls_at_issue: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    raw_local_custody_path_recorded: Literal[False] = False
    attempt_1_authorized: Literal[True] = True
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_receipt(self) -> "CloudflareD02OperatorAttestationReceiptV1":
        issued = _as_utc(self.issued_at_utc)
        expires = _as_utc(self.expires_at_utc)
        if expires <= issued:
            raise ValueError("D02 receipt expiry must be after issue time")
        if (expires - issued).total_seconds() > RECEIPT_MAX_LIFETIME_SECONDS:
            raise ValueError("D02 receipt lifetime exceeds 300 seconds")
        if issued.date().isoformat() != self.utc_day or expires.date().isoformat() != self.utc_day:
            raise ValueError("D02 receipt must remain inside one UTC day")
        if self.utc_day == D01_CONSUMED_UTC_DAY:
            raise ValueError("D02 receipt cannot authorize the D01-consumed UTC day")
        if tuple(self.model_ids) != ALLOWED_MODELS:
            raise ValueError("D02 model identity drift")
        payload = self.model_dump(mode="json", exclude={"receipt_sha256"})
        if self.receipt_sha256 != _canonical_sha256(payload):
            raise ValueError("D02 receipt_sha256 mismatch")
        return self


def _git_head_blob_sha(root: Path, path: str) -> str:
    try:
        completed = subprocess.run(["git", "rev-parse", f"HEAD:{path}"], cwd=root, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CloudflareAuthorizationError(f"cannot resolve canonical D02 Git blob for {path}") from exc
    value = completed.stdout.strip().lower()
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value):
        raise CloudflareAuthorizationError(f"invalid D02 Git blob identity for {path}")
    return value


def validate_frozen_d02_live_authorization(repo_root: Path | str = ".") -> dict:
    root = Path(repo_root).resolve()
    for path, expected in (
        (D02_AUTH_PROTOCOL_PATH, D02_AUTH_PROTOCOL_BLOB),
        (ADR_027_PATH, ADR_027_BLOB),
        (D02_COMPLETION_PROTOCOL_PATH, D02_COMPLETION_PROTOCOL_BLOB),
        (ADR_026_PATH, ADR_026_BLOB),
        (D02_CONTRACT_PATH, D02_CONTRACT_BLOB),
        (D02_LIVE_CORE_PATH, D02_LIVE_CORE_BLOB),
    ):
        if _git_head_blob_sha(root, path) != expected:
            raise CloudflareAuthorizationError(f"frozen D02 blob mismatch: {path}")
    protocol = json.loads((root / D02_AUTH_PROTOCOL_PATH).read_text(encoding="utf-8"))
    if protocol.get("schema_version") != D02_AUTH_PROTOCOL_VERSION:
        raise CloudflareAuthorizationError("D02 authorization protocol schema drift")
    packet = protocol.get("packet", {})
    if packet.get("attempts") != 32 or packet.get("completion_token_cap") != 1024 or packet.get("maximum_packet_neurons") != CLOUDFLARE_D02_MAX_PACKET_NEURONS or packet.get("minimum_free_neurons_before_attempt_1") != CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1 or packet.get("paid_spillover_allowed") is not False or packet.get("hard_usd_budget") != 0.0 or packet.get("automatic_retries") != 0 or packet.get("provider_fallbacks") != 0 or packet.get("parallel_live_calls") is not False:
        raise CloudflareAuthorizationError("D02 authorization packet drift")
    current = protocol.get("current_window", {})
    if current.get("utc_day") != D01_CONSUMED_UTC_DAY or current.get("d01_observed_neurons_consumed") != D01_OBSERVED_NEURONS or current.get("maximum_remaining_neurons_from_d01_accounting") != D01_MAXIMUM_IMPLIED_REMAINING or current.get("d02_live_eligible_in_this_window") is not False:
        raise CloudflareAuthorizationError("D02 current-window block drift")
    return protocol


def validate_d02_operator_attestation_evidence(evidence: CloudflareD02OperatorAttestationEvidenceV1, *, now_utc: datetime) -> None:
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    if now.date().isoformat() != evidence.utc_day:
        raise CloudflareAuthorizationError("D02 evidence is not from current UTC day")
    if evidence.utc_day == D01_CONSUMED_UTC_DAY:
        raise CloudflareAuthorizationError("D02 current UTC allocation window is blocked by D01 usage")
    age = (now - observed).total_seconds()
    if age < -CLOCK_SKEW_SECONDS:
        raise CloudflareAuthorizationError("D02 evidence observation is in the future")
    if age > EVIDENCE_MAX_AGE_SECONDS:
        raise CloudflareAuthorizationError("D02 operator-attestation evidence is stale")


def issue_d02_operator_attestation_receipt(evidence: CloudflareD02OperatorAttestationEvidenceV1, *, custody_root: Path | str, now_utc: datetime) -> CloudflareD02OperatorAttestationReceiptV1:
    validate_d02_operator_attestation_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    evidence_expiry = _as_utc(evidence.observed_at_utc) + timedelta(seconds=EVIDENCE_MAX_AGE_SECONDS)
    receipt_expiry = min(evidence_expiry, now + timedelta(seconds=RECEIPT_MAX_LIFETIME_SECONDS))
    if receipt_expiry <= now:
        raise CloudflareAuthorizationError("D02 evidence leaves no receipt lifetime")
    payload = {
        "schema_version": D02_RECEIPT_VERSION,
        "authorization_protocol_version": D02_AUTH_PROTOCOL_VERSION,
        "issued_at_utc": _utc_json(now),
        "expires_at_utc": _utc_json(receipt_expiry),
        "utc_day": evidence.utc_day,
        "evidence_sha256": evidence.canonical_sha256,
        "custody_root_sha256": canonical_custody_root_sha256(custody_root),
        "authorization_protocol_blob": D02_AUTH_PROTOCOL_BLOB,
        "adr_027_blob": ADR_027_BLOB,
        "d02_completion_protocol_blob": D02_COMPLETION_PROTOCOL_BLOB,
        "adr_026_blob": ADR_026_BLOB,
        "d02_contract_blob": D02_CONTRACT_BLOB,
        "d02_live_core_blob": D02_LIVE_CORE_BLOB,
        "plan_sha256": CLOUDFLARE_D02_EXPECTED_PLAN_SHA256,
        "provider_id": CLOUDFLARE_PROVIDER_ID,
        "route_id": CLOUDFLARE_ROUTE_ID,
        "model_ids": list(ALLOWED_MODELS),
        "evidence_mode": "OPERATOR_ZERO_USE_AFTER_UTC_RESET",
        "derived_free_neurons_at_issue": DAILY_FREE_NEURONS,
        "maximum_packet_neurons": CLOUDFLARE_D02_MAX_PACKET_NEURONS,
        "minimum_free_neurons_before_attempt_1": CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
        "workers_free_active_attested": True,
        "workers_paid_disabled_attested": True,
        "no_workers_ai_calls_since_reset_attested": True,
        "no_automated_workers_ai_consumers_since_reset_attested": True,
        "exclusive_workers_ai_account_window_until_packet_completion_attested": True,
        "direct_workers_ai_route": True,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "external_plan_source_artifact_required": False,
        "d02_attempts_consumed_at_issue": 0,
        "provider_inference_calls_at_issue": 0,
        "credentials_recorded": False,
        "account_identifier_recorded": False,
        "raw_local_custody_path_recorded": False,
        "attempt_1_authorized": True,
    }
    return CloudflareD02OperatorAttestationReceiptV1(**payload, receipt_sha256=_canonical_sha256(payload))


def validate_d02_operator_attestation_receipt_for_execution(receipt: CloudflareD02OperatorAttestationReceiptV1, evidence: CloudflareD02OperatorAttestationEvidenceV1, *, custody_root: Path | str, now_utc: datetime) -> None:
    validate_d02_operator_attestation_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    if now > _as_utc(receipt.expires_at_utc):
        raise CloudflareAuthorizationError("D02 authorization receipt expired")
    if receipt.evidence_sha256 != evidence.canonical_sha256:
        raise CloudflareAuthorizationError("D02 evidence hash mismatch")
    if receipt.custody_root_sha256 != canonical_custody_root_sha256(custody_root):
        raise CloudflareAuthorizationError("D02 custody root mismatch")
    if receipt.utc_day != evidence.utc_day or receipt.utc_day != now.date().isoformat():
        raise CloudflareAuthorizationError("D02 UTC day mismatch")


def d02_operator_attestation_to_pre_live_evidence(receipt: CloudflareD02OperatorAttestationReceiptV1, evidence: CloudflareD02OperatorAttestationEvidenceV1, *, custody_root: Path | str, now_utc: datetime) -> CloudflareD02PreLiveEvidence:
    validate_d02_operator_attestation_receipt_for_execution(receipt, evidence, custody_root=custody_root, now_utc=now_utc)
    return CloudflareD02PreLiveEvidence(
        workers_plan="Workers Free",
        workers_paid_enabled=False,
        prepaid_ai_gateway_enabled=False,
        direct_workers_ai_route=True,
        actual_cash_cost_usd=0.0,
        free_neurons_remaining=DAILY_FREE_NEURONS,
        evidence_source=f"ADR-027 D02 operator attestation receipt {receipt.receipt_sha256}",
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
    )
