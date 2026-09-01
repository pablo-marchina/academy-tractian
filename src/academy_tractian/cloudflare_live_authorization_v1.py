from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha1, sha256
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
)
from .cloudflare_provider_comparison_v2 import EXPECTED_PLAN_SHA256
from .cloudflare_provider_live_v2 import CloudflarePreLiveEvidence


AUTHORIZATION_PROTOCOL_VERSION = "cloudflare-live-authorization-protocol-v1"
AUTHORIZATION_EVIDENCE_VERSION = "cloudflare-live-authorization-evidence-v1"
AUTHORIZATION_RECEIPT_VERSION = "cloudflare-live-authorization-receipt-v1"
PROTOCOL_PATH = "research/experiments/cloudflare-live-authorization-protocol-v1.json"
ADR_018_PATH = "docs/adr/018-cloudflare-provider-model-comparison-preregistration-2026-08-31.md"
ADR_019_PATH = "docs/adr/019-cloudflare-provider-client-provider-free-implementation-2026-08-31.md"
ADR_020_PATH = "docs/adr/020-cloudflare-executor-custody-v2-provider-free-implementation-2026-09-01.md"

ADR_018_GIT_BLOB = "e075ab4ff21904b9412769496dd2680c049cdaa8"
ADR_019_GIT_BLOB = "b8f76831aceb13f5f3ffb5d7da0e12b595d9dd1a"
ADR_020_GIT_BLOB = "857eaab01e02f4615e0a4ec3b2a74f4e16faa90e"

DAILY_FREE_NEURONS = 10000.0
MIN_FREE_NEURONS = 9000.0
EVIDENCE_MAX_AGE_SECONDS = 600
RECEIPT_MAX_LIFETIME_SECONDS = 300
CLOCK_SKEW_SECONDS = 30

DIRECT_ENDPOINT_TEMPLATE = (
    "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions"
)
REQUIRED_TOKEN_PERMISSION = "Account > Workers AI > Read"
ALLOWED_MODELS = (CLOUDFLARE_GLM_MODEL_ID, CLOUDFLARE_NEMOTRON_MODEL_ID)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareAuthorizationError(RuntimeError):
    pass


def _canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _canonical_sha256(payload: Any) -> str:
    return sha256(_canonical_bytes(payload)).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _utc_json(value: datetime) -> str:
    return _as_utc(value).isoformat().replace("+00:00", "Z")


def canonical_custody_root_sha256(custody_root: Path | str) -> str:
    resolved = Path(custody_root).expanduser().resolve(strict=False).as_posix()
    return sha256(resolved.encode("utf-8")).hexdigest()


class CloudflareLiveAuthorizationEvidenceV1(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-evidence-v1"] = (
        AUTHORIZATION_EVIDENCE_VERSION
    )
    observed_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    workers_plan: Literal["Workers Free"] = "Workers Free"
    workers_paid_enabled: Literal[False] = False
    neurons_used_today: float = Field(ge=0, le=DAILY_FREE_NEURONS)
    free_neurons_remaining: float = Field(ge=0, le=DAILY_FREE_NEURONS)
    direct_workers_ai_route: Literal[True] = True
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    gateway_header_present: Literal[False] = False
    comparison_attempts_consumed: Literal[0] = 0
    exclusive_workers_ai_usage_window_attested: Literal[True] = True
    inference_used_to_obtain_evidence: Literal[False] = False
    credential_account_probe_used: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    secret_recorded: Literal[False] = False
    dashboard_source_artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dashboard_source_retained_outside_repo: Literal[True] = True

    @model_validator(mode="after")
    def validate_accounting(self) -> "CloudflareLiveAuthorizationEvidenceV1":
        observed = _as_utc(self.observed_at_utc)
        if observed.date().isoformat() != self.utc_day:
            raise ValueError("utc_day must match observed_at_utc UTC date")
        if abs((self.neurons_used_today + self.free_neurons_remaining) - DAILY_FREE_NEURONS) > 0.001:
            raise ValueError("used + remaining neurons must equal the 10000 daily free allocation")
        if self.free_neurons_remaining < MIN_FREE_NEURONS:
            raise ValueError("at least 9000 free neurons are required")
        return self

    @property
    def canonical_sha256(self) -> str:
        return _canonical_sha256(self.model_dump(mode="json"))


class CloudflareLiveAuthorizationReceiptV1(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-receipt-v1"] = (
        AUTHORIZATION_RECEIPT_VERSION
    )
    protocol_version: Literal["cloudflare-live-authorization-protocol-v1"] = (
        AUTHORIZATION_PROTOCOL_VERSION
    )
    issued_at_utc: datetime
    expires_at_utc: datetime
    utc_day: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    custody_root_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    adr_018_blob: Literal["e075ab4ff21904b9412769496dd2680c049cdaa8"] = ADR_018_GIT_BLOB
    adr_019_blob: Literal["b8f76831aceb13f5f3ffb5d7da0e12b595d9dd1a"] = ADR_019_GIT_BLOB
    adr_020_blob: Literal["857eaab01e02f4615e0a4ec3b2a74f4e16faa90e"] = ADR_020_GIT_BLOB
    plan_sha256: Literal[
        "092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb"
    ] = EXPECTED_PLAN_SHA256
    provider_id: Literal["cloudflare"] = CLOUDFLARE_PROVIDER_ID
    route_id: Literal["cloudflare.workers_ai.openai_compat.chat_completions.v1"] = (
        CLOUDFLARE_ROUTE_ID
    )
    model_ids: tuple[
        Literal["@cf/zai-org/glm-4.7-flash", "@cf/nvidia/nemotron-3-120b-a12b"], ...
    ] = ALLOWED_MODELS
    available_free_neurons_at_issue: float = Field(ge=MIN_FREE_NEURONS, le=DAILY_FREE_NEURONS)
    workers_free_required: Literal[True] = True
    workers_paid_enabled: Literal[False] = False
    ai_gateway_route_used: Literal[False] = False
    prepaid_unified_billing_route_used: Literal[False] = False
    exclusive_workers_ai_usage_window_attested: Literal[True] = True
    comparison_attempts_consumed_at_issue: Literal[0] = 0
    provider_inference_calls_at_issue: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    account_identifier_recorded: Literal[False] = False
    raw_local_custody_path_recorded: Literal[False] = False
    attempt_1_authorized: Literal[True] = True
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_receipt_hash_and_window(self) -> "CloudflareLiveAuthorizationReceiptV1":
        issued = _as_utc(self.issued_at_utc)
        expires = _as_utc(self.expires_at_utc)
        if expires <= issued:
            raise ValueError("receipt expiry must be after issue time")
        if (expires - issued).total_seconds() > RECEIPT_MAX_LIFETIME_SECONDS:
            raise ValueError("receipt lifetime exceeds 300 seconds")
        if issued.date().isoformat() != self.utc_day or expires.date().isoformat() != self.utc_day:
            raise ValueError("receipt must remain inside one UTC day")
        if tuple(self.model_ids) != ALLOWED_MODELS:
            raise ValueError("receipt model identity drift")
        payload = self.model_dump(mode="json", exclude={"receipt_sha256"})
        if self.receipt_sha256 != _canonical_sha256(payload):
            raise ValueError("receipt_sha256 mismatch")
        return self


def validate_frozen_authorization_protocol(repo_root: Path | str = ".") -> dict[str, Any]:
    root = Path(repo_root)
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    if protocol.get("schema_version") != AUTHORIZATION_PROTOCOL_VERSION:
        raise CloudflareAuthorizationError("authorization protocol schema drift")

    for path, expected in (
        (ADR_018_PATH, ADR_018_GIT_BLOB),
        (ADR_019_PATH, ADR_019_GIT_BLOB),
        (ADR_020_PATH, ADR_020_GIT_BLOB),
    ):
        data = (root / path).read_bytes()
        if _git_blob_sha1(data) != expected:
            raise CloudflareAuthorizationError(f"frozen upstream blob mismatch: {path}")

    pins = protocol.get("upstream_pins", {})
    if pins.get("adr_018_blob") != ADR_018_GIT_BLOB:
        raise CloudflareAuthorizationError("ADR-018 pin drift")
    if pins.get("adr_019_blob") != ADR_019_GIT_BLOB:
        raise CloudflareAuthorizationError("ADR-019 pin drift")
    if pins.get("adr_020_blob") != ADR_020_GIT_BLOB:
        raise CloudflareAuthorizationError("ADR-020 pin drift")
    if pins.get("plan_sha256") != EXPECTED_PLAN_SHA256:
        raise CloudflareAuthorizationError("plan pin drift")

    identity = protocol.get("candidate_identity", {})
    if identity.get("provider_id") != CLOUDFLARE_PROVIDER_ID:
        raise CloudflareAuthorizationError("provider identity drift")
    if identity.get("route_id") != CLOUDFLARE_ROUTE_ID:
        raise CloudflareAuthorizationError("route identity drift")
    if tuple(identity.get("models", [])) != ALLOWED_MODELS:
        raise CloudflareAuthorizationError("model identity drift")
    if identity.get("direct_endpoint_template") != DIRECT_ENDPOINT_TEMPLATE:
        raise CloudflareAuthorizationError("endpoint identity drift")

    evidence = protocol.get("authorization_evidence", {})
    receipt = protocol.get("authorization_receipt", {})
    secrets = protocol.get("secret_provisioning", {})
    if evidence.get("max_age_seconds") != EVIDENCE_MAX_AGE_SECONDS:
        raise CloudflareAuthorizationError("evidence freshness drift")
    if evidence.get("minimum_free_neurons_remaining") != MIN_FREE_NEURONS:
        raise CloudflareAuthorizationError("free-neuron threshold drift")
    if receipt.get("max_lifetime_seconds") != RECEIPT_MAX_LIFETIME_SECONDS:
        raise CloudflareAuthorizationError("receipt TTL drift")
    if secrets.get("api_token_minimum_permission") != REQUIRED_TOKEN_PERMISSION:
        raise CloudflareAuthorizationError("token permission drift")

    boundaries = protocol.get("current_task_boundaries", {})
    if boundaries != {
        "provider_model_inference_calls": 0,
        "credential_account_probes": 0,
        "live_network_validation": 0,
        "comparison_attempts_consumed": 0,
        "real_account_evidence_captured": False,
        "real_provider_credentials_required": False,
        "attempt_1_authorized": False,
        "production_provider_selected": False,
        "customer_mutations": 0,
        "c4_changes": 0,
    }:
        raise CloudflareAuthorizationError("current-task hard-boundary drift")
    return protocol


def validate_evidence_for_authorization(
    evidence: CloudflareLiveAuthorizationEvidenceV1,
    *,
    now_utc: datetime,
) -> None:
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    if now.date().isoformat() != evidence.utc_day:
        raise CloudflareAuthorizationError("evidence is not from the current UTC day")
    age = (now - observed).total_seconds()
    if age < -CLOCK_SKEW_SECONDS:
        raise CloudflareAuthorizationError("evidence observation is in the future")
    if age > EVIDENCE_MAX_AGE_SECONDS:
        raise CloudflareAuthorizationError("evidence is stale")


def issue_live_authorization_receipt(
    evidence: CloudflareLiveAuthorizationEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflareLiveAuthorizationReceiptV1:
    validate_evidence_for_authorization(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    observed = _as_utc(evidence.observed_at_utc)
    evidence_expiry = observed + timedelta(seconds=EVIDENCE_MAX_AGE_SECONDS)
    receipt_expiry = min(
        evidence_expiry,
        now + timedelta(seconds=RECEIPT_MAX_LIFETIME_SECONDS),
    )
    if receipt_expiry <= now:
        raise CloudflareAuthorizationError("evidence window leaves no receipt lifetime")

    payload = {
        "schema_version": AUTHORIZATION_RECEIPT_VERSION,
        "protocol_version": AUTHORIZATION_PROTOCOL_VERSION,
        "issued_at_utc": _utc_json(now),
        "expires_at_utc": _utc_json(receipt_expiry),
        "utc_day": evidence.utc_day,
        "evidence_sha256": evidence.canonical_sha256,
        "custody_root_sha256": canonical_custody_root_sha256(custody_root),
        "adr_018_blob": ADR_018_GIT_BLOB,
        "adr_019_blob": ADR_019_GIT_BLOB,
        "adr_020_blob": ADR_020_GIT_BLOB,
        "plan_sha256": EXPECTED_PLAN_SHA256,
        "provider_id": CLOUDFLARE_PROVIDER_ID,
        "route_id": CLOUDFLARE_ROUTE_ID,
        "model_ids": list(ALLOWED_MODELS),
        "available_free_neurons_at_issue": evidence.free_neurons_remaining,
        "workers_free_required": True,
        "workers_paid_enabled": False,
        "ai_gateway_route_used": False,
        "prepaid_unified_billing_route_used": False,
        "exclusive_workers_ai_usage_window_attested": True,
        "comparison_attempts_consumed_at_issue": 0,
        "provider_inference_calls_at_issue": 0,
        "credentials_recorded": False,
        "account_identifier_recorded": False,
        "raw_local_custody_path_recorded": False,
        "attempt_1_authorized": True,
    }
    return CloudflareLiveAuthorizationReceiptV1(
        **payload,
        receipt_sha256=_canonical_sha256(payload),
    )


def validate_receipt_for_execution(
    receipt: CloudflareLiveAuthorizationReceiptV1,
    evidence: CloudflareLiveAuthorizationEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> None:
    validate_evidence_for_authorization(evidence, now_utc=now_utc)
    now = _as_utc(now_utc)
    if now > _as_utc(receipt.expires_at_utc):
        raise CloudflareAuthorizationError("authorization receipt expired")
    if receipt.evidence_sha256 != evidence.canonical_sha256:
        raise CloudflareAuthorizationError("authorization evidence hash mismatch")
    if receipt.custody_root_sha256 != canonical_custody_root_sha256(custody_root):
        raise CloudflareAuthorizationError("authorization custody root mismatch")
    if receipt.utc_day != evidence.utc_day or receipt.utc_day != now.date().isoformat():
        raise CloudflareAuthorizationError("authorization UTC day mismatch")
    if receipt.available_free_neurons_at_issue != evidence.free_neurons_remaining:
        raise CloudflareAuthorizationError("authorization neuron evidence mismatch")


def authorization_to_adr020_pre_live_evidence(
    receipt: CloudflareLiveAuthorizationReceiptV1,
    evidence: CloudflareLiveAuthorizationEvidenceV1,
    *,
    custody_root: Path | str,
    now_utc: datetime,
) -> CloudflarePreLiveEvidence:
    validate_receipt_for_execution(
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
        free_neurons_remaining=evidence.free_neurons_remaining,
        utc_day=evidence.utc_day,
        evidence_source=f"ADR-021 receipt {receipt.receipt_sha256}",
        inference_used_to_obtain_evidence=False,
        credential_account_probe_used=False,
    )
