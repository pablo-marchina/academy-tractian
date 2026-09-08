from __future__ import annotations

from copy import deepcopy

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import CLOUDFLARE_PROVIDER_ID
from .decision_source import ProviderCallIdentity, ProviderDecisionRequest, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_clients import ProviderHttpRequest, UrllibProviderJsonTransport
from .release_provider import (
    RELEASE0_PROVIDER_DECISION_JSON_SCHEMA,
    _extract_structured_doc_ids,
    _provider_audit_model_id,
    _successful_observation,
    _terminal_variants_for_request,
    _tool_variant,
    validate_release_provider_config,
)
from .release_provider_v14 import (
    Release0CloudflareDecisionClientV14,
    Release0ProviderDecisionSourceV14,
    _mandatory_asset_continuation_v14,
    _normalize_text_v14,
)


RELEASE0_V14_KNOWLEDGE_VERSION = "release0-explicit-knowledge-retrieval-v1"
RELEASE0_V14_KNOWLEDGE_INSTRUCTION = """
Release 0 explicit knowledge retrieval:
- When the customer explicitly asks to consult or search the knowledge base, execute the supplied
  search_knowledge tool now before any terminal response. Do not merely recommend consulting it and
  do not promise to search later.
- When the customer explicitly asks to open/read the relevant knowledge document, continue from a
  successful search_knowledge result to get_knowledge_doc only when an exact structured doc_id was
  returned. Never invent a doc_id from prose or generic id fields.
- If the explicit knowledge search fails or returns no structured doc_id required by a document-depth
  request, stop with a truthful terminal response that explains the unavailable evidence.
""".strip()

_KNOWLEDGE_SURFACE_MARKERS = (
    "base de conhecimento",
    "knowledge base",
    "search knowledge",
    "searchknowledge",
    "documentacao tecnica",
    "technical documentation",
)
_KNOWLEDGE_DOCUMENT_MARKERS = (
    "get knowledge doc",
    "getknowledgedoc",
    "abra o documento",
    "abrir o documento",
    "leia o documento",
    "ler o documento",
    "resuma o documento",
    "resumir o documento",
    "documento mais relevante",
    "open the document",
    "read the document",
    "summarize the document",
    "most relevant document",
)


def _explicit_knowledge_request_v14(user_request: str) -> bool:
    normalized = _normalize_text_v14(user_request)
    return any(marker in normalized for marker in _KNOWLEDGE_SURFACE_MARKERS)


def _explicit_knowledge_document_request_v14(user_request: str) -> bool:
    if not _explicit_knowledge_request_v14(user_request):
        return False
    normalized = _normalize_text_v14(user_request)
    return any(marker in normalized for marker in _KNOWLEDGE_DOCUMENT_MARKERS)


def _latest_knowledge_search(request_or_context):
    return next(
        (
            observation
            for observation in reversed(request_or_context.observations)
            if observation.tool_name == "search_knowledge"
        ),
        None,
    )


def _knowledge_document_observed(request_or_context) -> bool:
    return any(
        observation.tool_name == "get_knowledge_doc"
        for observation in request_or_context.observations
    )


def _grounded_knowledge_doc_ids(request_or_context) -> tuple[str, ...]:
    observation = _latest_knowledge_search(request_or_context)
    if (
        observation is None
        or not observation.executed
        or observation.status != "success"
    ):
        return ()
    return _extract_structured_doc_ids(observation.body)


def _mandatory_knowledge_continuation_v14(request: ProviderDecisionRequest) -> bool:
    if not _explicit_knowledge_request_v14(request.user_request) or not request.tools:
        return False

    names = {tool.name for tool in request.tools}
    search = _latest_knowledge_search(request)
    if search is None:
        return names == {"search_knowledge"}

    if not _explicit_knowledge_document_request_v14(request.user_request):
        return False
    if _knowledge_document_observed(request):
        return False
    if (
        not search.executed
        or search.status != "success"
        or not _grounded_knowledge_doc_ids(request)
    ):
        return False
    return names == {"get_knowledge_doc"}


def _schema_for_visible_tools_v14_knowledge(
    request: ProviderDecisionRequest,
) -> dict[str, object]:
    template = deepcopy(RELEASE0_PROVIDER_DECISION_JSON_SCHEMA)
    variants = template.get("oneOf")
    if not isinstance(variants, list) or len(variants) != 3:
        raise RuntimeError("release0_v14_knowledge_provider_schema_contract_drift")

    mandatory = _mandatory_knowledge_continuation_v14(request) or _mandatory_asset_continuation_v14(
        request
    )
    terminal_variants = (
        []
        if mandatory
        else _terminal_variants_for_request(
            variants[1:],
            user_request=request.user_request,
        )
    )
    template["oneOf"] = [*(_tool_variant(tool) for tool in request.tools), *terminal_variants]
    return template


class Release0CloudflareDecisionClientV14Knowledge(Release0CloudflareDecisionClientV14):
    """V14 client with schema-enforced explicit knowledge retrieval."""

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        base = super().build_http_request(request)
        body = dict(base.body)
        messages = list(body.get("messages") or [])
        if len(messages) != 2 or not isinstance(messages[0], dict):
            raise RuntimeError("release0_v14_knowledge_cloudflare_message_contract_drift")
        system_content = messages[0].get("content")
        if not isinstance(system_content, str) or not system_content.strip():
            raise RuntimeError("release0_v14_knowledge_system_instruction_contract_drift")
        messages[0] = {
            **messages[0],
            "content": f"{system_content}\n\n{RELEASE0_V14_KNOWLEDGE_INSTRUCTION}",
        }
        body["messages"] = messages
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": _schema_for_visible_tools_v14_knowledge(request),
        }
        return ProviderHttpRequest(
            method=base.method,
            url=base.url,
            headers=dict(base.headers),
            body=body,
            timeout_seconds=base.timeout_seconds,
        )


class Release0ProviderDecisionSourceV14Knowledge(Release0ProviderDecisionSourceV14):
    """Give explicit knowledge intent deterministic precedence over unrelated reads."""

    def _visible_registry(self, context):
        if not _explicit_knowledge_request_v14(context.user_request):
            return super()._visible_registry(context)

        visible = {
            name: tool
            for name, tool in self.registry.items()
            if tool.kind.value == "read"
        }
        search = _latest_knowledge_search(context)
        if search is None:
            tool = visible.get("search_knowledge")
            return {"search_knowledge": tool} if tool is not None else {}

        if _knowledge_document_observed(context):
            return {}

        # A search-only request has now been fulfilled. Do not wander into unrelated reads merely
        # because they remain globally available in the registry.
        if not _explicit_knowledge_document_request_v14(context.user_request):
            return {}

        doc_ids = _grounded_knowledge_doc_ids(context)
        if not doc_ids:
            return {}
        doc_tool = visible.get("get_knowledge_doc")
        if doc_tool is None:
            raise RuntimeError("release0_get_knowledge_doc_missing")
        return {
            "get_knowledge_doc": self._constrain_doc_tool(doc_tool, doc_ids)
        }


def build_release_provider_decision_source_v14_knowledge(
    *,
    config: RemoteProductionConfig,
) -> ProviderDecisionSource:
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    assert config.provider_id is not None
    assert config.provider_model_id is not None
    assert config.provider_account_id is not None
    assert config.provider_api_token is not None
    if config.provider_id != CLOUDFLARE_PROVIDER_ID:
        raise RuntimeError("release_provider_not_supported")

    client = Release0CloudflareDecisionClientV14Knowledge(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return Release0ProviderDecisionSourceV14Knowledge(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=_provider_audit_model_id(client.model_id),
            route_id=client.route_id,
            live_call=True,
        ),
    )


def build_release_provider_decision_source_factory_v14_knowledge(
    config: RemoteProductionConfig,
):
    validate_release_provider_config(config)
    if not config.provider_calls_enabled:
        raise RuntimeError("release_provider_calls_not_enabled")
    return lambda: build_release_provider_decision_source_v14_knowledge(config=config)
