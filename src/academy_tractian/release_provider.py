from __future__ import annotations

from collections.abc import Callable

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
RELEASE0_PROVIDER_INSTRUCTION_VERSION = "release0-provider-instruction-v4"
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

For kind=TOOL:
- tool_name must exactly equal one supplied tools[].name.
- arguments must contain only exact public parameter names from that selected tool's tools[].parameters[].name entries. Never wrap tool arguments inside keys such as tool, params, input, payload, or arguments.
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
- If search_knowledge is available, use it at most once in a run. After one successful search_knowledge observation it is deliberately removed from the supplied tool list.
- After a successful search_knowledge observation, inspect a returned knowledge document with get_knowledge_doc only when the public observation exposes a concrete document identifier that can be passed as doc_id and the full document is materially needed for the requested answer.
- If no concrete document identifier is exposed, or the search result already contains enough relevant evidence, return FINAL instead of searching again.
- Never call a tool that is absent from the current supplied tools list.

Use TOOL only when another canonical read is materially necessary. Stop with a terminal decision as soon as the available observations are sufficient to answer safely. Do not repeat a successful tool call with materially equivalent arguments unless a prior observation identifies a specific unresolved gap. Honor explicit read-only and no-action requests; never propose an action when the user has prohibited actions.
"""
).strip()


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
                "json_schema": RELEASE0_PROVIDER_DECISION_JSON_SCHEMA,
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
    """Release-only adaptive public tool surface with deterministic duplicate-search prevention.

    The source never fabricates a model decision. It only removes ``search_knowledge`` from the
    provider-visible registry after that exact read has executed successfully. This preserves the
    canonical runtime registry and B1/B2/B3 boundaries while making the post-search choice explicit:
    inspect a concrete document with ``get_knowledge_doc`` when justified, or terminate normally.
    """

    def build_request(self, context: ControllerContext) -> ProviderDecisionRequest:
        searched_successfully = any(
            observation.tool_name == "search_knowledge"
            and observation.status == "success"
            and observation.executed
            for observation in context.observations
        )
        if not searched_successfully:
            return super().build_request(context)

        visible_registry = {
            name: tool for name, tool in self.registry.items() if name != "search_knowledge"
        }
        return build_provider_decision_request(
            context=context,
            registry=visible_registry,
        )


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
