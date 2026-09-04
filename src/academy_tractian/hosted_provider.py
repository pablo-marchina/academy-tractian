from __future__ import annotations

from research.e2.controller import DecisionSource

from .decision_source import ProviderCallIdentity, ProviderDecisionSource
from .provider_clients import (
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
    UrllibProviderJsonTransport,
)
from .runtime import canonical_tool_registry


SUPPORTED_HOSTED_PROVIDERS = frozenset({"openai", "google"})


def create_hosted_decision_source(*, provider: str, api_key: str) -> DecisionSource:
    """Build the live hosted decision source without changing application-owned agent semantics."""

    normalized = provider.strip().lower()
    if normalized not in SUPPORTED_HOSTED_PROVIDERS:
        raise ValueError("unsupported_hosted_provider")
    transport = UrllibProviderJsonTransport()
    if normalized == "openai":
        client = OpenAIResponsesDecisionClient(api_key=api_key, transport=transport)
    else:
        client = GoogleInteractionsDecisionClient(api_key=api_key, transport=transport)

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
