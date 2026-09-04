from __future__ import annotations

from research.e2.controller import DecisionSource

from .decision_source import (
    PROVIDER_DECISION_ADAPTER_VERSION,
    ProviderCallIdentity,
    ProviderDecisionSource,
)
from .google_v1_provider_client import (
    GOOGLE_37_MODEL_ID,
    GOOGLE_38_MODEL_ID,
    GOOGLE_V1_PROVIDER_ID,
    GOOGLE_V1_ROUTE_ID,
    GoogleV1InteractionsDecisionClient,
)
from .groq_provider_client import (
    GROQ_MODEL_ID,
    GROQ_PROVIDER_ID,
    GROQ_ROUTE_ID,
    GroqChatCompletionsDecisionClient,
)
from .provider_clients import (
    OPENAI_MODEL_ID,
    OPENAI_PROVIDER_ID,
    OPENAI_ROUTE_ID,
    OpenAIResponsesDecisionClient,
    UrllibProviderJsonTransport,
)
from .runtime import canonical_tool_registry
from .runtime_configuration_identity import RuntimeConfigurationIdentity


HOSTED_PROVIDER_CLIENTS_VERSION = "hosted-provider-clients-v2"
SUPPORTED_HOSTED_CANDIDATES = frozenset(
    {
        (OPENAI_PROVIDER_ID, OPENAI_MODEL_ID),
        (GOOGLE_V1_PROVIDER_ID, GOOGLE_37_MODEL_ID),
        (GOOGLE_V1_PROVIDER_ID, GOOGLE_38_MODEL_ID),
        (GROQ_PROVIDER_ID, GROQ_MODEL_ID),
    }
)
SUPPORTED_HOSTED_PROVIDERS = frozenset(provider for provider, _ in SUPPORTED_HOSTED_CANDIDATES)


def _normalize_candidate(provider: str, model: str) -> tuple[str, str]:
    candidate = (provider.strip().lower(), model.strip())
    if candidate not in SUPPORTED_HOSTED_CANDIDATES:
        raise ValueError("unsupported_hosted_candidate")
    return candidate


def hosted_runtime_configuration_identity(provider: str, model: str) -> RuntimeConfigurationIdentity:
    """Return a public provider+model identity bound into hosted runtime config hashes.

    Provider and model are both explicit so a provider release cannot silently change production
    semantics. API keys, request content and responses never enter the identity.
    """

    provider_id, model_id = _normalize_candidate(provider, model)
    if provider_id == OPENAI_PROVIDER_ID:
        route_id = OPENAI_ROUTE_ID
    elif provider_id == GOOGLE_V1_PROVIDER_ID:
        route_id = GOOGLE_V1_ROUTE_ID
    else:
        route_id = GROQ_ROUTE_ID

    return RuntimeConfigurationIdentity(
        candidate_id=f"{provider_id}:{model_id}",
        provider_id=provider_id,
        model_id=model_id,
        route_id=route_id,
        adapter_version=PROVIDER_DECISION_ADAPTER_VERSION,
        client_version=HOSTED_PROVIDER_CLIENTS_VERSION,
    )


def create_hosted_decision_source(*, provider: str, model: str, api_key: str) -> DecisionSource:
    """Build one explicit live candidate without changing application-owned agent semantics."""

    provider_id, model_id = _normalize_candidate(provider, model)
    transport = UrllibProviderJsonTransport()
    if provider_id == OPENAI_PROVIDER_ID:
        client = OpenAIResponsesDecisionClient(api_key=api_key, transport=transport)
    elif provider_id == GOOGLE_V1_PROVIDER_ID:
        client = GoogleV1InteractionsDecisionClient(
            api_key=api_key,
            model_id=model_id,
            transport=transport,
        )
    else:
        client = GroqChatCompletionsDecisionClient(api_key=api_key, transport=transport)

    if client.model_id != model_id:
        raise ValueError("hosted_candidate_client_model_mismatch")

    return ProviderDecisionSource(
        client=client,
        registry=canonical_tool_registry(),
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=client.model_id,
            route_id=client.route_id,
            live_call=True,
        ),
    )
