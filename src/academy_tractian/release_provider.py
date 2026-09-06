from __future__ import annotations

from collections.abc import Callable

from research.e2.tool_registry import TOOLS

from .cloudflare_provider_client import (
    CLOUDFLARE_ALLOWED_MODEL_IDS,
    CLOUDFLARE_PROVIDER_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from .decision_source import ProviderCallIdentity, ProviderDecisionSource
from .production_config import RemoteProductionConfig
from .provider_clients import (
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderJsonTransport,
    UrllibProviderJsonTransport,
)


NO_PROVIDER_SELECTION_STATE = "NO_SELECTION"
PROVISIONAL_RELEASE_PROVIDER_STATE = "PROVISIONAL_RELEASE_PROVIDER"
RELEASE0_PROVIDER_INSTRUCTION_VERSION = "release0-provider-instruction-v2"

RELEASE0_PROVIDER_SYSTEM_INSTRUCTION = (
    PROVIDER_DECISION_SYSTEM_INSTRUCTION
    + """

Release 0 decision contract:
Every response must include all eight top-level fields required by provider-decision-payload-v1.

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

Use TOOL only when another canonical read is materially necessary. Stop with a terminal decision as soon as the available observations are sufficient to answer safely. Do not repeat a successful tool call with materially equivalent arguments unless a prior observation identifies a specific unresolved gap. Honor explicit read-only and no-action requests; never propose an action when the user has prohibited actions.
"""
).strip()


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

    client = CloudflareWorkersAIChatCompletionsDecisionClient(
        api_token=config.provider_api_token.get_secret_value(),
        account_id=config.provider_account_id,
        model_id=config.provider_model_id,
        transport=transport or UrllibProviderJsonTransport(),
        timeout_seconds=config.provider_timeout_seconds,
        system_instruction=RELEASE0_PROVIDER_SYSTEM_INSTRUCTION,
    )
    registry = {tool.name: tool for tool in TOOLS}
    return ProviderDecisionSource(
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