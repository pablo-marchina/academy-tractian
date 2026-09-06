from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy

from research.e2.controller import ControllerContext
from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import (
    CLOUDFLARE_ALLOWED_MODEL_IDS,
    CLOUDFLARE_PROVIDER_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from .decision_source import (
    ProviderCallIdentity,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    ProviderToolDefinition,
    build_provider_decision_request,
)
from .production_config import RemoteProductionConfig
from .provider_clients import (
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderHttpRequest,
    ProviderJsonTransport,
    UrllibProviderJsonTransport,
)


NO_PROVIDER_SELECTION_STATE = "NO_SELECTION"
PROVISIONAL_RELEASE_PROVIDER_STATE = "PROVISIONAL_RELEASE_PROVIDER"
RELEASE0_PROVIDER_INSTRUCTION_VERSION = "release0-provider-instruction-v6"
RELEASE0_MAX_COMPLETION_TOKENS = 1024

_RELEASE0_REQUIRED_FIELDS = [
    "schema_version",
    "kind",
    "tool_name",
    "arguments",
    "evidence_id",
    "final",
    "message",
    "reason_code",
]


def _release0_base_properties(*, kind: list[str]) -> dict[str, object]:
    return {
        "schema_version": {
            "type": "string",
            "enum": ["provider-decision-payload-v1"],
        },
        "kind": {"type": "string", "enum": kind},
    }


RELEASE0_PROVIDER_DECISION_JSON_SCHEMA: dict[str, object] = {
    "oneOf": [
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **_release0_base_properties(kind=["TOOL"]),
                "tool_name": {"type": "string", "minLength": 1},
                "arguments": {"type": "object"},
                "evidence_id": {"type": ["string", "null"]},
                "final": {"type": "null"},
                "message": {"type": "null"},
                "reason_code": {"type": "null"},
            },
            "required": _RELEASE0_REQUIRED_FIELDS,
        },
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **_release0_base_properties(kind=["FINAL"]),
                "tool_name": {"type": "null"},
                "arguments": {"type": "object", "maxProperties": 0},
                "evidence_id": {"type": "null"},
                "final": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "decision": {"type": "string", "enum": ["ORIENT"]},
                        "response_mode": {
                            "type": "string",
                            "enum": [
                                "complete",
                                "partial",
                                "inconclusive",
                                "conflict",
                                "unavailable",
                            ],
                        },
                        "message": {"type": "string", "minLength": 1},
                    },
                    "required": ["decision", "response_mode", "message"],
                },
                "message": {"type": "null"},
                "reason_code": {"type": "null"},
            },
            "required": _RELEASE0_REQUIRED_FIELDS,
        },
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                **_release0_base_properties(kind=["CLARIFY", "ESCALATE", "ABSTAIN"]),
                "tool_name": {"type": "null"},
                "arguments": {"type": "object", "maxProperties": 0},
                "evidence_id": {"type": "null"},
                "final": {"type": "null"},
                "message": {"type": "string", "minLength": 1},
                "reason_code": {"type": "string", "minLength": 1},
            },
            "required": _RELEASE0_REQUIRED_FIELDS,
        },
    ]
}

RELEASE0_PROVIDER_SYSTEM_INSTRUCTION = (
    PROVIDER_DECISION_SYSTEM_INSTRUCTION
    + """

Release 0 decision contract:
Every response must include all eight top-level fields required by provider-decision-payload-v1.
The Release 0 response schema independently enforces the allowed relational shape for TOOL,
FINAL, CLARIFY, ESCALATE, and ABSTAIN. Do not rely on post-processing or output repair.

Release 0 is read-only. The supplied tools list contains only canonical read tools; action tools are
intentionally absent and therefore cannot be selected by a valid provider response. Human escalation
is expressed with kind=ESCALATE, not by proposing an action tool.

For kind=TOOL:
- tool_name must exactly equal one supplied tools[].name. The response schema creates one TOOL variant per tool visible in the current turn.
- arguments must exactly satisfy that selected tool's public parameter schema: only tools[].parameters[].name keys are allowed and every required parameter is required. Never wrap tool arguments inside keys such as tool, params, input, payload, or arguments.
- Use only values justified by the user request or prior public observations. Never invent hidden identity, seed, authorization, credentials, or evaluator state.
- For a read proposal, set evidence_id to a short non-secret identifier so the resulting observation can be referenced.
- Set final=null, message=null, and reason_code=null.

For kind=FINAL:
- Set tool_name=null, arguments={}, evidence_id=null, message=null, and reason_code=null.
- final must be an object containing decision="ORIENT", response_mode equal to exactly one of complete, partial, inconclusive, conflict, or unavailable, and a non-empty customer-safe message grounded only in the public observations.

For kind=CLARIFY, ESCALATE, or ABSTAIN:
- Set tool_name=null, arguments={}, evidence_id=null, and final=null.
- Put the customer-safe explanation in top-level message and a stable non-secret reason in top-level reason_code.

Knowledge investigation stopping rule:
- search_knowledge accepts only q and optional type. get_knowledge_doc accepts only doc_id.
- If search_knowledge is available, use it at most once in a run. After one successful search_knowledge observation it is deliberately removed from the supplied tool list and from the allowed response schema.
- After a successful search_knowledge observation, inspect a returned knowledge document with get_knowledge_doc only when the public observation exposes a concrete document identifier that can be passed as doc_id and the full document is materially needed for the requested answer.
- If no concrete document identifier is exposed, or the search result already contains enough relevant evidence, return FINAL instead of inventing a doc_id or searching again.
- Never call a tool that is absent from the current supplied tools list.

Use TOOL only when another canonical read is materially necessary. Stop with a terminal decision as soon as the available observations are sufficient to answer safely. Do not repeat a successful tool call with materially equivalent arguments unless a prior observation identifies a specific unresolved gap. Honor explicit read-only and no-action requests.
"""
).strip()


def _arguments_schema(tool: ProviderToolDefinition) -> dict[str, object]:
    """Project one public ToolSpec parameter list into a strict JSON object schema."""

    properties = {
        parameter.name: deepcopy(parameter.parameter_schema)
        for parameter in tool.parameters
    }
    required = [parameter.name for parameter in tool.parameters if parameter.required]
    schema: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
    }
    if required:
        schema["required"] = required
    if not properties:
        schema["maxProperties"] = 0
    return schema


def _tool_variant(tool: ProviderToolDefinition) -> dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            **_release0_base_properties(kind=["TOOL"]),
            "tool_name": {"type": "string", "enum": [tool.name]},
            "arguments": _arguments_schema(tool),
            "evidence_id": {"type": ["string", "null"]},
            "final": {"type": "null"},
            "message": {"type": "null"},
            "reason_code": {"type": "null"},
        },
        "required": _RELEASE0_REQUIRED_FIELDS,
    }


def _schema_for_visible_tools(request: ProviderDecisionRequest) -> dict[str, object]:
    """Bind provider output to exactly this turn's visible tools and ToolSpec arguments."""

    if not request.tools:
        raise RuntimeError("release0_provider_visible_tool_surface_empty")
    template = deepcopy(RELEASE0_PROVIDER_DECISION_JSON_SCHEMA)
    variants = template.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 3:
        raise RuntimeError("release0_provider_schema_contract_drift")
    terminal_variants = variants[1:]
    template["oneOf"] = [*(_tool_variant(tool) for tool in request.tools), *terminal_variants]
    return template


class Release0CloudflareDecisionClient(CloudflareWorkersAIChatCompletionsDecisionClient):
    """Release-only request policy layered over the immutable ADR-018 client.

    ADR-018 freezes the historical Cloudflare client byte-for-byte for reproducible comparison.
    Release 0 needs a larger completion budget, no reasoning token spend, and a stricter semantic
    instruction/schema. Keeping these overrides here preserves the frozen research artifact while
    the inherited transport, response parsing, usage accounting, zero-retry and zero-fallback
    properties remain unchanged.
    """

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        base = super().build_http_request(request)
        body = dict(base.body)
        messages = list(body.get("messages") or [])
        if len(messages) != 2 or not isinstance(messages[0], dict):
            raise RuntimeError("release0_cloudflare_message_contract_drift")
        messages[0] = {"role": "system", "content": RELEASE0_PROVIDER_SYSTEM_INSTRUCTION}
        body.update(
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": _schema_for_visible_tools(request),
            },
            max_completion_tokens=RELEASE0_MAX_COMPLETION_TOKENS,
            reasoning_effort=None,
            chat_template_kwargs={"enable_thinking": False},
        )
        return ProviderHttpRequest(
            method=base.method,
            url=base.url,
            headers=dict(base.headers),
            body=body,
            timeout_seconds=base.timeout_seconds,
        )


class Release0ProviderDecisionSource(ProviderDecisionSource):
    """Read-only adaptive provider surface with deterministic tool-budget protection.

    Release 0 exposes only canonical read tools to the model. After one successful
    ``search_knowledge`` that tool is removed from both the provider request and the adapter's
    accepted tool-name set for the rest of the run. The full canonical registry remains owned by
    the runtime/HarnessRunner, so B1/B2/B3 still independently validate every executed proposal.
    """

    @staticmethod
    def _searched_successfully(context: ControllerContext) -> bool:
        return any(
            observation.tool_name == "search_knowledge"
            and observation.status == "success"
            and observation.executed
            for observation in context.observations
        )

    def _visible_registry(self, context: ControllerContext):
        visible = {
            name: tool
            for name, tool in self.registry.items()
            if tool.kind.value == "read"
        }
        if self._searched_successfully(context):
            visible.pop("search_knowledge", None)
        return visible

    def build_request(self, context: ControllerContext) -> ProviderDecisionRequest:
        return build_provider_decision_request(
            context=context,
            registry=self._visible_registry(context),
        )

    def decide(self, context: ControllerContext):
        visible_names = frozenset(self._visible_registry(context))
        self._known_tools = frozenset(
            name for name in self._known_tools if name in visible_names
        )
        return super().decide(context)


def validate_release_provider_config(config: RemoteProductionConfig) -> None:
    """Validate the only Release 0 provider composition currently eligible for serving.

    The full provider tournament remains separate final-selection evidence. Release 0 only
    permits an explicitly configured provisional Cloudflare Workers AI route because that route
    already has a repository-owned one-shot client, USD0 eligibility evidence and no automatic
    retry/fallback behavior.
    """

    if not config.provider_calls_enabled:
        return
    if config.provider_selection_state != PROVISIONAL_RELEASE_PROVIDER_STATE:
        raise RuntimeError("release_provider_state_not_provisional")
    if config.provider_id != CLOUDFLARE_PROVIDER_ID:
        raise RuntimeError("release_provider_not_supported")
    if config.provider_model_id not in CLOUDFLARE_ALLOWED_MODEL_IDS:
        raise RuntimeError("release_provider_model_not_supported")
    if not config.provider_account_id:
        raise RuntimeError("release_provider_account_id_missing")
    if config.provider_api_token is None:
        raise RuntimeError("release_provider_api_token_missing")
    if not config.tractian_transport_enabled:
        raise RuntimeError("release_provider_requires_real_tractian_transport")


def _provider_audit_model_id(model_id: str) -> str:
    """Project Cloudflare's external `@cf/...` id into the v1 audit-id alphabet.

    `ProviderCallIdentity` v1 predates Cloudflare's leading-@ model ids and intentionally accepts
    a restricted non-secret identifier alphabet. The exact external model id remains separately
    available in production configuration/release metadata; only the audit identity removes the
    leading marker. A future provenance schema revision can carry the external id verbatim.
    """

    return model_id[1:] if model_id.startswith("@") else model_id


def build_release_provider_decision_source(
    *,
    config: RemoteProductionConfig,
    transport: ProviderJsonTransport | None = None,
) -> ProviderDecisionSource:
    """Build one auditable hosted DecisionSource for the read-only Release 0 path."""

    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    assert config.provider_id is not None
    assert config.provider_model_id is not None
    assert config.provider_account_id is not None
    assert config.provider_api_token is not None

    client = Release0CloudflareDecisionClient(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=transport or UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSource(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory(
    config: RemoteProductionConfig,
) -> Callable[[], ProviderDecisionSource]:
    """Return a per-run factory without opening a network connection at application boot."""

    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source(config=config)
