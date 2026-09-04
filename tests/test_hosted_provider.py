import pytest

from academy_tractian.decision_source import ProviderDecisionSource
from academy_tractian.hosted_provider import (
    create_hosted_decision_source,
    hosted_runtime_configuration_identity,
)
from academy_tractian.runtime import ProductionRuntimeConfig, canonical_tool_registry
from academy_tractian.runtime_configuration_identity import production_runtime_config_hash


@pytest.mark.parametrize(
    ("provider", "expected_model"),
    [
        ("openai", "gpt-5.6-sol"),
        ("google", "gemini-3.7-flash"),
        ("groq", "openai/gpt-oss-120b"),
    ],
)
def test_hosted_provider_factory_builds_audited_live_decision_source(
    provider: str,
    expected_model: str,
) -> None:
    source = create_hosted_decision_source(provider=provider, api_key="test-key")

    assert isinstance(source, ProviderDecisionSource)
    assert source.call_identity is not None
    assert source.call_identity.provider_id == provider
    assert source.call_identity.model_id == expected_model
    assert source.call_identity.live_call is True
    assert len(source.registry) == 18
    assert "test-key" not in repr(source.client)


def test_hosted_runtime_identity_matches_provider_client_identity_without_secret_material() -> None:
    for provider in ("openai", "google", "groq"):
        source = create_hosted_decision_source(provider=provider, api_key="SECRET-API-KEY")
        identity = hosted_runtime_configuration_identity(provider)
        assert source.call_identity is not None
        assert identity.provider_id == source.call_identity.provider_id
        assert identity.model_id == source.call_identity.model_id
        assert identity.route_id == source.call_identity.route_id
        assert identity.candidate_id == f"{identity.provider_id}:{identity.model_id}"
        assert "SECRET-API-KEY" not in identity.model_dump_json()


def test_all_hosted_candidates_produce_distinct_runtime_hashes() -> None:
    registry = canonical_tool_registry()
    config = ProductionRuntimeConfig()
    identities = {
        provider: hosted_runtime_configuration_identity(provider)
        for provider in ("openai", "google", "groq")
    }

    assert identities["openai"].candidate_id == "openai:gpt-5.6-sol"
    assert identities["google"].candidate_id == "google:gemini-3.7-flash"
    assert identities["groq"].candidate_id == "groq:openai/gpt-oss-120b"
    hashes = {
        production_runtime_config_hash(config, registry, identity)
        for identity in identities.values()
    }
    assert len(hashes) == 3


def test_hosted_provider_factory_rejects_unselected_or_local_provider() -> None:
    with pytest.raises(ValueError, match="unsupported_hosted_provider"):
        create_hosted_decision_source(provider="local-ollama", api_key="test-key")
    with pytest.raises(ValueError, match="unsupported_hosted_provider"):
        hosted_runtime_configuration_identity("local-ollama")
