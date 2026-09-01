from __future__ import annotations

from time import perf_counter_ns
from typing import Callable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import ControllerDecisionKind, DecisionSourceAuditRecord
from research.e2.models import ToolSpec

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
)
from .decision_source import (
    PROVIDER_DECISION_ADAPTER_VERSION,
    PROVIDER_MODEL_CALL_SCHEMA_VERSION,
    ProviderCallFailureCode,
    ProviderDecisionClient,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    _canonical_sha256,
    _model_call_id_payload,
)


CLOUDFLARE_PROVIDER_PROVENANCE_ADAPTER_VERSION = "cloudflare-provider-provenance-v2"
CloudflareModelId = Literal[
    "@cf/zai-org/glm-4.7-flash",
    "@cf/nvidia/nemotron-3-120b-a12b",
]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflareProviderCallIdentityV2(_FrozenModel):
    """Prospective exact-identity extension for Workers AI `@cf/...` model IDs.

    Historical ProviderCallIdentity remains immutable. This model intentionally accepts only the
    two ADR-018 model IDs and preserves their official strings byte-for-byte in provenance.
    """

    provider_id: Literal["cloudflare"] = CLOUDFLARE_PROVIDER_ID
    model_id: CloudflareModelId
    route_id: Literal["cloudflare.workers_ai.openai_compat.chat_completions.v1"] = (
        CLOUDFLARE_ROUTE_ID
    )
    live_call: bool = False


class CloudflareProviderModelCallRecordV2(_FrozenModel):
    """ADR-007-compatible model-call record with exact Cloudflare model identity.

    The persisted event shape and schema_version remain `provider-model-call-v1`; only the
    model-id validation domain is prospectively extended for the exact ADR-018 `@cf/...` IDs.
    All other sanitized provenance invariants and call-id derivation are unchanged.
    """

    schema_version: Literal["provider-model-call-v1"] = PROVIDER_MODEL_CALL_SCHEMA_VERSION
    adapter_version: Literal["provider-decision-adapter-v1"] = PROVIDER_DECISION_ADAPTER_VERSION
    call_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    provider_id: Literal["cloudflare"] = CLOUDFLARE_PROVIDER_ID
    model_id: CloudflareModelId
    route_id: Literal["cloudflare.workers_ai.openai_compat.chat_completions.v1"] = (
        CLOUDFLARE_ROUTE_ID
    )
    live_call: bool
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    turn_index: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    outcome: Literal["success", "failure"]
    decision_kind: ControllerDecisionKind | None = None
    failure_code: ProviderCallFailureCode | None = None
    latency_ms: int = Field(ge=0)
    adapter_client_invocations: Literal[1] = 1
    adapter_retry_count: Literal[0] = 0
    adapter_fallback_used: Literal[False] = False
    raw_request_recorded: Literal[False] = False
    raw_response_recorded: Literal[False] = False
    exception_text_recorded: Literal[False] = False

    @model_validator(mode="after")
    def validate_record(self) -> "CloudflareProviderModelCallRecordV2":
        expected_call_id = _canonical_sha256(
            _model_call_id_payload(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                live_call=self.live_call,
                request_sha256=self.request_sha256,
                turn_index=self.turn_index,
                tool_call_count=self.tool_call_count,
            )
        )
        if self.call_id != expected_call_id:
            raise ValueError("call_id does not match canonical Cloudflare model-call provenance")
        if self.outcome == "success":
            if (
                self.decision_kind is None
                or self.failure_code is not None
                or self.response_sha256 is None
            ):
                raise ValueError(
                    "successful model call requires decision_kind and response hash only"
                )
        else:
            if self.failure_code is None or self.decision_kind is not None:
                raise ValueError("failed model call requires failure_code and no decision_kind")
        return self

    def to_audit_record(self) -> DecisionSourceAuditRecord:
        return DecisionSourceAuditRecord(
            call_id=self.call_id,
            metadata=self.model_dump(mode="json", exclude={"call_id"}),
        )


class CloudflareProviderDecisionSourceV2(ProviderDecisionSource):
    """ProviderDecisionSource with a bounded exact-Cloudflare provenance extension only."""

    def __init__(
        self,
        *,
        client: ProviderDecisionClient,
        registry: Mapping[str, ToolSpec],
        call_identity: CloudflareProviderCallIdentityV2,
        clock_ns: Callable[[], int] = perf_counter_ns,
    ) -> None:
        super().__init__(
            client=client,
            registry=registry,
            call_identity=None,
            clock_ns=clock_ns,
        )
        self.cloudflare_call_identity = call_identity

    def _record_call(
        self,
        *,
        request: ProviderDecisionRequest,
        response_sha256: str | None,
        outcome: Literal["success", "failure"],
        decision_kind: ControllerDecisionKind | None,
        failure_code: ProviderCallFailureCode | None,
        started_ns: int,
        finished_ns: int,
    ) -> None:
        identity = self.cloudflare_call_identity
        elapsed_ns = max(0, finished_ns - started_ns)
        call_id = _canonical_sha256(
            _model_call_id_payload(
                provider_id=identity.provider_id,
                model_id=identity.model_id,
                route_id=identity.route_id,
                live_call=identity.live_call,
                request_sha256=request.request_sha256,
                turn_index=request.turn_index,
                tool_call_count=request.tool_call_count,
            )
        )
        record = CloudflareProviderModelCallRecordV2(
            call_id=call_id,
            provider_id=identity.provider_id,
            model_id=identity.model_id,
            route_id=identity.route_id,
            live_call=identity.live_call,
            request_sha256=request.request_sha256,
            response_sha256=response_sha256,
            turn_index=request.turn_index,
            tool_call_count=request.tool_call_count,
            outcome=outcome,
            decision_kind=decision_kind,
            failure_code=failure_code,
            latency_ms=elapsed_ns // 1_000_000,
        )
        self._pending_audit_records.append(record.to_audit_record())


def validate_cloudflare_audit_record_v2(
    *,
    provider_id: str,
    model_id: str,
    route_id: str,
    request_sha256: str,
    audit_records: tuple[object, ...],
    live_call: bool,
) -> tuple[CloudflareProviderModelCallRecordV2 | None, bool, tuple[str, ...]]:
    if len(audit_records) != 1:
        return None, False, ("AUDIT_RECORD_COUNT",)
    item = audit_records[0]
    call_id = getattr(item, "call_id", None)
    metadata = getattr(item, "metadata", None)
    if call_id is None or metadata is None:
        return None, False, ("AUDIT_RECORD_INVALID",)
    try:
        record = CloudflareProviderModelCallRecordV2.model_validate(
            {"call_id": call_id, **dict(metadata)}
        )
    except Exception:
        return None, False, ("AUDIT_RECORD_INVALID",)

    issues: list[str] = []
    if (
        record.provider_id != provider_id
        or record.model_id != model_id
        or record.route_id != route_id
        or record.live_call is not live_call
    ):
        issues.append("ROUTE_OR_MODEL_IDENTITY")
    if record.request_sha256 != request_sha256:
        issues.append("REQUEST_HASH_MISMATCH")
    if (
        record.adapter_client_invocations != 1
        or record.adapter_retry_count != 0
        or record.adapter_fallback_used is not False
    ):
        issues.append("HIDDEN_RETRY_OR_FALLBACK")
    if (
        record.raw_request_recorded
        or record.raw_response_recorded
        or record.exception_text_recorded
    ):
        issues.append("RAW_MATERIAL_RECORDED")
    return record, not issues, tuple(issues)


assert CLOUDFLARE_GLM_MODEL_ID == "@cf/zai-org/glm-4.7-flash"
assert CLOUDFLARE_NEMOTRON_MODEL_ID == "@cf/nvidia/nemotron-3-120b-a12b"
