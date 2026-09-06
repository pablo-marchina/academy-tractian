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
from .provider_clients import ProviderJsonTransport, UrllibProviderJsonTransport


NO_PROVIDER_SELECTION_STATE = "NO_SELECTION"
PROVISIONAL_RELEASE_PROVIDER_STATE = "PROVISIONAL_RELEASE_PROVIDER"


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
    )
    registry = {tool.name: tool for tool in TOOLS}
    return ProviderDecisionSource(
        client=client,
        registry=registry,
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=client.model_id,
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
