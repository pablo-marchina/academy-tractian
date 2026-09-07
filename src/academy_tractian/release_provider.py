from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from typing import Any

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
RELEASE0_PROVIDER_INSTRUCTION_VERSION = "release0-provider-instruction-v9"
RELEASE0_MAX_COMPLETION_TOKENS = 1024
_RELEASE0_MAX_GROUNDED_DOC_IDS = 32
_RELEASE0_MAX_GROUNDING_DEPTH = 8
_RELEASE0_MAX_DOC_ID_LENGTH = 256
_RELEASE0_MAX_GROUNDED_RESOURCE_IDS = 128

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

_ASSET_DISCOVERY_TOOL_NAMES = frozenset(
    {
        "get_asset",
        "list_analyses",
        "get_analysis",
        "get_baseline",
        "get_rms",
        "get_spectrum",
        "get_data_quality",
    }
)
_ASSET_DIAGNOSTIC_TOOL_NAMES = frozenset(
    {
        "get_analysis",
        "get_baseline",
        "get_rms",
        "get_spectrum",
        "get_data_quality",
    }
)


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
is expressed with kind=ESCALATE, not by proposing an action tool. An explicit user prohibition on
tool use is authoritative: in that case the runtime supplies no tools. When the user also explicitly
requests clarification, abstention because evidence is unavailable, or human escalation of an
unresolved contradiction, the runtime may narrow the response schema to that requested safe terminal
kind. Follow the supplied schema exactly.

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

Grounded identifier discovery and evidence sufficiency:
- Never ask the customer to supply company_id, asset_id, analysis_id, or another internal resource identifier when an exact value can be obtained from prior public observations and authorized read tools.
- For fleet-wide asset criticality, prioritization, or "what is happening" investigations, use the authenticated user context to discover the company when needed, list that company's assets, then inspect the selected asset's analysis or technical evidence before concluding.
- Use only exact structured identifiers observed from tool results. Do not infer identifiers from prose or invent them.
- CLARIFY only when required context cannot be resolved through the authorized read surface. Missing an identifier is not a reason to clarify when a safe read can discover it.
- Do not claim a highest-criticality asset or explain a fault from identity context alone. Comparative claims require asset evidence; diagnostic claims require analysis or technical evidence.

Knowledge investigation stopping rule:
- search_knowledge accepts only q and optional type. get_knowledge_doc accepts only doc_id.
- If search_knowledge is available, use it at most once in a run. After any search_knowledge observation, the runtime deliberately narrows the supplied tool surface.
- After a successful search_knowledge observation, get_knowledge_doc is supplied only when the public structured observation exposes one or more exact doc_id values. In that case, its doc_id parameter is restricted to exactly those observed values.
- Text that merely mentions an identifier, generic id fields, hidden state, or inferred identifiers never authorize get_knowledge_doc.
- If no structured doc_id is exposed, if the search failed, or after one get_knowledge_doc observation, no further read tool is supplied: return a terminal decision instead of inventing another tool continuation.
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


def _normalized_request(value: str) -> str:
    return " ".join(value.casefold().split())


def _asset_investigation_request(user_request: str) -> bool:
    """Conservative multilingual detector for fleet/asset investigations that need domain evidence."""

    normalized = _normalized_request(user_request)
    has_asset_scope = any(marker in normalized for marker in ("asset", "assets", "ativo", "ativos"))
    has_investigative_goal = any(
        marker in normalized
        for marker in (
            "critic",
            "maior",
            "highest",
            "most critical",
            "priorit",
            "attention",
            "atencao",
            "atenção",
            "acontecendo",
            "happening",
            "investig",
            "diagnos",
        )
    )
    return has_asset_scope and has_investigative_goal


def _successful_observation(context: ControllerContext, tool_name: str):
    return next(
        (
            observation
            for observation in reversed(context.observations)
            if observation.tool_name == tool_name
            and observation.executed
            and observation.status == "success"
        ),
        None,
    )


def _append_bounded_identifier(found: list[str], seen: set[str], value: Any) -> None:
    if not isinstance(value, str):
        return
    identifier = value.strip()
    if not identifier or len(identifier) > _RELEASE0_MAX_DOC_ID_LENGTH or identifier in seen:
        return
    if len(found) >= _RELEASE0_MAX_GROUNDED_RESOURCE_IDS:
        return
    seen.add(identifier)
    found.append(identifier)


def _extract_company_ids(value: Any) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()

    def visit(node: Any, *, depth: int) -> None:
        if depth > _RELEASE0_MAX_GROUNDING_DEPTH or len(found) >= _RELEASE0_MAX_GROUNDED_RESOURCE_IDS:
            return
        if isinstance(node, Mapping):
            for key in ("company_id", "companyId"):
                _append_bounded_identifier(found, seen, node.get(key))
            company = node.get("company")
            if isinstance(company, Mapping):
                for key in ("company_id", "companyId", "id"):
                    _append_bounded_identifier(found, seen, company.get(key))
            for child in node.values():
                visit(child, depth=depth + 1)
        elif isinstance(node, (list, tuple)):
            for child in node:
                visit(child, depth=depth + 1)

    visit(value, depth=0)
    return tuple(found)


def _extract_collection_ids(
    value: Any,
    *,
    explicit_keys: tuple[str, ...],
    collection_keys: tuple[str, ...],
) -> tuple[str, ...]:
    """Extract exact resource ids from a known collection response, never from free text."""

    found: list[str] = []
    seen: set[str] = set()

    def add_record(record: Any) -> None:
        if not isinstance(record, Mapping):
            return
        for key in explicit_keys:
            _append_bounded_identifier(found, seen, record.get(key))
        _append_bounded_identifier(found, seen, record.get("id"))

    if isinstance(value, (list, tuple)):
        for record in value:
            add_record(record)
        return tuple(found)

    if not isinstance(value, Mapping):
        return ()

    for key in explicit_keys:
        _append_bounded_identifier(found, seen, value.get(key))

    for collection_key in collection_keys:
        collection = value.get(collection_key)
        if isinstance(collection, (list, tuple)):
            for record in collection:
                add_record(record)
        elif isinstance(collection, Mapping):
            nested_items = collection.get("items")
            if isinstance(nested_items, (list, tuple)):
                for record in nested_items:
                    add_record(record)

    return tuple(found)


def _constrain_tool_parameter(tool, parameter_name: str, values: tuple[str, ...]):
    parameters = tuple(
        parameter.model_copy(
            update={
                "parameter_schema": {
                    **deepcopy(parameter.parameter_schema),
                    "enum": list(values),
                }
            }
        )
        if parameter.name == parameter_name
        else parameter
        for parameter in tool.parameters
    )
    if not any(parameter.name == parameter_name for parameter in parameters):
        raise RuntimeError(f"release0_tool_parameter_contract_drift:{tool.name}:{parameter_name}")
    return tool.model_copy(update={"parameters": parameters})


def _explicit_no_tool_request(user_request: str) -> bool:
    normalized = _normalized_request(user_request)
    return any(
        marker in normalized
        for marker in (
            "do not use any tool",
            "do not use tools",
            "do not use a tool",
            "prohibit tool use",
            "prohibit any tool",
            "without using tools",
            "without using any tool",
        )
    )


def _explicit_terminal_kind(user_request: str) -> str | None:
    """Recognize only explicit safe terminal instructions; never infer hidden intent.

    This is deliberately narrow. It does not classify ordinary requests. It only binds the provider
    when the user simultaneously prohibits tools and unambiguously asks for one safe terminal
    behavior. Ambiguous combinations return ``None`` and retain the normal provider schema.
    """

    if not _explicit_no_tool_request(user_request):
        return None
    normalized = _normalized_request(user_request)
    candidates: list[str] = []

    if (
        ("ask me" in normalized or "ask a" in normalized)
        and ("missing" in normalized or "clarif" in normalized)
        and ("question" in normalized or "context" in normalized)
    ):
        candidates.append("CLARIFY")

    if (
        ("cannot be made" in normalized or "cannot make" in normalized or "cannot be determined" in normalized)
        and ("diagnos" in normalized or "conclusion" in normalized or "determin" in normalized)
    ):
        candidates.append("ABSTAIN")

    if (
        ("human specialist" in normalized or "human expert" in normalized or "escalat" in normalized or "hand" in normalized)
        and ("contradict" in normalized or "conflict" in normalized)
        and ("unresolved" in normalized or "no authoritative evidence" in normalized)
    ):
        candidates.append("ESCALATE")

    return candidates[0] if len(candidates) == 1 else None


def _terminal_variants_for_request(
    terminal_variants: list[dict[str, object]],
    *,
    user_request: str,
) -> list[dict[str, object]]:
    explicit_kind = _explicit_terminal_kind(user_request)
    if explicit_kind is None:
        return terminal_variants
    control_variant = deepcopy(terminal_variants[-1])
    properties = control_variant.get("properties")
    if not isinstance(properties, dict):
        raise RuntimeError("release0_provider_terminal_schema_contract_drift")
    kind_schema = properties.get("kind")
    if not isinstance(kind_schema, dict):
        raise RuntimeError("release0_provider_terminal_kind_contract_drift")
    kind_schema["enum"] = [explicit_kind]
    return [control_variant]


def _mandatory_asset_continuation(request: ProviderDecisionRequest) -> bool:
    """Return true only when the runtime has deliberately exposed a grounded next read stage."""

    if not _asset_investigation_request(request.user_request) or not request.tools:
        return False
    names = {tool.name for tool in request.tools}
    successful = {
        observation.tool_name
        for observation in request.observations
        if observation.executed and observation.status == "success"
    }
    if "get_current_user" in successful and "list_assets_by_company" not in successful:
        return names == {"list_assets_by_company"}
    if "list_assets_by_company" in successful and not (successful & _ASSET_DIAGNOSTIC_TOOL_NAMES):
        return bool(names) and names <= _ASSET_DISCOVERY_TOOL_NAMES
    return False


def _schema_for_visible_tools(request: ProviderDecisionRequest) -> dict[str, object]:
    """Bind provider output to exactly this turn's visible tools and explicit safe terminal intent."""

    template = deepcopy(RELEASE0_PROVIDER_DECISION_JSON_SCHEMA)
    variants = template.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 3:
        raise RuntimeError("release0_provider_schema_contract_drift")
    terminal_variants = [] if _mandatory_asset_continuation(request) else _terminal_variants_for_request(
        variants[1:],
        user_request=request.user_request,
    )
    template["oneOf"] = [*(_tool_variant(tool) for tool in request.tools), *terminal_variants]
    return template


def _extract_structured_doc_ids(value: Any) -> tuple[str, ...]:
    """Extract bounded, exact ``doc_id`` fields from one public structured observation.

    Strings are opaque: identifiers mentioned in free text are intentionally ignored. Generic
    ``id`` keys are also ignored because only the canonical public ``doc_id`` contract authorizes
    the knowledge-document continuation.
    """

    found: list[str] = []
    seen: set[str] = set()

    def visit(node: Any, *, depth: int) -> None:
        if depth > _RELEASE0_MAX_GROUNDING_DEPTH or len(found) >= _RELEASE0_MAX_GROUNDED_DOC_IDS:
            return
        if isinstance(node, Mapping):
            raw_doc_id = node.get("doc_id")
            if isinstance(raw_doc_id, str):
                doc_id = raw_doc_id.strip()
                if (
                    doc_id
                    and len(doc_id) <= _RELEASE0_MAX_DOC_ID_LENGTH
                    and doc_id not in seen
                ):
                    seen.add(doc_id)
                    found.append(doc_id)
            for key, child in node.items():
                if key == "doc_id":
                    continue
                visit(child, depth=depth + 1)
                if len(found) >= _RELEASE0_MAX_GROUNDED_DOC_IDS:
                    break
            return
        if isinstance(node, (list, tuple)):
            for child in node:
                visit(child, depth=depth + 1)
                if len(found) >= _RELEASE0_MAX_GROUNDED_DOC_IDS:
                    break

    visit(value, depth=0)
    return tuple(found)


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
    """Read-only adaptive provider surface with deterministic grounded stopping and discovery."""

    @staticmethod
    def _latest_search_observation(context: ControllerContext):
        return next(
            (
                observation
                for observation in reversed(context.observations)
                if observation.tool_name == "search_knowledge"
            ),
            None,
        )

    @staticmethod
    def _knowledge_doc_observed(context: ControllerContext) -> bool:
        return any(
            observation.tool_name == "get_knowledge_doc"
            for observation in context.observations
        )

    @classmethod
    def _grounded_doc_ids(cls, context: ControllerContext) -> tuple[str, ...]:
        observation = cls._latest_search_observation(context)
        if (
            observation is None
            or not observation.executed
            or observation.status != "success"
        ):
            return ()
        return _extract_structured_doc_ids(observation.body)

    @staticmethod
    def _constrain_doc_tool(tool, doc_ids: tuple[str, ...]):
        return _constrain_tool_parameter(tool, "doc_id", doc_ids)

    @staticmethod
    def _asset_discovery_registry(context: ControllerContext, visible: Mapping[str, Any]):
        if not _asset_investigation_request(context.user_request):
            return None

        current_user = _successful_observation(context, "get_current_user")
        assets = _successful_observation(context, "list_assets_by_company")

        if current_user is not None and assets is None:
            company_ids = _extract_company_ids(current_user.body)
            tool = visible.get("list_assets_by_company")
            if len(company_ids) == 1 and tool is not None:
                return {
                    "list_assets_by_company": _constrain_tool_parameter(
                        tool,
                        "company_id",
                        company_ids,
                    )
                }
            return None

        if assets is None:
            return None

        if any(_successful_observation(context, name) is not None for name in _ASSET_DIAGNOSTIC_TOOL_NAMES):
            return None

        asset_ids = _extract_collection_ids(
            assets.body,
            explicit_keys=("asset_id", "assetId"),
            collection_keys=("assets", "items", "data", "results"),
        )
        if not asset_ids:
            return None

        restricted: dict[str, Any] = {}
        analyses = _successful_observation(context, "list_analyses")
        for name in (
            "get_asset",
            "get_data_quality",
            "get_baseline",
            "get_rms",
            "get_spectrum",
        ):
            tool = visible.get(name)
            if tool is not None:
                restricted[name] = _constrain_tool_parameter(tool, "asset_id", asset_ids)

        if analyses is None:
            tool = visible.get("list_analyses")
            if tool is not None:
                restricted["list_analyses"] = _constrain_tool_parameter(tool, "asset_id", asset_ids)
        else:
            analysis_ids = _extract_collection_ids(
                analyses.body,
                explicit_keys=("analysis_id", "analysisId"),
                collection_keys=("analyses", "items", "data", "results"),
            )
            tool = visible.get("get_analysis")
            if analysis_ids and tool is not None:
                restricted["get_analysis"] = _constrain_tool_parameter(
                    tool,
                    "analysis_id",
                    analysis_ids,
                )

        return restricted or None

    def _visible_registry(self, context: ControllerContext):
        if _explicit_no_tool_request(context.user_request):
            return {}
        visible = {
            name: tool
            for name, tool in self.registry.items()
            if tool.kind.value == "read"
        }
        if self._knowledge_doc_observed(context):
            return {}

        search_observation = self._latest_search_observation(context)
        if search_observation is not None:
            doc_ids = self._grounded_doc_ids(context)
            if not doc_ids:
                return {}
            doc_tool = visible.get("get_knowledge_doc")
            if doc_tool is None:
                raise RuntimeError("release0_get_knowledge_doc_missing")
            return {
                "get_knowledge_doc": self._constrain_doc_tool(doc_tool, doc_ids)
            }

        asset_discovery = self._asset_discovery_registry(context, visible)
        if asset_discovery is not None:
            return asset_discovery

        return visible

    def build_request(self, context: ControllerContext) -> ProviderDecisionRequest:
        return build_provider_decision_request(
            context=context,
            registry=self._visible_registry(context),
        )

    def decide(self, context: ControllerContext):
        visible_names = frozenset(self._visible_registry(context))
        self._known_tools = visible_names
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
