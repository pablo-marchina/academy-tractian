from __future__ import annotations

from research.e2.controller import DecisionSource

from .decision_source import (
    PROVIDER_DECISION_ADAPTER_VERSION,
    ProviderCallIdentity,
    ProviderDecisionSource,
)
from .groq_provider_client import (
    GROQ_MODEL_ID,
    GROQ_PROVIDER_ID,
    GROQ_ROUTE_ID,
    GroqChatCompletionsDecisionClient,
)
from .provider_clients import (
    GOOGLE_MODEL_ID,
    GOOGLE_PROVIDER_ID,
    GOOGLE_ROUTE_ID,
    OPENAI_MODEL_ID,
    OPENAI_PROVIDER_ID,
    OPENAI_ROUTE_ID,
    PROVIDER_HTTP_CLIENTS_VERSION,
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
    UrllibProviderJsonTransport,
)
from .runtime import canonical_tool_registry
from .runtime_configuration_identity import RuntimeConfigurationIdentity


SUPPORTED_HOSTED_PROVIDERS = frozenset({"openai", "google", "groq"})


def hosted_runtime_configuration_identity(provider: str) -> RuntimeConfigurationIdentity:
    """Return the public candidate identity bound into hosted runtime config hashes.

    The identity is derived only from code-owned provider/model/route/version constants. API keys,
    endpoints with credentials, request content and responses cannot enter it. Deployment choice is
    therefore observable provenance but is still not evidence that a candidate won promotion.
    """

    normalized = provider.strip().lower()
    if normalized == "openai":
        provider_id = OPENAI_PROVIDER_ID
        model_id = OPENAI_MODEL_ID
        route_id = OPENAI_ROUTE_ID
    elif normalized == "google":
        provider_id = GOOGLE_PROVIDER_ID
        model_id = GOOGLE_MODEL_ID
        route_id = GOOGLE_ROUTE_ID
    elif normalized == "groq":
        provider_id = GROQ_PROVIDER_ID
        model_id = GROQ_MODEL_ID
        route_id = GROQ_ROUTE_ID
    else:
        raise ValueError("unsupported_hosted_provider")

    return RuntimeConfigurationIdentity(
        candidate_id=f"{provider_id}:{model_id}",
        provider_id=provider_id,
        model_id=model_id,
        route_id=route_id,
        adapter_version=PROVIDER_DECISION_ADAPTER_VERSION,
        client_version=PROVIDER_HTTP_CLIENTS_VERSION,
    )


def create_hosted_decision_source(*, provider: str, api_key: str) -> DecisionSource:
    """Build one live hosted decision source without changing application-owned agent semantics."""

    normalized = provider.strip().lower()
    if normalized not in SUPPORTED_HOSTED_PROVIDERS:
        raise ValueError("unsupported_hosted_provider")
    transport = UrllibProviderJsonTransport()
    if normalized == "openai":
        client = OpenAIResponsesDecisionClient(api_key=api_key, transport=transport)
    elif normalized == "google":
        client = GoogleInteractionsDecisionClient(api_key=api_key, transport=transport)
    else:
        client = GroqChatCompletionsDecisionClient(api_key=api_key, transport=transport)

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
