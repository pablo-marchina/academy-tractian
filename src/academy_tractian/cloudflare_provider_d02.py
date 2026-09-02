from __future__ import annotations

from hashlib import sha256
import json
from time import perf_counter_ns
from typing import Any, Callable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import ControllerDecisionKind, DecisionSourceAuditRecord
from research.e2.models import ToolSpec

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CLOUDFLARE_PROVIDER_ID,
    CLOUDFLARE_ROUTE_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from .cloudflare_provider_comparison_v2 import (
    GLM_CANDIDATE_ID,
    NEMOTRON_CANDIDATE_ID,
    NEURON_RATES_PER_MILLION,
    build_cloudflare_provider_comparison_plan_v2,
    load_frozen_cloudflare_comparison_bundle_v2,
)
from .cloudflare_provider_provenance_v2 import (
    CloudflareProviderCallIdentityV2,
    CloudflareProviderDecisionSourceV2,
    CloudflareProviderModelCallRecordV2,
)
from .decision_source import (
    ProviderCallFailureCode,
    ProviderDecisionRequest,
    _canonical_sha256,
    _model_call_id_payload,
)
from .provider_clients import ProviderHttpClientError, ProviderHttpRequest, ProviderJsonTransport


CLOUDFLARE_D02_PROTOCOL_VERSION = "cloudflare-d02-completion-budget-protocol-v1"
CLOUDFLARE_D02_CLIENT_VERSION = "cloudflare-provider-client-d02-v1"
CLOUDFLARE_D02_PROVENANCE_VERSION = "cloudflare-provider-provenance-d02-v1"
CLOUDFLARE_D02_EXECUTOR_VERSION = "cloudflare-d02-comparison-executor-v1"
CLOUDFLARE_D02_PLAN_SCHEMA_VERSION = "cloudflare-d02-comparison-plan-v1"
CLOUDFLARE_D02_RESULT_SCHEMA_VERSION = "cloudflare-d02-comparison-result-v1"
CLOUDFLARE_D02_ATTEMPT_SCHEMA_VERSION = "cloudflare-d02-comparison-attempt-v1"

CLOUDFLARE_D02_MAX_INPUT_TOKENS = 8000
CLOUDFLARE_D02_MAX_COMPLETION_TOKENS = 1024
CLOUDFLARE_D02_MAX_ATTEMPTS = 32
CLOUDFLARE_D02_ATTEMPTS_PER_CANDIDATE = 16
CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS = 10000.0
CLOUDFLARE_D02_EXPECTED_PLAN_SHA256 = (
    "e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"
)

D02_CANDIDATE_IDS = (GLM_CANDIDATE_ID, NEMOTRON_CANDIDATE_ID)


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def observed_neurons_d02(
    candidate_id: str,
    *,
    input_tokens: int,
    output_tokens: int,
) -> float:
    if candidate_id not in NEURON_RATES_PER_MILLION:
        raise ValueError("unknown Cloudflare D02 candidate")
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token usage must be nonnegative")
    input_rate, output_rate = NEURON_RATES_PER_MILLION[candidate_id]
    return (
        input_tokens * input_rate / 1_000_000
        + output_tokens * output_rate / 1_000_000
    )


def worst_case_neurons_per_attempt_d02(candidate_id: str) -> float:
    return observed_neurons_d02(
        candidate_id,
        input_tokens=CLOUDFLARE_D02_MAX_INPUT_TOKENS,
        output_tokens=CLOUDFLARE_D02_MAX_COMPLETION_TOKENS,
    )


def worst_case_neurons_per_candidate_d02(candidate_id: str) -> float:
    return (
        CLOUDFLARE_D02_ATTEMPTS_PER_CANDIDATE
        * worst_case_neurons_per_attempt_d02(candidate_id)
    )


def worst_case_packet_neurons_d02() -> float:
    return sum(
        worst_case_neurons_per_candidate_d02(candidate_id)
        for candidate_id in D02_CANDIDATE_IDS
    )


CLOUDFLARE_D02_MAX_PACKET_NEURONS = worst_case_packet_neurons_d02()
CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1 = CLOUDFLARE_D02_MAX_PACKET_NEURONS
CLOUDFLARE_D02_MAX_MODELED_HEADROOM = (
    CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS - CLOUDFLARE_D02_MAX_PACKET_NEURONS
)

assert abs(CLOUDFLARE_D02_MAX_PACKET_NEURONS - 9352.805376) < 1e-9
assert abs(worst_case_neurons_per_candidate_d02(GLM_CANDIDATE_ID) - 1300.3776) < 1e-9
assert abs(worst_case_neurons_per_candidate_d02(NEMOTRON_CANDIDATE_ID) - 8052.427776) < 1e-9


class CloudflareWorkersAIChatCompletionsDecisionClientD02(
    CloudflareWorkersAIChatCompletionsDecisionClient
):
    """D01 client semantics with only the prospective D02 completion cap changed.

    The client keeps one sanitized failure subtype in memory for the immediately associated
    provenance record. It never stores response text, request text, credentials, or exception text.
    """

    client_version = CLOUDFLARE_D02_CLIENT_VERSION

    def __init__(
        self,
        *,
        api_token: str,
        account_id: str,
        model_id: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        super().__init__(
            api_token=api_token,
            account_id=account_id,
            model_id=model_id,
            transport=transport,
            timeout_seconds=timeout_seconds,
        )
        self._last_failure_subtype: str | None = None

    @property
    def last_failure_subtype(self) -> str | None:
        return self._last_failure_subtype

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        inherited = super().build_http_request(request)
        body = dict(inherited.body)
        body["max_completion_tokens"] = CLOUDFLARE_D02_MAX_COMPLETION_TOKENS
        return ProviderHttpRequest(
            method=inherited.method,
            url=inherited.url,
            headers=inherited.headers,
            body=body,
            timeout_seconds=inherited.timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        self._last_failure_subtype = None
        try:
            return super().complete(request)
        except ProviderHttpClientError as exc:
            self._last_failure_subtype = exc.code
            raise


class CloudflareProviderModelCallRecordD02(CloudflareProviderModelCallRecordV2):
    provenance_version: Literal["cloudflare-provider-provenance-d02-v1"] = (
        CLOUDFLARE_D02_PROVENANCE_VERSION
    )
    failure_subtype: str | None = Field(
        default=None,
        pattern=r"^[A-Z][A-Z0-9_]{0,95}$",
    )

    @model_validator(mode="after")
    def validate_d02_failure_subtype(self) -> "CloudflareProviderModelCallRecordD02":
        if self.outcome == "success":
            if self.failure_subtype is not None:
                raise ValueError("successful D02 call cannot contain failure_subtype")
            return self
        if self.failure_code == "CLIENT_FAILURE":
            if self.failure_subtype is None:
                raise ValueError("D02 CLIENT_FAILURE requires sanitized failure_subtype")
        elif self.failure_subtype is not None:
            raise ValueError("D02 failure_subtype is only valid for CLIENT_FAILURE")
        return self


class CloudflareProviderDecisionSourceD02(CloudflareProviderDecisionSourceV2):
    """D02 Cloudflare provenance source preserving a sanitized client-error subtype."""

    def __init__(
        self,
        *,
        client: CloudflareWorkersAIChatCompletionsDecisionClientD02,
        registry: Mapping[str, ToolSpec],
        call_identity: CloudflareProviderCallIdentityV2,
        clock_ns: Callable[[], int] = perf_counter_ns,
    ) -> None:
        if type(client) is not CloudflareWorkersAIChatCompletionsDecisionClientD02:
            raise ValueError("D02 requires the exact D02 Cloudflare client class")
        super().__init__(
            client=client,
            registry=registry,
            call_identity=call_identity,
            clock_ns=clock_ns,
        )

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
        failure_subtype = None
        if outcome == "failure" and failure_code == "CLIENT_FAILURE":
            failure_subtype = self.client.last_failure_subtype
        record = CloudflareProviderModelCallRecordD02(
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
            failure_subtype=failure_subtype,
            latency_ms=elapsed_ns // 1_000_000,
        )
        self._pending_audit_records.append(record.to_audit_record())


def validate_cloudflare_audit_record_d02(
    *,
    provider_id: str,
    model_id: str,
    route_id: str,
    request_sha256: str,
    audit_records: tuple[object, ...],
    live_call: bool,
) -> tuple[CloudflareProviderModelCallRecordD02 | None, bool, tuple[str, ...]]:
    if len(audit_records) != 1:
        return None, False, ("AUDIT_RECORD_COUNT",)
    item = audit_records[0]
    call_id = getattr(item, "call_id", None)
    metadata = getattr(item, "metadata", None)
    if call_id is None or metadata is None:
        return None, False, ("AUDIT_RECORD_INVALID",)
    try:
        record = CloudflareProviderModelCallRecordD02.model_validate(
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


class CloudflareD02PlanEntry(_FrozenModel):
    attempt_index: int = Field(ge=0, lt=CLOUDFLARE_D02_MAX_ATTEMPTS)
    candidate_id: str
    provider_id: str
    model_id: str
    route_id: str
    unit_id: str
    unit_index: int = Field(ge=0, lt=8)
    repeat_index: int = Field(ge=0, lt=2)


class CloudflareD02ComparisonPlan(_FrozenModel):
    schema_version: Literal["cloudflare-d02-comparison-plan-v1"] = (
        CLOUDFLARE_D02_PLAN_SCHEMA_VERSION
    )
    executor_version: Literal["cloudflare-d02-comparison-executor-v1"] = (
        CLOUDFLARE_D02_EXECUTOR_VERSION
    )
    entries: tuple[CloudflareD02PlanEntry, ...]
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_geometry(self) -> "CloudflareD02ComparisonPlan":
        if len(self.entries) != CLOUDFLARE_D02_MAX_ATTEMPTS:
            raise ValueError("D02 plan must contain exactly 32 attempts")
        if tuple(item.attempt_index for item in self.entries) != tuple(range(32)):
            raise ValueError("D02 attempt indexes must be canonical 0..31")
        payload = {
            "schema_version": self.schema_version,
            "executor_version": self.executor_version,
            "entries": [item.model_dump(mode="json") for item in self.entries],
        }
        if self.plan_sha256 != _canonical_sha256(payload):
            raise ValueError("D02 plan_sha256 mismatch")
        if self.plan_sha256 != CLOUDFLARE_D02_EXPECTED_PLAN_SHA256:
            raise ValueError("D02 canonical plan SHA drift")
        return self


def build_cloudflare_d02_plan(repo_root: str = ".") -> CloudflareD02ComparisonPlan:
    bundle = load_frozen_cloudflare_comparison_bundle_v2(repo_root)
    d01_plan = build_cloudflare_provider_comparison_plan_v2(bundle)
    entries = tuple(
        CloudflareD02PlanEntry(**item.model_dump(mode="json"))
        for item in d01_plan.entries
    )
    payload = {
        "schema_version": CLOUDFLARE_D02_PLAN_SCHEMA_VERSION,
        "executor_version": CLOUDFLARE_D02_EXECUTOR_VERSION,
        "entries": [item.model_dump(mode="json") for item in entries],
    }
    return CloudflareD02ComparisonPlan(
        entries=entries,
        plan_sha256=_canonical_sha256(payload),
    )


class CloudflareD02PreLiveEvidence(_FrozenModel):
    schema_version: Literal["cloudflare-d02-pre-live-evidence-v1"] = (
        "cloudflare-d02-pre-live-evidence-v1"
    )
    workers_plan: Literal["Workers Free"] = "Workers Free"
    workers_paid_enabled: Literal[False] = False
    prepaid_ai_gateway_enabled: Literal[False] = False
    direct_workers_ai_route: Literal[True] = True
    actual_cash_cost_usd: Literal[0.0] = 0.0
    free_neurons_remaining: float = Field(
        ge=0,
        le=CLOUDFLARE_D02_WORKERS_FREE_DAILY_NEURONS,
    )
    evidence_source: str = Field(min_length=1, max_length=256)
    inference_used_to_obtain_evidence: Literal[False] = False
    credential_account_probe_used: Literal[False] = False

    @model_validator(mode="after")
    def validate_start_gate(self) -> "CloudflareD02PreLiveEvidence":
        if (
            self.free_neurons_remaining + 1e-9
            < CLOUDFLARE_D02_MIN_FREE_NEURONS_BEFORE_ATTEMPT_1
        ):
            raise ValueError(
                "D02 requires at least 9352.805376 free neurons before attempt 1"
            )
        return self

    @property
    def canonical_sha256(self) -> str:
        return sha256(
            json.dumps(
                self.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()


class CloudflareD02ComparisonAttempt(_FrozenModel):
    schema_version: Literal["cloudflare-d02-comparison-attempt-v1"] = (
        CLOUDFLARE_D02_ATTEMPT_SCHEMA_VERSION
    )
    attempt_index: int = Field(ge=0, lt=32)
    candidate_id: str
    unit_id: str
    repeat_index: int = Field(ge=0, lt=2)
    outcome: Literal["success", "failure"]
    decision_kind: str | None = None
    tool_name: str | None = None
    failure_code: str | None = None
    failure_subtype: str | None = Field(
        default=None,
        pattern=r"^[A-Z][A-Z0-9_]{0,95}$",
    )
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    latency_ms: int | None = Field(default=None, ge=0)
    rubric_pass: bool
    trace_integrity: bool
    raw_material_recorded: Literal[False] = False

    @model_validator(mode="after")
    def validate_failure_diagnostics(self) -> "CloudflareD02ComparisonAttempt":
        if self.outcome == "success":
            if self.failure_code is not None or self.failure_subtype is not None:
                raise ValueError("successful D02 attempt cannot contain failure diagnostics")
        elif self.failure_code == "CLIENT_FAILURE" and self.failure_subtype is None:
            raise ValueError("D02 CLIENT_FAILURE requires failure_subtype")
        return self


class CloudflareD02ComparisonResult(_FrozenModel):
    schema_version: Literal["cloudflare-d02-comparison-result-v1"] = (
        CLOUDFLARE_D02_RESULT_SCHEMA_VERSION
    )
    executor_version: Literal["cloudflare-d02-comparison-executor-v1"] = (
        CLOUDFLARE_D02_EXECUTOR_VERSION
    )
    plan_sha256: Literal[
        "e768b324baa00dd337c8e56bdfb29b9444be92619508a9fefc30e30b746d1958"
    ] = CLOUDFLARE_D02_EXPECTED_PLAN_SHA256
    completion_token_cap: Literal[1024] = CLOUDFLARE_D02_MAX_COMPLETION_TOKENS
    max_packet_neurons: Literal[9352.805376] = 9352.805376
    attempted_calls: int = Field(ge=0, le=32)
    complete: bool
    attempts: tuple[CloudflareD02ComparisonAttempt, ...]
    selection: str
    actual_cash_cost_usd: Literal[0.0] = 0.0
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False


assert CLOUDFLARE_GLM_MODEL_ID == "@cf/zai-org/glm-4.7-flash"
assert CLOUDFLARE_NEMOTRON_MODEL_ID == "@cf/nvidia/nemotron-3-120b-a12b"
assert CLOUDFLARE_PROVIDER_ID == "cloudflare"
assert CLOUDFLARE_ROUTE_ID == "cloudflare.workers_ai.openai_compat.chat_completions.v1"
