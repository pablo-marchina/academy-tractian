from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cloudflare_live_authorization_v1 import (
    CloudflareAuthorizationError,
    _as_utc,
    _canonical_sha256,
    _utc_json,
    canonical_custody_root_sha256,
)
from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
)
from .cloudflare_provider_d02 import (
    CLOUDFLARE_D02_EXPECTED_PLAN_SHA256,
    CloudflareD02PreLiveEvidence,
)


D02_LIVE_AUTH_PROTOCOL_VERSION = "cloudflare-d02-fresh-reset-live-authorization-v1"
D02_EVIDENCE_VERSION = "cloudflare-d02-zero-use-evidence-v1"
D02_RECEIPT_VERSION = "cloudflare-d02-live-authorization-receipt-v1"

D02_LIVE_AUTH_PROTOCOL_PATH = (
    "research/experiments/cloudflare-d02-fresh-reset-live-authorization-v1.json"
)
ADR_026_PATH = "docs/adr/026-cloudflare-d02-completion-budget-amendment-2026-09-02.md"
ADR_027_PATH = "docs/adr/027-cloudflare-d02-fresh-reset-live-authorization-2026-09-02.md"
D02_PROTOCOL_PATH = "research/experiments/cloudflare-d02-completion-budget-protocol-v1.json"
D02_MODULE_PATH = "src/academy_tractian/cloudflare_provider_d02.py"
D02_EXECUTOR_PATH = "src/academy_tractian/cloudflare_provider_d02_executor.py"

ADR_026_GIT_BLOB = "c5d00a1668613cacd3b520cd241a8b969a262119"
ADR_027_GIT_BLOB = "e5c20622c9f1220a80a57424f4309705cf3a66cb"
D02_PROTOCOL_GIT_BLOB = "eda022821c4ffe08b28b80b814d0da28f84580f6"
D02_MODULE_GIT_BLOB = "c6cc416c4201a30961861c852aaa746e6c5c9113"
D02_EXECUTOR_GIT_BLOB = "24baaa914765e90d85a4d6f265eb2d43cf769825"
D02_LIVE_AUTH_PROTOCOL_GIT_BLOB = "8588284963b96970b997e6afa2bd1cbcc08ea012"

DAILY_FREE_NEURONS = 10000.0
D02_WORST_CASE_PACKET_NEURONS = 9352.805376
EVIDENCE_MAX_AGE_SECONDS = 600
RECEIPT_MAX_LIFETIME_SECONDS = 300
CLOCK_SKEW_SECONDS = 30
D01_USED_UTC_DAY = "2026-09-02"
ALLOWED_MODELS = (CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareD02ZeroUseEvidenceV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-zero-use-evidence-v1"] = D02_EVIDENCE_VERSION
    evidence_mode: Literal["OPERATOR_ZERO_USE_ATTESTATION"] = "OPERATOR_ZERO_USE_ATTESTATION"
    observed_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    reset_at_utc: datetime
    workers_free_active_attested: Literal[True] = True
    workers_paid_disabled_attested: Literal[True] = True
    free_allocation_neurons: Literal[10000.0] = DAILY_FREE_NEURONS
    derived_free_neurons_remaining: Literal[10000.0] = DAILY_FREE_NEURONS
    d02_worst_case_packet_neurons: Literal[9352.805376] = D02_WORST_CASE_PACKET_NEURONS
    no_workers_ai_calls_since_reset_attested: Literal[True] = True
    no_automated_workers_ai_consumers_since_reset_attested: Literal[True] = True
    exclusive_workers_ai_account_window_until_packet_completion_attested: Literal[True] = True
    direct_workers_ai_route: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    comparison_attempts_consumed: Literal[0] = 0
    inference_used_to_obtain_evidence: Literal[False] = False
    credential_account_probe_used: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False
    external_plan_source_artifact_required: Literal[False] = False

    @model_validator(mode="after")
    def validate_reset_window(self) -> "CloudflareD02ZeroUseEvidenceV1":
        observed = _as_utc(self.observed_at_utc)
        reset = _as_utc(self.reset_at_utc)
        expected_reset = datetime(
            observed.year,
            observed.month,
            observed.day,
            tzinfo=timezone.utc,
        )
        if observed.date().isoformat() != self.utc_day:
            raise ValueError("D02 utc_day must match observed_at_utc UTC date")
        if reset != expected_reset:
            raise ValueError("D02 reset_at_utc must be exactly 00:00:00 UTC on utc_day")
        if observed < reset:
            raise ValueError("D02 observation cannot precede reset")
        if self.utc_day == D01_USED_UTC_DAY:
            raise ValueError(
                "D02 cannot attest zero use on 2026-09-02 UTC because D01 already consumed Workers AI"
            )
        if self.derived_free_neurons_remaining < D02_WORST_CASE_PACKET_NEURONS:
            raise ValueError("D02 fresh-reset evidence cannot cover the worst-case packet")
        return self

    @property
    def canonical_sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class CloudflareD02LiveAuthorizationReceiptV1(_FrozenModel):
    schema_version: Literal["cloudflare-d02-live-authorization-receipt-v1"] = D02_RECEIPT_VERSION
    protocol_version: Literal["cloudflare-d02-fresh-reset-live-authorization-v1"] = (
        D02_LIVE_AUTH_PROTOCOL_VERSION
    )
    issued_at_utc: datetime
    expires_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    custody_root_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    plan_sha256: Literal[
        "e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"
    ] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    adr_026_blob: Literal["c5d00a1668613cacd3b520cd241a8b969a262119"] = ADR_026_GIT_BLOB
    adr_027_blob: Literal["e5c20622c9f1220a80a57424f4309705cf3a66cb"] = ADR_027_GIT_BLOB
    d02_protocol_blob: Literal["eda022821c4ffe08b28b80b814d0da28f84580f6"] = D02_PROTOCOL_GIT_BLOB
    d02_module_blob: Literal["c6cc416c4201a30961861c852aaa746e6c5c9113"] = D02_MODULE_GIT_BLOB
    d02_executor_blob: Literal["24baaa914765e90d85a4d6f265eb2d43cf769825"] = D02_EXECUTOR_GIT_BLOB
    live_auth_protocol_blob: Literal["8588284963b96970b997e6afa2bd1cbcc08ea012"] = (
        D02_LIVE_AUTH_PROTOCOL_GIT_BLOB
    )
    provider_id: Literal["cloudflare"] = CLOUDFLARE_PROVIDER_ID
    route_id: Literal["cloudflare.workers_ai.openai_compat.chat_completions.v1"] = (
        CLOUDFLARE_ROUTE_ID
    )
    model_ids: tuple[str, str] = ALLOWED_MODELS
    derived_free_neurons_at_issue: Literal[10000.0] = DAILY_FREE_NEURONS
    d02_worst_case_packet_neurons: Literal[9352.805376] = D02_WORST_CASE_PACKET_NEURONS
    workers_paid_disabled_attested: Literal[True] = True
    no_workers_ai_calls_since_reset_attested: Literal[True] = True
    no_automated_workers_ai_consumers_since_reset_attested: Literal[True] = True
    exclusive_workers_ai_account_window_until_packet_completion_attested: Literal[True] = True
    direct_workers_ai_route: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    provider_inference_calls_at_issue: Literal[0] = 0
    comparison_attempts_consumed_at_issue: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    raw_local_custody_path_recorded: Literal[False] = False
    attempt_1_authorized: Literal[True] = True
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_receipt(self) -> "CloudflareD02LiveAuthorizationReceiptV1":
        issued = _as_utc(self.issued_at_utc)
        expires = _as_utc(self.expires_at_utc)
        if expires <= issued:
            raise ValueError("D02 receipt expiry must follow issue time")
        if (expires - issued).total_seconds() > RECEIPT_MAX_LIFETIME_SECONDS:
            raise ValueError("D02 receipt lifetime exceeds 300 seconds")
        if issued.date().isoformat() != self.utc_day or expires.date().isoformat() != self.utc_day:
            raise ValueError("D02 receipt must remain within one UTC day")
        if self.utc_day == D01_USED_UTC_DAY:
            raise ValueError("D02 receipt cannot authorize the D01-used 2026-09-02 UTC window")
        if tuple(self.model_ids) != ALLOWED_MODELS:
            raise ValueError("D02 receipt model identity drift")
        payload = self.model_dump(mode="json", exclude={"receipt_sha256"})
        if self.receipt_sha256 != _canonical_sha256(payload):
            raise ValueError("D02 receipt_sha256 mismatch")
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
        raise CloudflareAuthorizationError(f"cannot resolve D02 canonical Git blob for {path}") from exc
    value = completed.stdout.strip().lower()
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value):
        raise CloudflareAuthorizationError(f"invalid D02 Git blob identity for {path}")
    return value


def validate_frozen_d02_live_authorization(repo_root: Path | str = ".") -> dict:
    root = Path(repo_root).resolve()
    pins = (
        (ADR_026_PATH, ADR_026_GIT_BLOB),
        (ADR_027_PATH, ADR_027_GIT_BLOB),
        (D02_PROTOCOL_PATH, D02_PROTOCOL_GIT_BLOB),
        (D02_MODULE_PATH, D02_MODULE_GIT_BLOB),
        (D02_EXECUTOR_PATH, D02_EXECUTOR_GIT_BLOB),
        (D02_LIVE_AUTH_PROTOCOL_PATH, D02_LIVE_AUTH_PROTOCOL_GIT_BLOB),
    )
    for path, expected in pins:
        if _git_head_blob_sha(root, path) != expected:
            raise CloudflareAuthorizationError(f"D02 frozen source blob mismatch: {path}")

    protocol = json.loads((root / D02_LIVE_AUTH_PROTOCOL_PATH).read_text(encoding="utf-8"))
    if protocol.get("schema_version") != D02_LIVE_AUTH_PROTOCOL_VERSION:
        raise CloudflareAuthorizationError("D02 live authorization protocol schema drift")
    if protocol.get("d02_plan_sha256") != CLOUDFLARE_D02_EXPECTED_PLAN_SHA256:
        raise CloudflareAuthorizationError("D02 live authorization plan drift")
    evidence = protocol.get("evidence", {})
    required_evidence = {
        "max_age_seconds": EVIDENCE_MAX_AGE_SECONDS,
        "reset_hour_utc": 0,
        "must_be_current_utc_day": True,
        "workers_free_active_required": True,
        "workers_paid_disabled_required": True,
        "no_workers_ai_calls_since_reset_required": True,
        "no_automated_workers_ai_consumers_since_reset_required": True,
        "exclusive_workers_ai_window_until_packet_completion_required": True,
        "direct_workers_ai_route_required": True,
        "ai_gateway_used": False,
        "prepaid_unified_billing_used": False,
        "credential_account_probe_used": False,
        "provider_inference_used": False,
        "external_plan_source_artifact_required": False,
        "derived_free_neurons_required": DAILY_FREE_NEURONS,
    }
    if any(evidence.get(key) != value for key, value in required_evidence.items()):
        raise CloudflareAuthorizationError("D02 evidence protocol drift")
    resource = protocol.get("resource_gate", {})
    if resource != {
        "workers_free_daily_neurons": 10000.0,
        "d02_worst_case_packet_neurons": 9352.805376,
        "minimum_numerical_capacity": 9352.805376,
        "authorization_requires_exact_fresh_reset_zero_use_capacity": 10000.0,
        "modeled_headroom": 647.194624,
        "actual_cash_cost_usd": 0.0,
        "paid_spillover_allowed": False,
    }:
        raise CloudflareAuthorizationError("D02 resource authorization drift")
    return protocol


def validate_d02_zero_use_evidence(
    evidence: CloudflareD02ZeroUseEvidenceV1,
    *,
    now_utc: datetime,
) -> None:
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    if now.date().isoformat() != evidence.utc_day:
        raise CloudflareAuthorizationError("D02 evidence is not from current UTC day")
    age = (now - observed).total_seconds()
    if age < -CLOCK_SKEW_SECONDS:
        raise CloudflareAuthorizationError("D02 evidence observation is in the future")
    if age > EVIDENCE_MAX_AGE_SECONDS:
        raise CloudflareAuthorizationError("D02 evidence is stale")


def issue_d02_live_authorization_receipt(
    evidence: CloudflareD02ZeroUseEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflareD02LiveAuthorizationReceiptV1:
    validate_d02_zero_use_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    evidence_expiry = _as_utc(evidence.observed_at_utc) + timedelta(seconds=EVIDENCE_MAX_AGE_SECONDS)
    receipt_expiry = min(evidence_expiry, now + timedelta(seconds=RECEIPT_MAX_LIFETIME_SECONDS))
    if receipt_expiry <= now:
        raise CloudflareAuthorizationError("D02 evidence leaves no receipt lifetime")
    payload = {
        "schema_version": D02_RECEIPT_VERSION,
        "protocol_version": D02_LIVE_AUTH_PROTOCOL_VERSION,
        "issued_at_utc": _utc_json(now),
        "expires_at_utc": _utc_json(receipt_expiry),
        "utc_day": evidence.utc_day,
        "evidence_sha256": evidence.canonical_sha256,
        "custody_root_sha256": canonical_custody_root_sha256(custody_root),
        "plan_sha256": CLOUDFLARE_D02_EXPECTED_PLAN_SHA256,
        "adr_026_blob": ADR_026_GIT_BLOB,
        "adr_027_blob": ADR_027_GIT_BLOB,
        "d02_protocol_blob": D02_PROTOCOL_GIT_BLOB,
        "d02_module_blob": D02_MODULE_GIT_BLOB,
        "d02_executor_blob": D02_EXECUTOR_GIT_BLOB,
        "live_auth_protocol_blob": D02_LIVE_AUTH_PROTOCOL_GIT_BLOB,
        "provider_id": CLOUDFLARE_PROVIDER_ID,
        "route_id": CLOUDFLARE_ROUTE_ID,
        "model_ids": list(ALLOWED_MODELS),
        "derived_free_neurons_at_issue": DAILY_FREE_NEURONS,
        "d02_worst_case_packet_neurons": D02_WORST_CASE_PACKET_NEURONS,
        "workers_paid_disabled_attested": True,
        "no_workers_ai_calls_since_reset_attested": True,
        "no_automated_workers_ai_consumers_since_reset_attested": True,
        "exclusive_workers_ai_account_window_until_packet_completion_attested": True,
        "direct_workers_ai_route": True,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "provider_inference_calls_at_issue": 0,
        "comparison_attempts_consumed_at_issue": 0,
        "credentials_recorded": False,
        "account_identifier_recorded": False,
        "raw_local_custody_path_recorded": False,
        "attempt_1_authorized": True,
    }
    return CloudflareD02LiveAuthorizationReceiptV1(
        **payload,
        receipt_sha256=_canonical_sha256(payload),
    )


def validate_d02_receipt_for_execution(
    receipt: CloudflareD02LiveAuthorizationReceiptV1,
    evidence: CloudflareD02ZeroUseEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> None:
    validate_d02_zero_use_evidence(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    issued = _as_utc(receipt.issued_at_utc)
    expires = _as_utc(receipt.expires_at_utc)
    if now < issued - timedelta(seconds=CLOCK_SKEW_SECONDS):
        raise CloudflareAuthorizationError("D02 receipt issue time is in the future")
    if now > expires:
        raise CloudflareAuthorizationError("D02 receipt is expired")
    if receipt.utc_day != evidence.utc_day:
        raise CloudflareAuthorizationError("D02 receipt/evidence UTC day mismatch")
    if receipt.evidence_sha256 != evidence.canonical_sha256:
        raise CloudflareAuthorizationError("D02 receipt/evidence hash mismatch")
    if receipt.custody_root_sha256 != canonical_custody_root_sha256(custody_root):
        raise CloudflareAuthorizationError("D02 receipt/custody binding mismatch")
    if receipt.plan_sha256 != CLOUDFLARE_D02_EXPECTED_PLAN_SHA256:
        raise CloudflareAuthorizationError("D02 receipt plan mismatch")


def d02_receipt_to_pre_live_evidence(
    receipt: CloudflareD02LiveAuthorizationReceiptV1,
    evidence: CloudflareD02ZeroUseEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflareD02PreLiveEvidence:
    validate_d02_receipt_for_execution(
        receipt,
        evidence,
        custody_root=custody_root,
        now_utc=now_utc,
    )
    return CloudflareD02PreLiveEvidence(
        free_neurons_remaining=DAILY_FREE_NEURONS,
        evidence_source=f"ADR-027 receipt {receipt.receipt_sha256}",
        workers_plan="Workers Free",
        workers_paid_enabled=False,
        prepaid_ai_gateway_enabled=False,
        direct_workers_ai_route=True,
        actual_cash_cost_usd=0.0,
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
    )
