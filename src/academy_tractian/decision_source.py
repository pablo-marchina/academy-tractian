from __future__ import annotations

from hashlib import sha256
import json
from time import perf_counter_ns
from typing import Any, Callable, Literal, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    DecisionSource,
    DecisionSourceAuditRecord,
    ToolProposal,
)
from research.e2.models import ToolSpec


PROVIDER_DECISION_ADAPTER_VERSION = "provider-decision-adapter-v1"
PROVIDER_REQUEST_SCHEMA_VERSION = "provider-decision-request-v1"
PROVIDER_DECISION_SCHEMA_VERSION = "provider-decision-payload-v1"
PROVIDER_MODEL_CALL_SCHEMA_VERSION = "provider-model-call-v1"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderToolParameter(_FrozenModel):
    name: str = Field(min_length=1)
    location: Literal["path", "query", "header", "body"]
    required: bool
    parameter_schema: dict[str, Any] = Field(default_factory=dict)


class ProviderToolDefinition(_FrozenModel):
    """Public ToolSpec projection visible to a future model/provider.

    Authorization, identity binding and other runtime-owned fields are deliberately absent.
    """

    name: str = Field(min_length=1)
    operation_id: str = Field(min_length=1)
    method: Literal["GET", "POST", "PATCH", "PUT", "DELETE"]
    path_template: str = Field(min_length=1)
    kind: Literal["read", "action"]
    description: str | None = None
    parameters: tuple[ProviderToolParameter, ...] = ()
    justification_required: bool = False
    minimum_justification_length: int | None = Field(default=None, ge=0)


class ProviderObservation(_FrozenModel):
    tool_name: str = Field(min_length=1)
    status: Literal["success", "failure", "blocked"]
    executed: bool
    blocked_code: str | None = None
    status_code: int | None = None
    body: Any = None
    error_code: str | None = None


class ProviderDecisionRequest(_FrozenModel):
    """Provider-visible request derived only from ADR-004 ControllerContext + public tools."""

    schema_version: Literal["provider-decision-request-v1"] = PROVIDER_REQUEST_SCHEMA_VERSION
    adapter_version: Literal["provider-decision-adapter-v1"] = PROVIDER_DECISION_ADAPTER_VERSION
    user_request: str = Field(min_length=1)
    turn_index: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    observations: tuple[ProviderObservation, ...] = ()
    tools: tuple[ProviderToolDefinition, ...] = ()
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def verify_request_hash(self) -> "ProviderDecisionRequest":
        expected = _canonical_sha256(
            self.model_dump(mode="json", exclude={"request_sha256"})
        )
        if self.request_sha256 != expected:
            raise ValueError("request_sha256 does not match canonical provider request")
        return self


class ProviderDecisionPayload(_FrozenModel):
    """Strict provider-neutral decision payload.

    Canonical ToolSpec argument semantics are intentionally not reimplemented here; known-tool
    arguments remain owned by the existing B1 HarnessRunner validation boundary.
    """

    schema_version: Literal["provider-decision-payload-v1"] = PROVIDER_DECISION_SCHEMA_VERSION
    kind: ControllerDecisionKind
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    evidence_id: str | None = None
    final: dict[str, Any] | None = None
    message: str | None = None
    reason_code: str | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "ProviderDecisionPayload":
        if self.kind is ControllerDecisionKind.TOOL:
            if not self.tool_name:
                raise ValueError("TOOL provider decision requires tool_name")
            if self.final is not None or self.message is not None or self.reason_code is not None:
                raise ValueError("TOOL provider decision cannot contain terminal fields")
            return self

        if self.tool_name is not None or self.arguments or self.evidence_id is not None:
            raise ValueError("terminal provider decision cannot contain tool fields")

        if self.kind is ControllerDecisionKind.FINAL:
            if self.final is None:
                raise ValueError("FINAL provider decision requires final")
            if self.message is not None or self.reason_code is not None:
                raise ValueError("FINAL provider decision must keep terminal content inside final")
            return self

        if self.final is not None:
            raise ValueError("CLARIFY/ESCALATE/ABSTAIN provider decisions cannot contain final")
        return self


class ProviderDecisionClient(Protocol):
    """Replaceable provider client boundary.

    Implementations return one JSON string for one request. The adapter owns strict parsing;
    provider SDKs, retries, fallbacks and live-call authorization are deliberately outside this
    contract and require separate governed work.
    """

    def complete(self, request: ProviderDecisionRequest) -> str: ...


class ProviderCallIdentity(_FrozenModel):
    """Non-secret identity of the serving route used for one auditable client configuration."""

    provider_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
    model_id: str = Field(pattern=r"^[@A-Za-z0-9][@A-Za-z0-9._:/-]{0,191}$")
    route_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
    live_call: bool = False


ProviderCallFailureCode = Literal[
    "CLIENT_FAILURE",
    "RESPONSE_TYPE_INVALID",
    "RESPONSE_JSON_INVALID",
    "RESPONSE_PAYLOAD_INVALID",
    "UNKNOWN_TOOL",
    "PROPOSAL_REJECTED",
]


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def _text_sha256(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _model_call_id_payload(
    *,
    provider_id: str,
    model_id: str,
    route_id: str,
    live_call: bool,
    request_sha256: str,
    turn_index: int,
    tool_call_count: int,
) -> dict[str, Any]:
    return {
        "schema_version": PROVIDER_MODEL_CALL_SCHEMA_VERSION,
        "adapter_version": PROVIDER_DECISION_ADAPTER_VERSION,
        "provider_id": provider_id,
        "model_id": model_id,
        "route_id": route_id,
        "live_call": live_call,
        "request_sha256": request_sha256,
        "turn_index": turn_index,
        "tool_call_count": tool_call_count,
    }


class ProviderModelCallRecord(_FrozenModel):
    """Sanitized one-client-invocation provenance carried by a `model_call` TraceEvent."""

    schema_version: Literal["provider-model-call-v1"] = PROVIDER_MODEL_CALL_SCHEMA_VERSION
    adapter_version: Literal["provider-decision-adapter-v1"] = PROVIDER_DECISION_ADAPTER_VERSION
    call_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    provider_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
    model_id: str = Field(pattern=r"^[@A-Za-z0-9][@A-Za-z0-9._:/-]{0,191}$")
    route_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
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
    def validate_record(self) -> "ProviderModelCallRecord":
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
            raise ValueError("call_id does not match canonical model-call provenance")

        if self.outcome == "success":
            if self.decision_kind is None or self.failure_code is not None or self.response_sha256 is None:
                raise ValueError("successful model call requires decision_kind and response hash only")
        else:
            if self.failure_code is None or self.decision_kind is not None:
                raise ValueError("failed model call requires failure_code and no decision_kind")
        return self

    def to_audit_record(self) -> DecisionSourceAuditRecord:
        return DecisionSourceAuditRecord(
            call_id=self.call_id,
            metadata=self.model_dump(mode="json", exclude={"call_id"}),
        )

    @classmethod
    def from_trace_event(cls, *, call_id: str | None, metadata: Mapping[str, Any]) -> "ProviderModelCallRecord":
        if call_id is None:
            raise ValueError("model_call trace event requires call_id")
        if "call_id" in metadata:
            raise ValueError("model_call metadata must not duplicate call_id")
        return cls.model_validate({"call_id": call_id, **dict(metadata)})


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _tool_projection(tool: ToolSpec) -> ProviderToolDefinition:
    return ProviderToolDefinition(
        name=tool.name,
        operation_id=tool.operation_id,
        method=tool.method,
        path_template=tool.path_template,
        kind=tool.kind.value,
        description=tool.description,
        parameters=tuple(
            ProviderToolParameter(
                name=parameter.name,
                location=parameter.location,
                required=parameter.required,
                parameter_schema=dict(parameter.parameter_schema),
            )
            for parameter in tool.parameters
        ),
        justification_required=tool.justification_required,
        minimum_justification_length=tool.minimum_justification_length,
    )


def build_provider_decision_request(
    *,
    context: ControllerContext,
    registry: Mapping[str, ToolSpec],
) -> ProviderDecisionRequest:
    """Create the deterministic provider-visible request from allowed context only."""

    tools = tuple(_tool_projection(registry[name]) for name in sorted(registry))
    observations = tuple(
        ProviderObservation(
            tool_name=observation.tool_name,
            status=observation.status,
            executed=observation.executed,
            blocked_code=observation.blocked_code,
            status_code=observation.status_code,
            body=observation.body,
            error_code=observation.error_code,
        )
        for observation in context.observations
    )
    payload = {
        "schema_version": PROVIDER_REQUEST_SCHEMA_VERSION,
        "adapter_version": PROVIDER_DECISION_ADAPTER_VERSION,
        "user_request": context.user_request,
        "turn_index": context.turn_index,
        "tool_call_count": context.tool_call_count,
        "observations": [observation.model_dump(mode="json") for observation in observations],
        "tools": [tool.model_dump(mode="json") for tool in tools],
    }
    return ProviderDecisionRequest(
        **payload,
        request_sha256=_canonical_sha256(payload),
    )


def _call_id(identity: ProviderCallIdentity, request: ProviderDecisionRequest) -> str:
    return _canonical_sha256(
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


class ProviderDecisionSource(DecisionSource):
    """Strict provider-neutral adapter implementing the frozen ADR-004 DecisionSource shape.

    Model-call auditing is optional. When `call_identity` is supplied, every client invocation
    queues exactly one sanitized `DecisionSourceAuditRecord` for the controller to append to the
    canonical RunTrace. Existing non-audited clients retain the ADR-006 behavior unchanged.
    """

    def __init__(
        self,
        *,
        client: ProviderDecisionClient,
        registry: Mapping[str, ToolSpec],
        call_identity: ProviderCallIdentity | None = None,
        clock_ns: Callable[[], int] = perf_counter_ns,
    ) -> None:
        if not registry:
            raise ValueError("provider decision adapter requires a non-empty ToolSpec registry")
        self.client = client
        self.registry = dict(registry)
        self._known_tools = frozenset(self.registry)
        self.call_identity = call_identity
        self._clock_ns = clock_ns
        self._pending_audit_records: list[DecisionSourceAuditRecord] = []

    def build_request(self, context: ControllerContext) -> ProviderDecisionRequest:
        return build_provider_decision_request(context=context, registry=self.registry)

    def drain_audit_records(self) -> tuple[DecisionSourceAuditRecord, ...]:
        records = tuple(self._pending_audit_records)
        self._pending_audit_records.clear()
        return records

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
        if self.call_identity is None:
            return
        elapsed_ns = max(0, finished_ns - started_ns)
        record = ProviderModelCallRecord(
            call_id=_call_id(self.call_identity, request),
            provider_id=self.call_identity.provider_id,
            model_id=self.call_identity.model_id,
            route_id=self.call_identity.route_id,
            live_call=self.call_identity.live_call,
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

    def decide(self, context: ControllerContext) -> ControllerDecision:
        request = self.build_request(context)
        started_ns = self._clock_ns()
        response_sha256: str | None = None

        try:
            raw_result = self.client.complete(request)
        except Exception:
            self._record_call(
                request=request,
                response_sha256=None,
                outcome="failure",
                decision_kind=None,
                failure_code="CLIENT_FAILURE",
                started_ns=started_ns,
                finished_ns=self._clock_ns(),
            )
            raise

        if not isinstance(raw_result, str):
            self._record_call(
                request=request,
                response_sha256=None,
                outcome="failure",
                decision_kind=None,
                failure_code="RESPONSE_TYPE_INVALID",
                started_ns=started_ns,
                finished_ns=self._clock_ns(),
            )
            raise TypeError("provider decision client must return a JSON string")

        raw = raw_result
        response_sha256 = _text_sha256(raw)
        try:
            decoded = json.loads(raw, object_pairs_hook=_reject_duplicate_object_pairs)
        except Exception:
            self._record_call(
                request=request,
                response_sha256=response_sha256,
                outcome="failure",
                decision_kind=None,
                failure_code="RESPONSE_JSON_INVALID",
                started_ns=started_ns,
                finished_ns=self._clock_ns(),
            )
            raise

        if not isinstance(decoded, dict):
            self._record_call(
                request=request,
                response_sha256=response_sha256,
                outcome="failure",
                decision_kind=None,
                failure_code="RESPONSE_JSON_INVALID",
                started_ns=started_ns,
                finished_ns=self._clock_ns(),
            )
            raise ValueError("provider decision payload must be a JSON object")

        try:
            payload = ProviderDecisionPayload.model_validate(decoded)
        except Exception:
            self._record_call(
                request=request,
                response_sha256=response_sha256,
                outcome="failure",
                decision_kind=None,
                failure_code="RESPONSE_PAYLOAD_INVALID",
                started_ns=started_ns,
                finished_ns=self._clock_ns(),
            )
            raise

        try:
            if payload.kind is ControllerDecisionKind.TOOL:
                assert payload.tool_name is not None
                if payload.tool_name not in self._known_tools:
                    self._record_call(
                        request=request,
                        response_sha256=response_sha256,
                        outcome="failure",
                        decision_kind=None,
                        failure_code="UNKNOWN_TOOL",
                        started_ns=started_ns,
                        finished_ns=self._clock_ns(),
                    )
                    raise ValueError(f"provider proposed unknown tool: {payload.tool_name}")
                proposal = ToolProposal(
                    tool_name=payload.tool_name,
                    arguments=dict(payload.arguments),
                    evidence_id=payload.evidence_id,
                )
                decision = ControllerDecision(
                    kind=ControllerDecisionKind.TOOL,
                    proposal=proposal,
                )
            elif payload.kind is ControllerDecisionKind.FINAL:
                assert payload.final is not None
                decision = ControllerDecision(
                    kind=ControllerDecisionKind.FINAL,
                    final=dict(payload.final),
                )
            else:
                decision = ControllerDecision(
                    kind=payload.kind,
                    message=payload.message,
                    reason_code=payload.reason_code,
                )
        except Exception:
            if payload.kind is ControllerDecisionKind.TOOL and payload.tool_name in self._known_tools:
                self._record_call(
                    request=request,
                    response_sha256=response_sha256,
                    outcome="failure",
                    decision_kind=None,
                    failure_code="PROPOSAL_REJECTED",
                    started_ns=started_ns,
                    finished_ns=self._clock_ns(),
                )
            raise

        self._record_call(
            request=request,
            response_sha256=response_sha256,
            outcome="success",
            decision_kind=decision.kind,
            failure_code=None,
            started_ns=started_ns,
            finished_ns=self._clock_ns(),
        )
        return decision
