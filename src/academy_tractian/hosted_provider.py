from __future__ import annotations

from research.e2.controller import DecisionSource

from .decision_source import (
    PROVIDER_DECISION_ADAPTER_VERSION,
    ProviderCallIdentity,
    ProviderDecisionSource,
)
from .google_interactions_provider_client import (
    GOOGLE_HOSTED_PROVIDER_ID,
    GoogleHostedInteractionsDecisionClient,
)
from .groq_provider_client import GROQ_PROVIDER_ID, GroqChatCompletionsDecisionClient
from .hosted_candidate_registry import (
    HOSTED_CANDIDATE_SPECS,
    SUPPORTED_HOSTED_PROVIDERS,
    resolve_hosted_candidate,
)
from .provider_clients import (
    OPENAI_PROVIDER_ID,
    OpenAIResponsesDecisionClient,
    UrllibProviderJsonTransport,
)
from .runtime import canonical_tool_registry
from .runtime_configuration_identity import RuntimeConfigurationIdentity


HOSTED_PROVIDER_CLIENTS_VERSION = "hosted-provider-clients-v3"
SUPPORTED_HOSTED_CANDIDATES = frozenset(
    (spec.provider_id, spec.model_id) for spec in HOSTED_CANDIDATE_SPECS
)


def hosted_runtime_configuration_identity(provider: str, model: str) -> RuntimeConfigurationIdentity:
    """Return a public provider+model identity bound into hosted runtime config hashes.

    Provider and model are both explicit so a provider release cannot silently change production
    semantics. API keys, request content and responses never enter the identity.
    """

    spec = resolve_hosted_candidate(provider, model)
    return RuntimeConfigurationIdentity(
        candidate_id=spec.candidate_id,
        provider_id=spec.provider_id,
        model_id=spec.model_id,
        route_id=spec.route_id,
        adapter_version=PROVIDER_DECISION_ADAPTER_VERSION,
        client_version=HOSTED_PROVIDER_CLIENTS_VERSION,
    )


def create_hosted_decision_source(*, provider: str, model: str, api_key: str) -> DecisionSource:
    """Build one explicit live candidate without changing application-owned agent semantics."""

    spec = resolve_hosted_candidate(provider, model)
    transport = UrllibProviderJsonTransport()
    if spec.provider_id == OPENAI_PROVIDER_ID:
        client = OpenAIResponsesDecisionClient(api_key=api_key, transport=transport)
    elif spec.provider_id == GOOGLE_HOSTED_PROVIDER_ID:
        client = GoogleHostedInteractionsDecisionClient(
            api_key=api_key,
            model_id=spec.model_id,
            transport=transport,
        )
    elif spec.provider_id == GROQ_PROVIDER_ID:
        client = GroqChatCompletionsDecisionClient(api_key=api_key, transport=transport)
    else:  # pragma: no cover - registry construction makes this unreachable.
        raise ValueError("unsupported_hosted_provider")

    if client.model_id != spec.model_id or client.route_id != spec.route_id:
        raise ValueError("hosted_candidate_client_identity_mismatch")

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
