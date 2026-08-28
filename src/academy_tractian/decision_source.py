from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Literal, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import (
    ControllerContext,
    ControllerDecision,
    ControllerDecisionKind,
    DecisionSource,
    ToolProposal,
)
from research.e2.models import ToolSpec


PROVIDER_DECISION_ADAPTER_VERSION = "provider-decision-adapter-v1"
PROVIDER_REQUEST_SCHEMA_VERSION = "provider-decision-request-v1"
PROVIDER_DECISION_SCHEMA_VERSION = "provider-decision-payload-v1"


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


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


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


class ProviderDecisionSource(DecisionSource):
    """Strict provider-neutral adapter implementing the frozen ADR-004 DecisionSource shape."""

    def __init__(
        self,
        *,
        client: ProviderDecisionClient,
        registry: Mapping[str, ToolSpec],
    ) -> None:
        if not registry:
            raise ValueError("provider decision adapter requires a non-empty ToolSpec registry")
        self.client = client
        self.registry = dict(registry)
        self._known_tools = frozenset(self.registry)

    def build_request(self, context: ControllerContext) -> ProviderDecisionRequest:
        return build_provider_decision_request(context=context, registry=self.registry)

    def decide(self, context: ControllerContext) -> ControllerDecision:
        request = self.build_request(context)
        raw = self.client.complete(request)
        if not isinstance(raw, str):
            raise TypeError("provider decision client must return a JSON string")

        decoded = json.loads(raw, object_pairs_hook=_reject_duplicate_object_pairs)
        if not isinstance(decoded, dict):
            raise ValueError("provider decision payload must be a JSON object")
        payload = ProviderDecisionPayload.model_validate(decoded)

        if payload.kind is ControllerDecisionKind.TOOL:
            assert payload.tool_name is not None
            if payload.tool_name not in self._known_tools:
                raise ValueError(f"provider proposed unknown tool: {payload.tool_name}")
            proposal = ToolProposal(
                tool_name=payload.tool_name,
                arguments=dict(payload.arguments),
                evidence_id=payload.evidence_id,
            )
            return ControllerDecision(
                kind=ControllerDecisionKind.TOOL,
                proposal=proposal,
            )

        if payload.kind is ControllerDecisionKind.FINAL:
            assert payload.final is not None
            return ControllerDecision(
                kind=ControllerDecisionKind.FINAL,
                final=dict(payload.final),
            )

        return ControllerDecision(
            kind=payload.kind,
            message=payload.message,
            reason_code=payload.reason_code,
        )
